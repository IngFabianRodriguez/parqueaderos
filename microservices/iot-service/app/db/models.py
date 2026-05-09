"""SQLAlchemy models — IoT Service."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models — provides tenant_id on all tables."""

    pass


class TenantMixin:
    """Adds tenant_id to any model."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )


class IoTDevice(TenantMixin, Base):
    """IoT Device (barrier, sensor, camera, etc.)."""

    __tablename__ = "iot_devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)  # barrier, sensor, camera, display
    serial_number: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    mac_address: Mapped[str | None] = mapped_column(String(17), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    sede_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sedes.id"), nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    config: Mapped[dict | None] = mapped_column(Text, nullable=True)  # JSON config
    firmware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    events: Mapped[list["IoTEvent"]] = relationship("IoTEvent", back_populates="device", cascade="all, delete-orphan")


class IoTEvent(TenantMixin, Base):
    """IoT Event / Telemetry log."""

    __tablename__ = "iot_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("iot_devices.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # entry, exit, barrier_trigger, etc.
    payload: Mapped[dict | None] = mapped_column(Text, nullable=True)  # JSON payload
    confidence: Mapped[float | None] = mapped_column(Integer, nullable=True)  # 0-100
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    device: Mapped["IoTDevice"] = relationship("IoTDevice", back_populates="events")


class IoTCommand(TenantMixin, Base):
    """Command sent to an IoT device (open barrier, etc.)."""

    __tablename__ = "iot_commands"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("iot_devices.id"), nullable=False, index=True)
    command_type: Mapped[str] = mapped_column(String(100), nullable=False)  # open_barrier, close_barrier, etc.
    params: Mapped[dict | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending, sent, acknowledged, failed
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)