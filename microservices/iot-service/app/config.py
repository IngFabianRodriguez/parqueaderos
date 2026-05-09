"""Application configuration — IoT Service."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración del servicio IoT."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service
    SERVICE_NAME: str = "iot-service"
    SERVICE_PORT: int = 8004
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://parqueaderos:parqueaderos@localhost:5432/parqueaderos"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/1"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "iot-service-consumers"

    # MQTT
    MQTT_BROKER_URL: str = "mqtt://localhost:1883"
    MQTT_USERNAME: str | None = None
    MQTT_PASSWORD: str | None = None
    MQTT_TOPIC_PREFIX: str = "parqueaderos/iot"

    # Security (JWT from API Gateway)
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    API_GATEWAY_URL: str = "http://localhost:8000"

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    OTEL_SERVICE_NAME: str = "iot-service"
    OTEL_ENABLED: bool = True


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()