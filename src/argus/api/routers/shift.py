"""Domain shift evaluation endpoint with RBAC and input bounds validation."""

from fastapi import APIRouter, Query, HTTPException, status, Depends
from structlog import get_logger

from argus.schemas.api import ShiftResponse
from argus.data.manager import data_manager, ALLOWED_DOMAINS
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal

logger = get_logger("argus.api.shift")

router = APIRouter()


@router.get("/shift", response_model=ShiftResponse, tags=["shift"])
async def get_domain_shift(
    domain: str = Query("nfton", description="Target domain: nfton or iec104"),
    window_size: int = Query(1000, ge=10, le=50000, description="Rolling window size for statistical shift testing"),
    user: UserPrincipal = Depends(require_permission("read:telemetry"))
):
    """Calculate rolling KS statistic and PSI drift metrics against source domain reference."""
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid domain '{domain}'. Allowed domains: {sorted(ALLOWED_DOMAINS)}"
        )

    try:
        shift_res = data_manager.calculate_shift(target_domain=domain, window_size=window_size)
        return shift_res
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telemetry data for domain '{domain}' not found."
        )
    except Exception as ex:
        logger.error("shift_calculation_failed", domain=domain, error=str(ex), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain distribution shift computation failed."
        )
