from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from pydantic import BaseModel
from argus.schemas.incident import Incident, IncidentStatus, TimelineEvent
from argus.schemas.api import APIResponse
from argus.security.audit import AuditLogger, SecurityAuditEvent
from argus.services.incident_service import incident_service, InvalidTransitionError

router = APIRouter()

class StatusUpdateRequest(BaseModel):
    status: IncidentStatus
    actor: str = "system"

class ApprovalRequest(BaseModel):
    reason: str

@router.post("/", response_model=APIResponse[Incident], status_code=status.HTTP_201_CREATED)
async def create_incident(incident: Incident):
    """Create a new incident."""
    try:
        created = incident_service.create_incident(incident)
        return APIResponse(data=created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=APIResponse[List[Incident]])
async def list_incidents():
    """List all incidents."""
    return APIResponse(data=incident_service.list_incidents())

@router.get("/{incident_id}", response_model=APIResponse[Incident])
async def get_incident(incident_id: str):
    """Get a specific incident."""
    incident = incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return APIResponse(data=incident)

@router.patch("/{incident_id}/status", response_model=APIResponse[Incident])
async def update_incident_status(
    incident_id: str, 
    update_req: StatusUpdateRequest):
    """Transition an incident to a new status."""
    try:
        updated = incident_service.update_status(incident_id, update_req.status, "system")
        return APIResponse(data=updated)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{incident_id}/approve", response_model=APIResponse[Incident])
async def approve_incident(
    incident_id: str, 
    approval_req: ApprovalRequest, 
    request: Request):
    """Grant human approval for an incident response."""
    try:
        updated = incident_service.approve_incident(incident_id, "system", approval_req.reason)
        
        # High impact action audit event
        AuditLogger.log_event(SecurityAuditEvent(
            actor_id="system",
            actor_type="human",
            action="RESPONSE_APPROVED",
            resource="incident",
            resource_id=incident_id,
            outcome="SUCCESS",
            reason=approval_req.reason,
            source_ip=request.client.host if request.client else None,
            incident_id=incident_id
        ))
        
        return APIResponse(data=updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{incident_id}/timeline", response_model=APIResponse[List[TimelineEvent]])
async def get_incident_timeline(incident_id: str):
    """Get the audit timeline of an incident."""
    incident = incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return APIResponse(data=incident.timeline)
