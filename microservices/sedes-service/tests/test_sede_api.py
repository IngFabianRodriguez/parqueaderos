"""Tests for sedes API endpoints.

Covers all CRUD endpoints for sedes, zonas, espacios.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.db.models import Sede, Zona, Espacio
from app.services.sede_service import (
    SedeNotFoundError,
    ZonaNotFoundError,
    EspacioNotFoundError,
    DuplicateSlugError,
)


# ============== HEALTH ENDPOINTS TESTS ==============

class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health endpoint returns healthy status."""
        from app.main import app

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "sedes-service"

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint returns service info."""
        from app.main import app

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Sedes Service"
            assert data["version"] == "0.1.0"


# ============== AUTH REQUIRED TESTS ==============

class TestAuthRequired:
    """Tests for authentication requirements on endpoints."""

    @pytest.mark.asyncio
    async def test_create_sede_requires_auth(self):
        """Test that create sede endpoint requires auth headers."""
        from app.main import app

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/sedes/", json={
                "nombre": "Sede Centro",
                "slug": "sede-centro",
                "direccion": "Calle 123",
            })
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_sedes_requires_auth(self):
        """Test that list sedes endpoint requires auth headers."""
        from app.main import app

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/sedes/")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_sede_requires_auth(self):
        """Test that get sede endpoint requires auth headers."""
        from app.main import app

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/sedes/sede-123")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_sede_requires_auth(self):
        """Test that update sede endpoint requires auth headers."""
        from app.main import app

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put("/api/v1/sedes/sede-123", json={
                "nombre": "Sede Actualizada",
            })
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_sede_requires_auth(self):
        """Test that delete sede endpoint requires auth headers."""
        from app.main import app

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/api/v1/sedes/sede-123")
            assert response.status_code == 401


# ============== SEDE ENDPOINTS TESTS ==============

class TestCreateSedeEndpoint:
    """Tests for POST /sedes endpoint."""

    @pytest.mark.asyncio
    async def test_create_sede_success(self, auth_headers: dict, sample_sede_data: dict):
        """Test successful sede creation."""
        from app.main import app
        from app.db.models import Sede
        from unittest.mock import AsyncMock

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.create_sede = AsyncMock(
                return_value=Sede(
                    id="new-sede-id",
                    tenant_id=auth_headers["x_tenant_id"],
                    nombre=sample_sede_data["nombre"],
                    slug=sample_sede_data["slug"],
                    direccion=sample_sede_data.get("direccion"),
                    ciudad=sample_sede_data.get("ciudad"),
                    departamento=sample_sede_data.get("departamento"),
                    pais=sample_sede_data.get("pais", "Colombia"),
                    capacidad=sample_sede_data.get("capacidad", 0),
                    espacios_activos=sample_sede_data.get("espacios_activos", 0),
                    estado=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/sedes/",
                    json=sample_sede_data,
                    headers=auth_headers,
                )
                assert response.status_code == 201
                data = response.json()
                assert data["nombre"] == sample_sede_data["nombre"]
                assert data["slug"] == sample_sede_data["slug"]

    @pytest.mark.asyncio
    async def test_create_sede_duplicate_slug(self, auth_headers: dict, sample_sede_data: dict):
        """Test create sede with duplicate slug returns 409."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.create_sede = AsyncMock(
                side_effect=DuplicateSlugError(sample_sede_data["slug"], auth_headers["x_tenant_id"])
            )
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/sedes/",
                    json=sample_sede_data,
                    headers=auth_headers,
                )
                assert response.status_code == 409


class TestListSedesEndpoint:
    """Tests for GET /sedes endpoint."""

    @pytest.mark.asyncio
    async def test_list_sedes_empty(self, auth_headers: dict):
        """Test listing sedes when none exist."""
        from app.main import app
        from app.db.models import Sede

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.list_sedes = AsyncMock(return_value=([], 0))
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/sedes/",
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert data["items"] == []
                assert data["total"] == 0
                assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_sedes_with_pagination(self, auth_headers: dict, sample_sede: Sede):
        """Test listing sedes with pagination."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.list_sedes = AsyncMock(return_value=([sample_sede], 1))
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/sedes/?page=1&page_size=10",
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data["items"]) == 1
                assert data["total"] == 1
                assert data["page"] == 1
                assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_list_sedes_with_filters(self, auth_headers: dict):
        """Test listing sedes with filters."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.list_sedes = AsyncMock(return_value=([], 0))
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/sedes/?estado=true&ciudad=Bogotá",
                    headers=auth_headers,
                )
                assert response.status_code == 200


