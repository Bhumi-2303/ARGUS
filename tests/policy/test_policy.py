import pytest
from argus.policy.schemas import PolicyContext, ActionType
from argus.policy.engine import PolicyEngine

def test_detector_pred_1_does_not_force_investigate():
    engine = PolicyEngine()
    context = PolicyContext(
        risk_tier="low",
        criticality=5,
        confidence="high",
        attack_category="Uncertain",
        detector_prediction=1
    )
    decision = engine.evaluate(context)
    # The action must NOT be INVESTIGATE just because detector_prediction is 1
    assert decision.action == ActionType.MONITOR
    assert decision.policy_id != "POL-INVESTIGATE"

def test_critical_risk_high_criticality():
    engine = PolicyEngine()
    context = PolicyContext(
        risk_tier="critical",
        criticality=3,
        confidence="high",
        attack_category="Attack",
        detector_prediction=1
    )
    decision = engine.evaluate(context)
    assert decision.action == ActionType.ISOLATE
    assert decision.requires_human_approval is True

def test_critical_risk_low_criticality():
    engine = PolicyEngine()
    context = PolicyContext(
        risk_tier="critical",
        criticality=1,
        confidence="high",
        attack_category="Attack",
        detector_prediction=1
    )
    decision = engine.evaluate(context)
    assert decision.action == ActionType.ESCALATE
    assert decision.requires_human_approval is True

def test_high_risk_low_confidence():
    engine = PolicyEngine()
    context = PolicyContext(
        risk_tier="high",
        criticality=3,
        confidence="low",
        attack_category="Attack",
        detector_prediction=1
    )
    decision = engine.evaluate(context)
    assert decision.action == ActionType.ESCALATE
    assert decision.requires_human_approval is True

def test_medium_risk():
    engine = PolicyEngine()
    context = PolicyContext(
        risk_tier="medium",
        criticality=1,
        confidence="low",
        attack_category="Attack",
        detector_prediction=1
    )
    decision = engine.evaluate(context)
    assert decision.action == ActionType.MONITOR
    
    # But if confidence is high, it investigates
    context.confidence = "high"
    decision = engine.evaluate(context)
    assert decision.action == ActionType.INVESTIGATE
    assert decision.requires_human_approval is False

def test_failsafe_logic():
    engine = PolicyEngine()
    context = PolicyContext(
        risk_tier="", # Missing risk context
        criticality=5,
        detector_prediction=1
    )
    decision = engine.evaluate(context)
    assert decision.action == ActionType.MONITOR
    assert decision.policy_id == "POL-FAILSAFE"
