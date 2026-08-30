from datetime import datetime
from pydantic import BaseModel, ConfigDict

class Tag(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
