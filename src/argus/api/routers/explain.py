"""SHAP explainability endpoint with RBAC authorization and error masking."""

from fastapi import APIRouter, HTTPException, status, Depends
from structlog import get_logger

from argus.schemas.api import ExplainRequest, ExplainResponse
from argus.registry.model_registry import model_registry
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal

logger = get_logger("argus.api.explain")

router = APIRouter()


@router.post("/explain", response_model=ExplainResponse, tags=["explain"])
async def explain_flow(
    request: ExplainRequest,
    user: UserPrincipal = Depends(require_permission("run:explanation"))
):
    """Compute SHAP feature attribution values for a target flow and model with RBAC enforcement."""
    features_dict = request.features.model_dump()
    model_name = request.model_name

    try:
        base_val, shap_dict, top_feat, top_impact = model_registry.explain(model_name, features_dict)
        return ExplainResponse(
            model_name=model_name,
            base_value=round(base_val, 6),
            shap_values={k: round(v, 6) for k, v in shap_dict.items()},
            feature_values=features_dict,
            top_feature=top_feat,
            top_feature_impact=round(top_impact, 6)
        )
    except KeyError:
        logger.warning("explain_unknown_model", model=model_name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{model_name}' is not configured for SHAP feature attribution."
        )
    except Exception as ex:
        logger.error("explain_calculation_failed", model=model_name, error=str(ex), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP feature explanation failed for model '{model_name}'."
        )
