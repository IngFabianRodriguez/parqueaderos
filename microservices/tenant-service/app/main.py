"""FastAPI application entry point with lifespan events."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.router import router as api_router
from app.core.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    setup_tracing()
    yield


def _get_setting(name: str, fallback):
    settings = get_settings()
    val = os.getenv(name.upper(), None)
    if val is not None:
        return val
    return getattr(settings, name, fallback)


import os
_service_name = os.getenv("SERVICE_NAME", "tenant-service")
_debug = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(
    title=_service_name,
    description="Tenant Service for Parqueaderos SaaS",
    version="0.1.0",
    lifespan=lifespan,
    debug=_debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/ready")
async def ready_check():
    """Readiness check endpoint."""
    return {"status": "ready"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Tenant Service", "version": "0.1.0"}