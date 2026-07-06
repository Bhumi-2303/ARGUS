"""Gemini Reasoner tool for Threat Analysis Agent."""
import os
import json
from typing import Any, Dict, List
import structlog

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.threat_analysis.models.schemas import ConfidenceResult, Evidence


class GeminiReasoner(BaseTool):
    """Uses LLM to provide contextual analysis of the threat."""

    def __init__(self):
        super().__init__(
            tool_id="ta_gemini_reasoner",
            name="Gemini Reasoner",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Analyzes threat evidence using Gemini.",
            required_permissions=["network:api:gemini"]
        )
        self.logger = structlog.get_logger("argus.tool.gemini_reasoner")
        self.client = None

    async def initialize(self) -> None:
        """Initialize the Gemini client."""
        if genai is None:
            self.logger.warning("google_genai_missing", msg="google-genai SDK not installed, reasoner will use fallback.")
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.logger.warning("gemini_api_key_missing", msg="GEMINI_API_KEY not set. Gemini reasoner will fail or fallback.")
            else:
                self.client = genai.Client(api_key=api_key)
                
        self.logger.info("gemini_reasoner_initialized")

    async def validate(self, confidence_result: ConfidenceResult, evidence: List[Evidence]) -> bool:
        """Validate inputs."""
        if not confidence_result:
            return False
        return True

    async def execute(self, confidence_result: ConfidenceResult, evidence: List[Evidence], event_id: str) -> Dict[str, Any]:
        """Request analysis from Gemini."""
        is_valid = await self.validate(confidence_result, evidence)
        if not is_valid:
            raise ValueError("Invalid inputs for Gemini Reasoner.")

        # If LLM is not available, return a fallback response
        if self.client is None:
            self.logger.warning("using_fallback_reasoning", event_id=event_id)
            return {
                "analysis": f"Fallback: Automated analysis determined {confidence_result.threat_level.value} threat based on {len(evidence)} pieces of evidence.",
                "recommended_actions": ["Review event manually", "Monitor source IP"] if confidence_result.threat_level.value in ("critical", "high") else []
            }

        # Build prompt
        prompt = self._build_prompt(confidence_result, evidence, event_id)
        
        try:
            # We use structured output via JSON schema
            response = self.client.models.generate_content(
                model='gemini-3.1-pro',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "analysis": {"type": "STRING", "description": "A concise paragraph analyzing the threat."},
                            "recommended_actions": {
                                "type": "ARRAY",
                                "items": {"type": "STRING"},
                                "description": "List of 1 to 3 recommended actions for the SOC team."
                            }
                        },
                        "required": ["analysis", "recommended_actions"]
                    },
                    temperature=0.2
                ),
            )
            
            result = json.loads(response.text)
            self.logger.info("gemini_reasoning_complete", event_id=event_id)
            return result
        except Exception as e:
            self.logger.error("gemini_reasoning_failed", error=str(e), event_id=event_id)
            return {
                "analysis": f"Error generating analysis: {e}",
                "recommended_actions": ["Investigate event manually due to LLM failure."]
            }

    def _build_prompt(self, confidence_result: ConfidenceResult, evidence: List[Evidence], event_id: str) -> str:
        """Construct the prompt for Gemini."""
        ev_str = "\\n".join([f"- {e.type}: {e.description} (Value: {e.value}, Importance: {e.importance:.2f})" for e in evidence])
        
        return f"""
        You are the ARGUS Threat Analysis Expert.
        Analyze the following security event (ID: {event_id}).
        
        Threat Level: {confidence_result.threat_level.value.upper()}
        Confidence Score: {confidence_result.confidence_score:.2f}
        
        Evidence Collected:
        {ev_str if ev_str else "None"}
        
        Provide a concise analysis and list recommended actions.
        """

    async def shutdown(self) -> None:
        """Clean up."""
        pass
