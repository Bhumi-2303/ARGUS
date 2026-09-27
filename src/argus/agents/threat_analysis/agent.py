"""Main Threat Analysis Agent implementation."""
import asyncio
from typing import Any, Dict, List, Optional
import structlog
import traceback
import time

from argus.core.base_agent import BaseAgent
from argus.core.enums import AgentStatus

from argus.agents.threat_analysis.config import config
from argus.agents.threat_analysis.models.schemas import (
    FeatureEventInput, ThreatAnalysisResult, ThreatLevel, Evidence
)
from argus.registry.model_registry import model_registry, MODEL_METADATA

class ThreatAnalysisAgent(BaseAgent):
    """Analyzes incoming feature events to detect threats using verified ML models."""

    def __init__(self, **kwargs):
        # Override default name/permissions if not provided
        kwargs.setdefault("agent_id", "agent_threat_analysis")
        kwargs.setdefault("name", "Threat Analysis Agent")
        kwargs.setdefault("version", "1.0.0")
        kwargs.setdefault("description", "Detects malicious activity using verified ML models.")
        kwargs.setdefault("capabilities", ["anomaly_detection", "threat_classification"])
        kwargs.setdefault("permissions", ["compute:inference", "fs:read:models"])
        kwargs.setdefault("tools", [])

        super().__init__(**kwargs)
        self.logger = structlog.get_logger("argus.agent.threat_analysis")

    async def initialize(self) -> None:
        """Initialize the agent."""
        self.status = AgentStatus.INITIALIZING
        self.logger.info("initializing_threat_analysis_agent")
        # Ensure model registry has loaded models.
        if len(model_registry.loaded_models) == 0:
            self.logger.warning("model_registry_empty_at_initialization")
        self.status = AgentStatus.READY

    async def validate(self, input_data: Any) -> bool:
        """Validate the incoming FEATURE_EVENT payload."""
        if not input_data:
            return False
        try:
            if isinstance(input_data, dict):
                FeatureEventInput(**input_data)
            return True
        except Exception as e:
            self.logger.warning("payload_validation_failed", error=str(e))
            return False

    async def reason(self, context: Any) -> Any:
        """Execute ML inference using the verified model registry."""
        if isinstance(context, dict):
            event = FeatureEventInput(**context)
        else:
            event = context
            
        self.logger.info("reasoning_started", event_id=event.event_id)
        
        # We will run both xgb_source and xgb_adapted to get results.
        # But we'll primary use xgb_adapted (Clean Class-aware CORAL).
        model_to_use = "xgb_adapted"
        
        start_t = time.time()
        try:
            prob, label, threshold = model_registry.predict(model_to_use, event.features)
            # Try to get SHAP attributions
            base_val, shap_vals, class_str, conf = model_registry.explain(model_to_use, event.features)
        except Exception as e:
            self.logger.error("inference_failed", error=str(e))
            prob, label, threshold = 0.5, 0, 0.5
            shap_vals = {}
            conf = 0.5
            
        latency = (time.time() - start_t) * 1000
        
        # Calculate Threat Level
        threat_level = ThreatLevel.LOW
        if label == 1:
            if prob > 0.90:
                threat_level = ThreatLevel.CRITICAL
            elif prob > 0.75:
                threat_level = ThreatLevel.HIGH
            else:
                threat_level = ThreatLevel.MEDIUM
                
        # Format Evidence
        evidence = []
        for feat, imp in shap_vals.items():
            if abs(imp) > 0.01:
                evidence.append(Evidence(
                    type="feature_attribution",
                    description=f"SHAP contribution from {feat}",
                    importance=imp,
                    value=event.features.get(feat)
                ))
        
        meta = MODEL_METADATA.get(model_to_use, {})
        protocol_status = meta.get("protocol_status", "diagnostic")
        
        return {
            "event": event,
            "threat_level": threat_level,
            "confidence": prob,
            "evidence": evidence,
            "model_version": model_to_use,
            "protocol_status": protocol_status
        }

    async def plan(self, reasoning: Any) -> Any:
        """Formulate final response."""
        return reasoning

    async def execute(self, plan: Any) -> Any:
        """Assemble the ThreatAnalysisResult."""
        event: FeatureEventInput = plan["event"]
        
        result = ThreatAnalysisResult(
            source_event_id=event.event_id,
            threat_level=plan["threat_level"],
            confidence=plan["confidence"],
            evidence=plan["evidence"],
            gemini_analysis=None,
            recommended_actions=[],
            model_version=plan["model_version"],
            protocol_status=plan["protocol_status"]
        )
        return result

    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        return []

    async def update_memory(self, result: Any) -> None:
        pass


    async def publish(self, result: Any) -> None:
        if isinstance(result, ThreatAnalysisResult) and self.blackboard and self.message_bus:
            from argus.schemas.messages import ThreatEvent
            from argus.core.enums import BlackboardSection, TaskPriority
            from datetime import datetime
            import uuid

            threat_event = ThreatEvent(
                request_id=str(uuid.uuid4()),
                trace_id=result.source_event_id,
                agent_id=str(self.agent_id),
                timestamp=datetime.utcnow(),
                priority=TaskPriority.HIGH,
                event_type="THREAT_EVENT",
                attack_type="attack" if result.threat_level.value != "low" else "benign",
                severity=result.confidence,
                description=f"Predicted by {result.model_version} ({result.protocol_status})",
                implementation_status=result.protocol_status
            )
            
            await self.blackboard.write(
                section=BlackboardSection.THREAT_RESULTS,
                key=threat_event.trace_id,
                value=threat_event
            )
            
            await self.message_bus.publish(
                topic=f"events.threat.{result.threat_level.value}",
                message=threat_event
            )


    async def health(self) -> Any:
        return {
            "agent_id": str(self.agent_id),
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed
        }

    async def shutdown(self) -> None:
        self.status = AgentStatus.SHUTDOWN
