"""Pydantic schemas for notifications."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, EmailStr


class NotificationSendRequest(BaseModel):
    user_id: str
    type: str = Field(..., description="email, push, sms, webhook")
    channel: str
    recipient: str
    subject: Optional[str] = None
    content: str
    metadata: Optional[dict[str, Any]] = None


class NotificationResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    type: str
    channel: str
    recipient: str
    subject: Optional[str]
    content: str
    metadata: Optional[dict]
    status: str
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class BatchNotificationRequest(BaseModel):
    user_ids: list[str]
    type: str
    channel: str
    subject: Optional[str] = None
    content: str
    metadata: Optional[dict[str, Any]] = None


class BatchNotificationResponse(BaseModel):
    total: int
    successful: int
    failed: int
    notification_ids: list[str]


class TemplateCreate(BaseModel):
    name: str
    type: str
    channel: str
    subject: Optional[str] = None
    content: str
    variables: Optional[list[str]] = None


class TemplateResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    type: str
    channel: str
    subject: Optional[str]
    content: str
    variables: Optional[list[str]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None


class PreferenceResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    email_enabled: bool
    push_enabled: bool
    sms_enabled: bool
    webhook_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceRegisterRequest(BaseModel):
    device_token: str
    device_type: str


class DeviceResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    device_token: str
    device_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookCreate(BaseModel):
    name: str
    url: str
    event_type: str
    secret: Optional[str] = None


class WebhookResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    url: str
    event_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True