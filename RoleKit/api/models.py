from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base

PERMISSION_GROUPS = (
    {
        "key": "documents",
        "label": "Documents",
        "items": (
            ("documents:read", "Read"),
            ("documents:write", "Write"),
            ("documents:edit", "Edit"),
            ("documents:delete", "Delete"),
        ),
    },
    {
        "key": "notes",
        "label": "Notes",
        "items": (
            ("notes:read", "Read"),
            ("notes:write", "Write"),
            ("notes:edit", "Edit"),
            ("notes:delete", "Delete"),
        ),
    },
    {
        "key": "announcements",
        "label": "Announcements",
        "items": (
            ("announcements:read", "Read"),
            ("announcements:write", "Write"),
            ("announcements:edit", "Edit"),
            ("announcements:delete", "Delete"),
        ),
    },
    {
        "key": "audit",
        "label": "Audit",
        "items": (("audit:read", "Read"),),
    },
    {
        "key": "settings",
        "label": "Settings",
        "items": (
            ("settings:read", "Read"),
            ("settings:edit", "Edit"),
        ),
    },
)

PERMISSION_CODES = tuple(
    code for group in PERMISSION_GROUPS for code, _label in group["items"]
)

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="owner")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="owner")
    announcements: Mapped[list["Announcement"]] = relationship(
        "Announcement",
        back_populates="owner",
    )


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("code", name="uq_permissions_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, nullable=False, index=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
    )


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("name", name="uq_roles_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False, default="")
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    owner: Mapped["User"] = relationship("User", back_populates="documents")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False, default="")
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    owner: Mapped["User"] = relationship("User", back_populates="notes")


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False, default="")
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    owner: Mapped["User"] = relationship("User", back_populates="announcements")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    detail: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workspace_name: Mapped[str] = mapped_column(String, nullable=False, default="RoleKit")
    banner: Mapped[str] = mapped_column(String, nullable=False, default="")
