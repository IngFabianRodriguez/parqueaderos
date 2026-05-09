"""Application configuration from environment variables."""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "production", "testing"] = "development"
    service_name: str = "reports-service"
    service_port: int = 8015
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
    kafka_group_id: str = "reports-service-group"
    kafka_auto_offset_reset: Literal["earliest", "latest"] = "earliest"

    # JWT / Security
    jwt_secret_key: str = "changeme-in-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "parqueaderos-gateway"

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = "http://jaeger:4317"
    otel_service_name: str = "reports-service"
    otel_enabled: bool = True

    # External Services
    gateway_url: str = "http://api-gateway:8000"
    auth_service_url: str = "http://auth-service:8001"

    # S3 / Storage
    s3_endpoint_url: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_reports: str = "reports"


settings = Settings()