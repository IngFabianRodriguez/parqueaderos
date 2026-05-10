"""Application configuration from environment variables.

No pydantic - pure Python dataclasses.
"""

import os
from dataclasses import dataclass, field
from typing import Literal


def _get_env(key: str, default: str = "") -> str:
    """Get environment variable or return default."""
    return os.environ.get(key, default)


def _get_int_env(key: str, default: int) -> int:
    """Get integer environment variable."""
    val = os.environ.get(key)
    return int(val) if val is not None else default


def _get_bool_env(key: str, default: bool) -> bool:
    """Get boolean environment variable."""
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes", "on")


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/parqueaderos"
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30


@dataclass
class RedisConfig:
    """Redis configuration."""
    url: str = "redis://redis:6379/0"
    pool_size: int = 10


@dataclass
class KafkaConfig:
    """Kafka configuration."""
    bootstrap_servers: str = "kafka:9092"
    group_id: str = "auth-service-group"
    auto_offset_reset: Literal["earliest", "latest"] = "earliest"


@dataclass
class JWTConfig:
    """JWT security configuration."""
    secret_key: str = "changeme-in-production"
    algorithm: str = "HS256"
    issuer: str = "parqueaderos-gateway"


@dataclass
class OtelConfig:
    """OpenTelemetry configuration."""
    exporter_otlp_endpoint: str = "http://jaeger:4317"
    service_name: str = "auth-service"
    enabled: bool = True


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    app_env: Literal["development", "production", "testing"] = "development"
    service_name: str = "auth-service"
    service_port: int = 8001
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
    kafka_group_id: str = "auth-service-group"
    kafka_auto_offset_reset: Literal["earliest", "latest"] = "earliest"

    # JWT / Security
    jwt_secret_key: str = "changeme-in-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "parqueaderos-gateway"

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = "http://jaeger:4317"
    otel_service_name: str = "auth-service"
    otel_enabled: bool = True

    # External Services
    gateway_url: str = "http://api-gateway:8000"

    # Token expiration
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    def __post_init__(self):
        """Post-initialization processing."""
        self.app_env = os.environ.get("APP_ENV", "development")
        self.service_name = os.environ.get("SERVICE_NAME", "auth-service")
        self.service_port = _get_int_env("SERVICE_PORT", 8001)
        self.debug = _get_bool_env("DEBUG", False)

        # Database
        self.database_url = os.environ.get(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@postgres:5432/parqueaderos"
        )
        self.db_pool_size = _get_int_env("DB_POOL_SIZE", 20)
        self.db_max_overflow = _get_int_env("DB_MAX_OVERFLOW", 10)
        self.db_pool_timeout = _get_int_env("DB_POOL_TIMEOUT", 30)

        # Redis
        self.redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
        self.redis_pool_size = _get_int_env("REDIS_POOL_SIZE", 10)

        # Kafka
        self.kafka_bootstrap_servers = os.environ.get(
            "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
        )
        self.kafka_group_id = os.environ.get("KAFKA_GROUP_ID", "auth-service-group")
        self.kafka_auto_offset_reset = os.environ.get(
            "KAFKA_AUTO_OFFSET_RESET", "earliest"
        )

        # JWT
        self.jwt_secret_key = os.environ.get("JWT_SECRET_KEY", "changeme-in-production")
        self.jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
        self.jwt_issuer = os.environ.get("JWT_ISSUER", "parqueaderos-gateway")

        # OpenTelemetry
        self.otel_exporter_otlp_endpoint = os.environ.get(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317"
        )
        self.otel_service_name = os.environ.get("OTEL_SERVICE_NAME", "auth-service")
        self.otel_enabled = _get_bool_env("OTEL_ENABLED", True)

        # External
        self.gateway_url = os.environ.get("GATEWAY_URL", "http://api-gateway:8000")

        # Token expiration
        self.access_token_expire_minutes = _get_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        self.refresh_token_expire_days = _get_int_env("REFRESH_TOKEN_EXPIRE_DAYS", 7)


settings = Settings()