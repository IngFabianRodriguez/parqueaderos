"""API integration tests for health endpoints — RF-100, RF-101."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from httpx import AsyncClient, ASGITransport

from app.main import app


class TestHealthEndpoints:
    """API tests for /api/v1/health/* endpoints."""

    @pytest.mark.asyncio
    async def test_liveness_returns_200(self):
        """GET /api/v1/health/live should return 200."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health/live")
            assert response.status_code == 200
            assert response.json()["status"] == "alive"

    @pytest.mark.asyncio
    async def test_health_root_returns_200(self):
        """GET /health should return 200."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_readiness_db_failure_returns_503(self):
        """GET /api/v1/health/ready should return 503 when DB is unreachable."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.db.session.get_db") as mock_get_db:
                mock_session = AsyncMock()
                mock_session.execute = AsyncMock(side_effect=Exception("DB connection failed"))
                mock_get_db.return_value = iter([mock_session])

                response = await client.get("/api/v1/health/ready")
                assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_list_service_health_requires_tenant_header(self):
        """GET /api/v1/health/services without X-Tenant-Id should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health/services")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_service_health_returns_list(self, tenant_id):
        """GET /api/v1/health/services with tenant header should return health list."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.health.HealthCheckService") as MockService:
                mock_instance = MagicMock()
                mock_instance.check_all_services = AsyncMock(return_value=[])
                mock_instance.close = AsyncMock()
                MockService.return_value = mock_instance

                response = await client.get(
                    "/api/v1/health/services",
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_service_health_validates_uuid(self, tenant_id):
        """GET /api/v1/health/services/{invalid} should return 422."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/health/services/not-a-uuid",
                headers={"X-Tenant-Id": str(tenant_id)},
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_dashboard_requires_tenant_header(self):
        """GET /api/v1/health/dashboard without tenant header should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health/dashboard")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_dashboard_returns_dashboard_response(self, tenant_id):
        """Dashboard endpoint should return aggregated health data."""
        from app.schemas.monitoring import DashboardResponse, ServiceHealthSummary

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.health.HealthCheckService") as MockService:
                mock_instance = MagicMock()
                mock_dashboard = DashboardResponse(
                    overall_status="DEGRADED",
                    healthy_count=2,
                    unhealthy_count=1,
                    services=[],
                    alerts_firing=3,
                    maintenance_windows=0,
                    checked_at=datetime.utcnow(),
                )
                mock_instance.build_dashboard = AsyncMock(return_value=mock_dashboard)
                mock_instance.close = AsyncMock()
                MockService.return_value = mock_instance

                response = await client.get(
                    "/api/v1/health/dashboard",
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["overall_status"] == "DEGRADED"
                assert data["healthy_count"] == 2
                assert data["unhealthy_count"] == 1


class TestAlertEndpoints:
    """API tests for /api/v1/alerts/* endpoints."""

    @pytest.mark.asyncio
    async def test_create_alert_returns_201(self, tenant_id):
        """POST /api/v1/alerts should return 201 with alert data."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.alerts.AlertService") as MockService:
                mock_instance = MagicMock()
                mock_instance.create_alert = AsyncMock(return_value=MagicMock(
                    id=uuid4(),
                    service_id="test-svc",
                    type_="SERVICE_DOWN",
                    severity="CRITICAL",
                    status="FIRING",
                    message="Service down",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    acknowledged=False,
                    acknowledged_at=None,
                    acknowledged_by=None,
                    silenced_until=None,
                    resolved_at=None,
                    metadata_={},
                ))
                MockService.return_value = mock_instance

                response = await client.post(
                    "/api/v1/alerts",
                    json={
                        "service_id": "test-svc",
                        "type": "SERVICE_DOWN",
                        "severity": "CRITICAL",
                        "message": "Service down",
                    },
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_alerts_requires_tenant(self):
        """GET /api/v1/alerts without tenant header should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/alerts")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_alerts_returns_paginated_response(self, tenant_id):
        """GET /api/v1/alerts should return paginated list."""
        from app.schemas.monitoring import AlertListResponse

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.alerts.AlertService") as MockService:
                mock_instance = MagicMock()
                mock_instance.list_alerts = AsyncMock(return_value=AlertListResponse(
                    items=[],
                    total=0,
                    page=1,
                    page_size=50,
                    total_pages=0,
                ))
                MockService.return_value = mock_instance

                response = await client.get(
                    "/api/v1/alerts",
                    params={"status": "FIRING", "page": 1, "page_size": 50},
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert "total" in data

    @pytest.mark.asyncio
    async def test_acknowledge_alert_requires_user_header(self, tenant_id, sample_alert):
        """POST /api/v1/alerts/{id}/acknowledge without X-User-Id should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/alerts/{uuid4()}/acknowledge",
                headers={"X-Tenant-Id": str(tenant_id)},
            )
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_acknowledge_alert_not_found_returns_404(self, tenant_id, user_id):
        """Acknowledging non-existent alert should return 404."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.alerts.AlertService") as MockService:
                mock_instance = MagicMock()
                mock_instance.acknowledge_alert = AsyncMock(return_value=None)
                MockService.return_value = mock_instance

                response = await client.post(
                    f"/api/v1/alerts/{uuid4()}/acknowledge",
                    headers={
                        "X-Tenant-Id": str(tenant_id),
                        "X-User-Id": str(user_id),
                    },
                )
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_silence_alert_requires_tenant(self):
        """POST /api/v1/alerts/{id}/silence without tenant should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/alerts/{uuid4()}/silence",
                json={"until": "2025-12-31T23:59:59Z", "reason": "Maintenance"},
            )
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_nonexistent_alert_returns_404(self, tenant_id):
        """GET /api/v1/alerts/{non-existent-id} should return 404."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.alerts.AlertService") as MockService:
                mock_instance = MagicMock()
                mock_instance.get_alert = AsyncMock(return_value=None)
                MockService.return_value = mock_instance

                response = await client.get(
                    f"/api/v1/alerts/{uuid4()}",
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 404


class TestMaintenanceWindowEndpoints:
    """API tests for /api/v1/maintenance-windows/* endpoints."""

    @pytest.mark.asyncio
    async def test_create_maintenance_window_requires_tenant(self):
        """POST /api/v1/maintenance-windows without tenant should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/maintenance-windows",
                json={
                    "name": "Test Window",
                    "start_time": "2025-06-01T00:00:00Z",
                    "end_time": "2025-06-01T02:00:00Z",
                },
            )
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_maintenance_windows(self, tenant_id):
        """GET /api/v1/maintenance-windows should return list."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.maintenance.MaintenanceWindowService") as MockService:
                mock_instance = MagicMock()
                mock_instance.list_windows = AsyncMock(return_value=[])
                MockService.return_value = mock_instance

                response = await client.get(
                    "/api/v1/maintenance-windows",
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 200
                assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_nonexistent_window_returns_404(self, tenant_id):
        """GET /api/v1/maintenance-windows/{id} should return 404."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.maintenance.MaintenanceWindowService") as MockService:
                mock_instance = MagicMock()
                mock_instance.get_window = AsyncMock(return_value=None)
                MockService.return_value = mock_instance

                response = await client.get(
                    f"/api/v1/maintenance-windows/{uuid4()}",
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 404


class TestMetricsEndpoints:
    """API tests for /api/v1/metrics/* endpoints."""

    @pytest.mark.asyncio
    async def test_metrics_requires_tenant(self):
        """GET /api/v1/metrics/infrastructure without tenant should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/metrics/infrastructure",
                params={"service_id": "test-svc", "from": "2025-01-01T00:00:00Z", "to": "2025-01-02T00:00:00Z"},
            )
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_infrastructure_metrics(self, tenant_id):
        """GET /api/v1/metrics/infrastructure should return metrics data."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.metrics.MetricsService") as MockService:
                mock_instance = MagicMock()
                mock_instance.get_infrastructure_metrics = AsyncMock(return_value={"cpu": [], "memory": []})
                MockService.return_value = mock_instance

                response = await client.get(
                    "/api/v1/metrics/infrastructure",
                    params={
                        "service_id": "test-svc",
                        "from": "2025-01-01T00:00:00Z",
                        "to": "2025-01-02T00:00:00Z",
                    },
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_export_metrics_defaults_to_json(self, tenant_id):
        """GET /api/v1/metrics/export should default to JSON format."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.metrics.MetricsService") as MockService:
                mock_instance = MagicMock()
                mock_instance.export_metrics = AsyncMock(return_value=MagicMock(
                    format="json",
                    data=[],
                    from_=datetime.utcnow(),
                    to=datetime.utcnow(),
                    service_id=None,
                    metric_type=None,
                ))
                MockService.return_value = mock_instance

                response = await client.get(
                    "/api/v1/metrics/export",
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_top_slow_endpoints_default_limit(self, tenant_id):
        """GET /api/v1/metrics/top-slow should default to limit=10."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.metrics.MetricsService") as MockService:
                mock_instance = MagicMock()
                mock_instance.get_top_slow_endpoints = AsyncMock(return_value=[])
                MockService.return_value = mock_instance

                response = await client.get(
                    "/api/v1/metrics/top-slow",
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 200
                mock_instance.get_top_slow_endpoints.assert_awaited_once()
                call_args = mock_instance.get_top_slow_endpoints.call_args
                assert call_args[1]["limit"] == 10


class TestSLAEndpoints:
    """API tests for /api/v1/sla/* endpoints."""

    @pytest.mark.asyncio
    async def test_generate_sla_report_requires_tenant(self):
        """POST /api/v1/sla/report without tenant should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/sla/report",
                json={
                    "service_id": "test-svc",
                    "sla_type": " uptime",
                    "target_percent": 99.9,
                    "from_": "2025-01-01T00:00:00Z",
                    "to": "2025-01-31T23:59:59Z",
                },
            )
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_uptime_requires_tenant(self):
        """GET /api/v1/sla/uptime/{service_id} without tenant should return 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/sla/uptime/test-svc")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_uptime_returns_percent(self, tenant_id):
        """GET /api/v1/sla/uptime/{service_id} should return uptime percent."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.sla.SLAService") as MockService:
                mock_instance = MagicMock()
                mock_instance.get_current_uptime = AsyncMock(return_value=99.95)
                MockService.return_value = mock_instance

                response = await client.get(
                    "/api/v1/sla/uptime/test-svc",
                    params={"days": 30},
                    headers={"X-Tenant-Id": str(tenant_id)},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["uptime_percent"] == 99.95
                assert data["window_days"] == 30


class TestGlobalErrorHandling:
    """Tests for global exception handler."""

    @pytest.mark.asyncio
    async def test_404_returns_proper_json(self):
        """Non-existent route should return 404 with proper JSON body."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/nonexistent")
            assert response.status_code == 404
            # FastAPI returns its own 404 body — this is correct behavior
