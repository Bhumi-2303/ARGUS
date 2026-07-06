import pytest
from unittest.mock import AsyncMock
from argus.agents.risk_prediction.agent import RiskPredictionAgent

@pytest.mark.asyncio
async def test_agent_pipeline(mock_risk_input):
    agent = RiskPredictionAgent()
    
    # Mock the tool initialize methods
    agent.tool_criticality.initialize = AsyncMock()
    agent.tool_impact.initialize = AsyncMock()
    agent.tool_trend.initialize = AsyncMock()
    agent.tool_scorer.initialize = AsyncMock()
    agent.tool_confidence.initialize = AsyncMock()
    agent.tool_publisher.initialize = AsyncMock()

    await agent.initialize()
    assert agent.status.value == "ready"

    # Test valid input
    is_valid = await agent.validate(mock_risk_input)
    assert is_valid is True
