import pytest
from argus.policy.models import PolicyContext, ActionType
from argus.policy.policy_engine import PolicyEngine

def test_failsafe_policy():
    engine = PolicyEngine()
    context = PolicyContext(risk_tier="unknown")
    decision = engine.evaluate(context)
    assert decision.action == ActionType.MONITOR
    assert decision.requires_human_approval is False

def test_low_risk_policy():
    engine = PolicyEngine()
    context = PolicyContext(risk_tier="low", criticality=1)
    decision = engine.evaluate(context)
    assert decision.action == ActionType.MONITOR

def test_medium_risk_policy():
    engine = PolicyEngine()
    context = PolicyContext(risk_tier="medium", criticality=5)
    decision = engine.evaluate(context)
    assert decision.action == ActionType.INVESTIGATE

def test_high_risk_policy():
    engine = PolicyEngine()
    context = PolicyContext(risk_tier="high", criticality=3, confidence="high")
    decision = engine.evaluate(context)
    assert decision.action == ActionType.ISOLATE
    assert decision.requires_human_approval is True

def test_critical_risk_policy():
    engine = PolicyEngine()
    context = PolicyContext(risk_tier="critical", criticality=1)
    decision = engine.evaluate(context)
    assert decision.action == ActionType.ESCALATE
    assert decision.requires_human_approval is True

def test_critical_risk_high_criticality():
    engine = PolicyEngine()
    context = PolicyContext(risk_tier="critical", criticality=5)
    decision = engine.evaluate(context)
    assert decision.action == ActionType.ISOLATE
    assert decision.requires_human_approval is True
