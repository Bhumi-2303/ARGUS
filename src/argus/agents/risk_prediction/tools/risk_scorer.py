"""Risk Scorer tool for Risk Prediction Agent."""
import structlog

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.risk_prediction.models.schemas import (
    RiskAnalysisInput, CriticalityResult, ImpactResult, EscalationResult, RiskScoreResult, AssetPriority, ImpactSeverity
)

class RiskScorer(BaseTool):
    """Calculates the final numeric risk score."""

    def __init__(self):
        super().__init__(
            tool_id="rp_risk_scorer",
            name="Risk Scorer",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Aggregates metrics to produce a final risk score.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.risk_scorer")

    async def initialize(self) -> None:
        """Initialize the scorer."""
        self.logger.info("risk_scorer_initialized")

    async def validate(
        self,
        criticality: CriticalityResult,
        impact: ImpactResult,
        escalation: EscalationResult
    ) -> bool:
        """Validate inputs."""
        if not criticality or not impact or not escalation:
            return False
        return True

    async def execute(
        self,
        criticality: CriticalityResult,
        impact: ImpactResult,
        escalation: EscalationResult
    ) -> RiskScoreResult:
        """Calculate the overall risk score."""
        if not await self.validate(criticality, impact, escalation):
            raise ValueError("Invalid input for RiskScorer")
            
        if impact.severity is None or criticality.asset_priority is None:
            return RiskScoreResult(
                score=None,
                severity=None,
                reasoning="Risk score calculation unavailable due to missing impact or criticality data."
            )

        # Base score derived from Impact
        impact_base = {
            ImpactSeverity.CATASTROPHIC: 80,
            ImpactSeverity.SEVERE: 60,
            ImpactSeverity.MODERATE: 40,
            ImpactSeverity.MINOR: 20,
            ImpactSeverity.NONE: 0
        }.get(impact.severity, 0)

        # Criticality multiplier
        crit_multiplier = {
            AssetPriority.CRITICAL: 1.2,
            AssetPriority.HIGH: 1.0,
            AssetPriority.MEDIUM: 0.8,
            AssetPriority.LOW: 0.5
        }.get(criticality.asset_priority, 1.0)
        
        esc_factor = escalation.escalation_factor if escalation.escalation_factor is not None else 1.0

        raw_score = impact_base * crit_multiplier * esc_factor
        
        # Clamp between 0 and 100
        final_score = int(max(0, min(100, round(raw_score))))

        # Determine qualitative severity from final score
        if final_score >= 90:
            severity = "CRITICAL"
        elif final_score >= 70:
            severity = "HIGH"
        elif final_score >= 40:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        reasoning = (
            f"Calculated base {impact_base} from {impact.severity.value.upper()} impact. "
            f"Applied criticality mult {crit_multiplier} and escalation factor {esc_factor:.2f}. "
            f"Resulting score: {final_score}/100 ({severity})."
        )

        self.logger.info("risk_scored", score=final_score, severity=severity)
        return RiskScoreResult(
            score=final_score,
            severity=severity,
            reasoning=reasoning
        )

    async def shutdown(self) -> None:
        """Clean up."""
        pass
