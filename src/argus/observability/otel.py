"""OpenTelemetry integration for ARGUS with optional Grafana Cloud export.

Provides:
- Request latency histogram
- Per-agent duration histogram
- Pipeline success/skip/failed stage rates
- Feature distribution drift metrics (KS and PSI)
- Optional OTLP gRPC/HTTP export to Grafana Cloud (off by default)
"""

import os
from typing import Optional, Dict, Any
from structlog import get_logger

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    InMemoryMetricReader,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

logger = get_logger("argus.observability.otel")

_METER_INITIALIZED = False
_IN_MEMORY_READER: Optional[InMemoryMetricReader] = None

# Metric Instruments
request_latency_hist = None
agent_duration_hist = None
pipeline_stage_counter = None
ks_drift_gauge = None
psi_drift_gauge = None


def is_otel_enabled() -> bool:
    """Check if OpenTelemetry / Grafana Cloud export is enabled via environment variables."""
    # Off by default
    v1 = os.getenv("ARGUS_OTEL_ENABLED", "").lower()
    v2 = os.getenv("OTEL_METRICS_ENABLED", "").lower()
    return v1 in ("true", "1", "yes", "on") or v2 in ("true", "1", "yes", "on")


def setup_opentelemetry(service_name: str = "argus-platform") -> None:
    """Initialize OpenTelemetry MeterProvider and TracerProvider with optional Grafana Cloud export."""
    global _METER_INITIALIZED, _IN_MEMORY_READER
    global \
        request_latency_hist, \
        agent_duration_hist, \
        pipeline_stage_counter, \
        ks_drift_gauge, \
        psi_drift_gauge

    if _METER_INITIALIZED:
        return

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "production"),
        }
    )

    readers = []

    # 1. In-memory reader always registered for internal diagnostics and testing
    _IN_MEMORY_READER = InMemoryMetricReader()
    readers.append(_IN_MEMORY_READER)

    # 2. Optional Grafana Cloud OTLP Exporter (off by default)
    if is_otel_enabled():
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
        headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")

        # Check Grafana Cloud specific credentials fallback
        if not endpoint and os.getenv("GRAFANA_CLOUD_OTLP_ENDPOINT"):
            endpoint = os.getenv("GRAFANA_CLOUD_OTLP_ENDPOINT")
            instance_id = os.getenv("GRAFANA_CLOUD_INSTANCE_ID", "")
            api_key = os.getenv("GRAFANA_CLOUD_API_KEY", "")
            if instance_id and api_key:
                import base64

                auth_header = base64.b64encode(f"{instance_id}:{api_key}".encode()).decode()
                headers = f"Authorization=Basic {auth_header}"

        if endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
                    OTLPMetricExporter,
                )

                otlp_headers = {}
                if headers:
                    for part in headers.split(","):
                        if "=" in part:
                            k, v = part.split("=", 1)
                            otlp_headers[k.strip()] = v.strip()

                exporter = OTLPMetricExporter(endpoint=endpoint, headers=otlp_headers)
                otlp_reader = PeriodicExportingMetricReader(exporter, export_interval_millis=15000)
                readers.append(otlp_reader)
                logger.info("otel_grafana_cloud_exporter_initialized", endpoint=endpoint)
            except Exception as ex:
                logger.warning("otel_exporter_init_failed", error=str(ex))
        else:
            logger.info("otel_enabled_without_remote_endpoint")
    else:
        logger.info("otel_export_disabled_by_default")

    # Set Global MeterProvider
    meter_provider = MeterProvider(resource=resource, metric_readers=readers)
    metrics.set_meter_provider(meter_provider)

    # Set Global TracerProvider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    meter = metrics.get_meter("argus.platform", "1.0.0")

    # Instrument 1: Request latency histogram (ms)
    request_latency_hist = meter.create_histogram(
        name="argus_request_latency_ms",
        description="HTTP request processing latency in milliseconds",
        unit="ms",
    )

    # Instrument 2: Per-agent duration histogram (ms)
    agent_duration_hist = meter.create_histogram(
        name="argus_agent_duration_ms",
        description="Execution duration of individual ARGUS agents in milliseconds",
        unit="ms",
    )

    # Instrument 3: Pipeline stage outcome counter (success, skipped, failed)
    pipeline_stage_counter = meter.create_counter(
        name="argus_pipeline_stage_total",
        description="Count of pipeline stage executions by outcome status",
        unit="1",
    )

    # Instrument 4: Distribution drift statistics (KS and PSI)
    ks_drift_gauge = meter.create_histogram(
        name="argus_drift_ks_statistic",
        description="Empirical Kolmogorov-Smirnov distribution drift statistic",
        unit="1",
    )

    psi_drift_gauge = meter.create_histogram(
        name="argus_drift_psi_statistic",
        description="Population Stability Index (PSI) drift metric",
        unit="1",
    )

    _METER_INITIALIZED = True


def record_request_latency(path: str, method: str, status_code: int, duration_ms: float) -> None:
    """Record HTTP request latency with endpoint dimensions."""
    if request_latency_hist is not None:
        request_latency_hist.record(
            duration_ms,
            {"http.route": path, "http.method": method, "http.status_code": str(status_code)},
        )


def record_agent_duration(agent_name: str, status: str, duration_ms: float) -> None:
    """Record execution duration of an individual agent stage."""
    if agent_duration_hist is not None:
        agent_duration_hist.record(duration_ms, {"agent.name": agent_name, "agent.status": status})


def record_pipeline_stage_outcome(agent_name: str, status: str) -> None:
    """Record pipeline stage outcome counter increment (SUCCESS, SKIPPED, FAILED)."""
    if pipeline_stage_counter is not None:
        pipeline_stage_counter.add(1, {"agent.name": agent_name, "agent.status": status})


def record_drift_metrics(
    feature_name: str, domain: str, ks_statistic: float, psi_statistic: float
) -> None:
    """Record distribution drift metrics for a feature."""
    if ks_drift_gauge is not None:
        ks_drift_gauge.record(ks_statistic, {"feature.name": feature_name, "target.domain": domain})
    if psi_drift_gauge is not None:
        psi_drift_gauge.record(
            psi_statistic, {"feature.name": feature_name, "target.domain": domain}
        )


def get_collected_metrics() -> Dict[str, Any]:
    """Retrieve collected metrics from in-memory reader for testing and diagnostics."""
    if _IN_MEMORY_READER is None:
        return {}
    data = _IN_MEMORY_READER.get_metrics_data()
    return {"metrics_count": len(data.resource_metrics) if data else 0, "data": data}
