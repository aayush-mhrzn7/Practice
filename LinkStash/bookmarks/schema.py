from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BookmarkCreate(BaseModel):
    url: str
    title: str

class Bookmark(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    url: str
    title: str
    user_id: int
    created_at: datetime
    updated_at: datetime
