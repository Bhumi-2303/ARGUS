"""Threat Publisher tool for Threat Analysis Agent."""
from typing import Any, Dict
import datetime
import structlog
import uuid

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory, BlackboardSection, TaskPriority
from argus.schemas.messages import EventMessage
from argus.core.interfaces import IBlackboard, IMessageBus
from argus.agents.threat_analysis.models.schemas import ThreatAnalysisResult


class ThreatPublisher(BaseTool):
    """Publishes threat results to the blackboard and message bus."""

    def __init__(self):
        super().__init__(
            tool_id="ta_threat_publisher",
            name="Threat Publisher",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Publishes threat analysis results to platform shared resources.",
            required_permissions=["bus:publish:threat", "blackboard:write"]
        )
        self.logger = structlog.get_logger("argus.tool.threat_publisher")

    async def initialize(self) -> None:
        """Initialize the publisher."""
        self.logger.info("threat_publisher_initialized")

    async def validate(self, result: ThreatAnalysisResult, blackboard: IBlackboard, message_bus: IMessageBus) -> bool:
        """Validate inputs."""
        if not result or not blackboard or not message_bus:
            return False
        return True

    async def execute(self, result: ThreatAnalysisResult, blackboard: IBlackboard, message_bus: IMessageBus) -> bool:
        """Publish the threat result."""
        is_valid = await self.validate(result, blackboard, message_bus)
        if not is_valid:
            raise ValueError("Invalid dependencies or result for ThreatPublisher")

        try:
            # 1. Write to Blackboard
            key = f"threat_{result.source_event_id}"
            await blackboard.set(
                section=BlackboardSection.THREAT_RESULTS,
                key=key,
                value=result.model_dump()
            )
            
            # 2. Publish to MessageBus
            event_id = str(uuid.uuid4())
            event_msg = EventMessage(
                request_id=event_id,
                trace_id=result.source_event_id, # Linking the trace
                agent_id="agent_threat_analysis",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                priority=TaskPriority.HIGH if result.threat_level.value in ("critical", "high") else TaskPriority.MEDIUM,
                event_type="THREAT_DETECTED",
                payload=result.model_dump()
            )
            
            await message_bus.publish(
                topic="threat.events",
                message=event_msg
            )
            
            self.logger.info(
                "threat_result_published",
                event_id=result.source_event_id,
                level=result.threat_level.value
            )
            return True
            
        except Exception as e:
            self.logger.error("threat_publish_failed", error=str(e), event_id=result.source_event_id)
            return False

    async def shutdown(self) -> None:
        """Clean up."""
        pass
