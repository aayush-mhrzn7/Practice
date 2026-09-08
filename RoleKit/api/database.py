"""
database.py — one SQLite file, one session per request.

Why this file exists
    Every route that talks to SQL needs a Session. FastAPI's Depends(get_db)
    calls this generator, yields a session for that request, then closes it.
    We do not keep a global session. That way a revoke in request A is visible
    to request B: they are different sessions, both reading the same file.

SQLite note
    check_same_thread=False is required because FastAPI can run the same engine
    from more than one thread. The file is still ./rolekit.db next to uvicorn.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./rolekit.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Parent of every ORM model. Alembic reads Base.metadata to know tables."""

    pass


def get_db():
    """
    Open a session, give it to the route, always close it.

    yield is how FastAPI Depends works: the route runs in the middle.
    If the route raises, we still hit finally and close.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
