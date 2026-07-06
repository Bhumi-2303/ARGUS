"""Confidence Calculator tool for Threat Analysis Agent."""
from typing import Any, Dict
import structlog

try:
    import numpy as np
except ImportError:
    np = None

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.threat_analysis.models.schemas import (
    ModelType, InferenceResult, ConfidenceResult, ThreatLevel
)
from argus.agents.threat_analysis.config import config


class ConfidenceCalculator(BaseTool):
    """Calculates confidence and maps to threat levels."""

    def __init__(self):
        super().__init__(
            tool_id="ta_confidence_calc",
            name="Confidence Calculator",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Derives confidence scores and threat levels from inference results.",
            required_permissions=["compute:inference"]
        )
        self.logger = structlog.get_logger("argus.tool.confidence_calculator")

    async def initialize(self) -> None:
        """Initialize the confidence calculator."""
        self.logger.info("confidence_calculator_initialized")

    async def validate(self, inference_result: InferenceResult) -> bool:
        """Validate input."""
        if not inference_result:
            return False
        return True

    async def execute(self, inference_result: InferenceResult) -> ConfidenceResult:
        """Calculate confidence from inference result."""
        is_valid = await self.validate(inference_result=inference_result)
        if not is_valid:
            raise ValueError("Invalid inference result provided to ConfidenceCalculator.")

        confidence_score = self._compute_confidence(inference_result)
        threat_level = self._map_to_threat_level(confidence_score, inference_result)

        self.logger.info(
            "confidence_calculated",
            score=confidence_score,
            level=threat_level.value,
            model=inference_result.model_type.value
        )

        return ConfidenceResult(
            confidence_score=confidence_score,
            threat_level=threat_level,
            threshold_used=config.confidence_threshold
        )

    def _compute_confidence(self, result: InferenceResult) -> float:
        """Compute a normalized 0.0 to 1.0 confidence score."""
        if result.model_type in (ModelType.XGBOOST, ModelType.RANDOM_FOREST):
            # Assume binary classification where class 1 is malicious
            if result.probabilities and len(result.probabilities) == 2:
                # Return the probability of class 1 as confidence of threat
                return float(result.probabilities[1])
            elif result.probabilities:
                # Multiclass? Return the max probability if it's the predicted class
                return float(max(result.probabilities))
            else:
                # Fallback if no proba
                return 1.0 if result.prediction == 1 else 0.0
                
        elif result.model_type == ModelType.ISOLATION_FOREST:
            # Isolation Forest decision_function: < 0 is anomaly, > 0 is normal.
            # We map negative scores to high threat confidence.
            # Typical range might be -0.5 to 0.5.
            if "decision_function" in result.raw_output:
                score = result.raw_output["decision_function"]
                if score < 0:
                    # Anomaly. Map -0.5 -> 1.0, 0.0 -> 0.5
                    # Simple linear scaling for demonstration:
                    mapped = 0.5 + min(abs(score), 0.5)
                    return mapped
                else:
                    # Normal. Map 0.0 -> 0.5, 0.5 -> 0.0
                    mapped = max(0.5 - score, 0.0)
                    return mapped
            else:
                # Fallback to binary prediction (-1 = anomaly, 1 = normal)
                return 1.0 if result.prediction == -1 else 0.0
                
        return 0.0

    def _map_to_threat_level(self, confidence: float, result: InferenceResult) -> ThreatLevel:
        """Map confidence score to a ThreatLevel enum."""
        # For non-anomalies (score < 0.5), it's INFO or LOW
        if confidence < 0.5:
            return ThreatLevel.INFO
            
        if confidence >= 0.9:
            return ThreatLevel.CRITICAL
        elif confidence >= 0.8:
            return ThreatLevel.HIGH
        elif confidence >= config.confidence_threshold:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    async def shutdown(self) -> None:
        """Clean up."""
        pass
