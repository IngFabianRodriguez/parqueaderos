"""Pytest fixtures and configuration for sedes-service tests."""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Sede, Zona, Espacio, OcupacionHistorial


# ============== EVENT LOOP FIXTURE ==============

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============== SAMPLE DATA FIXTURES ==============

@pytest.fixture
def sample_tenant_id() -> str:
    """Return a sample tenant ID."""
    return uuid.uuid4().hex


@pytest.fixture
def sample_sede_id() -> str:
    """Return a sample sede ID."""
    return uuid.uuid4().hex


@pytest.fixture
def sample_zona_id() -> str:
    """Return a sample zona ID."""
    return uuid.uuid4().hex


@pytest.fixture
def sample_espacio_id() -> str:
    """Return a sample espacio ID."""
    return uuid.uuid4().hex


@pytest.fixture
def sample_sede_data() -> dict:
    """Return sample sede creation data."""
    return {
        "nombre": "Sede Centro",
        "slug": "sede-centro",
        "direccion": "Calle 123 #45-67",
        "ciudad": "Bogotá",
        "departamento": "Cundinamarca",
        "pais": "Colombia",
        "latitud": 4.7110,
        "longitud": -74.0721,
        "telefono": "+573001234567",
        "email": "sede-centro@ejemplo.com",
        "capacidad": 100,
        "espacios_activos": 80,
        "horarios": '{"lunes": "07:00-22:00", "martes": "07:00-22:00"}',
        "servicios": '{"lavado": true, "seguridad": true}',
    }


@pytest.fixture
def sample_zona_data() -> dict:
    """Return sample zona creation data."""
    return {
        "nombre": "Zona A - Cubierta",
        "descripcion": "Zona cubierta para carros",
        "tipo": "cubierta",
        "capacidad": 50,
        "espacios_disponibles": 40,
        "piso": "P1",
        "estado": True,
    }


@pytest.fixture
def sample_espacio_data() -> dict:
    """Return sample espacio creation data."""
    return {
        "numero": "A-001",
        "piso": "P1",
        "tipo": "cubierta",
        "estado": "disponible",
        "descripcion": "Espacio cerca de la entrada",
    }


# ============== MODEL FIXTURES ==============

@pytest.fixture
def sample_sede(sample_sede_id: str, sample_tenant_id: str) -> Sede:
    """Return a sample Sede model instance."""
    return Sede(
        id=sample_sede_id,
        tenant_id=sample_tenant_id,
        nombre="Sede Centro",
        slug="sede-centro",
        direccion="Calle 123 #45-67",
        ciudad="Bogotá",
        departamento="Cundinamarca",
        pais="Colombia",
        latitud=4.7110,
        longitud=-74.0721,
        telefono="+573001234567",
        email="sede-centro@ejemplo.com",
        capacidad=100,
        espacios_activos=80,
        estado=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None,
    )


