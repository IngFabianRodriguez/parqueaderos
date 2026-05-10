"""Services — IoT Service. RF-018 to RF-022."""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Sequence

from app.config import get_settings
from app.db.models import Gate, GateAlert, GateCommand, GateStatusHistory, IoTDevice
from app.db.session import get_session_factory
from app.repositories.gate_repository import (
    GateAlertRepository,
    GateCommandRepository,
    GateRepository,
)
from app.schemas.iot import (
    AlertCreate,
    AlertResponse,
    DeviceHeartbeatRequest,
    GateCommandCreate,
    GateCommandResponse,
    GateStatus,
    GateStatusResponse,
    ManualOpenRequest,
    ManualOpenResponse,
)

settings = get_settings()


# ── Gate Service (RF-018 – RF-022) ─────────────────────────────────────────────


class GateService:
    """Business logic for gate/talanquera operations.

    RF-018: Open gate only with confirmed payment
    RF-019: Manual gate open by operator in emergency
    RF-020: Real-time gate status monitoring
    RF-021: Log every command sent to gate (immutable audit)
    RF-022: Detect gate failure and generate immediate alert
    """

    def __init__(self, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.session_factory = get_session_factory()

    async def _get_session(self):
        """Get a new database session."""
        return self.session_factory()

    # ── RF-020: Status Monitoring ───────────────────────────────────────────

    async def get_gate_status(self, gate_id: uuid.UUID) -> GateStatusResponse | None:
        """Get current status of a gate."""
        async with await self._get_session() as session:
            repo = GateRepository(session)
            gate = await repo.get_by_id(gate_id, self.tenant_id)
            if not gate:
                return None
            return GateStatusResponse.from_model(gate)

    async def list_all_gates(self, limit: int = 100, offset: int = 0) -> Sequence[Gate]:
        """List all gates for the tenant."""
        async with await self._get_session() as session:
            repo = GateRepository(session)
            return await repo.list_all(self.tenant_id, limit=limit, offset=offset)

    async def get_gate_status_history(
        self, gate_id: uuid.UUID, hours: int = 24
    ) -> Sequence[GateStatusHistory]:
        """Get status change history for a gate (RF-020)."""
        async with await self._get_session() as session:
            repo = GateRepository(session)
            return await repo.get_status_history(gate_id, self.tenant_id, hours=hours)

    async def process_heartbeat(
        self, heartbeat: DeviceHeartbeatRequest
    ) -> GateStatusResponse | None:
        """Process device heartbeat and update gate status (RF-020)."""
        async with await self._get_session() as session:
            gate_repo = GateRepository(session)

            # Find gate by device_id
            gate = await gate_repo.get_by_id(heartbeat.gate_id, self.tenant_id)
            if not gate:
                return None

            # Update heartbeat
            await gate_repo.update_last_heartbeat(heartbeat.gate_id, self.tenant_id)

            # Map arm_position and relay_state to gate status
            new_status = self._derive_status_from_heartbeat(heartbeat)
            if new_status:
                await gate_repo.update_status(
                    gate_id=heartbeat.gate_id,
                    tenant_id=self.tenant_id,
                    new_status=new_status,
                    changed_by="SYSTEM",
                    reason=f"Heartbeat: relay={heartbeat.relay_state}, arm={heartbeat.arm_position}",
                )

            gate = await gate_repo.get_by_id(heartbeat.gate_id, self.tenant_id)
            return GateStatusResponse.from_model(gate) if gate else None

    def _derive_status_from_heartbeat(self, heartbeat: DeviceHeartbeatRequest) -> str:
        """Derive gate status from heartbeat data."""
        if heartbeat.error_code:
            return GateStatus.ERROR

        arm = heartbeat.arm_position.lower() if heartbeat.arm_position else "down"
        relay = heartbeat.relay_state

        if arm == "up" and relay:
            return GateStatus.OPEN
        elif arm == "down" and not relay:
            return GateStatus.CLOSED
        elif arm == "moving":
            return GateStatus.OPENING if relay else GateStatus.CLOSING
        return GateStatus.CLOSED

    async def check_offline_gates(self) -> None:
        """Check for gates that haven't sent heartbeat and mark them offline."""
        threshold = datetime.utcnow() - timedelta(
            seconds=settings.GATE_OFFLINE_THRESHOLD_SECONDS
        )
        async with await self._get_session() as session:
            repo = GateRepository(session)
            from sqlalchemy import select

            result = await session.execute(
                select(Gate).where(
                    Gate.tenant_id == self.tenant_id,
                    Gate.current_status.not_in ("OFFLINE", "ERROR", "BLOCKED"),
                )
            )
            gates = result.scalars().all()
            for gate in gates:
                if gate.last_heartbeat and gate.last_heartbeat < threshold:
                    await repo.mark_offline(gate.id, self.tenant_id)

    # ── RF-021: Gate Command Logging ──────────────────────────────────────

    async def send_gate_command(
        self,
        command: GateCommandCreate,
        timeout_seconds: int | None = None,
    ) -> GateCommandResponse:
        """Send a command to a gate — creates immutable audit record first.

        RF-021: Every command is logged before being sent.
        """
        if timeout_seconds is None:
            timeout_seconds = settings.GATE_COMMAND_TIMEOUT_SECONDS

        async with await self._get_session() as session:
            gate_repo = GateRepository(session)
            cmd_repo = GateCommandRepository(session)

            # Check gate exists and is not blocked
            gate = await gate_repo.get_by_id(command.gate_id, self.tenant_id)
            if not gate:
                raise ValueError(f"Gate {command.gate_id} not found")

            if gate.is_blocked:
                raise ValueError(f"Gate {command.gate_id} is blocked: {gate.blocked_reason}")

            # Create command record FIRST (write-ahead log pattern)
            cmd = await cmd_repo.create(
                tenant_id=self.tenant_id,
                gate_id=command.gate_id,
                tipo_comando=command.tipo_comando,
                sede_id=command.sede_id,
                originator_type=command.originator_type,
                originator_id=command.originator_id,
                originator_ip=command.originator_ip,
                motivo_codigo=command.motivo_codigo,
                motivo_descripcion=command.motivo_descripcion,
                entrada_id=command.entrada_id,
                salida_id=command.salida_id,
            )

            try:
                # Update gate status to indicate command in progress
                if command.tipo_comando == "OPEN":
                    await gate_repo.update_status(
                        gate_id=command.gate_id,
                        tenant_id=self.tenant_id,
                        new_status="OPENING",
                        changed_by=command.originator_id,
                        reason=f"Command: {command.tipo_comando}",
                    )

                # Simulate device execution (in production, send via MQTT/HTTP)
                success = await self._execute_gate_command(
                    command.gate_id, command.tipo_comando, timeout_seconds
                )

                if success:
                    await cmd_repo.update_result(
                        comando_id=cmd.id,
                        tenant_id=self.tenant_id,
                        resultado="SUCCESS",
                        device_response_time_ms=timeout_seconds * 1000,
                        timestamp_apertura_confirmada=datetime.utcnow(),
                    )
                    if command.tipo_comando == "OPEN":
                        await gate_repo.update_status(
                            gate_id=command.gate_id,
                            tenant_id=self.tenant_id,
                            new_status="OPEN",
                            changed_by=command.originator_id,
                        )
                else:
                    raise TimeoutError("Device did not acknowledge command")

            except asyncio.TimeoutError:
                await cmd_repo.update_result(
                    comando_id=cmd.id,
                    tenant_id=self.tenant_id,
                    resultado="TIMEOUT",
                    error_code="TIMEOUT_APERTURA",
                    error_description=f"Device did not respond within {timeout_seconds}s",
                    device_response_time_ms=timeout_seconds * 1000,
                )
                if command.tipo_comando == "OPEN":
                    await gate_repo.update_status(
                        gate_id=command.gate_id,
                        tenant_id=self.tenant_id,
                        new_status="ERROR",
                        error_description="Timeout waiting for device",
                        changed_by=command.originator_id,
                    )
                # Trigger RF-022 alert
                await self._create_failure_alert(
                    gate_id=command.gate_id,
                    sede_id=command.sede_id,
                    tipo_falla="TIMEOUT_APERTURA",
                    comando_id=cmd.id,
                    device_status="TIMEOUT",
                )
                raise TimeoutError(f"Gate command timed out after {timeout_seconds}s")

            except Exception as exc:
                await cmd_repo.update_result(
                    comando_id=cmd.id,
                    tenant_id=self.tenant_id,
                    resultado="FAILED",
                    error_code="DEVICE_ERROR",
                    error_description=str(exc),
                )
                raise

            # Return updated command
            updated_cmd = await cmd_repo.get_by_id(cmd.id, self.tenant_id)
            return GateCommandResponse.from_model(updated_cmd)

    async def _execute_gate_command(
        self, gate_id: uuid.UUID, tipo: str, timeout: int
    ) -> bool:
        """Simulate gate command execution.

        In production: publish to MQTT broker and wait for acknowledgment.
        For testing: simulate immediate success.
        """
        # Simulate device response time
        await asyncio.sleep(0.05)  # 50ms simulated device latency
        return True  # Simulated success

    # ── RF-018: Open gate with confirmed payment ───────────────────────────

    async def open_gate_with_payment(
        self,
        gate_id: uuid.UUID,
        sede_id: uuid.UUID,
        entrada_id: uuid.UUID | None,
        salida_id: uuid.UUID,
        transaction_id: uuid.UUID,
        originator_id: str = "PARKING_SERVICE",
        originator_ip: str = "127.0.0.1",
    ) -> GateCommandResponse:
        """Open gate only when payment is confirmed (RF-018).

        Validates that payment state is: paid, exonerated, or prepago_aprobado.
        """
        command = GateCommandCreate(
            gate_id=gate_id,
            tipo_comando="OPEN",
            sede_id=sede_id,
            originator_type="system",
            originator_id=originator_id,
            originator_ip=originator_ip,
            motivo_codigo="PAGO_CONFIRMADO",
            motivo_descripcion="Apertura automática por pago confirmado",
            entrada_id=entrada_id,
            salida_id=salida_id,
        )
        return await self.send_gate_command(command)

    # ── RF-019: Manual gate open by operator ───────────────────────────────

    ALLOWED_MANUAL_OPEN_ROLES = {"admin_sede", "operador", "superadmin"}
    MAX_MANUAL_OPENS_PER_HOUR = 3

    async def manual_open(
        self, request: ManualOpenRequest, operator_role: str
    ) -> ManualOpenResponse:
        """Execute manual gate open by operator (RF-019).

        Validates:
        - Operator has allowed role
        - Reason is provided
        - Gate is not blocked
        - Rate limit not exceeded
        """
        if operator_role not in self.ALLOWED_MANUAL_OPEN_ROLES:
            raise PermissionError(
                f"Role '{operator_role}' cannot perform manual gate open"
            )

        if not request.confirmacion_operador:
            raise ValueError("Operator must confirm the action is logged")

        async with await self._get_session() as session:
            gate_repo = GateRepository(session)
            cmd_repo = GateCommandRepository(session)

            gate = await gate_repo.get_by_id(request.gate_id, self.tenant_id)
            if not gate:
                raise ValueError(f"Gate {request.gate_id} not found")

            # Rate limit: check recent manual opens
            count = await cmd_repo.count_by_sede(
                request.sede_id, self.tenant_id, hours=1
            )
            if count >= self.MAX_MANUAL_OPENS_PER_HOUR:
                raise ValueError(
                    f"Rate limit exceeded: {count} manual opens in last hour "
                    f"(max {self.MAX_MANUAL_OPENS_PER_HOUR})"
                )

            # Create audit log command
            cmd = await cmd_repo.create(
                tenant_id=self.tenant_id,
                gate_id=request.gate_id,
                tipo_comando="MANUAL_OPEN",
                sede_id=request.sede_id,
                originator_type="operator",
                originator_id=str(request.operador_id),
                originator_ip="0.0.0.0",  # Operator has no IP in this context
                motivo_codigo=request.motivo_codigo,
                motivo_descripcion=request.motivo_descripcion,
            )

            # Execute command
            try:
                await gate_repo.update_status(
                    gate_id=request.gate_id,
                    tenant_id=self.tenant_id,
                    new_status="OPENING",
                    changed_by=str(request.operador_id),
                    reason=f"Manual open: {request.motivo_codigo}",
                )

                success = await self._execute_gate_command(
                    request.gate_id, "MANUAL_OPEN",
                    settings.GATE_COMMAND_TIMEOUT_SECONDS,
                )

                if success:
                    await cmd_repo.update_result(
                        comando_id=cmd.id,
                        tenant_id=self.tenant_id,
                        resultado="SUCCESS",
                        device_response_time_ms=settings.GATE_COMMAND_TIMEOUT_SECONDS * 1000,
                        timestamp_apertura_confirmada=datetime.utcnow(),
                    )
                    await gate_repo.update_status(
                        gate_id=request.gate_id,
                        tenant_id=self.tenant_id,
                        new_status="OPEN",
                        changed_by=str(request.operador_id),
                    )

                    # Calculate auto-close time
                    auto_close = datetime.utcnow() + timedelta(
                        seconds=settings.GATE_AUTO_CLOSE_SECONDS
                    )

                    return ManualOpenResponse(
                        command_id=cmd.id,
                        gate_status="OPEN",
                        timestamp_apertura=datetime.utcnow(),
                        timestamp_cierre_programado=auto_close,
                        auditoria_id=cmd.id,
                    )
                else:
                    raise TimeoutError("Device did not respond to manual open")

            except Exception as exc:
                await cmd_repo.update_result(
                    comando_id=cmd.id,
                    tenant_id=self.tenant_id,
                    resultado="FAILED",
                    error_description=str(exc),
                )
                await gate_repo.update_status(
                    gate_id=request.gate_id,
                    tenant_id=self.tenant_id,
                    new_status="ERROR",
                    error_description=str(exc),
                    changed_by=str(request.operador_id),
                )
                raise

    # ── RF-022: Gate failure detection and alert generation ──────────────

    async def _create_failure_alert(
        self,
        gate_id: uuid.UUID,
        sede_id: uuid.UUID,
        tipo_falla: str,
        comando_id: uuid.UUID,
        device_status: str,
        intentos_anteriores: int = 0,
    ) -> AlertResponse:
        """Create a gate failure alert (RF-022)."""
        async with await self._get_session() as session:
            alert_repo = GateAlertRepository(session)

            # Determine severity
            severity = "HIGH"
            descripcion = self._build_failure_description(tipo_falla)

            alert = await alert_repo.create(
                tenant_id=self.tenant_id,
                gate_id=gate_id,
                sede_id=sede_id,
                tipo_falla=tipo_falla,
                comando_id=comando_id,
                timestamp_falla=datetime.utcnow(),
                severity=severity,
                device_status=device_status,
                intentos_anteriores=intentos_anteriores,
                descripcion=descripcion,
            )

            # Update gate status to ERROR
            gate_repo = GateRepository(session)
            await gate_repo.update_status(
                gate_id=gate_id,
                tenant_id=self.tenant_id,
                new_status="ERROR",
                error_description=descripcion,
                changed_by="SYSTEM",
            )

            # Check maintenance threshold
            recent_failures = await alert_repo.count_recent_failures(
                gate_id, self.tenant_id, hours=settings.MAINTENANCE_FAILURE_WINDOW_HOURS
            )
            if recent_failures >= settings.MAINTENANCE_FAILURE_THRESHOLD:
                # Create maintenance alert
                await alert_repo.create(
                    tenant_id=self.tenant_id,
                    gate_id=gate_id,
                    sede_id=sede_id,
                    tipo_falla="MAINTENANCE_PREDICTION",
                    comando_id=None,
                    timestamp_falla=datetime.utcnow(),
                    severity="MEDIUM",
                    device_status=device_status,
                    descripcion=(
                        f"Gate has had {recent_failures} failures in the last "
                        f"{settings.MAINTENANCE_FAILURE_WINDOW_HOURS}h — "
                        "consider preventive maintenance"
                    ),
                )

            return AlertResponse.from_model(alert)

    def _build_failure_description(self, tipo_falla: str) -> str:
        """Build human-readable failure description."""
        descriptions = {
            "TIMEOUT_APERTURA": "Gate did not respond to OPEN command within timeout",
            "TIMEOUT_CIERRE": "Gate did not confirm CLOSE within timeout",
            "SENSOR_FALLA": "Sensor reported invalid state",
            "COMUNICACION_PERDIDA": "Device stopped sending heartbeats",
            "ERROR_INTERNO": "Device reported internal error",
            "BLOQUEO_MECANICO": "Gate arm did not complete movement — possible mechanical blockage",
        }
        return descriptions.get(tipo_falla, tipo_falla)

    async def resolve_alert(
        self, alert_id: uuid.UUID, resolucion_por: str, nota: str | None = None
    ) -> AlertResponse | None:
        """Resolve an active alert."""
        async with await self._get_session() as session:
            repo = GateAlertRepository(session)
            alert = await repo.resolve(alert_id, self.tenant_id, resolucion_por, nota)
            if alert:
                return AlertResponse.from_model(alert)
            return None

    async def list_active_alerts(self) -> Sequence[GateAlert]:
        """List all active alerts for the tenant."""
        async with await self._get_session() as session:
            repo = GateAlertRepository(session)
            return await repo.list_active(self.tenant_id)

    # ── Gate management ────────────────────────────────────────────────────

    async def create_gate(
        self,
        name: str,
        gate_type: str,
        sede_id: uuid.UUID,
        device_id: uuid.UUID | None = None,
    ) -> Gate:
        """Create a new gate."""
        async with await self._get_session() as session:
            repo = GateRepository(session)
            return await repo.create(
                tenant_id=self.tenant_id,
                name=name,
                gate_type=gate_type,
                sede_id=sede_id,
                device_id=device_id,
            )

    async def block_gate(
        self, gate_id: uuid.UUID, reason: str, changed_by: str | None = None
    ) -> Gate | None:
        """Block a gate (security lock — RF-020)."""
        async with await self._get_session() as session:
            repo = GateRepository(session)
            return await repo.block(gate_id, self.tenant_id, reason, changed_by)

    async def unblock_gate(self, gate_id: uuid.UUID) -> Gate | None:
        """Unblock a gate after manual verification (RF-020)."""
        async with await self._get_session() as session:
            repo = GateRepository(session)
            return await repo.unblock(gate_id, self.tenant_id)

    async def reset_gate(
        self, gate_id: uuid.UUID, originator_id: str, originator_ip: str
    ) -> GateCommandResponse:
        """Reset a gate in error state (RF-020)."""
        command = GateCommandCreate(
            gate_id=gate_id,
            tipo_comando="RESET",
            sede_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),  # will be overridden
            originator_type="operator",
            originator_id=originator_id,
            originator_ip=originator_ip,
            motivo_codigo="RESET_ERROR",
            motivo_descripcion="Reset gate after error state",
        )
        async with await self._get_session() as session:
            gate_repo = GateRepository(session)
            gate = await gate_repo.get_by_id(gate_id, self.tenant_id)
            if gate:
                command.sede_id = gate.sede_id

        return await self.send_gate_command(command)