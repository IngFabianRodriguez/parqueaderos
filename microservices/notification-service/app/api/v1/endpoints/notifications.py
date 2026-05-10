"""Notifications API v1 endpoints."""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional

from app.core.security import validate_gateway_headers
from app.db.session import get_db
from app.services.notification_service import (
    NotificationService,
    TemplateService,
    PreferenceService,
    DeviceService,
    WebhookService,
    NotificationNotFoundError,
    TemplateNotFoundError,
    WebhookNotFoundError,
)
from app.schemas.notifications import (
    NotificationSendRequest,
    NotificationResponse,
    BatchNotificationRequest,
    BatchNotificationResponse,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    PreferenceUpdate,
    PreferenceResponse,
    DeviceRegisterRequest,
    DeviceResponse,
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookTestResponse,
    PaginatedResponse,
)


router = APIRouter(tags=["notifications"])


def _get_tenant_id(x_tenant_id: Optional[str]) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-Id header")
    return x_tenant_id


def _get_user_id(x_user_id: Optional[str]) -> str:
    if not x_user_id:
        raise HTTPException(status_code=400, detail="Missing X-User-Id header")
    return x_user_id


# ============== NOTIFICATION ENDPOINTS ==============

@router.post("/send", response_model=NotificationResponse, status_code=201)
async def send_notification(
    request: NotificationSendRequest,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Send a single notification via email/push/sms/webhook."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)
    user_id = _get_user_id(x_user_id)

    service = NotificationService(session)
    result = await service.send_notification(
        tenant_id=tenant_id,
        user_id=user_id,
        notification_type=request.type,
        channel=request.channel,
        recipient=request.recipient,
        subject=request.subject,
        content=request.content,
        metadata=request.metadata,
        use_template=False,
    )

    notification = await service.get_notification(result["notification_id"])
    return NotificationResponse.from_model(notification)


@router.post("/batch", response_model=BatchNotificationResponse)
async def send_batch_notifications(
    request: BatchNotificationRequest,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Send batch notifications to multiple users."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)

    service = NotificationService(session)
    result = await service.send_batch(
        tenant_id=tenant_id,
        user_ids=request.user_ids,
        notification_type=request.type,
        channel=request.channel,
        subject=request.subject,
        content=request.content,
        metadata=request.metadata,
    )
    return BatchNotificationResponse(**result)


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Get notification by ID."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    service = NotificationService(session)
    try:
        notification = await service.get_notification(notification_id)
        return NotificationResponse.from_model(notification)
    except NotificationNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notification {notification_id} not found")


@router.get("/notifications", response_model=PaginatedResponse)
async def list_notifications(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    session=Depends(get_db),
):
    """List notifications for the current tenant."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)

    service = NotificationService(session)
    notifications, total = await service.list_notifications(
        tenant_id, page, page_size, status
    )
    return PaginatedResponse(
        items=[NotificationResponse.from_model(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
    )


# ============== TEMPLATE ENDPOINTS ==============

@router.get("/templates", response_model=PaginatedResponse)
async def list_templates(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    page: int = 1,
    page_size: int = 20,
    type: Optional[str] = None,
    channel: Optional[str] = None,
    session=Depends(get_db),
):
    """List notification templates."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)

    service = TemplateService(session)
    templates, total = await service.list_templates(
        tenant_id, page, page_size, type, channel
    )
    return PaginatedResponse(
        items=[TemplateResponse.from_model(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/templates", response_model=TemplateResponse, status_code=201)
async def create_template(
    template_data: TemplateCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Create a new notification template."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)

    service = TemplateService(session)
    template = await service.create_template(
        tenant_id=tenant_id,
        name=template_data.name,
        template_type=template_data.type,
        channel=template_data.channel,
        subject=template_data.subject,
        content=template_data.content,
        variables=template_data.variables,
    )
    return TemplateResponse.from_model(template)


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Get template by ID."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    service = TemplateService(session)
    try:
        template = await service.get_template(template_id)
        return TemplateResponse.from_model(template)
    except TemplateNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Update a template."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    service = TemplateService(session)
    data = {
        "name": template_data.name,
        "type": template_data.type,
        "channel": template_data.channel,
        "subject": template_data.subject,
        "content": template_data.content,
        "variables": template_data.variables,
        "is_active": template_data.is_active,
    }
    data = {k: v for k, v in data.items() if v is not None}

    try:
        template = await service.update_template(template_id, data)
        return TemplateResponse.from_model(template)
    except TemplateNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Delete a template."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    service = TemplateService(session)
    deleted = await service.delete_template(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")


# ============== PREFERENCE ENDPOINTS ==============

@router.get("/preferences", response_model=PreferenceResponse)
async def get_preferences(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Get user notification preferences."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)
    user_id = _get_user_id(x_user_id)

    service = PreferenceService(session)
    pref = await service.get_preferences(tenant_id, user_id)
    return PreferenceResponse.from_model(pref)


@router.put("/preferences", response_model=PreferenceResponse)
async def update_preferences(
    preferences: PreferenceUpdate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Update user notification preferences."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)
    user_id = _get_user_id(x_user_id)

    service = PreferenceService(session)
    pref = await service.update_preferences(
        tenant_id=tenant_id,
        user_id=user_id,
        email_enabled=preferences.email_enabled,
        push_enabled=preferences.push_enabled,
        sms_enabled=preferences.sms_enabled,
        webhook_enabled=preferences.webhook_enabled,
    )
    return PreferenceResponse.from_model(pref)


# ============== DEVICE ENDPOINTS ==============

@router.post("/devices", response_model=DeviceResponse, status_code=201)
async def register_device(
    device_data: DeviceRegisterRequest,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Register a device for push notifications."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)
    user_id = _get_user_id(x_user_id)

    service = DeviceService(session)
    device = await service.register_device(
        tenant_id=tenant_id,
        user_id=user_id,
        device_token=device_data.device_token,
        device_type=device_data.device_type,
    )
    return DeviceResponse.from_model(device)


@router.get("/devices", response_model=list[DeviceResponse])
async def list_devices(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """List user's registered devices."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)
    user_id = _get_user_id(x_user_id)

    service = DeviceService(session)
    devices = await service.list_user_devices(tenant_id, user_id)
    return [DeviceResponse.from_model(d) for d in devices]


@router.delete("/devices/{device_id}", status_code=204)
async def unregister_device(
    device_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Unregister a device."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    service = DeviceService(session)
    success = await service.unregister_device(device_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")


# ============== WEBHOOK ENDPOINTS ==============

@router.get("/webhooks", response_model=PaginatedResponse)
async def list_webhooks(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    page: int = 1,
    page_size: int = 20,
    event_type: Optional[str] = None,
    session=Depends(get_db),
):
    """List webhook configurations."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)

    service = WebhookService(session)
    webhooks, total = await service.list_webhooks(tenant_id, page, page_size, event_type)
    return PaginatedResponse(
        items=[WebhookResponse.from_model(w) for w in webhooks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/webhooks", response_model=WebhookResponse, status_code=201)
async def create_webhook(
    webhook_data: WebhookCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Create a new webhook."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    tenant_id = _get_tenant_id(x_tenant_id)

    service = WebhookService(session)
    webhook = await service.create_webhook(
        tenant_id=tenant_id,
        name=webhook_data.name,
        url=webhook_data.url,
        event_type=webhook_data.event_type,
        secret=webhook_data.secret,
    )
    return WebhookResponse.from_model(webhook)


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Get webhook by ID."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    service = WebhookService(session)
    try:
        webhook = await service.get_webhook(webhook_id)
        return WebhookResponse.from_model(webhook)
    except WebhookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")


@router.delete("/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Delete a webhook."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    service = WebhookService(session)
    success = await service.delete_webhook(webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")


@router.post("/webhooks/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    session=Depends(get_db),
):
    """Test a webhook with a probe payload."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    service = WebhookService(session)
    try:
        result = await service.test_webhook(webhook_id)
        return WebhookTestResponse(**result)
    except WebhookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")