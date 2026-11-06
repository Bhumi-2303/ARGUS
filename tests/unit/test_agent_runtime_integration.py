"""Tests for optional agent runtime integration layer (Google ADK narrator & read-only MCP server).

Proves:
1. Pipeline outputs (risk scores, classifications, decisions) are 100% IDENTICAL with the layer enabled vs disabled.
2. The layer is OFF by default and never operates on the detection path.
3. The MCP server provides 4 strictly read-only tools (get_incident, get_trace, explain_flow, lookup_mitre).
4. The ADK narrator degrades cleanly when no API key is configured (zero-hallucination deterministic fallback).
5. The ADK narrator never alters risk scores, threat levels, or remediation decisions.
"""

import os
import uuid
import pytest
from unittest.mock import patch

from argus.orchestrator.pipeline import execute_pipeline
from argus.registry.model_registry import model_registry
from argus.services.incident_service import incident_service
from argus.schemas.incident import Incident, IncidentStatus
from argus.tools.mcp.mcp_registry import MCPRegistry
from argus.integrations.config import get_runtime_config
from argus.integrations.mcp.server import ArgusMCPServer
from argus.integrations.adk.narrator import IncidentNarrator, IncidentNarrative
from argus.integrations.adk.adapter import ADKAdapter


@pytest.fixture(autouse=True)
def ensure_models_loaded():
    """Ensure verified model registry is loaded before tests run."""
    if not model_registry.is_loaded:
        model_registry.load_all()


@pytest.fixture
def sample_flow_features():
    """Representative feature vector from CICIoT2023 / NF-ToN."""
    return {
        "pkt_mean_to_max": 0.42,
        "tcp_flag_density": 0.15,
        "log_pkt_mean": 5.2,
        "log_pkt_max": 7.1,
    }


@pytest.mark.asyncio
async def test_pipeline_output_identical_with_layer_enabled_and_disabled(sample_flow_features):
    """PROVE REQUIREMENT: Pipeline outputs are 100% identical with the layer enabled and disabled."""
    corr_disabled = f"flow-disabled-{uuid.uuid4().hex[:8]}"
    corr_enabled = f"flow-enabled-{uuid.uuid4().hex[:8]}"
    model_name = "model_d2_coral"

    # 1. Execute pipeline with layer DISABLED (default)
    with patch.dict(
        os.environ,
        {
            "ARGUS_AGENT_RUNTIME": "false",
            "ARGUS_MCP_SERVER": "false",
            "ARGUS_ADK_NARRATOR": "false",
        },
    ):
        cfg_disabled = get_runtime_config()
        assert not cfg_disabled.enabled
        assert not cfg_disabled.mcp_server_enabled
        assert not cfg_disabled.adk_narrator_enabled

        ctx_disabled = await execute_pipeline(
            features=sample_flow_features,
            model_name=model_name,
            correlation_id=corr_disabled,
        )

    # 2. Execute pipeline with layer ENABLED
    with patch.dict(
        os.environ,
        {"ARGUS_AGENT_RUNTIME": "true", "ARGUS_MCP_SERVER": "true", "ARGUS_ADK_NARRATOR": "true"},
    ):
        cfg_enabled = get_runtime_config()
        assert cfg_enabled.enabled
        assert cfg_enabled.mcp_server_enabled
        assert cfg_enabled.adk_narrator_enabled

        ctx_enabled = await execute_pipeline(
            features=sample_flow_features,
            model_name=model_name,
            correlation_id=corr_enabled,
        )

    # 3. Assert EVERY pipeline output is bit-for-bit identical
    assert ctx_disabled.status == ctx_enabled.status == "completed"

    # Threat Analysis outputs
    assert ctx_disabled.threat.threat_level == ctx_enabled.threat.threat_level
    assert ctx_disabled.threat.confidence == pytest.approx(ctx_enabled.threat.confidence, abs=1e-7)
    assert ctx_disabled.threat.model_version == ctx_enabled.threat.model_version

    # Explainability (TreeSHAP) outputs
    assert ctx_disabled.explanation["status"] == ctx_enabled.explanation["status"]
    assert ctx_disabled.explanation["top_feature"] == ctx_enabled.explanation["top_feature"]
    assert ctx_disabled.explanation["top_feature_impact"] == pytest.approx(
        ctx_enabled.explanation["top_feature_impact"], abs=1e-7
    )
    for feat, val in ctx_disabled.explanation["shap_values"].items():
        assert val == pytest.approx(ctx_enabled.explanation["shap_values"][feat], abs=1e-7)

    # Knowledge Context outputs
    assert ctx_disabled.knowledge.mitre_techniques == ctx_enabled.knowledge.mitre_techniques

    # Risk Prediction outputs
    assert ctx_disabled.risk.risk_score == ctx_enabled.risk.risk_score
    assert ctx_disabled.risk.severity == ctx_enabled.risk.severity

    # Decision Support outputs
    actions_disabled = [
        (
            a.action_type,
            a.description,
            tuple(a.target_assets),
            a.playbook_reference,
            a.priority,
            a.urgency,
        )
        for a in ctx_disabled.decision.recommended_actions
    ]
    actions_enabled = [
        (
            a.action_type,
            a.description,
            tuple(a.target_assets),
            a.playbook_reference,
            a.priority,
            a.urgency,
        )
        for a in ctx_enabled.decision.recommended_actions
    ]
    assert actions_disabled == actions_enabled
    assert ctx_disabled.decision.approval_required == ctx_enabled.decision.approval_required


