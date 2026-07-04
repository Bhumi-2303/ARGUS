"""Exception hierarchy for ARGUS platform."""
from typing import Any, Dict, Optional


class ArgusError(Exception):
    """Base exception for all ARGUS errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


# --- Agent Errors ---
class AgentError(ArgusError):
    """Base class for agent-related errors."""


class AgentInitError(AgentError):
    """Raised when an agent fails to initialize."""


class AgentExecutionError(AgentError):
    """Raised when an agent encounters an error during execution."""


class AgentTimeoutError(AgentError):
    """Raised when an agent exceeds its execution timeout."""


# --- Security Errors ---
class SecurityError(ArgusError):
    """Base class for security-related errors."""


class AuthenticationError(SecurityError):
    """Raised when authentication fails."""


class AuthorizationError(SecurityError):
    """Raised when authorization fails or permissions are insufficient."""


class ValidationError(SecurityError):
    """Raised when input/output validation fails."""


class InjectionDetectedError(SecurityError):
    """Raised when prompt injection is detected."""


# --- Tool Errors ---
class ToolError(ArgusError):
    """Base class for tool-related errors."""


class ToolInitError(ToolError):
    """Raised when a tool fails to initialize."""


class ToolExecutionError(ToolError):
    """Raised when a tool encounters an error during execution."""


# --- Blackboard Errors ---
class BlackboardError(ArgusError):
    """Base class for blackboard-related errors."""


class LockError(BlackboardError):
    """Raised when failing to acquire a lock on a blackboard section."""


class ConcurrencyError(BlackboardError):
    """Raised when an optimistic concurrency control conflict occurs."""


# --- Orchestrator Errors ---
class OrchestratorError(ArgusError):
    """Base class for orchestrator-related errors."""


class SchedulingError(OrchestratorError):
    """Raised when task scheduling fails."""


class RoutingError(OrchestratorError):
    """Raised when a task cannot be routed to a capable agent."""


class DependencyError(OrchestratorError):
    """Raised when task dependencies cannot be resolved or have cycles."""


# --- Memory Errors ---
class MemoryError(ArgusError):
    """Base class for memory-related errors."""


class StorageError(MemoryError):
    """Raised when memory storage operations fail."""


class CacheError(MemoryError):
    """Raised when cache operations fail."""
