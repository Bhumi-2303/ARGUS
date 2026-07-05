"""Abstract base class for all ARGUS agents."""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import structlog
from datetime import datetime, timezone

from argus.core.enums import AgentStatus
from argus.core.types import AgentId, TaskId

if TYPE_CHECKING:
    from argus.core.interfaces import (
        IBlackboard,
        IMessageBus,
        IMemoryStore,
        ISecurityProvider,
    )


class BaseAgent(ABC):
    """Every ARGUS agent MUST inherit this class.

    Lifecycle:
        initialize() -> validate() -> [reason() -> plan() -> execute() ->
        call_tools() -> update_memory() -> publish()] -> health() -> shutdown()

    Infrastructure dependencies are injected as optional keyword arguments.
    When not provided, they default to None and agents operate in stub mode.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        version: str,
        description: str,
        capabilities: List[str],
        permissions: List[str],
        tools: List[str],
        *,
        # --- Infrastructure dependencies (all optional) ---
        blackboard: Optional["IBlackboard"] = None,
        message_bus: Optional["IMessageBus"] = None,
        tool_registry: Optional[Any] = None,
        working_memory: Optional["IMemoryStore"] = None,
        shared_memory: Optional["IMemoryStore"] = None,
        vector_memory: Optional[Any] = None,
        cache: Optional[Any] = None,
        security: Optional["ISecurityProvider"] = None,
    ):
        # --- Identity ---
        self.agent_id = AgentId(agent_id)
        self.name = name
        self.version = version
        self.description = description
        self.capabilities = capabilities
        self.permissions = permissions
        self.tools = tools

        # --- Status & Logging ---
        self.status = AgentStatus.INITIALIZING
        self.logger = structlog.get_logger("argus.agent").bind(
            agent_id=self.agent_id,
            agent_name=self.name,
        )

        # --- Metrics ---
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.avg_response_time = 0.0

        # --- Infrastructure (None when not injected) ---
        self.blackboard = blackboard
        self.message_bus = message_bus
        self.tool_registry = tool_registry
        self.working_memory = working_memory
        self.shared_memory = shared_memory
        self.vector_memory = vector_memory
        self.cache = cache
        self.security = security

    # ------------------------------------------------------------------
    # Abstract lifecycle methods — subclasses MUST implement all 10.
    # ------------------------------------------------------------------

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent, load models, connect to resources."""

    @abstractmethod
    async def validate(self, input_data: Any) -> bool:
        """Validate incoming task payload."""

    @abstractmethod
    async def reason(self, context: Any) -> Any:
        """Perform reasoning on the input and context."""

    @abstractmethod
    async def plan(self, reasoning: Any) -> Any:
        """Create an execution plan based on reasoning."""

    @abstractmethod
    async def execute(self, plan: Any) -> Any:
        """Execute the plan."""

    @abstractmethod
    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        """Execute any tool requests generated during execution."""

    @abstractmethod
    async def update_memory(self, result: Any) -> None:
        """Update working/shared memory with results."""

    @abstractmethod
    async def publish(self, result: Any) -> None:
        """Publish the final result to the blackboard or message bus."""

    @abstractmethod
    async def health(self) -> Any:
        """Return the health status of the agent."""

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up resources before shutdown."""

    # ------------------------------------------------------------------
    # Concrete lifecycle orchestration — DO NOT OVERRIDE.
    # ------------------------------------------------------------------

    async def process_task(self, task_payload: Any, context: Any) -> Any:
        """Orchestrate the full lifecycle for a single task."""
        start_time = datetime.now(timezone.utc)
        self.status = AgentStatus.BUSY
        try:
            is_valid = await self.validate(task_payload)
            if not is_valid:
                raise ValueError("Invalid task payload")

            reasoning = await self.reason(context)
            plan = await self.plan(reasoning)
            execution_result = await self.execute(plan)
            # Placeholder for tool calling logic
            await self.update_memory(execution_result)
            await self.publish(execution_result)

            self.tasks_completed += 1
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._update_avg_response_time(duration)
            return execution_result
        except Exception as e:
            self.tasks_failed += 1
            self.logger.error("task_processing_failed", error=str(e), exc_info=True)
            self.status = AgentStatus.ERROR
            raise
        finally:
            if self.status != AgentStatus.ERROR:
                self.status = AgentStatus.READY

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_avg_response_time(self, new_duration: float) -> None:
        if self.tasks_completed == 1:
            self.avg_response_time = new_duration
        else:
            self.avg_response_time = (
                self.avg_response_time * (self.tasks_completed - 1) + new_duration
            ) / self.tasks_completed

    async def _emit_heartbeat(self) -> None:
        """Emit a heartbeat signal via the message bus (if available)."""
        if self.message_bus is None:
            return
        heartbeat = {
            "agent_id": str(self.agent_id),
            "status": self.status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_response_time": self.avg_response_time,
        }
        try:
            await self.message_bus.publish(
                f"agent.{self.agent_id}.heartbeat", heartbeat
            )
        except Exception as exc:
            self.logger.warning("heartbeat_publish_failed", error=str(exc))
