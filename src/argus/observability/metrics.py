"""Metrics tracking."""
import structlog
from typing import Dict, Any
from datetime import datetime, timezone

logger = structlog.get_logger("argus.metrics")

class MetricsTracker:
    """Tracks application metrics."""
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        
    def increment(self, name: str, value: int = 1, tags: Dict[str, str] = None) -> None:
        key = self._format_key(name, tags)
        self.counters[key] = self.counters.get(key, 0) + value
        
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        key = self._format_key(name, tags)
        self.gauges[key] = value
        
    def _format_key(self, name: str, tags: Dict[str, str] = None) -> str:
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
        
    def log_metrics(self) -> None:
        logger.info("system_metrics", counters=self.counters, gauges=self.gauges)

metrics = MetricsTracker()
