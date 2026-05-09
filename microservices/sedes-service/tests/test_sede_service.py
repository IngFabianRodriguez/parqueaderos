"""Tests for sede service business logic.

Covers SedeService, ZonaService, EspacioService, and DisponibilidadService.
Target: 90%+ coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.sede_service import (
    SedeService,
    ZonaService,
    EspacioService,
    DisponibilidadService,
    SedeNotFoundError,
    ZonaNotFoundError,
    EspacioNotFoundError,
    DuplicateSlugError,
)
from app.db.models import Sede, Zona, Espacio, OcupacionHistorial


# ============== SEDE SERVICE TESTS ==============

class TestSedeServiceCreate:
    """Tests for SedeService.create_sede method."""

    @pytest.mark.asyncio
    async def test_create_sede_success(self, mock_db_session: AsyncMock, sample_tenant_id: str, sample_sede_data: dict):
        """Test successful sede creation."""
        service = SedeService(mock_db_session)

        # Mock no existing sede
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Mock refresh to set attributes
        async def mock_refresh(obj):
            obj.id = "new-sede-id"
        mock_db_session.refresh = mock_refresh

        result = await service.create_sede(tenant_id=sample_tenant_id, data=sample_sede_data)

        assert result.nombre == sample_sede_data["nombre"]
        assert result.slug == sample_sede_data["slug"]
        assert result.tenant_id == sample_tenant_id
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_sede_duplicate_slug_raises_error(self, mock_db_session: AsyncMock, sample_tenant_id: str, sample_sede_data: dict, sample_sede: Sede):
        """Test that duplicate slug raises DuplicateSlugError."""
        service = SedeService(mock_db_session)

        # Mock existing sede with same slug
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_sede
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(DuplicateSlugError) as exc_info:
            await service.create_sede(tenant_id=sample_tenant_id, data=sample_sede_data)

        assert exc_info.value.slug == sample_sede_data["slug"]
        assert exc_info.value.tenant_id == sample_tenant_id


class TestSedeServiceGet:
    """Tests for SedeService.get_sede method."""

    @pytest.mark.asyncio
    async def test_get_sede_success(self, mock_db_session: AsyncMock, sample_sede: Sede, sample_tenant_id: str):
        """Test successful sede retrieval."""
        service = SedeService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_sede
        mock_db_session.execute.return_value = mock_result

        result = await service.get_sede(sample_sede.id, tenant_id=sample_tenant_id)

        assert result.id == sample_sede.id
        assert result.nombre == sample_sede.nombre

    @pytest.mark.asyncio
    async def test_get_sede_not_found_raises_error(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test that non-existent sede raises SedeNotFoundError."""
        service = SedeService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        sede_id = "non-existent-id"
        with pytest.raises(SedeNotFoundError) as exc_info:
            await service.get_sede(sede_id, tenant_id=sample_tenant_id)

        assert exc_info.value.sede_id == sede_id


