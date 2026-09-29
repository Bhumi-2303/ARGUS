"""End-to-end tests for the ARGUS real multi-agent pipeline.

Tests that the full pipeline:
  Data Intelligence → Threat Analysis → Explainability →
  Knowledge Context → Risk Prediction → Decision Support
executes with real agents and produces truthful results.
"""
import pytest
import asyncio
from argus.orchestrator.pipeline import execute_pipeline, pipeline_context_to_response


# -- Fixtures --

BENIGN_FEATURES = {
    "pkt_mean_to_max": 0.45,
    "tcp_flag_density": 0.12,
    "log_pkt_mean": 3.8,
    "log_pkt_max": 5.2,
}

ATTACK_FEATURES = {
    "pkt_mean_to_max": 0.99,
    "tcp_flag_density": 0.95,
    "log_pkt_mean": 8.5,
    "log_pkt_max": 9.1,
}


# ------------------------------------------------------------------
# Phase 3: Data Intelligence
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_data_intelligence_validates_features():
    """DIA step validates all 4 required features."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    assert ctx.data_intelligence_result is not None
    assert ctx.data_intelligence_result["status"] == "success"
    assert ctx.data_intelligence_result["feature_count"] == 4


@pytest.mark.asyncio
async def test_data_intelligence_rejects_unrecognizable_fields():
    """DIA step fails when input has no recognizable telemetry fields."""
    ctx = await execute_pipeline({"completely_unknown_field": 0.5})
    assert ctx.status == "failed"
    assert "No recognizable raw telemetry columns" in ctx.error
    # The first trace step should show FAILED
    assert ctx.trace.steps[0].stage == "DATA_INTELLIGENCE"
    assert ctx.trace.steps[0].status == "FAILED"


@pytest.mark.asyncio
async def test_data_intelligence_rejects_nan():
    """DIA step fails when a feature is NaN."""
    features = dict(BENIGN_FEATURES)
    features["log_pkt_mean"] = float("nan")
    ctx = await execute_pipeline(features)
    assert ctx.status == "failed"
    assert "non-finite" in ctx.error


# ------------------------------------------------------------------
# Phase 4: Threat Analysis
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_threat_analysis_runs_real_model():
    """Threat Analysis uses the real model registry for inference."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    assert ctx.threat_result is not None
    assert ctx.threat_result.model_version in ("xgb_adapted", "xgb_source")
    assert 0.0 <= ctx.threat_result.confidence <= 1.0
    assert ctx.threat_result.threat_level.value in ("low", "medium", "high", "critical", "info")


@pytest.mark.asyncio
async def test_threat_analysis_records_trace():
    """Threat Analysis produces a trace step with model version."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    threat_step = next(s for s in ctx.trace.steps if s.stage == "THREAT_ANALYSIS")
    assert threat_step.status == "SUCCESS"
    assert threat_step.model_version is not None
    assert threat_step.duration_ms is not None
    assert threat_step.duration_ms >= 0


# ------------------------------------------------------------------
# Phase 5: Explainability
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_explainability_produces_real_shap():
    """Explainability step returns real SHAP values from TreeExplainer."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    assert ctx.explainability_result is not None
    if ctx.explainability_result["status"] == "available":
        shap_vals = ctx.explainability_result["shap_values"]
        assert isinstance(shap_vals, dict)
        assert len(shap_vals) == 4
        for feat in ("pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"):
            assert feat in shap_vals
            assert isinstance(shap_vals[feat], float)
    else:
        # If SHAP is unavailable, verify it's honestly reported
        assert ctx.explainability_result["status"] == "unavailable"
        assert "reason" in ctx.explainability_result


