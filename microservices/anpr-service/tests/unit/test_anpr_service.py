"""Unit tests for ANPR service business logic — RF-005 to RF-009.

All tests mock external dependencies (DB, HTTP) so they run without
any real PostgreSQL, Redis or network access.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.anpr_service import (
    ANPRCameraService,
    PlateDetectionService,
    OCRService,
)
from app.repositories.anpr import ANPRCameraRepository, PlateDetectionRepository
from app.schemas.anpr import (
    ANPRCameraCreate,
    ANPRCameraUpdate,
    PlateDetectionCreate,
    OCRInferenceRequest,
)


# ─────────────────────────────────────────────────────────────────────────────
# ANPRCameraService tests — RF-005
# ─────────────────────────────────────────────────────────────────────────────

class TestANPRCameraService:
    """Tests for camera CRUD operations."""

    @pytest.fixture
    def camera_service(self, mock_db_session):
        return ANPRCameraService(mock_db_session)

    @pytest.mark.asyncio
    async def test_create_camera_returns_response(self, camera_service, tenant_id):
        """Creating a camera returns a camera response."""
        from app.db.models import ANPRCamera

        mock_camera = MagicMock(spec=ANPRCamera)
        mock_camera.id = uuid.uuid4()
        mock_camera.tenant_id = tenant_id
        mock_camera.name = "Entry Camera"
        mock_camera.sede_id = uuid.uuid4()
        mock_camera.stream_url = "rtsp://test:554/stream"
        mock_camera.is_active = True
        mock_camera.lane_id = "lane-1"
        mock_camera.confidence_threshold = 0.75
        mock_camera.detection_zone = None
        mock_camera.model_path = None
        mock_camera.created_at = datetime.now(timezone.utc)
        mock_camera.updated_at = datetime.now(timezone.utc)

        with patch.object(
            ANPRCameraRepository, "create", AsyncMock(return_value=mock_camera)
        ):
            camera_in = ANPRCameraCreate(
                name="Entry Camera",
                sede_id=uuid.uuid4(),
                stream_url="rtsp://test:554/stream",
                confidence_threshold=0.75,
            )
            result = await camera_service.create_camera(tenant_id, camera_in)
            assert result.name == "Entry Camera"
            assert result.confidence_threshold == 0.75

    @pytest.mark.asyncio
    async def test_get_camera_returns_none_when_not_found(self, camera_service, tenant_id):
        """Getting a non-existent camera returns None."""
        with patch.object(
            ANPRCameraRepository, "get_by_id", AsyncMock(return_value=None)
        ):
            result = await camera_service.get_camera(tenant_id, uuid.uuid4())
            assert result is None

    @pytest.mark.asyncio
    async def test_get_camera_returns_response(self, camera_service, tenant_id, sample_camera):
        """Getting an existing camera returns a response."""
        with patch.object(
            ANPRCameraRepository, "get_by_id", AsyncMock(return_value=sample_camera)
        ):
            result = await camera_service.get_camera(tenant_id, sample_camera.id)
            assert result is not None
            assert result.id == sample_camera.id

    @pytest.mark.asyncio
    async def test_list_cameras_returns_empty_list(self, camera_service, tenant_id):
        """Listing cameras returns empty list when none exist."""
        with patch.object(
            ANPRCameraRepository, "list", AsyncMock(return_value=[])
        ):
            result = await camera_service.list_cameras(tenant_id)
            assert result == []

    @pytest.mark.asyncio
    async def test_list_cameras_filters_by_sede(self, camera_service, tenant_id, sample_camera):
        """Listing cameras with sede_id filter passes it to repo."""
        sede_id = uuid.uuid4()
        with patch.object(
            ANPRCameraRepository, "list", AsyncMock(return_value=[sample_camera])
        ) as mock_list:
            result = await camera_service.list_cameras(tenant_id, sede_id=sede_id)
            mock_list.assert_called_once_with(tenant_id, sede_id, None, 100, 0)
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_cameras_filters_by_is_active(self, camera_service, tenant_id):
        """Listing cameras with is_active filter passes it to repo."""
        with patch.object(
            ANPRCameraRepository, "list", AsyncMock(return_value=[])
        ) as mock_list:
            await camera_service.list_cameras(tenant_id, is_active=True)
            mock_list.assert_called_once_with(tenant_id, None, True, 100, 0)

    @pytest.mark.asyncio
    async def test_list_cameras_pagination(self, camera_service, tenant_id):
        """Listing cameras passes limit and offset to repo."""
        with patch.object(
            ANPRCameraRepository, "list", AsyncMock(return_value=[])
        ) as mock_list:
            await camera_service.list_cameras(tenant_id, limit=50, offset=10)
            mock_list.assert_called_once_with(tenant_id, None, None, 50, 10)

    @pytest.mark.asyncio
    async def test_update_camera_returns_none_when_not_found(self, camera_service, tenant_id):
        """Updating a non-existent camera returns None."""
        update = ANPRCameraUpdate(name="New Name")
        with patch.object(
            ANPRCameraRepository, "get_by_id", AsyncMock(return_value=None)
        ):
            result = await camera_service.update_camera(tenant_id, uuid.uuid4(), update)
            assert result is None

    @pytest.mark.asyncio
    async def test_update_camera_patches_fields(self, camera_service, tenant_id, sample_camera):
        """Updating a camera patches provided fields."""
        update = ANPRCameraUpdate(name="Updated Name", is_active=False)
        sample_camera.name = "Updated Name"
        sample_camera.is_active = False
        with patch.object(
            ANPRCameraRepository, "get_by_id", AsyncMock(return_value=sample_camera)
        ), patch.object(
            ANPRCameraRepository, "update", AsyncMock(return_value=sample_camera)
        ):
            result = await camera_service.update_camera(tenant_id, sample_camera.id, update)
            assert result.name == "Updated Name"
            assert result.is_active is False

    @pytest.mark.asyncio
    async def test_delete_camera_returns_false_when_not_found(self, camera_service, tenant_id):
        """Deleting a non-existent camera returns False."""
        with patch.object(
            ANPRCameraRepository, "get_by_id", AsyncMock(return_value=None)
        ):
            result = await camera_service.delete_camera(tenant_id, uuid.uuid4())
            assert result is False

    @pytest.mark.asyncio
    async def test_delete_camera_returns_true_on_success(self, camera_service, tenant_id, sample_camera):
        """Deleting an existing camera returns True."""
        with patch.object(
            ANPRCameraRepository, "get_by_id", AsyncMock(return_value=sample_camera)
        ), patch.object(
            ANPRCameraRepository, "delete", AsyncMock()
        ):
            result = await camera_service.delete_camera(tenant_id, sample_camera.id)
            assert result is True


# ─────────────────────────────────────────────────────────────────────────────
# PlateDetectionService tests — RF-006, RF-007
# ─────────────────────────────────────────────────────────────────────────────

class TestPlateDetectionService:
    """Tests for plate detection operations."""

    @pytest.fixture
    def detection_service(self, mock_db_session):
        return PlateDetectionService(mock_db_session)

    @pytest.mark.asyncio
    async def test_create_detection_returns_response(self, detection_service, tenant_id):
        """Creating a detection returns a detection response."""
        from app.db.models import PlateDetection

        mock_detection = MagicMock(spec=PlateDetection)
        mock_detection.id = uuid.uuid4()
        mock_detection.tenant_id = tenant_id
        mock_detection.camera_id = uuid.uuid4()
        mock_detection.plate_number = "XYZ789"
        mock_detection.confidence = 0.92
        mock_detection.detection_type = "exit"
        mock_detection.image_path = None
        mock_detection.cropped_plate_path = None
        mock_detection.processing_time_ms = 38
        mock_detection.matched_reservation_id = None
        mock_detection.timestamp = datetime.now(timezone.utc)
        mock_detection.created_at = datetime.now(timezone.utc)

        with patch.object(
            PlateDetectionRepository, "create", AsyncMock(return_value=mock_detection)
        ):
            detection_in = PlateDetectionCreate(
                camera_id=uuid.uuid4(),
                plate_number="XYZ789",
                confidence=0.92,
                detection_type="exit",
            )
            result = await detection_service.create_detection(tenant_id, detection_in)
            assert result.plate_number == "XYZ789"
            assert result.detection_type == "exit"

    @pytest.mark.asyncio
    async def test_get_detection_returns_none_when_not_found(self, detection_service, tenant_id):
        """Getting a non-existent detection returns None."""
        with patch.object(
            PlateDetectionRepository, "get_by_id", AsyncMock(return_value=None)
        ):
            result = await detection_service.get_detection(tenant_id, uuid.uuid4())
            assert result is None

    @pytest.mark.asyncio
    async def test_get_detection_returns_response(self, detection_service, tenant_id, sample_detection):
        """Getting an existing detection returns a response."""
        with patch.object(
            PlateDetectionRepository, "get_by_id", AsyncMock(return_value=sample_detection)
        ):
            result = await detection_service.get_detection(tenant_id, sample_detection.id)
            assert result is not None
            assert result.id == sample_detection.id

    @pytest.mark.asyncio
    async def test_list_detections_returns_empty_list(self, detection_service, tenant_id):
        """Listing detections returns empty list when none exist."""
        with patch.object(
            PlateDetectionRepository, "list", AsyncMock(return_value=[])
        ):
            result = await detection_service.list_detections(tenant_id)
            assert result == []

    @pytest.mark.asyncio
    async def test_list_detections_filters_by_camera_id(self, detection_service, tenant_id, sample_detection):
        """Listing detections with camera_id filter passes it to repo."""
        camera_id = uuid.uuid4()
        with patch.object(
            PlateDetectionRepository, "list", AsyncMock(return_value=[sample_detection])
        ) as mock_list:
            result = await detection_service.list_detections(tenant_id, camera_id=camera_id)
            mock_list.assert_called_once_with(tenant_id, camera_id, None, None, 100, 0)
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_detections_filters_by_plate_number(self, detection_service, tenant_id, sample_detection):
        """Listing detections with plate_number filter passes it to repo."""
        with patch.object(
            PlateDetectionRepository, "list", AsyncMock(return_value=[sample_detection])
        ) as mock_list:
            await detection_service.list_detections(tenant_id, plate_number="ABC")
            mock_list.assert_called_once_with(tenant_id, None, "ABC", None, 100, 0)

    @pytest.mark.asyncio
    async def test_list_detections_filters_by_detection_type(self, detection_service, tenant_id, sample_detection):
        """Listing detections with detection_type filter passes it to repo."""
        with patch.object(
            PlateDetectionRepository, "list", AsyncMock(return_value=[sample_detection])
        ) as mock_list:
            await detection_service.list_detections(tenant_id, detection_type="entry")
            mock_list.assert_called_once_with(tenant_id, None, None, "entry", 100, 0)

    @pytest.mark.asyncio
    async def test_list_detections_pagination(self, detection_service, tenant_id):
        """Listing detections passes limit and offset to repo."""
        with patch.object(
            PlateDetectionRepository, "list", AsyncMock(return_value=[])
        ) as mock_list:
            await detection_service.list_detections(tenant_id, limit=50, offset=20)
            mock_list.assert_called_once_with(tenant_id, None, None, None, 50, 20)

    @pytest.mark.asyncio
    async def test_get_stats_returns_stats(self, detection_service, tenant_id):
        """Getting stats returns detection statistics."""
        mock_stats = {
            "total_detections": 25,
            "avg_confidence": 0.873,
            "entries": 15,
            "exits": 10,
        }
        with patch.object(
            PlateDetectionRepository, "get_stats", AsyncMock(return_value=mock_stats)
        ):
            camera_id = uuid.uuid4()
            result = await detection_service.get_stats(tenant_id, camera_id, hours=48)
            assert result.total_detections == 25
            assert result.avg_confidence == 0.873
            assert result.entries == 15
            assert result.exits == 10


# ─────────────────────────────────────────────────────────────────────────────
# OCRService tests — RF-017 (placeholder)
# ─────────────────────────────────────────────────────────────────────────────

class TestOCRService:
    """Tests for OCR inference placeholder."""

    @pytest.fixture
    def ocr_service(self, mock_db_session, mock_camera_repo):
        return OCRService(mock_db_session, mock_camera_repo)

    @pytest.mark.asyncio
    async def test_infer_plate_returns_none_when_camera_not_found(self, ocr_service, tenant_id):
        """Inference returns None when camera does not belong to tenant."""
        mock_camera_repo = MagicMock()
        mock_camera_repo.get_by_id = AsyncMock(return_value=None)
        ocr = OCRService(MagicMock(), mock_camera_repo)

        request = OCRInferenceRequest(
            camera_id=uuid.uuid4(),
            image_base64="SSBhbSB0ZXN0",
            timestamp=datetime.now(timezone.utc),
        )
        result = await ocr.infer_plate(tenant_id, request)
        assert result is None

    @pytest.mark.asyncio
    async def test_infer_plate_returns_response(self, ocr_service, tenant_id, sample_camera):
        """Inference returns a response with placeholder plate data."""
        mock_camera_repo = MagicMock()
        mock_camera_repo.get_by_id = AsyncMock(return_value=sample_camera)
        ocr = OCRService(MagicMock(), mock_camera_repo)

        request = OCRInferenceRequest(
            camera_id=sample_camera.id,
            image_base64="SSBhbSB0ZXN0",
            timestamp=datetime.now(timezone.utc),
        )
        result = await ocr.infer_plate(tenant_id, request)
        assert result is not None
        assert result.plate_number == "ABC123"
        assert result.confidence == 0.85
        assert result.processing_time_ms is not None


# ─────────────────────────────────────────────────────────────────────────────
# Schema tests — dataclass serialization
# ─────────────────────────────────────────────────────────────────────────────

class TestANPRCameraSchemas:
    """Tests for ANPRCamera dataclass schemas."""

    def test_camera_create_to_dict(self):
        """ANPRCameraCreate.to_dict() returns correct dict."""
        camera = ANPRCameraCreate(
            name="Test Camera",
            sede_id=uuid.uuid4(),
            stream_url="rtsp://test/stream",
            confidence_threshold=0.8,
            lane_id="lane-2",
        )
        d = camera.to_dict()
        assert d["name"] == "Test Camera"
        assert d["confidence_threshold"] == 0.8
        assert d["lane_id"] == "lane-2"

    def test_camera_update_to_dict_partial(self):
        """ANPRCameraUpdate.to_dict() only includes set fields."""
        update = ANPRCameraUpdate(name="New Name")
        d = update.to_dict()
        assert "name" in d
        assert "is_active" not in d

    def test_camera_response_to_dict(self):
        """ANPRCameraResponse.to_dict() returns JSON-serializable dict."""
        from app.schemas.anpr import ANPRCameraResponse
        now = datetime.now(timezone.utc)
        response = ANPRCameraResponse(
            id=uuid.uuid4(),
            name="Test",
            sede_id=uuid.uuid4(),
            stream_url="rtsp://test",
            is_active=True,
            lane_id=None,
            confidence_threshold=0.75,
            created_at=now,
            updated_at=now,
        )
        d = response.to_dict()
        assert d["name"] == "Test"
        assert d["is_active"] is True
        assert "id" in d
        assert "created_at" in d

    def test_camera_response_from_model(self, sample_camera):
        """ANPRCameraResponse.from_model() creates correct response."""
        from app.schemas.anpr import ANPRCameraResponse
        response = ANPRCameraResponse.from_model(sample_camera)
        assert response.name == sample_camera.name
        assert response.id == sample_camera.id


class TestPlateDetectionSchemas:
    """Tests for PlateDetection dataclass schemas."""

    def test_detection_create_to_dict(self):
        """PlateDetectionCreate.to_dict() returns correct dict."""
        detection = PlateDetectionCreate(
            camera_id=uuid.uuid4(),
            plate_number="DEF456",
            confidence=0.88,
            detection_type="entry",
            processing_time_ms=50,
        )
        d = detection.to_dict()
        assert d["plate_number"] == "DEF456"
        assert d["confidence"] == 0.88
        assert d["processing_time_ms"] == 50

    def test_detection_response_to_dict(self):
        """PlateDetectionResponse.to_dict() returns JSON-serializable dict."""
        from app.schemas.anpr import PlateDetectionResponse
        now = datetime.now(timezone.utc)
        response = PlateDetectionResponse(
            id=uuid.uuid4(),
            camera_id=uuid.uuid4(),
            plate_number="GHI789",
            confidence=0.91,
            detection_type="exit",
            image_path=None,
            cropped_plate_path=None,
            processing_time_ms=42,
            matched_reservation_id=None,
            timestamp=now,
            created_at=now,
        )
        d = response.to_dict()
        assert d["plate_number"] == "GHI789"
        assert d["matched_reservation_id"] is None

    def test_detection_response_from_model(self, sample_detection):
        """PlateDetectionResponse.from_model() creates correct response."""
        from app.schemas.anpr import PlateDetectionResponse
        response = PlateDetectionResponse.from_model(sample_detection)
        assert response.plate_number == sample_detection.plate_number
        assert response.confidence == sample_detection.confidence


class TestOCRInferenceSchemas:
    """Tests for OCR inference schemas."""

    def test_ocr_inference_request_from_dict(self):
        """OCRInferenceRequest.from_dict() parses JSON correctly."""
        data = {
            "camera_id": str(uuid.uuid4()),
            "image_base64": "SGVsbG8gV29ybGQ=",
            "timestamp": "2025-01-15T10:30:00Z",
        }
        request = OCRInferenceRequest.from_dict(data)
        assert request.image_base64 == "SGVsbG8gV29ybGQ="
        assert request.camera_id == uuid.UUID(data["camera_id"])

    def test_ocr_inference_response_to_dict(self):
        """OCRInferenceResponse.to_dict() returns JSON-serializable dict."""
        response = OCRInferenceResponse(
            plate_number="ABC123",
            confidence=0.85,
            processing_time_ms=35,
            cropped_image_base64=None,
        )
        d = response.to_dict()
        assert d["plate_number"] == "ABC123"
        assert d["confidence"] == 0.85


# ─────────────────────────────────────────────────────────────────────────────
# Repository tests
# ─────────────────────────────────────────────────────────────────────────────

class TestANPRCameraRepository:
    """Tests for ANPRCameraRepository data access."""

    def test_repo_initialized_with_session(self, mock_db_session):
        """Repository stores session reference."""
        repo = ANPRCameraRepository(mock_db_session)
        assert repo.session is mock_db_session


class TestPlateDetectionRepository:
    """Tests for PlateDetectionRepository data access."""

    def test_repo_initialized_with_session(self, mock_db_session):
        """Repository stores session reference."""
        repo = PlateDetectionRepository(mock_db_session)
        assert repo.session is mock_db_session