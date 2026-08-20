import os, json, time
from pathlib import Path
from typing import List, Dict, Union, Any, Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 1. Environment & Configuration Constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY_PATH = str(PROJECT_ROOT / "risk_agent/asset_inventory.json")

DETECTOR_API_URL = os.getenv("DETECTOR_API_URL", "http://localhost:8000/predict")
INVENTORY_PATH = os.getenv("INVENTORY_PATH", DEFAULT_INVENTORY_PATH)

# Formula Weights (Explainable methodology for research paper)
WEIGHT_PROBABILITY = float(os.getenv("WEIGHT_PROBABILITY", "0.60"))
WEIGHT_CRITICALITY = float(os.getenv("WEIGHT_CRITICALITY", "0.40"))
DEFAULT_CRITICALITY = 3  # Medium default if asset_id not found in inventory

asset_inventory: Dict[str, Dict[str, Any]] = {}

def load_asset_inventory() -> Dict[str, Dict[str, Any]]:
    """Loads synthetic asset inventory table from JSON file."""
    global asset_inventory
    inv_file = Path(INVENTORY_PATH)
    if not inv_file.exists():
        print(f"[!] Warning: Asset inventory file not found at {INVENTORY_PATH}. Using fallback defaults.")
        asset_inventory = {}
        return asset_inventory

    with open(inv_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        asset_inventory = {item["asset_id"]: item for item in data}
    print(f"[+] Loaded {len(asset_inventory)} synthetic asset records from {INVENTORY_PATH}.")
    return asset_inventory

# Load inventory at module initialization
load_asset_inventory()

# 2. Pydantic Models
class FlowRecord(BaseModel):
    pkt_mean_to_max: float = Field(..., description="Ratio of mean packet length to max packet length [0,1]")
    tcp_flag_density: float = Field(..., description="TCP flag multiplicity count")
    log_pkt_mean: float = Field(..., description="Log-transformed mean packet length")
    log_pkt_max: float = Field(..., description="Log-transformed max packet length")

class RiskScoreRequest(BaseModel):
    flow_record: Optional[FlowRecord] = Field(None, description="Raw 4-tuple flow record for detector inference")
    detection_probability: Optional[float] = Field(None, description="Pre-computed detection probability in [0,1]")
    asset_id: str = Field(..., description="Asset identifier (e.g. SCADA-MTU-01)")
    asset_criticality_override: Optional[int] = Field(None, ge=1, le=5, description="Optional criticality override [1-5]")

    model_config = {
        "json_schema_extra": {
            "example": {
                "asset_id": "SCADA-MTU-01",
                "flow_record": {
                    "pkt_mean_to_max": 0.95,
                    "tcp_flag_density": 1.0,
                    "log_pkt_mean": 4.2,
                    "log_pkt_max": 4.3
                }
            }
        }
    }

class RiskScoreResponse(BaseModel):
    asset_id: str = Field(..., description="Target asset identifier")
    asset_name: str = Field(..., description="Target asset human-readable name")
    detection_probability: float = Field(..., description="Detection probability P in [0,1]")
    asset_criticality: int = Field(..., description="Asset criticality C in [1,5]")
    risk_score: float = Field(..., description="Calculated 0-100 explainable Risk Score")
    risk_tier: str = Field(..., description="Risk tier: Low / Medium / High / Critical")
    formula_explanation: str = Field(..., description="Step-by-step mathematical calculation formula for paper methodology")

class TriageResponse(BaseModel):
    total_alerts: int = Field(..., description="Total number of alert records triaged")
    sorted_alerts: List[RiskScoreResponse] = Field(..., description="Alerts sorted by risk_score descending")

# 3. Explainable Risk Formula Function
def calculate_risk(probability: float, criticality: int) -> tuple:
    """
    Computes explainable Risk Score = (w_p * P + w_c * (C / 5.0)) * 100.
    Returns (risk_score, risk_tier, formula_explanation).
    """
    c_norm = criticality / 5.0
    score = (WEIGHT_PROBABILITY * probability + WEIGHT_CRITICALITY * c_norm) * 100.0
    score = round(score, 2)

    if score >= 80.0:
        tier = "Critical"
    elif score >= 60.0:
        tier = "High"
    elif score >= 40.0:
        tier = "Medium"
    else:
        tier = "Low"

    explanation = (
        f"Risk Score = ({WEIGHT_PROBABILITY:.2f} * {probability:.4f} + "
        f"{WEIGHT_CRITICALITY:.2f} * ({criticality}/5.0)) * 100 = {score:.2f} [{tier}]"
    )
    return score, tier, explanation

# 4. FastAPI Service
app = FastAPI(
    title="ARGUS Risk Prediction & Triage Agent",
    description="FastAPI agent converting high-recall SCADA detections into triaged, ranked 0-100 risk scores.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """Health check endpoint for Risk Prediction agent."""
    return {
        "status": "healthy",
        "detector_api_url": DETECTOR_API_URL,
        "asset_inventory_count": len(asset_inventory),
        "inventory_path": INVENTORY_PATH,
        "formula": f"Risk Score = ({WEIGHT_PROBABILITY:.2f} * P + {WEIGHT_CRITICALITY:.2f} * (C / 5.0)) * 100",
        "synthetic_notice": "Asset inventory table is synthetic and intended for SCADA demo & triage evaluation."
    }

def get_asset_info(asset_id: str, override_crit: Optional[int] = None) -> tuple:
    """Retrieves asset name and criticality score from inventory."""
    if asset_id in asset_inventory:
        info = asset_inventory[asset_id]
        name = info.get("asset_name", asset_id)
        crit = info.get("criticality", DEFAULT_CRITICALITY)
    else:
        name = f"Unknown Asset ({asset_id})"
        crit = DEFAULT_CRITICALITY

    if override_crit is not None:
        crit = override_crit

    return name, crit

def resolve_probability(req: RiskScoreRequest) -> float:
    """Resolves detection probability from pre-computed value or Detector API call."""
    if req.detection_probability is not None:
        return float(req.detection_probability)

    if req.flow_record is None:
        raise HTTPException(
            status_code=400,
            detail="Must provide either 'detection_probability' or 'flow_record' for inference."
        )

    # Call Detector API (POST http://localhost:8000/predict)
    detector_payload = [req.flow_record.model_dump()]
    try:
        response = requests.post(DETECTOR_API_URL, json=detector_payload, timeout=5.0)
        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Detector API returned error {response.status_code}: {response.text}"
            )
        data = response.json()
        predictions = data.get("predictions", [])
        if not predictions:
            raise HTTPException(status_code=500, detail="Detector API returned empty predictions.")
        return float(predictions[0]["probability"])
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=53,
            detail=f"Failed to connect to Detector API at {DETECTOR_API_URL}: {str(e)}"
        )

@app.post("/risk_score", response_model=RiskScoreResponse)
def compute_risk_score(req: RiskScoreRequest):
    """
    POST /risk_score endpoint.
    Accepts flow record + asset_id (or detection_probability + asset_id).
    Returns detection_probability, asset_criticality, 0-100 risk_score, and risk_tier.
    """
    prob = resolve_probability(req)
    name, crit = get_asset_info(req.asset_id, req.asset_criticality_override)
    score, tier, explanation = calculate_risk(prob, crit)

    return RiskScoreResponse(
        asset_id=req.asset_id,
        asset_name=name,
        detection_probability=prob,
        asset_criticality=crit,
        risk_score=score,
        risk_tier=tier,
        formula_explanation=explanation
    )

@app.post("/triage", response_model=TriageResponse)
def triage_batch(requests_list: List[RiskScoreRequest]):
    """
    POST /triage endpoint.
    Accepts a list of alert requests, computes risk scores for all items,
    and returns them sorted by risk_score descending (highest risk score first).
    """
    if not requests_list:
        raise HTTPException(status_code=400, detail="No alert requests provided for triage.")

    # Batch resolution if flow_records are provided
    flow_records_to_query = []
    query_indices = []

    for i, req in enumerate(requests_list):
        if req.detection_probability is None and req.flow_record is not None:
            flow_records_to_query.append(req.flow_record.model_dump())
            query_indices.append(i)

    # Batch query detector API if needed
    batch_probs = {}
    if flow_records_to_query:
        try:
            resp = requests.post(DETECTOR_API_URL, json=flow_records_to_query, timeout=5.0)
            if resp.status_code == 200:
                preds = resp.json().get("predictions", [])
                for idx_in_query, original_idx in enumerate(query_indices):
                    batch_probs[original_idx] = float(preds[idx_in_query]["probability"])
        except Exception as e:
            print(f"[!] Batch detector query warning: {e}")

    responses = []
    for i, req in enumerate(requests_list):
        if req.detection_probability is not None:
            prob = float(req.detection_probability)
        elif i in batch_probs:
            prob = batch_probs[i]
        else:
            prob = resolve_probability(req)

        name, crit = get_asset_info(req.asset_id, req.asset_criticality_override)
        score, tier, explanation = calculate_risk(prob, crit)

        responses.append(RiskScoreResponse(
            asset_id=req.asset_id,
            asset_name=name,
            detection_probability=prob,
            asset_criticality=crit,
            risk_score=score,
            risk_tier=tier,
            formula_explanation=explanation
        ))

    # Triage function: Sort by risk_score descending
    sorted_responses = sorted(responses, key=lambda x: x.risk_score, reverse=True)

    return TriageResponse(
        total_alerts=len(sorted_responses),
        sorted_alerts=sorted_responses
    )
