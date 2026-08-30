from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from bookmarks.models import Bookmark
from bookmarks.schema import BookmarkCreate, BookmarkUpdate
from tags.models import Tag
from user.models import User
from utils import get_paginated


class BookmarkService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _owned(self, user: User):
        return self.db.query(Bookmark).filter(Bookmark.user_id == user.id).options(
            selectinload(Bookmark.tags)
        )

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=409, detail="Bookmark URL already exists")

    def create_bookmark(self, bookmark: BookmarkCreate, user: User) -> Bookmark:
        db_bookmark = Bookmark(
            url=bookmark.url,
            title=bookmark.title,
            notes=bookmark.notes,
            user_id=user.id,
        )
        self.db.add(db_bookmark)
        self._commit()
        self.db.refresh(db_bookmark)
        return db_bookmark

    def get_bookmark(self, bookmark_id: int, user: User) -> Bookmark:
        db_bookmark = self._owned(user).filter(Bookmark.id == bookmark_id).first()
        if db_bookmark is None:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        return db_bookmark

    def get_all_bookmarks(
        self,
        user: User,
        filters: dict | None = None,
        page: int = 1,
        page_size: int = 10,
        sort_dir: str = "desc",
        tag: str | None = None,
        q: str | None = None,
    ):
        query = self._owned(user)
        if tag:
            query = query.filter(Bookmark.tags.any(Tag.name == tag.strip().lower()))
        if q:
            like = f"%{q}%"
            query = query.filter(or_(Bookmark.title.ilike(like), Bookmark.url.ilike(like)))
        return get_paginated(
            self.db,
            Bookmark,
            filters=filters,
            page=page,
            page_size=page_size,
            sort_dir=sort_dir,
            query=query,
        )

    def update_bookmark(self, bookmark_id: int, bookmark: BookmarkCreate, user: User) -> Bookmark:
        db_bookmark = self.get_bookmark(bookmark_id, user)
        db_bookmark.url = bookmark.url
        db_bookmark.title = bookmark.title
        db_bookmark.notes = bookmark.notes
        self._commit()
        self.db.refresh(db_bookmark)
        return db_bookmark

    def patch_bookmark(self, bookmark_id: int, bookmark: BookmarkUpdate, user: User) -> Bookmark:
        db_bookmark = self.get_bookmark(bookmark_id, user)
        for field, value in bookmark.model_dump(exclude_unset=True).items():
            setattr(db_bookmark, field, value)
        self._commit()
        self.db.refresh(db_bookmark)
        return db_bookmark

    def delete_bookmark(self, bookmark_id: int, user: User) -> None:
        db_bookmark = self.get_bookmark(bookmark_id, user)
        self.db.delete(db_bookmark)
        self.db.commit()

    def _owned_tag(self, tag_id: int, user: User) -> Tag:
        db_tag = (
            self.db.query(Tag)
            .filter(Tag.id == tag_id, Tag.users.any(User.id == user.id))
            .first()
        )
        if db_tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")
        return db_tag

    def attach_tag(self, bookmark_id: int, tag_id: int, user: User) -> Bookmark:
        db_bookmark = self.get_bookmark(bookmark_id, user)
        db_tag = self._owned_tag(tag_id, user)
        if any(existing.id == db_tag.id for existing in db_bookmark.tags):
            raise HTTPException(status_code=409, detail="Tag already attached")
        db_bookmark.tags.append(db_tag)
        self.db.commit()
        self.db.refresh(db_bookmark)
        return db_bookmark

    def detach_tag(self, bookmark_id: int, tag_id: int, user: User) -> None:
        db_bookmark = self.get_bookmark(bookmark_id, user)
        db_tag = next((existing for existing in db_bookmark.tags if existing.id == tag_id), None)
        if db_tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")
        db_bookmark.tags.remove(db_tag)
        self.db.commit()
