"""Health and monitoring schemas."""
from typing import Any, Dict, Optional
from pydantic import BaseModel

from argus.core.enums import AgentStatus


class HealthStatus(BaseModel):
    """General health status representation."""
    status: AgentStatus
    message: str
    checks: Dict[str, Any] = {}


class ComponentHealth(BaseModel):
    """Health status of an individual system component."""
    name: str
    healthy: bool
    status: str
    details: Dict[str, Any] = {}
    last_checked: str


class SystemHealth(BaseModel):
    """Aggregated health status of the entire system."""
    status: str
    uptime: float
    components: Dict[str, ComponentHealth] = {}
    timestamp: str
