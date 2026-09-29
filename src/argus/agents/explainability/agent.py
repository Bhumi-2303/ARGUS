import time
from typing import Any, Dict, List
import structlog

from argus.core.base_agent import BaseAgent
from argus.core.enums import AgentStatus
from argus.registry.model_registry import model_registry

from argus.agents.explainability.schemas import ExplainabilityInput, ExplainabilityResult

class ExplainabilityAgent(BaseAgent):
    """
    Explainability Agent
    Calculates feature attributions using real TreeSHAP via the model registry.
    """
    
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_id", "agent_explainability")
        kwargs.setdefault("name", "Explainability Agent")
        kwargs.setdefault("version", "1.0.0")
        kwargs.setdefault("description", "Feature attribution using real SHAP from the verified model registry.")
        kwargs.setdefault("capabilities", ["explainability", "shap"])
        kwargs.setdefault("permissions", ["compute:inference"])
        kwargs.setdefault("tools", [])
        
        super().__init__(**kwargs)
        self.logger = structlog.get_logger("argus.agent.explainability")
        self.status = AgentStatus.INITIALIZING
        
    async def initialize(self) -> None:
        self.logger.info("initializing_explainability_agent")
        # Do not load mock models! We use the real model_registry.
        if not model_registry.is_loaded:
            self.logger.info("loading_model_registry_for_explainability")
            try:
                model_registry.load_all()
            except Exception as e:
                self.logger.warning("model_registry_load_failed", error=str(e))
        self.status = AgentStatus.READY
        
    async def validate(self, input_data: Any) -> bool:
        if not input_data:
            return False
        try:
            if isinstance(input_data, dict):
                ExplainabilityInput(**input_data)
            return True
        except Exception as e:
            self.logger.warning("payload_validation_failed", error=str(e))
            return False
        
    async def reason(self, context: Any) -> Any:
        if isinstance(context, dict):
            event = ExplainabilityInput(**context)
        else:
            event = context
            
        start_t = time.time()
        
        try:
            # We explicitly want to use the actual model version used by Threat Analysis
            base_val, shap_vals, top_feat, top_impact = model_registry.explain(
                event.model_version, event.features
            )
            
            latency = (time.time() - start_t) * 1000.0
            
            return {
                "event": event,
                "status": "available",
                "base_value": base_val,
                "shap_values": shap_vals,
                "top_feature": top_feat,
                "top_feature_impact": top_impact,
                "latency_ms": latency
            }
        except Exception as e:
            self.logger.warning("shap_calculation_failed", error=str(e), model_version=event.model_version)
            latency = (time.time() - start_t) * 1000.0
            # If SHAP cannot be calculated, return a structured unavailable result
            return {
                "event": event,
                "status": "unavailable",
                "reason": str(e),
                "latency_ms": latency
            }
        
    async def plan(self, reasoning: Any) -> Any:
        return reasoning
        
    async def execute(self, plan: Any) -> Any:
        event: ExplainabilityInput = plan["event"]
        
        if plan["status"] == "unavailable":
            return ExplainabilityResult(
                status="unavailable",
                reason=plan["reason"],
                event_id=event.event_id,
                correlation_id=event.correlation_id,
                model_version=event.model_version,
                latency_ms=plan["latency_ms"]
            )
            
        return ExplainabilityResult(
            status="available",
            event_id=event.event_id,
            correlation_id=event.correlation_id,
            model_version=event.model_version,
            base_value=plan["base_value"],
            shap_values=plan["shap_values"],
            top_feature=plan["top_feature"],
            top_feature_impact=plan["top_feature_impact"],
            latency_ms=plan["latency_ms"]
        )
        
    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        return []
        
    async def update_memory(self, result: Any) -> None:
        pass
        
    async def publish(self, result: Any) -> None:
        pass
        
    async def health(self) -> Any:
        return {"status": self.status.value}
        
    async def shutdown(self) -> None:
        self.status = AgentStatus.SHUTDOWN

