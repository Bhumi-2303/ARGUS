"""KnowledgePublisher — Builds KnowledgeEvent messages from synthesis results."""
import uuid
from datetime import datetime, timezone
from typing import Any

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory, TaskPriority
from argus.schemas.messages import KnowledgeEvent
from argus.agents.knowledge_context.schemas import SynthesisResult


class KnowledgePublisher(BaseTool):
    """Builds a ``KnowledgeEvent`` from a ``SynthesisResult``.

    Does NOT publish directly — the agent's ``publish()`` lifecycle
    method handles writing to Blackboard and Message Bus.
    """

    def __init__(self, resources_dir: str = ""):
        super().__init__(
            tool_id="tool-publisher-kca-01",
            name="knowledge_publisher",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Builds KnowledgeEvent messages for publication.",
            required_permissions=["data:write"],
        )

    async def initialize(self) -> None:
        pass

    async def validate(self, **kwargs: Any) -> bool:
        return "synthesis_result" in kwargs and "agent_id" in kwargs and "processing_duration_ms" in kwargs

    async def execute(self, **kwargs: Any) -> KnowledgeEvent:
        result: SynthesisResult = kwargs["synthesis_result"]
        agent_id: str = kwargs["agent_id"]
        duration_ms: float = kwargs["processing_duration_ms"]
        event_id = kwargs.get("event_id") or str(uuid.uuid4())
        correlation_id = kwargs.get("correlation_id") or str(uuid.uuid4())

        return KnowledgeEvent(
            request_id=event_id,
            trace_id=correlation_id,
            agent_id=agent_id,
            timestamp=datetime.now(timezone.utc),
            priority=TaskPriority.HIGH,
            event_type="KNOWLEDGE_EVENT",
            attack_context=result.attack_context,
            mitre_techniques=result.mitre_techniques,
            cves=result.cves,
            cisa_advisories=result.cisa_advisories,
            recommended_mitigations=result.recommended_mitigations,
            references=result.references,
            confidence=result.confidence,
            processing_metadata={
                "processing_duration_ms": duration_ms,
                "sources_searched": result.attack_context.get("sources_consulted", []),
                "total_records": result.attack_context.get("total_records_retrieved", 0),
                "synthesis_mode": "template",
            },
        )

    async def shutdown(self) -> None:
        pass

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {
                "synthesis_result": {"type": "object"},
                "agent_id": {"type": "string"},
                "processing_duration_ms": {"type": "number"},
            },
            "required": ["synthesis_result", "agent_id", "processing_duration_ms"],
        }
        return md
