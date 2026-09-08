"""
models.py — the tables.

Shape
    User ──< user_roles >── Role ──< role_permissions >── Permission
      │
      └── documents.owner_id
    AuditEvent is a log row, not part of the grant graph.

Why association tables instead of a column on User
    A user can have many roles. A role can have many permissions.
    Grant = insert a user_roles row. Revoke = delete that row.
    The JWT never stores this graph, so the next request re-reads it.

PERMISSION_CODES
    Frozen list. Alembic inserts matching rows. The roles UI ticks these
    strings; unknown codes are rejected in routers/roles.py.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base

PERMISSION_CODES = [
    "documents:read",
    "documents:write",
    "documents:edit",
    "documents:delete",
    "audit:read",
]

# Many-to-many: which users have which roles.
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

# Many-to-many: which roles have which permission codes.
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class User(Base):
    """
    An account. is_admin only unlocks /roles and /users (the matrix).
    Document and audit access come from roles, not from this flag.
    """

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    roles: Mapped[list["Role"]] = relationship("Role", secondary=user_roles, back_populates="users")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="owner")


class Permission(Base):
    """One frozen code, e.g. documents:read. The UI cannot create new rows."""

    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("code", name="uq_permissions_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False)

    roles: Mapped[list["Role"]] = relationship("Role", secondary=role_permissions, back_populates="permissions")


class Role(Base):
    """A name you type (viewer, night-editor) plus a set of permission rows."""

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("name", name="uq_roles_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
    )
    users: Mapped[list["User"]] = relationship("User", secondary=user_roles, back_populates="roles")


class Document(Base):
    """The gated resource. Enough CRUD to prove a 403."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False, default="")
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="documents")


class AuditEvent(Base):
    """Append-only log of role create / replace / grant / revoke."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    detail: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
