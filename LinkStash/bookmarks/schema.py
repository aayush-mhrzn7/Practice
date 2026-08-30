from datetime import datetime
from pydantic import BaseModel, ConfigDict

from tags.schema import Tag


class BookmarkCreate(BaseModel):
    url: str
    title: str
    notes: str | None = None


class BookmarkUpdate(BaseModel):
    url: str | None = None
    title: str | None = None
    notes: str | None = None


class BookmarkTagAttach(BaseModel):
    tag_id: int


class Bookmark(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    url: str
    title: str
    notes: str | None = None
    user_id: int
    tags: list[Tag] = []
    created_at: datetime
    updated_at: datetime