class TestGetSedeEndpoint:
    """Tests for GET /sedes/{sede_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_sede_success(self, auth_headers: dict, sample_sede: Sede):
        """Test successful sede retrieval."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_sede = AsyncMock(return_value=sample_sede)
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    f"/api/v1/sedes/{sample_sede.id}",
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == sample_sede.id
                assert data["nombre"] == sample_sede.nombre

    @pytest.mark.asyncio
    async def test_get_sede_not_found(self, auth_headers: dict):
        """Test get non-existent sede returns 404."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_sede = AsyncMock(
                side_effect=SedeNotFoundError("non-existent")
            )
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/sedes/non-existent",
                    headers=auth_headers,
                )
                assert response.status_code == 404


class TestUpdateSedeEndpoint:
    """Tests for PUT /sedes/{sede_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_sede_success(self, auth_headers: dict, sample_sede: Sede):
        """Test successful sede update."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.update_sede = AsyncMock(return_value=sample_sede)
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    f"/api/v1/sedes/{sample_sede.id}",
                    json={"nombre": "Sede Actualizada"},
                    headers=auth_headers,
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_sede_not_found(self, auth_headers: dict):
        """Test update non-existent sede returns 404."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.update_sede = AsyncMock(
                side_effect=SedeNotFoundError("non-existent")
            )
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/sedes/non-existent",
                    json={"nombre": "Test"},
                    headers=auth_headers,
                )
                assert response.status_code == 404


class TestDeleteSedeEndpoint:
    """Tests for DELETE /sedes/{sede_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_sede_success(self, auth_headers: dict, sample_sede: Sede):
        """Test successful sede deletion."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.delete_sede = AsyncMock(return_value=True)
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.delete(
                    f"/api/v1/sedes/{sample_sede.id}",
                    headers=auth_headers,
                )
                assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_sede_not_found(self, auth_headers: dict):
        """Test delete non-existent sede returns 404."""
        from app.main import app

        with patch("app.api.v1.router.get_sede_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.delete_sede = AsyncMock(
                side_effect=SedeNotFoundError("non-existent")
            )
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.delete(
                    "/api/v1/sedes/non-existent",
                    headers=auth_headers,
                )
                assert response.status_code == 404


# ============== ZONA ENDPOINTS TESTS ==============

