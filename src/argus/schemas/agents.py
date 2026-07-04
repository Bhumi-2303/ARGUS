"""Agent schemas for registry and metadata."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from argus.core.enums import AgentStatus


class AgentCapabilities(BaseModel):
    """Capabilities of an agent."""
    capabilities: List[str] = Field(default_factory=list)


class AgentRegistration(BaseModel):
    """Registration information for an agent."""
    agent_id: str
    name: str
    version: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    registered_at: datetime = Field(default_factory=datetime.utcnow)


class AgentHealthReport(BaseModel):
    """Health and status report for an agent."""
    agent_id: str
    status: AgentStatus
    uptime: float
    tasks_completed: int
    tasks_failed: int
    memory_usage_mb: float
    last_heartbeat: datetime
    error_message: Optional[str] = None
