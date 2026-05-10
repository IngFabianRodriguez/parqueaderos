"""ANPR Service — FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_v1_router
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: startup / shutdown."""
    yield


app = FastAPI(
    title="ANPR Service",
    description="Automatic Number Plate Recognition — Parqueaderos SaaS",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.get("/ready")
async def ready():
    """Readiness probe — verify DB connectivity."""
    try:
        from app.db.session import get_engine
        engine = get_engine()
        async with engine.connect() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return JSONResponse({"status": "not ready", "database": str(e)}, status_code=503)


# Mount API routes
app.include_router(api_v1_router, prefix="/api/v1")