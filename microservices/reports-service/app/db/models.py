"""SQLAlchemy models for reports-service."""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Report(Base):
    """Report model for generated reports."""

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)  # revenue, occupancy, etc.
    format: Mapped[str] = mapped_column(String(20), default="pdf")  # pdf, csv, xlsx
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, generating, ready, failed
    file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)
    parameters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    generated_by: Mapped[str] = mapped_column(String(36), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ReportSchedule(Base):
    """ReportSchedule model for scheduled report generation."""

    __tablename__ = "report_schedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    schedule_cron: Mapped[str] = mapped_column(String(100), nullable=False)  # cron expression
    format: Mapped[str] = mapped_column(String(20), default="pdf")
    parameters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recipients: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BIConnector(Base):
    """BIConnector model for external BI tool integrations."""

    __tablename__ = "bi_connectors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    connector_type: Mapped[str] = mapped_column(String(50), nullable=False)  # tableau, powerbi, looker
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON encrypted
    status: Mapped[str] = mapped_column(String(20), default="disconnected")  # connected, disconnected, error
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)