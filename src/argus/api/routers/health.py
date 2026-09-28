"""Health, readiness, and liveness endpoints."""

import time
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
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


@router.get("/liveness", tags=["health"])
async def get_liveness():
    """Kubernetes/container liveness probe returning 200 if process is running."""
    return {"status": "alive"}


@router.get("/readiness", tags=["health"])
async def get_readiness():
    """Kubernetes/container readiness probe verifying loaded models and subsystem readiness."""
    status_dict = model_registry.get_status_dict()
    # Required production models must be True
    required = ["model_d2_coral", "model_d1_baseline", "xgb_adapted"]
    not_ready = [m for m in required if not status_dict.get(m)]
    if not_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Subsystems not ready: {not_ready}"
        )
    return {
        "status": "ready",
        "ready_models_count": sum(1 for v in status_dict.values() if v),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
