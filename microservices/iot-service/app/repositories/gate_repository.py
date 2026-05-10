"""Repositories — IoT Service. RF-018 to RF-022."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Sequence

from sqlalchemy import and_, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Gate,
    GateAlert,
    GateCommand,
    GateStatusHistory,
    IoTDevice,
    IoTEvent,
)


# ── Gate Repository ─────────────────────────────────────────────────────────────


class GateRepository:
    """Repository for Gate CRUD and status management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, gate_id: uuid.UUID, tenant_id: uuid.UUID) -> Gate | None:
        """Get a gate by ID for a tenant."""
        result = await self.session.execute(
            select(Gate).where(Gate.id == gate_id, Gate.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list_by_sede(
        self, sede_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Sequence[Gate]:
        """List all gates for a sede."""
        result = await self.session.execute(
            select(Gate)
            .where(Gate.sede_id == sede_id, Gate.tenant_id == tenant_id)
            .order_by(Gate.name)
        )
        return result.scalars().all()

    async def list_all(
        self, tenant_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> Sequence[Gate]:
        """List all gates for a tenant."""
        result = await self.session.execute(
            select(Gate)
            .where(Gate.tenant_id == tenant_id)
            .order_by(Gate.name)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        tenant_id: uuid.UUID,
        name: str,
        gate_type: str,
        sede_id: uuid.UUID,
        device_id: uuid.UUID | None = None,
    ) -> Gate:
        """Create a new gate."""
        gate = Gate(
            tenant_id=tenant_id,
            name=name,
            gate_type=gate_type,
            sede_id=sede_id,
            device_id=device_id,
            current_status="CLOSED",
        )
        self.session.add(gate)
        await self.session.flush()
        await self.session.refresh(gate)
        return gate

    async def update_status(
        self,
        gate_id: uuid.UUID,
        tenant_id: uuid.UUID,
        new_status: str,
        error_description: str | None = None,
        changed_by: str | None = None,
        reason: str | None = None,
    ) -> Gate | None:
        """Update gate status and record history."""
        gate = await self.get_by_id(gate_id, tenant_id)
        if not gate:
            return None

        previous_status = gate.current_status

        gate.current_status = new_status
        gate.last_command_timestamp = datetime.utcnow()

        if new_status == "ERROR" and error_description:
            gate.error_description = error_description
        elif new_status == "CLOSED":
            gate.error_description = None

        if new_status in ("CLOSED", "OPEN"):
            gate.is_blocked = False
            gate.blocked_reason = None

        self.session.add(gate)
        await self.session.flush()

        # Record status change history
        history = GateStatusHistory(
            tenant_id=tenant_id,
            gate_id=gate_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason,
        )
        self.session.add(history)
        await self.session.flush()

        return gate

    async def mark_online(self, gate_id: uuid.UUID, tenant_id: uuid.UUID) -> Gate | None:
        """Mark gate as online and update last_heartbeat."""
        gate = await self.get_by_id(gate_id, tenant_id)
        if not gate:
            return None
        gate.is_online = True
        gate.last_heartbeat = datetime.utcnow()
        if gate.current_status == "OFFLINE":
            gate.current_status = "CLOSED"
        await self.session.flush()
        return gate

    async def mark_offline(self, gate_id: uuid.UUID, tenant_id: uuid.UUID) -> Gate | None:
        """Mark gate as offline (no heartbeat received)."""
        gate = await self.get_by_id(gate_id, tenant_id)
        if not gate:
            return None
        if gate.current_status not in ("OFFLINE", "ERROR"):
            gate.current_status = "OFFLINE"
        await self.session.flush()
        return gate

    async def block(
        self,
        gate_id: uuid.UUID,
        tenant_id: uuid.UUID,
        reason: str,
        changed_by: str | None = None,
    ) -> Gate | None:
        """Block a gate (security lock — no auto commands accepted)."""
        gate = await self.get_by_id(gate_id, tenant_id)
        if not gate:
            return None
        gate.is_blocked = True
        gate.blocked_reason = reason
        gate.blocked_at = datetime.utcnow()
        gate.current_status = "BLOCKED"
        await self.session.flush()
        return gate

    async def unblock(self, gate_id: uuid.UUID, tenant_id: uuid.UUID) -> Gate | None:
        """Unblock a gate after manual verification."""
        gate = await self.get_by_id(gate_id, tenant_id)
        if not gate:
            return None
        gate.is_blocked = False
        gate.blocked_reason = None
        gate.blocked_at = None
        gate.current_status = "CLOSED"
        gate.error_description = None
        await self.session.flush()
        return gate

    async def get_status_history(
        self, gate_id: uuid.UUID, tenant_id: uuid.UUID, hours: int = 24
    ) -> Sequence[GateStatusHistory]:
        """Get status change history for a gate."""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(GateStatusHistory)
            .where(
                GateStatusHistory.gate_id == gate_id,
                GateStatusHistory.tenant_id == tenant_id,
                GateStatusHistory.timestamp >= since,
            )
            .order_by(desc(GateStatusHistory.timestamp))
        )
        return result.scalars().all()

    async def update_last_heartbeat(
        self, gate_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Gate | None:
        """Update last_heartbeat timestamp from device heartbeat."""
        gate = await self.get_by_id(gate_id, tenant_id)
        if not gate:
            return None
        gate.last_heartbeat = datetime.utcnow()
        if gate.current_status == "OFFLINE":
            gate.current_status = "CLOSED"
        await self.session.flush()
        return gate


# ── GateCommand Repository (RF-021) ─────────────────────────────────────────────


class GateCommandRepository:
    """Repository for gate command audit logs — immutable append-only."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: uuid.UUID,
        gate_id: uuid.UUID,
        tipo_comando: str,
        sede_id: uuid.UUID,
        originator_type: str,
        originator_id: str,
        originator_ip: str,
        motivo_codigo: str | None = None,
        motivo_descripcion: str | None = None,
        entrada_id: uuid.UUID | None = None,
        salida_id: uuid.UUID | None = None,
    ) -> GateCommand:
        """Create a new gate command record (pre-command audit)."""
        cmd = GateCommand(
            tenant_id=tenant_id,
            gate_id=gate_id,
            tipo_comando=tipo_comando,
            sede_id=sede_id,
            originator_type=originator_type,
            originator_id=originator_id,
            originator_ip=originator_ip,
            motivo_codigo=motivo_codigo,
            motivo_descripcion=motivo_descripcion,
            entrada_id=entrada_id,
            salida_id=salida_id,
            timestamp_solicitud=datetime.utcnow(),
            resultado="PENDING",
        )
        self.session.add(cmd)
        await self.session.flush()
        await self.session.refresh(cmd)
        return cmd

    async def get_by_id(
        self, comando_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> GateCommand | None:
        """Get a command by ID."""
        result = await self.session.execute(
            select(GateCommand).where(
                GateCommand.id == comando_id, GateCommand.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def update_result(
        self,
        comando_id: uuid.UUID,
        tenant_id: uuid.UUID,
        resultado: str,
        error_code: str | None = None,
        error_description: str | None = None,
        device_response_time_ms: int | None = None,
        timestamp_apertura_confirmada: datetime | None = None,
        timestamp_cierre_confirmada: datetime | None = None,
    ) -> GateCommand | None:
        """Update command result after device responds."""
        cmd = await self.get_by_id(comando_id, tenant_id)
        if not cmd:
            return None
        cmd.resultado = resultado
        cmd.timestamp_resultado = datetime.utcnow()
        cmd.timestamp_envio = cmd.timestamp_solicitud  # TODO: separate send time
        if error_code:
            cmd.error_code = error_code
        if error_description:
            cmd.error_description = error_description
        if device_response_time_ms is not None:
            cmd.device_response_time_ms = device_response_time_ms
        if timestamp_apertura_confirmada:
            cmd.timestamp_apertura_confirmada = timestamp_apertura_confirmada
        if timestamp_cierre_confirmada:
            cmd.timestamp_cierre_confirmada = timestamp_cierre_confirmada
        await self.session.flush()
        return cmd

    async def list_by_sede(
        self,
        sede_id: uuid.UUID,
        tenant_id: uuid.UUID,
        tipo_comando: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[GateCommand]:
        """List commands for a sede."""
        query = select(GateCommand).where(
            GateCommand.sede_id == sede_id, GateCommand.tenant_id == tenant_id
        )
        if tipo_comando:
            query = query.where(GateCommand.tipo_comando == tipo_comando)
        query = query.order_by(desc(GateCommand.timestamp_solicitud)).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_by_originator(
        self, originator_id: str, tenant_id: uuid.UUID, limit: int = 50
    ) -> Sequence[GateCommand]:
        """List commands by a specific originators."""
        result = await self.session.execute(
            select(GateCommand)
            .where(
                GateCommand.originator_id == originator_id,
                GateCommand.tenant_id == tenant_id,
            )
            .order_by(desc(GateCommand.timestamp_solicitud))
            .limit(limit)
        )
        return result.scalars().all()

    async def count_by_sede(
        self, sede_id: uuid.UUID, tenant_id: uuid.UUID, hours: int = 1
    ) -> int:
        """Count commands for a sede in the last N hours (for rate limiting)."""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(func.count(GateCommand.id)).where(
                GateCommand.sede_id == sede_id,
                GateCommand.tenant_id == tenant_id,
                GateCommand.timestamp_solicitud >= since,
                GateCommand.tipo_comando == "MANUAL_OPEN",
            )
        )
        return result.scalar_one()


# ── GateAlert Repository (RF-022) ───────────────────────────────────────────────


class GateAlertRepository:
    """Repository for gate failure alerts."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: uuid.UUID,
        gate_id: uuid.UUID,
        sede_id: uuid.UUID,
        tipo_falla: str,
        comando_id: uuid.UUID | None,
        timestamp_falla: datetime,
        severity: str,
        device_status: str,
        intentos_anteriores: int = 0,
        descripcion: str | None = None,
    ) -> GateAlert:
        """Create a new gate alert."""
        alert = GateAlert(
            tenant_id=tenant_id,
            gate_id=gate_id,
            sede_id=sede_id,
            tipo_falla=tipo_falla,
            comando_id=comando_id,
            timestamp_falla=timestamp_falla,
            severity=severity,
            device_status=device_status,
            intentos_anteriores=intentos_anteriores,
            descripcion=descripcion,
        )
        self.session.add(alert)
        await self.session.flush()
        await self.session.refresh(alert)
        return alert

    async def get_active_by_gate(
        self, gate_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Sequence[GateAlert]:
        """Get all active alerts for a gate."""
        result = await self.session.execute(
            select(GateAlert)
            .where(
                GateAlert.gate_id == gate_id,
                GateAlert.tenant_id == tenant_id,
                GateAlert.estado == "ACTIVA",
            )
            .order_by(desc(GateAlert.timestamp_falla))
        )
        return result.scalars().all()

    async def list_active(self, tenant_id: uuid.UUID) -> Sequence[GateAlert]:
        """List all active alerts for a tenant."""
        result = await self.session.execute(
            select(GateAlert)
            .where(GateAlert.tenant_id == tenant_id, GateAlert.estado == "ACTIVA")
            .order_by(desc(GateAlert.timestamp_falla))
        )
        return result.scalars().all()

    async def resolve(
        self,
        alert_id: uuid.UUID,
        tenant_id: uuid.UUID,
        resolucion_por: str,
        nota_resolucion: str | None = None,
    ) -> GateAlert | None:
        """Mark an alert as resolved."""
        result = await self.session.execute(
            select(GateAlert).where(
                GateAlert.id == alert_id, GateAlert.tenant_id == tenant_id
            )
        )
        alert = result.scalar_one_or_none()
        if not alert:
            return None
        alert.estado = "RESUELTA"
        alert.timestamp_resolucion = datetime.utcnow()
        alert.resolucion_por = resolucion_por
        if nota_resolucion:
            alert.nota_resolucion = nota_resolucion
        await self.session.flush()
        return alert

    async def escalate(self, alert_id: uuid.UUID, tenant_id: uuid.UUID) -> GateAlert | None:
        """Escalate an alert."""
        result = await self.session.execute(
            select(GateAlert).where(
                GateAlert.id == alert_id, GateAlert.tenant_id == tenant_id
            )
        )
        alert = result.scalar_one_or_none()
        if not alert:
            return None
        alert.estado = "ESCALADA"
        await self.session.flush()
        return alert

    async def count_recent_failures(
        self, gate_id: uuid.UUID, tenant_id: uuid.UUID, hours: int = 24
    ) -> int:
        """Count recent failures for maintenance prediction."""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(func.count(GateAlert.id)).where(
                GateAlert.gate_id == gate_id,
                GateAlert.tenant_id == tenant_id,
                GateAlert.timestamp_falla >= since,
            )
        )
        return result.scalar_one()


# ── IoT Device Repository ───────────────────────────────────────────────────────


class IoTDeviceRepository:
    """Repository for IoT devices."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, device_id: uuid.UUID, tenant_id: uuid.UUID) -> IoTDevice | None:
        result = await self.session.execute(
            select(IoTDevice).where(
                IoTDevice.id == device_id, IoTDevice.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_serial(self, serial: str) -> IoTDevice | None:
        result = await self.session.execute(
            select(IoTDevice).where(IoTDevice.serial_number == serial)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self, tenant_id: uuid.UUID, sede_id: uuid.UUID | None = None, limit: int = 100, offset: int = 0
    ) -> Sequence[IoTDevice]:
        query = select(IoTDevice).where(IoTDevice.tenant_id == tenant_id)
        if sede_id:
            query = query.where(IoTDevice.sede_id == sede_id)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return result.scalars().all()

    async def create(
        self,
        tenant_id: uuid.UUID,
        name: str,
        device_type: str,
        serial_number: str,
        sede_id: uuid.UUID,
        mac_address: str | None = None,
        ip_address: str | None = None,
        config: dict | None = None,
    ) -> IoTDevice:
        device = IoTDevice(
            tenant_id=tenant_id,
            name=name,
            device_type=device_type,
            serial_number=serial_number,
            sede_id=sede_id,
            mac_address=mac_address,
            ip_address=ip_address,
            config=config,
        )
        self.session.add(device)
        await self.session.flush()
        await self.session.refresh(device)
        return device

    async def update_online_status(
        self, device_id: uuid.UUID, tenant_id: uuid.UUID, is_online: bool
    ) -> IoTDevice | None:
        device = await self.get_by_id(device_id, tenant_id)
        if not device:
            return None
        device.is_online = is_online
        device.last_seen = datetime.utcnow()
        await self.session.flush()
        return device


# ── IoT Event Repository ────────────────────────────────────────────────────────


class IoTEventRepository:
    """Repository for IoT events/telemetry."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: uuid.UUID,
        device_id: uuid.UUID,
        event_type: str,
        payload: dict | None = None,
        confidence: int | None = None,
        timestamp: datetime | None = None,
    ) -> IoTEvent:
        event = IoTEvent(
            tenant_id=tenant_id,
            device_id=device_id,
            event_type=event_type,
            payload=payload,
            confidence=confidence,
            timestamp=timestamp or datetime.utcnow(),
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_recent(
        self, device_id: uuid.UUID, tenant_id: uuid.UUID, limit: int = 50
    ) -> Sequence[IoTEvent]:
        result = await self.session.execute(
            select(IoTEvent)
            .where(IoTEvent.device_id == device_id, IoTEvent.tenant_id == tenant_id)
            .order_by(desc(IoTEvent.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_processed(self, event_id: uuid.UUID) -> None:
        await self.session.execute(
            update(IoTEvent).where(IoTEvent.id == event_id).values(processed=True)
        )
        await self.session.flush()