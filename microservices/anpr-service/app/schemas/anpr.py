"""ANPR schemas — pure Python dataclasses (no pydantic v2)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ── Enums ────────────────────────────────────────────────────────────────────


@dataclass
class DetectionType:
    """Detection type enum values."""
    ENTRY: str = "entry"
    EXIT: str = "exit"


# ── Camera ───────────────────────────────────────────────────────────────────


@dataclass
class ANPRCameraBase:
    """Base fields for ANPR camera."""
    name: str
    sede_id: uuid.UUID
    stream_url: str


@dataclass
class ANPRCameraCreate(ANPRCameraBase):
    """Fields needed to create a camera."""
    detection_zone: Optional[dict] = None
    lane_id: Optional[str] = None
    model_path: Optional[str] = None
    confidence_threshold: float = 0.7

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "sede_id": self.sede_id,
            "stream_url": self.stream_url,
            "detection_zone": self.detection_zone,
            "lane_id": self.lane_id,
            "model_path": self.model_path,
            "confidence_threshold": self.confidence_threshold,
        }


@dataclass
class ANPRCameraUpdate:
    """Fields that can be patched on a camera."""
    name: Optional[str] = None
    stream_url: Optional[str] = None
    detection_zone: Optional[dict] = None
    is_active: Optional[bool] = None
    confidence_threshold: Optional[float] = None

    def to_dict(self) -> dict:
        out = {}
        if self.name is not None:
            out["name"] = self.name
        if self.stream_url is not None:
            out["stream_url"] = self.stream_url
        if self.detection_zone is not None:
            out["detection_zone"] = self.detection_zone
        if self.is_active is not None:
            out["is_active"] = self.is_active
        if self.confidence_threshold is not None:
            out["confidence_threshold"] = self.confidence_threshold
        return out


@dataclass
class ANPRCameraResponse:
    """Camera as returned by API."""
    id: uuid.UUID
    name: str
    sede_id: uuid.UUID
    stream_url: str
    is_active: bool
    lane_id: Optional[str]
    confidence_threshold: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, camera) -> ANPRCameraResponse:
        return cls(
            id=camera.id,
            name=camera.name,
            sede_id=camera.sede_id,
            stream_url=camera.stream_url,
            is_active=camera.is_active,
            lane_id=camera.lane_id,
            confidence_threshold=camera.confidence_threshold,
            created_at=camera.created_at,
            updated_at=camera.updated_at,
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "sede_id": str(self.sede_id),
            "stream_url": self.stream_url,
            "is_active": self.is_active,
            "lane_id": self.lane_id,
            "confidence_threshold": self.confidence_threshold,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ── Detection ────────────────────────────────────────────────────────────────


@dataclass
class PlateDetectionBase:
    """Base fields for plate detection."""
    camera_id: uuid.UUID
    plate_number: str
    confidence: float
    detection_type: str  # "entry" or "exit"


@dataclass
class PlateDetectionCreate(PlateDetectionBase):
    """Fields needed to record a detection."""
    image_path: Optional[str] = None
    cropped_plate_path: Optional[str] = None
    processing_time_ms: Optional[int] = None
    matched_reservation_id: Optional[uuid.UUID] = None

    def to_dict(self) -> dict:
        return {
            "camera_id": self.camera_id,
            "plate_number": self.plate_number,
            "confidence": self.confidence,
            "detection_type": self.detection_type,
            "image_path": self.image_path,
            "cropped_plate_path": self.cropped_plate_path,
            "processing_time_ms": self.processing_time_ms,
            "matched_reservation_id": self.matched_reservation_id,
        }


@dataclass
class PlateDetectionResponse:
    """Detection as returned by API."""
    id: uuid.UUID
    camera_id: uuid.UUID
    plate_number: str
    confidence: float
    detection_type: str
    image_path: Optional[str]
    cropped_plate_path: Optional[str]
    processing_time_ms: Optional[int]
    matched_reservation_id: Optional[uuid.UUID]
    timestamp: datetime
    created_at: datetime

    @classmethod
    def from_model(cls, detection) -> PlateDetectionResponse:
        return cls(
            id=detection.id,
            camera_id=detection.camera_id,
            plate_number=detection.plate_number,
            confidence=detection.confidence,
            detection_type=detection.detection_type,
            image_path=detection.image_path,
            cropped_plate_path=detection.cropped_plate_path,
            processing_time_ms=detection.processing_time_ms,
            matched_reservation_id=detection.matched_reservation_id,
            timestamp=detection.timestamp,
            created_at=detection.created_at,
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "camera_id": str(self.camera_id),
            "plate_number": self.plate_number,
            "confidence": self.confidence,
            "detection_type": self.detection_type,
            "image_path": self.image_path,
            "cropped_plate_path": self.cropped_plate_path,
            "processing_time_ms": self.processing_time_ms,
            "matched_reservation_id": str(self.matched_reservation_id) if self.matched_reservation_id else None,
            "timestamp": self.timestamp.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


# ── OCR Inference ────────────────────────────────────────────────────────────


@dataclass
class OCRInferenceRequest:
    """Incoming frame from camera for OCR inference."""
    camera_id: uuid.UUID
    image_base64: str
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: dict) -> OCRInferenceRequest:
        return cls(
            camera_id=uuid.UUID(data["camera_id"]),
            image_base64=data["image_base64"],
            timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
        )


@dataclass
class OCRInferenceResponse:
    """Result from OCR inference."""
    plate_number: Optional[str] = None
    confidence: Optional[float] = None
    processing_time_ms: Optional[int] = None
    cropped_image_base64: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "plate_number": self.plate_number,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
            "cropped_image_base64": self.cropped_image_base64,
        }


# ── Statistics ──────────────────────────────────────────────────────────────


@dataclass
class DetectionStats:
    """Detection statistics for a camera."""
    total_detections: int
    avg_confidence: float
    entries: int
    exits: int

    def to_dict(self) -> dict:
        return {
            "total_detections": self.total_detections,
            "avg_confidence": self.avg_confidence,
            "entries": self.entries,
            "exits": self.exits,
        }