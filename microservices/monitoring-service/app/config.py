"""Configuration for monitoring-service."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MONITORING_", extra="ignore")
    
    SERVICE_NAME: str = "monitoring-service"
    SERVICE_PORT: int = 8018
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/monitoring"
    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    OTEL_SERVICE_NAME: str = "monitoring-service"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    
    ALERT_CHECK_INTERVAL_SECONDS: int = 30
    HEALTH_CHECK_TIMEOUT_SECONDS: int = 5


settings = Settings()
