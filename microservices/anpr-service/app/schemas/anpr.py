"""Pydantic schemas — ANPR Service."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


# ── Camera ───────────────────────────────────────────────────────────────────


class ANPRCameraBase(BaseModel):
    name: str = Field(..., max_length=255)
    sede_id: uuid.UUID
    stream_url: str


class ANPRCameraCreate(ANPRCameraBase):
    detection_zone: dict | None = None
    lane_id: str | None = None
    model_path: str | None = None
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)


class ANPRCameraUpdate(BaseModel):
    name: str | None = None
    stream_url: str | None = None
    detection_zone: dict | None = None
    is_active: bool | None = None
    confidence_threshold: float | None = Field(None, ge=0.0, le=1.0)


class ANPRCameraResponse(ANPRCameraBase):
    id: uuid.UUID
    is_active: bool
    lane_id: str | None
    confidence_threshold: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Detection ────────────────────────────────────────────────────────────────


class PlateDetectionBase(BaseModel):
    camera_id: uuid.UUID
    plate_number: str = Field(..., max_length=20)
    confidence: float = Field(..., ge=0.0, le=1.0)
    detection_type: str = Field(..., pattern="^(entry|exit)$")


class PlateDetectionCreate(PlateDetectionBase):
    image_path: str | None = None
    cropped_plate_path: str | None = None
    processing_time_ms: int | None = None
    matched_reservation_id: uuid.UUID | None = None


class PlateDetectionResponse(PlateDetectionBase):
    id: uuid.UUID
    image_path: str | None
    cropped_plate_path: str | None
    processing_time_ms: int | None
    matched_reservation_id: uuid.UUID | None
    timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ── OCR Inference (placeholder) ───────────────────────────────────────────────
# TODO: RF-017 — Integration with LPR OCR engine (LPRNet / ONNX)


class OCRInferenceRequest(BaseModel):
    """Placeholder: incoming frame from camera stream for OCR inference."""

    camera_id: uuid.UUID
    image_base64: str  # base64-encoded JPEG frame
    timestamp: datetime


class OCRInferenceResponse(BaseModel):
    """Placeholder: result from OCR inference."""

    plate_number: str | None
    confidence: float | None
    processing_time_ms: int | None
    cropped_image_base64: str | None = None