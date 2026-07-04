"""Task schemas for orchestration."""
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from argus.core.enums import TaskPriority, TaskStatus


class TaskDefinition(BaseModel):
    """Definition of a task to be executed."""
    task_type: str
    required_capabilities: List[str] = Field(default_factory=list)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    timeout: int = Field(default=300)
    dependencies: List[str] = Field(default_factory=list)
    payload: Dict[str, Any] = Field(default_factory=dict)


class TaskAssignment(BaseModel):
    """Assignment of a task to an agent."""
    task_id: str
    agent_id: str
    assigned_at: datetime = Field(default_factory=datetime.utcnow)


class TaskProgress(BaseModel):
    """Progress update for a task."""
    task_id: str
    status: TaskStatus
    progress_pct: float = Field(ge=0.0, le=100.0)
    status_message: str


class TaskCompletion(BaseModel):
    """Result of a completed task."""
    task_id: str
    status: TaskStatus
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    duration: float
    metrics: Dict[str, float] = Field(default_factory=dict)
