"""Health check endpoint."""

import time
from datetime import datetime, timezone
from fastapi import APIRouter
from argus.schemas.api import HealthResponse
from argus.registry.model_registry import model_registry

router = APIRouter()
START_TIME = time.time()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def get_health():
    """Get system operational health status."""
    uptime = time.time() - START_TIME
    return HealthResponse(
        status="healthy",
        uptime_seconds=round(uptime, 2),
        timestamp=datetime.now(timezone.utc).isoformat(),
        models_loaded=model_registry.get_status_dict()
    )
