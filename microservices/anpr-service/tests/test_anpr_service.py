"""Pytest skeleton — ANPR Service."""
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
    assert data["service"] == "anpr-service"


@pytest.mark.asyncio
async def test_list_cameras_unauthorized(client):
    """Endpoint requires auth — no token returns 403."""
    response = await client.get("/api/v1/cameras")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_ready_endpoint(client):
    """Readiness probe checks DB connection."""
    response = await client.get("/ready")
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    """Prometheus metrics endpoint returns text."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_infer_endpoint_placeholder(client):
    """
    OCR inference endpoint returns placeholder response.
    TODO: RF-017 — replace with real ONNX inference tests.
    """
    import uuid

    camera_id = str(uuid.uuid4())
    response = await client.post(
        "/api/v1/infer",
        json={
            "camera_id": camera_id,
            "image_base64": "SSBhbSB0ZXN0",
            "timestamp": "2025-01-01T00:00:00Z",
        },
        headers={"Authorization": "Bearer test-token"},  # Will fail on real auth
    )
    # Without real JWT, will return 401/403 — placeholder is fine for scaffold