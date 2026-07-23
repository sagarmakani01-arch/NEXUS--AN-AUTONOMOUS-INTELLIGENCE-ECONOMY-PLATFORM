import os
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "NEXUS"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR.parent / 'nexus.db'}"
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False

    SECRET_KEY: str = "nexus-dev-secret-key-not-for-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440

    CORS_ORIGINS: list[str] = ["http://localhost:3001"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