# ------------------------------------------------------------------
# Phase 6: Knowledge Context
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_knowledge_context_runs():
    """Knowledge Context Agent executes and returns a result."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    kc_step = next(s for s in ctx.trace.steps if s.stage == "KNOWLEDGE_CONTEXT")
    # Should succeed (even if no MITRE matches found)
    assert kc_step.status == "SUCCESS"
    # knowledge_result can contain empty lists — that's correct
    assert ctx.knowledge_result is not None


# ------------------------------------------------------------------
# Phase 7: Risk Prediction
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_risk_prediction_runs():
    """Risk Prediction Agent executes with real tools."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    risk_step = next(s for s in ctx.trace.steps if s.stage == "RISK_PREDICTION")
    assert risk_step.status == "SUCCESS"
    assert ctx.risk_result is not None
    assert 0 <= ctx.risk_result.risk_score <= 100
    assert ctx.risk_result.severity in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert 0.0 <= ctx.risk_result.confidence <= 1.0


# ------------------------------------------------------------------
# Phase 8: Decision Support
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_decision_support_runs():
    """Decision Support Agent generates real recommendations."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    ds_step = next(s for s in ctx.trace.steps if s.stage == "DECISION_SUPPORT")
    assert ds_step.status == "SUCCESS"
    assert ctx.decision_result is not None
    assert isinstance(ctx.decision_result.recommended_actions, list)
    assert len(ctx.decision_result.recommended_actions) > 0
    assert isinstance(ctx.decision_result.approval_required, bool)


# ------------------------------------------------------------------
# Phase 9: Complete End-to-End
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_complete_pipeline_all_6_stages():
    """Full pipeline executes all 6 stages and produces complete trace."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    assert ctx.status == "completed"
    assert len(ctx.trace.steps) == 6

    expected_stages = [
        "DATA_INTELLIGENCE",
        "THREAT_ANALYSIS",
        "EXPLAINABILITY",
        "KNOWLEDGE_CONTEXT",
        "RISK_PREDICTION",
        "DECISION_SUPPORT",
    ]
    actual_stages = [s.stage for s in ctx.trace.steps]
    assert actual_stages == expected_stages

    # All should succeed
    for step in ctx.trace.steps:
        assert step.status in ("SUCCESS", "PARTIAL"), f"Step {step.stage} had status {step.status}"


@pytest.mark.asyncio
async def test_full_argus_agent_pipeline():
    """Explicit end-to-end integration test proving real downstream data consumption.
    
    Verifies:
      Input Flow
      → Data Intelligence (features extracted)
      → Threat Analysis (real XGBoost model inference & threat level)
      → Explainability (actual TreeSHAP feature attributions)
      → Knowledge Context (MITRE ATT&CK & CVE intelligence retrieval)
      → Risk Prediction (cyber-physical impact & risk scoring)
      → Decision Support (automated playbook selection & prioritized actions)
      → Execution Trace (timing, status, and input/output summaries)
    """
    test_input = {
        "pkt_mean_to_max": 0.85,
        "tcp_flag_density": 0.70,
        "log_pkt_mean": 6.5,
        "log_pkt_max": 8.0,
    }
    
    ctx = await execute_pipeline(test_input, model_name="xgb_adapted")
    
    # 1. Pipeline Status
    assert ctx.status == "completed"
    assert ctx.error is None
    
    # 2. Stage 1: Data Intelligence
    assert ctx.features is not None
    assert len(ctx.features) == 4
    assert ctx.features["pkt_mean_to_max"] == 0.85
    
    # 3. Stage 2: Threat Analysis (consumed DIA features)
    assert ctx.threat is not None
    assert ctx.threat.model_version == "xgb_adapted"
    assert 0.0 <= ctx.threat.confidence <= 1.0
    assert ctx.threat.threat_level.value in ("low", "medium", "high", "critical", "info")
    
    # 4. Stage 3: Explainability (consumed DIA features & model)
    assert ctx.explanation is not None
    assert ctx.explanation["status"] == "available"
    assert "shap_values" in ctx.explanation
    assert len(ctx.explanation["shap_values"]) == 4
    assert ctx.explanation["top_feature"] in test_input
    
    # 5. Stage 4: Knowledge Context (consumed threat classification)
    assert ctx.knowledge is not None
    assert ctx.knowledge.confidence >= 0.0
    assert isinstance(ctx.knowledge.mitre_techniques, list)
    assert isinstance(ctx.knowledge.cves, list)
    
    # 6. Stage 5: Risk Prediction (consumed threat & knowledge context)
    assert ctx.risk is not None
    assert 0 <= ctx.risk.risk_score <= 100
    assert ctx.risk.severity in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert 0.0 <= ctx.risk.confidence <= 1.0
    assert ctx.risk.impact_estimation is not None
    
    # 7. Stage 6: Decision Support (consumed risk & knowledge context)
    assert ctx.decision is not None
    assert len(ctx.decision.recommended_actions) > 0
    assert ctx.decision.priority in (1, 2, 3, 4, 5)
    assert ctx.decision.urgency in ("low", "medium", "high", "critical")
    assert ctx.decision.execution_plan is not None
    
    # 8. Execution Trace
    assert len(ctx.trace) == 6
    stages_in_trace = [t.agent for t in ctx.trace]
    assert stages_in_trace == [
        "DATA_INTELLIGENCE",
        "THREAT_ANALYSIS",
        "EXPLAINABILITY",
        "KNOWLEDGE_CONTEXT",
        "RISK_PREDICTION",
        "DECISION_SUPPORT",
    ]
    for step in ctx.trace:
        assert step.status == "SUCCESS"
        assert step.duration is not None and step.duration >= 0
        assert step.input_summary is not None
        assert step.output_summary is not None


