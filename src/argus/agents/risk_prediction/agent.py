"""Main Risk Prediction Agent implementation."""
import asyncio
from typing import Any, Dict, List, Optional
import structlog

from argus.core.base_agent import BaseAgent
from argus.core.enums import AgentStatus

from argus.agents.risk_prediction.models.schemas import (
    RiskAnalysisInput, RiskEvent
)

# Tools
from argus.agents.risk_prediction.tools.critical_asset_analyzer import CriticalAssetAnalyzer
from argus.agents.risk_prediction.tools.impact_estimator import ImpactEstimator
from argus.agents.risk_prediction.tools.trend_analyzer import TrendAnalyzer
from argus.agents.risk_prediction.tools.risk_scorer import RiskScorer
from argus.agents.risk_prediction.tools.confidence_calculator import ConfidenceCalculator
from argus.agents.risk_prediction.tools.risk_publisher import RiskPublisher


class RiskPredictionAgent(BaseAgent):
    """Calculates cyber-physical risk from incoming threats and knowledge context."""

    def __init__(self, **kwargs):
        kwargs.setdefault("agent_id", "agent_risk_prediction")
        kwargs.setdefault("name", "Risk Prediction Agent")
        kwargs.setdefault("version", "1.0.0")
        kwargs.setdefault("description", "Estimates operational risk from threats and context.")
        kwargs.setdefault("capabilities", ["risk_scoring", "impact_estimation", "escalation_analysis"])
        kwargs.setdefault("permissions", ["bus:publish:risk", "blackboard:write"])
        kwargs.setdefault("tools", ["critical_asset", "impact", "trend", "scorer", "confidence", "publisher"])

        super().__init__(**kwargs)
        
        self.logger = structlog.get_logger("argus.agent.risk_prediction")
        
        # Instantiate tools
        self.tool_criticality = CriticalAssetAnalyzer()
        self.tool_impact = ImpactEstimator()
        self.tool_trend = TrendAnalyzer()
        self.tool_scorer = RiskScorer()
        self.tool_confidence = ConfidenceCalculator()
        self.tool_publisher = RiskPublisher()

    async def initialize(self) -> None:
        """Initialize the agent and its tools."""
        self.status = AgentStatus.INITIALIZING
        self.logger.info("initializing_risk_prediction_agent")
        
        await self.tool_criticality.initialize()
        await self.tool_impact.initialize()
        await self.tool_trend.initialize()
        await self.tool_scorer.initialize()
        await self.tool_confidence.initialize()
        await self.tool_publisher.initialize()
            
        self.status = AgentStatus.READY

    async def validate(self, input_data: Any) -> bool:
        """Validate the incoming THREAT_EVENT and KNOWLEDGE_EVENT payload."""
        if not input_data:
            return False
            
        try:
            if isinstance(input_data, dict):
                RiskAnalysisInput(**input_data)
            elif isinstance(input_data, RiskAnalysisInput):
                pass
            else:
                return False
            return True
        except Exception as e:
            self.logger.warning("payload_validation_failed", error=str(e))
            return False

    async def reason(self, context: Any) -> Any:
        """Execute risk pipeline tools."""
        if isinstance(context, dict):
            input_data = RiskAnalysisInput(**context)
        else:
            input_data = context
            
        self.logger.info("risk_reasoning_started", event_id=input_data.threat_event.source_event_id)
        
        # 1. Critical Asset Analysis
        criticality = await self.tool_criticality.execute(input_data)
        
        # 2. Impact Estimation
        impact = await self.tool_impact.execute(input_data, criticality)
        
        # 3. Trend/Escalation Analysis
        escalation = await self.tool_trend.execute(input_data)
        
        return {
            "input_data": input_data,
            "criticality": criticality,
            "impact": impact,
            "escalation": escalation
        }

    async def plan(self, reasoning: Any) -> Any:
        """Formulate the final risk score and confidence."""
        input_data: RiskAnalysisInput = reasoning["input_data"]
        criticality = reasoning["criticality"]
        impact = reasoning["impact"]
        escalation = reasoning["escalation"]
        
        # 4. Calculate Risk Score
        risk_score = await self.tool_scorer.execute(criticality, impact, escalation)
        
        # 5. Calculate Confidence
        confidence = await self.tool_confidence.execute(input_data)
        
        return {
            "input_data": input_data,
            "criticality": criticality,
            "impact": impact,
            "escalation": escalation,
            "risk_score": risk_score,
            "confidence": confidence
        }

    async def execute(self, plan: Any) -> Any:
        """Assemble the RiskEvent."""
        input_data: RiskAnalysisInput = plan["input_data"]
        criticality = plan["criticality"]
        impact = plan["impact"]
        escalation = plan["escalation"]
        risk_score = plan["risk_score"]
        confidence = plan["confidence"]
        
        # Combine reasoning chains
        reasoning_str = (
            f"Asset Criticality: {criticality.reasoning}\n"
            f"Impact: {impact.reasoning}\n"
            f"Escalation: {escalation.reasoning}\n"
            f"Final Risk: {risk_score.reasoning}"
        )
        
        result = RiskEvent(
            source_event_id=input_data.threat_event.source_event_id,
            risk_score=risk_score.score,
            severity=risk_score.severity,
            confidence=confidence,
            asset_priority=criticality.asset_priority,
            impact_estimation=impact,
            reasoning=reasoning_str,
            metadata={
                "escalation_factor": escalation.escalation_factor,
                "historical_context": escalation.historical_context
            }
        )
        return result

    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        """Not utilized in this agent as we invoke tools explicitly."""
        return []

    async def update_memory(self, result: Any) -> None:
        """Update working memory with the result."""
        if self.working_memory and isinstance(result, RiskEvent):
            try:
                await self.working_memory.set(
                    key=f"risk_{result.source_event_id}",
                    value=result.model_dump()
                )
            except Exception as e:
                self.logger.warning("memory_update_failed", error=str(e))

    async def publish(self, result: Any) -> None:
        """Publish the RiskEvent."""
        if isinstance(result, RiskEvent):
            if self.blackboard and self.message_bus:
                await self.tool_publisher.execute(
                    result=result,
                    blackboard=self.blackboard,
                    message_bus=self.message_bus
                )
            else:
                self.logger.warning("publish_skipped_missing_infrastructure")

    async def health(self) -> Any:
        """Return health status."""
        return {
            "agent_id": str(self.agent_id),
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed
        }

    async def shutdown(self) -> None:
        """Clean up."""
        self.logger.info("shutting_down_risk_prediction_agent")
        self.status = AgentStatus.SHUTDOWN
        
        await self.tool_criticality.shutdown()
        await self.tool_impact.shutdown()
        await self.tool_trend.shutdown()
        await self.tool_scorer.shutdown()
        await self.tool_confidence.shutdown()
        await self.tool_publisher.shutdown()
