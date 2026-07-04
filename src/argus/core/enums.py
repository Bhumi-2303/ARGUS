"""Shared enumerations for ARGUS platform."""
from enum import StrEnum


class AgentStatus(StrEnum):
    """Status of an agent."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class TaskStatus(StrEnum):
    """Lifecycle status of a task."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(StrEnum):
    """Priority levels for tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MessageType(StrEnum):
    """Types of messages in the system."""
    AGENT_MESSAGE = "agent_message"
    EVENT = "event"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"
    TASK_REQUEST = "task_request"
    TASK_RESULT = "task_result"
    STATUS_UPDATE = "status_update"
    ALERT = "alert"


class SecurityRole(StrEnum):
    """RBAC security roles."""
    ADMIN = "admin"
    OPERATOR = "operator"
    AGENT = "agent"
    VIEWER = "viewer"
    TOOL = "tool"


class BlackboardSection(StrEnum):
    """Sections of the shared blackboard."""
    TASK_QUEUE = "task_queue"
    COMPLETED_TASKS = "completed_tasks"
    SHARED_CONTEXT = "shared_context"
    THREAT_RESULTS = "threat_results"
    KNOWLEDGE_RESULTS = "knowledge_results"
    RISK_RESULTS = "risk_results"
    DECISION_RESULTS = "decision_results"


class ToolCategory(StrEnum):
    """Categories of tools."""
    LLM = "llm"
    DATABASE = "database"
    API = "api"
    FILESYSTEM = "filesystem"
    SECURITY = "security"
    UTILITY = "utility"
