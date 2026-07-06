"""Internal data models and schemas for Risk Prediction Agent."""
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# Inputs
# ------------------------------------------------------------------

class ThreatAnalysisResult(BaseModel):
    """Schema representing the input from the Threat Analysis Agent."""
    source_event_id: str
    threat_level: str
    confidence: float
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    model_version: str

class KnowledgeContext(BaseModel):
    """Schema representing the input from the Knowledge Agent."""
    affected_assets: List[str] = Field(default_factory=list)
    asset_types: Dict[str, str] = Field(default_factory=dict)
    known_vulnerabilities: List[str] = Field(default_factory=list)
    related_incidents: List[str] = Field(default_factory=list)

class RiskAnalysisInput(BaseModel):
    """Combined input schema for the Risk Prediction pipeline."""
    threat_event: ThreatAnalysisResult
    knowledge_event: KnowledgeContext


# ------------------------------------------------------------------
# Intermediate Results
# ------------------------------------------------------------------

class AssetPriority(StrEnum):
    """Asset priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CriticalityResult(BaseModel):
    """Output from the Critical Asset Analyzer tool."""
    asset_priority: AssetPriority
    critical_assets: List[str]
    reasoning: str

class ImpactSeverity(StrEnum):
    """Operational impact severity levels."""
    CATASTROPHIC = "catastrophic"
    SEVERE = "severe"
    MODERATE = "moderate"
    MINOR = "minor"
    NONE = "none"

class ImpactResult(BaseModel):
    """Output from the Impact Estimator tool."""
    severity: ImpactSeverity
    estimated_downtime_hours: float
    impacted_services: List[str]
    reasoning: str

class EscalationResult(BaseModel):
    """Output from the Trend Analyzer tool."""
    escalation_factor: float = Field(..., description="Multiplier for risk score based on trends")
    historical_context: str
    reasoning: str

class RiskScoreResult(BaseModel):
    """Output from the Risk Scorer tool."""
    score: int = Field(..., description="Numeric risk score 0-100")
    severity: str = Field(..., description="Categorical risk severity")
    reasoning: str


# ------------------------------------------------------------------
# Final Output
# ------------------------------------------------------------------

class RiskEvent(BaseModel):
    """Final output schema to be published as a RISK_EVENT."""
    source_event_id: str
    risk_score: int
    severity: str
    confidence: float
    asset_priority: AssetPriority
    impact_estimation: ImpactResult
    reasoning: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
