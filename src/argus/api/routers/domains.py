"""Domains endpoint with RBAC authorization."""

from fastapi import APIRouter, Depends
from argus.schemas.api import DomainsResponse
from argus.data.manager import data_manager
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal

router = APIRouter()


@router.get("/domains", response_model=DomainsResponse, tags=["domains"])
async def get_domains(
    user: UserPrincipal = Depends(require_permission("read:domains"))
):
    """Get available network telemetry domains and sample sizes with RBAC enforcement."""
    domains_list = data_manager.get_domains()
    return DomainsResponse(domains=domains_list)
