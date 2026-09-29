"""Impact Estimator tool for Risk Prediction Agent."""
from typing import Any
import structlog

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.risk_prediction.models.schemas import (
    RiskAnalysisInput, CriticalityResult, ImpactResult, ImpactSeverity, AssetPriority
)

class ImpactEstimator(BaseTool):
    """Estimates the operational impact of a threat."""

    def __init__(self):
        super().__init__(
            tool_id="rp_impact_estimator",
            name="Impact Estimator",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Estimates potential disruption to operations.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.impact_estimator")

    async def initialize(self) -> None:
        """Initialize the estimator."""
        self.logger.info("impact_estimator_initialized")

    async def validate(self, input_data: RiskAnalysisInput, criticality: CriticalityResult) -> bool:
        """Validate inputs."""
        if not input_data or not criticality:
            return False
        return True

    async def execute(self, input_data: RiskAnalysisInput, criticality: CriticalityResult) -> ImpactResult:
        """Calculate operational impact."""
        if not await self.validate(input_data, criticality):
            raise ValueError("Invalid input for ImpactEstimator")

        threat_level = input_data.threat_event.threat_level.lower()
        asset_priority = criticality.asset_priority

        if asset_priority is None:
            return ImpactResult(
                severity=None,
                estimated_downtime_hours=None,
                impacted_services=[],
                reasoning="Asset criticality unavailable; cannot estimate impact."
            )

        # Simple matrix for impact estimation
        if asset_priority == AssetPriority.CRITICAL and threat_level in ("critical", "high"):
            severity = ImpactSeverity.CATASTROPHIC
            downtime = 24.0
        elif asset_priority == AssetPriority.CRITICAL or threat_level == "critical":
            severity = ImpactSeverity.SEVERE
            downtime = 12.0
        elif asset_priority == AssetPriority.HIGH and threat_level == "high":
            severity = ImpactSeverity.SEVERE
            downtime = 8.0
        elif asset_priority in (AssetPriority.HIGH, AssetPriority.MEDIUM) and threat_level in ("high", "medium"):
            severity = ImpactSeverity.MODERATE
            downtime = 4.0
        elif threat_level == "info":
            severity = ImpactSeverity.NONE
            downtime = 0.0
        else:
            severity = ImpactSeverity.MINOR
            downtime = 1.0

        reasoning = f"Impact estimated as {severity.value.upper()} based on {asset_priority.value.upper()} asset criticality and {threat_level.upper()} threat level."

        self.logger.info("impact_estimated", severity=severity.value, downtime=downtime)
        return ImpactResult(
            severity=severity,
            estimated_downtime_hours=downtime,
            impacted_services=criticality.critical_assets,
            reasoning=reasoning
        )

    async def shutdown(self) -> None:
        """Clean up."""
        pass