class TestZonasEndpoints:
    """Tests for zona CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_zonas_empty(self, auth_headers: dict, sample_sede: Sede):
        """Test listing zonas when none exist."""
        from app.main import app

        with patch("app.api.v1.router.get_zona_service") as mock_zona_get:
            with patch("app.api.v1.router.get_sede_service") as mock_sede_get:
                mock_zona_service = MagicMock()
                mock_zona_service.list_zonas = AsyncMock(return_value=[])
                mock_zona_get.return_value = mock_zona_service

                mock_sede_service = MagicMock()
                mock_sede_service.get_sede = AsyncMock(return_value=sample_sede)
                mock_sede_get.return_value = mock_sede_service

                from httpx import AsyncClient, ASGITransport
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get(
                        f"/api/v1/sedes/{sample_sede.id}/zonas",
                        headers=auth_headers,
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert data["items"] == []
                    assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_zona_success(self, auth_headers: dict, sample_sede: Sede, sample_zona_data: dict):
        """Test successful zona creation."""
        from app.main import app
        from app.db.models import Zona

        zona = Zona(
            id="new-zona-id",
            sede_id=sample_sede.id,
            tenant_id=auth_headers["x_tenant_id"],
            nombre=sample_zona_data["nombre"],
            descripcion=sample_zona_data.get("descripcion"),
            tipo=sample_zona_data["tipo"],
            capacidad=sample_zona_data["capacidad"],
            espacios_disponibles=sample_zona_data["espacios_disponibles"],
            piso=sample_zona_data["piso"],
            estado=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with patch("app.api.v1.router.get_zona_service") as mock_zona_get:
            with patch("app.api.v1.router.get_sede_service") as mock_sede_get:
                mock_zona_service = MagicMock()
                mock_zona_service.create_zona = AsyncMock(return_value=zona)
                mock_zona_get.return_value = mock_zona_service

                mock_sede_service = MagicMock()
                mock_sede_service.get_sede = AsyncMock(return_value=sample_sede)
                mock_sede_get.return_value = mock_sede_service

                from httpx import AsyncClient, ASGITransport
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        f"/api/v1/sedes/{sample_sede.id}/zonas",
                        json=sample_zona_data,
                        headers=auth_headers,
                    )
                    assert response.status_code == 201
                    data = response.json()
                    assert data["nombre"] == sample_zona_data["nombre"]


# ============== ESPACIO ENDPOINTS TESTS ==============

class TestEspaciosEndpoints:
    """Tests for espacio CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_espacios_empty(self, auth_headers: dict, sample_sede: Sede, sample_zona: Zona):
        """Test listing espacios when none exist."""
        from app.main import app

        with patch("app.api.v1.router.get_espacio_service") as mock_espacio_get:
            with patch("app.api.v1.router.get_zona_service") as mock_zona_get:
                mock_espacio_service = MagicMock()
                mock_espacio_service.list_espacios = AsyncMock(return_value=[])
                mock_espacio_get.return_value = mock_espacio_service

                mock_zona_service = MagicMock()
                mock_zona_service.get_zona = AsyncMock(return_value=sample_zona)
                mock_zona_get.return_value = mock_zona_service

                from httpx import AsyncClient, ASGITransport
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get(
                        f"/api/v1/sedes/{sample_sede.id}/zonas/{sample_zona.id}/espacios",
                        headers=auth_headers,
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert data["items"] == []
                    assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_espacio_success(self, auth_headers: dict, sample_sede: Sede, sample_zona: Zona, sample_espacio_data: dict):
        """Test successful espacio creation."""
        from app.main import app
        from app.db.models import Espacio

        espacio = Espacio(
            id="new-espacio-id",
            zona_id=sample_zona.id,
            sede_id=sample_sede.id,
            tenant_id=auth_headers["x_tenant_id"],
            numero=sample_espacio_data["numero"],
            piso=sample_espacio_data["piso"],
            tipo=sample_espacio_data["tipo"],
            estado=sample_espacio_data["estado"],
            descripcion=sample_espacio_data.get("descripcion"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with patch("app.api.v1.router.get_espacio_service") as mock_espacio_get:
            with patch("app.api.v1.router.get_zona_service") as mock_zona_get:
                mock_espacio_service = MagicMock()
                mock_espacio_service.create_espacio = AsyncMock(return_value=espacio)
                mock_espacio_get.return_value = mock_espacio_service

                mock_zona_service = MagicMock()
                mock_zona_service.get_zona = AsyncMock(return_value=sample_zona)
                mock_zona_get.return_value = mock_zona_service

                from httpx import AsyncClient, ASGITransport
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        f"/api/v1/sedes/{sample_sede.id}/zonas/{sample_zona.id}/espacios",
                        json=sample_espacio_data,
                        headers=auth_headers,
                    )
                    assert response.status_code == 201
                    data = response.json()
                    assert data["numero"] == sample_espacio_data["numero"]


# ============== DISPONIBILIDAD ENDPOINTS TESTS ==============

class TestDisponibilidadEndpoints:
    """Tests for disponibilidad endpoints."""

    @pytest.mark.asyncio
    async def test_get_disponibilidad_success(self, auth_headers: dict, sample_sede: Sede):
        """Test successful disponibilidad retrieval."""
        from app.main import app

        disponibilidad_data = {
            "sede_id": sample_sede.id,
            "nombre": sample_sede.nombre,
            "total_espacios": 100,
            "espacios_disponibles": 75,
            "espacios_ocupados": 25,
            "ocupacion_pct": 25.0,
            "zonas": [],
        }

        with patch("app.api.v1.router.get_disponibilidad_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_disponibilidad = AsyncMock(return_value=disponibilidad_data)
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    f"/api/v1/sedes/{sample_sede.id}/disponibilidad",
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert data["sede_id"] == sample_sede.id
                assert data["total_espacios"] == 100
                assert data["espacios_disponibles"] == 75

    @pytest.mark.asyncio
    async def test_get_disponibilidad_sede_not_found(self, auth_headers: dict):
        """Test disponibilidad for non-existent sede returns 404."""
        from app.main import app

        with patch("app.api.v1.router.get_disponibilidad_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_disponibilidad = AsyncMock(
                side_effect=SedeNotFoundError("non-existent")
            )
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/sedes/non-existent/disponibilidad",
                    headers=auth_headers,
                )
                assert response.status_code == 404


class TestOcupacionHistorialEndpoint:
    """Tests for ocupacion historial endpoint."""

    @pytest.mark.asyncio
    async def test_get_ocupacion_historial_success(self, auth_headers: dict, sample_sede: Sede):
        """Test successful ocupacion historial retrieval."""
        from app.main import app

        historial_data = [
            {
                "fecha": datetime.now(timezone.utc).isoformat(),
                "hora": 10,
                "espacios_totales": 100,
                "espacios_ocupados": 75,
                "ocupacion_pct": 75.0,
            }
        ]

        with patch("app.api.v1.router.get_disponibilidad_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_ocupacion_historial = AsyncMock(return_value=historial_data)
            mock_get_service.return_value = mock_service

            from httpx import AsyncClient, ASGITransport
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                fecha_inicio = "2024-01-01T00:00:00Z"
                fecha_fin = "2024-01-31T23:59:59Z"
                response = await client.get(
                    f"/api/v1/sedes/{sample_sede.id}/ocupacion?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}",
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert data["sede_id"] == sample_sede.id
                assert len(data["datos"]) == 1