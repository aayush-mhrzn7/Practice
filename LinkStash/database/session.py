from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL,echo=True,connect_args={"check_same_thread": False},pool_pre_ping=True)
local_session = sessionmaker(engine,autoflush=False,autocommit=False)

def get_db():
    try:
        db = local_session()
        yield db
    finally:
        db.close()