class TestSedeServiceList:
    """Tests for SedeService.list_sedes method."""

    @pytest.mark.asyncio
    async def test_list_sedes_empty(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test listing sedes when none exist."""
        service = SedeService(mock_db_session)

        # Mock empty result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_result.subquery.return_value = MagicMock()

        # Mock count query
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_db_session.execute.return_value = mock_count_result

        sedes, total = await service.list_sedes(sample_tenant_id)

        assert total == 0
        assert len(sedes) == 0

    @pytest.mark.asyncio
    async def test_list_sedes_with_results(self, mock_db_session: AsyncMock, sample_tenant_id: str, sample_sede: Sede):
        """Test listing sedes with existing results."""
        service = SedeService(mock_db_session)

        # Mock count result
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        # Mock list result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_sede]
        mock_list_result = MagicMock()
        mock_list_result.scalars.return_value = mock_scalars

        mock_db_session.execute.side_effect = [mock_count_result, mock_list_result]

        sedes, total = await service.list_sedes(sample_tenant_id)

        assert total == 1
        assert len(sedes) == 1
        assert sedes[0].id == sample_sede.id

    @pytest.mark.asyncio
    async def test_list_sedes_with_filters(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test listing sedes with filters."""
        service = SedeService(mock_db_session)

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_db_session.execute.return_value = mock_count_result

        filtros = {"estado": True, "ciudad": "Bogotá"}
        sedes, total = await service.list_sedes(
            tenant_id=sample_tenant_id,
            page=1,
            page_size=20,
            filtros=filtros,
        )

        assert total == 0
        mock_db_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_list_sedes_pagination(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test listing sedes with pagination."""
        service = SedeService(mock_db_session)

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 50
        mock_db_session.execute.return_value = mock_count_result

        sedes, total = await service.list_sedes(
            tenant_id=sample_tenant_id,
            page=2,
            page_size=10,
        )

        assert total == 50


class TestSedeServiceUpdate:
    """Tests for SedeService.update_sede method."""

    @pytest.mark.asyncio
    async def test_update_sede_success(self, mock_db_session: AsyncMock, sample_sede: Sede, sample_tenant_id: str):
        """Test successful sede update."""
        service = SedeService(mock_db_session)

        # Mock get_sede
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_sede
        mock_db_session.execute.return_value = mock_result

        update_data = {"nombre": "Sede Actualizada"}
        result = await service.update_sede(sample_sede.id, tenant_id=sample_tenant_id, data=update_data)

        assert result.nombre == sample_sede.nombre  # Before refresh update
        mock_db_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_update_sede_not_found(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test update non-existent sede raises error."""
        service = SedeService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(SedeNotFoundError):
            await service.update_sede("non-existent", tenant_id=sample_tenant_id, data={"nombre": "Test"})

    @pytest.mark.asyncio
    async def test_update_sede_multiple_fields(self, mock_db_session: AsyncMock, sample_sede: Sede, sample_tenant_id: str):
        """Test updating multiple fields."""
        service = SedeService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_sede
        mock_db_session.execute.return_value = mock_result

        update_data = {
            "nombre": "Nuevo Nombre",
            "direccion": "Nueva Direccion",
            "ciudad": "Medellín",
        }
        await service.update_sede(sample_sede.id, tenant_id=sample_tenant_id, data=update_data)

        mock_db_session.execute.assert_called()


class TestSedeServiceDelete:
    """Tests for SedeService.delete_sede method."""

    @pytest.mark.asyncio
    async def test_delete_sede_success(self, mock_db_session: AsyncMock, sample_sede: Sede, sample_tenant_id: str):
        """Test successful sede deletion."""
        service = SedeService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_sede
        mock_db_session.execute.return_value = mock_result

        result = await service.delete_sede(sample_sede.id, tenant_id=sample_tenant_id)

        assert result is True
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_sede_not_found(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test delete non-existent sede raises error."""
        service = SedeService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(SedeNotFoundError):
            await service.delete_sede("non-existent", tenant_id=sample_tenant_id)


# ============== ZONA SERVICE TESTS ==============

class TestZonaServiceCreate:
    """Tests for ZonaService.create_zona method."""

    @pytest.mark.asyncio
    async def test_create_zona_success(self, mock_db_session: AsyncMock, sample_zona_data: dict, sample_sede_id: str, sample_tenant_id: str):
        """Test successful zona creation."""
        service = ZonaService(mock_db_session)

        async def mock_refresh(obj):
            obj.id = "new-zona-id"
        mock_db_session.refresh = mock_refresh

        result = await service.create_zona(sede_id=sample_sede_id, tenant_id=sample_tenant_id, data=sample_zona_data)

        assert result.nombre == sample_zona_data["nombre"]
        assert result.sede_id == sample_sede_id
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


class TestZonaServiceGet:
    """Tests for ZonaService.get_zona method."""

    @pytest.mark.asyncio
    async def test_get_zona_success(self, mock_db_session: AsyncMock, sample_zona: Zona, sample_tenant_id: str):
        """Test successful zona retrieval."""
        service = ZonaService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_zona
        mock_db_session.execute.return_value = mock_result

        result = await service.get_zona(sample_zona.id, tenant_id=sample_tenant_id)

        assert result.id == sample_zona.id

    @pytest.mark.asyncio
    async def test_get_zona_not_found(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test that non-existent zona raises ZonaNotFoundError."""
        service = ZonaService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(ZonaNotFoundError):
            await service.get_zona("non-existent", tenant_id=sample_tenant_id)


class TestZonaServiceList:
    """Tests for ZonaService.list_zonas method."""

    @pytest.mark.asyncio
    async def test_list_zonas_empty(self, mock_db_session: AsyncMock, sample_sede_id: str, sample_tenant_id: str):
        """Test listing zonas when none exist."""
        service = ZonaService(mock_db_session)

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        zonas = await service.list_zonas(sede_id=sample_sede_id, tenant_id=sample_tenant_id)

        assert len(zonas) == 0

    @pytest.mark.asyncio
    async def test_list_zonas_with_results(self, mock_db_session: AsyncMock, sample_sede_id: str, sample_tenant_id: str, sample_zona: Zona):
        """Test listing zonas with existing results."""
        service = ZonaService(mock_db_session)

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_zona]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        zonas = await service.list_zonas(sede_id=sample_sede_id, tenant_id=sample_tenant_id)

        assert len(zonas) == 1
        assert zonas[0].id == sample_zona.id


class TestZonaServiceUpdate:
    """Tests for ZonaService.update_zona method."""

    @pytest.mark.asyncio
    async def test_update_zona_success(self, mock_db_session: AsyncMock, sample_zona: Zona, sample_tenant_id: str):
        """Test successful zona update."""
        service = ZonaService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_zona
        mock_db_session.execute.return_value = mock_result

        update_data = {"nombre": "Zona Actualizada", "capacidad": 100}
        result = await service.update_zona(sample_zona.id, tenant_id=sample_tenant_id, data=update_data)

        assert result.nombre == sample_zona.nombre
        mock_db_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_update_zona_not_found(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test update non-existent zona raises error."""
        service = ZonaService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(ZonaNotFoundError):
            await service.update_zona("non-existent", tenant_id=sample_tenant_id, data={"nombre": "Test"})


class TestZonaServiceDelete:
    """Tests for ZonaService.delete_zona method."""

    @pytest.mark.asyncio
    async def test_delete_zona_success(self, mock_db_session: AsyncMock, sample_zona: Zona, sample_tenant_id: str):
        """Test successful zona deletion."""
        service = ZonaService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_zona
        mock_db_session.execute.return_value = mock_result

        result = await service.delete_zona(sample_zona.id, tenant_id=sample_tenant_id)

        assert result is True
        mock_db_session.commit.assert_called_once()


# ============== ESPACIO SERVICE TESTS ==============

class TestEspacioServiceCreate:
    """Tests for EspacioService.create_espacio method."""

    @pytest.mark.asyncio
    async def test_create_espacio_success(self, mock_db_session: AsyncMock, sample_espacio_data: dict, sample_zona_id: str, sample_sede_id: str, sample_tenant_id: str):
        """Test successful espacio creation."""
        service = EspacioService(mock_db_session)

        async def mock_refresh(obj):
            obj.id = "new-espacio-id"
        mock_db_session.refresh = mock_refresh

        result = await service.create_espacio(
            zona_id=sample_zona_id,
            sede_id=sample_sede_id,
            tenant_id=sample_tenant_id,
            data=sample_espacio_data,
        )

        assert result.numero == sample_espacio_data["numero"]
        assert result.zona_id == sample_zona_id
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


class TestEspacioServiceGet:
    """Tests for EspacioService.get_espacio method."""

    @pytest.mark.asyncio
    async def test_get_espacio_success(self, mock_db_session: AsyncMock, sample_espacio: Espacio, sample_tenant_id: str):
        """Test successful espacio retrieval."""
        service = EspacioService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_espacio
        mock_db_session.execute.return_value = mock_result

        result = await service.get_espacio(sample_espacio.id, tenant_id=sample_tenant_id)

        assert result.id == sample_espacio.id

    @pytest.mark.asyncio
    async def test_get_espacio_not_found(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test that non-existent espacio raises EspacioNotFoundError."""
        service = EspacioService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(EspacioNotFoundError):
            await service.get_espacio("non-existent", tenant_id=sample_tenant_id)


class TestEspacioServiceList:
    """Tests for EspacioService.list_espacios method."""

    @pytest.mark.asyncio
    async def test_list_espacios_empty(self, mock_db_session: AsyncMock, sample_zona_id: str, sample_tenant_id: str):
        """Test listing espacios when none exist."""
        service = EspacioService(mock_db_session)

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        espacios = await service.list_espacios(zona_id=sample_zona_id, tenant_id=sample_tenant_id)

        assert len(espacios) == 0

    @pytest.mark.asyncio
    async def test_list_espacios_with_results(self, mock_db_session: AsyncMock, sample_zona_id: str, sample_tenant_id: str, sample_espacio: Espacio):
        """Test listing espacios with existing results."""
        service = EspacioService(mock_db_session)

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_espacio]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        espacios = await service.list_espacios(zona_id=sample_zona_id, tenant_id=sample_tenant_id)

        assert len(espacios) == 1
        assert espacios[0].id == sample_espacio.id

    @pytest.mark.asyncio
    async def test_list_espacios_filter_by_tipo(self, mock_db_session: AsyncMock, sample_zona_id: str, sample_tenant_id: str, sample_espacio: Espacio):
        """Test listing espacios filtered by tipo."""
        service = EspacioService(mock_db_session)

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_espacio]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        espacios = await service.list_espacios(zona_id=sample_zona_id, tenant_id=sample_tenant_id, tipo="cubierta")

        assert len(espacios) == 1


class TestEspacioServiceUpdate:
    """Tests for EspacioService.update_espacio method."""

    @pytest.mark.asyncio
    async def test_update_espacio_success(self, mock_db_session: AsyncMock, sample_espacio: Espacio, sample_tenant_id: str):
        """Test successful espacio update."""
        service = EspacioService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_espacio
        mock_db_session.execute.return_value = mock_result

        update_data = {"estado": "ocupado"}
        result = await service.update_espacio(sample_espacio.id, tenant_id=sample_tenant_id, data=update_data)

        assert result.estado == sample_espacio.estado
        mock_db_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_update_espacio_not_found(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test update non-existent espacio raises error."""
        service = EspacioService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(EspacioNotFoundError):
            await service.update_espacio("non-existent", tenant_id=sample_tenant_id, data={"estado": "ocupado"})


class TestEspacioServiceDelete:
    """Tests for EspacioService.delete_espacio method."""

    @pytest.mark.asyncio
    async def test_delete_espacio_success(self, mock_db_session: AsyncMock, sample_espacio: Espacio, sample_tenant_id: str):
        """Test successful espacio deletion."""
        service = EspacioService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_espacio
        mock_db_session.execute.return_value = mock_result

        result = await service.delete_espacio(sample_espacio.id, tenant_id=sample_tenant_id)

        assert result is True
        mock_db_session.commit.assert_called_once()


# ============== DISPONIBILIDAD SERVICE TESTS ==============

class TestDisponibilidadServiceGetDisponibilidad:
    """Tests for DisponibilidadService.get_disponibilidad method."""

    @pytest.mark.asyncio
    async def test_get_disponibilidad_success(self, mock_db_session: AsyncMock, sample_sede: Sede, sample_zona: Zona, sample_tenant_id: str):
        """Test successful disponibilidad retrieval."""
        service = DisponibilidadService(mock_db_session)

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock zonas lookup
        mock_zonas_scalars = MagicMock()
        mock_zonas_scalars.all.return_value = [sample_zona]
        mock_zonas_result = MagicMock()
        mock_zonas_result.scalars.return_value = mock_zonas_scalars

        # Mock espacios lookup
        mock_espacios_scalars = MagicMock()
        mock_espacios_scalars.all.return_value = []
        mock_espacios_result = MagicMock()
        mock_espacios_result.scalars.return_value = mock_espacios_scalars

        mock_db_session.execute.side_effect = [mock_sede_result, mock_zonas_result, mock_espacios_result]

        result = await service.get_disponibilidad(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            incluye_zonas=True,
            tipo_espacio=None,
        )

        assert result["sede_id"] == sample_sede.id
        assert result["nombre"] == sample_sede.nombre
        assert "zonas" in result

    @pytest.mark.asyncio
    async def test_get_disponibilidad_sede_not_found(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test that non-existent sede raises SedeNotFoundError."""
        service = DisponibilidadService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(SedeNotFoundError):
            await service.get_disponibilidad(
                sede_id="non-existent",
                tenant_id=sample_tenant_id,
                incluye_zonas=True,
                tipo_espacio=None,
            )

    @pytest.mark.asyncio
    async def test_get_disponibilidad_with_espacios_count(self, mock_db_session: AsyncMock, sample_sede: Sede, sample_zona: Zona, sample_espacio: Espacio, sample_espacio_ocupado: Espacio, sample_tenant_id: str):
        """Test disponibilidad calculation with spaces."""
        service = DisponibilidadService(mock_db_session)

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock zonas lookup
        mock_zonas_scalars = MagicMock()
        mock_zonas_scalars.all.return_value = [sample_zona]
        mock_zonas_result = MagicMock()
        mock_zonas_result.scalars.return_value = mock_zonas_scalars

        # Mock espacios lookup - 1 disponible, 1 ocupado
        mock_espacios_scalars = MagicMock()
        mock_espacios_scalars.all.return_value = [sample_espacio, sample_espacio_ocupado]
        mock_espacios_result = MagicMock()
        mock_espacios_result.scalars.return_value = mock_espacios_scalars

        mock_db_session.execute.side_effect = [mock_sede_result, mock_zonas_result, mock_espacios_result]

        result = await service.get_disponibilidad(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            incluye_zonas=True,
            tipo_espacio=None,
        )

        assert result["total_espacios"] == 2
        assert result["espacios_disponibles"] == 1
        assert result["espacios_ocupados"] == 1


class TestDisponibilidadServiceGetOcupacionHistorial:
    """Tests for DisponibilidadService.get_ocupacion_historial method."""

    @pytest.mark.asyncio
    async def test_get_ocupacion_historial_success(self, mock_db_session: AsyncMock, sample_sede: Sede, sample_ocupacion_historial: OcupacionHistorial, sample_tenant_id: str):
        """Test successful ocupacion historial retrieval."""
        service = DisponibilidadService(mock_db_session)

        fecha_inicio = datetime.now(timezone.utc)
        fecha_fin = datetime.now(timezone.utc)

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock ocupacion lookup
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_ocupacion_historial]
        mock_historial_result = MagicMock()
        mock_historial_result.scalars.return_value = mock_scalars

        mock_db_session.execute.side_effect = [mock_sede_result, mock_historial_result]

        result = await service.get_ocupacion_historial(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        assert len(result) == 1
        assert result[0]["hora"] == sample_ocupacion_historial.hora

    @pytest.mark.asyncio
    async def test_get_ocupacion_historial_empty(self, mock_db_session: AsyncMock, sample_sede: Sede, sample_tenant_id: str):
        """Test ocupacion historial when no records exist."""
        service = DisponibilidadService(mock_db_session)

        fecha_inicio = datetime.now(timezone.utc)
        fecha_fin = datetime.now(timezone.utc)

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock empty ocupacion lookup
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_historial_result = MagicMock()
        mock_historial_result.scalars.return_value = mock_scalars

        mock_db_session.execute.side_effect = [mock_sede_result, mock_historial_result]

        result = await service.get_ocupacion_historial(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_ocupacion_historial_sede_not_found(self, mock_db_session: AsyncMock, sample_tenant_id: str):
        """Test that non-existent sede raises SedeNotFoundError."""
        service = DisponibilidadService(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(SedeNotFoundError):
            await service.get_ocupacion_historial(
                sede_id="non-existent",
                tenant_id=sample_tenant_id,
                fecha_inicio=datetime.now(timezone.utc),
                fecha_fin=datetime.now(timezone.utc),
            )


class TestDisponibilidadServiceRecordOcupacion:
    """Tests for DisponibilidadService.record_ocupacion method."""

    @pytest.mark.asyncio
    async def test_record_ocupacion_new_record(self, mock_db_session: AsyncMock, sample_sede_id: str, sample_tenant_id: str):
        """Test recording ocupacion for new record."""
        service = DisponibilidadService(mock_db_session)

        # Mock no existing record
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        async def mock_refresh(obj):
            obj.id = "new-record-id"
        mock_db_session.refresh = mock_refresh

        fecha = datetime.now(timezone.utc)
        result = await service.record_ocupacion(
            sede_id=sample_sede_id,
            tenant_id=sample_tenant_id,
            fecha=fecha,
            hora=10,
            espacios_totales=100,
            espacios_ocupados=75,
        )

        mock_db_session.add.assert_called_once()
        assert result.espacios_totales == 100
        assert result.espacios_ocupados == 75

    @pytest.mark.asyncio
    async def test_record_ocupacion_update_existing(self, mock_db_session: AsyncMock, sample_sede_id: str, sample_tenant_id: str, sample_ocupacion_historial: OcupacionHistorial):
        """Test updating existing ocupacion record."""
        service = DisponibilidadService(mock_db_session)

        # Mock existing record
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_ocupacion_historial
        mock_db_session.execute.return_value = mock_result

        fecha = datetime.now(timezone.utc)
        result = await service.record_ocupacion(
            sede_id=sample_sede_id,
            tenant_id=sample_tenant_id,
            fecha=fecha,
            hora=10,
            espacios_totales=100,
            espacios_ocupados=80,
        )

        assert result == sample_ocupacion_historial


# ============== ERROR CLASS TESTS ==============

class TestErrorClasses:
    """Tests for error classes."""

    def test_sede_not_found_error(self):
        """Test SedeNotFoundError attributes."""
        error = SedeNotFoundError("sede-123")
        assert error.sede_id == "sede-123"
        assert "Sede not found: sede-123" in str(error)

    def test_zona_not_found_error(self):
        """Test ZonaNotFoundError attributes."""
        error = ZonaNotFoundError("zona-123")
        assert error.zona_id == "zona-123"
        assert "Zona not found: zona-123" in str(error)

    def test_espacio_not_found_error(self):
        """Test EspacioNotFoundError attributes."""
        error = EspacioNotFoundError("espacio-123")
        assert error.espacio_id == "espacio-123"
        assert "Espacio not found: espacio-123" in str(error)

    def test_duplicate_slug_error(self):
        """Test DuplicateSlugError attributes."""
        error = DuplicateSlugError("test-slug", "tenant-123")
        assert error.slug == "test-slug"
        assert error.tenant_id == "tenant-123"
        assert "Slug 'test-slug' already exists" in str(error)