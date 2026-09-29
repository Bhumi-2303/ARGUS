"""Knowledge & Context Agent — enriches THREAT_EVENTs with cybersecurity knowledge."""
import os
from typing import Any, List

from argus.core.base_agent import BaseAgent
from argus.core.enums import BlackboardSection
from argus.schemas.messages import KnowledgeEvent
from argus.agents.knowledge_context.pipeline import KnowledgePipeline
from argus.agents.knowledge_context.schemas import KCAPipelineConfig


class KnowledgeContextAgent(BaseAgent):
    """Knowledge & Context Agent (KCA).

    Consumes ``THREAT_EVENT`` messages from the Blackboard, enriches them
    with MITRE ATT&CK, CVE, CISA, and playbook intelligence, and publishes
    ``KNOWLEDGE_EVENT`` messages back to the Blackboard and Message Bus.

    The KCA never detects attacks, loads datasets, trains models,
    predicts risks, or makes final decisions.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("agent_id", "agent_knowledge_context")
        kwargs.setdefault("name", "Knowledge Context Agent")
        kwargs.setdefault("version", "1.0.0")
        kwargs.setdefault("description", "Enriches threats with security intelligence.")
        kwargs.setdefault("capabilities", ["threat_enrichment", "mitre_mapping", "cve_lookup"])
        kwargs.setdefault("permissions", ["read:security_context"])
        kwargs.setdefault("tools", [])
        super().__init__(**kwargs)

    async def initialize(self) -> None:
        self.logger.info("initializing_knowledge_context_agent")

        # Determine resources directory (sibling to this file)
        resources_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "resources"
        )

        self._config = KCAPipelineConfig(resources_dir=resources_dir)
        self.pipeline = KnowledgePipeline(
            agent_id=str(self.agent_id),
            config=self._config,
        )
        await self.pipeline.initialize()

    async def validate(self, input_data: Any) -> bool:
        self.logger.debug("validating_input")
        if not isinstance(input_data, dict):
            return False
        if "attack_type" not in input_data:
            return False
        return True

    async def reason(self, context: Any) -> Any:
        self.logger.debug("reasoning")
        # Extract threat data from context
        threat_data = {}
        if isinstance(context, dict):
            threat_data["event_id"] = context.get("event_id")
            threat_data["correlation_id"] = context.get("correlation_id")
            threat_data["attack_type"] = context.get("attack_type", "unknown")
            threat_data["cve_id"] = context.get("cve_id")
            threat_data["mitre_technique_id"] = context.get("mitre_technique_id")
            threat_data["severity"] = context.get("severity", 0.5)
            threat_data["description"] = context.get("description", "")
        return threat_data

    async def plan(self, reasoning: Any) -> Any:
        self.logger.debug("planning")
        return {
            "stages": [
                "extract_attack_type",
                "retrieve_mitre",
                "retrieve_mitre_ics",
                "retrieve_cves",
                "retrieve_cisa",
                "retrieve_playbooks",
                "vector_search",
                "gemini_synthesis",
                "publish_knowledge_event",
            ],
            "threat_data": reasoning,
        }

    async def execute(self, plan: Any) -> Any:
        self.logger.debug("executing_plan")
        threat_data = plan["threat_data"]
        event = await self.pipeline.process_threat(threat_data)
        return event

    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        # Tools are orchestrated by the pipeline internally.
        return []

    async def update_memory(self, result: Any) -> None:
        if self.working_memory and isinstance(result, KnowledgeEvent):
            await self.working_memory.set(
                f"latest_knowledge_{self.agent_id}",
                result.model_dump(),
            )

    async def publish(self, result: Any) -> None:
        if not isinstance(result, KnowledgeEvent):
            return

        self.logger.info(
            "publishing_knowledge_event",
            confidence=result.confidence,
            mitre_count=len(result.mitre_techniques),
            cve_count=len(result.cves),
        )

        # Write to Blackboard
        if self.blackboard:
            await self.blackboard.write(
                BlackboardSection.KNOWLEDGE_RESULTS,
                key=f"knowledge_event_{result.request_id}",
                value=result.model_dump(),
                agent_id=str(self.agent_id),
            )

        # Publish to Message Bus
        if self.message_bus:
            await self.message_bus.publish("events.knowledge", result)

    async def health(self) -> Any:
        return {
            "status": "healthy",
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_response_time": self.avg_response_time,
        }

    async def shutdown(self) -> None:
        self.logger.info("shutting_down_knowledge_context_agent")
        await self.pipeline.shutdown()
