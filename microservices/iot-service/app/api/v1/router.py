"""API v1 router — IoT Service."""
from fastapi import APIRouter

from app.api.v1.endpoints import gates, devices

router = APIRouter()

router.include_router(gates.router)
router.include_router(devices.router)