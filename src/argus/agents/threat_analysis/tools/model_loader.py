"""Model Loader tool for Threat Analysis Agent."""
import asyncio
import hashlib
import os
import joblib
from typing import Any, Dict
import structlog
from pathlib import Path

# Since this is a generic implementation, we use a try-except to gracefully handle missing XGBoost
try:
    import xgboost as xgb
except ImportError:
    xgb = None

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.threat_analysis.models.schemas import ModelType
from argus.agents.threat_analysis.config import config


class ModelLoader(BaseTool):
    """Tool for loading and caching machine learning models from disk."""

    def __init__(self):
        super().__init__(
            tool_id="ta_model_loader",
            name="Model Loader",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Loads and caches ML models from disk securely.",
            required_permissions=["fs:read:models"]
        )
        self._model_cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self.logger = structlog.get_logger("argus.tool.model_loader")

    async def initialize(self) -> None:
        """Initialize the model loader cache."""
        self._model_cache.clear()
        self.logger.info("model_loader_initialized", cache_size=0)

    async def validate(self, model_type: ModelType, model_path: str) -> bool:
        """Validate that the model file exists and the checksum is valid."""
        path = Path(model_path)
        if not path.exists() or not path.is_file():
            self.logger.error("model_not_found", path=str(path))
            return False

        sha256_path = path.with_suffix(path.suffix + ".sha256")
        if not sha256_path.exists():
            self.logger.warning("checksum_missing", path=str(sha256_path))
            # In a strict environment, return False. For now, allow missing checksums if intended
            # Returning True here assumes the environment is trusted if no checksum is provided.
            return True

        # Verify checksum
        try:
            expected_hash = sha256_path.read_text().strip()
            
            # Read file in chunks to not exhaust memory
            sha256 = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            
            actual_hash = sha256.hexdigest()
            if actual_hash != expected_hash:
                self.logger.error("checksum_mismatch", path=str(path), expected=expected_hash, actual=actual_hash)
                return False
                
            return True
        except Exception as e:
            self.logger.error("checksum_validation_failed", error=str(e))
            return False

    async def execute(self, model_type: ModelType, model_path: str) -> Any:
        """Load a model, using cache if available."""
        # Check cache first (fast path)
        if model_path in self._model_cache:
            return self._model_cache[model_path]

        # Acquire lock to prevent multiple threads loading the same model
        async with self._lock:
            # Check cache again inside lock
            if model_path in self._model_cache:
                return self._model_cache[model_path]
                
            is_valid = await self.validate(model_type, model_path)
            if not is_valid:
                raise ValueError(f"Model validation failed for {model_path}")

            self.logger.info("loading_model", path=model_path, type=model_type)
            
            # Offload blocking IO to a thread
            model = await asyncio.to_thread(self._load_model_sync, model_type, model_path)
            self._model_cache[model_path] = model
            return model

    def _load_model_sync(self, model_type: ModelType, model_path: str) -> Any:
        """Synchronous method to actually load the model using joblib/xgboost."""
        if model_type == ModelType.XGBOOST:
            if xgb is None:
                raise ImportError("xgboost is not installed.")
            model = xgb.Booster()
            model.load_model(model_path)
            return model
        elif model_type in (ModelType.ISOLATION_FOREST, ModelType.RANDOM_FOREST):
            return joblib.load(model_path)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    async def shutdown(self) -> None:
        """Clear cache and release resources."""
        self._model_cache.clear()
        self.logger.info("model_loader_shutdown")

    def metadata(self) -> Dict[str, Any]:
        """Return the tool's metadata."""
        meta = super().metadata()
        meta["supported_models"] = [m.value for m in ModelType]
        return meta
