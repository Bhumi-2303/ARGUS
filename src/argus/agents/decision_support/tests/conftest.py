import pytest
from typing import Dict, Any

from argus.agents.decision_support.models.schemas import DecisionAnalysisInput

@pytest.fixture
def mock_decision_input() -> Dict[str, Any]:
    return {
        "risk_event": {
            "source_event_id": "evt-12345",
            "risk_score": 95,
            "severity": "CRITICAL",
            "confidence": 0.88,
            "asset_priority": "CRITICAL",
            "impact_estimation": {
                "severity": "SEVERE",
                "estimated_downtime_hours": 12.0
            },
            "reasoning": "High risk detected"
        },
        "knowledge_event": {
            "affected_assets": ["scada_server_1"],
            "asset_types": {
                "scada_server_1": "scada_server"
            },
            "known_vulnerabilities": ["CVE-2023-XXXX"],
            "related_incidents": ["inc-001"]
        }
    }

@pytest.fixture
def decision_input_model(mock_decision_input) -> DecisionAnalysisInput:
    return DecisionAnalysisInput(**mock_decision_input)
