from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    ESCALATED = "ESCALATED"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOT_REQUIRED = "NOT_REQUIRED"

class TimelineEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    actor: str = "system"
    details: str = ""

class Incident(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: IncidentStatus = IncidentStatus.DETECTED
    severity: str
    asset: str
    asset_criticality: Optional[int] = None
    risk_score: Optional[float] = None
    risk_tier: Optional[str] = None
    
    # Context summaries
    detector_summary: str = ""
    knowledge_summary: str = ""
    
    # Decisions & Responses
    decision: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    assigned_to: Optional[str] = None
    
    # Approval logic
    approval_required: bool = False
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_reason: Optional[str] = None
    
    timeline: List[TimelineEvent] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    model_provenance: Optional[Dict[str, Any]] = None

    def add_timeline_event(self, action: str, details: str = "", actor: str = "system"):
        self.timeline.append(TimelineEvent(action=action, details=details, actor=actor))
        self.updated_at = datetime.utcnow()
