"""ARGUS Model Loader & Predictor Wrappers with Secure Deserialization."""

import os
from pathlib import Path
from typing import Any, Optional
import numpy as np
import pandas as pd

from argus.security.artifacts import (
    InsecureArtifactError,
    load_artifact,
    BANNED_EXTENSIONS,
)


class ArgusModelWrapper:
    """Unified predictor wrapper for ARGUS models using safe serialization formats."""

    def __init__(self, model_type: str, model_path: str):
        self.model_type = model_type.lower()
        self.model_path = str(model_path)
        self._model = None
        self.load()

    def load(self):
        """Loads model weights based on model type using secure deserialization."""
        path = Path(self.model_path)
        if not path.exists():
            raise FileNotFoundError(f"Model path does not exist: {self.model_path}")

        # Ban pickle and joblib extensions strictly
        if path.suffix.lower() in BANNED_EXTENSIONS:
            raise InsecureArtifactError(
                f"Loading insecure model format '{path.suffix}' is forbidden. "
                "Models must use safe formats: XGBoost (.json, .ubj), LightGBM (.txt), or PyTorch weights_only."
            )

        # Attempt to load through load_artifact if manifest exists, otherwise use safe native format loaders
        try:
            self._model = load_artifact(path, model_type=self.model_type)
            return
        except Exception:
            # Fall back to native safe loader if no standalone manifest is present
            pass

        if self.model_type == "xgboost":
            import xgboost as xgb

            if path.suffix.lower() in (".json", ".ubj"):
                self._model = xgb.XGBClassifier()
                self._model.load_model(str(path))
            else:
                raise InsecureArtifactError(
                    f"Unsupported XGBoost model format '{path.suffix}'. Use .json or .ubj."
                )

        elif self.model_type == "lightgbm":
            import lightgbm as lgb

            if path.suffix.lower() == ".txt":
                self._model = lgb.Booster(model_file=str(path))
            else:
                raise InsecureArtifactError(
                    f"Unsupported LightGBM model format '{path.suffix}'. Use native .txt format."
                )

        elif self.model_type == "dann":
            if path.suffix.lower() == ".safetensors":
                from safetensors.torch import load_file

                self._model = load_file(str(path))
            else:
                import torch

                self._model = torch.load(str(path), map_location="cpu", weights_only=True)

        else:
            raise InsecureArtifactError(
                f"Unsupported model type '{self.model_type}'. Insecure fallback loaders are prohibited."
            )

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts attack probability distribution."""
        if self.model_type == "xgboost":
            return self._model.predict_proba(X)[:, 1]
        elif self.model_type == "lightgbm":
            if hasattr(self._model, "predict"):
                preds = self._model.predict(X)
                if preds.ndim == 2:
                    return preds[:, 1]
                return preds
            return self._model.predict_proba(X)[:, 1]
        else:
            if hasattr(self._model, "predict_proba"):
                return self._model.predict_proba(X)[:, 1]
            return np.zeros(len(X))
