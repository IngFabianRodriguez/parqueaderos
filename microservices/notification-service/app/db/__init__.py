"""DB module for notification-service."""

from app.db.base import Base
from app.db.session import get_db, init_db, close_db, engine, AsyncSessionLocal
from app.db.models import Notification, Template, Device, Webhook, UserPreference

__all__ = ["Base", "get_db", "init_db", "close_db", "engine", "AsyncSessionLocal", "Notification", "Template", "Device", "Webhook", "UserPreference"]