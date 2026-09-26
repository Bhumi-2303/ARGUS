"""Domains endpoint."""

from fastapi import APIRouter
from argus.schemas.api import DomainsResponse
from argus.data.manager import data_manager

router = APIRouter()


@router.get("/domains", response_model=DomainsResponse, tags=["domains"])
async def get_domains():
    """Get available network telemetry domains and sample sizes."""
    domains_list = data_manager.get_domains()
    return DomainsResponse(domains=domains_list)
