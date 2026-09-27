"""Main Decision Support Agent implementation."""
import asyncio
from typing import Any, Dict, List, Optional
import structlog

from argus.core.base_agent import BaseAgent
from argus.core.enums import AgentStatus

from argus.agents.decision_support.models.schemas import (
    DecisionAnalysisInput, DecisionEvent
)

# Tools
from argus.agents.decision_support.tools.playbook_selector import PlaybookSelector
from argus.agents.decision_support.tools.recommendation_engine import RecommendationEngine
from argus.agents.decision_support.tools.action_prioritizer import ActionPrioritizer
from argus.agents.decision_support.tools.impact_estimator import ImpactEstimator
from argus.agents.decision_support.tools.approval_generator import ApprovalGenerator
from argus.agents.decision_support.tools.decision_publisher import DecisionPublisher

class DecisionSupportAgent(BaseAgent):
    """Converts risk assessments into actionable recommendations."""

    def __init__(self, **kwargs):
        kwargs.setdefault("agent_id", "agent_decision_support")
        kwargs.setdefault("name", "Decision Support Agent")
        kwargs.setdefault("version", "1.0.0")
        kwargs.setdefault("description", "Generates human-actionable recommendations from risks.")
        kwargs.setdefault("capabilities", ["playbook_selection", "action_generation", "impact_estimation"])
        kwargs.setdefault("permissions", ["bus:publish:decision", "blackboard:write"])
        kwargs.setdefault("tools", ["playbook", "recommend", "prioritize", "impact", "approve", "publish"])

        super().__init__(**kwargs)
        
        self.logger = structlog.get_logger("argus.agent.decision_support")
        
        # Instantiate tools
        self.tool_playbooks = PlaybookSelector()
        self.tool_recommendations = RecommendationEngine()
        self.tool_prioritizer = ActionPrioritizer()
        self.tool_impact = ImpactEstimator()
        self.tool_approval = ApprovalGenerator()
        self.tool_publisher = DecisionPublisher()

    async def initialize(self) -> None:
        """Initialize the agent and its tools."""
        self.status = AgentStatus.INITIALIZING
        self.logger.info("initializing_decision_support_agent")
        
        await self.tool_playbooks.initialize()
        await self.tool_recommendations.initialize()
        await self.tool_prioritizer.initialize()
        await self.tool_impact.initialize()
        await self.tool_approval.initialize()
        await self.tool_publisher.initialize()
            
        self.status = AgentStatus.READY

    async def validate(self, input_data: Any) -> bool:
        """Validate the incoming payload."""
        if not input_data:
            return False
            
        try:
            if isinstance(input_data, dict):
                DecisionAnalysisInput(**input_data)
            elif isinstance(input_data, DecisionAnalysisInput):
                pass
            else:
                return False
            return True
        except Exception as e:
            self.logger.warning("payload_validation_failed", error=str(e))
            return False

    async def reason(self, context: Any) -> Any:
        """Execute early decision pipeline steps."""
        if isinstance(context, dict):
            input_data = DecisionAnalysisInput(**context)
        else:
            input_data = context
            
        self.logger.info("decision_reasoning_started", event_id=input_data.risk_event.source_event_id)
        
        # 1. Analyze Risk & Knowledge to Select Playbooks
        playbooks = await self.tool_playbooks.execute(input_data)
        
        # 2. Generate Recommendations
        raw_recommendations = await self.tool_recommendations.execute(input_data, playbooks)
        
        return {
            "input_data": input_data,
            "playbooks": playbooks,
            "raw_recommendations": raw_recommendations
        }

    async def plan(self, reasoning: Any) -> Any:
        """Prioritize recommendations and estimate impacts."""
        input_data: DecisionAnalysisInput = reasoning["input_data"]
        raw_recommendations = reasoning["raw_recommendations"]
        
        # 3. Prioritize Actions
        action_plan = await self.tool_prioritizer.execute(input_data, raw_recommendations)
        
        # 4. Estimate Expected Impact
        impact = await self.tool_impact.execute(action_plan)
        
        # 5. Generate Human Approval Plan
        approval = await self.tool_approval.execute(action_plan, impact)
        
        return {
            "input_data": input_data,
            "action_plan": action_plan,
            "impact": impact,
            "approval": approval
        }

    async def execute(self, plan: Any) -> Any:
        """Assemble the DecisionEvent."""
        input_data: DecisionAnalysisInput = plan["input_data"]
        action_plan = plan["action_plan"]
        impact = plan["impact"]
        approval = plan["approval"]
        
        reasoning_str = (
            f"Analyzed RISK_EVENT {input_data.risk_event.source_event_id} "
            f"({input_data.risk_event.severity}). "
            f"Generated {len(action_plan.recommendations)} prioritized recommendations."
        )

        top_priority = 5
        top_urgency = "low"
        if action_plan.recommendations:
            top_priority = action_plan.recommendations[0].priority
            top_urgency = action_plan.recommendations[0].urgency
        
        result = DecisionEvent(
            implementation_status="not_implemented",

            source_event_id=input_data.risk_event.source_event_id,
            recommended_actions=action_plan.recommendations,
            priority=top_priority,
            urgency=top_urgency,
            confidence=input_data.risk_event.confidence, # inherits risk confidence initially
            estimated_impact=impact,
            approval_required=approval.approval_required,
            execution_plan=action_plan.primary_objective,
            reasoning=reasoning_str
        )
        return result

    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        """Not utilized in this agent as we invoke tools explicitly."""
        return []

    async def update_memory(self, result: Any) -> None:
        """Update working memory with the result."""
        if self.working_memory and isinstance(result, DecisionEvent):
            try:
                await self.working_memory.set(
                    key=f"decision_{result.source_event_id}",
                    value=result.model_dump()
                )
            except Exception as e:
                self.logger.warning("memory_update_failed", error=str(e))

    async def publish(self, result: Any) -> None:
        """Publish the DecisionEvent."""
        if isinstance(result, DecisionEvent):
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
        self.logger.info("shutting_down_decision_support_agent")
        self.status = AgentStatus.SHUTDOWN
        
        await self.tool_playbooks.shutdown()
        await self.tool_recommendations.shutdown()
        await self.tool_prioritizer.shutdown()
        await self.tool_impact.shutdown()
        await self.tool_approval.shutdown()
        await self.tool_publisher.shutdown()
