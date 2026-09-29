import pytest
from unittest.mock import AsyncMock

from argus.agents.risk_prediction.agent import RiskPredictionAgent
from argus.agents.risk_prediction.models.schemas import RiskAnalysisInput

@pytest.mark.asyncio
async def test_agent_full_pipeline(risk_input_model):
    agent = RiskPredictionAgent()
    await agent.initialize()
    
    # The framework would normally call process_task() which calls reason->plan->execute
    is_valid = await agent.validate(risk_input_model)
    assert is_valid
    
    reasoning = await agent.reason(risk_input_model)
    plan = await agent.plan(reasoning)
    result = await agent.execute(plan)
    
    assert result.source_event_id == "evt-12345"
    assert result.risk_score is not None
    assert result.severity is not None
    assert result.asset_priority == "critical"
    
@pytest.mark.asyncio
async def test_agent_missing_data_pipeline():
    # Empty knowledge event
    mock_risk_input = {
        "threat_event": {
            "source_event_id": "evt-empty",
            "threat_level": "info",
            "confidence": 0.5,
            "evidence": [],
            "recommended_actions": [],
            "model_version": "v1"
        },
        "knowledge_event": {
            "affected_assets": [],
            "asset_types": {},
            "known_vulnerabilities": [],
            "related_incidents": []
        }
    }
    input_model = RiskAnalysisInput(**mock_risk_input)
    
    agent = RiskPredictionAgent()
    await agent.initialize()
    
    reasoning = await agent.reason(input_model)
    plan = await agent.plan(reasoning)
    result = await agent.execute(plan)
    
    assert result.source_event_id == "evt-empty"
    assert result.asset_priority is None
    assert result.impact_estimation.severity is None
    assert result.risk_score is None
    assert result.severity is None
