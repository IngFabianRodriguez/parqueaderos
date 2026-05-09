"""Schemas module for notification-service."""

from app.schemas.notifications import (
    NotificationSendRequest, NotificationResponse,
    BatchNotificationRequest, BatchNotificationResponse,
    TemplateCreate, TemplateResponse,
    PreferenceUpdate, PreferenceResponse,
    DeviceRegisterRequest, DeviceResponse,
    WebhookCreate, WebhookResponse,
)

__all__ = [
    "NotificationSendRequest", "NotificationResponse",
    "BatchNotificationRequest", "BatchNotificationResponse",
    "TemplateCreate", "TemplateResponse",
    "PreferenceUpdate", "PreferenceResponse",
    "DeviceRegisterRequest", "DeviceResponse",
    "WebhookCreate", "WebhookResponse",
]