"""Alert management endpoints — RF-101, RF-102, RF-106, RF-107, RF-109."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from uuid import UUID
from typing import Annotated, Optional

from app.db.session import AsyncSession, get_db
from app.services.alert_service import AlertService, AlertRuleService, NotificationChannelService
from app.schemas.monitoring import (
    AlertCreate, AlertResponse, AlertListResponse,
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    NotificationChannelCreate, NotificationChannelResponse,
    AlertAcknowledgeRequest, AlertSilenceRequest,
)


router = APIRouter(tags=["alerts"])


def _get_tenant_id(x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None) -> UUID:
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing X-Tenant-Id header")
    return UUID(x_tenant_id)


def _get_user_id(x_user_id: Annotated[str | None, Query(alias="X-User-Id")] = None) -> Optional[UUID]:
    return UUID(x_user_id) if x_user_id else None


# ─────────────────────────────────────────────────────────────────────────────
# Alert CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/alerts",
    response_model=AlertResponse,
    status_code=201,
    summary="Create alert (RF-102)",
)
async def create_alert(
    alert_in: AlertCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Create a new alert (usually triggered by monitoring logic)."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertService(db)
    return await service.create_alert(tenant_id, alert_in)


@router.get(
    "/alerts",
    response_model=AlertListResponse,
    summary="List alerts (RF-101)",
)
async def list_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
    status: Annotated[str | None, Query(description="Filter by status: FIRING, ACKNOWLEDGED, RESOLVED, SILENCED")] = None,
    severity: Annotated[str | None, Query(description="Filter by severity: CRITICAL, WARNING, INFO")] = None,
    service_id: Annotated[str | None, Query(description="Filter by service ID")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """List alerts with optional filters. RF-109."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertService(db)
    return await service.list_alerts(
        tenant_id, status=status, severity=severity, service_id=service_id,
        page=page, page_size=page_size,
    )


@router.get(
    "/alerts/{alert_id}",
    response_model=AlertResponse,
    summary="Get single alert",
)
async def get_alert(
    alert_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Get a specific alert by ID."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertService(db)
    result = await service.get_alert(tenant_id, alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


@router.post(
    "/alerts/{alert_id}/acknowledge",
    response_model=AlertResponse,
    summary="Acknowledge alert (RF-102)",
)
async def acknowledge_alert(
    alert_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
    x_user_id: Annotated[str | None, Query(alias="X-User-Id")] = None,
    body: AlertAcknowledgeRequest | None = None,
):
    """Mark an alert as acknowledged (being worked on)."""
    tenant_id = _get_tenant_id(x_tenant_id)
    user_id = _get_user_id(x_user_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")

    service = AlertService(db)
    result = await service.acknowledge_alert(
        tenant_id, alert_id, user_id, note=body.note if body else None
    )
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


@router.post(
    "/alerts/{alert_id}/silence",
    response_model=AlertResponse,
    summary="Silence alert (RF-108)",
)
async def silence_alert(
    alert_id: UUID,
    body: AlertSilenceRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Temporarily silence an alert with a maintenance window."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertService(db)
    result = await service.silence_alert(
        tenant_id, alert_id, until=body.until, reason=body.reason
    )
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


@router.post(
    "/alerts/{alert_id}/resolve",
    response_model=AlertResponse,
    summary="Resolve alert (RF-102)",
)
async def resolve_alert(
    alert_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Mark an alert as resolved."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertService(db)
    result = await service.resolve_alert(tenant_id, alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Alert Rules
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/alerts/rules",
    response_model=AlertRuleResponse,
    status_code=201,
    summary="Create alert rule (RF-106)",
)
async def create_alert_rule(
    rule_in: AlertRuleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Create a new alert rule."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertRuleService(db)
    return await service.create_rule(tenant_id, rule_in)


@router.get(
    "/alerts/rules",
    response_model=list[AlertRuleResponse],
    summary="List alert rules",
)
async def list_alert_rules(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
    enabled_only: Annotated[bool, Query(description="Only enabled rules")] = False,
):
    """List all alert rules for the tenant."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertRuleService(db)
    return await service.list_rules(tenant_id, enabled_only=enabled_only)


@router.get(
    "/alerts/rules/{rule_id}",
    response_model=AlertRuleResponse,
    summary="Get alert rule",
)
async def get_alert_rule(
    rule_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Get a specific alert rule."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertRuleService(db)
    result = await service.get_rule(tenant_id, rule_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return result


@router.patch(
    "/alerts/rules/{rule_id}",
    response_model=AlertRuleResponse,
    summary="Update alert rule",
)
async def update_alert_rule(
    rule_id: UUID,
    update_in: AlertRuleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Update an alert rule."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertRuleService(db)
    result = await service.update_rule(tenant_id, rule_id, update_in)
    if not result:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return result


@router.delete(
    "/alerts/rules/{rule_id}",
    status_code=204,
    summary="Delete alert rule",
)
async def delete_alert_rule(
    rule_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Delete an alert rule."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = AlertRuleService(db)
    deleted = await service.delete_rule(tenant_id, rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert rule not found")


# ─────────────────────────────────────────────────────────────────────────────
# Notification Channels
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/notification-channels",
    response_model=NotificationChannelResponse,
    status_code=201,
    summary="Create notification channel (RF-107)",
)
async def create_notification_channel(
    channel_in: NotificationChannelCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Create a new notification channel (email, slack, pagerduty, webhook)."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = NotificationChannelService(db)
    return await service.create_channel(tenant_id, channel_in)


@router.get(
    "/notification-channels",
    response_model=list[NotificationChannelResponse],
    summary="List notification channels",
)
async def list_notification_channels(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """List all enabled notification channels."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = NotificationChannelService(db)
    return await service.list_channels(tenant_id)


@router.post(
    "/notification-channels/{channel_id}/test",
    summary="Test notification channel",
)
async def test_notification_channel(
    channel_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Send a test notification through the channel."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = NotificationChannelService(db)
    return await service.test_channel(tenant_id, channel_id)