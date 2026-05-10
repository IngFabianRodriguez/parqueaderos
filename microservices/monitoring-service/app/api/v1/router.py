"""API v1 router — aggregates all endpoint routers."""
from fastapi import APIRouter
from app.api.v1.endpoints import health, alerts, maintenance, metrics, sla

router = APIRouter()

router.include_router(health.router)
router.include_router(alerts.router)
router.include_router(maintenance.router)
router.include_router(metrics.router)
router.include_router(sla.router)