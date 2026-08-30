from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import get_settings

settings = get_settings()
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def _sqlite_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


local_session = sessionmaker(engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()


def get_db():
    try:
        db = local_session()
        yield db
    finally:
        db.close()
