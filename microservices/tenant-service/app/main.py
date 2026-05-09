"""FastAPI application entry point with lifespan events."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import router as api_router
from app.core.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    setup_tracing()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=f"{settings.service_name}",
    description="Tenant Service for Parqueaderos SaaS",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
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
    return {"status": "healthy", "service": settings.service_name}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Tenant Service", "version": "0.1.0"}