@pytest.fixture
def sample_sede_inactive(sample_sede_id: str, sample_tenant_id: str) -> Sede:
    """Return an inactive sample Sede model instance."""
    return Sede(
        id=sample_sede_id,
        tenant_id=sample_tenant_id,
        nombre="Sede Inactiva",
        slug="sede-inactiva",
        direccion="Calle 000",
        ciudad="Medellín",
        departamento="Antioquia",
        pais="Colombia",
        capacidad=50,
        espacios_activos=0,
        estado=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_zona(sample_zona_id: str, sample_sede_id: str, sample_tenant_id: str) -> Zona:
    """Return a sample Zona model instance."""
    return Zona(
        id=sample_zona_id,
        sede_id=sample_sede_id,
        tenant_id=sample_tenant_id,
        nombre="Zona A - Cubierta",
        descripcion="Zona cubierta para carros",
        tipo="cubierta",
        capacidad=50,
        espacios_disponibles=40,
        piso="P1",
        estado=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_zona_vip(sample_zona_id: str, sample_sede_id: str, sample_tenant_id: str) -> Zona:
    """Return a VIP sample Zona model instance."""
    return Zona(
        id=sample_zona_id,
        sede_id=sample_sede_id,
        tenant_id=sample_tenant_id,
        nombre="Zona VIP",
        descripcion="Zona VIP",
        tipo="vip",
        capacidad=10,
        espacios_disponibles=5,
        piso="P2",
        estado=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_espacio(sample_espacio_id: str, sample_zona_id: str, sample_sede_id: str, sample_tenant_id: str) -> Espacio:
    """Return a sample Espacio model instance."""
    return Espacio(
        id=sample_espacio_id,
        zona_id=sample_zona_id,
        sede_id=sample_sede_id,
        tenant_id=sample_tenant_id,
        numero="A-001",
        piso="P1",
        tipo="cubierta",
        estado="disponible",
        descripcion="Espacio cerca de la entrada",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_espacio_ocupado(sample_espacio_id: str, sample_zona_id: str, sample_sede_id: str, sample_tenant_id: str) -> Espacio:
    """Return an occupied sample Espacio model instance."""
    return Espacio(
        id=sample_espacio_id,
        zona_id=sample_zona_id,
        sede_id=sample_sede_id,
        tenant_id=sample_tenant_id,
        numero="A-002",
        piso="P1",
        tipo="cubierta",
        estado="ocupado",
        descripcion="Espacio ocupado",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_ocupacion_historial(sample_sede_id: str, sample_tenant_id: str) -> OcupacionHistorial:
    """Return a sample OcupacionHistorial model instance."""
    return OcupacionHistorial(
        id=uuid.uuid4().hex,
        sede_id=sample_sede_id,
        tenant_id=sample_tenant_id,
        fecha=datetime.now(timezone.utc),
        hora=10,
        espacios_totales=100,
        espacios_ocupados=75,
        ocupacion_pct=75.0,
        created_at=datetime.now(timezone.utc),
    )


# ============== DB SESSION FIXTURES ==============

@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Create a mock AsyncSession for testing."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_result() -> MagicMock:
    """Create a mock Result object."""
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    result.scalars = MagicMock()
    result.scalars.all = MagicMock(return_value=[])
    result.scalars().all = MagicMock(return_value=[])
    return result


@pytest_asyncio.fixture
async def async_db_session(mock_result: MagicMock) -> AsyncMock:
    """Create an async mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock(return_value=mock_result)
    session.close = AsyncMock()

    # For proper context manager usage
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    return session


# ============== SERVICE FIXTURES ==============

@pytest.fixture
def sede_service(mock_db_session: AsyncMock):
    """Create a SedeService with mock DB session."""
    from app.services.sede_service import SedeService
    return SedeService(mock_db_session)


@pytest_asyncio.fixture
async def sede_service_async(async_db_session: AsyncMock):
    """Create a SedeService with async mock DB session."""
    from app.services.sede_service import SedeService
    return SedeService(async_db_session)


@pytest.fixture
def zona_service(mock_db_session: AsyncMock):
    """Create a ZonaService with mock DB session."""
    from app.services.sede_service import ZonaService
    return ZonaService(mock_db_session)


@pytest_asyncio.fixture
async def zona_service_async(async_db_session: AsyncMock):
    """Create a ZonaService with async mock DB session."""
    from app.services.sede_service import ZonaService
    return ZonaService(async_db_session)


@pytest.fixture
def espacio_service(mock_db_session: AsyncMock):
    """Create an EspacioService with mock DB session."""
    from app.services.sede_service import EspacioService
    return EspacioService(mock_db_session)


@pytest_asyncio.fixture
async def espacio_service_async(async_db_session: AsyncMock):
    """Create an EspacioService with async mock DB session."""
    from app.services.sede_service import EspacioService
    return EspacioService(async_db_session)


@pytest.fixture
def disponibilidad_service(mock_db_session: AsyncMock):
    """Create a DisponibilidadService with mock DB session."""
    from app.services.sede_service import DisponibilidadService
    return DisponibilidadService(mock_db_session)


@pytest_asyncio.fixture
async def disponibilidad_service_async(async_db_session: AsyncMock):
    """Create a DisponibilidadService with async mock DB session."""
    from app.services.sede_service import DisponibilidadService
    return DisponibilidadService(async_db_session)


# ============== AUTH FIXTURES ==============

@pytest.fixture
def auth_headers() -> dict:
    """Return valid authentication headers."""
    return {
        "x_user_id": "user-123",
        "x_rol": "admin",
        "x_tenant_id": "tenant-123",
    }


@pytest.fixture
def auth_headers_operator() -> dict:
    """Return valid authentication headers for operator role."""
    return {
        "x_user_id": "operator-456",
        "x_rol": "operador",
        "x_tenant_id": "tenant-123",
    }


# ============== PAGINATION FIXTURES ==============

@pytest.fixture
def pagination_params() -> dict:
    """Return standard pagination parameters."""
    return {"page": 1, "page_size": 20}


# ============== FILTER FIXTURES ==============

@pytest.fixture
def filter_params_ciudad() -> dict:
    """Return filter parameters by ciudad."""
    return {"ciudad": "Bogotá"}


@pytest.fixture
def filter_params_estado() -> dict:
    """Return filter parameters by estado."""
    return {"estado": True}
