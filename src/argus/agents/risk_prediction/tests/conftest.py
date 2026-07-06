import pytest
from typing import Dict, Any

from argus.agents.risk_prediction.models.schemas import RiskAnalysisInput

@pytest.fixture
def mock_risk_input() -> Dict[str, Any]:
    return {
        "threat_event": {
            "source_event_id": "evt-12345",
            "threat_level": "critical",
            "confidence": 0.95,
            "evidence": [{"type": "anomaly_score", "value": -0.8}],
            "recommended_actions": ["Isolate network"],
            "model_version": "isolation_forest-v1"
        },
        "knowledge_event": {
            "affected_assets": ["scada_server_1", "hmi_terminal_2"],
            "asset_types": {
                "scada_server_1": "scada_server",
                "hmi_terminal_2": "hmi"
            },
            "known_vulnerabilities": ["CVE-2023-XXXX"],
            "related_incidents": ["inc-001", "inc-005"]
        }
    }

@pytest.fixture
def risk_input_model(mock_risk_input) -> RiskAnalysisInput:
    return RiskAnalysisInput(**mock_risk_input)
