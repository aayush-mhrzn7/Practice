from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from utils import get_paginated
from tags.models import Tag
from tags.schema import Tag as TagSchema
from user.models import User


class TagService:
    def __init__(self, db: Session) -> None:
        self.db = db

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

    def get_tag(self, tag_id: int) -> Tag:
        return self.db.query(Tag).filter(Tag.id == tag_id).first()

    def get_all_tags(self, filters: dict = {}) -> List[Tag]:
        return get_paginated(self.db, Tag, filters=filters, page=1, page_size=10)

    def update_tag(self, tag_id: int, tag: TagSchema) -> Tag:
        db_tag = self.get_tag(tag_id)
        if db_tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")
        db_tag.name = tag.name.strip()
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag

    def delete_tag(self, tag_id: int) -> bool:
        self.db.query(Tag).filter(Tag.id == tag_id).delete()
        self.db.commit()
        return True
