"""Repository layer for notification-service.

Each repository wraps SQLAlchemy queries for a single model.
"""

from app.repositories.notification_repository import NotificationRepository
from app.repositories.template_repository import TemplateRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.preference_repository import PreferenceRepository
from app.repositories.webhook_repository import WebhookRepository

__all__ = [
    "NotificationRepository",
    "TemplateRepository",
    "DeviceRepository",
    "PreferenceRepository",
    "WebhookRepository",
]