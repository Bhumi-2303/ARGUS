from fastapi import APIRouter, HTTPException, Depends
import yaml
import os
import numpy as np
from argus.monitoring.drift import analyze_batch_drift, DriftConfig, DriftReport
from typing import Dict, Any

router = APIRouter()

REGISTRY_PATH = "artifacts/models/registry.yaml"

@router.get("/registry", summary="Get model provenance registry")
async def get_model_registry() -> Dict[str, Any]:
    if not os.path.exists(REGISTRY_PATH):
        raise HTTPException(status_code=404, detail="Model registry not found")
        
    with open(REGISTRY_PATH, "r") as f:
        registry = yaml.safe_load(f)
        
    return registry

@router.get("/drift/{model_id}", summary="Get drift status for a specific model")
async def get_drift_status(model_id: str) -> DriftReport:
    # In a real environment, this would pull the latest batch of features/predictions 
    # from a database (e.g. Postgres or TimescaleDB) for the given model_id.
    # For demonstration/monitoring exposition, we generate a synthetic drift report
    # representing current batch state.
    
    # Read registry to get domain info
    registry = await get_model_registry(user=user)
    models = registry.get("models", {})
    
    # Find model by id or key
    model_info = None
    for key, info in models.items():
        if info.get("model_id") == model_id or key == model_id:
            model_info = info
            break
            
    if not model_info:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found in registry")
        
    source_domain = model_info.get("source_domain", "UNKNOWN")
    target_domain = model_info.get("target_domain", "UNKNOWN")
    
    # Read real sample feature distributions from data_manager
    ref_path = "data/samples/ciciot.parquet"
    tgt_path = f"data/samples/{target_domain}.parquet"
    if not os.path.exists(ref_path) or not os.path.exists(tgt_path):
        raise HTTPException(
            status_code=404,
            detail="REQUIRES VERIFICATION: Sample data for drift monitoring not found."
        )

    import pandas as pd
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
