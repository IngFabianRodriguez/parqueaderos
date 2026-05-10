"""Tests for auth-service endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock


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


def test_check_permission_admin_tenant():
    """Test check_permission for admin_tenant role."""
    from app.core.security import check_permission

    assert check_permission("admin_tenant", "superadmin") is False
    assert check_permission("admin_tenant", "admin_tenant") is True
    assert check_permission("admin_tenant", "supervisor") is True
    assert check_permission("admin_tenant", "operador") is True
    assert check_permission("admin_tenant", "cliente") is True


def test_check_permission_operador():
    """Test check_permission for operador role."""
    from app.core.security import check_permission

    assert check_permission("operador", "superadmin") is False
    assert check_permission("operador", "admin_tenant") is False
    assert check_permission("operador", "supervisor") is False
    assert check_permission("operador", "operador") is True
    assert check_permission("operador", "cliente") is True


def test_check_permission_cliente():
    """Test check_permission for cliente role."""
    from app.core.security import check_permission

    assert check_permission("cliente", "superadmin") is False
    assert check_permission("cliente", "admin_tenant") is False
    assert check_permission("cliente", "supervisor") is False
    assert check_permission("cliente", "operador") is False
    assert check_permission("cliente", "cliente") is True


def test_check_permission_superadmin():
    """Test check_permission for superadmin role (highest level)."""
    from app.core.security import check_permission

    assert check_permission("superadmin", "superadmin") is True
    assert check_permission("superadmin", "admin_tenant") is True
    assert check_permission("superadmin", "supervisor") is True
    assert check_permission("superadmin", "operador") is True
    assert check_permission("superadmin", "cliente") is True


def test_is_admin():
    """Test is_admin helper function."""
    from app.core.security import is_admin

    assert is_admin("superadmin") is True
    assert is_admin("admin_tenant") is True
    assert is_admin("supervisor") is False
    assert is_admin("operador") is False
    assert is_admin("cliente") is False


def test_require_role():
    """Test require_role helper function."""
    from app.core.security import require_role

    assert require_role("admin_tenant", ["superadmin", "admin_tenant"]) is True
    assert require_role("operador", ["superadmin", "admin_tenant"]) is False
    assert require_role("superadmin", ["superadmin"]) is True


class TestAuthService:
    """Tests for AuthService."""

    def test_hash_password(self):
        """Test password hashing."""
        from app.services.auth_service import AuthService

        password = "testpassword123"
        hashed = AuthService.hash_password(password)

        assert hashed != password
        assert AuthService.verify_password(password, hashed) is True

    def test_verify_password_wrong(self):
        """Test verify_password with wrong password."""
        from app.services.auth_service import AuthService

        password = "testpassword123"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Test access token creation."""
        from app.services.auth_service import AuthService

        data = {"sub": "user-123", "tenant_id": "tenant-456"}
        token = AuthService.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        from app.services.auth_service import AuthService

        token = AuthService.create_refresh_token()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) == 36  # UUID format