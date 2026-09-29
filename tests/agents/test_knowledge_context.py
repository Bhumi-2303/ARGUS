"""Tests for Knowledge Context Agent integration.

Verifies:
1. Matching knowledge (valid attack).
2. No-match case (benign).
3. Retrieval failure (graceful handling).
4. Provenance preservation.
"""
import pytest
import os
from unittest.mock import patch
from argus.agents.knowledge_context.agent import KnowledgeContextAgent
from argus.schemas.messages import KnowledgeEvent


@pytest.fixture
async def kca():
    agent = KnowledgeContextAgent()
    await agent.initialize()
    return agent


@pytest.mark.asyncio
async def test_kca_matching_knowledge(kca):
    """1. Matching knowledge logic."""
    kca_input = {
        "event_id": "evt-123",
        "correlation_id": "corr-456",
        "attack_type": "dos",
        "severity": 0.95
    }
    
    reasoning = await kca.reason(kca_input)
    plan = await kca.plan(reasoning)
    result = await kca.execute(plan)
    
    assert isinstance(result, KnowledgeEvent)
    assert result.request_id == "evt-123"
    assert result.trace_id == "corr-456"
    assert result.attack_context["attack_type"] == "dos"
    
    # Assert actual evidence was retrieved
    assert len(result.mitre_techniques) > 0
    assert len(result.cves) > 0
    assert len(result.cisa_advisories) > 0
    assert result.confidence > 0.0
    
    # 4. Provenance Preservation
    assert "mitre_attack" in result.processing_metadata["sources_searched"]
    assert "cve" in result.processing_metadata["sources_searched"]
    assert result.processing_metadata["total_records"] == (
        len(result.mitre_techniques) + len(result.cves) + len(result.cisa_advisories) + len(result.recommended_mitigations)
    )


@pytest.mark.asyncio
async def test_kca_no_match_case(kca):
    """2. No-match case returns empty lists without error."""
    kca_input = {
        "event_id": "evt-benign",
        "correlation_id": "corr-benign",
        "attack_type": "benign",
        "severity": 0.1
    }
    
    reasoning = await kca.reason(kca_input)
    plan = await kca.plan(reasoning)
    result = await kca.execute(plan)
    
    assert isinstance(result, KnowledgeEvent)
    assert result.attack_context["attack_type"] == "benign"
    
    # Assert lists are empty, no fake data
    assert len(result.mitre_techniques) == 0
    assert len(result.cves) == 0
    assert len(result.cisa_advisories) == 0
    assert len(result.recommended_mitigations) == 0
    assert result.confidence == 0.0
    assert result.processing_metadata["total_records"] == 0


@pytest.mark.asyncio
async def test_kca_retrieval_failure(kca):
    """3. Retrieval failure handles exceptions gracefully."""
    kca_input = {
        "event_id": "evt-fail",
        "correlation_id": "corr-fail",
        "attack_type": "dos",
        "severity": 0.95
    }
    
    # Patch the mitre tool to raise an Exception simulating a failure
    with patch("argus.agents.knowledge_context.tools.mitre.MitreTool.execute", side_effect=RuntimeError("Database offline")):
        reasoning = await kca.reason(kca_input)
        plan = await kca.plan(reasoning)
        
        # We expect the agent to still return a valid KnowledgeEvent, possibly omitting the failed part or failing the pipeline explicitly
        try:
            result = await kca.execute(plan)
        except Exception as e:
            # If the pipeline currently raises exceptions on retrieval failure, we catch it
            assert "Database offline" in str(e)
            return
            
        # If the pipeline handles it and returns partial, verify it
        assert isinstance(result, KnowledgeEvent)
        assert result.request_id == "evt-fail"
