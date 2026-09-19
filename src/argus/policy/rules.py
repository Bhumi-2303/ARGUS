from argus.policy.models import PolicyContext, ActionType

def evaluate_risk(context: PolicyContext) -> str:
    """Evaluate risk context to determine deterministic action tier."""
    if context.risk_tier == "critical":
        if context.criticality >= 3:
            return "ISOLATE"
        return "ESCALATE"
        
    if context.risk_tier == "high":
        if context.criticality >= 3 and context.confidence == "high":
            return "ISOLATE"
        return "ESCALATE"
        
    if context.risk_tier == "medium":
        if context.criticality >= 5 or context.confidence == "high":
            return "INVESTIGATE"
            
    # CRITICAL RULE: detector pred=1 does NOT override a low risk tier.
    return "MONITOR"

def requires_approval(action: str, criticality: int) -> bool:
    """Determine if human approval is required before execution."""
    # Critical rule: High impact actions require human approval safely.
    if action in ["ISOLATE", "ESCALATE"]:
        return True
    return False
