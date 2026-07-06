"""Inference Engine tool for Threat Analysis Agent."""
import asyncio
import time
from typing import Any, Dict, List, Optional
import structlog

try:
    import numpy as np
except ImportError:
    np = None
    
try:
    import xgboost as xgb
except ImportError:
    xgb = None

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.threat_analysis.models.schemas import ModelType, InferenceResult


class InferenceEngine(BaseTool):
    """Tool for running ML inference on feature vectors."""

    def __init__(self):
        super().__init__(
            tool_id="ta_inference_engine",
            name="Inference Engine",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Executes ML models against feature vectors.",
            required_permissions=["compute:inference"]
        )
        self.logger = structlog.get_logger("argus.tool.inference_engine")

    async def initialize(self) -> None:
        """Initialize the inference engine."""
        if np is None:
            self.logger.warning("numpy_not_installed", msg="Inference might fail if dependencies are missing.")
        self.logger.info("inference_engine_initialized")

    async def validate(self, features: Dict[str, float], model: Any, model_type: ModelType) -> bool:
        """Validate input features against expected model format."""
        if not features:
            self.logger.error("empty_features")
            return False
        if model is None:
            self.logger.error("null_model")
            return False
        return True

    async def execute(self, features: Dict[str, float], model: Any, model_type: ModelType) -> InferenceResult:
        """Execute inference."""
        is_valid = await self.validate(features=features, model=model, model_type=model_type)
        if not is_valid:
            raise ValueError("Validation failed for inference inputs.")

        start_time = time.perf_counter()

        # Run inference in a thread pool to avoid blocking the event loop
        prediction, probabilities, raw_output = await asyncio.to_thread(
            self._run_inference_sync, features, model, model_type
        )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return InferenceResult(
            prediction=prediction,
            probabilities=probabilities,
            raw_output=raw_output,
            model_type=model_type,
            latency_ms=latency_ms
        )

    def _run_inference_sync(self, features: Dict[str, float], model: Any, model_type: ModelType) -> tuple[Any, Optional[List[float]], Any]:
        """Synchronous inference execution."""
        # Note: In a real system, we must align feature names to the model's expected training order.
        # Here we assume the keys in features dict are ordered or we just sort them for stability.
        sorted_feature_values = [features[k] for k in sorted(features.keys())]
        
        # Reshape to 2D array (1 sample, n features)
        X = np.array(sorted_feature_values).reshape(1, -1) if np is not None else [sorted_feature_values]

        prediction = None
        probabilities = None
        raw_output = {}

        if model_type == ModelType.XGBOOST:
            if xgb is None:
                raise ImportError("xgboost is not installed")
            
            dmatrix = xgb.DMatrix(X, feature_names=sorted(features.keys()))
            # predict returns probabilities for classification by default in many XGB setups
            preds = model.predict(dmatrix)
            raw_output["raw_preds"] = preds.tolist()
            
            if len(preds.shape) > 1 and preds.shape[1] > 1:
                # Multiclass
                probabilities = preds[0].tolist()
                prediction = int(np.argmax(preds[0])) if np is not None else int(preds[0].index(max(preds[0])))
            else:
                # Binary
                prob = float(preds[0])
                probabilities = [1.0 - prob, prob]
                prediction = 1 if prob > 0.5 else 0

        elif model_type in (ModelType.RANDOM_FOREST, ModelType.ISOLATION_FOREST):
            # scikit-learn models
            preds = model.predict(X)
            prediction = int(preds[0])
            raw_output["prediction"] = prediction

            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X)
                probabilities = probs[0].tolist()
                raw_output["probabilities"] = probabilities
            
            if hasattr(model, "decision_function"):
                scores = model.decision_function(X)
                raw_output["decision_function"] = float(scores[0])
                
                # Isolation forest convention: -1 is anomaly, 1 is normal
                # Some implementations vary, we capture the raw score
        
        else:
            raise ValueError(f"Unsupported model type for inference: {model_type}")

        return prediction, probabilities, raw_output

    async def shutdown(self) -> None:
        """Clean up."""
        self.logger.info("inference_engine_shutdown")

    def metadata(self) -> Dict[str, Any]:
        """Tool metadata."""
        return super().metadata()
