"""Unit and integration tests for the Knowledge & Context Agent."""
import pytest
import os

from argus.agents.knowledge_context.agent import KnowledgeContextAgent
from argus.agents.knowledge_context.pipeline import KnowledgePipeline
from argus.agents.knowledge_context.schemas import KCAPipelineConfig, EnrichmentContext
from argus.agents.knowledge_context.tools.mitre import MitreTool
from argus.agents.knowledge_context.tools.mitre_ics import MitreICSTool
from argus.agents.knowledge_context.tools.cve import CVETool
from argus.agents.knowledge_context.tools.cisa import CISATool
from argus.agents.knowledge_context.tools.playbook import PlaybookTool
from argus.agents.knowledge_context.tools.vector_search import VectorSearchTool
from argus.agents.knowledge_context.tools.gemini_reasoner import GeminiReasoner
from argus.agents.knowledge_context.tools.publisher import KnowledgePublisher
from argus.schemas.messages import KnowledgeEvent


RESOURCES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "src", "argus", "agents", "knowledge_context", "resources",
)
RESOURCES_DIR = os.path.normpath(RESOURCES_DIR)


# ────────────────────────────────────────────────────────
# Individual tool unit tests
# ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mitre_tool_brute_force():
    tool = MitreTool(resources_dir=RESOURCES_DIR)
    await tool.initialize()
    result = await tool.execute(attack_type="brute_force")
    assert result.hit_count > 0
    assert result.source == "mitre_attack"
    assert any(r["id"] == "T1110" for r in result.records)
    await tool.shutdown()


@pytest.mark.asyncio
async def test_mitre_ics_tool_dos():
    tool = MitreICSTool(resources_dir=RESOURCES_DIR)
    await tool.initialize()
    result = await tool.execute(attack_type="dos")
    assert result.hit_count > 0
    assert result.source == "mitre_attack_ics"
    await tool.shutdown()


@pytest.mark.asyncio
async def test_cve_tool_by_attack_type():
    tool = CVETool(resources_dir=RESOURCES_DIR)
    await tool.initialize()
    result = await tool.execute(attack_type="exploit")
    assert result.hit_count > 0
    assert result.source == "cve_db"
    await tool.shutdown()


@pytest.mark.asyncio
async def test_cve_tool_by_id():
    tool = CVETool(resources_dir=RESOURCES_DIR)
    await tool.initialize()
    result = await tool.execute(cve_id="CVE-2023-3595")
    assert result.hit_count == 1
    assert result.records[0]["id"] == "CVE-2023-3595"
    await tool.shutdown()


@pytest.mark.asyncio
async def test_cve_tool_unknown_id():
    tool = CVETool(resources_dir=RESOURCES_DIR)
    await tool.initialize()
    result = await tool.execute(cve_id="CVE-9999-0000")
    assert result.hit_count == 0
    await tool.shutdown()


@pytest.mark.asyncio
async def test_cisa_tool():
    tool = CISATool(resources_dir=RESOURCES_DIR)
    await tool.initialize()
    result = await tool.execute(attack_type="exploit")
    assert result.hit_count > 0
    assert result.source == "cisa_advisories"
    await tool.shutdown()


@pytest.mark.asyncio
async def test_playbook_tool():
    tool = PlaybookTool(resources_dir=RESOURCES_DIR)
    await tool.initialize()
    result = await tool.execute(attack_type="ransomware")
    assert result.hit_count > 0
    assert result.source == "playbooks"
    assert "immediate_actions" in result.records[0]
    await tool.shutdown()


@pytest.mark.asyncio
async def test_vector_search_placeholder():
    tool = VectorSearchTool()
    await tool.initialize()
    result = await tool.execute(query="brute force modbus")
    assert result.hit_count == 0
    assert result.source == "vector_search"
    await tool.shutdown()


# ────────────────────────────────────────────────────────
# GeminiReasoner tests
# ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_gemini_reasoner_synthesis():
    """Test that the reasoner aggregates mitigations and computes confidence."""
    from argus.agents.knowledge_context.schemas import RetrievalResult

    ctx = EnrichmentContext(
        attack_type="brute_force",
        mitre_results=RetrievalResult(
            source="mitre_attack",
            records=[{
                "id": "T1110",
                "name": "Brute Force",
                "tactic": "Credential Access",
                "mitigations": ["Account Lockout Policies", "Multi-Factor Authentication"],
                "references": ["https://attack.mitre.org/techniques/T1110/"],
            }],
            query_used="brute_force",
            hit_count=1,
        ),
        mitre_ics_results=RetrievalResult(
            source="mitre_attack_ics",
            records=[],
            query_used="brute_force",
            hit_count=0,
        ),
        cve_results=RetrievalResult(
            source="cve_db",
            records=[{
                "id": "CVE-2023-38408",
                "cvss_score": 9.8,
                "patch": "Update to OpenSSH 9.3p2",
                "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-38408"],
            }],
            query_used="brute_force",
            hit_count=1,
        ),
        cisa_results=RetrievalResult(source="cisa_advisories", records=[], query_used="brute_force", hit_count=0),
        playbook_results=RetrievalResult(source="playbooks", records=[], query_used="brute_force", hit_count=0),
    )

    reasoner = GeminiReasoner()
    await reasoner.initialize()
    result = await reasoner.execute(enrichment_context=ctx)

    assert result.confidence == 0.4  # 2 out of 5 sources hit
    assert len(result.recommended_mitigations) >= 2
    assert len(result.references) >= 2
    assert "brute_force" in result.attack_context["attack_type"]
    await reasoner.shutdown()


