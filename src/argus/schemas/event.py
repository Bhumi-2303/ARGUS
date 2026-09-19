"""Canonical ARGUS Security Event Schema and Contracts."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# Provenance
# ------------------------------------------------------------------
class Provenance(BaseModel):
    """Tracks model and experiment provenance."""
    model_id: Optional[str] = Field(None, description="Identifier of the model used")
    model_version: Optional[str] = Field(None, description="Version of the model")
    feature_schema_version: Optional[str] = Field(None, description="Version of the feature schema")
    adaptation_method: Optional[str] = Field(None, description="Domain adaptation method used, e.g., CORAL")
    threshold: Optional[float] = Field(None, description="Detection threshold used")
    training_dataset: Optional[str] = Field(None, description="Dataset used for training")
    training_date: Optional[str] = Field(None, description="Date the model was trained")
    calibration_version: Optional[str] = Field(None, description="Version of the calibration method")
    seed: Optional[int] = Field(None, description="Random seed used")
    artifact_reference: Optional[str] = Field(None, description="Path or URI to the model artifact")
    experiment_version: Optional[str] = Field(None, description="Version of the experiment")


# ------------------------------------------------------------------
# Stage Contracts
# ------------------------------------------------------------------
class DetectorContract(BaseModel):
    """Contract for the Detector stage."""
    is_anomaly: bool = Field(..., description="Whether an anomaly was detected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    threat_category: Optional[str] = Field(None, description="Category of the threat if known")
    scores: Dict[str, float] = Field(default_factory=dict, description="Raw scores from models")

class RiskContract(BaseModel):
    """Contract for the Risk Prediction stage."""
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Calculated risk score")
    severity: str = Field(..., description="Categorical risk severity (e.g., critical, high)")
    asset_priority: int = Field(..., description="Priority of the affected asset")
    impact_estimation: str = Field(..., description="Description of potential impact")

class KnowledgeContract(BaseModel):
    """Contract for the Knowledge Context stage."""
    mitre_techniques: List[str] = Field(default_factory=list, description="Associated MITRE techniques")
    cve_ids: List[str] = Field(default_factory=list, description="Associated CVEs")
    cisa_advisories: List[str] = Field(default_factory=list, description="Associated CISA advisories")
    recommended_mitigations: List[str] = Field(default_factory=list, description="Suggested mitigations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the knowledge provided")

class ExplainabilityContract(BaseModel):
    """Contract for the Explainability stage."""
    shap_values: Dict[str, float] = Field(default_factory=dict, description="SHAP values for features")
    top_features: List[str] = Field(default_factory=list, description="Top contributing features")
    human_readable_explanation: str = Field(..., description="Explanation intended for analysts")

class ReviewContract(BaseModel):
    """Contract for the Human-in-the-Loop Review stage."""
    reviewer_id: str = Field(..., description="ID of the human or AI reviewer")
    review_status: str = Field(..., description="Status of the review (e.g., approved, rejected, escalated)")
    comments: str = Field(..., description="Reviewer comments")

class PolicyContract(BaseModel):
    """Contract for the Policy Evaluation stage."""
    policy_id: str = Field(..., description="ID of the policy evaluated")
    action_allowed: bool = Field(..., description="Whether the proposed action is allowed")
    violations: List[str] = Field(default_factory=list, description="Any policy violations found")

class DecisionContract(BaseModel):
    """Contract for the Decision Support stage."""
    recommended_actions: List[str] = Field(default_factory=list, description="Actions to be taken")
    priority: int = Field(..., description="Priority of the actions")
    urgency: str = Field(..., description="Urgency level")
    approval_required: bool = Field(..., description="Whether hitl approval is required")

class ResponseContract(BaseModel):
    """Contract for the Response stage."""
    action_taken: str = Field(..., description="Action that was executed")
    success: bool = Field(..., description="Whether the execution was successful")
    execution_details: str = Field(..., description="Details of the execution")

class AuditContract(BaseModel):
    """Contract for the Audit stage."""
    audit_id: str = Field(..., description="Unique audit record identifier")
    timestamp: datetime = Field(..., description="Time of the audit log")
    log_entry: str = Field(..., description="Audit log entry")


# ------------------------------------------------------------------
# Canonical Event
# ------------------------------------------------------------------
class ArgusEvent(BaseModel):
    """Canonical Security Event containing explicit stage contracts."""
    schema_version: str = Field(default="1.0", description="Schema version")
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time the event was created")
    source: str = Field(..., description="Source system generating the event")
    domain: str = Field(..., description="Domain of the event (e.g., IT, OT)")
    asset: str = Field(..., description="Target asset")
    asset_criticality: Optional[int] = Field(None, description="Criticality of the asset")
    telemetry_reference: Optional[str] = Field(None, description="Reference to raw telemetry")
    
    provenance: Optional[Provenance] = Field(None, description="Model provenance information")
    
    detector: Optional[DetectorContract] = Field(None, description="Detector stage output")
    risk: Optional[RiskContract] = Field(None, description="Risk stage output")
    knowledge: Optional[KnowledgeContract] = Field(None, description="Knowledge stage output")
    explanation: Optional[ExplainabilityContract] = Field(None, description="Explainability stage output")
    review: Optional[ReviewContract] = Field(None, description="Review stage output")
    policy: Optional[PolicyContract] = Field(None, description="Policy evaluation output")
    decision: Optional[DecisionContract] = Field(None, description="Decision stage output")
    response: Optional[ResponseContract] = Field(None, description="Response stage output")
    audit: Optional[AuditContract] = Field(None, description="Audit log output")
    
    class Config:
        validate_assignment = True
        extra = "forbid"
