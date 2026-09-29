"""Domain onboarding simulation endpoint with RBAC and error masking."""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from structlog import get_logger

from argus.schemas.api import OnboardRequest, OnboardResponse
from argus.data.manager import data_manager
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal
from argus.security.audit import AuditLogger, SecurityAuditEvent

logger = get_logger("argus.api.onboard")

router = APIRouter()


@router.post("/onboard", response_model=OnboardResponse, tags=["onboard"])
async def onboard_domain(
    request: OnboardRequest,
    req: Request,
    user: UserPrincipal = Depends(require_permission("run:onboarding"))
):
    """Simulate domain onboarding with CORAL alignment and threshold calibration."""
    try:
        res = data_manager.simulate_onboard(
            target_domain=request.target_domain,
            adapt_size=request.adaptation_window_size,
            calib_size=request.calibration_window_size,
            test_size=request.test_window_size
        )

        AuditLogger.log_event(SecurityAuditEvent(
            actor_id=user.sub,
            action="SIMULATE_DOMAIN_ONBOARDING",
            resource=f"/onboard/{request.target_domain}",
            outcome="SUCCESS",
            source_ip=req.client.host if req.client else None
        ))

        return OnboardResponse(
            target_domain=res["target_domain"],
            demo_scale=True,
            coral_fitted=res["coral_fitted"],
            selected_threshold=res["selected_threshold"],
            metrics=res["metrics"],
            evaluated_test_size=res["evaluated_test_size"]
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target domain: '{request.target_domain}'."
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telemetry data for domain '{request.target_domain}' not found."
        )
    except Exception as ex:
        logger.error("onboarding_simulation_failed", error=str(ex), domain=request.target_domain)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain onboarding simulation failed."
        )
