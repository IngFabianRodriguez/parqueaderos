"""SQLAlchemy models — IoT Service (RF-018 to RF-022)."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class TenantMixin:
    """Adds tenant_id to any model."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )


# ── Core IoT Models ─────────────────────────────────────────────────────────────

class IoTDevice(TenantMixin, Base):
    """IoT Device (barrier, sensor, camera, etc.)."""

    __tablename__ = "iot_devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # barrier, sensor, camera, display
    serial_number: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    mac_address: Mapped[str | None] = mapped_column(String(17), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    sede_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sedes.id"), nullable=False
    )
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    config: Mapped[dict | None] = mapped_column(Text, nullable=True)  # JSON config
    firmware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    events: Mapped[list["IoTEvent"]] = relationship(
        "IoTEvent", back_populates="device", cascade="all, delete-orphan"
    )
    commands: Mapped[list["IoTCommand"]] = relationship(
        "IoTCommand", back_populates="device", cascade="all, delete-orphan"
    )
    gate_commands: Mapped[list["GateCommand"]] = relationship(
        "GateCommand", back_populates="gate", cascade="all, delete-orphan"
    )


class IoTEvent(TenantMixin, Base):
    """IoT Event / Telemetry log."""

    __tablename__ = "iot_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("iot_devices.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # entry, exit, barrier_trigger, etc.
    payload: Mapped[dict | None] = mapped_column(Text, nullable=True)  # JSON payload
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    device: Mapped["IoTDevice"] = relationship(
        "IoTDevice", back_populates="events"
    )


class IoTCommand(TenantMixin, Base):
    """Command sent to an IoT device (open barrier, etc.)."""

    __tablename__ = "iot_commands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("iot_devices.id"), nullable=False, index=True
    )
    command_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # open_barrier, close_barrier, etc.
    params: Mapped[dict | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True
    )  # pending, sent, acknowledged, failed
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)

    device: Mapped["IoTDevice"] = relationship("IoTDevice", back_populates="commands")


# ── Gate / Talanquera (RF-018 – RF-022) ────────────────────────────────────────

class Gate(TenantMixin, Base):
    """Gate/Talanquera — logical representation of a barrier."""

    __tablename__ = "gates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gate_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # entry, exit
    sede_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sedes.id"), nullable=False
    )
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("iot_devices.id"), nullable=True
    )
    current_status: Mapped[str] = mapped_column(
        String(20), default="CLOSED"
    )  # CLOSED, OPEN, OPENING, CLOSING, ERROR, OFFLINE, BLOCKED
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_command_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    last_command_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    uptime_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    battery_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    commands: Mapped[list["GateCommand"]] = relationship(
        "GateCommand", back_populates="gate", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["GateAlert"]] = relationship(
        "GateAlert", back_populates="gate", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_gates_sede_id", "sede_id"),
        Index("ix_gates_status", "current_status"),
    )


class GateCommand(TenantMixin, Base):
    """Command sent to a gate — immutable audit log (RF-021)."""

    __tablename__ = "gate_commands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gates.id"), nullable=False, index=True
    )
    tipo_comando: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # OPEN, CLOSE, MANUAL_OPEN, RESET
    sede_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sedes.id"), nullable=False
    )
    originator_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # system, operator, admin, superadmin
    originator_id: Mapped[str] = mapped_column(String(255), nullable=False)
    originator_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    motivo_codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    motivo_descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    entrada_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    salida_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    timestamp_solicitud: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    timestamp_envio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timestamp_resultado: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    resultado: Mapped[str] = mapped_column(
        String(20), default="PENDING"
    )  # PENDING, SUCCESS, FAILED, TIMEOUT
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    device_response_time_ms: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    timestamp_apertura_confirmada: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    timestamp_cierre_confirmada: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    gate: Mapped["Gate"] = relationship("Gate", back_populates="commands")

    __table_args__ = (
        Index("ix_gate_commands_sede_timestamp", "sede_id", "timestamp_solicitud"),
        Index("ix_gate_commands_originator", "originator_id"),
        Index("ix_gate_commands_tipo", "tipo_comando"),
    )


class GateAlert(TenantMixin, Base):
    """Alert generated when a gate fails (RF-022)."""

    __tablename__ = "gate_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gates.id"), nullable=False, index=True
    )
    sede_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sedes.id"), nullable=False
    )
    tipo_falla: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # TIMEOUT_APERTURA, TIMEOUT_CIERRE, SENSOR_FALLA, etc.
    comando_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gate_commands.id"), nullable=True
    )
    timestamp_falla: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # CRITICAL, HIGH, MEDIUM
    device_status: Mapped[str] = mapped_column(String(50), nullable=True)
    intentos_anteriores: Mapped[int] = mapped_column(Integer, default=0)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp_resolucion: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    estado: Mapped[str] = mapped_column(
        String(20), default="ACTIVA"
    )  # ACTIVA, RESUELTA, ESCALADA
    resolucion_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nota_resolucion: Mapped[str | None] = mapped_column(Text, nullable=True)
    notificacion_enviada: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    gate: Mapped["Gate"] = relationship("Gate", back_populates="alerts")

    __table_args__ = (
        Index("ix_gate_alerts_sede_estado", "sede_id", "estado"),
        Index("ix_gate_alerts_timestamp", "timestamp_falla"),
    )


class GateStatusHistory(TenantMixin, Base):
    """Historical record of gate status changes (RF-020)."""

    __tablename__ = "gate_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gates.id"), nullable=False, index=True
    )
    previous_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)  # system/operator
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    __table_args__ = (Index("ix_gate_status_history_gate_timestamp", "gate_id", "timestamp"),)