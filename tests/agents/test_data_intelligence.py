"""Tests for the Data Intelligence Agent single-flow processing.

Covers:
- Pre-computed feature validation
- Raw telemetry → feature extraction via extract_four_features()
- Structured error reporting
- Correlation/event ID preservation
- DIA → Threat Analysis Agent integration (real model inference)
"""
import math
import pytest
from argus.agents.data_intelligence.agent import DataIntelligenceAgent
from argus.agents.data_intelligence.schemas import FlowInput, FlowResult
from argus.features.extractor import FEATURE_NAMES
from argus.registry.model_registry import HARMONIZED_FEATURES


# ----- helpers -----

async def _make_dia() -> DataIntelligenceAgent:
    dia = DataIntelligenceAgent(
        agent_id="test-di-01",
        name="test_di",
        version="1.0.0",
        description="Test agent",
        capabilities=["data:ingest"],
        permissions=["data:read", "data:write"],
        tools=[],
    )
    await dia.initialize()
    return dia


# =====================================================================
# Existing tests — preserved
# =====================================================================

@pytest.mark.asyncio
async def test_data_intelligence_agent_initialization():
    agent = await _make_dia()
    assert agent.pipeline is not None
    await agent.shutdown()


@pytest.mark.asyncio
async def test_data_intelligence_agent_validation():
    agent = await _make_dia()
    assert await agent.validate({"file_path": "non_existent.csv"}) is False
    assert await agent.validate({"file_path": "invalid.txt"}) is False


@pytest.mark.asyncio
async def test_data_intelligence_agent_reasoning():
    agent = await _make_dia()
    reasoning = await agent.reason({
        "pipeline_config": {"chunk_size": 100, "normalization_method": "min_max"},
    })
    assert reasoning["config"].chunk_size == 100
    assert reasoning["config"].normalization_method == "min_max"


@pytest.mark.asyncio
async def test_data_intelligence_agent_planning():
    agent = await _make_dia()
    reasoning = await agent.reason({
        "pipeline_config": {"chunk_size": 100},
    })
    plan = await agent.plan(reasoning)
    assert plan["stages"] == ["load", "validate", "clean", "normalize", "extract", "publish"]
    assert plan["config"].chunk_size == 100


# =====================================================================
# Pre-computed feature path
# =====================================================================

@pytest.mark.asyncio
async def test_precomputed_features_success():
    """Passes the 4 harmonized features — DIA validates and returns them."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        correlation_id="corr-1",
        event_id="evt-1",
        source_domain="nfton",
        fields={
            "pkt_mean_to_max": 0.45,
            "tcp_flag_density": 0.12,
            "log_pkt_mean": 3.8,
            "log_pkt_max": 5.2,
        },
    ))
    assert result.status == "success"
    assert result.feature_source == "pre_computed"
    assert set(result.features.keys()) == set(HARMONIZED_FEATURES)
    assert result.features["pkt_mean_to_max"] == 0.45
    assert result.features["tcp_flag_density"] == 0.12
    assert result.features["log_pkt_mean"] == 3.8
    assert result.features["log_pkt_max"] == 5.2
    assert result.error is None


@pytest.mark.asyncio
async def test_precomputed_preserves_ids():
    """Correlation and event IDs propagate to the result."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        correlation_id="trace-abc",
        event_id="evt-xyz",
        fields={"pkt_mean_to_max": 0.5, "tcp_flag_density": 0.1,
                "log_pkt_mean": 2.0, "log_pkt_max": 3.0},
    ))
    assert result.correlation_id == "trace-abc"
    assert result.event_id == "evt-xyz"


@pytest.mark.asyncio
async def test_precomputed_nan_rejected():
    """NaN feature value is rejected with structured error."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        fields={"pkt_mean_to_max": float("nan"), "tcp_flag_density": 0.1,
                "log_pkt_mean": 2.0, "log_pkt_max": 3.0},
    ))
    assert result.status == "error"
    assert result.features == {}
    assert result.error is not None
    assert result.error.error_type == "value_error"
    assert "non-finite" in result.error.error


@pytest.mark.asyncio
async def test_precomputed_inf_rejected():
    """Inf feature value is rejected."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        fields={"pkt_mean_to_max": float("inf"), "tcp_flag_density": 0.1,
                "log_pkt_mean": 2.0, "log_pkt_max": 3.0},
    ))
    assert result.status == "error"
    assert result.error.error_type == "value_error"


