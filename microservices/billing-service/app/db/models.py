"""SQLAlchemy models for billing-service."""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Text, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.db.base import Base


class EstadoConciliacion(str, enum.Enum):
    CONCILIADO = "conciliado"
    EN_DISCREPANCIA = "en_discrepancia"
    JUSTIFICADO = "justificado"
    SIN_DATOS = "sin_datos"


class MotivoDiferencia(str, enum.Enum):
    ERROR_CONTEO = "ERROR_CONTEO"
    BILLETE_FALSO = "BILLETE_FALSO"
    TRANSACCION_OMITIDA = "TRANSACCION_OMITIDA"
    VENTA_CANCELADA = "VENTA_CANCELADA"
    SOBRANTE_CAJA = "SOBRANTE_CAJA"
    FALTANTE_CAJA = "FALTANTE_CAJA"
    OTRO = "OTRO"


class EstadoJustificacion(str, enum.Enum):
    PENDIENTE_APROBACION = "pendiente_aprobacion"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"


class EstadoTurno(str, enum.Enum):
    ABIERTO = "abierto"
    CERRADO = "cerrado"


class Tariff(Base):
    """Tariff model for pricing rules."""

    __tablename__ = "tariffs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sede_id: Mapped[str] = mapped_column(String(36), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tariff_type: Mapped[str] = mapped_column(String(20), nullable=False)  # hourly, fixed, subscription
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="COP")
    billing_period: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # daily, monthly
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # car, motorcycle, truck
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Invoice(Base):
    """Invoice model for billing invoices."""

    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    customer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_nit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sede_id: Mapped[str] = mapped_column(String(36), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="COP")
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, issued, paid, cancelled
    dian_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # DIAN response ID
    dian_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    issued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InvoiceLine(Base):
    """InvoiceLine model for invoice line items."""

    __tablename__ = "invoice_lines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Moroso(Base):
    """Moroso (delinquent) model for tracking unpaid invoices."""

    __tablename__ = "morosos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False)
    amount_due: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    days_overdue: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, paid, written_off
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Wallet(Base):
    """Wallet model for prepaid balances."""

    __tablename__ = "billing_wallets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3), default="COP")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conciliacion(Base):
    """Conciliacion model for cash reconciliation (RF-169, RF-170)."""

    __tablename__ = "conciliaciones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    turno_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    operador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sede_id: Mapped[str] = mapped_column(String(36), nullable=False)
    total_esperado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total_fisico: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    diferencia: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    porcentaje_diferencia: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    estado: Mapped[str] = mapped_column(String(30), default="sin_datos")  # conciliado, en_discrepancia, justificado, sin_datos
    umbral_aplicado: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.5"))
    fecha_ultima_conciliacion: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JustificacionDiferencia(Base):
    """JustificacionDiferencia model for documenting cash discrepancies (RF-171)."""

    __tablename__ = "justificaciones_diferencia"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    conciliacion_id: Mapped[str] = mapped_column(String(36), ForeignKey("conciliaciones.id"), nullable=False)
    operador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    motivo: Mapped[str] = mapped_column(String(30), nullable=False)  # ERROR_CONTEO, BILLETE_FALSO, etc.
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    evidencia_foto_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    evidencia_pendiente: Mapped[bool] = mapped_column(Boolean, default=False)
    estado: Mapped[str] = mapped_column(String(30), default="pendiente_aprobacion")
    administrador_revisor: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    fecha_revision: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    comentario_revision: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Turno(Base):
    """Turno model for operator shifts (RF-172)."""

    __tablename__ = "turnos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    operador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sede_id: Mapped[str] = mapped_column(String(36), nullable=False)
    caja_id: Mapped[str] = mapped_column(String(36), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="abierto")  # abierto, cerrado
    hora_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    hora_cierre: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_pasajes: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_recargas: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_otros: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_ingresos: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_aperturas: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    cantidad_alertas_atendidas: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReporteCierre(Base):
    """ReporteCierre model for shift closing reports (RF-173)."""

    __tablename__ = "reportes_cierre"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    turno_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    operador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sede_id: Mapped[str] = mapped_column(String(36), nullable=False)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    hash_documento: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    firma_digital: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    resumen_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON with turn summary
    generado_ok: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NotificacionCierre(Base):
    """NotificacionCierre model for shift close notifications (RF-174)."""

    __tablename__ = "notificaciones_cierre"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    turno_id: Mapped[str] = mapped_column(String(36), nullable=False)
    operador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    administrador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sede_id: Mapped[str] = mapped_column(String(36), nullable=False)
    canales_utilizados: Mapped[str] = mapped_column(String(100), nullable=True)  # comma separated: email,push,slack,sms
    estado_envio: Mapped[str] = mapped_column(String(30), default="pendiente")  # enviado, fallido, pendiente_reintento
    contenido_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp_envio: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)