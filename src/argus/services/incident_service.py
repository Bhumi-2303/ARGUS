from typing import Dict, List, Optional
from datetime import datetime
from argus.schemas.incident import Incident, IncidentStatus, ApprovalStatus

class InvalidTransitionError(Exception):
    pass

class IncidentService:
    def __init__(self):
        # Simplest maintainable implementation: In-memory store
        self._incidents: Dict[str, Incident] = {}

    def create_incident(self, incident: Incident) -> Incident:
        if incident.incident_id in self._incidents:
            raise ValueError(f"Incident {incident.incident_id} already exists")
        
        incident.add_timeline_event("incident_created", "Incident created from detection event.")
        self._incidents[incident.incident_id] = incident
        return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        return self._incidents.get(incident_id)

    def list_incidents(self) -> List[Incident]:
        return list(self._incidents.values())

    def update_status(self, incident_id: str, new_status: IncidentStatus, actor: str = "system") -> Incident:
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        current = incident.status
        
        # Valid explicit transitions
        valid_transitions = {
            IncidentStatus.DETECTED: [IncidentStatus.TRIAGED, IncidentStatus.CLOSED],
            IncidentStatus.TRIAGED: [IncidentStatus.INVESTIGATING, IncidentStatus.ESCALATED, IncidentStatus.CLOSED],
            IncidentStatus.INVESTIGATING: [IncidentStatus.CONTAINED, IncidentStatus.RESOLVED, IncidentStatus.ESCALATED],
            IncidentStatus.ESCALATED: [IncidentStatus.INVESTIGATING, IncidentStatus.CONTAINED, IncidentStatus.CLOSED],
            IncidentStatus.CONTAINED: [IncidentStatus.RESOLVED],
            IncidentStatus.RESOLVED: [IncidentStatus.CLOSED],
            IncidentStatus.CLOSED: []
        }

        if new_status not in valid_transitions.get(current, []):
            raise InvalidTransitionError(f"Cannot transition from {current} to {new_status}")

        incident.status = new_status
        incident.add_timeline_event("status_changed", f"Status changed from {current.value} to {new_status.value}", actor=actor)
        return incident

    def approve_incident(self, incident_id: str, approver: str, reason: str) -> Incident:
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        if not incident.approval_required:
            raise ValueError("Incident does not require approval")
            
        incident.approval_status = ApprovalStatus.APPROVED
        incident.approved_by = approver
        incident.approved_at = datetime.utcnow()
        incident.approval_reason = reason
        
        incident.add_timeline_event("approval_granted", f"Action approved by {approver}: {reason}", actor=approver)
        return incident

# Global singleton for lightweight runtime
incident_service = IncidentService()
