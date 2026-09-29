"""Trend Analyzer tool for Risk Prediction Agent."""
import structlog

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.risk_prediction.models.schemas import (
    RiskAnalysisInput, EscalationResult
)

class TrendAnalyzer(BaseTool):
    """Analyzes historical trends to evaluate attack escalation potential."""

    def __init__(self):
        super().__init__(
            tool_id="rp_trend_analyzer",
            name="Trend Analyzer",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Evaluates attack escalation based on related incidents.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.trend_analyzer")

    async def initialize(self) -> None:
        """Initialize the analyzer."""
        self.logger.info("trend_analyzer_initialized")

    async def validate(self, input_data: RiskAnalysisInput) -> bool:
        """Validate inputs."""
        if not input_data or not input_data.knowledge_event:
            return False
        return True

    async def execute(self, input_data: RiskAnalysisInput) -> EscalationResult:
        """Calculate escalation factor."""
        if not await self.validate(input_data):
            raise ValueError("Invalid input for TrendAnalyzer")

        knowledge = input_data.knowledge_event
        related_incidents = knowledge.related_incidents
        vulns = knowledge.known_vulnerabilities

        if not related_incidents and not vulns:
            return EscalationResult(
                escalation_factor=None,
                historical_context="No related incidents or vulnerabilities available.",
                reasoning="Escalation analysis unavailable due to missing historical context."
            )

        escalation_factor = 1.0
        context_notes = []

        if len(related_incidents) > 5:
            escalation_factor += 0.5
            context_notes.append("High volume of recent related incidents indicates active campaign.")
        elif len(related_incidents) > 0:
            escalation_factor += 0.2
            context_notes.append("Prior incidents indicate persistent threat actor.")

        if vulns:
            escalation_factor += 0.3
            context_notes.append("Known unpatched vulnerabilities provide immediate escalation paths.")

        reasoning = f"Escalation factor computed as {escalation_factor:.2f}. " + " ".join(context_notes)

        self.logger.info("escalation_analyzed", factor=escalation_factor)
        return EscalationResult(
            escalation_factor=escalation_factor,
            historical_context=" | ".join(context_notes) if context_notes else "No significant historical context.",
            reasoning=reasoning
        )

    async def shutdown(self) -> None:
        """Clean up."""
        pass
