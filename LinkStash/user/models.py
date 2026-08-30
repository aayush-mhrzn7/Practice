from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database.session import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    bio: Mapped[str] = mapped_column(String, nullable=True)
    bookmarks: Mapped[list["Bookmark"]] = relationship("Bookmark", back_populates="user")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="user_tags", back_populates="users")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

