"""Demo-scale onboarding endpoint."""

from fastapi import APIRouter, HTTPException, status
from argus.schemas.api import OnboardRequest, OnboardResponse
from argus.data.manager import data_manager

router = APIRouter()


@router.post("/onboard", response_model=OnboardResponse, tags=["onboard"])
async def onboard_domain(request: OnboardRequest):
    """Simulate demo-scale domain onboarding with CORAL alignment and calibration."""
    try:
        res = data_manager.simulate_onboard(
            target_domain=request.target_domain,
            adapt_size=request.adaptation_window_size,
            calib_size=request.calibration_window_size,
            test_size=request.test_window_size
        )
        return OnboardResponse(
            target_domain=res["target_domain"],
            demo_scale=True,  # ALWAYS True for demo onboarding response
            coral_fitted=res["coral_fitted"],
            selected_threshold=res["selected_threshold"],
            metrics=res["metrics"],
            evaluated_test_size=res["evaluated_test_size"]
        )
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnfe)
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Onboarding simulation failed: {str(ex)}"
        )
