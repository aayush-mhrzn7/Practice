from database.session import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey, Integer, String

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True)
    password: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )

class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, index=True)
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions"
    )

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"))
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.id"))


class UserRole(Base):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"))