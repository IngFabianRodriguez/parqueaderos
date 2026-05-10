"""Configuration — IoT Service (env-based settings, no pydantic v2)."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any


class Settings:
    """Application settings loaded from environment variables."""

    SERVICE_NAME: str = "iot-service"
    SERVICE_PORT: int = 8004
    DEBUG: bool = False

    DATABASE_URL: str = (
        "postgresql+asyncpg://parqueaderos:parqueaderos@localhost:5432/parqueaderos"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    REDIS_URL: str = "redis://localhost:6379/1"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "iot-service-consumers"

    MQTT_BROKER_URL: str = "mqtt://localhost:1883"
    MQTT_USERNAME: str | None = None
    MQTT_PASSWORD: str | None = None
    MQTT_TOPIC_PREFIX: str = "parqueaderos/iot"

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    API_GATEWAY_URL: str = "http://localhost:8000"

    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    OTEL_SERVICE_NAME: str = "iot-service"
    OTEL_ENABLED: bool = True

    # Gate / barrier defaults
    GATE_COMMAND_TIMEOUT_SECONDS: int = 3
    GATE_AUTO_CLOSE_SECONDS: int = 5
    GATE_OFFLINE_THRESHOLD_SECONDS: int = 30

    # Alert defaults
    ALERT_ESCALATION_MINUTES: int = 5
    ALERT_CRITICAL_THRESHOLD_MINUTES: int = 30
    MAINTENANCE_FAILURE_WINDOW_HOURS: int = 24
    MAINTENANCE_FAILURE_THRESHOLD: int = 2

    class Config:
        extra = "ignore"


def _get_from_env(key: str, default: Any) -> Any:
    """Read env var with IOT_ prefix."""
    return os.environ.get(f"IOT_{key}", default)


@lru_cache
def get_settings() -> Settings:
    """Build Settings from env vars."""
    s = Settings()
    for name in dir(s):
        if name.isupper():
            env_key = f"IOT_{name}"
            val = os.environ.get(env_key)
            if val is not None:
                # Typed conversion
                orig = getattr(Settings, name, None)
                if orig is not None:
                    # Use the class attribute type hint
                    pass
                try:
                    if isinstance(getattr(Settings, name), int):
                        val = int(val)
                    elif isinstance(getattr(Settings, name), bool):
                        val = val.lower() in ("1", "true", "yes")
                except (ValueError, TypeError):
                    pass
                setattr(s, name, val)
    return s


settings = get_settings()