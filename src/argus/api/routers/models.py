"""Models endpoint."""

from fastapi import APIRouter
from argus.schemas.api import ModelsResponse
from argus.registry.model_registry import model_registry

router = APIRouter()


@router.get("/models", response_model=ModelsResponse, tags=["models"])
async def get_models():
    """Get list of models, protocol status, decision thresholds, and provenance."""
    models_list = model_registry.get_model_info_list()
    return ModelsResponse(models=models_list)
