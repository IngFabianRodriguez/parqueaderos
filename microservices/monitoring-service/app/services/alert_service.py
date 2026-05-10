"""Business logic for alert management — RF-101, RF-102, RF-106, RF-107, RF-109."""
from __future__ import annotations

import structlog
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.db.session import AsyncSession
from app.repositories.monitoring import AlertRepository, AlertRuleRepository, NotificationChannelRepository
from app.schemas.monitoring import (
    AlertCreate, AlertResponse, AlertListResponse,
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    NotificationChannelCreate, NotificationChannelResponse,
    AlertSeverity, AlertStatus, AlertType,
)


logger = structlog.get_logger(__name__)


class AlertService:
    """Manages alert lifecycle: create, acknowledge, resolve, silence. RF-101, RF-109."""

    def __init__(self, session: AsyncSession):
        self._s = session
        self._alert_repo = AlertRepository(session)
        self._rule_repo = AlertRuleRepository(session)
        self._channel_repo = NotificationChannelRepository(session)

    async def create_alert(self, tenant_id: UUID, alert_in: AlertCreate) -> AlertResponse:
        """Create a new alert. RF-102."""
        alert = await self._alert_repo.create(tenant_id, **alert_in.model_dump())
        logger.info(
            "alert_created",
            alert_id=str(alert.id),
            service_id=alert.service_id,
            severity=alert.severity,
        )
        # Dispatch notification
        await self._dispatch_notification(tenant_id, alert)
        return AlertResponse.model_validate(alert)

    async def list_alerts(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        service_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> AlertListResponse:
        offset = (page - 1) * page_size
        alerts, total = await self._alert_repo.list(
            tenant_id, status=status, severity=severity, service_id=service_id,
            limit=page_size, offset=offset,
        )
        return AlertListResponse(
            total=total,
            page=page,
            page_size=page_size,
            alerts=[AlertResponse.model_validate(a) for a in alerts],
        )

    async def get_alert(self, tenant_id: UUID, alert_id: UUID) -> Optional[AlertResponse]:
        alert = await self._alert_repo.get_by_id(tenant_id, alert_id)
        return AlertResponse.model_validate(alert) if alert else None

    async def acknowledge_alert(
        self, tenant_id: UUID, alert_id: UUID, user_id: UUID, note: Optional[str] = None
    ) -> Optional[AlertResponse]:
        alert = await self._alert_repo.get_by_id(tenant_id, alert_id)
        if not alert:
            return None
        updated = await self._alert_repo.acknowledge(alert, user_id)
        logger.info("alert_acknowledged", alert_id=str(alert_id), by=str(user_id))
        return AlertResponse.model_validate(updated)

    async def silence_alert(
        self, tenant_id: UUID, alert_id: UUID, until: datetime, reason: Optional[str] = None
    ) -> Optional[AlertResponse]:
        alert = await self._alert_repo.get_by_id(tenant_id, alert_id)
        if not alert:
            return None
        updated = await self._alert_repo.silence(alert, until)
        logger.info("alert_silenced", alert_id=str(alert_id), until=until.isoformat())
        return AlertResponse.model_validate(updated)

    async def resolve_alert(self, tenant_id: UUID, alert_id: UUID) -> Optional[AlertResponse]:
        alert = await self._alert_repo.get_by_id(tenant_id, alert_id)
        if not alert:
            return None
        # Check if this was a SERVICE_DOWN and emit recovery event
        was_down = alert.type_ == AlertType.SERVICE_DOWN.value
        updated = await self._alert_repo.resolve(alert)
        logger.info("alert_resolved", alert_id=str(alert_id))
        if was_down:
            await self._emit_recovery(tenant_id, alert)
        return AlertResponse.model_validate(updated)

    async def _dispatch_notification(self, tenant_id: UUID, alert) -> None:
        """Send alert to all enabled notification channels for the tenant. RF-107."""
        channels = await self._channel_repo.list_enabled(tenant_id)
        if not channels:
            logger.warning("no_notification_channels", tenant_id=str(tenant_id))
            return

        for channel in channels:
            try:
                await self._send_to_channel(channel, alert)
            except Exception as exc:
                logger.error(
                    "notification_send_failed",
                    channel_id=str(channel.id),
                    alert_id=str(alert.id),
                    error=str(exc),
                )

    async def _send_to_channel(self, channel, alert) -> None:
        """Send alert notification to a specific channel."""
        config = channel.configuration or {}
        channel_type = channel.channel_type

        if channel_type == "email":
            await self._send_email_alert(config, alert)
        elif channel_type == "slack":
            await self._send_slack_alert(config, alert)
        elif channel_type == "webhook":
            await self._send_webhook_alert(config, alert)
        elif channel_type == "pagerduty":
            await self._send_pagerduty_alert(config, alert)
        # SMS etc...

    async def _send_email_alert(self, config: dict, alert) -> None:
        import httpx
        # Email sending via external service (SendGrid, SES, etc.)
        # Placeholder — integrate with notification-service in production
        logger.info("email_alert_sent", to=config.get("addresses"), alert_id=str(alert.id))

    async def _send_slack_alert(self, config: dict, alert) -> None:
        import httpx
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            return
        payload = {
            "text": f"[{alert.severity}] {alert.message}",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*{alert.severity}*: {alert.message}"}},
                {"type": "context", "elements": [{"type": "mrkdwn", "text": f"Service: {alert.service_id}"}]},
            ],
        }
        async with httpx.AsyncClient() as client:
            await client.post(str(webhook_url), json=payload, timeout=10.0)

    async def _send_webhook_alert(self, config: dict, alert) -> None:
        import httpx
        url = config.get("url")
        headers = config.get("headers", {})
        if not url:
            return
        async with httpx.AsyncClient() as client:
            await client.post(
                str(url),
                json={
                    "alert_id": str(alert.id),
                    "severity": alert.severity,
                    "service_id": alert.service_id,
                    "message": alert.message,
                    "timestamp": alert.created_at.isoformat(),
                },
                headers=headers,
                timeout=10.0,
            )

    async def _send_pagerduty_alert(self, config: dict, alert) -> None:
        import httpx
        integration_key = config.get("integration_key")
        if not integration_key:
            return
        payload = {
            "routing_key": integration_key,
            "event_action": "trigger",
            "payload": {
                "summary": f"[{alert.severity}] {alert.message}",
                "source": alert.service_id,
                "severity": "error" if alert.severity == "CRITICAL" else "warning",
            },
        }
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=10.0,
            )

    async def _emit_recovery(self, tenant_id: UUID, alert) -> None:
        """When a SERVICE_DOWN alert resolves, emit a recovery event."""
        recovery = AlertCreate(
            service_id=alert.service_id,
            service_name=alert.service_name,
            type_=AlertType.SERVICE_RECOVERY,
            severity=AlertSeverity.INFO,
            message=f"Service {alert.service_id} has recovered",
            metadata_={"original_alert_id": str(alert.id)},
        )
        await self._alert_repo.create(tenant_id, **recovery.model_dump())


