from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore")
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    CSRF_SECRET_KEY: str
    PROD: bool

@lru_cache
def get_settings():
    return Settings()