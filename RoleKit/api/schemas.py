"""
schemas.py — request/response shapes.

Why Pydantic here and SQLAlchemy in models.py
    Models are tables. Schemas are JSON in and out.
    from_attributes=True lets us return an ORM row and FastAPI dumps it to JSON.

We never put permission codes on TokenOut. The token is only access_token;
GET /me reloads codes from SQL so a revoke is visible immediately.
"""

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
    """What GET /me returns. permissions is computed, not stored on User."""

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
    """permissions is the full set of checked codes, not a single toggle."""

    name: str | None = None
    permissions: list[str] | None = None


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    permissions: list[str] = []


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1)
    body: str = ""


class DocumentUpdate(BaseModel):
    title: str | None = None
    body: str | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    owner_id: int
    created_at: datetime


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    action: str
    detail: str
    created_at: datetime
