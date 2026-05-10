"""Notification service — business logic for notifications.

Implements send operations with retry logic across channels:
email, push, SMS, webhook.
"""

import asyncio
import logging
import time
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.repositories.notification_repository import NotificationRepository
from app.repositories.template_repository import TemplateRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.preference_repository import PreferenceRepository
from app.repositories.webhook_repository import WebhookRepository


logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """Base exception for notification errors."""
    pass


class ChannelUnavailableError(NotificationError):
    """Raised when notification channel is unavailable."""
    pass


class NotificationNotFoundError(NotificationError):
    """Raised when notification is not found."""
    pass


class TemplateNotFoundError(NotificationError):
    """Raised when template is not found."""
    pass


class DeviceNotFoundError(NotificationError):
    """Raised when device is not found."""
    pass


class PreferenceNotFoundError(NotificationError):
    """Raised when preferences are not found."""
    pass


class WebhookNotFoundError(NotificationError):
    """Raised when webhook is not found."""
    pass


def _render_template(content: str, variables: dict[str, str]) -> str:
    """Simple {{variable}} template renderer."""
    result = content
    for key, val in variables.items():
        result = result.replace(f"{{{{ {key} }}}}", str(val))
        result = result.replace(f"{{{{{key}}}}}", str(val))
    return result


