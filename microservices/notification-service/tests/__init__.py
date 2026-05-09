"""Tests for notification-service."""

import pytest


@pytest.fixture
def auth_headers():
    return {
        "X-User-Id": "test-user-id",
        "X-Tenant-Id": "test-tenant-id",
        "X-Rol": "admin",
    }


@pytest.fixture
def sample_notification():
    return {
        "id": "notif-123",
        "tenant_id": "test-tenant-id",
        "user_id": "test-user-id",
        "type": "email",
        "channel": "smtp",
        "recipient": "test@example.com",
        "subject": "Test",
        "content": "Test content",
    }