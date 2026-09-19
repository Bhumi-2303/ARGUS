from argus.policy.models import PolicyContext, DecisionOutput, ActionType
from argus.policy.rules import evaluate_risk, requires_approval
from argus.policy.config import load_policy_config

class PolicyEngine:
    """Deterministic security policy engine."""
    
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.config = load_policy_config()

    def evaluate(self, context: PolicyContext) -> DecisionOutput:
        # Fail-safe logic: If context is invalid/missing, default to safe monitoring
        if not context.risk_tier or context.risk_tier == "unknown":
            return DecisionOutput(
                action=ActionType.MONITOR,
                risk_tier="unknown",
                policy_id="POL-FAILSAFE",
                policy_version=self.version,
                requires_human_approval=False,
                reason_codes=["fallback_due_to_missing_context"],
                evidence_refs=[]
            )

        # Execute deterministic risk policy
        action_str = evaluate_risk(context)
        action = ActionType(action_str)
        req_approval = requires_approval(action_str, context.criticality)
        
        # Determine policy ID based on action
        policy_id = f"POL-{action_str}"

        return DecisionOutput(
            action=action,
            risk_tier=context.risk_tier,
            policy_id=policy_id,
            policy_version=self.version,
            requires_human_approval=req_approval,
            reason_codes=[f"matched_{action_str.lower()}_rules"],
            evidence_refs=[]
        )
