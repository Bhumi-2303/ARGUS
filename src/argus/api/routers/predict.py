"""Prediction endpoint with RBAC authorization and error masking."""

from fastapi import APIRouter, HTTPException, status, Depends
from structlog import get_logger

from argus.schemas.api import PredictRequest, PredictResponse
from argus.registry.model_registry import model_registry
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal

logger = get_logger("argus.api.predict")

router = APIRouter()


@router.post("/predict", response_model=PredictResponse, tags=["predict"])
async def predict_flow(
    request: PredictRequest,
    user: UserPrincipal = Depends(require_permission("run:prediction"))
):
    """Predict attack probability and binary label for a network flow with RBAC enforcement."""
    features_dict = request.features.model_dump()
    model_name = request.model_name

    try:
        prob, label, threshold = model_registry.predict(model_name, features_dict)
        return PredictResponse(
            model_name=model_name,
            probability=round(prob, 6),
            prediction=label,
            threshold=threshold,
            features=features_dict
        )
    except KeyError as ke:
        logger.warning("predict_unknown_model_or_feature", model=model_name, error=str(ke))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model '{model_name}' or invalid feature structure."
        )
    except NotImplementedError as nie:
        # Expected response for unverified DANN model
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(nie)
        )
    except Exception as ex:
        logger.error("inference_execution_failed", model=model_name, error=str(ex), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed for model '{model_name}'."
        )
