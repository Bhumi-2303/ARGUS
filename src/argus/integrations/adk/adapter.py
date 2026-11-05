"""Adapter for Google ADK framework and LLM narration.

Provides optional integration with Google Agent Development Kit (ADK) conventions
and LLM-assisted incident narration.

ARCHITECTURE RULE:
- This adapter is OFF by default and never operates on the real-time detection path.
- All core detection, ML inference, and decision-making logic remain 100% deterministic.
"""

from typing import Any, Dict, Optional
import structlog

from argus.core.base_agent import BaseAgent
from argus.integrations.adk.narrator import IncidentNarrator, IncidentNarrative

logger = structlog.get_logger("argus.integrations.adk")


class ADKAdapter:
    """Adapts ARGUS agents and incident outputs to Google ADK framework conventions."""

    _narrator: Optional[IncidentNarrator] = None

    @classmethod
    def get_narrator(cls, api_key: Optional[str] = None) -> IncidentNarrator:
        """Get or initialize the shared IncidentNarrator instance."""
        if cls._narrator is None or api_key is not None:
            cls._narrator = IncidentNarrator(api_key=api_key)
        return cls._narrator

    @classmethod
    async def narrate_incident(cls, incident: Any, api_key: Optional[str] = None) -> IncidentNarrative:
        """Summarize an already-computed security incident into an executive narrative."""
        narrator = cls.get_narrator(api_key=api_key)
        return await narrator.narrate_incident(incident)

    @staticmethod
    async def run_with_adk(agent: BaseAgent, task_payload: Any) -> Any:
        """Run an ARGUS agent using Google ADK abstractions with clean local fallback."""
        logger.info("running_with_adk", agent_id=agent.agent_id)
        return await agent.process_task(task_payload, {"source": "adk_adapter"})
