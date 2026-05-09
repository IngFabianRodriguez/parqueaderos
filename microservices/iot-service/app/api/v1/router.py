"""API v1 router — IoT Service.

TODO references:
  - RF-007: Crear tabla iot_devices
  - RF-008: Integración MQTT — conectar broker y suscribir topics de dispositivos
  - RF-009: Integración Kafka — publicar eventos en topic iot.events
  - RF-010: Endpoints CRUD dispositivos y comandos
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import TokenData, get_current_tenant
from app.db.models import IoTCommand, IoTDevice, IoTEvent
from app.db.session import AsyncSession, get_db
from app.schemas.iot import (
    IoTCommandCreate,
    IoTCommandResponse,
    IoTDeviceCreate,
    IoTDeviceResponse,
    IoTDeviceUpdate,
    IoTEventCreate,
    IoTEventResponse,
)

router = APIRouter(tags=["IoT"])


# ── Devices ──────────────────────────────────────────────────────────────────


@router.get("/devices", response_model=list[IoTDeviceResponse])
async def list_devices(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    sede_id: str | None = None,
    device_type: str | None = None,
    is_online: bool | None = None,
    limit: int = 100,
    offset: int = 0,
):
    """List IoT devices for the current tenant. RF-007."""
    query = select(IoTDevice).where(IoTDevice.tenant_id == tenant.tenant_id)
    if sede_id:
        query = query.where(IoTDevice.sede_id == sede_id)
    if device_type:
        query = query.where(IoTDevice.device_type == device_type)
    if is_online is not None:
        query = query.where(IoTDevice.is_online == is_online)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/devices", response_model=IoTDeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device: IoTDeviceCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new IoT device. RF-007."""
    db_device = IoTDevice(
        tenant_id=tenant.tenant_id,
        **device.model_dump(),
    )
    db.add(db_device)
    try:
        await db.flush()
        await db.refresh(db_device)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Device serial_number already exists")
    return db_device


@router.get("/devices/{device_id}", response_model=IoTDeviceResponse)
async def get_device(
    device_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single IoT device. RF-007."""
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == device_id,
            IoTDevice.tenant_id == tenant.tenant_id,
        )
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.patch("/devices/{device_id}", response_model=IoTDeviceResponse)
async def update_device(
    device_id: str,
    update: IoTDeviceUpdate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update an IoT device (online status, config, etc.). RF-007."""
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == device_id,
            IoTDevice.tenant_id == tenant.tenant_id,
        )
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(device, key, value)
    await db.flush()
    await db.refresh(device)
    return device


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an IoT device. RF-007."""
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == device_id,
            IoTDevice.tenant_id == tenant.tenant_id,
        )
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await db.delete(device)


# ── Events ───────────────────────────────────────────────────────────────────


@router.post("/events", response_model=IoTEventResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(
    event: IoTEventCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Ingest an IoT event (from MQTT subscriber or HTTP). RF-009."""
    db_event = IoTEvent(
        tenant_id=tenant.tenant_id,
        **event.model_dump(),
    )
    db.add(db_event)
    await db.flush()
    await db.refresh(db_event)

    # TODO: RF-009 — Publish event to Kafka topic "iot.events"
    #   from app.services.kafka_producer import publish_event
    #   await publish_event(db_event)

    return db_event


@router.get("/events", response_model=list[IoTEventResponse])
async def list_events(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: str | None = None,
    event_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    """List IoT events for the tenant. RF-007."""
    query = select(IoTEvent).where(IoTEvent.tenant_id == tenant.tenant_id)
    if device_id:
        query = query.where(IoTEvent.device_id == device_id)
    if event_type:
        query = query.where(IoTEvent.event_type == event_type)
    query = query.order_by(IoTEvent.timestamp.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# ── Commands ──────────────────────────────────────────────────────────────────


@router.post("/commands", response_model=IoTCommandResponse, status_code=status.HTTP_201_CREATED)
async def send_command(
    command: IoTCommandCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Send a command to an IoT device. RF-010."""
    # Verify device belongs to tenant
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == command.device_id,
            IoTDevice.tenant_id == tenant.tenant_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Device not found")

    db_command = IoTCommand(
        tenant_id=tenant.tenant_id,
        created_by=tenant.sub,
        **command.model_dump(),
    )
    db.add(db_command)
    await db.flush()
    await db.refresh(db_command)

    # TODO: RF-008 — Publish command to MQTT broker (device topic)
    # TODO: RF-009 — Publish to Kafka for audit trail

    return db_command


@router.get("/commands/{command_id}", response_model=IoTCommandResponse)
async def get_command(
    command_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get command status. RF-010."""
    result = await db.execute(
        select(IoTCommand).where(
            IoTCommand.id == command_id,
            IoTCommand.tenant_id == tenant.tenant_id,
        )
    )
    command = result.scalar_one_or_none()
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    return command


@router.get("/devices/{device_id}/commands", response_model=list[IoTCommandResponse])
async def list_device_commands(
    device_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
):
    """List commands sent to a specific device. RF-010."""
    result = await db.execute(
        select(IoTCommand)
        .where(IoTCommand.device_id == device_id, IoTCommand.tenant_id == tenant.tenant_id)
        .order_by(IoTCommand.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()