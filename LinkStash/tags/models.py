from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Table, ForeignKey, Column
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database.session import Base

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        "Bookmark", secondary="bookmark_tags", back_populates="tags"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

bookmark_tags = Table(
    "bookmark_tags",
    Base.metadata,
    Column("bookmark_id", ForeignKey("bookmarks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