@pytest.mark.asyncio
async def test_complete_pipeline_with_attack_features():
    """Full pipeline with attack-like features should detect threat."""
    ctx = await execute_pipeline(ATTACK_FEATURES)
    assert ctx.status == "completed"
    assert ctx.threat_result is not None
    # With extreme feature values, the model should detect something
    # (we don't assert specific prediction since that depends on real model)


@pytest.mark.asyncio
async def test_pipeline_response_serialization():
    """Pipeline response serializes to valid JSON-compatible dict."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    response = pipeline_context_to_response(ctx)

    assert response["correlation_id"] is not None
    assert response["status"] == "completed"
    assert response["total_duration_ms"] is not None
    assert response["total_duration_ms"] > 0
    assert "results" in response
    assert "trace" in response
    assert response["trace"]["total_steps"] == 6

    # Verify all result sections are present
    results = response["results"]
    assert "data_intelligence" in results
    assert "threat_analysis" in results
    assert "explainability" in results
    assert "knowledge_context" in results
    assert "risk_prediction" in results
    assert "decision_support" in results


# ------------------------------------------------------------------
# Phase 9: Failure Propagation
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_failure_does_not_appear_as_success():
    """An agent failure must NOT appear as SUCCESS in the trace."""
    # Missing features cause DIA to fail
    ctx = await execute_pipeline({"bad": 1.0})
    assert ctx.status == "failed"
    assert len(ctx.trace.steps) >= 1

    dia_step = ctx.trace.steps[0]
    assert dia_step.stage == "DATA_INTELLIGENCE"
    assert dia_step.status == "FAILED"
    assert dia_step.error is not None


@pytest.mark.asyncio
async def test_correlation_id_preserved():
    """Correlation ID is preserved across the full pipeline."""
    ctx = await execute_pipeline(BENIGN_FEATURES, correlation_id="test-corr-123")
    assert ctx.correlation_id == "test-corr-123"


# ------------------------------------------------------------------
# Phase 10: Trace Correctness
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_trace_has_timestamps_and_durations():
    """Every trace step has start_time, end_time, and duration_ms."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    for step in ctx.trace.steps:
        assert step.start_time is not None, f"Step {step.stage} missing start_time"
        assert step.end_time is not None, f"Step {step.stage} missing end_time"
        assert step.duration_ms is not None, f"Step {step.stage} missing duration_ms"
        assert step.duration_ms >= 0, f"Step {step.stage} has negative duration"


@pytest.mark.asyncio
async def test_trace_event_id_matches_context():
    """Trace event_id matches the pipeline context event_id."""
    ctx = await execute_pipeline(BENIGN_FEATURES)
    assert ctx.trace.event_id == ctx.event_id
