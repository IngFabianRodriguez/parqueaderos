"""API v1 router — ANPR Service.

TODO references:
  - RF-015: Crear tablas anpr_cameras, plate_detections
  - RF-016: Integración Kafka — consumir eventos de detecciones
  - RF-017: OCR Engine — integración con LPRNet ONNX
  - RF-018: Endpoint para recibir frames y devolver placa leída
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import TokenData, get_current_tenant
from app.db.models import ANPRCamera, PlateDetection
from app.db.session import AsyncSession, get_db
from app.schemas.anpr import (
    ANPRCameraCreate,
    ANPRCameraResponse,
    ANPRCameraUpdate,
    OCRInferenceRequest,
    OCRInferenceResponse,
    PlateDetectionCreate,
    PlateDetectionResponse,
)

router = APIRouter(tags=["ANPR"])


# ── Cameras ──────────────────────────────────────────────────────────────────


@router.get("/cameras", response_model=list[ANPRCameraResponse])
async def list_cameras(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    sede_id: str | None = None,
    is_active: bool | None = None,
    limit: int = 100,
    offset: int = 0,
):
    """List ANPR cameras for the tenant. RF-015."""
    query = select(ANPRCamera).where(ANPRCamera.tenant_id == tenant.tenant_id)
    if sede_id:
        query = query.where(ANPRCamera.sede_id == sede_id)
    if is_active is not None:
        query = query.where(ANPRCamera.is_active == is_active)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/cameras", response_model=ANPRCameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera: ANPRCameraCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new ANPR camera. RF-015."""
    db_camera = ANPRCamera(
        tenant_id=tenant.tenant_id,
        **camera.model_dump(),
    )
    db.add(db_camera)
    try:
        await db.flush()
        await db.refresh(db_camera)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Camera with same name already exists")
    return db_camera


@router.get("/cameras/{camera_id}", response_model=ANPRCameraResponse)
async def get_camera(
    camera_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single ANPR camera. RF-015."""
    result = await db.execute(
        select(ANPRCamera).where(
            ANPRCamera.id == camera_id,
            ANPRCamera.tenant_id == tenant.tenant_id,
        )
    )
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.patch("/cameras/{camera_id}", response_model=ANPRCameraResponse)
async def update_camera(
    camera_id: str,
    update: ANPRCameraUpdate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update an ANPR camera. RF-015."""
    result = await db.execute(
        select(ANPRCamera).where(
            ANPRCamera.id == camera_id,
            ANPRCamera.tenant_id == tenant.tenant_id,
        )
    )
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(camera, key, value)
    await db.flush()
    await db.refresh(camera)
    return camera


@router.delete("/cameras/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an ANPR camera. RF-015."""
    result = await db.execute(
        select(ANPRCamera).where(
            ANPRCamera.id == camera_id,
            ANPRCamera.tenant_id == tenant.tenant_id,
        )
    )
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    await db.delete(camera)


# ── Detections ───────────────────────────────────────────────────────────────


@router.post("/detections", response_model=PlateDetectionResponse, status_code=status.HTTP_201_CREATED)
async def create_detection(
    detection: PlateDetectionCreate,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Record a license plate detection. RF-016."""
    # Verify camera belongs to tenant
    result = await db.execute(
        select(ANPRCamera).where(
            ANPRCamera.id == detection.camera_id,
            ANPRCamera.tenant_id == tenant.tenant_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Camera not found")

    db_detection = PlateDetection(
        tenant_id=tenant.tenant_id,
        **detection.model_dump(),
    )
    db.add(db_detection)
    await db.flush()
    await db.refresh(db_detection)

    # TODO: RF-016 — Publish to Kafka topic "anpr.plate-detected"
    # TODO: RF-017 — Trigger reservation matching via Notification Service

    return db_detection


@router.get("/detections", response_model=list[PlateDetectionResponse])
async def list_detections(
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    camera_id: str | None = None,
    plate_number: str | None = None,
    detection_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    """List plate detections. RF-015."""
    query = select(PlateDetection).where(PlateDetection.tenant_id == tenant.tenant_id)
    if camera_id:
        query = query.where(PlateDetection.camera_id == camera_id)
    if plate_number:
        query = query.where(PlateDetection.plate_number.ilike(f"%{plate_number}%"))
    if detection_type:
        query = query.where(PlateDetection.detection_type == detection_type)
    query = query.order_by(PlateDetection.timestamp.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/detections/{detection_id}", response_model=PlateDetectionResponse)
async def get_detection(
    detection_id: str,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single detection. RF-015."""
    result = await db.execute(
        select(PlateDetection).where(
            PlateDetection.id == detection_id,
            PlateDetection.tenant_id == tenant.tenant_id,
        )
    )
    detection = result.scalar_one_or_none()
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


# ── OCR Inference (placeholder) ─────────────────────────────────────────────
# TODO: RF-017 — Replace with actual LPR OCR engine integration


@router.post("/infer", response_model=OCRInferenceResponse)
async def infer_plate(
    payload: OCRInferenceRequest,
    tenant: Annotated[TokenData, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Perform OCR inference on a camera frame.

    PLACEHOLDER — RF-017: Replace with LPRNet/ONNX runtime.
    Expected implementation:
      1. Decode base64 image
      2. Pre-process (resize, normalize)
      3. Run ONNX inference via onnxruntime
      4. Post-process → plate string + confidence
      5. Return structured response
    """
    # Verify camera belongs to tenant
    camera_result = await db.execute(
        select(ANPRCamera).where(
            ANPRCamera.id == payload.camera_id,
            ANPRCamera.tenant_id == tenant.tenant_id,
        )
    )
    camera = camera_result.scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # PLACEHOLDER — placeholder response for now
    # TODO: RF-017 — call app.state.lpr_engine.predict(image_bytes)
    import time

    start = time.perf_counter()

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