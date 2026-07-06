"""Approval Generator tool for Decision Support Agent."""
import structlog

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.decision_support.models.schemas import (
    ActionPlan, ImpactAssessment, ApprovalRequirement
)

class ApprovalGenerator(BaseTool):
    """Generates Human-in-the-Loop (HITL) approval requirements."""

    def __init__(self):
        super().__init__(
            tool_id="ds_approval_generator",
            name="Approval Generator",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Determines if human approval is required prior to execution.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.approval_generator")

    async def initialize(self) -> None:
        """Initialize the generator."""
        self.logger.info("approval_generator_initialized")

    async def validate(self, action_plan: ActionPlan, impact: ImpactAssessment) -> bool:
        """Validate inputs."""
        if not action_plan or not impact:
            return False
        return True

    async def execute(self, action_plan: ActionPlan, impact: ImpactAssessment) -> ApprovalRequirement:
        """Determine approval needs."""
        if not await self.validate(action_plan, impact):
            raise ValueError("Invalid input for ApprovalGenerator")

        has_immediate = any(r.urgency == "immediate" for r in action_plan.recommendations)
        high_impact = impact.total_expected_downtime_hours > 2.0 or len(impact.services_disrupted) > 2

        if has_immediate and high_impact:
            req = ApprovalRequirement(
                approval_required=True,
                approver_role="incident_commander",
                justification="Immediate actions proposed with high operational impact."
            )
        elif high_impact:
            req = ApprovalRequirement(
                approval_required=True,
                approver_role="system_owner",
                justification="Actions will cause significant operational disruption."
            )
        else:
            req = ApprovalRequirement(
                approval_required=False,
                approver_role=None,
                justification="Low impact actions can be auto-executed."
            )

        self.logger.info("approval_requirement_generated", required=req.approval_required)
        return req

    async def shutdown(self) -> None:
        """Clean up."""
        pass
