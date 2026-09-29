"""Models endpoint with RBAC authorization."""

from fastapi import APIRouter, Depends
from argus.schemas.api import ModelsResponse
from argus.registry.model_registry import model_registry
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal

router = APIRouter()


@router.get("/models", response_model=ModelsResponse, tags=["models"])
async def get_models(
    user: UserPrincipal = Depends(require_permission("read:models"))
):
    """Get list of models, protocol status, decision thresholds, and provenance with RBAC enforcement."""
    models_list = model_registry.get_model_info_list()
    return ModelsResponse(models=models_list)
