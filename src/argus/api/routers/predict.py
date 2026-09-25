"""Prediction endpoint."""

from fastapi import APIRouter, HTTPException, status
from argus.schemas.api import PredictRequest, PredictResponse
from argus.registry.model_registry import model_registry

router = APIRouter()


@router.post("/predict", response_model=PredictResponse, tags=["predict"])
async def predict_flow(request: PredictRequest):
    """Predict attack probability and binary label for a network flow."""
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ke)
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error for model '{model_name}': {str(ex)}"
        )
