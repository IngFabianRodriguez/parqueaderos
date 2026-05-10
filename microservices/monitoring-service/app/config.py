"""Configuration for monitoring-service — env-based settings with pydantic v1."""
from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    SERVICE_NAME: str = "monitoring-service"
    SERVICE_PORT: int = 8018

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/monitoring"
    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    OTEL_SERVICE_NAME: str = "monitoring-service"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    ALERT_CHECK_INTERVAL_SECONDS: int = 30
    HEALTH_CHECK_TIMEOUT_SECONDS: int = 5

    class Config:
        extra = "ignore"


def _get_from_env(key: str, default: Any) -> Any:
    """Read env var with MONITORING_ prefix."""
    return os.environ.get(f"MONITORING_{key}", default)


def get_settings() -> Settings:
    """Build Settings from env vars — each field checks its own env var."""
    return Settings(
        SERVICE_NAME=os.environ.get("MONITORING_SERVICE_NAME", "monitoring-service"),
        SERVICE_PORT=int(os.environ.get("MONITORING_SERVICE_PORT", "8018")),
        DATABASE_URL=os.environ.get(
            "MONITORING_DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/monitoring",
        ),
        REDIS_URL=os.environ.get("MONITORING_REDIS_URL", "redis://localhost:6379/0"),
        KAFKA_BOOTSTRAP_SERVERS=os.environ.get(
            "MONITORING_KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        ),
        OTEL_SERVICE_NAME=os.environ.get("MONITORING_OTEL_SERVICE_NAME", "monitoring-service"),
        OTEL_EXPORTER_OTLP_ENDPOINT=os.environ.get(
            "MONITORING_OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
        ),
        ALERT_CHECK_INTERVAL_SECONDS=int(
            os.environ.get("MONITORING_ALERT_CHECK_INTERVAL_SECONDS", "30")
        ),
        HEALTH_CHECK_TIMEOUT_SECONDS=int(
            os.environ.get("MONITORING_HEALTH_CHECK_TIMEOUT_SECONDS", "5")
        ),
    )


settings = get_settings()