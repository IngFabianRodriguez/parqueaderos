"""SQLAlchemy models for Tenant Service.

Multi-tenant architecture: all tables include tenant_id column.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Text, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Tenant(Base):
    """Tenant model - represents a tenant in the system."""

    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True)
    nombre = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)
    plan = Column(String(50), default="free")  # free, basic, premium, enterprise
    estado = Column(Boolean, default=True)
    config_data = Column(Text, nullable=True)  # JSON string for extra config

    # Multi-tenant
    tenant_id = Column(String(36), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, nombre={self.nombre}, slug={self.slug})>"


class TenantUser(Base):
    """Tenant user association model."""

    __tablename__ = "tenant_users"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    rol = Column(String(50), nullable=False)  # admin, operador, cliente

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<TenantUser(tenant_id={self.tenant_id}, user_id={self.user_id}, rol={self.rol})>"


class TenantConfig(Base):
    """Tenant configuration/settings model."""

    __tablename__ = "tenant_configs"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, unique=True, index=True)
    clave = Column(String(100), nullable=False)
    valor = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<TenantConfig(tenant_id={self.tenant_id}, clave={self.clave})>"