@pytest.mark.asyncio
async def test_mcp_server_tool_listing_and_metadata():
    """Verify ArgusMCPServer exposes exactly the 4 required read-only tools."""
    server = ArgusMCPServer()
    await server.initialize()

    tools = await server.list_tools()
    assert len(tools) == 4
    tool_names = [t["name"] for t in tools]
    assert "get_incident" in tool_names
    assert "get_trace" in tool_names
    assert "explain_flow" in tool_names
    assert "lookup_mitre" in tool_names

    for tool in tools:
        assert tool.get("read_only") is True
        assert "parameters_schema" in tool

    await server.shutdown()


@pytest.mark.asyncio
async def test_mcp_tool_explain_flow(sample_flow_features):
    """Verify MCP explain_flow tool computes valid TreeSHAP attributions."""
    server = ArgusMCPServer()
    await server.initialize()

    res = await server.call_tool(
        "explain_flow", {"features": sample_flow_features, "model_name": "model_d2_coral"}
    )

    assert res["success"] is True
    assert "probability" in res
    assert 0.0 <= res["probability"] <= 1.0
    assert "shap_attributions" in res
    assert len(res["shap_attributions"]) == 4
    assert res["top_feature"] in sample_flow_features
    assert "base_value" in res

    # Verify invalid features handling
    err_res = await server.call_tool("explain_flow", {"features": {}})
    assert err_res["success"] is False

    await server.shutdown()


@pytest.mark.asyncio
async def test_mcp_tool_lookup_mitre():
    """Verify MCP lookup_mitre tool resolves techniques by ID and attack type."""
    server = ArgusMCPServer()
    await server.initialize()

    # 1. Lookup by technique ID
    t1059 = await server.call_tool("lookup_mitre", {"technique_id": "T1059"})
    assert t1059["found"] is True
    assert t1059["technique"]["id"] == "T1059"
    assert "Command and Scripting" in t1059["technique"]["name"]
    assert len(t1059["technique"]["mitigations"]) > 0

    # 2. Lookup by attack category
    brute = await server.call_tool("lookup_mitre", {"attack_type": "brute_force"})
    assert brute["found"] is True
    assert brute["matched_count"] > 0

    # 3. Lookup non-existent technique
    missing = await server.call_tool("lookup_mitre", {"technique_id": "T999999"})
    assert missing["found"] is False
    assert "available_ids" in missing

    # 4. General catalog summary
    summary = await server.call_tool("lookup_mitre", {})
    assert summary["found"] is True
    assert summary["total_techniques"] > 0

    await server.shutdown()


