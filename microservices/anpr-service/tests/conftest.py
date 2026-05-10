"""conftest.py — shared pytest configuration and fixtures for anpr-service.

All DB/HTTP/external calls are mocked so tests run without any real infrastructure.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure the app module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────────────────────────────────────
# Mock async session — fully mocked, no real DB needed
# ─────────────────────────────────────────────────────────────────────────────

def _make_mock_session():
    """Create a fully async-mocked AsyncSession with no real engine."""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(
        scalar_one_or_none=AsyncMock(return_value=None),
        scalars=AsyncMock(return_value=MagicMock(all=AsyncMock(return_value=[]))),
        one=AsyncMock(return_value=MagicMock()),
        all=AsyncMock(return_value=[]),
    ))
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.begin = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.get_bind = MagicMock(return_value=None)
    return session


# ─────────────────────────────────────────────────────────────────────────────
# Pytest configuration — patch BEFORE app is imported
# ─────────────────────────────────────────────────────────────────────────────

with patch("app.db.session._engine", MagicMock()), \
     patch("app.db.session._SessionFactory", MagicMock()):

    # Now import the app — lazy engine is mocked, no asyncpg needed
    from app.main import app
    from app.db.session import get_db


# ─────────────────────────────────────────────────────────────────────────────
# Pytest override — replace FastAPI dependency injection
# ─────────────────────────────────────────────────────────────────────────────

def _mock_get_db():
    """Yields the mock session — used as FastAPI dependency override."""
    session = _make_mock_session()
    async def _gen():
        yield session
    return _gen()


app.dependency_overrides[get_db] = lambda: _mock_get_db()


# ─────────────────────────────────────────────────────────────────────────────
# UUID fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def auth_headers(tenant_id, user_id) -> dict[str, str]:
    return {
        "X-Tenant-Id": str(tenant_id),
        "X-User-Id": str(user_id),
        "X-Trace-ID": "test-trace-id",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Mock database session fixture (for unit tests)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db_session():
    """Async mock for sqlalchemy.ext.asyncio.AsyncSession."""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(
        scalar_one_or_none=AsyncMock(return_value=None),
        scalars=AsyncMock(return_value=MagicMock(all=AsyncMock(return_value=[]))),
        one=AsyncMock(return_value=MagicMock()),
        all=AsyncMock(return_value=[]),
        rowcount=AsyncMock(return_value=0),
    ))
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.begin = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.get_bind = MagicMock(return_value=None)
    return session


# ─────────────────────────────────────────────────────────────────────────────
# Mock repository fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_camera_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list = AsyncMock(return_value=[])
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_detection_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list = AsyncMock(return_value=[])
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.get_stats = AsyncMock(return_value={
        "total_detections": 0,
        "avg_confidence": 0.0,
        "entries": 0,
        "exits": 0,
    })
    return repo


# ─────────────────────────────────────────────────────────────────────────────
# Sample domain objects
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_camera(tenant_id):
    """Minimal ANPRCamera mock."""
    from app.db.models import ANPRCamera
    cam = MagicMock(spec=ANPRCamera)
    cam.id = uuid.uuid4()
    cam.tenant_id = tenant_id
    cam.name = "Test Camera"
    cam.sede_id = uuid.uuid4()
    cam.stream_url = "rtsp://test:554/stream"
    cam.is_active = True
    cam.lane_id = "lane-1"
    cam.confidence_threshold = 0.7
    cam.detection_zone = None
    cam.model_path = None
    cam.created_at = datetime.now(timezone.utc)
    cam.updated_at = datetime.now(timezone.utc)
    return cam


@pytest.fixture
def sample_detection(tenant_id, sample_camera):
    """Minimal PlateDetection mock."""
    from app.db.models import PlateDetection
    det = MagicMock(spec=PlateDetection)
    det.id = uuid.uuid4()
    det.tenant_id = tenant_id
    det.camera_id = sample_camera.id
    det.plate_number = "ABC123"
    det.confidence = 0.95
    det.detection_type = "entry"
    det.image_path = None
    det.cropped_plate_path = None
    det.processing_time_ms = 45
    det.matched_reservation_id = None
    det.timestamp = datetime.now(timezone.utc)
    det.created_at = datetime.now(timezone.utc)
    return det


# ─────────────────────────────────────────────────────────────────────────────
# HTTP client fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Async HTTP client — uses app.dependency_overrides for mock DB."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─────────────────────────────────────────────────────────────────────────────
# Pytest configuration
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "unit: unit test")
    config.addinivalue_line("markers", "api: api integration test")