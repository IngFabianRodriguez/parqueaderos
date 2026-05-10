"""Application configuration from environment variables."""

from typing import Literal
import os

_settings = None

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://parqueaderos:password@localhost:5432/parqueaderos"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "reports-service")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    def __init__(self):
        global _settings
        _settings = self

    def __getattr__(self, name: str):
        return os.getenv(name.upper(), getattr(self.__class__, name, None))


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


settings = get_settings()

