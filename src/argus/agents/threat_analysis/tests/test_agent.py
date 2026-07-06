import pytest
from unittest.mock import AsyncMock, MagicMock
from argus.agents.threat_analysis.agent import ThreatAnalysisAgent
from argus.agents.threat_analysis.models.schemas import ThreatLevel

@pytest.mark.asyncio
async def test_agent_initialization():
    agent = ThreatAnalysisAgent()
    # Mock the tool initialize methods so we don't need real models/APIs
    agent.tool_model_loader.initialize = AsyncMock()
    agent.tool_model_loader.execute = AsyncMock(return_value="mock_model")
    agent.tool_inference.initialize = AsyncMock()
    agent.tool_confidence.initialize = AsyncMock()
    agent.tool_evidence.initialize = AsyncMock()
    agent.tool_gemini.initialize = AsyncMock()
    agent.tool_publisher.initialize = AsyncMock()

    await agent.initialize()
    assert agent.status.value == "ready"
    assert agent._active_model == "mock_model"

@pytest.mark.asyncio
async def test_agent_validate(mock_feature_event):
    agent = ThreatAnalysisAgent()
    
    # Test valid input
    is_valid = await agent.validate(mock_feature_event)
    assert is_valid is True
    
    # Test invalid input
    is_valid = await agent.validate({"bad": "data"})
    assert is_valid is False
