import pytest
from datetime import datetime
from pydantic import ValidationError

from argus.schemas.event import (
    ArgusEvent, DetectorContract, RiskContract, KnowledgeContract, DecisionContract
)

def test_valid_event_creation():
    event = ArgusEvent(
        event_id="evt-001",
        timestamp=datetime.utcnow(),
        source="sensor-1",
        domain="OT",
        asset="PLC-01",
    )
    assert event.event_id == "evt-001"
    assert event.schema_version == "1.0"
    assert event.detector is None

def test_missing_required_field():
    with pytest.raises(ValidationError):
        # Missing source, domain, asset
        ArgusEvent(
            event_id="evt-002",
            timestamp=datetime.utcnow()
        )

def test_invalid_risk_score():
    with pytest.raises(ValidationError):
        RiskContract(
            risk_score=150.0, # invalid, > 100
            severity="high",
            asset_priority=1,
            impact_estimation="high impact"
        )

def test_invalid_criticality():
    with pytest.raises(ValidationError):
        # Using string for int field
        RiskContract(
            risk_score=50.0,
            severity="high",
            asset_priority="HIGH", # Should be int
            impact_estimation="high impact"
        )

def test_invalid_action():
    with pytest.raises(ValidationError):
        DecisionContract(
            recommended_actions="isolate_host", # Should be a list
            priority=1,
            urgency="high",
            approval_required=True
        )

def test_missing_detector_result():
    with pytest.raises(ValidationError):
        # Missing required is_anomaly
        DetectorContract(
            confidence=0.9
        )

def test_partial_knowledge_response():
    # Should be valid with only confidence, other fields are optional lists
    contract = KnowledgeContract(
        confidence=0.8
    )
    assert contract.confidence == 0.8
    assert contract.cve_ids == []

def test_schema_version_mismatch():
    # Attempting to assign an invalid field to the extra='forbid' config
    with pytest.raises(ValidationError):
        ArgusEvent(
            event_id="evt-001",
            source="sensor-1",
            domain="OT",
            asset="PLC-01",
            unsupported_version_field="2.0"
        )
