"""API v1 router — ANPR Service."""
from fastapi import APIRouter

from app.api.v1.endpoints.anpr import router as anpr_router

router = APIRouter()
router.include_router(anpr_router)