"""Dataclass schemas (POPOs) — IoT Service. No pydantic v2."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ── Device ────────────────────────────────────────────────────────────────────


@dataclass
class IoTDeviceBase:
    name: str
    device_type: str
    serial_number: str
    sede_id: uuid.UUID


@dataclass
class IoTDeviceCreate(IoTDeviceBase):
    mac_address: str | None = None
    ip_address: str | None = None
    config: dict | None = None


@dataclass
class IoTDeviceUpdate:
    name: str | None = None
    is_online: bool | None = None
    config: dict | None = None
    firmware_version: str | None = None


@dataclass
class IoTDeviceResponse(IoTDeviceBase):
    id: uuid.UUID
    is_online: bool
    last_seen: datetime | None
    firmware_version: str | None
    created_at: datetime
    updated_at: datetime
    mac_address: str | None = None
    ip_address: str | None = None

    @classmethod
    def from_model(cls, model) -> IoTDeviceResponse:
        return cls(
            id=model.id,
            name=model.name,
            device_type=model.device_type,
            serial_number=model.serial_number,
            sede_id=model.sede_id,
            mac_address=model.mac_address,
            ip_address=model.ip_address,
            is_online=model.is_online,
            last_seen=model.last_seen,
            firmware_version=model.firmware_version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# ── Event ──────────────────────────────────────────────────────────────────────


@dataclass
class IoTEventBase:
    device_id: uuid.UUID
    event_type: str
    payload: dict | None = None


@dataclass
class IoTEventCreate(IoTEventBase):
    confidence: int | None = None


@dataclass
class IoTEventResponse(IoTEventBase):
    id: uuid.UUID
    confidence: int | None
    timestamp: datetime
    processed: bool
    created_at: datetime

    @classmethod
    def from_model(cls, model) -> IoTEventResponse:
        return cls(
            id=model.id,
            device_id=model.device_id,
            event_type=model.event_type,
            payload=model.payload,
            confidence=model.confidence,
            timestamp=model.timestamp,
            processed=model.processed,
            created_at=model.created_at,
        )


# ── Command ────────────────────────────────────────────────────────────────────


@dataclass
class IoTCommandBase:
    device_id: uuid.UUID
    command_type: str
    params: dict | None = None


@dataclass
class IoTCommandCreate(IoTCommandBase):
    pass


@dataclass
class IoTCommandResponse(IoTCommandBase):
    id: uuid.UUID
    status: str
    sent_at: datetime | None
    acknowledged_at: datetime | None
    created_at: datetime
    created_by: str

    @classmethod
    def from_model(cls, model) -> IoTCommandResponse:
        return cls(
            id=model.id,
            device_id=model.device_id,
            command_type=model.command_type,
            params=model.params,
            status=model.status,
            sent_at=model.sent_at,
            acknowledged_at=model.acknowledged_at,
            created_at=model.created_at,
            created_by=model.created_by,
        )


# ── Gate / Talanquera (RF-018 – RF-022) ────────────────────────────────────────

# Gate status enum as dataclass-like
class GateStatus:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"
    BLOCKED = "BLOCKED"


@dataclass
class GateCommandCreate:
    gate_id: uuid.UUID
    tipo_comando: str  # OPEN, CLOSE, MANUAL_OPEN, RESET
    sede_id: uuid.UUID
    originator_type: str  # system, operator, admin, superadmin
    originator_id: str
    originator_ip: str
    motivo_codigo: str | None = None
    motivo_descripcion: str | None = None
    entrada_id: uuid.UUID | None = None
    salida_id: uuid.UUID | None = None
    session_token: str | None = None


@dataclass
class GateCommandResponse:
    comando_id: uuid.UUID
    tipo_comando: str
    gate_id: uuid.UUID
    sede_id: uuid.UUID
    originator_type: str
    originator_id: str
    originator_ip: str
    motivo_codigo: str | None
    motivo_descripcion: str | None
    timestamp_solicitud: datetime
    timestamp_envio: datetime | None
    timestamp_resultado: datetime | None
    resultado: str  # PENDING, SUCCESS, FAILED, TIMEOUT
    error_code: str | None
    error_description: str | None
    device_response_time_ms: int | None
    timestamp_apertura_confirmada: datetime | None
    timestamp_cierre_confirmada: datetime | None
    created_at: datetime

    @classmethod
    def from_model(cls, model) -> GateCommandResponse:
        return cls(
            comando_id=model.id,
            tipo_comando=model.tipo_comando,
            gate_id=model.gate_id,
            sede_id=model.sede_id,
            originator_type=model.originator_type,
            originator_id=model.originator_id,
            originator_ip=model.originator_ip,
            motivo_codigo=model.motivo_codigo,
            motivo_descripcion=model.motivo_descripcion,
            timestamp_solicitud=model.timestamp_solicitud,
            timestamp_envio=model.timestamp_envio,
            timestamp_resultado=model.timestamp_resultado,
            resultado=model.resultado,
            error_code=model.error_code,
            error_description=model.error_description,
            device_response_time_ms=model.device_response_time_ms,
            timestamp_apertura_confirmada=model.timestamp_apertura_confirmada,
            timestamp_cierre_confirmada=model.timestamp_cierre_confirmada,
            created_at=model.created_at,
        )


@dataclass
class ManualOpenRequest:
    gate_id: uuid.UUID
    operador_id: uuid.UUID
    sede_id: uuid.UUID
    motivo_codigo: str
    motivo_descripcion: str
    placa_vehiculo: str | None = None
    confirmacion_operador: bool = True


@dataclass
class ManualOpenResponse:
    command_id: uuid.UUID
    gate_status: str
    timestamp_apertura: datetime | None
    timestamp_cierre_programado: datetime | None
    auditoria_id: uuid.UUID
    mensaje_error: str | None = None


@dataclass
class GateStatusResponse:
    gate_id: uuid.UUID
    gate_name: str
    sede_id: uuid.UUID
    current_status: str
    last_heartbeat: datetime | None
    last_command_timestamp: datetime | None
    last_command_type: str | None
    error_description: str | None
    uptime_hours: int | None
    battery_level: int | None

    @classmethod
    def from_model(cls, model) -> GateStatusResponse:
        return cls(
            gate_id=model.id,
            gate_name=model.name,
            sede_id=model.sede_id,
            current_status=model.current_status,
            last_heartbeat=model.last_heartbeat,
            last_command_timestamp=model.last_command_timestamp,
            last_command_type=model.last_command_type,
            error_description=model.error_description,
            uptime_hours=model.uptime_hours,
            battery_level=model.battery_level,
        )


# ── Alert (RF-022) ──────────────────────────────────────────────────────────────


@dataclass
class AlertCreate:
    gate_id: uuid.UUID
    sede_id: uuid.UUID
    tipo_falla: str
    comando_id: uuid.UUID
    timestamp_falla: datetime
    severity: str  # CRITICAL, HIGH, MEDIUM
    device_status: str
    intentos_anteriores: int = 0


@dataclass
class AlertResponse:
    alert_id: uuid.UUID
    gate_id: uuid.UUID
    gate_name: str | None
    sede_id: uuid.UUID
    sede_name: str | None
    tipo_falla: str
    descripcion: str
    timestamp_inicio: datetime
    timestamp_resolucion: datetime | None
    duracion_minutos: int | None
    estado: str  # ACTIVA, RESUELTA, ESCALADA
    resolucion_por: str | None
    nota_resolucion: str | None
    notificacion_enviada: bool

    @classmethod
    def from_model(cls, model) -> AlertResponse:
        return cls(
            alert_id=model.id,
            gate_id=model.gate_id,
            gate_name=getattr(model, "gate_name", None),
            sede_id=model.sede_id,
            sede_name=getattr(model, "sede_name", None),
            tipo_falla=model.tipo_falla,
            descripcion=model.descripcion,
            timestamp_inicio=model.timestamp_inicio,
            timestamp_resolucion=model.timestamp_resolucion,
            duracion_minutos=model.duracion_minutos,
            estado=model.estado,
            resolucion_por=model.resolucion_por,
            nota_resolucion=model.nota_resolucion,
            notificacion_enviada=model.notificacion_enviada,
        )


# ── Heartbeat (RF-020) ─────────────────────────────────────────────────────────


@dataclass
class DeviceHeartbeatRequest:
    device_id: uuid.UUID
    gate_id: uuid.UUID
    relay_state: bool
    arm_position: str  # up, down, moving
    battery_voltage: float | None = None
    signal_strength: int | None = None
    temperature: float | None = None
    timestamp: datetime
    error_code: str | None = None


# ── Audit log entry ─────────────────────────────────────────────────────────────


@dataclass
class AuditLogEntry:
    id: uuid.UUID
    timestamp: datetime
    action: str
    actor_type: str  # system, operator, admin, superadmin
    actor_id: str
    resource_type: str
    resource_id: str
    details: dict | None
    ip_address: str | None