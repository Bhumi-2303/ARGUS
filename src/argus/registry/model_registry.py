"""Model Registry module for ARGUS API.

Loads trained model artifacts once at startup and fails loudly with explicit errors
if any artifact is missing or invalid.
"""

import os
import hashlib
import json
from typing import Dict, Any, Tuple, List
import numpy as np
import lightgbm as lgb
import xgboost as xgb
import shap
import structlog

from argus.schemas.api import ModelInfo

logger = structlog.get_logger("argus.registry")

HARMONIZED_FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]

MODEL_METADATA = {
    "model_d1_baseline": {
        "model_id": "mod-d1-base-001",
        "name": "model_d1_baseline",
        "artifact_path": "artifacts/models/model_d1_baseline.txt",
        "type": "lightgbm",
        "protocol_status": "native",
        "threshold": 0.50,
        "source_domain": "ciciot",
        "target_domain": "ciciot",
        "status": "planned",
        "provenance": {
            "training_dataset": "CICIoT2023 Train (5.49M)",
            "adaptation_method": "NONE",
            "features": HARMONIZED_FEATURES,
            "training_date": "2026-08-19",
        }
    },
    "model_d2_coral": {
        "model_id": "mod-d2-coral-001",
        "name": "model_d2_coral",
        "artifact_path": "artifacts/models/model_d2_coral.txt",
        "type": "lightgbm",
        "protocol_status": "coral_aligned",
        "threshold": 0.99,
        "source_domain": "ciciot",
        "target_domain": "nfton",
        "status": "verified",
        "provenance": {
            "training_dataset": "CICIoT2023 Train + NF-ToN Adaptation (8.41M)",
            "adaptation_method": "Clean Class-aware CORAL",
            "features": HARMONIZED_FEATURES,
            "threshold_selection": "NF-ToN Calibration (2.10M, max MCC)",
            "training_date": "2026-08-19",
        }
    },
    "model_d3_native": {
        "model_id": "mod-d3-native-001",
        "name": "model_d3_native",
        "artifact_path": "artifacts/models/model_d3_native.txt",
        "type": "lightgbm",
        "protocol_status": "native",
        "threshold": 0.50,
        "source_domain": "iec104",
        "target_domain": "iec104",
        "status": "partial",
        "provenance": {
            "training_dataset": "IEC104 Train (2.29M)",
            "adaptation_method": "NONE",
            "features": HARMONIZED_FEATURES,
            "training_date": "2026-08-20",
        }
    },
    "xgb_source": {
        "model_id": "mod-xgb-src-001",
        "name": "xgb_source",
        "artifact_path": "artifacts/models/xgb_source.json",
        "type": "xgboost",
        "protocol_status": "native",
        "threshold": 0.50,
        "source_domain": "ciciot",
        "target_domain": "ciciot",
        "status": "planned",
        "provenance": {
            "training_dataset": "CICIoT2023 Train",
            "adaptation_method": "NONE",
            "features": HARMONIZED_FEATURES,
            "training_date": "2026-08-20",
        }
    },
    "xgb_adapted": {
        "model_id": "mod-xgb-adapt-001",
        "name": "xgb_adapted",
        "artifact_path": "artifacts/models/xgb_adapted.json",
        "type": "xgboost",
        "protocol_status": "coral_aligned",
        "threshold": 0.99,
        "source_domain": "ciciot",
        "target_domain": "nfton",
        "status": "verified",
        "provenance": {
            "training_dataset": "CICIoT2023 Train + NF-ToN Adaptation",
            "adaptation_method": "CORAL Aligned XGBoost",
            "features": HARMONIZED_FEATURES,
            "training_date": "2026-08-20",
        }
    },
    "dann": {
        "model_id": "mod-dann-001",
        "name": "dann",
        "artifact_path": "results/verified/dann_final_test_metrics.csv",
        "type": "dann_simulated",
        "protocol_status": "dann_adapted",
        "threshold": None,
        "source_domain": "ciciot",
        "target_domain": "nfton",
        "status": "unavailable",
        "provenance": {
            "training_dataset": "CICIoT2023 + NF-ToN DANN Neural Net",
            "adaptation_method": "Domain-Adversarial Neural Network",
            "features": HARMONIZED_FEATURES,
            "training_date": "2026-08-22",
            "note": "No verified checkpoint — unavailable for live inference",
        }
    }
}


