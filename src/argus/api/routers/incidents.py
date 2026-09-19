from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from argus.schemas.incident import Incident, IncidentStatus, TimelineEvent
from argus.schemas.api import APIResponse
from argus.security.auth import get_current_user
from argus.schemas.security import TokenPayload
from argus.services.incident_service import incident_service, InvalidTransitionError

router = APIRouter()

class StatusUpdateRequest(BaseModel):
    status: IncidentStatus
    actor: str = "system"

class ApprovalRequest(BaseModel):
    reason: str
    actor: str

@router.post("/", response_model=APIResponse[Incident], status_code=status.HTTP_201_CREATED)
async def create_incident(incident: Incident, user: TokenPayload = Depends(get_current_user)):
    """Create a new incident."""
    try:
        created = incident_service.create_incident(incident)
        return APIResponse(data=created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=APIResponse[List[Incident]])
async def list_incidents(user: TokenPayload = Depends(get_current_user)):
    """List all incidents."""
    return APIResponse(data=incident_service.list_incidents())

@router.get("/{incident_id}", response_model=APIResponse[Incident])
async def get_incident(incident_id: str, user: TokenPayload = Depends(get_current_user)):
    """Get a specific incident."""
    incident = incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return APIResponse(data=incident)

@router.patch("/{incident_id}/status", response_model=APIResponse[Incident])
async def update_incident_status(
    incident_id: str, 
    update_req: StatusUpdateRequest, 
    user: TokenPayload = Depends(get_current_user)
):
    """Transition an incident to a new status."""
    try:
        updated = incident_service.update_status(incident_id, update_req.status, update_req.actor)
        return APIResponse(data=updated)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{incident_id}/approve", response_model=APIResponse[Incident])
async def approve_incident(
    incident_id: str, 
    approval_req: ApprovalRequest, 
    user: TokenPayload = Depends(get_current_user)
):
    """Grant human approval for an incident response."""
    try:
        updated = incident_service.approve_incident(incident_id, approval_req.actor, approval_req.reason)
        return APIResponse(data=updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{incident_id}/timeline", response_model=APIResponse[List[TimelineEvent]])
async def get_incident_timeline(incident_id: str, user: TokenPayload = Depends(get_current_user)):
    """Get the audit timeline of an incident."""
    incident = incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return APIResponse(data=incident.timeline)
