"""ANPR Service — FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_metrics

from app.api.v1.router import router as api_v1_router
from app.config import get_settings
from app.db.session import get_engine

settings = get_settings()

# Prometheus metrics
REQUEST_COUNT = Counter("anpr_service_requests_total", "Total requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("anpr_service_request_latency_seconds", "Request latency", ["endpoint"])

# Import models so metadata is available
from app.db.models import Base  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: startup / shutdown."""
    # Startup: create DB tables if needed
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # TODO: RF-016 — Start Kafka consumer for ANPR events
    # TODO: RF-017 — Initialize OCR engine (LPRNet ONNX runtime)
    #   # Example placeholder:
    #   # from app.services.ocr_engine import LPREngine
    #   # app.state.lpr_engine = LPREngine(settings.LPR_MODEL_PATH)
    #   # app.state.lpr_engine.load()

    yield

    # Shutdown
    await engine.dispose()
    # TODO: Close Kafka consumer


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


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record request count and latency."""
    import time

    method = request.method
    path = request.url.path

    if path == "/metrics":
        return await call_next(request)

    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    REQUEST_COUNT.labels(method=method, endpoint=path).inc()
    REQUEST_LATENCY.labels(endpoint=path).observe(duration)

    return response


@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.get("/ready")
async def ready():
    """Readiness probe — verify DB connectivity."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return JSONResponse({"status": "not ready", "database": str(e)}, status_code=503)


# OpenTelemetry tracing
from app.core.tracing import setup_tracing  # noqa: E402

setup_tracing(app, get_engine())

# Mount API routes
app.include_router(api_v1_router, prefix="/api/v1")


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics scrape endpoint."""
    from starlette.responses import Response

    generate_metrics()
    from prometheus_client import CONTENT_TYPE, generate_latest

    return Response(generate_latest(), media_type=CONTENT_TYPE)