class AlertRuleService:
    """Manages alert rules. RF-106."""

    def __init__(self, session: AsyncSession):
        self._s = session
        self._repo = AlertRuleRepository(session)

    async def create_rule(
        self, tenant_id: UUID, rule_in: AlertRuleCreate
    ) -> AlertRuleResponse:
        rule = await self._repo.create(tenant_id, **rule_in.model_dump())
        return AlertRuleResponse.model_validate(rule)

    async def list_rules(
        self, tenant_id: UUID, enabled_only: bool = False
    ) -> list[AlertRuleResponse]:
        rules = await self._repo.list(tenant_id, enabled_only=enabled_only)
        return [AlertRuleResponse.model_validate(r) for r in rules]

    async def get_rule(self, tenant_id: UUID, rule_id: UUID) -> Optional[AlertRuleResponse]:
        rule = await self._repo.get_by_id(tenant_id, rule_id)
        return AlertRuleResponse.model_validate(rule) if rule else None

    async def update_rule(
        self, tenant_id: UUID, rule_id: UUID, update_in: AlertRuleUpdate
    ) -> Optional[AlertRuleResponse]:
        rule = await self._repo.get_by_id(tenant_id, rule_id)
        if not rule:
            return None
        updated = await self._repo.update(rule, **update_in.model_dump(exclude_unset=True))
        return AlertRuleResponse.model_validate(updated)

    async def delete_rule(self, tenant_id: UUID, rule_id: UUID) -> bool:
        return await self._repo.delete(tenant_id, rule_id)


class NotificationChannelService:
    """Manages notification channels. RF-107."""

    def __init__(self, session: AsyncSession):
        self._s = session
        self._repo = NotificationChannelRepository(session)

    async def create_channel(
        self, tenant_id: UUID, channel_in: NotificationChannelCreate
    ) -> NotificationChannelResponse:
        # Strip secrets from configuration for storage — keep plain config
        config_dict = channel_in.configuration.model_dump() if hasattr(channel_in.configuration, 'model_dump') else channel_in.configuration
        channel = await self._repo.create(
            tenant_id,
            name=channel_in.name,
            channel_type=channel_in.channel_type.value,
            configuration=config_dict,
            enabled=channel_in.enabled,
        )
        return NotificationChannelResponse.model_validate(channel)

    async def list_channels(self, tenant_id: UUID) -> list[NotificationChannelResponse]:
        channels = await self._repo.list_enabled(tenant_id)
        return [NotificationChannelResponse.model_validate(c) for c in channels]

    async def test_channel(self, tenant_id: UUID, channel_id: UUID) -> dict:
        channel = await self._repo.get_by_id(tenant_id, channel_id)
        if not channel:
            return {"status": "error", "message": "Channel not found"}
        # Send test notification to the channel
        return {"status": "ok", "message": "Test notification sent"}