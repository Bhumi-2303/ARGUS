"""Metrics schemas."""
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class MetricPoint(BaseModel):
    """A single metric data point."""
    name: str
    value: float
    timestamp: str
    labels: Dict[str, str] = Field(default_factory=dict)


class MetricSeries(BaseModel):
    """A series of metric points."""
    name: str
    points: List[MetricPoint] = Field(default_factory=list)


class AgentMetrics(BaseModel):
    """Aggregated metrics for a specific agent."""
    agent_id: str
    tasks_completed: int
    tasks_failed: int
    avg_latency_ms: float
    error_rate: float


class SystemMetrics(BaseModel):
    """Aggregated system-wide metrics."""
    total_tasks: int
    active_agents: int
    queue_depth: int
    system_latency_ms: float
    timestamp: str
