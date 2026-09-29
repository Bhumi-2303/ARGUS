"""Tests for the Explainability Agent integration.

Verifies:
- SHAP calculation uses real model registry.
- Actual features from pipeline are passed correctly.
- Top contributing features and metadata are returned.
- Explanation failure yields structured unavailable result.
- No faked/synthesized explanations are produced.
"""
import pytest
from argus.agents.explainability.agent import ExplainabilityAgent
from argus.agents.explainability.schemas import ExplainabilityInput, ExplainabilityResult
from argus.registry.model_registry import model_registry

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
async def exp_agent():
    agent = ExplainabilityAgent()
    await agent.initialize()
    return agent


@pytest.mark.asyncio
async def test_explainability_validates_input(exp_agent):
    """Ensure it correctly validates ExplainabilityInput."""
    valid_input = {
        "event_id": "test-evt-1",
        "correlation_id": "test-corr-1",
        "features": TEST_FEATURES,
        "model_version": "xgb_adapted"
    }
    assert await exp_agent.validate(valid_input) is True
    
    # Missing required features field
    assert await exp_agent.validate({"event_id": "test-evt-1", "model_version": "xgb_adapted"}) is False


@pytest.mark.asyncio
async def test_explainability_real_shap(exp_agent):
    """Run actual SHAP extraction from model registry without faking it."""
    valid_input = {
        "event_id": "test-evt-2",
        "correlation_id": "test-corr-2",
        "features": TEST_FEATURES,
        "model_version": "xgb_adapted"
    }
    
    reasoning = await exp_agent.reason(valid_input)
    result = await exp_agent.execute(reasoning)
    
    assert isinstance(result, ExplainabilityResult)
    assert result.status == "available"
    assert result.event_id == "test-evt-2"
    assert result.correlation_id == "test-corr-2"
    assert result.model_version == "xgb_adapted"
    
    # Has SHAP dictionary for all 4 features
    assert len(result.shap_values) == 4
    for f in TEST_FEATURES.keys():
        assert f in result.shap_values
        assert isinstance(result.shap_values[f], float)
        
    # Top feature is identified correctly
    assert result.top_feature in TEST_FEATURES.keys()
    assert result.top_feature_impact == result.shap_values[result.top_feature]
    
    # Timing is recorded
    assert result.latency_ms > 0
    assert result.base_value is not None


@pytest.mark.asyncio
async def test_explainability_handles_missing_model(exp_agent):
    """If the model cannot be explained, it returns 'unavailable' rather than faking SHAP."""
    valid_input = {
        "event_id": "test-evt-3",
        "features": TEST_FEATURES,
        "model_version": "unknown_model_that_does_not_exist"
    }
    
    reasoning = await exp_agent.reason(valid_input)
    result = await exp_agent.execute(reasoning)
    
    assert isinstance(result, ExplainabilityResult)
    assert result.status == "unavailable"
    assert result.reason is not None
    assert "Unknown model 'unknown_model_that_does_not_exist'" in result.reason
    assert result.top_feature is None
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_explainability_handles_unavailable_model(exp_agent):
    """DANN model cannot be live-explained, should return unavailable."""
    valid_input = {
        "event_id": "test-evt-4",
        "features": TEST_FEATURES,
        "model_version": "dann"
    }
    
    reasoning = await exp_agent.reason(valid_input)
    result = await exp_agent.execute(reasoning)
    
    assert isinstance(result, ExplainabilityResult)
    assert result.status == "unavailable"
    assert "unavailable for live inference" in result.reason
