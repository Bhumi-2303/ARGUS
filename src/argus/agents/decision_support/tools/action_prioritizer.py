"""Action Prioritizer tool for Decision Support Agent."""
import structlog
from typing import List

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.decision_support.models.schemas import (
    DecisionAnalysisInput, Recommendation, ActionPlan
)

class ActionPrioritizer(BaseTool):
    """Prioritizes and sequences recommended actions."""

    def __init__(self):
        super().__init__(
            tool_id="ds_action_prioritizer",
            name="Action Prioritizer",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Assigns priority and urgency to actions, forming an Action Plan.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.action_prioritizer")

    async def initialize(self) -> None:
        """Initialize the prioritizer."""
        self.logger.info("action_prioritizer_initialized")

    async def validate(self, input_data: DecisionAnalysisInput, recommendations: List[Recommendation]) -> bool:
        """Validate inputs."""
        if not input_data or recommendations is None:
            return False
        return True

    async def execute(self, input_data: DecisionAnalysisInput, recommendations: List[Recommendation]) -> ActionPlan:
        """Prioritize recommendations into an ActionPlan."""
        if not await self.validate(input_data, recommendations):
            raise ValueError("Invalid input for ActionPrioritizer")

        severity = input_data.risk_event.severity.upper() if input_data.risk_event.severity else "UNKNOWN"
        
        # Determine global urgency based on Risk severity
        if severity == "CRITICAL":
            global_urgency = "immediate"
            base_priority = 1
        elif severity == "HIGH":
            global_urgency = "high"
            base_priority = 2
        elif severity == "MEDIUM":
            global_urgency = "medium"
            base_priority = 3
        else:
            global_urgency = "low"
            base_priority = 4

        # Annotate each recommendation
        for idx, rec in enumerate(recommendations):
            # The first few actions from playbooks are typically most critical
            rec.priority = min(5, base_priority + (0 if idx == 0 else 1))
            
            # Action specific urgency overrides
            if rec.action_type == "isolate_network":
                rec.urgency = "immediate"
                rec.priority = 1
            else:
                rec.urgency = global_urgency

        # Sort recommendations by priority (1 is highest)
        sorted_recs = sorted(recommendations, key=lambda r: r.priority)

        plan = ActionPlan(
            recommendations=sorted_recs,
            primary_objective=f"Mitigate {severity} risk on {len(input_data.knowledge_event.affected_assets)} assets."
        )

        self.logger.info("actions_prioritized", top_priority=plan.recommendations[0].priority if sorted_recs else None)
        return plan

    async def shutdown(self) -> None:
        """Clean up."""
        pass