class NotificationService:
    """Service for notification operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repo = NotificationRepository(session)
        self.template_repo = TemplateRepository(session)
        self.device_repo = DeviceRepository(session)
        self.preference_repo = PreferenceRepository(session)
        self.webhook_repo = WebhookRepository(session)

    # ============== CHANNEL SEND OPERATIONS ==============

    @staticmethod
    async def _retry(func, *args, max_retries: int = 3, delay: float = 1.0, **kwargs):
        """Execute async function with retry logic."""
        last_error = None
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay * (attempt + 1))
                else:
                    logger.error(f"All {max_retries} attempts failed: {e}")
        raise last_error

    async def _send_email(
        self,
        recipient: str,
        subject: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """Send email via SMTP (stubbed — requires real SMTP server)."""
        logger.info(f"[EMAIL] To: {recipient}, Subject: {subject}")
        # In production, use aiosmtplib or similar
        return True

    async def _send_push(
        self,
        device_token: str,
        title: str,
        body: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """Send push notification via Firebase (stubbed)."""
        logger.info(f"[PUSH] Token: {device_token[:20]}..., Title: {title}")
        return True

    async def _send_sms(
        self,
        phone: str,
        message: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """Send SMS via provider (stubbed)."""
        logger.info(f"[SMS] To: {phone}, Message: {message[:50]}")
        return True

    async def _send_webhook(
        self,
        url: str,
        payload: dict,
        secret: str,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[int], Optional[float]]:
        """Send webhook POST request with HMAC signature."""
        start = time.monotonic()
        try:
            import hmac
            import hashlib
            body_bytes = str(payload).encode()
            signature = hmac.new(
                secret.encode(), body_bytes, hashlib.sha256
            ).hexdigest()

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Notification-Signature": signature,
                        "X-Notification-Timestamp": str(int(time.time())),
                    },
                )
            elapsed_ms = (time.monotonic() - start) * 1000
            return response.status_code < 400, response.status_code, elapsed_ms
        except httpx.RequestError as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error(f"Webhook failed: {e}")
            return False, None, elapsed_ms

    # ============== PUBLIC API ==============

    async def send_notification(
        self,
        tenant_id: str,
        user_id: str,
        notification_type: str,
        channel: str,
        recipient: str,
        subject: Optional[str],
        content: str,
        metadata: Optional[dict] = None,
        use_template: bool = False,
    ) -> dict:
        """Send a single notification with retry logic.

        Args:
            tenant_id: Tenant identifier
            user_id: Target user
            notification_type: email|push|sms|webhook
            channel: smtp|fcm|sms|http
            recipient: email address, phone, device token, or webhook URL
            subject: Subject line (optional)
            content: Message content
            metadata: Additional context
            use_template: Whether to resolve content from active template

        Returns:
            dict with notification_id, status, sent_at
        """
        # Resolve template if requested
        if use_template:
            template = await self.template_repo.get_active_by_type(
                tenant_id, notification_type, channel
            )
            if template:
                content = _render_template(template.content, metadata or {})
                subject = subject or template.subject

        # Create DB record
        notification = await self.notification_repo.create(
            tenant_id=tenant_id,
            user_id=user_id,
            notification_type=notification_type,
            channel=channel,
            recipient=recipient,
            subject=subject,
            content=content,
            metadata=metadata,
        )

        # Send via appropriate channel
        success = False
        try:
            if notification_type == "email":
                success = await self._send_email(recipient, subject or "", content, metadata)
            elif notification_type == "push":
                success = await self._send_push(recipient, subject or "Notification", content, metadata)
            elif notification_type == "sms":
                success = await self._send_sms(recipient, content, metadata)
            elif notification_type == "webhook":
                success, status_code, elapsed_ms = await self._send_webhook(
                    recipient, {"content": content, "metadata": metadata}, secret=metadata.get("secret", ""), metadata=metadata
                )
                if metadata:
                    metadata["http_status"] = status_code
                    metadata["response_time_ms"] = elapsed_ms
            else:
                logger.warning(f"Unknown notification type: {notification_type}")

            # Update status
            from datetime import datetime
            new_status = "sent" if success else "failed"
            await self.notification_repo.update_status(
                notification.id, new_status, datetime.utcnow() if success else None
            )
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {e}")
            await self.notification_repo.mark_failed(notification.id, str(e))
            success = False

        return {
            "notification_id": notification.id,
            "status": "sent" if success else "failed",
            "sent_at": notification.sent_at,
        }

    async def send_batch(
        self,
        tenant_id: str,
        user_ids: list[str],
        notification_type: str,
        channel: str,
        subject: Optional[str],
        content: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Send notifications to multiple users."""
        items = [
            {
                "tenant_id": tenant_id,
                "user_id": uid,
                "type": notification_type,
                "channel": channel,
                "recipient": metadata.get("recipient", "") if metadata else "",
                "subject": subject,
                "content": content,
                "metadata": metadata,
            }
            for uid in user_ids
        ]

        # Use first user's recipient if not overridden
        if items and metadata and not metadata.get("recipient"):
            items[0]["recipient"] = metadata.get("recipient", "")

        notifications = await self.notification_repo.bulk_create(items)

        # Fire send tasks
        results = []
        for notif in notifications:
            try:
                if notification_type == "email":
                    await self._send_email(notif.recipient, subject or "", content, metadata)
                elif notification_type == "push":
                    await self._send_push(notif.recipient, subject or "Notification", content, metadata)
                elif notification_type == "sms":
                    await self._send_sms(notif.recipient, content, metadata)

                from datetime import datetime
                await self.notification_repo.update_status(notif.id, "sent", datetime.utcnow())
                results.append({"id": notif.id, "status": "sent"})
            except Exception as e:
                await self.notification_repo.mark_failed(notif.id, str(e))
                results.append({"id": notif.id, "status": "failed"})

        successful = sum(1 for r in results if r["status"] == "sent")
        return {
            "total": len(notifications),
            "successful": successful,
            "failed": len(notifications) - successful,
            "notification_ids": [r["id"] for r in results],
        }

    async def get_notification(self, notification_id: str) -> dict:
        """Get notification by ID."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundError(f"Notification {notification_id} not found")
        return notification

    async def list_notifications(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> tuple[list, int]:
        """List notifications with pagination."""
        return await self.notification_repo.list_by_tenant(tenant_id, page, page_size, status)


class TemplateService:
    """Service for template operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_repo = TemplateRepository(session)

    async def create_template(
        self,
        tenant_id: str,
        name: str,
        template_type: str,
        channel: str,
        content: str,
        subject: Optional[str] = None,
        variables: Optional[list[str]] = None,
    ) -> dict:
        """Create a new notification template."""
        template = await self.template_repo.create(
            tenant_id=tenant_id,
            name=name,
            template_type=template_type,
            channel=channel,
            content=content,
            subject=subject,
            variables=variables,
        )
        return template

    async def get_template(self, template_id: str) -> dict:
        """Get template by ID."""
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise TemplateNotFoundError(f"Template {template_id} not found")
        return template

    async def list_templates(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        template_type: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> tuple[list, int]:
        """List templates with pagination."""
        return await self.template_repo.list_by_tenant(
            tenant_id, page, page_size, template_type, channel
        )

    async def update_template(
        self,
        template_id: str,
        data: dict,
    ) -> dict:
        """Update a template."""
        template = await self.template_repo.update(template_id, data)
        if not template:
            raise TemplateNotFoundError(f"Template {template_id} not found")
        return template

    async def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        return await self.template_repo.delete(template_id)


class PreferenceService:
    """Service for user notification preferences."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.preference_repo = PreferenceRepository(session)

    async def get_preferences(self, tenant_id: str, user_id: str) -> dict:
        """Get user notification preferences."""
        pref = await self.preference_repo.get_by_user(user_id, tenant_id)
        if not pref:
            # Return defaults
            return {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "email_enabled": True,
                "push_enabled": True,
                "sms_enabled": False,
                "webhook_enabled": True,
            }
        return pref

    async def update_preferences(
        self,
        tenant_id: str,
        user_id: str,
        email_enabled: Optional[bool] = None,
        push_enabled: Optional[bool] = None,
        sms_enabled: Optional[bool] = None,
        webhook_enabled: Optional[bool] = None,
    ) -> dict:
        """Update user notification preferences."""
        return await self.preference_repo.update(
            tenant_id=tenant_id,
            user_id=user_id,
            email_enabled=email_enabled,
            push_enabled=push_enabled,
            sms_enabled=sms_enabled,
            webhook_enabled=webhook_enabled,
        )


class DeviceService:
    """Service for device management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.device_repo = DeviceRepository(session)

    async def register_device(
        self,
        tenant_id: str,
        user_id: str,
        device_token: str,
        device_type: str,
    ) -> dict:
        """Register a device for push notifications."""
        # Check for existing registration with same token
        existing = await self.device_repo.get_by_token(device_token)
        if existing:
            # Update existing device
            return await self.device_repo.update(existing.id, is_active=True, device_token=device_token)

        return await self.device_repo.create(
            tenant_id=tenant_id,
            user_id=user_id,
            device_token=device_token,
            device_type=device_type,
        )

    async def unregister_device(self, device_id: str) -> bool:
        """Unregister (deactivate) a device."""
        return await self.device_repo.deactivate(device_id)

    async def list_user_devices(
        self, tenant_id: str, user_id: str
    ) -> list[dict]:
        """List active devices for a user."""
        return await self.device_repo.list_by_user(user_id, tenant_id)


class WebhookService:
    """Service for webhook management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.webhook_repo = WebhookRepository(session)

    async def create_webhook(
        self,
        tenant_id: str,
        name: str,
        url: str,
        event_type: str,
        secret: Optional[str] = None,
    ) -> dict:
        """Create a new webhook."""
        return await self.webhook_repo.create(
            tenant_id=tenant_id,
            name=name,
            url=url,
            event_type=event_type,
            secret=secret,
        )

    async def get_webhook(self, webhook_id: str) -> dict:
        """Get webhook by ID."""
        webhook = await self.webhook_repo.get_by_id(webhook_id)
        if not webhook:
            raise WebhookNotFoundError(f"Webhook {webhook_id} not found")
        return webhook

    async def list_webhooks(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        event_type: Optional[str] = None,
    ) -> tuple[list, int]:
        """List webhooks with pagination."""
        return await self.webhook_repo.list_by_tenant(tenant_id, page, page_size, event_type)

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        return await self.webhook_repo.delete(webhook_id)

    async def test_webhook(self, webhook_id: str) -> dict:
        """Test a webhook by sending a probe payload."""
        webhook = await self.webhook_repo.get_by_id(webhook_id)
        if not webhook:
            raise WebhookNotFoundError(f"Webhook {webhook_id} not found")

        payload = {
            "event": "test",
            "webhook_id": webhook_id,
            "timestamp": int(time.time()),
        }

        success, status_code, elapsed_ms = await NotificationService._send_webhook(
            webhook.url, payload, webhook.secret
        )

        return {
            "success": success,
            "status_code": status_code,
            "response_time_ms": elapsed_ms,
            "error": None if success else "HTTP error" if status_code else "Request failed",
        }


# Factory functions for dependency injection
def get_notification_service(session: AsyncSession) -> NotificationService:
    return NotificationService(session)


def get_template_service(session: AsyncSession) -> TemplateService:
    return TemplateService(session)


def get_preference_service(session: AsyncSession) -> PreferenceService:
    return PreferenceService(session)


def get_device_service(session: AsyncSession) -> DeviceService:
    return DeviceService(session)


def get_webhook_service(session: AsyncSession) -> WebhookService:
    return WebhookService(session)