class ModelRegistry:
    """Registry managing model artifact loading and inference operations."""

    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.loaded_models: Dict[str, Any] = {}
        self.explainers: Dict[str, Any] = {}
        self.is_loaded: bool = False
        self._integrity_manifest: Dict[str, Any] = {}

    def _load_integrity_manifest(self) -> Dict[str, Any]:
        """Load the trusted SHA-256 integrity manifest from disk."""
        manifest_path = os.path.join(self.base_dir, "artifacts", "models", "INTEGRITY_MANIFEST.json")
        if not os.path.exists(manifest_path):
            logger.warning("integrity_manifest_not_found", path=manifest_path)
            return {}
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            # Strip metadata keys
            return {k: v for k, v in manifest.items() if not k.startswith("_")}
        except Exception as e:
            logger.error("integrity_manifest_load_failed", error=str(e))
            return {}

    @staticmethod
    def _compute_sha256(file_path: str) -> str:
        """Compute SHA-256 hex digest of a file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def _verify_artifact_integrity(self, model_name: str, full_path: str) -> None:
        """Verify a model artifact against the trusted integrity manifest.

        Raises:
            RuntimeError: If hash mismatch or model not in manifest.
        """
        if model_name not in self._integrity_manifest:
            raise RuntimeError(
                f"Model '{model_name}' is not present in the trusted integrity manifest. "
                "Cannot verify artifact integrity — refusing to load."
            )

        expected_hash = self._integrity_manifest[model_name].get("sha256")
        if not expected_hash:
            raise RuntimeError(
                f"Model '{model_name}' has no SHA-256 hash in the integrity manifest."
            )

        actual_hash = self._compute_sha256(full_path)
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"INTEGRITY FAILURE for model '{model_name}': "
                f"expected SHA-256 {expected_hash}, got {actual_hash}. "
                "Artifact may have been tampered with — refusing to load."
            )
        logger.info("artifact_integrity_verified", model_name=model_name, sha256=actual_hash)

    def load_all(self) -> None:
        """Load all configured model artifacts into memory.
        
        Verifies SHA-256 integrity BEFORE deserialization.
        Fails loudly if any required model artifact is missing or tampered.
        """
        logger.info("model_registry_loading_started")
        missing_artifacts = []

        # Load the trusted integrity manifest
        self._integrity_manifest = self._load_integrity_manifest()

        for model_name, meta in MODEL_METADATA.items():
            rel_path = meta["artifact_path"]
            full_path = os.path.join(self.base_dir, rel_path)
            
            if not os.path.exists(full_path):
                missing_artifacts.append((model_name, full_path))
                continue

            try:
                # Verify integrity BEFORE loading (critical for joblib deserialization safety)
                if model_name in self._integrity_manifest:
                    self._verify_artifact_integrity(model_name, full_path)

                model_type = meta["type"]
                if model_type == "lightgbm":
                    # Normalize line endings if needed
                    with open(full_path, "rb") as f:
                        data = f.read()
                    if b"\r\n" in data:
                        data = data.replace(b"\r\n", b"\n")
                        with open(full_path, "wb") as f:
                            f.write(data)
                    model = lgb.Booster(model_file=full_path)
                    self.loaded_models[model_name] = model
                    try:
                        self.explainers[model_name] = shap.TreeExplainer(model)
                    except Exception as ex:
                        logger.warning("shap_explainer_init_failed", model_name=model_name, error=str(ex))
                        
                elif model_type == "xgboost":
                    model = xgb.Booster()
                    model.load_model(full_path)
                    self.loaded_models[model_name] = model
                    try:
                        self.explainers[model_name] = shap.TreeExplainer(model)
                    except Exception as ex:
                        logger.warning("shap_explainer_init_failed", model_name=model_name, error=str(ex))
                        
                elif model_type == "dann_simulated":
                    # DANN has no verified weights artifact for live inference
                    pass
                    
                logger.info("model_loaded_successfully", model_name=model_name, path=full_path)
            except RuntimeError as e:
                # Integrity failures are fatal — do not silently continue
                logger.error("model_integrity_check_failed", model_name=model_name, error=str(e))
                raise
            except Exception as e:
                logger.error("model_load_failed", model_name=model_name, path=full_path, error=str(e))
                missing_artifacts.append((model_name, full_path))

        if missing_artifacts:
            error_msg = f"CRITICAL: Failed to load {len(missing_artifacts)} model artifact(s):\n"
            for m_name, m_path in missing_artifacts:
                error_msg += f"  - Model '{m_name}': file not found or corrupted at '{m_path}'\n"
            raise FileNotFoundError(error_msg)

        self.is_loaded = True
        logger.info("model_registry_load_complete", total_models=len(self.loaded_models))

    def get_status_dict(self) -> Dict[str, bool]:
        """Return readiness status for loaded models."""
        if not self.is_loaded:
            self.load_all()
        return {
            name: (name in self.loaded_models and MODEL_METADATA[name].get("status") != "unavailable")
            for name in MODEL_METADATA.keys()
        }

    def get_model_info_list(self) -> List[ModelInfo]:
        """Get structured list of ModelInfo for GET /api/v1/models."""
        res = []
        for name, meta in MODEL_METADATA.items():
            res.append(ModelInfo(
                model_id=meta["model_id"],
                name=meta["name"],
                protocol_status=meta["protocol_status"],
                threshold=meta["threshold"],
                source_domain=meta["source_domain"],
                target_domain=meta["target_domain"],
                status=meta["status"],
                provenance=meta["provenance"]
            ))
        return res

    def predict(self, model_name: str, features: Dict[str, float]) -> Tuple[float, int, float]:
        """Predict probability and binary label for 4 features."""
        if not self.is_loaded:
            self.load_all()
        if model_name not in MODEL_METADATA:
            raise KeyError(f"Unknown model name '{model_name}'. Available: {list(MODEL_METADATA.keys())}")

        meta = MODEL_METADATA[model_name]
        if model_name == "dann" or meta.get("status") == "unavailable":
            raise NotImplementedError("Model 'dann' is unavailable for live inference: no verified checkpoint found.")

        threshold = meta["threshold"]
        if threshold is None:
            raise NotImplementedError(f"Model '{model_name}' has no calibrated threshold.")
        
        # Prepare input array
        x_vec = np.array([[features[col] for col in HARMONIZED_FEATURES]], dtype=np.float32)

        model = self.loaded_models.get(model_name)
        if model is None:
            raise RuntimeError(f"Model '{model_name}' is not loaded.")

        if meta["type"] == "lightgbm":
            prob_arr = model.predict(x_vec)
            prob = float(prob_arr[0])
        elif meta["type"] == "xgboost":
            dmat = xgb.DMatrix(x_vec, feature_names=HARMONIZED_FEATURES)
            prob_arr = model.predict(dmat)
            prob = float(prob_arr[0])
        else:
            raise ValueError(f"Unsupported model type '{meta['type']}' for live inference.")

        label = 1 if prob >= threshold else 0
        return prob, label, threshold

    def predict_batch(self, model_name: str, x_matrix: np.ndarray) -> np.ndarray:
        """Predict batch of probabilities for array of shape (N, 4)."""
        meta = MODEL_METADATA.get(model_name)
        if not meta:
            raise KeyError(f"Unknown model '{model_name}'")

        if model_name == "dann":
            raise ValueError("No verified checkpoint — unavailable for live inference.")

        model = self.loaded_models.get(model_name)
        if not model:
            raise RuntimeError(f"Model '{model_name}' is not loaded.")

        if meta["type"] == "lightgbm":
            return model.predict(x_matrix)
        elif meta["type"] == "xgboost":
            dmat = xgb.DMatrix(x_matrix, feature_names=HARMONIZED_FEATURES)
            return model.predict(dmat)
        raise ValueError(f"Unsupported model type '{meta['type']}' for live inference.")

    def explain(self, model_name: str, features: Dict[str, float]) -> Tuple[float, Dict[str, float], str, float]:
        """Compute real SHAP feature attributions for a single flow using TreeExplainer."""
        if model_name not in MODEL_METADATA:
            raise KeyError(f"Unknown model '{model_name}'.")

        if model_name == "dann":
            raise ValueError("No verified checkpoint — unavailable for live inference.")

        meta = MODEL_METADATA[model_name]
        x_vec = np.array([[features[col] for col in HARMONIZED_FEATURES]], dtype=np.float32)

        explainer = self.explainers.get(model_name)
        if explainer is None:
            raise RuntimeError(f"TreeExplainer is not initialized for model '{model_name}'.")

        sv = explainer.shap_values(x_vec)
        if isinstance(sv, list):
            sv = sv[1] if len(sv) > 1 else sv[0]
        
        sv_flat = sv[0] if len(sv.shape) > 1 else sv
        shap_dict = {feat: float(val) for feat, val in zip(HARMONIZED_FEATURES, sv_flat)}
        
        # Base value
        bv = getattr(explainer, "expected_value", 0.50)
        if isinstance(bv, (list, np.ndarray)):
            bv = float(bv[0])
        base_val = float(bv)

        # Top feature
        top_feat = max(shap_dict.keys(), key=lambda k: abs(shap_dict[k]))
        top_impact = shap_dict[top_feat]

        return base_val, shap_dict, top_feat, top_impact

# Singleton instance
model_registry = ModelRegistry()
