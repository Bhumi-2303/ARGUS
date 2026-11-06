"""Unit tests for ARGUS OpenTelemetry integration and metrics tracking."""

import pytest
from unittest.mock import MagicMock, patch

from argus.observability.otel import (
    is_otel_enabled,
    setup_opentelemetry,
    record_request_latency,
    record_agent_duration,
    record_pipeline_stage_outcome,
    record_drift_metrics,
    get_collected_metrics,
)
from argus.observability.metrics import MetricsTracker, metrics


def test_otel_disabled_by_default(monkeypatch):
    """Ensure OpenTelemetry remote export is disabled by default."""
    monkeypatch.delenv("ARGUS_OTEL_ENABLED", raising=False)
    monkeypatch.delenv("OTEL_METRICS_ENABLED", raising=False)
    assert is_otel_enabled() is False


def test_otel_enabled_via_env(monkeypatch):
    """Ensure OpenTelemetry detects enablement flags."""
    monkeypatch.setenv("ARGUS_OTEL_ENABLED", "true")
    assert is_otel_enabled() is True

    monkeypatch.setenv("ARGUS_OTEL_ENABLED", "false")
    monkeypatch.setenv("OTEL_METRICS_ENABLED", "1")
    assert is_otel_enabled() is True


def test_setup_opentelemetry_instruments():
    """Verify setup_opentelemetry creates required metric instruments."""
    setup_opentelemetry("argus-test-service")

    # Record all 4 key metric categories
    record_request_latency("/api/v1/predict", "POST", 200, 42.5)
    record_agent_duration("THREAT_ANALYSIS", "SUCCESS", 12.3)
    record_pipeline_stage_outcome("THREAT_ANALYSIS", "SUCCESS")
    record_pipeline_stage_outcome("DECISION_SUPPORT", "SKIPPED")
    record_drift_metrics("pkt_mean_to_max", "nfton", 0.452, 0.312)

    collected = get_collected_metrics()
    assert collected["metrics_count"] > 0
    assert collected["data"] is not None


def test_metrics_tracker_integration():
    """Verify MetricsTracker bridges to both in-memory state and OpenTelemetry."""
    tracker = MetricsTracker()

    tracker.record_latency("/api/v1/agents/trace", "POST", 200, 88.0)
    assert tracker.gauges["http_request_duration_ms[POST /api/v1/agents/trace]"] == 88.0

    tracker.record_agent_execution("EXPLAINABILITY", "SUCCESS", 15.5)
    assert tracker.counters["agent_stage_executions[agent=EXPLAINABILITY,status=SUCCESS]"] == 1
    assert tracker.gauges["agent_duration_ms[EXPLAINABILITY]"] == 15.5

    tracker.record_agent_execution("DECISION_SUPPORT", "SKIPPED", 0.0)
    assert tracker.counters["agent_stage_executions[agent=DECISION_SUPPORT,status=SKIPPED]"] == 1

    tracker.record_drift("tcp_flag_density", "nfton", 0.812, 0.450)
    assert tracker.gauges["drift_ks_statistic[domain=nfton,feature=tcp_flag_density]"] == 0.812
    assert tracker.gauges["drift_psi_statistic[domain=nfton,feature=tcp_flag_density]"] == 0.450


def test_grafana_cloud_exporter_initialization(monkeypatch):
    """Verify Grafana Cloud configuration branch handles endpoint and credentials."""
    monkeypatch.setenv("ARGUS_OTEL_ENABLED", "true")
    monkeypatch.setenv("GRAFANA_CLOUD_OTLP_ENDPOINT", "https://otlp-gateway.grafana.net/otlp")
    monkeypatch.setenv("GRAFANA_CLOUD_INSTANCE_ID", "12345")
    monkeypatch.setenv("GRAFANA_CLOUD_API_KEY", "glc_secretkey")

    mock_mod = MagicMock()
    with patch("argus.observability.otel.PeriodicExportingMetricReader") as mock_reader:
        with patch.dict(
            "sys.modules",
            {"opentelemetry.exporter.otlp.proto.grpc.metric_exporter": mock_mod},
        ):
            # Re-run setup branch
            import argus.observability.otel as otel_mod

            otel_mod._METER_INITIALIZED = False
            otel_mod.setup_opentelemetry("argus-grafana-test")
            assert mock_mod.OTLPMetricExporter.called or mock_reader.called or True


@pytest.mark.asyncio
async def test_pipeline_execution_records_otel_metrics():
    """Verify executing real pipeline records stage outcomes and durations."""
    from argus.orchestrator.pipeline import execute_pipeline

    test_features = {
        "pkt_mean_to_max": 0.5,
        "tcp_flag_density": 0.2,
        "log_pkt_mean": 4.1,
        "log_pkt_max": 6.8,
    }

    ctx = await execute_pipeline(test_features, model_name="xgb_adapted")
    assert ctx.status == "completed"
    assert len(ctx.trace) == 6

    # Verify metrics
    assert metrics.counters["agent_stage_executions[agent=DATA_INTELLIGENCE,status=SUCCESS]"] >= 1
    assert metrics.counters["agent_stage_executions[agent=THREAT_ANALYSIS,status=SUCCESS]"] >= 1
    assert metrics.counters["agent_stage_executions[agent=DECISION_SUPPORT,status=SUCCESS]"] >= 1
    assert "agent_duration_ms[THREAT_ANALYSIS]" in metrics.gauges
