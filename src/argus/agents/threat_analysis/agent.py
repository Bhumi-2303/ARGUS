"""Main Threat Analysis Agent implementation."""
import asyncio
from typing import Any, Dict, List, Optional
import structlog
import traceback

from argus.core.base_agent import BaseAgent
from argus.core.enums import AgentStatus

from argus.agents.threat_analysis.config import config
from argus.agents.threat_analysis.models.schemas import (
    FeatureEventInput, ThreatAnalysisResult, ModelType,
    InferenceResult, ConfidenceResult, Evidence
)

# Tools
from argus.agents.threat_analysis.tools.model_loader import ModelLoader
from argus.agents.threat_analysis.tools.inference_engine import InferenceEngine
from argus.agents.threat_analysis.tools.confidence_calculator import ConfidenceCalculator
from argus.agents.threat_analysis.tools.evidence_collector import EvidenceCollector
from argus.agents.threat_analysis.tools.threat_publisher import ThreatPublisher


class ThreatAnalysisAgent(BaseAgent):
    """Analyzes incoming feature events to detect threats using ML models."""

    def __init__(self, **kwargs):
        # Override default name/permissions if not provided
        kwargs.setdefault("agent_id", "agent_threat_analysis")
        kwargs.setdefault("name", "Threat Analysis Agent")
        kwargs.setdefault("version", "1.0.0")
        kwargs.setdefault("description", "Detects malicious activity using ML models.")
        kwargs.setdefault("capabilities", ["anomaly_detection", "threat_classification", "llm_reasoning"])
        kwargs.setdefault("permissions", ["compute:inference", "fs:read:models", "network:api:gemini"])
        kwargs.setdefault("tools", ["model_loader", "inference", "confidence", "evidence", "gemini", "publisher"])

        super().__init__(**kwargs)
        
        self.logger = structlog.get_logger("argus.agent.threat_analysis")
        
        # Instantiate tools
        self.tool_model_loader = ModelLoader()
        self.tool_inference = InferenceEngine()
        self.tool_confidence = ConfidenceCalculator()
        self.tool_evidence = EvidenceCollector()
        self.tool_publisher = ThreatPublisher()
        
        self._active_model = None

    async def initialize(self) -> None:
        """Initialize the agent and its tools."""
        self.status = AgentStatus.INITIALIZING
        self.logger.info("initializing_threat_analysis_agent")
        
        # Initialize tools
        await self.tool_model_loader.initialize()
        await self.tool_inference.initialize()
        await self.tool_confidence.initialize()
        await self.tool_evidence.initialize()
        await self.tool_publisher.initialize()
        
        # Load the default model
        model_path = f"{config.model_dir}/{config.default_model_type.value}.model"
        try:
            self._active_model = await self.tool_model_loader.execute(
                model_type=config.default_model_type,
                model_path=model_path
            )
            self.logger.info("model_loaded", model_type=config.default_model_type.value)
        except Exception as e:
            self.logger.error("failed_to_load_model", error=str(e), path=model_path)
            # Depending on platform rules, this might be a fatal error.
            # We'll set status to ERROR, but don't necessarily crash the process.
            self.status = AgentStatus.ERROR
            raise
            
        self.status = AgentStatus.READY

    async def validate(self, input_data: Any) -> bool:
        """Validate the incoming FEATURE_EVENT payload."""
        if not input_data:
            return False
            
        # Optional: Ask SecurityProvider to check for injection in the payload
        if self.security:
            # We assume detect_injection returns True if malicious/injection detected
            is_malicious = await self.security.detect_injection(str(input_data))
            if is_malicious:
                self.logger.warning("security_injection_detected_in_payload")
                return False

        try:
            # Parse into Pydantic model to ensure schema validity
            if isinstance(input_data, dict):
                FeatureEventInput(**input_data)
            elif isinstance(input_data, FeatureEventInput):
                pass
            else:
                return False
            return True
        except Exception as e:
            self.logger.warning("payload_validation_failed", error=str(e))
            return False

    async def reason(self, context: Any) -> Any:
        """Execute ML inference and gather evidence."""
        # context is the validated input_data
        if isinstance(context, dict):
            event = FeatureEventInput(**context)
        else:
            event = context
            
        self.logger.info("reasoning_started", event_id=event.event_id)
        
        # 1. Inference
        inference_result = await self.tool_inference.execute(
            features=event.features,
            model=self._active_model,
            model_type=config.default_model_type
        )
        
        # 2. Calculate Confidence
        confidence_result = await self.tool_confidence.execute(
            inference_result=inference_result
        )
        
        # 3. Collect Evidence
        evidence_list = await self.tool_evidence.execute(
            features=event.features,
            inference_result=inference_result
        )
        
        return {
            "event": event,
            "inference": inference_result,
            "confidence": confidence_result,
            "evidence": evidence_list
        }

    async def plan(self, reasoning: Any) -> Any:
        """Decide if LLM analysis is needed and formulate final response."""
        event: FeatureEventInput = reasoning["event"]
        confidence: ConfidenceResult = reasoning["confidence"]
        evidence: List[Evidence] = reasoning["evidence"]
        
        gemini_analysis = None
        recommended_actions = []
            
        return {
            "event": event,
            "confidence": confidence,
            "evidence": evidence,
            "gemini_analysis": gemini_analysis,
            "recommended_actions": recommended_actions
        }

    async def execute(self, plan: Any) -> Any:
        """Assemble the ThreatAnalysisResult."""
        event: FeatureEventInput = plan["event"]
        confidence: ConfidenceResult = plan["confidence"]
        
        result = ThreatAnalysisResult(
            source_event_id=event.event_id,
            threat_level=confidence.threat_level,
            confidence=confidence.confidence_score,
            evidence=plan["evidence"],
            gemini_analysis=plan["gemini_analysis"],
            recommended_actions=plan["recommended_actions"],
            model_version=f"{config.default_model_type.value}-v1"
        )
        return result

    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        """Not utilized in this agent as we invoke tools explicitly in lifecycle steps."""
        return []

    async def update_memory(self, result: Any) -> None:
        """Update working memory with the result if available."""
        if self.working_memory and isinstance(result, ThreatAnalysisResult):
            try:
                await self.working_memory.set(
                    key=f"threat_analysis_{result.source_event_id}",
                    value=result.model_dump()
                )
            except Exception as e:
                self.logger.warning("memory_update_failed", error=str(e))

    async def publish(self, result: Any) -> None:
        """Publish the ThreatAnalysisResult."""
        if isinstance(result, ThreatAnalysisResult):
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
            "model_loaded": self._active_model is not None,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed
        }

    async def shutdown(self) -> None:
        """Clean up."""
        self.logger.info("shutting_down_threat_analysis_agent")
        self.status = AgentStatus.SHUTDOWN
        
        await self.tool_model_loader.shutdown()
        await self.tool_inference.shutdown()
        await self.tool_confidence.shutdown()
        await self.tool_evidence.shutdown()
        await self.tool_publisher.shutdown()
