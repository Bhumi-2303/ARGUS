"""Impact Estimator tool for Decision Support Agent."""
import structlog
from typing import List

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.decision_support.models.schemas import ActionPlan, ImpactAssessment

class ImpactEstimator(BaseTool):
    """Estimates the impact of executing the recommended actions."""

    def __init__(self):
        super().__init__(
            tool_id="ds_impact_estimator",
            name="Impact Estimator",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Estimates operational downtime and risk reduction from actions.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.ds_impact_estimator")

    async def initialize(self) -> None:
        """Initialize the estimator."""
        self.logger.info("impact_estimator_initialized")

    async def validate(self, action_plan: ActionPlan) -> bool:
        """Validate inputs."""
        if not action_plan:
            return False
        return True

    async def execute(self, action_plan: ActionPlan) -> ImpactAssessment:
        """Calculate the estimated impact of the plan."""
        if not await self.validate(action_plan):
            raise ValueError("Invalid input for ImpactEstimator")

        total_downtime = 0.0
        services_disrupted = set()
        
        for rec in action_plan.recommendations:
            total_downtime += rec.expected_downtime_hours
            for asset in rec.target_assets:
                services_disrupted.add(asset)

        # Basic risk reduction estimate based on presence of immediate actions
        has_immediate = any(r.urgency == "immediate" for r in action_plan.recommendations)
        has_high = any(r.urgency == "high" for r in action_plan.recommendations)
        
        if has_immediate:
            reduction = 0.9  # 90% risk reduction
        elif has_high:
            reduction = 0.7  # 70% risk reduction
        elif action_plan.recommendations:
            reduction = 0.3  # 30% risk reduction
        else:
            reduction = 0.0

        assessment = ImpactAssessment(
            total_expected_downtime_hours=total_downtime,
            services_disrupted=list(services_disrupted),
            risk_reduction_estimate=reduction
        )

        self.logger.info("impact_estimated", downtime=total_downtime, reduction=reduction)
        return assessment

    async def shutdown(self) -> None:
        """Clean up."""
        pass
