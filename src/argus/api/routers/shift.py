"""Domain shift evaluation endpoint."""

from fastapi import APIRouter, Query, HTTPException, status
from argus.schemas.api import ShiftResponse
from argus.data.manager import data_manager

router = APIRouter()


@router.get("/shift", response_model=ShiftResponse, tags=["shift"])
async def get_domain_shift(
    domain: str = Query("nfton", description="Target domain: nfton or iec104"),
    window_size: int = Query(1000, description="Rolling window size for statistical shift testing")
):
    """Calculate rolling KS statistic and PSI drift metrics against source domain reference."""
    try:
        shift_res = data_manager.calculate_shift(target_domain=domain, window_size=window_size)
        return shift_res
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnfe)
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shift computation failed: {str(ex)}"
        )
