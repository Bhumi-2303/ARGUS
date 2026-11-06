"""Metrics tracking facade integrating in-memory counters with OpenTelemetry."""

from typing import Dict, Optional
import structlog

from .otel import (
    setup_opentelemetry,
    record_request_latency,
    record_agent_duration,
    record_pipeline_stage_outcome,
    record_drift_metrics,
)

logger = structlog.get_logger("argus.metrics")


class MetricsTracker:
    """Tracks application metrics and bridges to OpenTelemetry instruments."""

    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        # Ensure OpenTelemetry is initialized
        try:
            setup_opentelemetry()
        except Exception as ex:
            logger.warning("opentelemetry_auto_init_skipped", error=str(ex))

    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        key = self._format_key(name, tags)
        self.counters[key] = self.counters.get(key, 0) + value

    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        key = self._format_key(name, tags)
        self.gauges[key] = value

    def record_latency(self, path: str, method: str, status_code: int, duration_ms: float) -> None:
        """Record HTTP endpoint latency in both in-memory gauges and OpenTelemetry."""
        key = f"http_request_duration_ms[{method} {path}]"
        self.gauges[key] = duration_ms
        record_request_latency(path, method, status_code, duration_ms)

    def record_agent_execution(self, agent_name: str, status: str, duration_ms: float) -> None:
        """Record agent duration and outcome status in OpenTelemetry and in-memory counters."""
        self.increment("agent_stage_executions", 1, {"agent": agent_name, "status": status})
        self.gauge(f"agent_duration_ms[{agent_name}]", duration_ms)
        record_agent_duration(agent_name, status, duration_ms)
        record_pipeline_stage_outcome(agent_name, status)

    def record_drift(
        self, feature_name: str, domain: str, ks_statistic: float, psi_statistic: float
    ) -> None:
        """Record KS and PSI drift metrics in both in-memory gauges and OpenTelemetry."""
        self.gauge("drift_ks_statistic", ks_statistic, {"feature": feature_name, "domain": domain})
        self.gauge(
            "drift_psi_statistic", psi_statistic, {"feature": feature_name, "domain": domain}
        )
        record_drift_metrics(feature_name, domain, ks_statistic, psi_statistic)

    def _format_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"

    def log_metrics(self) -> None:
        logger.info("system_metrics", counters=self.counters, gauges=self.gauges)


# Authoritative singleton metrics instance
metrics = MetricsTracker()
