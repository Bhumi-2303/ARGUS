"""Confidence Calculator tool for Risk Prediction Agent."""
import structlog

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.risk_prediction.models.schemas import RiskAnalysisInput

class ConfidenceCalculator(BaseTool):
    """Calculates the confidence score of the final risk prediction."""

    def __init__(self):
        super().__init__(
            tool_id="rp_confidence_calculator",
            name="Confidence Calculator",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Computes confidence of risk estimation.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.confidence_calculator")

    async def initialize(self) -> None:
        """Initialize the calculator."""
        self.logger.info("confidence_calculator_initialized")

    async def validate(self, input_data: RiskAnalysisInput) -> bool:
        """Validate inputs."""
        if not input_data:
            return False
        return True

    async def execute(self, input_data: RiskAnalysisInput) -> float:
        """Calculate the confidence score."""
        if not await self.validate(input_data):
            raise ValueError("Invalid input for ConfidenceCalculator")

        threat_conf = input_data.threat_event.confidence
        knowledge = input_data.knowledge_event

        # Evaluate completeness of knowledge
        knowledge_score = 0.5 # Base score for having some context
        
        if knowledge.affected_assets:
            knowledge_score += 0.2
        if knowledge.asset_types:
            knowledge_score += 0.2
        if knowledge.known_vulnerabilities or knowledge.related_incidents:
            knowledge_score += 0.1

        # Final confidence is a weighted blend of Threat confidence and Knowledge completeness
        # Threat detection confidence weighs heavier (60%) than context (40%)
        final_conf = (threat_conf * 0.6) + (knowledge_score * 0.4)
        
        final_conf = max(0.0, min(1.0, final_conf))

        self.logger.info("risk_confidence_calculated", score=final_conf)
        return final_conf

    async def shutdown(self) -> None:
        """Clean up."""
        pass
