from fastapi import APIRouter, HTTPException
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
    registry = await get_model_registry()
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
    
    # Simulate batch data
    np.random.seed(42)
    reference_features = np.random.randn(1000, 5)
    
    # Introduce slight drift
    current_features = np.random.randn(200, 5) * 1.1 + 0.15 
    
    current_predictions = (np.random.rand(200) > 0.8).astype(int)
    current_confidences = np.random.uniform(0.5, 1.0, size=200)
    
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
