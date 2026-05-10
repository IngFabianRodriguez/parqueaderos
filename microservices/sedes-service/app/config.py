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
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "sedes-service")
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


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Literal["development", "production", "testing"] = "development"
    service_name: str = "sedes-service"
    service_port: int = 8003
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/parqueaderos"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    # Redis
    redis_url: str = "redis://redis:6379/0"
    redis_pool_size: int = 10

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_group_id: str = "sedes-service-group"
    kafka_auto_offset_reset: Literal["earliest", "latest"] = "earliest"

    # JWT / Security
    jwt_secret_key: str = "changeme-in-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "parqueaderos-gateway"

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = "http://jaeger:4317"
    otel_service_name: str = "sedes-service"
    otel_enabled: bool = True

    # External Services
    gateway_url: str = "http://api-gateway:8000"


settings = Settings()