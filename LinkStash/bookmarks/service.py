from fastapi import HTTPException
from sqlalchemy.orm import Session

from bookmarks.models import Bookmark
from bookmarks.schema import BookmarkCreate
from user.models import User
from utils import get_paginated


class BookmarkService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _owned(self, user: User):
        return self.db.query(Bookmark).filter(Bookmark.user_id == user.id)

    def create_bookmark(self, bookmark: BookmarkCreate, user: User) -> Bookmark:
        db_bookmark = Bookmark(url=bookmark.url, title=bookmark.title, user_id=user.id)
        self.db.add(db_bookmark)
        self.db.commit()
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
    ):
        return get_paginated(
            self.db,
            Bookmark,
            filters=filters,
            page=page,
            page_size=page_size,
            sort_dir=sort_dir,
            query=self._owned(user),
        )

    def update_bookmark(self, bookmark_id: int, bookmark: BookmarkCreate, user: User) -> Bookmark:
        db_bookmark = self.get_bookmark(bookmark_id, user)
        db_bookmark.url = bookmark.url
        db_bookmark.title = bookmark.title
        self.db.commit()
        self.db.refresh(db_bookmark)
        return db_bookmark

    def delete_bookmark(self, bookmark_id: int, user: User) -> bool:
        db_bookmark = self.get_bookmark(bookmark_id, user)
        self.db.delete(db_bookmark)
        self.db.commit()
        return True
