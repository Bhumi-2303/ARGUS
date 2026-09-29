"""Data models and schemas for the Decision Support Agent."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import datetime
import uuid

# Re-use or mock internal structures for completeness
# (Assuming RiskEvent and KnowledgeContext exist somewhere in argus.schemas, 
# but for this agent we define the input contract we expect)

class RiskEventInput(BaseModel):
    """The RiskEvent payload received from the MessageBus."""
    source_event_id: str
    risk_score: Optional[int] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None
    asset_priority: Optional[str] = None
    impact_estimation: Optional[Dict[str, Any]] = None
    reasoning: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class KnowledgeContextInput(BaseModel):
    """The KnowledgeContext payload received from the MessageBus."""
    affected_assets: List[str] = Field(default_factory=list)
    asset_types: Dict[str, str] = Field(default_factory=dict)
    known_vulnerabilities: List[str] = Field(default_factory=list)
    related_incidents: List[str] = Field(default_factory=list)

class DecisionAnalysisInput(BaseModel):
    """Composite input containing both Risk and Knowledge events."""
    risk_event: RiskEventInput
    knowledge_event: KnowledgeContextInput

class Playbook(BaseModel):
    """Represents a Standard Operating Procedure (SOP) or Playbook."""
    playbook_id: str
    name: str
    description: str
    applicable_assets: List[str] = Field(default_factory=list)

class Recommendation(BaseModel):
    """An individual actionable recommendation."""
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str  # e.g., "isolate_network", "patch_system", "block_ip"
    description: str
    target_assets: List[str]
    playbook_reference: Optional[str] = None
    priority: int = 0  # 1 (Highest) to 5 (Lowest)
    urgency: str = "medium"  # low, medium, high, immediate
    expected_downtime_hours: float = 0.0

class ActionPlan(BaseModel):
    """A prioritized collection of recommendations."""
    recommendations: List[Recommendation] = Field(default_factory=list)
    primary_objective: str

class ImpactAssessment(BaseModel):
    """Estimated operational impact of executing the action plan."""
    total_expected_downtime_hours: float
    services_disrupted: List[str]
    risk_reduction_estimate: float # 0.0 to 1.0 multiplier

class ApprovalRequirement(BaseModel):
    """Details regarding Human-in-the-Loop (HITL) approval."""
    approval_required: bool
    approver_role: Optional[str] = None
    justification: str

class DecisionEvent(BaseModel):
    """The final DECISION_EVENT payload to be published."""
    source_event_id: str
    recommended_actions: List[Recommendation]
    priority: int
    urgency: str
    confidence: Optional[float] = None
    estimated_impact: ImpactAssessment
    approval_required: bool
    execution_plan: str
    reasoning: str
