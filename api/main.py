import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Dict, Union, Any

import numpy as np
import lightgbm as lgb
import shap
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Constants & Configurations
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = str(PROJECT_ROOT / "phase3_results/models/model_d2_coral.txt")
MODEL_PATH = os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH)
THRESHOLD = float(os.getenv("THRESHOLD", "0.50"))
FEATURE_NAMES = [
    "pkt_mean_to_max",
    "tcp_flag_density",
    "log_pkt_mean",
    "log_pkt_max"
]

# Global variables for persistent model & explainer instance
model = None
explainer = None

class FlowRecord(BaseModel):
    pkt_mean_to_max: float = Field(..., description="Ratio of mean packet length to max packet length [0,1]")
    tcp_flag_density: float = Field(..., description="TCP flag multiplicity count")
    log_pkt_mean: float = Field(..., description="Log-transformed mean packet length")
    log_pkt_max: float = Field(..., description="Log-transformed max packet length")

    model_config = {
        "json_schema_extra": {
            "example": {
                "pkt_mean_to_max": 0.95,
                "tcp_flag_density": 1.0,
                "log_pkt_mean": 4.2,
                "log_pkt_max": 4.3
            }
        }
    }

class PredictionItem(BaseModel):
    prediction: int = Field(..., description="Binary detection label (1=Attack, 0=Benign)")
    probability: float = Field(..., description="Continuous attack detection probability")
    threshold: float = Field(..., description="Decision threshold used (default: 0.50)")
    shap_values: Dict[str, float] = Field(..., description="Per-feature SHAP contribution values")

class PredictionResponse(BaseModel):
    predictions: List[PredictionItem]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager: loads model and initializes SHAP TreeExplainer once at startup."""
    global model, explainer
    model_file = Path(MODEL_PATH)
    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found at path: {MODEL_PATH}")
    
    print(f"[*] Loading trained LightGBM model from: {MODEL_PATH}")
    model = lgb.Booster(model_file=str(model_file))
    
    print("[*] Initializing SHAP TreeExplainer...")
    explainer = shap.TreeExplainer(model)
    print("[+] Model and SHAP TreeExplainer initialized successfully.")
    
    yield
    
    print("[*] Shutting down FastAPI service.")

app = FastAPI(
    title="ARGUS Cross-Domain Intrusion Detection API",
    description="FastAPI service serving trained cross-domain intrusion detector for IEC 60870-5-104 SCADA target domain.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    """Health check endpoint returning service status and model metadata."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH,
        "target_domain": "IEC 60870-5-104 (SCADA)",
        "threshold": THRESHOLD,
        "features": FEATURE_NAMES
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(payload: Union[List[FlowRecord], FlowRecord, Dict[str, Any]]):
    """
    POST /predict endpoint.
    Accepts a single flow record, a list of flow records, or a dict containing a 'records' key.
    Returns probability, binary prediction at theta=0.50, and per-feature SHAP values.
    """
    if model is None or explainer is None:
        raise HTTPException(status_code=503, detail="Model service is not initialized.")
    
    # Flexible parsing of input payload
    if isinstance(payload, FlowRecord):
        records = [payload]
    elif isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict) and "records" in payload:
        records = [FlowRecord(**r) for r in payload["records"]]
    elif isinstance(payload, dict):
        records = [FlowRecord(**payload)]
    else:
        raise HTTPException(status_code=400, detail="Invalid request payload format.")

    if not records:
        raise HTTPException(status_code=400, detail="No flow records provided.")

    # Construct input feature matrix (N, 4) in exact order
    X_data = np.array([
        [r.pkt_mean_to_max, r.tcp_flag_density, r.log_pkt_mean, r.log_pkt_max]
        for r in records
    ], dtype=np.float32)

    # 1. Model inference
    probabilities = model.predict(X_data)

    # 2. Per-request SHAP computation
    raw_shap = explainer.shap_values(X_data)
    if isinstance(raw_shap, list):
        raw_shap = raw_shap[1]

    results = []
    for i in range(len(records)):
        prob = float(probabilities[i])
        binary_pred = 1 if prob >= THRESHOLD else 0
        shap_dict = {
            feat_name: float(raw_shap[i, col_idx])
            for col_idx, feat_name in enumerate(FEATURE_NAMES)
        }
        results.append(PredictionItem(
            prediction=binary_pred,
            probability=round(prob, 6),
            threshold=THRESHOLD,
            shap_values=shap_dict
        ))

    return PredictionResponse(predictions=results)
