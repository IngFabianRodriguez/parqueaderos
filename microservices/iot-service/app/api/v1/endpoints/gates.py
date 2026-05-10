"""API v1 endpoints — IoT Service. RF-018 to RF-022.

Gate commands, status monitoring, alerts.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenData, get_current_tenant
from app.db.session import AsyncSession, get_db
from app.repositories.gate_repository import (
    GateAlertRepository,
    GateCommandRepository,
    GateRepository,
)
from app.schemas.iot import (
    AlertCreate,
    AlertResponse,
    DeviceHeartbeatRequest,
    GateCommandResponse,
    GateStatusResponse,
    ManualOpenRequest,
    ManualOpenResponse,
)
from app.services.gate_service import GateService

router = APIRouter(tags=["Gates (RF-018–RF-022)"])


# ── Gate Status (RF-020) ────────────────────────────────────────────────────────


@router.get(
    "/gates/status",
    response_model=list[GateStatusResponse],
    summary="List all gate statuses",
    description="Returns current status of all gates for the tenant (RF-020).",
)
async def list_gate_statuses(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    sede_id: uuid.UUID | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List current status of all gates for the tenant (RF-020)."""
    repo = GateRepository(db)
    if sede_id:
        gates = await repo.list_by_sede(sede_id, tenant.tenant_id)
    else:
        gates = await repo.list_all(tenant.tenant_id, limit=limit, offset=offset)
    return [GateStatusResponse.from_model(g) for g in gates]


