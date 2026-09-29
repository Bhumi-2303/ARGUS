"""ARGUS Model Loader & Predictor Wrappers."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


class ArgusModelWrapper:
    """Unified predictor wrapper for ARGUS models."""
    
    def __init__(self, model_type: str, model_path: str):
        self.model_type = model_type
        self.model_path = model_path
        self._model = None
        self.load()

    def load(self):
        """Loads model weights based on model type."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model path does not exist: {self.model_path}")
            
        if self.model_type == "xgboost":
            import xgboost as xgb
            self._model = xgb.XGBClassifier()
            if self.model_path.endswith(".json"):
                self._model.load_model(self.model_path)
            else:
                import joblib
                self._model = joblib.load(self.model_path)
        elif self.model_type == "lightgbm":
            import lightgbm as lgb
            if self.model_path.endswith(".txt"):
                self._model = lgb.Booster(model_file=self.model_path)
            else:
                import joblib
                self._model = joblib.load(self.model_path)
        elif self.model_type == "dann":
            import torch
            self._model = torch.load(self.model_path, map_location="cpu", weights_only=True)
        else:
            import joblib
            self._model = joblib.load(self.model_path)

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
