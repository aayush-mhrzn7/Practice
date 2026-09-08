from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserLogin(BaseModel):
    email: str
    password: str


class RoleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_admin: bool
    permissions: list[str] = []


class UserListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_admin: bool
    roles: list[RoleBrief] = []


class TokenOut(BaseModel):
    access_token: str


class RoleCreate(BaseModel):
    name: str = Field(min_length=1)


class RoleUpdate(BaseModel):
    name: str | None = None
    permissions: list[str] | None = None


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    permissions: list[str] = []


class TitledCreate(BaseModel):
    title: str = Field(min_length=1)
    body: str = ""


class TitledUpdate(BaseModel):
    title: str | None = None
    body: str | None = None


class TitledOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    owner_id: int
    created_at: datetime


class PermissionItem(BaseModel):
    code: str
    label: str


class PermissionGroupOut(BaseModel):
    key: str
    label: str
    permissions: list[PermissionItem]


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    action: str
    detail: str
    created_at: datetime


class SettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workspace_name: str
    banner: str


class SettingUpdate(BaseModel):
    workspace_name: str | None = None
    banner: str | None = None
