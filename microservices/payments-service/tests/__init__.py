"""Tests for payments-service."""

import pytest


@pytest.fixture
def auth_headers():
    return {
        "X-User-Id": "test-user-id",
        "X-Tenant-Id": "test-tenant-id",
        "X-Rol": "admin",
    }


@pytest.fixture
def sample_wallet():
    return {
        "id": "wallet-123",
        "tenant_id": "test-tenant-id",
        "user_id": "test-user-id",
        "balance": "100.00",
        "currency": "COP",
    }