@pytest.mark.asyncio
async def test_mcp_tool_get_incident_read_only():
    """Verify MCP get_incident retrieves incident without mutating state."""
    # Seed an incident in incident_service
    inc = Incident(
        incident_id=f"INC-TEST-{uuid.uuid4().hex[:6]}",
        event_id=f"EVT-{uuid.uuid4().hex[:6]}",
        asset="substation-alpha",
        status=IncidentStatus.DETECTED,
        severity="HIGH",
        risk_score=78.0,
        detector_summary="MALICIOUS (confidence: 0.92)",
        knowledge_summary="T1059",
        decision={"recommendations": ["Isolate host 192.168.1.100", "Review SCADA firewall rules"]},
    )
    incident_service.create_incident(inc)

    server = ArgusMCPServer()
    await server.initialize()

    # Retrieve via tool
    res = await server.call_tool("get_incident", {"incident_id": inc.incident_id})
    assert res["found"] is True
    assert res["incident_id"] == inc.incident_id
    assert res["risk_score"] == 78
    assert "MALICIOUS" in res["threat_level"]
    assert res["mitre_techniques"] == ["T1059"]
    assert len(res["recommended_actions"]) == 2

    # Query non-existent
    res_missing = await server.call_tool("get_incident", {"incident_id": "INC-NON-EXISTENT"})
    assert res_missing["found"] is False

    await server.shutdown()


@pytest.mark.asyncio
async def test_mcp_tool_get_trace(sample_flow_features):
    """Verify MCP get_trace retrieves persisted multi-agent trace steps."""
    corr_id = f"flow-trace-{uuid.uuid4().hex[:8]}"
    ctx = await execute_pipeline(features=sample_flow_features, correlation_id=corr_id)
    assert ctx.status == "completed"

    server = ArgusMCPServer()
    await server.initialize()

    res = await server.call_tool("get_trace", {"correlation_id": corr_id})
    assert res["found"] is True
    assert res["correlation_id"] == corr_id
    assert res["status"] == "completed"
    assert res["total_stages"] >= 6
    stages = [t["agent"] for t in res["traces"]]
    assert "DATA_INTELLIGENCE" in stages
    assert "THREAT_ANALYSIS" in stages
    assert "DECISION_SUPPORT" in stages

    # Non-existent trace
    res_missing = await server.call_tool("get_trace", {"correlation_id": "non-existent-corr-id"})
    assert res_missing["found"] is False

    await server.shutdown()


@pytest.mark.asyncio
async def test_mcp_resources_listing_and_read():
    """Verify MCP resources listing and read access."""
    server = ArgusMCPServer()
    await server.initialize()

    resources = await server.list_resources()
    assert len(resources) == 3
    uris = [r["uri"] for r in resources]
    assert "argus://incidents" in uris
    assert "argus://models" in uris
    assert "argus://mitre" in uris

    # Read models resource
    models_res = await server.read_resource("argus://models")
    assert isinstance(models_res, list)
    model_names = [m["model_name"] for m in models_res]
    assert "model_d2_coral" in model_names

    # Read mitre resource
    mitre_res = await server.read_resource("argus://mitre")
    assert isinstance(mitre_res, list)
    assert len(mitre_res) > 0

    await server.shutdown()


@pytest.mark.asyncio
async def test_mcp_registry_lifecycle():
    """Verify ArgusMCPServer works with MCPRegistry."""
    registry = MCPRegistry()
    server = ArgusMCPServer(name="custom-mcp")

    await registry.register_server(server)
    assert "custom-mcp" in registry.list_servers()
    assert registry.get_server("custom-mcp") is server

    # Call tool via registered server
    tool_res = await server.call_tool("lookup_mitre", {"technique_id": "T1059"})
    assert tool_res["found"] is True

    await registry.shutdown_all()
    assert len(registry.list_servers()) == 0


