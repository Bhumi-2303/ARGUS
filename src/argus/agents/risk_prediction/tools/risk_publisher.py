"""Risk Publisher tool for Risk Prediction Agent."""
from typing import Any
import datetime
import structlog
import uuid

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory, BlackboardSection, TaskPriority
from argus.schemas.messages import EventMessage
from argus.core.interfaces import IBlackboard, IMessageBus
from argus.agents.risk_prediction.models.schemas import RiskEvent

class RiskPublisher(BaseTool):
    """Publishes risk results to the blackboard and message bus."""

    def __init__(self):
        super().__init__(
            tool_id="rp_risk_publisher",
            name="Risk Publisher",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Publishes risk prediction results to platform shared resources.",
            required_permissions=["bus:publish:risk", "blackboard:write"]
        )
        self.logger = structlog.get_logger("argus.tool.risk_publisher")

    async def initialize(self) -> None:
        """Initialize the publisher."""
        self.logger.info("risk_publisher_initialized")

    async def validate(self, result: RiskEvent, blackboard: IBlackboard, message_bus: IMessageBus) -> bool:
        """Validate inputs."""
        if not result or not blackboard or not message_bus:
            return False
        return True

    async def execute(self, result: RiskEvent, blackboard: IBlackboard, message_bus: IMessageBus) -> bool:
        """Publish the risk result."""
        if not await self.validate(result, blackboard, message_bus):
            raise ValueError("Invalid dependencies or result for RiskPublisher")

        try:
            # 1. Write to Blackboard
            key = f"risk_{result.source_event_id}"
            await blackboard.set(
                section=BlackboardSection.RISK_RESULTS,
                key=key,
                value=result.model_dump()
            )
            
            # 2. Publish to MessageBus
            event_id = str(uuid.uuid4())
            event_msg = EventMessage(
                request_id=event_id,
                trace_id=result.source_event_id,
                agent_id="agent_risk_prediction",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                priority=TaskPriority.CRITICAL if result.severity in ("CRITICAL", "HIGH") else TaskPriority.MEDIUM,
                event_type="RISK_EVENT",
                payload=result.model_dump()
            )
            
            await message_bus.publish(
                topic="risk.events",
                message=event_msg
            )
            
            self.logger.info(
                "risk_result_published",
                event_id=result.source_event_id,
                score=result.risk_score,
                severity=result.severity
            )
            return True
            
        except Exception as e:
            self.logger.error("risk_publish_failed", error=str(e), event_id=result.source_event_id)
            return False

    async def shutdown(self) -> None:
        """Clean up."""
        pass
