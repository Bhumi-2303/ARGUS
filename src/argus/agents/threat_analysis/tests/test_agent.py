import pytest
from argus.agents.threat_analysis.agent import ThreatAnalysisAgent


@pytest.mark.asyncio
async def test_agent_initialization():
    agent = ThreatAnalysisAgent()
    await agent.initialize()
    assert agent.status.value == "ready"


@pytest.mark.asyncio
async def test_agent_validate(mock_feature_event):
    agent = ThreatAnalysisAgent()

    # Test valid input
    is_valid = await agent.validate(mock_feature_event)
    assert is_valid is True

    # Test invalid input
    is_valid = await agent.validate({"bad": "data"})
    assert is_valid is False
