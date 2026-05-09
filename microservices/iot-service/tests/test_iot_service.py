"""Pytest skeleton — IoT Service."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    """Health endpoint returns 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "iot-service"


@pytest.mark.asyncio
async def test_list_devices_unauthorized(client):
    """Endpoint requires auth — no token returns 403."""
    response = await client.get("/api/v1/devices")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_ready_endpoint(client):
    """Readiness probe checks DB connection."""
    response = await client.get("/ready")
    # May be 200 or 503 if no DB — design decision
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    """Prometheus metrics endpoint returns text."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text" in response.headers.get("content-type", "")