"""Health check router."""
from fastapi import APIRouter
from argus.schemas.health import SystemHealth

router = APIRouter()

@router.get("/live", response_model=SystemHealth)
async def health_live():
    """Liveness check endpoint."""
    return SystemHealth(status="healthy", uptime=100.0, timestamp="2025-01-01T00:00:00Z")

@router.get("/ready", response_model=SystemHealth)
async def health_ready():
    """Readiness check endpoint."""
    return SystemHealth(status="healthy", uptime=100.0, timestamp="2025-01-01T00:00:00Z")