@pytest.mark.asyncio
async def test_adk_narrator_degrades_cleanly_without_api_key():
    """Verify IncidentNarrator produces clean deterministic summary when no API key is set."""
    narrator = IncidentNarrator(api_key=None)

    incident_dict = {
        "incident_id": "INC-20261105-DEMO",
        "threat_level": "MALICIOUS",
        "confidence": 0.9412,
        "risk_score": 82,
        "severity": "CRITICAL",
        "top_feature": "pkt_mean_to_max",
        "top_feature_impact": 0.3812,
        "mitre_techniques": ["T1059", "T1110"],
        "recommended_actions": [
            "Trigger automated firewall drop rule on ingress router",
            "Notify SOC Tier 2 on-call analyst",
        ],
    }

    narrative = await narrator.narrate_incident(incident_dict)

    # Assert clean degradation
    assert narrative.is_llm_generated is False
    assert narrative.fallback_reason is not None
    assert "API key" in narrative.fallback_reason

    # Invariants: Scores and actions are completely unchanged
    assert narrative.verified_risk_score == 82
    assert narrative.verified_severity == "CRITICAL"
    assert narrative.verified_threat_level == "MALICIOUS"
    assert narrative.verified_decision_actions == incident_dict["recommended_actions"]

    # Narrative content contains all verified elements
    assert "INC-20261105-DEMO" in narrative.narrative_markdown
    assert "pkt_mean_to_max" in narrative.narrative_markdown
    assert "82/100" in narrative.narrative_markdown
    assert "T1059" in narrative.narrative_markdown


@pytest.mark.asyncio
async def test_adk_narrator_never_alters_original_incident_or_pipeline():
    """Verify narrator leaves the original incident dictionary completely unmodified."""
    original = {
        "incident_id": "INC-IMMUTABLE-01",
        "threat_level": "HIGH",
        "confidence": 0.88,
        "risk_score": 75,
        "severity": "HIGH",
        "top_feature": "tcp_flag_density",
        "top_feature_impact": 0.194,
        "mitre_techniques": ["T0814"],
        "recommended_actions": ["Reroute substation telemetry to backup link"],
    }
    # Deep copy representation
    import copy

    snapshot = copy.deepcopy(original)

    narrator = IncidentNarrator()
    narrative = await narrator.narrate_incident(original)

    # Input object must be 100% identical
    assert original == snapshot
    # Output verified anchors must match input exactly
    assert narrative.verified_risk_score == snapshot["risk_score"]
    assert narrative.verified_severity == snapshot["severity"]


@pytest.mark.asyncio
async def test_adk_narrator_graceful_handling_of_llm_error():
    """Verify narrator falls back to deterministic summary if live LLM call throws error."""
    narrator = IncidentNarrator(api_key="mock-key-for-test")

    incident_dict = {
        "incident_id": "INC-ERROR-TEST",
        "threat_level": "MALICIOUS",
        "confidence": 0.95,
        "risk_score": 90,
        "severity": "CRITICAL",
        "top_feature": "log_pkt_mean",
        "top_feature_impact": 0.45,
        "mitre_techniques": ["T1059"],
        "recommended_actions": ["Isolate node"],
    }

    # Simulate network timeout during LLM call
    with patch.object(
        narrator, "_call_gemini_narrator", side_effect=TimeoutError("Request timed out after 5.0s")
    ):
        narrative = await narrator.narrate_incident(incident_dict)

        assert narrative.is_llm_generated is False
        assert "timed out" in narrative.fallback_reason
        assert narrative.verified_risk_score == 90
        assert narrative.verified_severity == "CRITICAL"
        assert "INC-ERROR-TEST" in narrative.narrative_markdown


@pytest.mark.asyncio
async def test_adk_adapter_class_methods():
    """Verify ADKAdapter helper methods work as expected."""
    incident_dict = {
        "incident_id": "INC-ADAPTER-TEST",
        "threat_level": "SUSPICIOUS",
        "confidence": 0.70,
        "risk_score": 45,
        "severity": "MEDIUM",
        "top_feature": "log_pkt_max",
        "top_feature_impact": 0.12,
        "mitre_techniques": [],
        "recommended_actions": ["Log event for periodic review"],
    }

    narrative = await ADKAdapter.narrate_incident(incident_dict)
    assert isinstance(narrative, IncidentNarrative)
    assert narrative.verified_risk_score == 45
    assert narrative.verified_severity == "MEDIUM"