@pytest.mark.asyncio
async def test_precomputed_non_numeric_rejected():
    """String feature value is rejected."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        fields={"pkt_mean_to_max": "abc", "tcp_flag_density": 0.1,
                "log_pkt_mean": 2.0, "log_pkt_max": 3.0},
    ))
    assert result.status == "error"
    assert result.error.error_type == "type_error"


@pytest.mark.asyncio
async def test_precomputed_records_metadata():
    """Processing metadata is recorded."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        fields={"pkt_mean_to_max": 0.5, "tcp_flag_density": 0.1,
                "log_pkt_mean": 2.0, "log_pkt_max": 3.0},
    ))
    assert result.processing_duration_ms >= 0
    assert result.input_field_count == 4


# =====================================================================
# Raw telemetry → feature extraction path
# =====================================================================

@pytest.mark.asyncio
async def test_raw_telemetry_ciciot_format():
    """Raw CICIoT-style columns produce correct harmonized features."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        source_domain="ciciot",
        fields={
            "Pkt Len Mean": 500.0,
            "Pkt Len Max": 1000.0,
            "fin_flag_number": 1,
            "syn_flag_number": 0,
            "rst_flag_number": 0,
            "psh_flag_number": 1,
            "ack_flag_number": 1,
        },
    ))
    assert result.status == "success"
    assert result.feature_source == "extracted"
    assert set(result.features.keys()) == set(FEATURE_NAMES)

    # pkt_mean_to_max = 500/1000 = 0.5
    assert abs(result.features["pkt_mean_to_max"] - 0.5) < 1e-6
    # tcp_flag_density = 1+0+0+1+1 = 3
    assert result.features["tcp_flag_density"] == 3.0
    # log_pkt_mean = log1p(500)
    import numpy as np
    assert abs(result.features["log_pkt_mean"] - np.log1p(500.0)) < 1e-6
    # log_pkt_max = log1p(1000)
    assert abs(result.features["log_pkt_max"] - np.log1p(1000.0)) < 1e-6


@pytest.mark.asyncio
async def test_raw_telemetry_header_length_format():
    """Header_Length / Duration fallback path works."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        fields={
            "Header_Length": 200.0,
            "Duration": 50.0,
            "Rate": 100.0,
            "Size": 800.0,
        },
    ))
    assert result.status == "success"
    assert result.feature_source == "extracted"
    # pkt_mean_to_max uses Duration/Header_Length = 50/200 = 0.25
    assert abs(result.features["pkt_mean_to_max"] - 0.25) < 1e-6


