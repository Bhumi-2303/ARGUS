from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ActionType(str, Enum):
    MONITOR = "MONITOR"
    INVESTIGATE = "INVESTIGATE"
    ESCALATE = "ESCALATE"
    ISOLATE = "ISOLATE"

class PolicyContext(BaseModel):
    risk_tier: str
    asset_type: str = "generic"
    criticality: int = 1
    confidence: str = "low"
    attack_category: str = "Benign"
    detector_prediction: int = 0
    operational_constraints: Dict[str, Any] = {}

class DecisionOutput(BaseModel):
    action: ActionType
    risk_tier: str
    policy_id: str
    policy_version: str
    requires_human_approval: bool
    reason_codes: List[str]
    evidence_refs: List[str]
