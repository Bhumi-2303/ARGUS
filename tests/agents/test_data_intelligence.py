import pytest
import os
import asyncio
from argus.agents.data_intelligence.agent import DataIntelligenceAgent

@pytest.fixture
def sample_config():
    return {
        "pipeline_config": {
            "chunk_size": 100,
            "normalization_method": "min_max",
            "drop_labels": True,
            "drop_ips": True
        }
    }

@pytest.mark.asyncio
async def test_data_intelligence_agent_initialization():
    agent = DataIntelligenceAgent(
        agent_id="test-di-01",
        name="test_di",
        version="1.0.0",
        description="Test agent",
        capabilities=["data:ingest"],
        permissions=["data:read", "data:write"],
        tools=[]
    )
    await agent.initialize()
    assert agent.pipeline is not None
    await agent.shutdown()

@pytest.mark.asyncio
async def test_data_intelligence_agent_validation():
    agent = DataIntelligenceAgent(
        agent_id="test-di-01",
        name="test_di",
        version="1.0.0",
        description="Test agent",
        capabilities=["data:ingest"],
        permissions=["data:read", "data:write"],
        tools=[]
    )
    
    assert await agent.validate({"file_path": "non_existent.csv"}) == False
    assert await agent.validate({"file_path": "invalid.txt"}) == False
    # If we had a real file we could test True condition

@pytest.mark.asyncio
async def test_data_intelligence_agent_reasoning(sample_config):
    agent = DataIntelligenceAgent(
        agent_id="test-di-01",
        name="test_di",
        version="1.0.0",
        description="Test agent",
        capabilities=["data:ingest"],
        permissions=["data:read", "data:write"],
        tools=[]
    )
    reasoning = await agent.reason(sample_config)
    assert reasoning["config"].chunk_size == 100
    assert reasoning["config"].normalization_method == "min_max"

@pytest.mark.asyncio
async def test_data_intelligence_agent_planning(sample_config):
    agent = DataIntelligenceAgent(
        agent_id="test-di-01",
        name="test_di",
        version="1.0.0",
        description="Test agent",
        capabilities=["data:ingest"],
        permissions=["data:read", "data:write"],
        tools=[]
    )
    reasoning = await agent.reason(sample_config)
    plan = await agent.plan(reasoning)
    assert plan["stages"] == ["load", "validate", "clean", "normalize", "extract", "publish"]
    assert plan["config"].chunk_size == 100
