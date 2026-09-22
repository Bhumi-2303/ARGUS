from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    MONITOR = "MONITOR"
    INVESTIGATE = "INVESTIGATE"
    ESCALATE = "ESCALATE"
    ISOLATE = "ISOLATE"

class PolicyContext(BaseModel):
    risk_tier: str = Field(..., pattern="^(critical|high|medium|low|unknown)$")
    asset_type: str = "generic"
    criticality: int = Field(1, ge=1, le=5)
    confidence: str = Field("low", pattern="^(high|medium|low)$")
    attack_category: str = "Benign"
    detector_prediction: int = Field(0, ge=0, le=1)
    operational_constraints: Dict[str, Any] = {}

class DecisionOutput(BaseModel):
    action: ActionType
    risk_tier: str
    policy_id: str
    policy_version: str
    requires_human_approval: bool
    reason_codes: List[str]
    evidence_refs: List[str]
