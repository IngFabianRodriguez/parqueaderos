"""Unit tests for monitoring-service business logic — RF-100 to RF-115.

All tests mock external dependencies (DB, HTTP) so they run without
any real PostgreSQL, Redis or network access.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.services.health_check_service import HealthCheckService
from app.services.alert_service import AlertService, AlertRuleService
from app.services.maintenance_window_service import MaintenanceWindowService
from app.services.sla_service import SLAService


# ─────────────────────────────────────────────────────────────────────────────
# HealthCheckService tests — RF-100, RF-101
# ─────────────────────────────────────────────────────────────────────────────

class TestHealthCheckService:
    """Active health checks against registered services."""

    @pytest.fixture
    def svc(self, mock_db_session):
        """Build a HealthCheckService with all repos pre-mocked."""
        svc = HealthCheckService(mock_db_session)
        svc._registry_repo = MagicMock()
        svc._alert_repo = MagicMock()
        svc._health_check_repo = MagicMock()
        svc._latency_repo = MagicMock()
        svc._http = MagicMock()
        return svc

    @pytest.mark.asyncio
    async def test_check_service_unregistered_returns_unknown(self, mock_db_session, tenant_id, service_id):
        """Service not in registry → status UNKNOWN."""
        svc = HealthCheckService(mock_db_session)
        svc._registry_repo = MagicMock()
        svc._registry_repo.get_by_service_id = AsyncMock(return_value=None)
        svc._alert_repo = MagicMock()
        svc._alert_repo.has_recent_firing = AsyncMock(return_value=False)
        svc._http = MagicMock()

        result = await svc.check_service(tenant_id, service_id)

        assert result["status"].value == "UNKNOWN"
        assert "not registered" in result["error"]
        await svc.close()

    @pytest.mark.asyncio
    async def test_check_service_returns_up_on_200(self, mock_db_session, tenant_id, sample_service_registry):
        """HTTP 200 → status UP with latency measurement."""
        svc = HealthCheckService(mock_db_session)
        svc._registry_repo = MagicMock()
        svc._registry_repo.get_by_service_id = AsyncMock(return_value=sample_service_registry)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"status": "UP", "version": "1.0.0", "dependencies": []})

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        mock_http.aclose = AsyncMock()
        svc._http = mock_http
        svc._latency_repo = MagicMock()
        svc._alert_repo = MagicMock()
        svc._alert_repo.has_recent_firing = AsyncMock(return_value=False)
        svc._health_check_repo = MagicMock()

        result = await svc.check_service(tenant_id, sample_service_registry.service_id)

        assert result["status"].value == "UP"
        assert "latency_ms" in result
        await svc.close()

    @pytest.mark.asyncio
    async def test_check_service_retries_on_timeout(self, mock_db_session, tenant_id, sample_service_registry):
        """Connection timeout → retry 3 times → status DOWN after all retries fail."""
        svc = HealthCheckService(mock_db_session)
        svc._registry_repo = MagicMock()
        svc._registry_repo.get_by_service_id = AsyncMock(return_value=sample_service_registry)

        mock_timeout_exc = Exception("Connection timeout")
        mock_call_count = [0]

        async def fake_get(*args, **kwargs):
            mock_call_count[0] += 1
            raise mock_timeout_exc

        mock_http = AsyncMock()
        mock_http.get = fake_get
        mock_http.aclose = AsyncMock()
        svc._http = mock_http
        svc._latency_repo = MagicMock()
        svc._alert_repo = MagicMock()
        svc._alert_repo.has_recent_firing = AsyncMock(return_value=False)
        svc._alert_repo.create = AsyncMock()
        svc._health_check_repo = MagicMock()
        svc._health_check_repo.record = AsyncMock()

        result = await svc.check_service(tenant_id, sample_service_registry.service_id)

        assert result["status"].value == "DOWN"
        assert mock_call_count[0] == 3  # 3 retries
        await svc.close()

    @pytest.mark.asyncio
    async def test_check_all_services_aggregates_results(self, mock_db_session, tenant_id):
        """check_all_services returns all registered services with their health status."""
        svc = HealthCheckService(mock_db_session)

        mock_reg1 = MagicMock()
        mock_reg1.service_id = "svc-a"
        mock_reg1.health_url = "http://svc-a:8001/health"
        mock_reg1.service_name = "Service A"

        mock_reg2 = MagicMock()
        mock_reg2.service_id = "svc-b"
        mock_reg2.health_url = "http://svc-b:8001/health"
        mock_reg2.service_name = "Service B"

        svc._registry_repo = MagicMock()
        svc._registry_repo.list_active = AsyncMock(return_value=[mock_reg1, mock_reg2])
        svc._alert_repo = MagicMock()
        svc._alert_repo.has_recent_firing = AsyncMock(return_value=False)
        svc._health_check_repo = MagicMock()
        svc._health_check_repo.record = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"status": "UP", "version": "1.0.0", "dependencies": []})

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        mock_http.aclose = AsyncMock()
        svc._http = mock_http

        results = await svc.check_all_services(tenant_id)

        assert len(results) == 2
        await svc.close()


# ─────────────────────────────────────────────────────────────────────────────
# AlertService tests — RF-102, RF-106, RF-107, RF-109
# ─────────────────────────────────────────────────────────────────────────────

class TestAlertService:
    """Alert lifecycle management."""

    @pytest.fixture
    def svc(self, mock_db_session):
        svc = AlertService(mock_db_session)
        svc._alert_repo = MagicMock()
        svc._rule_repo = MagicMock()
        svc._channel_repo = MagicMock()
        return svc

    @pytest.mark.asyncio
    async def test_create_alert_returns_alert_response(self, mock_db_session, tenant_id, service_id):
        """Creating an alert returns the alert with FIRING status."""
        from app.schemas.monitoring import AlertCreate

        svc = AlertService(mock_db_session)
        svc._alert_repo = MagicMock()
        svc._rule_repo = MagicMock()
        svc._channel_repo = MagicMock()

        # Build a mock that behaves like a real SQLAlchemy Alert model
        mock_alert = MagicMock()
        mock_alert.id = uuid4()
        mock_alert.tenant_id = tenant_id
        mock_alert.service_id = service_id
        mock_alert.service_name = "Test Service"
        mock_alert.type_ = "SERVICE_DOWN"
        mock_alert.severity = "CRITICAL"
        mock_alert.status = "FIRING"
        mock_alert.message = "Service is down"
        mock_alert.payload = {}
        mock_alert.acknowledged = False
        mock_alert.acknowledged_at = None
        mock_alert.acknowledged_by = None
        mock_alert.silenced_until = None
        mock_alert.resolved_at = None
        mock_alert.created_at = datetime.now(timezone.utc)
        mock_alert.updated_at = datetime.now(timezone.utc)
        mock_alert.model_validate = lambda *a, **kw: mock_alert  # make model_validate a no-op

        svc._alert_repo.create = AsyncMock(return_value=mock_alert)
        svc._rule_repo.list_enabled = AsyncMock(return_value=[])
        svc._channel_repo.list_enabled = AsyncMock(return_value=[])

        alert_in = AlertCreate(
            service_id=service_id,
            service_name="Test Service",
            alert_type="SERVICE_DOWN",
            severity="CRITICAL",
            message="Service is down",
        )
        result = await svc.create_alert(tenant_id=tenant_id, alert_in=alert_in)

        assert result.status == "FIRING"
        assert result.severity == "CRITICAL"

    @pytest.mark.asyncio
    async def test_acknowledge_alert_returns_updated_response(self, mock_db_session, tenant_id):
        """Acknowledging an alert returns the updated alert response."""
        svc = AlertService(mock_db_session)
        svc._alert_repo = MagicMock()

        alert_id = uuid4()
        user_id = uuid4()

        mock_alert = MagicMock()
        mock_alert.id = alert_id
        mock_alert.status = "FIRING"
        mock_alert.acknowledged = False
        mock_alert.acknowledged_at = None
        mock_alert.acknowledged_by = None
        mock_alert.model_validate = lambda *a, **kw: mock_alert

        svc._alert_repo.get_by_id = AsyncMock(return_value=mock_alert)
        svc._alert_repo.acknowledge = AsyncMock()
        svc._rule_repo = MagicMock()
        svc._channel_repo = MagicMock()

        result = await svc.acknowledge_alert(tenant_id, alert_id, user_id)

        assert result is not None
        svc._alert_repo.acknowledge.assert_called_once_with(mock_alert, user_id, None)

    @pytest.mark.asyncio
    async def test_silence_alert_returns_updated_response(self, mock_db_session, tenant_id):
        """Silencing an alert returns the updated alert response."""
        svc = AlertService(mock_db_session)
        svc._alert_repo = MagicMock()

        alert_id = uuid4()
        silence_until = datetime.now(timezone.utc) + timedelta(hours=1)

        mock_alert = MagicMock()
        mock_alert.id = alert_id
        mock_alert.status = "FIRING"
        mock_alert.silenced_until = None
        mock_alert.model_validate = lambda *a, **kw: mock_alert

        svc._alert_repo.get_by_id = AsyncMock(return_value=mock_alert)
        svc._alert_repo.silence = AsyncMock()
        svc._rule_repo = MagicMock()
        svc._channel_repo = MagicMock()

        result = await svc.silence_alert(tenant_id, alert_id, silence_until)

        assert result is not None
        svc._alert_repo.silence.assert_called_once_with(mock_alert, silence_until, None)

    @pytest.mark.asyncio
    async def test_list_alerts_returns_paginated(self, mock_db_session, tenant_id):
        """list_alerts returns (items, total) tuple for pagination."""
        svc = AlertService(mock_db_session)
        svc._alert_repo = MagicMock()
        svc._rule_repo = MagicMock()
        svc._channel_repo = MagicMock()

        mock_alert = MagicMock()
        mock_alert.id = uuid4()
        mock_alert.status = "FIRING"
        mock_alert.acknowledged = False
        mock_alert.model_validate = lambda *a, **kw: mock_alert

        svc._alert_repo.list = AsyncMock(return_value=([mock_alert], 1))

        items, total = await svc.list_alerts(tenant_id)

        assert total == 1
        assert len(items) == 1


# ─────────────────────────────────────────────────────────────────────────────
# MaintenanceWindowService tests — RF-108
# ─────────────────────────────────────────────────────────────────────────────

class TestMaintenanceWindowService:
    """Maintenance window management."""

    @pytest.fixture
    def svc(self, mock_db_session):
        svc = MaintenanceWindowService(mock_db_session)
        svc._repo = MagicMock()
        svc._alert_repo = MagicMock()
        return svc

    @pytest.mark.asyncio
    async def test_create_window_validates_no_overlap(self, mock_db_session, tenant_id):
        """Creating a window that overlaps an existing one raises ValueError."""
        from app.schemas.monitoring import MaintenanceWindowCreate

        svc = MaintenanceWindowService(mock_db_session)
        svc._repo = MagicMock()
        svc._alert_repo = MagicMock()

        existing_start = datetime.now(timezone.utc)
        existing_end = existing_start + timedelta(hours=2)

        existing = MagicMock()
        existing.start_time = existing_start
        existing.end_time = existing_end
        existing.estado = "active"
        existing.model_validate = lambda *a, **kw: existing

        svc._repo.list = AsyncMock(return_value=[existing])

        new_start = existing_start + timedelta(minutes=30)
        new_end = existing_end + timedelta(minutes=30)

        window_in = MaintenanceWindowCreate(
            name="Test Maintenance",
            start_time=new_start,
            end_time=new_end,
        )

        with pytest.raises(ValueError, match="overlaps"):
            await svc.create_window(tenant_id=tenant_id, window_in=window_in)

    @pytest.mark.asyncio
    async def test_create_window_no_overlap_succeeds(self, mock_db_session, tenant_id):
        """Non-overlapping window is created successfully."""
        from app.schemas.monitoring import MaintenanceWindowCreate

        svc = MaintenanceWindowService(mock_db_session)
        svc._repo = MagicMock()
        svc._alert_repo = MagicMock()

        svc._repo.list = AsyncMock(return_value=[])

        mock_window = MagicMock()
        mock_window.id = uuid4()
        mock_window.name = "Test Maintenance"
        mock_window.estado = "active"
        mock_window.model_validate = lambda *a, **kw: mock_window
        svc._repo.create = AsyncMock(return_value=mock_window)

        start = datetime.now(timezone.utc) + timedelta(days=1)
        end = start + timedelta(hours=1)

        window_in = MaintenanceWindowCreate(
            name="Test Maintenance",
            start_time=start,
            end_time=end,
        )

        result = await svc.create_window(tenant_id=tenant_id, window_in=window_in)

        assert result is not None
        svc._repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_windows_returns_all_windows(self, mock_db_session, tenant_id):
        """list_windows returns all windows for the tenant."""
        svc = MaintenanceWindowService(mock_db_session)
        svc._repo = MagicMock()
        svc._alert_repo = MagicMock()

        mock_window = MagicMock()
        mock_window.id = uuid4()
        mock_window.name = "Test Window"
        mock_window.model_validate = lambda *a, **kw: mock_window

        svc._repo.list = AsyncMock(return_value=[mock_window])

        windows = await svc.list_windows(tenant_id)

        assert len(windows) == 1


# ─────────────────────────────────────────────────────────────────────────────
# SLAService tests — RF-111, RF-113
# ─────────────────────────────────────────────────────────────────────────────

class TestSLAService:
    """SLA reporting and uptime calculation."""

    @pytest.fixture
    def svc(self, mock_db_session):
        svc = SLAService(mock_db_session)
        svc._health_repo = MagicMock()
        svc._alert_repo = MagicMock()
        svc._sla_report_repo = MagicMock()
        return svc

    @pytest.mark.asyncio
    async def test_get_current_uptime_returns_float(self, mock_db_session, tenant_id, service_id):
        """get_current_uptime returns a float percentage."""
        svc = SLAService(mock_db_session)
        svc._health_repo = MagicMock()
        svc._health_repo.calculate_uptime = AsyncMock(return_value=99.5)
        svc._alert_repo = MagicMock()
        svc._sla_report_repo = MagicMock()

        uptime = await svc.get_current_uptime(tenant_id, service_id, days=30)

        assert uptime == 99.5
        svc._health_repo.calculate_uptime.assert_called_once_with(tenant_id, service_id, 30)

    @pytest.mark.asyncio
    async def test_generate_report_returns_sla_response(self, mock_db_session, tenant_id, service_id):
        """generate_report returns an SLAReportResponse."""
        from app.schemas.monitoring import SLAReportRequest

        svc = SLAService(mock_db_session)
        svc._health_repo = MagicMock()
        svc._health_repo.calculate_uptime = AsyncMock(return_value=99.5)
        svc._alert_repo = MagicMock()
        svc._alert_repo.list = AsyncMock(return_value=([], 0))
        svc._sla_report_repo = MagicMock()

        mock_report = MagicMock()
        mock_report.id = uuid4()
        mock_report.model_validate = lambda *a, **kw: mock_report
        svc._sla_report_repo.create = AsyncMock(return_value=mock_report)

        request = SLAReportRequest(
            service_id=service_id,
            start_date=datetime.now(timezone.utc) - timedelta(days=30),
            end_date=datetime.now(timezone.utc),
        )

        report = await svc.generate_report(tenant_id=tenant_id, request=request)

        assert report is not None
        svc._sla_report_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_metrics_returns_business_metrics(self, mock_db_session, tenant_id):
        """get_metrics returns business metrics for the tenant."""
        svc = SLAService(mock_db_session)
        svc._health_repo = MagicMock()
        svc._health_repo.list_recent = AsyncMock(return_value=[])
        svc._alert_repo = MagicMock()
        svc._alert_repo.list = AsyncMock(return_value=([], 0))
        svc._sla_report_repo = MagicMock()

        metrics = await svc.get_metrics(tenant_id)

        assert metrics is not None
        assert hasattr(metrics, "total_alerts") or hasattr(metrics, "uptime_percentage")


# ─────────────────────────────────────────────────────────────────────────────
# AlertRuleService tests — RF-106
# ─────────────────────────────────────────────────────────────────────────────

class TestAlertRuleService:
    """Alert rule CRUD operations."""

    @pytest.fixture
    def svc(self, mock_db_session):
        svc = AlertRuleService(mock_db_session)
        svc._repo = MagicMock()
        return svc

    @pytest.mark.asyncio
    async def test_create_rule_returns_rule_response(self, mock_db_session, tenant_id):
        """Creating a rule returns the rule with all configuration fields."""
        from app.schemas.monitoring import AlertRuleCreate

        svc = AlertRuleService(mock_db_session)
        svc._repo = MagicMock()

        mock_rule = MagicMock()
        mock_rule.id = uuid4()
        mock_rule.tenant_id = tenant_id
        mock_rule.name = "CPU High Rule"
        mock_rule.severity = "WARNING"
        mock_rule.condition = {"metric": "cpu_percent", "operator": "gt", "threshold": 80}
        mock_rule.enabled = True
        mock_rule.created_at = datetime.now(timezone.utc)
        mock_rule.updated_at = datetime.now(timezone.utc)
        mock_rule.model_validate = lambda *a, **kw: mock_rule

        svc._repo.create = AsyncMock(return_value=mock_rule)

        rule_in = AlertRuleCreate(
            name="CPU High Rule",
            severity="WARNING",
            condition={"metric": "cpu_percent", "operator": "gt", "threshold": 80},
        )
        result = await svc.create_rule(tenant_id=tenant_id, rule_in=rule_in)

        assert result.name == "CPU High Rule"
        assert result.severity == "WARNING"
        assert result.enabled is True

    @pytest.mark.asyncio
    async def test_delete_rule_returns_bool(self, mock_db_session, tenant_id):
        """Deleting a rule calls the repository and returns success bool."""
        svc = AlertRuleService(mock_db_session)
        svc._repo = MagicMock()
        svc._repo.delete = AsyncMock(return_value=True)

        rule_id = uuid4()
        result = await svc.delete_rule(tenant_id, rule_id)

        assert result is True
        svc._repo.delete.assert_called_once_with(tenant_id, rule_id)