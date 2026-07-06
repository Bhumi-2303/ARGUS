"""Recommendation Engine tool for Decision Support Agent."""
import structlog
from typing import List
import uuid

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.decision_support.models.schemas import (
    DecisionAnalysisInput, Playbook, Recommendation
)

class RecommendationEngine(BaseTool):
    """Generates specific actionable recommendations."""

    def __init__(self):
        super().__init__(
            tool_id="ds_recommendation_engine",
            name="Recommendation Engine",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Transforms playbooks and context into specific recommendations.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.recommendation_engine")

    async def initialize(self) -> None:
        """Initialize the engine."""
        self.logger.info("recommendation_engine_initialized")

    async def validate(self, input_data: DecisionAnalysisInput, playbooks: List[Playbook]) -> bool:
        """Validate inputs."""
        if not input_data or playbooks is None:
            return False
        return True

    async def execute(self, input_data: DecisionAnalysisInput, playbooks: List[Playbook]) -> List[Recommendation]:
        """Generate recommendations based on selected playbooks (Rule-based implementation)."""
        if not await self.validate(input_data, playbooks):
            raise ValueError("Invalid input for RecommendationEngine")

        recommendations = []
        
        for playbook in playbooks:
            if playbook.playbook_id == "SOP-CONTAIN-01":
                recommendations.append(Recommendation(
                    action_id=str(uuid.uuid4()),
                    action_type="isolate_network",
                    description=f"Isolate network segments for assets: {', '.join(playbook.applicable_assets)}",
                    target_assets=playbook.applicable_assets,
                    playbook_reference=playbook.playbook_id,
                    expected_downtime_hours=4.0
                ))
            elif playbook.playbook_id == "SOP-PATCH-02":
                recommendations.append(Recommendation(
                    action_id=str(uuid.uuid4()),
                    action_type="apply_patch",
                    description=f"Apply emergency patches to vulnerabilities on assets: {', '.join(playbook.applicable_assets)}",
                    target_assets=playbook.applicable_assets,
                    playbook_reference=playbook.playbook_id,
                    expected_downtime_hours=2.0
                ))
            elif playbook.playbook_id == "SOP-MONITOR-01":
                recommendations.append(Recommendation(
                    action_id=str(uuid.uuid4()),
                    action_type="increase_telemetry",
                    description=f"Increase monitoring and telemetry for assets: {', '.join(playbook.applicable_assets)}",
                    target_assets=playbook.applicable_assets,
                    playbook_reference=playbook.playbook_id,
                    expected_downtime_hours=0.0
                ))
                
        # If no specific rules matched but we have a playbook, generate a generic recommendation
        if not recommendations and playbooks:
            pb = playbooks[0]
            recommendations.append(Recommendation(
                action_id=str(uuid.uuid4()),
                action_type="investigate",
                description="Investigate the affected assets manually.",
                target_assets=pb.applicable_assets,
                playbook_reference=pb.playbook_id,
                expected_downtime_hours=0.0
            ))

        self.logger.info("recommendations_generated", count=len(recommendations))
        return recommendations

    async def shutdown(self) -> None:
        """Clean up."""
        pass
