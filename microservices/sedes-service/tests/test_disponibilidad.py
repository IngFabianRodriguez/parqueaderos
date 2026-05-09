"""Tests for disponibilidad service and endpoints.

Covers real-time disponibilidad and historical ocupacion tracking.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.services.sede_service import DisponibilidadService, SedeNotFoundError
from app.db.models import Sede, Zona, Espacio


# ============== DISPONIBILIDAD SERVICE TESTS ==============

class TestDisponibilidadService:
    """Tests for DisponibilidadService class."""

    @pytest.mark.asyncio
    async def test_get_disponibilidad_calculates_percentages(
        self,
        mock_db_session: AsyncMock,
        sample_sede: Sede,
        sample_zona: Zona,
        sample_tenant_id: str,
    ):
        """Test that disponibilidad correctly calculates occupation percentage."""
        service = DisponibilidadService(mock_db_session)

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock zonas lookup
        mock_zonas_scalars = MagicMock()
        mock_zonas_scalars.all.return_value = [sample_zona]
        mock_zonas_result = MagicMock()
        mock_zonas_result.scalars.return_value = mock_zonas_scalars

        # Mock espacios lookup with mixed status
        espacio_disponible = Espacio(
            id="espacio-1",
            zona_id=sample_zona.id,
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            numero="A-001",
            piso="P1",
            tipo="cubierta",
            estado="disponible",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        espacio_ocupado = Espacio(
            id="espacio-2",
            zona_id=sample_zona.id,
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            numero="A-002",
            piso="P1",
            tipo="cubierta",
            estado="ocupado",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        espacio_mantenimiento = Espacio(
            id="espacio-3",
            zona_id=sample_zona.id,
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            numero="A-003",
            piso="P1",
            tipo="cubierta",
            estado="mantenimiento",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        mock_espacios_scalars = MagicMock()
        mock_espacios_scalars.all.return_value = [
            espacio_disponible,
            espacio_ocupado,
            espacio_mantenimiento,
        ]
        mock_espacios_result = MagicMock()
        mock_espacios_result.scalars.return_value = mock_espacios_scalars

        mock_db_session.execute.side_effect = [
            mock_sede_result,
            mock_zonas_result,
            mock_espacios_result,
        ]

        result = await service.get_disponibilidad(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            incluye_zonas=True,
            tipo_espacio=None,
        )

        # With 1 disponible, 1 ocupado, 1 mantenimiento (not counted as disponible or ocupado)
        assert result["total_espacios"] == 3
        assert result["espacios_disponibles"] == 1
        assert result["espacios_ocupados"] == 1
        # Only disponible and ocupado count for percentage
        assert result["ocupacion_pct"] == 50.0

    @pytest.mark.asyncio
    async def test_get_disponibilidad_with_tipo_filter(
        self,
        mock_db_session: AsyncMock,
        sample_sede: Sede,
        sample_zona: Zona,
        sample_tenant_id: str,
    ):
        """Test disponibilidad filtering by tipo_espacio."""
        service = DisponibilidadService(mock_db_session)

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock zonas lookup
        mock_zonas_scalars = MagicMock()
        mock_zonas_scalars.all.return_value = [sample_zona]
        mock_zonas_result = MagicMock()
        mock_zonas_result.scalars.return_value = mock_zonas_scalars

        # Mock espacios lookup - empty filtered result
        mock_espacios_scalars = MagicMock()
        mock_espacios_scalars.all.return_value = []
        mock_espacios_result = MagicMock()
        mock_espacios_result.scalars.return_value = mock_espacios_scalars

        mock_db_session.execute.side_effect = [
            mock_sede_result,
            mock_zonas_result,
            mock_espacios_result,
        ]

        result = await service.get_disponibilidad(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            incluye_zonas=True,
            tipo_espacio="vip",
        )

        assert result["total_espacios"] == 0
        assert result["espacios_disponibles"] == 0
        assert result["espacios_ocupados"] == 0

    @pytest.mark.asyncio
    async def test_get_disponibilidad_no_zonas(
        self,
        mock_db_session: AsyncMock,
        sample_sede: Sede,
        sample_tenant_id: str,
    ):
        """Test disponibilidad when sede has no zonas."""
        service = DisponibilidadService(mock_db_session)

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock empty zonas lookup
        mock_zonas_scalars = MagicMock()
        mock_zonas_scalars.all.return_value = []
        mock_zonas_result = MagicMock()
        mock_zonas_result.scalars.return_value = mock_zonas_scalars

        mock_db_session.execute.side_effect = [mock_sede_result, mock_zonas_result]

        result = await service.get_disponibilidad(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            incluye_zonas=True,
            tipo_espacio=None,
        )

        assert result["total_espacios"] == 0
        assert result["espacios_disponibles"] == 0
        assert result["espacios_ocupados"] == 0
        assert result["zonas"] == []

    @pytest.mark.asyncio
    async def test_get_disponibilidad_multiple_zonas(
        self,
        mock_db_session: AsyncMock,
        sample_sede: Sede,
        sample_tenant_id: str,
    ):
        """Test disponibilidad with multiple zonas."""
        service = DisponibilidadService(mock_db_session)

        zona1 = Zona(
            id="zona-1",
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            nombre="Zona 1",
            tipo="cubierta",
            capacidad=10,
            espacios_disponibles=8,
            piso="P1",
            estado=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        zona2 = Zona(
            id="zona-2",
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            nombre="Zona 2",
            tipo="descubierta",
            capacidad=20,
            espacios_disponibles=15,
            piso="P2",
            estado=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock zonas lookup - two zonas
        mock_zonas_scalars = MagicMock()
        mock_zonas_scalars.all.return_value = [zona1, zona2]
        mock_zonas_result = MagicMock()
        mock_zonas_result.scalars.return_value = mock_zonas_scalars

        # Mock espacios lookup - empty for each zona
        mock_espacios_scalars = MagicMock()
        mock_espacios_scalars.all.return_value = []
        mock_espacios_result = MagicMock()
        mock_espacios_result.scalars.return_value = mock_espacios_scalars

        mock_db_session.execute.side_effect = [
            mock_sede_result,
            mock_zonas_result,
            mock_espacios_result,
            mock_espacios_result,
        ]

        result = await service.get_disponibilidad(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            incluye_zonas=True,
            tipo_espacio=None,
        )

        assert result["total_espacios"] == 0
        assert len(result["zonas"]) == 2


class TestOcupacionHistorial:
    """Tests for ocupacion historial functionality."""

    @pytest.mark.asyncio
    async def test_get_ocupacion_historial_returns_formatted_data(
        self,
        mock_db_session: AsyncMock,
        sample_sede: Sede,
        sample_tenant_id: str,
    ):
        """Test that ocupacion historial returns properly formatted data."""
        from app.db.models import OcupacionHistorial

        service = DisponibilidadService(mock_db_session)

        fecha_inicio = datetime.now(timezone.utc)
        fecha_fin = datetime.now(timezone.utc)

        # Create sample historial records
        record1 = OcupacionHistorial(
            id="record-1",
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            fecha=fecha_inicio,
            hora=9,
            espacios_totales=100,
            espacios_ocupados=50,
            ocupacion_pct=50.0,
            created_at=datetime.now(timezone.utc),
        )
        record2 = OcupacionHistorial(
            id="record-2",
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            fecha=fecha_inicio,
            hora=10,
            espacios_totales=100,
            espacios_ocupados=75,
            ocupacion_pct=75.0,
            created_at=datetime.now(timezone.utc),
        )

        # Mock sede lookup
        mock_sede_result = MagicMock()
        mock_sede_result.scalar_one_or_none.return_value = sample_sede

        # Mock historial lookup
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [record1, record2]
        mock_historial_result = MagicMock()
        mock_historial_result.scalars.return_value = mock_scalars

        mock_db_session.execute.side_effect = [mock_sede_result, mock_historial_result]

        result = await service.get_ocupacion_historial(
            sede_id=sample_sede.id,
            tenant_id=sample_tenant_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        assert len(result) == 2
        assert result[0]["hora"] == 9
        assert result[0]["espacios_totales"] == 100
        assert result[0]["ocupacion_pct"] == 50.0
        assert result[1]["hora"] == 10
        assert result[1]["ocupacion_pct"] == 75.0

    @pytest.mark.asyncio
    async def test_record_ocupacion_calculates_percentage(
        self,
        mock_db_session: AsyncMock,
        sample_sede_id: str,
        sample_tenant_id: str,
    ):
        """Test that record_ocupacion correctly calculates percentage."""
        service = DisponibilidadService(mock_db_session)

        # Mock no existing record
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        async def mock_refresh(obj):
            pass
        mock_db_session.refresh = mock_refresh

        fecha = datetime.now(timezone.utc)
        result = await service.record_ocupacion(
            sede_id=sample_sede_id,
            tenant_id=sample_tenant_id,
            fecha=fecha,
            hora=12,
            espacios_totales=50,
            espacios_ocupados=25,
        )

        # 25/50 = 50%
        mock_db_session.add.assert_called_once()
        call_args = mock_db_session.add.call_args[0][0]
        assert call_args.espacios_totales == 50
        assert call_args.espacios_ocupados == 25
        assert call_args.ocupacion_pct == 50.0

    @pytest.mark.asyncio
    async def test_record_ocupacion_zero_total_handled(
        self,
        mock_db_session: AsyncMock,
        sample_sede_id: str,
        sample_tenant_id: str,
    ):
        """Test that record_ocupacion handles zero total spaces."""
        service = DisponibilidadService(mock_db_session)

        # Mock no existing record
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        async def mock_refresh(obj):
            pass
        mock_db_session.refresh = mock_refresh

        fecha = datetime.now(timezone.utc)
        result = await service.record_ocupacion(
            sede_id=sample_sede_id,
            tenant_id=sample_tenant_id,
            fecha=fecha,
            hora=12,
            espacios_totales=0,
            espacios_ocupados=0,
        )

        # 0/0 = 0% (avoid division by zero)
        call_args = mock_db_session.add.call_args[0][0]
        assert call_args.ocupacion_pct == 0.0


# ============== DISPONIBILIDAD SCHEMA TESTS ==============

class TestDisponibilidadSchemas:
    """Tests for disponibilidad Pydantic schemas."""

    def test_disponibilidad_zona_schema(self):
        """Test DisponibilidadZona schema validation."""
        from app.schemas.sede import DisponibilidadZona

        zona = DisponibilidadZona(
            zona_id="zona-123",
            nombre="Zona A",
            tipo="cubierta",
            total=50,
            disponibles=40,
            ocupados=10,
            ocupacion_pct=20.0,
        )

        assert zona.zona_id == "zona-123"
        assert zona.nombre == "Zona A"
        assert zona.tipo == "cubierta"
        assert zona.total == 50
        assert zona.disponibles == 40
        assert zona.ocupados == 10
        assert zona.ocupacion_pct == 20.0

    def test_disponibilidad_response_schema(self):
        """Test DisponibilidadResponse schema validation."""
        from app.schemas.sede import DisponibilidadResponse, DisponibilidadZona

        response = DisponibilidadResponse(
            sede_id="sede-123",
            nombre="Sede Centro",
            total_espacios=100,
            espacios_disponibles=75,
            espacios_ocupados=25,
            ocupacion_pct=25.0,
            zonas=[
                DisponibilidadZona(
                    zona_id="zona-1",
                    nombre="Zona A",
                    tipo="cubierta",
                    total=50,
                    disponibles=40,
                    ocupados=10,
                    ocupacion_pct=20.0,
                ),
            ],
        )

        assert response.sede_id == "sede-123"
        assert response.total_espacios == 100
        assert len(response.zonas) == 1

    def test_ocupacion_historial_item_schema(self):
        """Test OcupacionHistorialItem schema validation."""
        from app.schemas.sede import OcupacionHistorialItem

        item = OcupacionHistorialItem(
            fecha=datetime.now(timezone.utc),
            hora=10,
            espacios_totales=100,
            espacios_ocupados=75,
            ocupacion_pct=75.0,
        )

        assert item.hora == 10
        assert item.espacios_totales == 100
        assert item.espacios_ocupados == 75
        assert item.ocupacion_pct == 75.0

    def test_ocupacion_historial_response_schema(self):
        """Test OcupacionHistorialResponse schema validation."""
        from app.schemas.sede import OcupacionHistorialResponse, OcupacionHistorialItem

        now = datetime.now(timezone.utc)
        response = OcupacionHistorialResponse(
            sede_id="sede-123",
            fecha_inicio=now,
            fecha_fin=now,
            datos=[
                OcupacionHistorialItem(
                    fecha=now,
                    hora=9,
                    espacios_totales=100,
                    espacios_ocupados=50,
                    ocupacion_pct=50.0,
                ),
                OcupacionHistorialItem(
                    fecha=now,
                    hora=10,
                    espacios_totales=100,
                    espacios_ocupados=75,
                    ocupacion_pct=75.0,
                ),
            ],
        )

        assert response.sede_id == "sede-123"
        assert len(response.datos) == 2