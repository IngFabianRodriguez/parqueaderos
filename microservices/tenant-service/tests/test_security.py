"""Tests for security utilities."""
import pytest
from fastapi import HTTPException
from app.core.security import (
    validate_gateway_headers,
    require_tenant_admin,
    check_permission,
)


def test_validate_headers_all_present():
    result = validate_gateway_headers(
        x_user_id="user-123",
        x_rol="tenant_admin",
        x_tenant_id="tenant-456",
    )
    assert result == {"user_id": "user-123", "rol": "tenant_admin", "tenant_id": "tenant-456"}


def test_validate_headers_missing_user_id():
    with pytest.raises(HTTPException) as exc:
        validate_gateway_headers(x_user_id=None, x_rol="admin", x_tenant_id="t")
    assert exc.value.status_code == 401
    assert "X-User-Id" in exc.value.detail


def test_validate_headers_missing_rol():
    with pytest.raises(HTTPException) as exc:
        validate_gateway_headers(x_user_id="u", x_rol=None, x_tenant_id="t")
    assert exc.value.status_code == 401
    assert "X-Rol" in exc.value.detail


def test_validate_headers_missing_tenant():
    with pytest.raises(HTTPException) as exc:
        validate_gateway_headers(x_user_id="u", x_rol="a", x_tenant_id=None)
    assert exc.value.status_code == 401
    assert "X-Tenant-Id" in exc.value.detail


def test_require_tenant_admin_valid():
    require_tenant_admin("tenant_admin")  # No exception


def test_require_tenant_admin_superadmin_valid():
    require_tenant_admin("superadmin")  # No exception


def test_require_tenant_admin_invalid():
    with pytest.raises(HTTPException) as exc:
        require_tenant_admin("operador")
    assert exc.value.status_code == 403


def test_require_tenant_admin_cliente_fails():
    with pytest.raises(HTTPException) as exc:
        require_tenant_admin("cliente")
    assert exc.value.status_code == 403


def test_check_permission_superadmin():
    assert check_permission("superadmin", "superadmin") is True
    assert check_permission("superadmin", "tenant_admin") is True
    assert check_permission("superadmin", "sede_manager") is True
    assert check_permission("superadmin", "operador") is True
    assert check_permission("superadmin", "cliente") is True


def test_check_permission_tenant_admin():
    assert check_permission("tenant_admin", "tenant_admin") is True
    assert check_permission("tenant_admin", "sede_manager") is True
    assert check_permission("tenant_admin", "operador") is True
    assert check_permission("tenant_admin", "cliente") is True
    assert check_permission("tenant_admin", "superadmin") is False


def test_check_permission_sede_manager():
    assert check_permission("sede_manager", "sede_manager") is True
    assert check_permission("sede_manager", "operador") is True
    assert check_permission("sede_manager", "cliente") is True
    assert check_permission("sede_manager", "tenant_admin") is False


def test_check_permission_operador():
    assert check_permission("operador", "operador") is True
    assert check_permission("operador", "cliente") is True
    assert check_permission("operador", "sede_manager") is False


def test_check_permission_cliente():
    assert check_permission("cliente", "cliente") is True
    assert check_permission("cliente", "operador") is False


def test_check_permission_unknown_role():
    assert check_permission("unknown", "cliente") is False
