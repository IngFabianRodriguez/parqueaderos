"""Initial monitoring tables — service_registry, alerts, alert_rules,
notification_channels, maintenance_windows, health_check_records,
metric_records, sla_reports. RF-100 to RF-115."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


def upgrade() -> None:
    # ── ServiceRegistry ────────────────────────────────────────────────────────
    op.create_table(
        "service_registry",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("service_id", sa.String(100), nullable=False, unique=True),
        sa.Column("service_name", sa.String(255), nullable=False),
        sa.Column("service_type", sa.String(50), nullable=True),
        sa.Column("health_url", sa.String(500), nullable=True),
        sa.Column("internal_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("metadata_", JSONB, nullable=True),
        sa.Column("version", sa.String(50), nullable=True),
        sa.Column("last_health_status", sa.String(20), nullable=True),
        sa.Column("last_health_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_latency_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        op.UniqueConstraint("service_id"),
    )
    op.create_index("ix_service_registry_tenant_active", "service_registry", ["tenant_id", "is_active"])

    # ── Alert ──────────────────────────────────────────────────────────────────
    op.create_table(
        "alert",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("service_id", sa.String(100), nullable=True, index=True),
        sa.Column("service_name", sa.String(255), nullable=True),
        sa.Column("type_", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, default="FIRING"),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, default=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", UUID(as_uuid=True), nullable=True),
        sa.Column("silenced_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alert_tenant_status", "alert", ["tenant_id", "status"])
    op.create_index("ix_alert_tenant_severity", "alert", ["tenant_id", "severity"])
    op.create_index("ix_alert_created_at", "alert", ["created_at"])

    # ── AlertRule ──────────────────────────────────────────────────────────────
    op.create_table(
        "alert_rule",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("condition", JSONB, nullable=False),
        sa.Column("cooldown_seconds", sa.Integer(), nullable=True, default=300),
        sa.Column("enabled", sa.Boolean(), nullable=False, default=True),
        sa.Column("service_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alert_rule_tenant_enabled", "alert_rule", ["tenant_id", "enabled"])

    # ── NotificationChannel ────────────────────────────────────────────────────
    op.create_table(
        "notification_channel",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("channel_type", sa.String(50), nullable=False),
        sa.Column("target", sa.String(500), nullable=True),
        sa.Column("config_", JSONB, nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notification_channel_tenant_enabled", "notification_channel", ["tenant_id", "enabled"])

    # ── MaintenanceWindow ───────────────────────────────────────────────────────
    op.create_table(
        "maintenance_window",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, default="scheduled"),
        sa.Column("service_ids", JSONB, nullable=True),
        sa.Column("silenced_alert_ids", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_maintenance_window_tenant_estado", "maintenance_window", ["tenant_id", "estado"])
    op.create_index("ix_maintenance_window_start_time", "maintenance_window", ["start_time"])

    # ── HealthCheckRecord ───────────────────────────────────────────────────────
    op.create_table(
        "health_check_record",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("service_id", sa.String(100), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("response_code", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_health_check_service_time", "health_check_record", ["service_id", "checked_at"])
    op.create_index("ix_health_check_tenant_time", "health_check_record", ["tenant_id", "checked_at"])

    # ── MetricRecord ────────────────────────────────────────────────────────────
    op.create_table(
        "metric_record",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("service_id", sa.String(100), nullable=False, index=True),
        sa.Column("metric_type", sa.String(50), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("labels_", JSONB, nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, index=True),
    )
    op.create_index("ix_metric_record_service_type_time", "metric_record", ["service_id", "metric_type", "recorded_at"])
    op.create_index("ix_metric_record_tenant_time", "metric_record", ["tenant_id", "recorded_at"])

    # ── SLAReport ───────────────────────────────────────────────────────────────
    op.create_table(
        "sla_report",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("service_id", sa.String(100), nullable=False),
        sa.Column("sla_type", sa.String(50), nullable=False),
        sa.Column("target_percent", sa.Float(), nullable=False),
        sa.Column("actual_percent", sa.Float(), nullable=False),
        sa.Column("total_incidents", sa.Integer(), nullable=True),
        sa.Column("total_downtime_seconds", sa.Integer(), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sla_report_service_period", "sla_report", ["service_id", "period_start", "period_end"])


def downgrade() -> None:
    op.drop_table("sla_report")
    op.drop_table("metric_record")
    op.drop_table("health_check_record")
    op.drop_table("maintenance_window")
    op.drop_table("notification_channel")
    op.drop_table("alert_rule")
    op.drop_table("alert")
    op.drop_table("service_registry")