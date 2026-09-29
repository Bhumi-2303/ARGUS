"""Incident management router with explicit RBAC and human approval auditing."""

from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status, Request
from structlog import get_logger

from argus.schemas.incident import Incident, IncidentStatus, TimelineEvent
from argus.schemas.api import APIResponse
from argus.security.audit import AuditLogger, SecurityAuditEvent
from argus.services.incident_service import incident_service, InvalidTransitionError
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal

logger = get_logger("argus.api.incidents")

router = APIRouter()


class StatusUpdateRequest(BaseModel):
    status: IncidentStatus
    actor: Optional[str] = None


class ApprovalRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=1000, description="Audit justification for incident approval")


@router.post("/", response_model=APIResponse[Incident], status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident: Incident,
    user: UserPrincipal = Depends(require_permission("write:incidents"))
):
    """Create a new security incident."""
    try:
        created = incident_service.create_incident(incident)
        return APIResponse(data=created)
    except ValueError as e:
        logger.warning("create_incident_failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident definition.")


@router.get("/", response_model=APIResponse[List[Incident]])
async def list_incidents(
    user: UserPrincipal = Depends(require_permission("read:incidents"))
):
    """List all incidents."""
    return APIResponse(data=incident_service.list_incidents())


@router.get("/{incident_id}", response_model=APIResponse[Incident])
async def get_incident(
    incident_id: str,
    user: UserPrincipal = Depends(require_permission("read:incidents"))
):
    """Get a specific incident by ID."""
    incident = incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found.")
    return APIResponse(data=incident)


@router.patch("/{incident_id}/status", response_model=APIResponse[Incident])
async def update_incident_status(
    incident_id: str,
    update_req: StatusUpdateRequest,
    user: UserPrincipal = Depends(require_permission("write:incidents"))
):
    """Transition an incident to a new lifecycle status."""
    actor = user.sub
    try:
        updated = incident_service.update_status(incident_id, update_req.status, actor)
        return APIResponse(data=updated)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found.")
    except InvalidTransitionError as ite:
        logger.warning("invalid_incident_transition", incident_id=incident_id, error=str(ite))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status transition for incident.")


@router.post("/{incident_id}/approve", response_model=APIResponse[Incident])
async def approve_incident(
    incident_id: str,
    approval_req: ApprovalRequest,
    request: Request,
    user: UserPrincipal = Depends(require_permission("approve:response"))
):
    """Grant authorized human approval for an incident response mitigation."""
    incident = incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found.")
    if not incident.approval_required:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incident does not require approval.")

    actor_id = user.sub
    try:
        updated = incident_service.approve_incident(incident_id, actor_id, approval_req.reason)

        # Durably record high-impact approval action with verified caller identity
        AuditLogger.log_event(SecurityAuditEvent(
            actor_id=actor_id,
            actor_type="human",
            action="RESPONSE_APPROVED",
            resource="incident",
            resource_id=incident_id,
            outcome="SUCCESS",
            reason=approval_req.reason,
            source_ip=request.client.host if request.client else None,
            incident_id=incident_id,
            authorization_context={
                "sub": user.sub,
                "roles": user.roles,
                "permissions": list(user.permissions)
            }
        ))

        return APIResponse(data=updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{incident_id}/timeline", response_model=APIResponse[List[TimelineEvent]])
async def get_incident_timeline(
    incident_id: str,
    user: UserPrincipal = Depends(require_permission("read:incidents"))
):
    """Get the immutable audit timeline of an incident."""
    incident = incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found.")
    return APIResponse(data=incident.timeline)
