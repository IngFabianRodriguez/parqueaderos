"""Application configuration from environment variables."""
import os

_settings = None


class Settings:
    """Plain Python settings — reads from environment variables."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://parqueaderos:password@localhost:5432/parqueaderos"
    )
    # Aliases used by different services
    database_url: str = DATABASE_URL
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "tenant-service")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317")
    OTEL_ENABLED: bool = os.getenv("OTEL_ENABLED", "true").lower() == "true"
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "tenant-service")
    GATEWAY_URL: str = os.getenv("GATEWAY_URL", "http://api-gateway:8000")

    def __init__(self):
        global _settings
        _settings = self
        # Sync DATABASE_URL -> database_url
        if not hasattr(self, 'database_url') or not self.database_url:
            self.database_url = self.DATABASE_URL

    def __getattr__(self, name: str):
        return os.getenv(name.upper(), getattr(self.__class__, name, None))


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


settings = get_settings()