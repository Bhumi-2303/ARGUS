"""Message schemas for inter-component communication."""
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from argus.core.enums import MessageType, TaskPriority


class BaseMessage(BaseModel):
    """Base class for all messages in the system."""
    request_id: str = Field(..., description="Unique request identifier")
    trace_id: str = Field(..., description="Distributed trace ID")
    agent_id: str = Field(..., description="Source agent identifier")
    timestamp: datetime = Field(..., description="UTC timestamp")
    priority: TaskPriority = Field(..., description="Message priority")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    signature: Optional[str] = Field(default=None, description="HMAC signature")
    version: str = Field(default="1.0.0", description="Protocol version")


class AgentMessage(BaseMessage):
    """Message sent between agents (via orchestrator/blackboard)."""
    target_agent_id: Optional[str] = Field(default=None, description="Optional target agent")


class EventMessage(BaseMessage):
    """System event broadcast message."""
    event_type: str = Field(..., description="Type of event")


class ResponseMessage(BaseMessage):
    """Response to a previous message."""
    in_response_to: str = Field(..., description="Request ID of the original message")


class Heartbeat(BaseMessage):
    """Agent heartbeat message."""
    status: str = Field(..., description="Current agent status")


class TaskRequest(BaseMessage):
    """Request to execute a task."""
    task_type: str = Field(..., description="Type of task to execute")


class TaskResult(BaseMessage):
    """Result of a task execution."""
    task_id: str = Field(..., description="ID of the completed task")
    success: bool = Field(..., description="Whether the task succeeded")


class StatusUpdate(BaseMessage):
    """Update on the status of an ongoing task."""
    task_id: str = Field(..., description="ID of the task")
    progress: float = Field(..., description="Progress percentage (0-100)")


class Alert(BaseMessage):
    """Security or system alert."""
    severity: str = Field(..., description="Alert severity (e.g., critical, warning)")
    description: str = Field(..., description="Alert description")
