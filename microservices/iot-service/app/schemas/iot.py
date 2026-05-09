"""Pydantic schemas — IoT Service."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


# ── Device ──────────────────────────────────────────────────────────────────


class IoTDeviceBase(BaseModel):
    name: str = Field(..., max_length=255)
    device_type: str = Field(..., max_length=50)
    serial_number: str = Field(..., max_length=255)
    sede_id: uuid.UUID


class IoTDeviceCreate(IoTDeviceBase):
    mac_address: str | None = None
    ip_address: str | None = None
    config: dict | None = None


class IoTDeviceUpdate(BaseModel):
    name: str | None = None
    is_online: bool | None = None
    config: dict | None = None
    firmware_version: str | None = None


class IoTDeviceResponse(IoTDeviceBase):
    id: uuid.UUID
    is_online: bool
    last_seen: datetime | None
    firmware_version: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Event ────────────────────────────────────────────────────────────────────


class IoTEventBase(BaseModel):
    device_id: uuid.UUID
    event_type: str = Field(..., max_length=100)
    payload: dict | None = None


class IoTEventCreate(IoTEventBase):
    confidence: int | None = Field(None, ge=0, le=100)


class IoTEventResponse(IoTEventBase):
    id: uuid.UUID
    confidence: int | None
    timestamp: datetime
    processed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Command ──────────────────────────────────────────────────────────────────


class IoTCommandBase(BaseModel):
    device_id: uuid.UUID
    command_type: str = Field(..., max_length=100)
    params: dict | None = None


class IoTCommandCreate(IoTCommandBase):
    pass


class IoTCommandResponse(IoTCommandBase):
    id: uuid.UUID
    status: str
    sent_at: datetime | None
    acknowledged_at: datetime | None
    created_at: datetime
    created_by: str

    model_config = {"from_attributes": True}