"""Clear app tables and load demo users, tags, and bookmarks.

Run from LinkStash/:
    python seed.py
"""

from database.session import Base, local_session
from user.models import User
from tags.models import Tag
from bookmarks.models import Bookmark
from user.utils import hash_password

DEV_TAGS = [
    "python",
    "fastapi",
    "sqlalchemy",
    "docker",
    "postgres",
    "git",
    "linux",
    "javascript",
    "typescript",
    "react",
    "rust",
    "golang",
    "kubernetes",
    "redis",
    "testing",
]

DEV_BOOKMARKS = [
    ("https://docs.python.org/3/", "Python 3 documentation", ["python"]),
    ("https://fastapi.tiangolo.com/", "FastAPI documentation", ["python", "fastapi"]),
    ("https://docs.sqlalchemy.org/", "SQLAlchemy documentation", ["python", "sqlalchemy"]),
    ("https://alembic.sqlalchemy.org/", "Alembic documentation", ["python", "sqlalchemy"]),
    ("https://docs.pydantic.dev/", "Pydantic documentation", ["python", "fastapi"]),
    ("https://docs.docker.com/", "Docker documentation", ["docker", "linux"]),
    ("https://www.postgresql.org/docs/", "PostgreSQL documentation", ["postgres"]),
    ("https://git-scm.com/doc", "Git documentation", ["git"]),
    ("https://developer.mozilla.org/en-US/docs/Web/JavaScript", "MDN JavaScript", ["javascript"]),
    ("https://www.typescriptlang.org/docs/", "TypeScript handbook", ["javascript", "typescript"]),
    ("https://react.dev/", "React documentation", ["javascript", "react"]),
    ("https://doc.rust-lang.org/book/", "The Rust Programming Language", ["rust"]),
    ("https://go.dev/doc/", "Go documentation", ["golang"]),
    ("https://kubernetes.io/docs/home/", "Kubernetes documentation", ["kubernetes", "docker"]),
    ("https://redis.io/docs/", "Redis documentation", ["redis"]),
    ("https://docs.pytest.org/", "pytest documentation", ["python", "testing"]),
    ("https://realpython.com/", "Real Python", ["python"]),
]

WIKI_TAGS = [
    "history",
    "science",
    "geography",
    "biography",
    "technology",
    "mathematics",
    "culture",
    "nature",
    "philosophy",
    "language",
    "politics",
    "art",
    "music",
    "literature",
    "sports",
]

WIKI_BOOKMARKS = [
    ("https://en.wikipedia.org/wiki/History_of_the_Internet", "History of the Internet", ["history", "technology"]),
    ("https://en.wikipedia.org/wiki/Alan_Turing", "Alan Turing", ["biography", "mathematics", "science"]),
    ("https://en.wikipedia.org/wiki/World_Wide_Web", "World Wide Web", ["technology", "history"]),
    ("https://en.wikipedia.org/wiki/Linux", "Linux", ["technology"]),
    ("https://en.wikipedia.org/wiki/SQL", "SQL", ["technology", "mathematics"]),
    ("https://en.wikipedia.org/wiki/Algorithm", "Algorithm", ["mathematics", "science"]),
    ("https://en.wikipedia.org/wiki/Machine_learning", "Machine learning", ["science", "technology"]),
    ("https://en.wikipedia.org/wiki/Albert_Einstein", "Albert Einstein", ["biography", "science"]),
    ("https://en.wikipedia.org/wiki/Himalayas", "Himalayas", ["geography", "nature"]),
    ("https://en.wikipedia.org/wiki/Tokyo", "Tokyo", ["geography", "culture"]),
    ("https://en.wikipedia.org/wiki/Open_source", "Open source", ["technology", "culture"]),
    ("https://en.wikipedia.org/wiki/Cryptography", "Cryptography", ["mathematics", "technology"]),
    ("https://en.wikipedia.org/wiki/HTTP", "HTTP", ["technology"]),
    ("https://en.wikipedia.org/wiki/Wikipedia", "Wikipedia", ["culture", "language"]),
    ("https://en.wikipedia.org/wiki/Philosophy", "Philosophy", ["philosophy"]),
    ("https://en.wikipedia.org/wiki/The_Odyssey", "The Odyssey", ["literature", "history"]),
    ("https://en.wikipedia.org/wiki/Football", "Football", ["sports"]),
    ("https://en.wikipedia.org/wiki/Jazz", "Jazz", ["music", "art", "culture"]),
]


def _clear(db):
    for table in reversed(Base.metadata.sorted_tables):
        if table.name == "alembic_version":
            continue
        db.execute(table.delete())
    db.commit()


def _tags(db, names: list[str]) -> dict[str, Tag]:
    by_name: dict[str, Tag] = {}
    for name in names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        by_name[name] = tag
    return by_name


def _user(db, email: str, name: str, bio: str, tag_names: list[str], bookmarks: list[tuple]) -> None:
    user = User(
        email=email,
        password=hash_password("Test@123"),
        name=name,
        bio=bio,
    )
    db.add(user)
    db.flush()
    tags = _tags(db, tag_names)
    user.tags.extend(tags[name] for name in tag_names)
    for url, title, bookmark_tag_names in bookmarks:
        bookmark = Bookmark(url=url, title=title, user_id=user.id)
        bookmark.tags.extend(tags[name] for name in bookmark_tag_names)
        db.add(bookmark)


def seed() -> None:
    db = local_session()
    try:
        _clear(db)
        _user(
            db,
            email="aayush@gmail.com",
            name="Aayush Maharjan",
            bio="Developer bookmarks: docs, books, and tooling.",
            tag_names=DEV_TAGS,
            bookmarks=DEV_BOOKMARKS,
        )
        _user(
            db,
            email="aayush2@gmail.com",
            name="Aayush Two",
            bio="Wikipedia rabbit holes.",
            tag_names=WIKI_TAGS,
            bookmarks=WIKI_BOOKMARKS,
        )
        db.commit()
        print("Seeded aayush@gmail.com and aayush2@gmail.com (password: Test@123)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
