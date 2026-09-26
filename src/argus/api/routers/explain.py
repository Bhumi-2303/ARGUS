"""SHAP explainability endpoint."""

from fastapi import APIRouter, HTTPException, status
from argus.schemas.api import ExplainRequest, ExplainResponse
from argus.registry.model_registry import model_registry

router = APIRouter()


@router.post("/explain", response_model=ExplainResponse, tags=["explain"])
async def explain_flow(request: ExplainRequest):
    """Compute SHAP feature attribution values for a target flow and model."""
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
    except KeyError as ke:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ke)
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP explanation failed for model '{model_name}': {str(ex)}"
        )
