"""POPO schemas for notifications — pure Python dataclasses, no pydantic."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any


# ============== NOTIFICATION SCHEMAS ==============

@dataclass
class NotificationSendRequest:
    """Request to send a single notification."""
    user_id: str
    type: str  # email, push, sms, webhook
    channel: str
    recipient: str
    subject: Optional[str] = None
    content: str = ""
    metadata: Optional[dict[str, Any]] = None


@dataclass
class NotificationResponse:
    """Response representing a notification."""
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

    @classmethod
    def from_model(cls, obj: Any) -> "NotificationResponse":
        return cls(
            id=obj.id,
            tenant_id=obj.tenant_id,
            user_id=obj.user_id,
            type=obj.type,
            channel=obj.channel,
            recipient=obj.recipient,
            subject=obj.subject,
            content=obj.content,
            metadata=obj.metadata,
            status=obj.status,
            sent_at=obj.sent_at,
            created_at=obj.created_at,
        )


@dataclass
class BatchNotificationRequest:
    """Request to send batch notifications."""
    user_ids: list[str]
    type: str
    channel: str
    subject: Optional[str] = None
    content: str = ""
    metadata: Optional[dict[str, Any]] = None


@dataclass
class BatchNotificationResponse:
    """Response for batch notification send."""
    total: int
    successful: int
    failed: int
    notification_ids: list[str]


# ============== TEMPLATE SCHEMAS ==============

@dataclass
class TemplateCreate:
    """Request to create a notification template."""
    name: str
    type: str  # email, push, sms, webhook
    channel: str
    subject: Optional[str] = None
    content: str = ""
    variables: Optional[list[str]] = None


@dataclass
class TemplateUpdate:
    """Request to update a notification template."""
    name: Optional[str] = None
    type: Optional[str] = None
    channel: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[list[str]] = None
    is_active: Optional[bool] = None


@dataclass
class TemplateResponse:
    """Response representing a notification template."""
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

    @classmethod
    def from_model(cls, obj: Any) -> "TemplateResponse":
        return cls(
            id=obj.id,
            tenant_id=obj.tenant_id,
            name=obj.name,
            type=obj.type,
            channel=obj.channel,
            subject=obj.subject,
            content=obj.content,
            variables=obj.variables,
            is_active=obj.is_active,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ============== PREFERENCE SCHEMAS ==============

@dataclass
class PreferenceUpdate:
    """Request to update user notification preferences."""
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None


@dataclass
class PreferenceResponse:
    """Response representing user notification preferences."""
    id: str
    tenant_id: str
    user_id: str
    email_enabled: bool
    push_enabled: bool
    sms_enabled: bool
    webhook_enabled: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, obj: Any) -> "PreferenceResponse":
        return cls(
            id=obj.id,
            tenant_id=obj.tenant_id,
            user_id=obj.user_id,
            email_enabled=obj.email_enabled,
            push_enabled=obj.push_enabled,
            sms_enabled=obj.sms_enabled,
            webhook_enabled=obj.webhook_enabled,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ============== DEVICE SCHEMAS ==============

@dataclass
class DeviceRegisterRequest:
    """Request to register a device for push notifications."""
    device_token: str
    device_type: str  # ios, android, web


@dataclass
class DeviceResponse:
    """Response representing a registered device."""
    id: str
    tenant_id: str
    user_id: str
    device_token: str
    device_type: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_model(cls, obj: Any) -> "DeviceResponse":
        return cls(
            id=obj.id,
            tenant_id=obj.tenant_id,
            user_id=obj.user_id,
            device_token=obj.device_token,
            device_type=obj.device_type,
            is_active=obj.is_active,
            created_at=obj.created_at,
        )


# ============== WEBHOOK SCHEMAS ==============

@dataclass
class WebhookCreate:
    """Request to create a webhook configuration."""
    name: str
    url: str
    event_type: str  # entry, exit, payment
    secret: Optional[str] = None


@dataclass
class WebhookUpdate:
    """Request to update a webhook configuration."""
    name: Optional[str] = None
    url: Optional[str] = None
    event_type: Optional[str] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class WebhookResponse:
    """Response representing a webhook configuration."""
    id: str
    tenant_id: str
    name: str
    url: str
    event_type: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_model(cls, obj: Any) -> "WebhookResponse":
        return cls(
            id=obj.id,
            tenant_id=obj.tenant_id,
            name=obj.name,
            url=obj.url,
            event_type=obj.event_type,
            is_active=obj.is_active,
            created_at=obj.created_at,
        )


@dataclass
class WebhookTestResponse:
    """Response for webhook test."""
    success: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


# ============== PAGINATION SCHEMAS ==============

@dataclass
class PaginatedResponse:
    """Generic paginated response."""
    items: list
    total: int
    page: int
    page_size: int
    pages: int = 0

    def __post_init__(self):
        if self.pages == 0 and self.page_size > 0:
            self.pages = (self.total + self.page_size - 1) // self.page_size