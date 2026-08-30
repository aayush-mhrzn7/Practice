from fastapi import HTTPException
from sqlalchemy.orm import Session

from tags.models import Tag
from tags.schema import Tag as TagSchema
from user.models import User
from utils import get_paginated


class TagService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _owned(self, user: User):
        return self.db.query(Tag).filter(Tag.users.any(User.id == user.id))

    def get_tag_by_name(self, name: str) -> Tag | None:
        return self.db.query(Tag).filter(Tag.name == name).first()

    def create_tag(self, tag: TagSchema, user: User) -> Tag:
        name = tag.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Tag name is required")

        db_tag = self.get_tag_by_name(name)
        if db_tag is None:
            db_tag = Tag(name=name)
            self.db.add(db_tag)
            self.db.flush()

        if any(existing.id == db_tag.id for existing in user.tags):
            raise HTTPException(status_code=400, detail="Tag already exists")

        user.tags.append(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag

    def get_tag(self, tag_id: int, user: User) -> Tag:
        db_tag = self._owned(user).filter(Tag.id == tag_id).first()
        if db_tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")
        return db_tag

    def get_all_tags(
        self,
        user: User,
        filters: dict | None = None,
        page: int = 1,
        page_size: int = 10,
        sort_dir: str = "desc",
    ):
        return get_paginated(
            self.db,
            Tag,
            filters=filters,
            page=page,
            page_size=page_size,
            sort_dir=sort_dir,
            query=self._owned(user),
        )

    def update_tag(self, tag_id: int, tag: TagSchema, user: User) -> Tag:
        db_tag = self.get_tag(tag_id, user)
        name = tag.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Tag name is required")
        db_tag.name = name
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag

    def delete_tag(self, tag_id: int, user: User) -> bool:
        db_tag = self.get_tag(tag_id, user)
        user.tags.remove(db_tag)
        self.db.flush()
        if not db_tag.users and not db_tag.bookmarks:
            self.db.delete(db_tag)
        self.db.commit()
        return True
