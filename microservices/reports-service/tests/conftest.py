"""Test configuration and fixtures for reports-service."""

import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create async SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide async database session for tests."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_session():
    """Mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    session.get = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_report_model():
    """Sample Report SQLAlchemy model data."""
    from app.db.models import Report
    return Report(
        id="report-123",
        tenant_id="tenant-456",
        name="Test Report",
        report_type="ingresos",
        format="pdf",
        status="ready",
        file_url="https://s3.example.com/reports/test.pdf",
        file_size_bytes=1024,
        parameters=None,
        generated_by="user-789",
        error_message=None,
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_schedule_model():
    """Sample ReportSchedule SQLAlchemy model data."""
    from app.db.models import ReportSchedule
    return ReportSchedule(
        id="schedule-123",
        tenant_id="tenant-456",
        name="Weekly Revenue Report",
        report_type="ingresos",
        schedule_cron="0 8 * * 1",
        format="pdf",
        parameters=None,
        recipients='["admin@example.com"]',
        is_active=True,
        created_by="user-789",
        last_run_at=None,
        next_run_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_bi_connector_model():
    """Sample BIConnector SQLAlchemy model data."""
    from app.db.models import BIConnector
    return BIConnector(
        id="connector-123",
        tenant_id="tenant-456",
        name="Power BI Connector",
        connector_type="powerbi",
        config='{"api_key": "xxx"}',
        status="connected",
        last_sync_at=datetime.utcnow(),
        last_error=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_tenant_headers():
    """Sample gateway headers for tenant context."""
    return {
        "x_user_id": "user-123",
        "x_rol": "admin",
        "x_tenant_id": "tenant-456",
    }


@pytest.fixture
def reports_service(mock_session):
    """ReportsService with mock session."""
    from app.services.reports_service import ReportsService
    service = ReportsService(db_session=mock_session)
    return service


@pytest.fixture
def schedules_service(mock_session):
    """SchedulesService with mock session."""
    from app.services.reports_service import SchedulesService
    service = SchedulesService(db_session=mock_session)
    return service


@pytest.fixture
def bi_connectors_service(mock_session):
    """BIConnectorsService with mock session."""
    from app.services.reports_service import BIConnectorsService
    service = BIConnectorsService(db_session=mock_session)
    return service


@pytest.fixture
def export_service():
    """ExportService instance."""
    from app.services.reports_service import ExportService
    return ExportService()