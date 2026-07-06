"""Evidence Collector tool for Threat Analysis Agent."""
from typing import Any, Dict, List
import structlog

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.threat_analysis.models.schemas import Evidence, InferenceResult


class EvidenceCollector(BaseTool):
    """Collects and formats evidence supporting the threat classification."""

    def __init__(self):
        super().__init__(
            tool_id="ta_evidence_collector",
            name="Evidence Collector",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Collects supporting evidence for inference results.",
            required_permissions=["compute:inference"]
        )
        self.logger = structlog.get_logger("argus.tool.evidence_collector")

    async def initialize(self) -> None:
        """Initialize the evidence collector."""
        self.logger.info("evidence_collector_initialized")

    async def validate(self, features: Dict[str, float], inference_result: InferenceResult) -> bool:
        """Validate inputs."""
        if not features or not inference_result:
            return False
        return True

    async def execute(self, features: Dict[str, float], inference_result: InferenceResult) -> List[Evidence]:
        """Collect evidence from features and inference result."""
        is_valid = await self.validate(features, inference_result)
        if not is_valid:
            raise ValueError("Invalid inputs to EvidenceCollector")

        evidence_list: List[Evidence] = []
        
        # 1. Look for extreme feature values as basic evidence
        # In a real system, this would compare against a baseline mean/stddev.
        # For this mock, we highlight features with large absolute values.
        for feat_name, feat_val in features.items():
            # Heuristic: arbitrarily flag values > 100 or < -100 as 'anomalous' features
            if abs(feat_val) > 100.0:
                evidence_list.append(
                    Evidence(
                        type="extreme_feature",
                        description=f"Feature '{feat_name}' has an unusually large magnitude.",
                        importance=0.8,
                        value=feat_val
                    )
                )

        # 2. Extract model-specific evidence
        if "decision_function" in inference_result.raw_output:
            score = inference_result.raw_output["decision_function"]
            evidence_list.append(
                Evidence(
                    type="anomaly_score",
                    description="Isolation Forest decision function score.",
                    importance=1.0 if score < 0 else 0.5,
                    value=score
                )
            )
            
        if "probabilities" in inference_result.raw_output:
            probs = inference_result.raw_output["probabilities"]
            if len(probs) >= 2:
                evidence_list.append(
                    Evidence(
                        type="malicious_probability",
                        description="Model estimated probability of malicious class.",
                        importance=probs[1],
                        value=probs[1]
                    )
                )

        # Sort evidence by importance descending
        evidence_list.sort(key=lambda e: e.importance, reverse=True)
        
        self.logger.info("evidence_collected", count=len(evidence_list))
        return evidence_list

    async def shutdown(self) -> None:
        """Clean up."""
        pass
