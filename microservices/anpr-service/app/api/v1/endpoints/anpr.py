"""API v1 endpoints — ANPR Service. RF-005 to RF-009."""
from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError

from app.core.security import TokenData, get_current_tenant
from app.db.session import AsyncSession, get_db
from app.repositories.anpr import ANPRCameraRepository, PlateDetectionRepository
from app.services.anpr_service import (
    ANPRCameraService,
    PlateDetectionService,
    OCRService,
)
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

router = APIRouter(tags=["ANPR"])


# ── Cameras ──────────────────────────────────────────────────────────────────


@router.get("/cameras", response_model=list[ANPRCameraResponse])
async def list_cameras(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    sede_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List ANPR cameras for the tenant. RF-005."""
    tenant_id = uuid.UUID(tenant.tenant_id)
    sede_uuid = uuid.UUID(sede_id) if sede_id else None

    svc = ANPRCameraService(db)
    cameras = await svc.list_cameras(tenant_id, sede_uuid, is_active, limit, offset)
    return [c.to_dict() for c in cameras]


@router.post("/cameras", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera: ANPRCameraCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new ANPR camera. RF-005."""
    tenant_id = uuid.UUID(tenant.tenant_id)
    svc = ANPRCameraService(db)
    try:
        created = await svc.create_camera(tenant_id, camera)
        return created.to_dict()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Camera with same name already exists")


@router.get("/cameras/{camera_id}", response_model=dict)
async def get_camera(
    camera_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single ANPR camera. RF-005."""
    tenant_id = uuid.UUID(tenant.tenant_id)
    camera_uuid = uuid.UUID(camera_id)
    svc = ANPRCameraService(db)
    camera = await svc.get_camera(tenant_id, camera_uuid)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera.to_dict()


@router.patch("/cameras/{camera_id}", response_model=dict)
async def update_camera(
    camera_id: str,
    update: ANPRCameraUpdate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update an ANPR camera. RF-005."""
    tenant_id = uuid.UUID(tenant.tenant_id)
    camera_uuid = uuid.UUID(camera_id)
    svc = ANPRCameraService(db)
    camera = await svc.update_camera(tenant_id, camera_uuid, update)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera.to_dict()


@router.delete("/cameras/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an ANPR camera. RF-005."""
    tenant_id = uuid.UUID(tenant.tenant_id)
    camera_uuid = uuid.UUID(camera_id)
    svc = ANPRCameraService(db)
    deleted = await svc.delete_camera(tenant_id, camera_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Camera not found")


# ── Detections ───────────────────────────────────────────────────────────────


@router.post("/detections", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_detection(
    detection: PlateDetectionCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Record a license plate detection. RF-006, RF-007."""
    tenant_id = uuid.UUID(tenant.tenant_id)

    # Verify camera belongs to tenant
    camera_repo = ANPRCameraRepository(db)
    camera = await camera_repo.get_by_id(tenant_id, detection.camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    svc = PlateDetectionService(db)
    created = await svc.create_detection(tenant_id, detection)
    return created.to_dict()


@router.get("/detections", response_model=list[dict])
async def list_detections(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    camera_id: Optional[str] = Query(None),
    plate_number: Optional[str] = Query(None),
    detection_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List plate detections. RF-006."""
    tenant_id = uuid.UUID(tenant.tenant_id)
    camera_uuid = uuid.UUID(camera_id) if camera_id else None

    svc = PlateDetectionService(db)
    detections = await svc.list_detections(
        tenant_id, camera_uuid, plate_number, detection_type, limit, offset
    )
    return [d.to_dict() for d in detections]


@router.get("/detections/{detection_id}", response_model=dict)
async def get_detection(
    detection_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single detection. RF-006."""
    tenant_id = uuid.UUID(tenant.tenant_id)
    detection_uuid = uuid.UUID(detection_id)
    svc = PlateDetectionService(db)
    detection = await svc.get_detection(tenant_id, detection_uuid)
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection.to_dict()


# ── Detection Stats ─────────────────────────────────────────────────────────


@router.get("/cameras/{camera_id}/stats", response_model=dict)
async def get_camera_stats(
    camera_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    hours: int = Query(24, ge=1, le=168),
):
    """Get detection statistics for a camera. RF-006."""
    tenant_id = uuid.UUID(tenant.tenant_id)
    camera_uuid = uuid.UUID(camera_id)

    # Verify camera belongs to tenant
    camera_repo = ANPRCameraRepository(db)
    camera = await camera_repo.get_by_id(tenant_id, camera_uuid)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    svc = PlateDetectionService(db)
    stats = await svc.get_stats(tenant_id, camera_uuid, hours)
    return stats.to_dict()


# ── OCR Inference ────────────────────────────────────────────────────────────


@router.post("/infer", response_model=dict)
async def infer_plate(
    payload: OCRInferenceRequest,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Perform OCR inference on a camera frame.

    PLACEHOLDER — RF-017: Replace with LPRNet/ONNX runtime.
    """
    tenant_id = uuid.UUID(tenant.tenant_id)
    camera_repo = ANPRCameraRepository(db)
    svc = OCRService(db, camera_repo)
    result = await svc.infer_plate(tenant_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return result.to_dict()


# ── Reservation Validation (RF-007, RF-009) ───────────────────────────────────


@router.get("/validate/{plate_number}", response_model=dict)
async def validate_vehicle(
    plate_number: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    sede_id: Optional[str] = Query(None),
):
    """
    Check if a vehicle with given plate is registered for this tenant/sede.

    RF-007: Validar vehículo registrado.
    RF-009: Detectar vehículos no autorizados.

    Returns:
      - authorized: true/false
      - matched_reservation_id: if found
      - detection_type: "entry" or "exit"
    """
    tenant_id = uuid.UUID(tenant.tenant_id)
    sede_uuid = uuid.UUID(sede_id) if sede_id else None

    # TODO: RF-017 — query reservations service for matching plate
    # For now, return unauthorized (placeholder)
    return {
        "authorized": False,
        "plate_number": plate_number,
        "matched_reservation_id": None,
        "detection_type": None,
        "message": "Vehicle not registered",
    }


@router.post("/detections/{detection_id}/authorize", response_model=dict)
async def authorize_detection(
    detection_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    matched_reservation_id: Optional[str] = None,
):
    """
    Mark a detection as authorized (linked to a reservation).

    RF-007: Vincular detección a reserva.
    """
    tenant_id = uuid.UUID(tenant.tenant_id)
    detection_uuid = uuid.UUID(detection_id)

    repo = PlateDetectionRepository(db)
    detection = await repo.get_by_id(tenant_id, detection_uuid)
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")

    if matched_reservation_id:
        detection.matched_reservation_id = uuid.UUID(matched_reservation_id)
        await repo.update(detection)

    return PlateDetectionResponse.from_model(detection).to_dict()