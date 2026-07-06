"""Decision Publisher tool for Decision Support Agent."""
import datetime
import structlog
import uuid

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory, BlackboardSection, TaskPriority
from argus.schemas.messages import EventMessage
from argus.core.interfaces import IBlackboard, IMessageBus
from argus.agents.decision_support.models.schemas import DecisionEvent

class DecisionPublisher(BaseTool):
    """Publishes decision results to the blackboard and message bus."""

    def __init__(self):
        super().__init__(
            tool_id="ds_decision_publisher",
            name="Decision Publisher",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Publishes decision recommendations to platform shared resources.",
            required_permissions=["bus:publish:decision", "blackboard:write"]
        )
        self.logger = structlog.get_logger("argus.tool.decision_publisher")

    async def initialize(self) -> None:
        """Initialize the publisher."""
        self.logger.info("decision_publisher_initialized")

    async def validate(self, result: DecisionEvent, blackboard: IBlackboard, message_bus: IMessageBus) -> bool:
        """Validate inputs."""
        if not result or not blackboard or not message_bus:
            return False
        return True

    async def execute(self, result: DecisionEvent, blackboard: IBlackboard, message_bus: IMessageBus) -> bool:
        """Publish the decision result."""
        if not await self.validate(result, blackboard, message_bus):
            raise ValueError("Invalid dependencies or result for DecisionPublisher")

        try:
            # 1. Write to Blackboard
            key = f"decision_{result.source_event_id}"
            await blackboard.set(
                section=BlackboardSection.DECISION_RESULTS,
                key=key,
                value=result.model_dump()
            )
            
            # 2. Publish to MessageBus
            event_id = str(uuid.uuid4())
            priority_val = TaskPriority.CRITICAL if result.priority <= 2 else TaskPriority.MEDIUM
            
            event_msg = EventMessage(
                request_id=event_id,
                trace_id=result.source_event_id,
                agent_id="agent_decision_support",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                priority=priority_val,
                event_type="DECISION_EVENT",
                payload=result.model_dump()
            )
            
            await message_bus.publish(
                topic="decision.events",
                message=event_msg
            )
            
            self.logger.info(
                "decision_published",
                event_id=result.source_event_id,
                priority=result.priority
            )
            return True
            
        except Exception as e:
            self.logger.error("decision_publish_failed", error=str(e), event_id=result.source_event_id)
            return False

    async def shutdown(self) -> None:
        """Clean up."""
        pass
