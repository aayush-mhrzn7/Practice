from datetime import datetime
from pydantic import BaseModel, ConfigDict

class Bookmark(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    url: str
    title: str
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
