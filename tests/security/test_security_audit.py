import pytest
from pydantic import ValidationError
from argus.core.events import ArgusEvent, DetectorContract, RiskContract
from argus.policy.models import PolicyContext, ActionType
from argus.policy.policy_engine import PolicyEngine
from argus.schemas.incident import Incident, IncidentStatus
from argus.services.decision_agent.main import DecisionAgent
from argus.services.common.schemas import AgentMessage

# --- 1. Malformed Canonical Event / Validation ---

def test_malformed_canonical_event():
    with pytest.raises(ValidationError):
        ArgusEvent(event_id=123, source="test") # event_id should be string, domain/asset missing

def test_invalid_probability():
    with pytest.raises(ValidationError):
        DetectorContract(is_anomaly=True, confidence=1.5, scores={})

def test_invalid_criticality():
    with pytest.raises(ValidationError):
        PolicyContext(risk_tier="high", criticality=10) # max 5

def test_invalid_risk_tier():
    with pytest.raises(ValidationError):
        PolicyContext(risk_tier="super_critical", criticality=3)

# --- 2. Policy Engine Safety (LLM Boundary) ---

def test_policy_ignores_malicious_llm():
    engine = PolicyEngine()
    # Even if LLM recommended "DO_NOT_ISOLATE" or something weird,
    # the policy context only takes specific arguments.
    # A low risk should result in MONITOR.
    context = PolicyContext(risk_tier="low", criticality=1)
    decision = engine.evaluate(context)
    assert decision.action == ActionType.MONITOR

def test_critical_asset_requires_approval():
    engine = PolicyEngine()
    # High risk, high criticality -> ISOLATE -> requires approval
    context = PolicyContext(risk_tier="critical", criticality=5)
    decision = engine.evaluate(context)
    assert decision.action == ActionType.ISOLATE
    assert decision.requires_human_approval is True

def test_policy_fails_safe_on_unknown():
    engine = PolicyEngine()
    context = PolicyContext(risk_tier="unknown", criticality=1)
    decision = engine.evaluate(context)
    assert decision.action == ActionType.MONITOR
    assert decision.requires_human_approval is False
    assert "fallback_due_to_missing_context" in decision.reason_codes

# --- 3. Incident Transitions ---

def test_incident_invalid_transition():
    from argus.services.incident_service import incident_service, InvalidTransitionError
    inc = incident_service.create_incident(Incident(title="Test", description="Test", severity="low", affected_assets=[], event_id="E123", asset="Pump1"))
    with pytest.raises(InvalidTransitionError):
        # Cannot go straight from NEW to RESOLVED without INVESTIGATING
        incident_service.update_status(inc.incident_id, IncidentStatus.RESOLVED, "system")

