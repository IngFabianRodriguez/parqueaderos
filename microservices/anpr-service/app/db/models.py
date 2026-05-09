"""SQLAlchemy models — ANPR Service."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models — provides tenant_id on all tables."""

    pass


class TenantMixin:
    """Adds tenant_id to any model."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )


class ANPRCamera(TenantMixin, Base):
    """ANPR Camera configuration."""

    __tablename__ = "anpr_cameras"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sede_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sedes.id"), nullable=False)
    stream_url: Mapped[str] = mapped_column(Text, nullable=False)
    detection_zone: Mapped[dict | None] = mapped_column(Text, nullable=True)  # JSON polygon
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    lane_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_path: Mapped[str | None] = mapped_column(String(500), nullable=True)  # path to LPR model
    confidence_threshold: Mapped[float] = mapped_column(Float, default=0.7)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    detections: Mapped[list["PlateDetection"]] = relationship("PlateDetection", back_populates="camera", cascade="all, delete-orphan")


class PlateDetection(TenantMixin, Base):
    """License plate detection event."""

    __tablename__ = "plate_detections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("anpr_cameras.id"), nullable=False, index=True)
    plate_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 - 1.0
    detection_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # entry | exit
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cropped_plate_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    matched_reservation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reservations.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    camera: Mapped["ANPRCamera"] = relationship("ANPRCamera", back_populates="detections")


class PlateDetectionEvent(TenantMixin, Base):
    """Kafka-stored fallback for detection events (if DB write fails)."""

    __tablename__ = "plate_detection_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("anpr_cameras.id"), nullable=False, index=True)
    plate_number: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    detection_type: Mapped[str] = mapped_column(String(20), nullable=False)
    kafka_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kafka_partition: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)