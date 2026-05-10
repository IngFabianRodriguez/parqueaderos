"""API v1 router — aggregates all endpoint modules."""

from fastapi import APIRouter

from app.api.v1.endpoints.notifications import router as notifications_router


router = APIRouter()
router.include_router(notifications_router, prefix="/notifications")