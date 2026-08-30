from datetime import datetime
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    email: str
    password: str
    name: str
    bio: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    bio: str | None = None
    created_at: datetime
    updated_at: datetime
