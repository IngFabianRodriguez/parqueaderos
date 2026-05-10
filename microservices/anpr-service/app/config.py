"""Application configuration — ANPR Service. No pydantic-settings."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    return int(os.environ.get(key, str(default)))


def _env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key, "").lower()
    if not val:
        return default
    return val in ("1", "true", "yes")


@dataclass
class Settings:
    """Configuración del servicio ANPR — plain Python dataclass."""

    # Service identity
    SERVICE_NAME: str = "anpr-service"
    SERVICE_PORT: int = 8006
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://parqueaderos:parqueaderos@localhost:5432/parqueaderos"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/2"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "anpr-service-consumers"
    KAFKA_TOPIC_ANPR_EVENTS: str = "anpr.plate-detected"

    # Security (JWT from API Gateway)
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    API_GATEWAY_URL: str = "http://localhost:8000"

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    OTEL_SERVICE_NAME: str = "anpr-service"
    OTEL_ENABLED: bool = True

    # ANPR/OCR (placeholder)
    LPR_MODEL_PATH: str = "/models/lprnet.onnx"
    LPR_CONFIDENCE_THRESHOLD: float = 0.7
    LPR_IMAGE_WIDTH: int = 640
    LPR_IMAGE_HEIGHT: int = 480


def get_settings() -> Settings:
    """Build Settings from environment variables with ANPR_ prefix."""
    return Settings(
        SERVICE_NAME=_env("ANPR_SERVICE_NAME", "anpr-service"),
        SERVICE_PORT=_env_int("ANPR_SERVICE_PORT", 8006),
        DEBUG=_env_bool("ANPR_DEBUG", False),
        DATABASE_URL=_env(
            "ANPR_DATABASE_URL",
            "postgresql+asyncpg://parqueaderos:parqueaderos@localhost:5432/parqueaderos",
        ),
        DB_POOL_SIZE=_env_int("ANPR_DB_POOL_SIZE", 10),
        DB_MAX_OVERFLOW=_env_int("ANPR_DB_MAX_OVERFLOW", 20),
        REDIS_URL=_env("ANPR_REDIS_URL", "redis://localhost:6379/2"),
        KAFKA_BOOTSTRAP_SERVERS=_env("ANPR_KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        KAFKA_CONSUMER_GROUP=_env("ANPR_KAFKA_CONSUMER_GROUP", "anpr-service-consumers"),
        KAFKA_TOPIC_ANPR_EVENTS=_env("ANPR_KAFKA_TOPIC_ANPR_EVENTS", "anpr.plate-detected"),
        JWT_SECRET_KEY=_env("ANPR_JWT_SECRET_KEY", "change-me-in-production"),
        JWT_ALGORITHM=_env("ANPR_JWT_ALGORITHM", "HS256"),
        API_GATEWAY_URL=_env("ANPR_API_GATEWAY_URL", "http://localhost:8000"),
        OTEL_EXPORTER_OTLP_ENDPOINT=_env("ANPR_OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        OTEL_SERVICE_NAME=_env("ANPR_OTEL_SERVICE_NAME", "anpr-service"),
        OTEL_ENABLED=_env_bool("ANPR_OTEL_ENABLED", True),
        LPR_MODEL_PATH=_env("ANPR_LPR_MODEL_PATH", "/models/lprnet.onnx"),
        LPR_CONFIDENCE_THRESHOLD=float(_env("ANPR_LPR_CONFIDENCE_THRESHOLD", "0.7")),
        LPR_IMAGE_WIDTH=_env_int("ANPR_LPR_IMAGE_WIDTH", 640),
        LPR_IMAGE_HEIGHT=_env_int("ANPR_LPR_IMAGE_HEIGHT", 480),
    )


settings = get_settings()