@pytest.mark.asyncio
async def test_unrecognizable_raw_fields_rejected():
    """Fields with no extractable columns produce a structured error."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        fields={"random_col_a": 1.0, "random_col_b": 2.0},
    ))
    assert result.status == "error"
    assert result.error.error_type == "missing_fields"
    assert "No recognizable raw telemetry columns" in result.error.error


@pytest.mark.asyncio
async def test_error_includes_received_and_required_fields():
    """Error result lists both received and required fields."""
    dia = await _make_dia()
    result = await dia.process_flow(FlowInput(
        fields={"bad_field": 1.0},
    ))
    assert result.status == "error"
    assert "bad_field" in result.error.received_fields
    assert set(result.error.required_fields) == set(HARMONIZED_FEATURES)


# =====================================================================
# DIA → Threat Analysis integration (acceptance test)
# =====================================================================

@pytest.mark.asyncio
async def test_dia_to_threat_analysis_precomputed():
    """Pre-computed features flow from DIA directly to TAA with real inference."""
    from argus.agents.threat_analysis.agent import ThreatAnalysisAgent
    from argus.agents.threat_analysis.models.schemas import ThreatAnalysisResult
    from argus.registry.model_registry import model_registry

    if not model_registry.is_loaded:
        model_registry.load_all()

    # Step 1: DIA processes the flow
    dia = await _make_dia()
    dia_result = await dia.process_flow(FlowInput(
        correlation_id="integration-test-01",
        event_id="evt-int-01",
        source_domain="nfton",
        fields={
            "pkt_mean_to_max": 0.45,
            "tcp_flag_density": 0.12,
            "log_pkt_mean": 3.8,
            "log_pkt_max": 5.2,
        },
    ))
    assert dia_result.status == "success"

    # Step 2: TAA consumes the DIA output directly — no manual modification
    taa = ThreatAnalysisAgent()
    await taa.initialize()
    reasoning = await taa.reason({
        "event_id": dia_result.event_id,
        "source": "data_intelligence",
        "features": dia_result.features,
        "timestamp": "2026-09-29T00:00:00Z",
    })
    result = await taa.execute(reasoning)

    assert isinstance(result, ThreatAnalysisResult)
    assert result.source_event_id == "evt-int-01"
    assert 0.0 <= result.confidence <= 1.0
    assert result.threat_level.value in ("low", "medium", "high", "critical", "info")
    assert result.model_version in ("xgb_adapted", "xgb_source")


@pytest.mark.asyncio
async def test_dia_to_threat_analysis_raw_telemetry():
    """Raw telemetry → DIA extraction → TAA inference, no manual feature modification."""
    from argus.agents.threat_analysis.agent import ThreatAnalysisAgent
    from argus.agents.threat_analysis.models.schemas import ThreatAnalysisResult
    from argus.registry.model_registry import model_registry

    if not model_registry.is_loaded:
        model_registry.load_all()

    # Step 1: DIA extracts features from raw telemetry
    dia = await _make_dia()
    dia_result = await dia.process_flow(FlowInput(
        correlation_id="integration-test-02",
        event_id="evt-int-02",
        source_domain="ciciot",
        fields={
            "Pkt Len Mean": 500.0,
            "Pkt Len Max": 1000.0,
            "fin_flag_number": 1,
            "syn_flag_number": 0,
            "rst_flag_number": 0,
            "psh_flag_number": 1,
            "ack_flag_number": 1,
        },
    ))
    assert dia_result.status == "success"
    assert dia_result.feature_source == "extracted"

    # Step 2: Feed DIA output directly to TAA — no manual modification
    taa = ThreatAnalysisAgent()
    await taa.initialize()
    reasoning = await taa.reason({
        "event_id": dia_result.event_id,
        "source": "data_intelligence",
        "features": dia_result.features,
        "timestamp": "2026-09-29T00:00:00Z",
    })
    result = await taa.execute(reasoning)

    assert isinstance(result, ThreatAnalysisResult)
    assert 0.0 <= result.confidence <= 1.0
    # The features were EXTRACTED, not pre-computed — verify they all exist
    for f in HARMONIZED_FEATURES:
        assert f in dia_result.features, f"Feature {f} missing from DIA output"


# =====================================================================
# Full pipeline integration (DIA as real step)
# =====================================================================

@pytest.mark.asyncio
async def test_full_pipeline_with_raw_telemetry():
    """Full pipeline accepts raw telemetry — DIA extracts, rest proceeds."""
    from argus.orchestrator.pipeline import execute_pipeline

    ctx = await execute_pipeline(
        features={
            "Pkt Len Mean": 500.0,
            "Pkt Len Max": 1000.0,
            "fin_flag_number": 1,
            "syn_flag_number": 0,
            "psh_flag_number": 1,
            "ack_flag_number": 1,
        },
    )
    assert ctx.status == "completed", f"Pipeline failed: {ctx.error}"
    assert ctx.data_intelligence_result["feature_source"] == "extracted"
    assert len(ctx.trace.steps) == 6
    assert ctx.threat_result is not None


@pytest.mark.asyncio
async def test_full_pipeline_with_precomputed():
    """Full pipeline accepts pre-computed features — DIA validates."""
    from argus.orchestrator.pipeline import execute_pipeline

    ctx = await execute_pipeline(
        features={
            "pkt_mean_to_max": 0.45,
            "tcp_flag_density": 0.12,
            "log_pkt_mean": 3.8,
            "log_pkt_max": 5.2,
        },
    )
    assert ctx.status == "completed", f"Pipeline failed: {ctx.error}"
    assert ctx.data_intelligence_result["feature_source"] == "pre_computed"
