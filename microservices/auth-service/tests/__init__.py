"""Tests for auth-service."""

import pytest


@pytest.fixture
def auth_headers():
    return {
        "X-User-Id": "test-user-id",
        "X-Tenant-Id": "test-tenant-id",
        "X-Rol": "admin",
    }


@pytest.fixture
def sample_user():
    return {
        "id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "email": "test@example.com",
        "full_name": "Test User",
        "rol": "admin",
    }