"""Tests for reports-service endpoints."""

import pytest


def test_validate_token_success():
    """Test validate_token with valid headers."""
    from app.core.security import validate_gateway_headers

    result = validate_gateway_headers(
        user_id="user-123",
        rol="admin",
        tenant_id="tenant-456",
    )
    assert result == {"user_id": "user-123", "rol": "admin", "tenant_id": "tenant-456"}


def test_validate_token_missing_user_id():
    """Test validate_token raises exception when user_id is missing."""
    from app.core.security import validate_gateway_headers
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        validate_gateway_headers(user_id=None, rol="admin", tenant_id="tenant-456")
    assert exc_info.value.status_code == 401
    assert "Missing X-User-Id header" in exc_info.value.detail


def test_check_permission_admin():
    """Test check_permission for admin role."""
    from app.core.security import check_permission

    assert check_permission("admin", "admin") is True
    assert check_permission("admin", "operador") is True


def test_check_permission_cliente():
    """Test check_permission for cliente role."""
    from app.core.security import check_permission

    assert check_permission("cliente", "admin") is False
    assert check_permission("cliente", "cliente") is True


class TestReportsService:
    """Tests for ReportsService."""

    def test_service_initialization(self):
        """Test reports service can be imported."""
        from app.services.reports_service import reports_service
        assert reports_service is not None