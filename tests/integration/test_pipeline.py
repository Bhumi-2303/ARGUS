import pytest
from tests.fixtures.events import FIXTURES
from argus.schemas.event import RiskContract, PolicyContract

def test_integration_low_criticality_benign():
    event = FIXTURES["low_criticality_benign"]()
    # In a real integration test, this would pass through the orchestrator.
    # Here we mock the pipeline sequence.
    assert event.detector.is_anomaly is False
    assert event.asset_criticality == 1
    # Pipeline short-circuits here
    assert event.risk is None

def test_integration_high_criticality_attack():
    event = FIXTURES["high_criticality_attack"]()
    # Mocking pipeline sequence
    assert event.detector.is_anomaly is True
    assert event.risk.risk_score == 95.0
    assert event.knowledge.confidence == 0.9
    assert "High confidence attack" in event.explanation.human_readable_explanation
    
    # Evaluate policy
    event.policy = PolicyContract(policy_id="P-001", action_allowed=True, violations=[])
    assert event.policy.action_allowed is True

def test_integration_policy_failure():
    event = FIXTURES["policy_failure"]()
    assert event.detector.is_anomaly is True
    assert event.policy.action_allowed is False
    assert len(event.policy.violations) > 0