@router.get(
    "/gate/status/{gate_id}",
    response_model=GateStatusResponse,
    summary="Get gate status",
    description="Returns current status of a specific gate (RF-020).",
)
async def get_gate_status(
    gate_id: uuid.UUID,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get current status of a specific gate (RF-020)."""
    repo = GateRepository(db)
    gate = await repo.get_by_id(gate_id, tenant.tenant_id)
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
    return GateStatusResponse.from_model(gate)


@router.get(
    "/gate/history/{gate_id}",
    response_model=list[dict],
    summary="Get gate status history",
    description="Returns status change history for a gate (RF-020, last 24h).",
)
async def get_gate_status_history(
    gate_id: uuid.UUID,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    hours: int = Query(default=24, ge=1, le=168),
):
    """Get gate status change history (RF-020)."""
    repo = GateRepository(db)
    history = await repo.get_status_history(gate_id, tenant.tenant_id, hours=hours)
    return [
        {
            "id": str(h.id),
            "previous_status": h.previous_status,
            "new_status": h.new_status,
            "changed_by": h.changed_by,
            "reason": h.reason,
            "timestamp": h.timestamp.isoformat(),
        }
        for h in history
    ]


# ── Device Heartbeat (RF-020) ───────────────────────────────────────────────────


@router.post(
    "/devices/heartbeat",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Device heartbeat",
    description="Receive heartbeat from IoT device and update gate status (RF-020).",
)
async def device_heartbeat(
    heartbeat: DeviceHeartbeatRequest,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Receive heartbeat from device and update gate status (RF-020).

    If the device doesn't report for > GATE_OFFLINE_THRESHOLD_SECONDS,
    the gate is marked OFFLINE.
    """
    service = GateService(tenant.tenant_id)
    result = await service.process_heartbeat(heartbeat)
    if not result:
        raise HTTPException(status_code=404, detail="Gate not found for this device")
    # No content on success — 204


# ── Gate Commands (RF-018, RF-019, RF-021) ──────────────────────────────────────


@router.post(
    "/gate/open",
    response_model=GateCommandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Open gate with payment confirmation",
    description="Opens a gate only when payment is confirmed (RF-018).",
)
async def open_gate_with_payment(
    gate_id: uuid.UUID,
    entrada_id: uuid.UUID | None,
    salida_id: uuid.UUID,
    sede_id: uuid.UUID,
    transaction_id: uuid.UUID,
    request: Request,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Open gate when payment is confirmed (RF-018).

    Only opens if payment estado is: paid, exonerated, or prepago_aprobado.
    """
    service = GateService(tenant.tenant_id)
    originator_ip = request.client.host if request.client else "0.0.0.0"

    try:
        result = await service.open_gate_with_payment(
            gate_id=gate_id,
            sede_id=sede_id,
            entrada_id=entrada_id,
            salida_id=salida_id,
            transaction_id=transaction_id,
            originator_id="PARKING_SERVICE",
            originator_ip=originator_ip,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post(
    "/gate/manual-open",
    response_model=ManualOpenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manual gate open by operator",
    description="Emergency manual gate open by authorized operator (RF-019).",
)
async def manual_gate_open(
    req: ManualOpenRequest,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Manual gate open by operator (RF-019).

    Requires:
    - operator role: admin_sede, operador, or superadmin
    - motivo_codigo and motivo_descripcion are mandatory
    - Rate limit: max 3 manual opens per hour per sede

    Creates an immutable audit log entry (RF-021).
    """
    service = GateService(tenant.tenant_id)

    try:
        return await service.manual_open(req, operator_role=tenant.role)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400, detail=str(e))


@router.post(
    "/gate/reset",
    response_model=GateCommandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reset gate after error",
    description="Reset a gate that is in ERROR state (RF-020).",
)
async def reset_gate(
    gate_id: uuid.UUID,
    request: Request,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Reset a gate in error state (RF-020).

    Only operators with appropriate roles can reset a gate.
    """
    if tenant.role not in {"admin_sede", "operador", "superadmin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{tenant.role}' cannot reset gates",
        )

    service = GateService(tenant.tenant_id)
    originator_ip = request.client.host if request.client else "0.0.0.0"

    try:
        return await service.reset_gate(gate_id, str(tenant.sub), originator_ip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get(
    "/gate/command/{command_id}",
    response_model=GateCommandResponse,
    summary="Get gate command details",
    description="Get details of a specific gate command (RF-021).",
)
async def get_gate_command(
    command_id: uuid.UUID,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get details of a specific gate command (RF-021)."""
    repo = GateCommandRepository(db)
    cmd = await repo.get_by_id(command_id, tenant.tenant_id)
    if not cmd:
        raise HTTPException(status_code=404, detail="Command not found")
    return GateCommandResponse.from_model(cmd)


@router.get(
    "/gate/commands",
    response_model=list[GateCommandResponse],
    summary="List gate commands",
    description="List gate command audit logs for a sede (RF-021).",
)
async def list_gate_commands(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    sede_id: uuid.UUID | None = None,
    tipo_comando: str | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List gate commands (audit log) — RF-021."""
    repo = GateCommandRepository(db)
    if sede_id:
        commands = await repo.list_by_sede(
            sede_id, tenant.tenant_id, tipo_comando=tipo_comando,
            limit=limit, offset=offset
        )
    else:
        # Tenant-wide query — fetch and filter in memory for now
        # (production would add tenant filter at DB level)
        commands = await repo.list_by_sede(
            uuid.UUID("00000000-0000-0000-0000-000000000000"),
            tenant.tenant_id,
            tipo_comando=tipo_comando,
            limit=limit,
            offset=offset,
        )
    return [GateCommandResponse.from_model(c) for c in commands]


# ── Alerts (RF-022) ─────────────────────────────────────────────────────────────


@router.post(
    "/alerts",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create gate alert",
    description="Create a new gate failure alert (RF-022).",
)
async def create_alert(
    alert: AlertCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new gate alert (RF-022)."""
    repo = GateAlertRepository(db)
    gate_repo = GateRepository(db)

    gate = await gate_repo.get_by_id(alert.gate_id, tenant.tenant_id)
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")

    created = await repo.create(
        tenant_id=tenant.tenant_id,
        gate_id=alert.gate_id,
        sede_id=alert.sede_id,
        tipo_falla=alert.tipo_falla,
        comando_id=alert.comando_id,
        timestamp_falla=alert.timestamp_falla,
        severity=alert.severity,
        device_status=alert.device_status,
        intentos_anteriores=alert.intentos_anteriores,
    )
    return AlertResponse.from_model(created)


@router.get(
    "/alerts/active",
    response_model=list[AlertResponse],
    summary="List active alerts",
    description="List all currently active gate alerts (RF-022).",
)
async def list_active_alerts(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all active alerts (RF-022)."""
    repo = GateAlertRepository(db)
    alerts = await repo.list_active(tenant.tenant_id)
    return [AlertResponse.from_model(a) for a in alerts]


@router.put(
    "/alerts/{alert_id}/resolve",
    response_model=AlertResponse,
    summary="Resolve alert",
    description="Mark an active alert as resolved (RF-022).",
)
async def resolve_alert(
    alert_id: uuid.UUID,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    resolucion_por: str = Query(..., description="ID of operator/support that resolved"),
    nota: str | None = Query(None, description="Optional resolution note"),
):
    """Resolve an active alert (RF-022)."""
    service = GateService(tenant.tenant_id)
    result = await service.resolve_alert(alert_id, resolucion_por, nota)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


# ── Gate management ─────────────────────────────────────────────────────────────


@router.post(
    "/gates",
    status_code=status.HTTP_201_CREATED,
    summary="Create a gate",
    description="Register a new gate/talanquera.",
)
async def create_gate(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: str = Query(..., description="Gate name"),
    gate_type: str = Query(..., description="Gate type: entry or exit"),
    sede_id: uuid.UUID = Query(..., description="Sede ID"),
    device_id: uuid.UUID | None = Query(None, description="Optional IoT device ID"),
):
    """Create a new gate (talanquera)."""
    service = GateService(tenant.tenant_id)
    gate = await service.create_gate(name, gate_type, sede_id, device_id)
    return GateStatusResponse.from_model(gate)


@router.put(
    "/gate/{gate_id}/block",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Block a gate",
    description="Block a gate — no automatic commands accepted until unblocked (RF-020).",
)
async def block_gate(
    gate_id: uuid.UUID,
    reason: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Block a gate — security lock (RF-020)."""
    if tenant.role not in {"admin_sede", "superadmin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{tenant.role}' cannot block gates",
        )
    repo = GateRepository(db)
    result = await repo.block(gate_id, tenant.tenant_id, reason, str(tenant.sub))
    if not result:
        raise HTTPException(status_code=404, detail="Gate not found")


@router.put(
    "/gate/{gate_id}/unblock",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unblock a gate",
    description="Unblock a gate after manual verification (RF-020).",
)
async def unblock_gate(
    gate_id: uuid.UUID,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Unblock a gate after manual verification (RF-020)."""
    if tenant.role not in {"admin_sede", "superadmin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{tenant.role}' cannot unblock gates",
        )
    repo = GateRepository(db)
    result = await repo.unblock(gate_id, tenant.tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Gate not found")