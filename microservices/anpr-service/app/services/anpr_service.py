"""ANPR Service — business logic."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.repositories.anpr import ANPRCameraRepository, PlateDetectionRepository
from app.schemas.anpr import (
    ANPRCameraCreate,
    ANPRCameraUpdate,
    ANPRCameraResponse,
    PlateDetectionCreate,
    PlateDetectionResponse,
    OCRInferenceRequest,
    OCRInferenceResponse,
    DetectionStats,
)


@dataclass
class ANPRCameraService:
    """Business logic for ANPR cameras."""
    session: any

    def _repo(self) -> ANPRCameraRepository:
        return ANPRCameraRepository(self.session)

    async def create_camera(
        self, tenant_id: uuid.UUID, camera_in: ANPRCameraCreate
    ) -> ANPRCameraResponse:
        """Register a new ANPR camera for a tenant."""
        from app.db.models import ANPRCamera

        camera = ANPRCamera(
            tenant_id=tenant_id,
            name=camera_in.name,
            sede_id=camera_in.sede_id,
            stream_url=camera_in.stream_url,
            detection_zone=camera_in.detection_zone,
            lane_id=camera_in.lane_id,
            model_path=camera_in.model_path,
            confidence_threshold=camera_in.confidence_threshold,
        )
        created = await self._repo().create(camera)
        return ANPRCameraResponse.from_model(created)

    async def get_camera(
        self, tenant_id: uuid.UUID, camera_id: uuid.UUID
    ) -> Optional[ANPRCameraResponse]:
        """Get a single camera by ID."""
        camera = await self._repo().get_by_id(tenant_id, camera_id)
        if camera is None:
            return None
        return ANPRCameraResponse.from_model(camera)

    async def list_cameras(
        self,
        tenant_id: uuid.UUID,
        sede_id: Optional[uuid.UUID] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ANPRCameraResponse]:
        """List cameras for a tenant with optional filters."""
        cameras = await self._repo().list(tenant_id, sede_id, is_active, limit, offset)
        return [ANPRCameraResponse.from_model(c) for c in cameras]

    async def update_camera(
        self, tenant_id: uuid.UUID, camera_id: uuid.UUID, update: ANPRCameraUpdate
    ) -> Optional[ANPRCameraResponse]:
        """Patch-update a camera."""
        camera = await self._repo().get_by_id(tenant_id, camera_id)
        if camera is None:
            return None
        updates = update.to_dict()
        for key, value in updates.items():
            setattr(camera, key, value)
        updated = await self._repo().update(camera)
        return ANPRCameraResponse.from_model(updated)

    async def delete_camera(
        self, tenant_id: uuid.UUID, camera_id: uuid.UUID
    ) -> bool:
        """Delete a camera. Returns True if deleted, False if not found."""
        camera = await self._repo().get_by_id(tenant_id, camera_id)
        if camera is None:
            return False
        await self._repo().delete(camera)
        return True


@dataclass
class PlateDetectionService:
    """Business logic for plate detections."""
    session: any

    def _repo(self) -> PlateDetectionRepository:
        return PlateDetectionRepository(self.session)

    async def create_detection(
        self, tenant_id: uuid.UUID, detection_in: PlateDetectionCreate
    ) -> PlateDetectionResponse:
        """Record a new plate detection."""
        from app.db.models import PlateDetection

        detection = PlateDetection(
            tenant_id=tenant_id,
            camera_id=detection_in.camera_id,
            plate_number=detection_in.plate_number,
            confidence=detection_in.confidence,
            detection_type=detection_in.detection_type,
            image_path=detection_in.image_path,
            cropped_plate_path=detection_in.cropped_plate_path,
            processing_time_ms=detection_in.processing_time_ms,
            matched_reservation_id=detection_in.matched_reservation_id,
        )
        created = await self._repo().create(detection)
        return PlateDetectionResponse.from_model(created)

    async def get_detection(
        self, tenant_id: uuid.UUID, detection_id: uuid.UUID
    ) -> Optional[PlateDetectionResponse]:
        """Get a single detection by ID."""
        detection = await self._repo().get_by_id(tenant_id, detection_id)
        if detection is None:
            return None
        return PlateDetectionResponse.from_model(detection)

    async def list_detections(
        self,
        tenant_id: uuid.UUID,
        camera_id: Optional[uuid.UUID] = None,
        plate_number: Optional[str] = None,
        detection_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PlateDetectionResponse]:
        """List detections with optional filters."""
        detections = await self._repo().list(
            tenant_id, camera_id, plate_number, detection_type, limit, offset
        )
        return [PlateDetectionResponse.from_model(d) for d in detections]

    async def get_stats(
        self, tenant_id: uuid.UUID, camera_id: uuid.UUID, hours: int = 24
    ) -> DetectionStats:
        """Get detection statistics for a camera."""
        stats = await self._repo().get_stats(tenant_id, camera_id, hours)
        return DetectionStats(
            total_detections=stats["total_detections"],
            avg_confidence=stats["avg_confidence"],
            entries=stats["entries"],
            exits=stats["exits"],
        )


@dataclass
class OCRService:
    """Business logic for OCR inference.

    This is a placeholder — RF-017 will integrate the LPR ONNX engine.
    Currently returns a simulated response.
    """
    session: any
    camera_repo: ANPRCameraRepository

    async def infer_plate(
        self, tenant_id: uuid.UUID, request: OCRInferenceRequest
    ) -> Optional[OCRInferenceResponse]:
        """Run OCR inference on a camera frame.

        PLACEHOLDER — replaces with LPRNet/ONNX runtime for RF-017.
        Steps:
          1. Decode base64 image
          2. Pre-process (resize, normalize)
          3. Run ONNX inference via onnxruntime
          4. Post-process → plate string + confidence
          5. Return structured response
        """
        import time
        start = time.perf_counter()

        # Verify camera belongs to tenant
        camera = await self.camera_repo.get_by_id(tenant_id, request.camera_id)
        if camera is None:
            return None

        # TODO: RF-017 — call app.state.lpr_engine.predict(image_bytes)
        # Simulated inference
        plate_number = "ABC123"
        confidence = 0.85
        processing_time_ms = int((time.perf_counter() - start) * 1000)

        return OCRInferenceResponse(
            plate_number=plate_number,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
            cropped_image_base64=None,
        )