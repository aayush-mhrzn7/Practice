from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import MetaData, create_engine
import os
from dotenv import load_dotenv

load_dotenv()


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

DATABASE_URL = os.getenv("DATABASE_URL") or ""
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base(metadata=MetaData(naming_convention=NAMING_CONVENTION))


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
