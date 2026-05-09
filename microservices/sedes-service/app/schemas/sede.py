"""Pydantic schemas for Sedes Service."""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class TipoEspacio(str, Enum):
    """Tipo de espacio de estacionamiento."""
    CUBIERTA = "cubierta"
    DESCUBIERTA = "descubierta"
    VIP = "vip"
    MOTO = "moto"


class EstadoEspacio(str, Enum):
    """Estado de un espacio."""
    DISPONIBLE = "disponible"
    OCUPADO = "ocupado"
    MANTENIMIENTO = "mantenimiento"


# ============== SEDE SCHEMAS ==============

class SedeBase(BaseModel):
    """Base sede schema."""
    nombre: str = Field(..., min_length=1, max_length=255, description="Sede name")
    direccion: Optional[str] = Field(None, description="Address")
    ciudad: Optional[str] = Field(None, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    pais: str = Field(default="Colombia", max_length=100)
    latitud: Optional[float] = Field(None, description="Latitude")
    longitud: Optional[float] = Field(None, description="Longitude")
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    capacidad: int = Field(default=0, ge=0, description="Total parking spots")
    espacios_activos: int = Field(default=0, ge=0, description="Active spaces")
    horarios: Optional[str] = Field(None, description="Operating hours as JSON")
    servicios: Optional[str] = Field(None, description="Services as JSON")


class SedeCreate(SedeBase):
    """Schema for creating a sede."""
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")


class SedeUpdate(BaseModel):
    """Schema for updating a sede."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    pais: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    capacidad: Optional[int] = Field(None, ge=0)
    espacios_activos: Optional[int] = Field(None, ge=0)
    estado: Optional[bool] = None
    horarios: Optional[str] = None
    servicios: Optional[str] = None


class SedeResponse(SedeBase):
    """Schema for sede response."""
    id: str = Field(..., description="Sede ID")
    slug: str = Field(..., description="URL-friendly slug")
    estado: bool = Field(default=True)
    tenant_id: str = Field(..., description="Multi-tenant ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SedeListResponse(BaseModel):
    """Schema for paginated sede listing."""
    items: list[SedeResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============== ZONA SCHEMAS ==============

class ZonaBase(BaseModel):
    """Base zona schema."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Zone name")
    descripcion: Optional[str] = Field(None, description="Zone description")
    tipo: str = Field(default="general", max_length=50, description="Zone type")
    capacidad: int = Field(default=0, ge=0, description="Total spots in zone")
    espacios_disponibles: int = Field(default=0, ge=0, description="Available spots")
    piso: Optional[str] = Field(None, max_length=20, description="Floor")
    estado: bool = Field(default=True, description="Active state")


class ZonaCreate(ZonaBase):
    """Schema for creating a zona."""
    pass


class ZonaUpdate(BaseModel):
    """Schema for updating a zona."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    capacidad: Optional[int] = Field(None, ge=0)
    espacios_disponibles: Optional[int] = Field(None, ge=0)
    piso: Optional[str] = None
    estado: Optional[bool] = None


class ZonaResponse(ZonaBase):
    """Schema for zona response."""
    id: str = Field(..., description="Zone ID")
    sede_id: str = Field(..., description="Sede ID")
    tenant_id: str = Field(..., description="Multi-tenant ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ZonaListResponse(BaseModel):
    """Schema for paginated zona listing."""
    items: list[ZonaResponse]
    total: int


# ============== ESPACIO SCHEMAS ==============

class EspacioBase(BaseModel):
    """Base espacio schema."""
    numero: str = Field(..., min_length=1, max_length=20, description="Space number")
    piso: Optional[str] = Field(None, max_length=20, description="Floor")
    tipo: str = Field(..., max_length=50, description="Space type")
    estado: str = Field(default="disponible", max_length=50, description="Space status")
    descripcion: Optional[str] = Field(None, description="Space description")


class EspacioCreate(EspacioBase):
    """Schema for creating an espacio."""
    pass


class EspacioUpdate(BaseModel):
    """Schema for updating an espacio."""
    numero: Optional[str] = Field(None, min_length=1, max_length=20)
    piso: Optional[str] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None
    descripcion: Optional[str] = None


class EspacioResponse(EspacioBase):
    """Schema for espacio response."""
    id: str = Field(..., description="Space ID")
    zona_id: str = Field(..., description="Zone ID")
    sede_id: str = Field(..., description="Sede ID")
    tenant_id: str = Field(..., description="Multi-tenant ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EspacioListResponse(BaseModel):
    """Schema for paginated espacio listing."""
    items: list[EspacioResponse]
    total: int


# ============== DISPONIBILIDAD SCHEMAS ==============

class DisponibilidadZona(BaseModel):
    """Disponibilidad para una zona."""
    zona_id: str
    nombre: str
    tipo: str
    total: int
    disponibles: int
    ocupados: int
    ocupacion_pct: float


class DisponibilidadResponse(BaseModel):
    """Schema for disponibilidad response."""
    sede_id: str
    nombre: str
    total_espacios: int
    espacios_disponibles: int
    espacios_ocupados: int
    ocupacion_pct: float
    zonas: list[DisponibilidadZona]


class OcupacionHistorialItem(BaseModel):
    """Item de historial de ocupación."""
    fecha: datetime
    hora: int
    espacios_totales: int
    espacios_ocupados: int
    ocupacion_pct: float


class OcupacionHistorialResponse(BaseModel):
    """Schema for ocupación historial response."""
    sede_id: str
    fecha_inicio: datetime
    fecha_fin: datetime
    datos: list[OcupacionHistorialItem]


# ============== CONFIG SCHEMAS ==============

class SedeConfigSchema(BaseModel):
    """Schema for sede configuration."""
    clave: str = Field(..., description="Config key")
    valor: str = Field(..., description="Config value")
    tipo: str = Field(default="string", description="Value type")


class SedeConfigResponse(BaseModel):
    """Schema for sede config response."""
    sede_id: str
    configs: list[SedeConfigSchema]