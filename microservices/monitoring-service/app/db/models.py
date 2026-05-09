"""SQLAlchemy models for monitoring-service."""
from sqlalchemy import Column, String, DateTime, JSON, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

# Base model with tenant_id for multi-tenancy
class BaseModel:
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


from sqlalchemy.orm import declarative_base
Base = declarative_base()


class AlertRule(Base, BaseModel):
    __tablename__ = "alert_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    condition = Column(JSON, nullable=False)  # e.g., {"metric": "cpu", "op": "gt", "threshold": 80}
    severity = Column(String(50), nullable=False)  # critical, warning, info
    enabled = Column(Boolean, default=True)
    cooldowm_seconds = Column(Integer, default=300)


class Alert(Base, BaseModel):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), nullable=True)
    service_id = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    message = Column(String(500), nullable=False)
    metadata = Column(JSON, default={})
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)


class ServiceHealth(Base, BaseModel):
    __tablename__ = "service_health"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(String(100), nullable=False, unique=True)
    status = Column(String(50), nullable=False)  # healthy, degraded, down
    latency_ms = Column(Integer, nullable=True)
    metadata = Column(JSON, default={})
    last_check = Column(DateTime(timezone=True), nullable=False)
