"""Tests for the Threat Analysis Agent.

Covers:
- Execution using the existing XGBoost verified models (no fakes).
- Accurate preservation of correlation_ids.
- Returning of prediction, probability, and execution latency.
- Structured error propagation for unknown or unavailable models.
- Handling of correct FeatureEventInput payloads.
"""
import pytest
from argus.agents.threat_analysis.agent import ThreatAnalysisAgent
from argus.agents.threat_analysis.models.schemas import FeatureEventInput, ThreatAnalysisResult
from argus.registry.model_registry import model_registry

# Known verified test features (benign format)
TEST_FEATURES = {
    "pkt_mean_to_max": 0.45,
    "tcp_flag_density": 0.12,
    "log_pkt_mean": 3.8,
    "log_pkt_max": 5.2,
}

@pytest.fixture(autouse=True)
def setup_registry():
    if not model_registry.is_loaded:
        model_registry.load_all()

@pytest.fixture
async def ta_agent():
    agent = ThreatAnalysisAgent()
    await agent.initialize()
    return agent


@pytest.mark.asyncio
async def test_threat_analysis_agent_validates_input(ta_agent):
    """Ensure it correctly validates FeatureEventInput dicts."""
    valid_input = {
        "event_id": "test-evt-1",
        "correlation_id": "test-corr-1",
        "source": "data_intelligence",
        "features": TEST_FEATURES,
        "timestamp": "2026-09-29T00:00:00Z"
    }
    assert await ta_agent.validate(valid_input) is True
    
    # Missing required fields
    assert await ta_agent.validate({"event_id": "test-evt-1"}) is False


@pytest.mark.asyncio
async def test_threat_analysis_agent_real_inference(ta_agent):
    """Run real inference without fabricating outputs, verify outputs."""
    valid_input = {
        "event_id": "test-evt-2",
        "correlation_id": "test-corr-2",
        "source": "data_intelligence",
        "features": TEST_FEATURES,
        "timestamp": "2026-09-29T00:00:00Z",
        "model_version": "xgb_adapted"
    }
    
    reasoning = await ta_agent.reason(valid_input)
    result = await ta_agent.execute(reasoning)
    
    assert isinstance(result, ThreatAnalysisResult)
    assert result.source_event_id == "test-evt-2"
    assert result.correlation_id == "test-corr-2"
    assert result.model_version == "xgb_adapted"
    assert result.protocol_status == "coral_aligned"
    
    # Real inference produces valid float probabilities 0.0 to 1.0
    assert 0.0 <= result.confidence <= 1.0
    assert result.threat_level.value in ("low", "medium", "high", "critical")
    
    # Timing is recorded
    assert result.latency_ms > 0
    
    # SHAP Evidence was recorded
    assert len(result.evidence) > 0
    assert all(e.type == "feature_attribution" for e in result.evidence)


@pytest.mark.asyncio
async def test_threat_analysis_agent_fallback_model(ta_agent):
    """If no model is specified, it uses xgb_adapted by default."""
    valid_input = {
        "event_id": "test-evt-3",
        "correlation_id": "test-corr-3",
        "source": "data_intelligence",
        "features": TEST_FEATURES,
        "timestamp": "2026-09-29T00:00:00Z"
    }
    
    reasoning = await ta_agent.reason(valid_input)
    result = await ta_agent.execute(reasoning)
    
    assert result.model_version == "xgb_adapted"
    assert result.latency_ms > 0


@pytest.mark.asyncio
async def test_threat_analysis_agent_propagates_model_errors(ta_agent):
    """If given an unknown model, it raises a real KeyError instead of swallowing it."""
    bad_input = {
        "event_id": "test-evt-4",
        "correlation_id": "test-corr-4",
        "source": "data_intelligence",
        "features": TEST_FEATURES,
        "timestamp": "2026-09-29T00:00:00Z",
        "model_version": "non_existent_model"
    }
    
    with pytest.raises(KeyError, match="Unknown model name"):
        await ta_agent.reason(bad_input)


@pytest.mark.asyncio
async def test_threat_analysis_agent_propagates_unavailable_model_errors(ta_agent):
    """If given an unavailable model like 'dann', it raises NotImplementedError."""
    bad_input = {
        "event_id": "test-evt-5",
        "source": "data_intelligence",
        "features": TEST_FEATURES,
        "timestamp": "2026-09-29T00:00:00Z",
        "model_version": "dann"
    }
    
    with pytest.raises(NotImplementedError, match="unavailable for live inference"):
        await ta_agent.reason(bad_input)
