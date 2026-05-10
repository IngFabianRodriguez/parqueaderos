"""Application configuration from environment variables."""

import os
from typing import Literal


def _get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


class Settings:
    """Application settings loaded from environment variables."""

    app_env: Literal["development", "production", "testing"] = "development"
    service_name: str = "notification-service"
    service_port: int = 8007
    debug: bool = False

    # Database
    database_url: str = _get_env(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/parqueaderos"
    )
    db_pool_size: int = int(_get_env("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(_get_env("DB_MAX_OVERFLOW", "10"))
    db_pool_timeout: int = int(_get_env("DB_POOL_TIMEOUT", "30"))

    # Redis
    redis_url: str = _get_env("REDIS_URL", "redis://localhost:6379/0")
    redis_pool_size: int = int(_get_env("REDIS_POOL_SIZE", "10"))

    # Kafka
    kafka_bootstrap_servers: str = _get_env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_group_id: str = "notification-service-group"
    kafka_auto_offset_reset: Literal["earliest", "latest"] = "earliest"

    # JWT / Security
    jwt_secret_key: str = _get_env("JWT_SECRET_KEY", "changeme-in-production")
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "parqueaderos-gateway"

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = _get_env("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    otel_service_name: str = "notification-service"
    otel_enabled: bool = _get_env("OTEL_ENABLED", "true").lower() in ("true", "1", "yes")

    # External Services
    gateway_url: str = _get_env("GATEWAY_URL", "http://localhost:8000")

    # Email (SMTP)
    smtp_host: str = _get_env("SMTP_HOST", "smtp.example.com")
    smtp_port: int = int(_get_env("SMTP_PORT", "587"))
    smtp_user: str = _get_env("SMTP_USER", "")
    smtp_password: str = _get_env("SMTP_PASSWORD", "")

    # Push notifications (Firebase)
    firebase_credentials: str = _get_env("FIREBASE_CREDENTIALS", "")

    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: float = 1.0


settings = Settings()