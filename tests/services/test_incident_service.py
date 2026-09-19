import pytest
from argus.schemas.incident import Incident, IncidentStatus, ApprovalStatus
from argus.services.incident_service import IncidentService, InvalidTransitionError
from pydantic import ValidationError

def test_valid_lifecycle():
    service = IncidentService()
    incident = Incident(event_id="evt-1", severity="high", asset="PLC-1")
    
    # Creation
    created = service.create_incident(incident)
    assert created.status == IncidentStatus.DETECTED
    assert len(created.timeline) == 1
    
    # Transition to TRIAGED
    updated = service.update_status(created.incident_id, IncidentStatus.TRIAGED)
    assert updated.status == IncidentStatus.TRIAGED
    assert len(updated.timeline) == 2

    # Transition to INVESTIGATING
    updated = service.update_status(created.incident_id, IncidentStatus.INVESTIGATING)
    assert updated.status == IncidentStatus.INVESTIGATING

def test_invalid_transition():
    service = IncidentService()
    incident = Incident(event_id="evt-1", severity="high", asset="PLC-1")
    created = service.create_incident(incident)
    
    # Cannot jump from DETECTED directly to CONTAINED
    with pytest.raises(InvalidTransitionError):
        service.update_status(created.incident_id, IncidentStatus.CONTAINED)

def test_duplicate_incident():
    service = IncidentService()
    incident = Incident(incident_id="dup-1", event_id="evt-1", severity="high", asset="PLC-1")
    service.create_incident(incident)
    
    with pytest.raises(ValueError, match="already exists"):
        service.create_incident(incident)

def test_missing_event():
    with pytest.raises(ValidationError):
        # Missing event_id, severity, asset
        Incident()

def test_approval_requirement():
    service = IncidentService()
    incident = Incident(event_id="evt-1", severity="critical", asset="PLC-1", approval_required=True)
    created = service.create_incident(incident)
    
    assert created.approval_status == ApprovalStatus.NOT_REQUIRED # Wait, defaults to NOT_REQUIRED, let's check schema.
    # Ah, the schema defaults to NOT_REQUIRED. 
    created.approval_status = ApprovalStatus.PENDING # Usually set prior to asking for approval
    
    approved = service.approve_incident(created.incident_id, "admin", "Looks safe")
    assert approved.approval_status == ApprovalStatus.APPROVED
    assert approved.approved_by == "admin"
    assert "approval_granted" in [t.action for t in approved.timeline]

def test_critical_incident():
    service = IncidentService()
    incident = Incident(
        event_id="evt-crit", 
        severity="critical", 
        asset="SCADA-01", 
        asset_criticality=5,
        risk_tier="critical"
    )
    created = service.create_incident(incident)
    assert created.risk_tier == "critical"
    
def test_incident_closure():
    service = IncidentService()
    incident = Incident(event_id="evt-1", severity="high", asset="PLC-1")
    created = service.create_incident(incident)
    
    # DETECTED -> CLOSED is valid
    closed = service.update_status(created.incident_id, IncidentStatus.CLOSED)
    assert closed.status == IncidentStatus.CLOSED
