"""Dataclass schemas for billing-service (POPO - Plain Old Python Objects)."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


# ─── Enums ────────────────────────────────────────────────────────────────────

class EstadoConciliacion:
    CONCILIADO = "conciliado"
    EN_DISCREPANCIA = "en_discrepancia"
    JUSTIFICADO = "justificado"
    SIN_DATOS = "sin_datos"


class MotivoDiferencia:
    ERROR_CONTEO = "ERROR_CONTEO"
    BILLETE_FALSO = "BILLETE_FALSO"
    TRANSACCION_OMITIDA = "TRANSACCION_OMITIDA"
    VENTA_CANCELADA = "VENTA_CANCELADA"
    SOBRANTE_CAJA = "SOBRANTE_CAJA"
    FALTANTE_CAJA = "FALTANTE_CAJA"
    OTRO = "OTRO"


class EstadoJustificacion:
    PENDIENTE_APROBACION = "pendiente_aprobacion"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"


class EstadoTurno:
    ABIERTO = "abierto"
    CERRADO = "cerrado"


# ─── Tariff Schemas ─────────────────────────────────────────────────────────────

@dataclass
class TariffCreate:
    """Input schema for creating a tariff."""
    sede_id: str
    name: str
    tariff_type: str  # hourly, fixed, subscription
    amount: Decimal
    currency: str = "COP"
    billing_period: Optional[str] = None  # daily, monthly
    vehicle_type: Optional[str] = None  # car, motorcycle, truck
    valid_from: datetime = None
    valid_to: Optional[datetime] = None


@dataclass
class TariffResponse:
    """Output schema for tariff."""
    id: str
    tenant_id: str
    sede_id: str
    name: str
    tariff_type: str
    amount: Decimal
    currency: str
    billing_period: Optional[str] = None
    vehicle_type: Optional[str] = None
    valid_from: datetime = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class TariffListResponse:
    """List response for tariffs."""
    items: List[TariffResponse]
    total: int


# ─── Invoice Schemas ────────────────────────────────────────────────────────────

@dataclass
class InvoiceLineCreate:
    """Input schema for invoice line."""
    description: str
    quantity: Decimal = Decimal("1.00")
    unit_price: Decimal = Decimal("0.00")
    tax_rate: Decimal = Decimal("0.00")


@dataclass
class InvoiceCreate:
    """Input schema for creating an invoice."""
    customer_id: str
    customer_name: str
    customer_nit: Optional[str] = None
    sede_id: str = ""
    lines: List[dict] = field(default_factory=list)
    due_date: Optional[datetime] = None


@dataclass
class InvoiceResponse:
    """Output schema for invoice."""
    id: str
    tenant_id: str
    invoice_number: str
    customer_id: str
    customer_name: str
    customer_nit: Optional[str] = None
    sede_id: str
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    currency: str
    status: str
    dian_id: Optional[str] = None
    dian_status: Optional[str] = None
    issued_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class InvoiceListResponse:
    """List response for invoices."""
    items: List[InvoiceResponse]
    total: int
    page: int = 1
    page_size: int = 20


@dataclass
class InvoiceLineResponse:
    """Output schema for invoice line."""
    id: str
    invoice_id: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    amount: Decimal


# ─── Wallet Schemas ────────────────────────────────────────────────────────────

@dataclass
class WalletTopUpRequest:
    """Input schema for wallet top-up."""
    amount: Decimal


@dataclass
class WalletResponse:
    """Output schema for wallet."""
    id: str
    tenant_id: str
    user_id: str
    balance: Decimal
    currency: str
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None


# ─── Morosos Schemas ───────────────────────────────────────────────────────────

@dataclass
class MorosoResponse:
    """Output schema for moroso (delinquent)."""
    id: str
    tenant_id: str
    customer_id: str
    customer_name: str
    invoice_id: str
    amount_due: Decimal
    days_overdue: int
    status: str  # active, paid, written_off
    created_at: datetime = None
    resolved_at: Optional[datetime] = None


@dataclass
class MorosoListResponse:
    """List response for morosos."""
    items: List[MorosoResponse]
    total: int


# ─── Conciliacion Schemas (RF-169, RF-170) ──────────────────────────────────────

@dataclass
class ConciliacionResponse:
    """Output schema for cash reconciliation."""
    id: str
    tenant_id: str
    turno_id: str
    operador_id: str
    sede_id: str
    total_esperado: Decimal
    total_fisico: Decimal
    diferencia: Decimal
    porcentaje_diferencia: Decimal
    estado: str  # conciliado, en_discrepancia, justificado, sin_datos
    umbral_aplicado: Decimal
    fecha_ultima_conciliacion: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class ConciliacionCreate:
    """Input schema for creating/updating a reconciliation."""
    turno_id: str
    operador_id: str
    sede_id: str
    total_esperado: Decimal = Decimal("0.00")
    total_fisico: Decimal = Decimal("0.00")
    diferencia: Decimal = Decimal("0.00")
    porcentaje_diferencia: Decimal = Decimal("0.00")
    estado: str = EstadoConciliacion.SIN_DATOS
    umbral_aplicado: Decimal = Decimal("0.5")


@dataclass
class ConciliacionDetalleResponse:
    """Detailed reconciliation response with shift info."""
    turno_id: str
    operador_id: str
    total_esperado: Decimal
    total_fisico: Decimal
    diferencia: Decimal
    porcentaje_diferencia: Decimal
    estado_conciliacion: str
    fecha_ultima_conciliacion: Optional[datetime] = None
    tiene_justificacion: bool = False
    ingresos: dict = None  # {pasajes, recargas, otros}
    aperturas: list = None  # [{hora, monto}, ...]


# ─── Justificacion Schemas (RF-171) ────────────────────────────────────────────

@dataclass
class JustificacionCreate:
    """Input schema for creating a justification."""
    conciliacion_id: str
    operador_id: str
    motivo: str  # MotivoDiferencia enum values
    descripcion: str
    evidencia_foto_url: Optional[str] = None


@dataclass
class JustificacionResponse:
    """Output schema for justification."""
    id: str
    tenant_id: str
    conciliacion_id: str
    operador_id: str
    motivo: str
    descripcion: str
    evidencia_foto_url: Optional[str] = None
    evidencia_pendiente: bool = False
    estado: str  # pendiente_aprobacion, aprobada, rechazada
    administrador_revisor: Optional[str] = None
    fecha_revision: Optional[datetime] = None
    comentario_revision: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class JustificacionRevision:
    """Input schema for reviewing (approving/rejecting) a justification."""
    estado: str  # aprobada, rechazada
    comentario_revision: Optional[str] = None


# ─── Turno Schemas (RF-172) ─────────────────────────────────────────────────────

@dataclass
class TurnoResponse:
    """Output schema for turn/shift."""
    id: str
    tenant_id: str
    operador_id: str
    sede_id: str
    caja_id: str
    estado: str  # abierto, cerrado
    hora_inicio: datetime
    hora_cierre: Optional[datetime] = None
    total_pasajes: Decimal = Decimal("0.00")
    total_recargas: Decimal = Decimal("0.00")
    total_otros: Decimal = Decimal("0.00")
    total_ingresos: Decimal = Decimal("0.00")
    total_aperturas: Decimal = Decimal("0.00")
    cantidad_alertas_atendidas: int = 0
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class TurnoResumenResponse:
    """Summary response for turn closing (RF-172)."""
    turno_id: str
    estado: str
    resumen_turno: dict  # {ingresos: {pasajes, recargas, otros}, aperturas_talanquera, conciliacion: {estado, diferencia}}
    reporte_cierre_id: Optional[str] = None
    timestamp_cierre: Optional[datetime] = None
    operador_cierre: Optional[str] = None


# ─── Reporte Cierre Schemas (RF-173) ───────────────────────────────────────────

@dataclass
class ReporteCierreResponse:
    """Output schema for closing report."""
    id: str
    tenant_id: str
    turno_id: str
    operador_id: str
    sede_id: str
    pdf_url: Optional[str] = None
    hash_documento: Optional[str] = None
    firma_digital: Optional[str] = None
    resumen_json: Optional[str] = None
    generado_ok: bool = True
    created_at: datetime = None


@dataclass
class ReporteCierreDownloadResponse:
    """Response for downloading closing report PDF."""
    reporte_id: str
    archivo_pdf: Optional[bytes] = None
    url_descarga: Optional[str] = None
    hash_documento: Optional[str] = None
    firma_digital: Optional[str] = None
    timestamp_generacion: Optional[datetime] = None


# ─── Notificacion Cierre Schemas (RF-174) ─────────────────────────────────────

@dataclass
class NotificacionCierreResponse:
    """Output schema for close notification."""
    id: str
    tenant_id: str
    turno_id: str
    operador_id: str
    administrador_id: str
    sede_id: str
    canales_utilizados: Optional[str] = None
    estado_envio: str
    contenido_json: Optional[str] = None
    timestamp_envio: Optional[datetime] = None
    created_at: datetime = None


# ─── Discrepancia List Schema ───────────────────────────────────────────────────

@dataclass
class DiscrepanciaResponse:
    """Output schema for listing discrepancies."""
    id: str
    turno_id: str
    operador_id: str
    sede_id: str
    diferencia: Decimal
    porcentaje: Decimal
    estado: str
    fecha_conciliacion: datetime
    tiene_justificacion: bool = False


@dataclass
class DiscrepanciaListResponse:
    """List response for discrepancies."""
    items: List[DiscrepanciaResponse]
    total: int