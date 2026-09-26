import re

with open("src/argus/services/decision_agent/main.py", "r") as f:
    content = f.read()

# Replace the naive decision logic with PolicyEngine
import_str = "from argus.policy.policy_engine import PolicyEngine\nfrom argus.policy.models import PolicyContext\n"
if "PolicyEngine" not in content:
    content = content.replace("from argus.services.common.base_agent import BaseAgent", import_str + "from argus.services.common.base_agent import BaseAgent")

old_logic = """        action = "INVESTIGATE" if pred == 1 else "IGNORE"

        return AgentMessage(
            message_id=message.message_id + "-resp",
            event_id=message.event_id,
            sender=self.name,
            receiver=message.sender,
            message_type="response",
            payload={
                "action": action,
                "explanation_text": exp_text,
                "llm_fallback_used": fallback_used
            },
            confidence=max(0.1, conf),
            evidence={"explanation": exp_text},
            trace_id=message.trace_id
        )"""

new_logic = """        # Use the deterministic Policy Engine
        engine = PolicyEngine()
        context = PolicyContext(
            risk_tier=risk_tier if risk_tier else "unknown",
            asset_type=payload.get("asset_type", "generic"),
            criticality=payload.get("asset_criticality", 1),
            confidence="high" if conf > 0.8 else "low",
            detector_prediction=pred if pred is not None else 0
        )
        decision = engine.evaluate(context)

        return AgentMessage(
            message_id=message.message_id + "-resp",
            event_id=message.event_id,
            sender=self.name,
            receiver=message.sender,
            message_type="response",
            payload={
                "action": decision.action.value,
                "policy_id": decision.policy_id,
                "requires_human_approval": decision.requires_human_approval,
                "explanation_text": exp_text,
                "llm_fallback_used": fallback_used
            },
            confidence=max(0.1, conf),
            evidence={"explanation": exp_text, "policy_id": decision.policy_id},
            trace_id=message.trace_id
        )"""

content = content.replace(old_logic, new_logic)

with open("src/argus/services/decision_agent/main.py", "w") as f:
    f.write(content)