# ────────────────────────────────────────────────────────
# KnowledgePublisher tests
# ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_knowledge_publisher():
    from argus.agents.knowledge_context.schemas import SynthesisResult

    synthesis = SynthesisResult(
        attack_context={"attack_type": "dos"},
        mitre_techniques=[{"id": "T1498"}],
        cves=[],
        cisa_advisories=[],
        recommended_mitigations=["Rate-limit traffic"],
        references=["https://attack.mitre.org/techniques/T1498/"],
        confidence=0.6,
        summary_markdown="# DoS Summary",
    )

    publisher = KnowledgePublisher()
    await publisher.initialize()
    event = await publisher.execute(
        synthesis_result=synthesis,
        agent_id="test-kca-01",
        processing_duration_ms=42.5,
    )

    assert isinstance(event, KnowledgeEvent)
    assert event.event_type == "KNOWLEDGE_EVENT"
    assert event.confidence == 0.6
    assert event.processing_metadata["processing_duration_ms"] == 42.5
    await publisher.shutdown()


# ────────────────────────────────────────────────────────
# Pipeline integration test
# ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_end_to_end():
    config = KCAPipelineConfig(resources_dir=RESOURCES_DIR)
    pipeline = KnowledgePipeline(agent_id="test-kca-pipeline", config=config)
    await pipeline.initialize()

    event = await pipeline.process_threat({
        "attack_type": "brute_force",
        "severity": 0.85,
    })

    assert isinstance(event, KnowledgeEvent)
    assert event.event_type == "KNOWLEDGE_EVENT"
    assert event.confidence > 0
    assert len(event.mitre_techniques) > 0
    assert len(event.recommended_mitigations) > 0
    assert event.processing_metadata["processing_duration_ms"] > 0

    await pipeline.shutdown()


@pytest.mark.asyncio
async def test_pipeline_unknown_attack():
    config = KCAPipelineConfig(resources_dir=RESOURCES_DIR)
    pipeline = KnowledgePipeline(agent_id="test-kca-pipeline", config=config)
    await pipeline.initialize()

    event = await pipeline.process_threat({
        "attack_type": "totally_unknown_attack_type_xyz",
    })

    assert isinstance(event, KnowledgeEvent)
    # Should still produce results via 'default' mapping
    assert event.confidence >= 0

    await pipeline.shutdown()


# ────────────────────────────────────────────────────────
# Agent lifecycle tests
# ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_agent_initialization():
    agent = KnowledgeContextAgent(
        agent_id="test-kca-01",
        name="test_kca",
        version="1.0.0",
        description="Test KCA",
        capabilities=["knowledge:enrich"],
        permissions=["read:security_context"],
        tools=[],
    )
    await agent.initialize()
    assert agent.pipeline is not None
    await agent.shutdown()


@pytest.mark.asyncio
async def test_agent_validation():
    agent = KnowledgeContextAgent(
        agent_id="test-kca-01",
        name="test_kca",
        version="1.0.0",
        description="Test KCA",
        capabilities=["knowledge:enrich"],
        permissions=["read:security_context"],
        tools=[],
    )
    assert await agent.validate({"attack_type": "dos"}) is True
    assert await agent.validate({"no_attack": "foo"}) is False
    assert await agent.validate("not a dict") is False


@pytest.mark.asyncio
async def test_agent_process_task():
    agent = KnowledgeContextAgent(
        agent_id="test-kca-01",
        name="test_kca",
        version="1.0.0",
        description="Test KCA",
        capabilities=["knowledge:enrich"],
        permissions=["read:security_context"],
        tools=[],
    )
    await agent.initialize()

    threat = {
        "attack_type": "dos",
        "severity": 0.9,
        "description": "Volumetric DoS against Modbus endpoint",
    }

    result = await agent.process_task(threat, threat)

    assert isinstance(result, KnowledgeEvent)
    assert result.confidence > 0
    assert len(result.mitre_techniques) > 0
    assert agent.tasks_completed == 1
    assert agent.tasks_failed == 0

    await agent.shutdown()


@pytest.mark.asyncio
async def test_agent_multiple_attack_types():
    """Run the agent against several attack types to exercise all databases."""
    agent = KnowledgeContextAgent(
        agent_id="test-kca-02",
        name="test_kca_multi",
        version="1.0.0",
        description="Test KCA multi",
        capabilities=["knowledge:enrich"],
        permissions=["read:security_context"],
        tools=[],
    )
    await agent.initialize()

    for attack in ["brute_force", "dos", "ransomware", "exploit", "mitm", "scanning"]:
        threat = {"attack_type": attack, "severity": 0.7}
        result = await agent.process_task(threat, threat)
        assert isinstance(result, KnowledgeEvent)
        assert result.event_type == "KNOWLEDGE_EVENT"

    assert agent.tasks_completed == 6
    await agent.shutdown()
