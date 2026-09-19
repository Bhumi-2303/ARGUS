from argus.policy.schemas import PolicyContext, ActionType

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
