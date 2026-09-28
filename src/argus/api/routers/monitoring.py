"""Monitoring and model drift evaluation router."""

import os
import yaml
from typing import Dict, Any
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, status
from structlog import get_logger

from argus.monitoring.drift import analyze_batch_drift, DriftConfig, DriftReport
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal
from argus.data.manager import ALLOWED_DOMAINS

logger = get_logger("argus.monitoring")

router = APIRouter()

REGISTRY_PATH = "artifacts/models/registry.yaml"


@router.get("/registry", summary="Get model provenance registry")
async def get_model_registry(
    user: UserPrincipal = Depends(require_permission("read:monitoring"))
) -> Dict[str, Any]:
    """Retrieve verified model provenance registry."""
    if not os.path.exists(REGISTRY_PATH):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model registry metadata file not found.")

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = yaml.safe_load(f)
        return registry or {}
    except Exception as e:
        logger.error("model_registry_read_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load model registry metadata."
        )


@router.get("/drift/{model_id}", summary="Get drift status for a specific model")
async def get_drift_status(
    model_id: str,
    user: UserPrincipal = Depends(require_permission("read:monitoring"))
) -> DriftReport:
    """Evaluate batch distribution drift for a specified model."""
    if not model_id or not isinstance(model_id, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid model_id.")

    # Read registry safely without invalid arguments
    registry = await get_model_registry(user=user)
    models = registry.get("models", {})

    model_info = None
    for key, info in models.items():
        if info.get("model_id") == model_id or key == model_id:
            model_info = info
            break

    if not model_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Model '{model_id}' not found in registry.")

    source_domain = model_info.get("source_domain", "UNKNOWN")
    target_domain = model_info.get("target_domain", "UNKNOWN")

    if target_domain not in ALLOWED_DOMAINS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported target domain: '{target_domain}'.")

    ref_path = "data/samples/ciciot.parquet"
    tgt_path = f"data/samples/{target_domain}.parquet"
    if not os.path.exists(ref_path) or not os.path.exists(tgt_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample data for drift monitoring not found."
        )

    try:
        ref_df = pd.read_parquet(ref_path).head(1000)
        tgt_df = pd.read_parquet(tgt_path).head(200)

        features_cols = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
        reference_features = ref_df[features_cols].values
        current_features = tgt_df[features_cols].values

        current_predictions = tgt_df["label"].values if "label" in tgt_df.columns else np.zeros(len(tgt_df))
        current_confidences = np.full(len(tgt_df), 0.95)

        report = analyze_batch_drift(
            current_features=current_features,
            current_predictions=current_predictions,
            current_confidences=current_confidences,
            reference_features=reference_features,
            source_domain=source_domain,
            target_domain=target_domain,
            config=DriftConfig()
        )
        return report
    except Exception as e:
        logger.error("drift_analysis_failed", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Drift analysis calculation failed."
        )
