"""FastAPI application for monitoring-service."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.tracing import setup_tracing
from app.config import get_settings

settings = get_settings()

_DEBUG = settings.SERVICE_NAME  # any truthy check


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    yield


app = FastAPI(
    title="monitoring-service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — in production, restrict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenTelemetry tracing
setup_tracing(app)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": str(exc),
            "trace_id": request.headers.get("X-Trace-ID", "unknown"),
        },
    )

# Include all v1 routes
app.include_router(v1_router, prefix="/api/v1")


# Root health — mirrors the individual liveness probe
@app.get("/health")
async def root_health():
    return {"status": "ok", "service": "monitoring-service", "version": "1.0.0"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}