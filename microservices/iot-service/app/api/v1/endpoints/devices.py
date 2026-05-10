"""Device endpoints — IoT Service. RF-007, RF-008."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenData, get_current_tenant
from app.db.models import IoTDevice
from app.db.session import AsyncSession, get_db
from app.repositories.gate_repository import IoTDeviceRepository, IoTEventRepository
from app.schemas.iot import (
    IoTDeviceCreate,
    IoTDeviceResponse,
    IoTDeviceUpdate,
    IoTEventCreate,
    IoTEventResponse,
)

router = APIRouter(tags=["Devices"])


@router.get("/devices", response_model=list[IoTDeviceResponse])
async def list_devices(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    sede_id: uuid.UUID | None = None,
    device_type: str | None = None,
    is_online: bool | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List IoT devices for the current tenant. RF-007."""
    repo = IoTDeviceRepository(db)
    devices = await repo.list_all(
        tenant.tenant_id, sede_id=sede_id, limit=limit, offset=offset
    )
    if device_type is not None:
        devices = [d for d in devices if d.device_type == device_type]
    if is_online is not None:
        devices = [d for d in devices if d.is_online == is_online]
    return [IoTDeviceResponse.from_model(d) for d in devices]


@router.post(
    "/devices",
    response_model=IoTDeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
    device: IoTDeviceCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new IoT device. RF-007."""
    repo = IoTDeviceRepository(db)
    created = await repo.create(
        tenant_id=tenant.tenant_id,
        name=device.name,
        device_type=device.device_type,
        serial_number=device.serial_number,
        sede_id=device.sede_id,
        mac_address=device.mac_address,
        ip_address=device.ip_address,
        config=device.config,
    )
    return IoTDeviceResponse.from_model(created)


@router.get("/devices/{device_id}", response_model=IoTDeviceResponse)
async def get_device(
    device_id: uuid.UUID,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single IoT device. RF-007."""
    repo = IoTDeviceRepository(db)
    device = await repo.get_by_id(device_id, tenant.tenant_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return IoTDeviceResponse.from_model(device)


@router.patch("/devices/{device_id}", response_model=IoTDeviceResponse)
async def update_device(
    device_id: uuid.UUID,
    update: IoTDeviceUpdate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update an IoT device (online status, config, etc.). RF-007."""
    repo = IoTDeviceRepository(db)
    device = await repo.get_by_id(device_id, tenant.tenant_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    for key, value in update.__dict__.items():
        if value is not None:
            setattr(device, key, value)
    await db.flush()
    await db.refresh(device)
    return IoTDeviceResponse.from_model(device)


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: uuid.UUID,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an IoT device. RF-007."""
    repo = IoTDeviceRepository(db)
    device = await repo.get_by_id(device_id, tenant.tenant_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await db.delete(device)


# ── Events ──────────────────────────────────────────────────────────────────────


@router.post(
    "/events",
    response_model=IoTEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_event(
    event: IoTEventCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Ingest an IoT event (from MQTT subscriber or HTTP). RF-009."""
    repo = IoTEventRepository(db)
    created = await repo.create(
        tenant_id=tenant.tenant_id,
        device_id=event.device_id,
        event_type=event.event_type,
        payload=event.payload,
        confidence=event.confidence,
    )
    return IoTEventResponse.from_model(created)


@router.get("/events", response_model=list[IoTEventResponse])
async def list_events(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: uuid.UUID | None = None,
    event_type: str | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List IoT events for the tenant. RF-007."""
    # Note: filtering by device_id/event_type requires full table scan in this simple impl
    # Production would add proper indexed queries
    from sqlalchemy import select

    query = select(IoTEvent).where(IoTEvent.tenant_id == tenant.tenant_id)
    if device_id:
        query = query.where(IoTEvent.device_id == device_id)
    if event_type:
        query = query.where(IoTEvent.event_type == event_type)
    query = query.order_by(IoTEvent.timestamp.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()
    return [IoTEventResponse.from_model(e) for e in events]