"""SQLAlchemy models for Sedes Service.

Multi-tenant architecture: all tables include tenant_id column.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Sede(Base):
    """Sede model - represents a parking location/sede."""

    __tablename__ = "sedes"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    direccion = Column(Text, nullable=True)
    ciudad = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)
    pais = Column(String(100), default="Colombia")
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    capacidad = Column(Integer, default=0)  # Total parking spots
    espacios_activos = Column(Integer, default=0)  # Active spots
    estado = Column(Boolean, default=True)
    horarios = Column(Text, nullable=True)  # JSON string for operating hours
    servicios = Column(Text, nullable=True)  # JSON string for services

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    zonas = relationship("Zona", back_populates="sede", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Sede(id={self.id}, nombre={self.nombre}, tenant_id={self.tenant_id})>"


class Zona(Base):
    """Zona model - represents a zone within a sede."""

    __tablename__ = "zonas"

    id = Column(String(36), primary_key=True)
    sede_id = Column(String(36), ForeignKey("sedes.id"), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(50), default="general")  # general, discapacidad, electrico, etc
    capacidad = Column(Integer, default=0)
    espacios_disponibles = Column(Integer, default=0)
    piso = Column(String(20), nullable=True)
    estado = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sede = relationship("Sede", back_populates="zonas")
    espacios = relationship("Espacio", back_populates="zona", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Zona(id={self.id}, nombre={self.nombre}, sede_id={self.sede_id})>"


class Espacio(Base):
    """Parking space model."""

    __tablename__ = "espacios"

    id = Column(String(36), primary_key=True)
    zona_id = Column(String(36), ForeignKey("zonas.id"), nullable=False, index=True)
    sede_id = Column(String(36), ForeignKey("sedes.id"), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    numero = Column(String(20), nullable=False)
    piso = Column(String(20), nullable=True)
    tipo = Column(String(50), nullable=False)  # cubierta, descubierta, vip, moto
    estado = Column(String(50), default="disponible")  # disponible, ocupado, mantenimiento
    descripcion = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    zona = relationship("Zona", back_populates="espacios")

    def __repr__(self) -> str:
        return f"<Espacio(id={self.id}, sede_id={self.sede_id}, numero={self.numero})>"


class OcupacionHistorial(Base):
    """Historical occupation data for a sede."""

    __tablename__ = "ocupacion_historial"

    id = Column(String(36), primary_key=True)
    sede_id = Column(String(36), ForeignKey("sedes.id"), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    fecha = Column(DateTime(timezone=True), nullable=False, index=True)
    hora = Column(Integer, nullable=False)  # 0-23
    espacios_totales = Column(Integer, default=0)
    espacios_ocupados = Column(Integer, default=0)
    ocupacion_pct = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<OcupacionHistorial(sede_id={self.sede_id}, fecha={self.fecha}, hora={self.hora})>"
