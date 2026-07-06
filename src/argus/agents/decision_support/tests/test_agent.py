import pytest
from unittest.mock import AsyncMock
from argus.agents.decision_support.agent import DecisionSupportAgent

@pytest.mark.asyncio
async def test_agent_pipeline(mock_decision_input):
    agent = DecisionSupportAgent()
    
    # Mock the tool initialize methods
    agent.tool_playbooks.initialize = AsyncMock()
    agent.tool_recommendations.initialize = AsyncMock()
    agent.tool_prioritizer.initialize = AsyncMock()
    agent.tool_impact.initialize = AsyncMock()
    agent.tool_approval.initialize = AsyncMock()
    agent.tool_publisher.initialize = AsyncMock()

    await agent.initialize()
    assert agent.status.value == "ready"

    # Test valid input
    is_valid = await agent.validate(mock_decision_input)
    assert is_valid is True
