import pytest
from typing import Dict, Any

from argus.agents.threat_analysis.models.schemas import FeatureEventInput

@pytest.fixture
def mock_feature_event() -> Dict[str, Any]:
    return {
        "event_id": "evt-12345",
        "source": "network_sensor_01",
        "features": {
            "bytes_in": 1500.0,
            "bytes_out": 200.0,
            "connection_duration": 0.5,
            "failed_logins": 0.0
        },
        "timestamp": "2023-10-25T10:00:00Z"
    }

@pytest.fixture
def feature_event_model(mock_feature_event) -> FeatureEventInput:
    return FeatureEventInput(**mock_feature_event)
