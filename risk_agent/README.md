# ARGUS Risk Prediction & Triage Agent

FastAPI Decision Support microservice for the **ARGUS project** that converts raw high-recall SCADA intrusion detections ($\theta=0.50$, $96\%$ recall, $87\%$ FPR) into triaged, ranked 0–100 Risk Scores.

> ⚠️ **SYNTHETIC ASSET INVENTORY NOTICE**:
> Real asset inventory data from operational SCADA facilities is proprietary. A small synthetic asset inventory table (`asset_inventory.json`) with criticality scores from 1 (Low) to 5 (Critical) is provided for demonstration, paper methodology validation, and alert triage benchmarking purposes.

---

## 📐 Explainable Risk Score Methodology

To avoid adding another opaque black-box machine learning model, ARGUS uses a **transparent, deterministic, explainable weighted risk formula** that can be directly justified in a research methodology section:

$$\text{Risk Score} = \left( w_p \cdot P + w_c \cdot \frac{C}{5.0} \right) \times 100$$

Where:
- **$P \in [0.0, 1.0]$**: Continuous attack detection probability from Detector API.
- **$C \in [1, 5]$**: Asset criticality score from SCADA asset inventory.
- **$w_p = 0.60$**: Probability Weight.
- **$w_c = 0.40$**: Asset Criticality Weight.

### Risk Tier Classification
- 🚨 **Critical**: $\text{Risk Score} \ge 80.0$
- 🟠 **High**: $60.0 \le \text{Risk Score} < 80.0$
- 🟡 **Medium**: $40.0 \le \text{Risk Score} < 60.0$
- 🟢 **Low**: $\text{Risk Score} < 40.0$

---

## 📌 Endpoints

### 1. `GET /health`
Returns service status, formula definition, and loaded asset count.

### 2. `POST /risk_score`
Calculates Risk Score and Tier for a single flow record and asset ID.

**Example Request**:
```bash
curl -X POST "http://localhost:8002/risk_score" \
     -H "Content-Type: application/json" \
     -d '{
       "asset_id": "SCADA-MTU-01",
       "detection_probability": 0.85
     }'
```

**Example Response**:
```json
{
  "asset_id": "SCADA-MTU-01",
  "asset_name": "Main Master Terminal Unit (Control Center)",
  "detection_probability": 0.85,
  "asset_criticality": 5,
  "risk_score": 91.0,
  "risk_tier": "Critical",
  "formula_explanation": "Risk Score = (0.60 * 0.8500 + 0.40 * (5/5.0)) * 100 = 91.00 [Critical]"
}
```

### 3. `POST /triage`
Batch triage endpoint. Accepts a list of alert requests and returns them **sorted by `risk_score` descending** (highest risk first).

**Example Request**:
```bash
curl -X POST "http://localhost:8002/triage" \
     -H "Content-Type: application/json" \
     -d '[
       {"asset_id": "SENSOR-NODE-88", "detection_probability": 0.20},
       {"asset_id": "SCADA-MTU-01", "detection_probability": 0.90},
       {"asset_id": "SENSOR-NODE-88", "detection_probability": 0.90},
       {"asset_id": "SCADA-MTU-01", "detection_probability": 0.20}
     ]'
```

**Example Response (Sorted Descending)**:
```json
{
  "total_alerts": 4,
  "sorted_alerts": [
    { "asset_id": "SCADA-MTU-01", "detection_probability": 0.90, "asset_criticality": 5, "risk_score": 94.0, "risk_tier": "Critical" },
    { "asset_id": "SENSOR-NODE-88", "detection_probability": 0.90, "asset_criticality": 1, "risk_score": 62.0, "risk_tier": "High" },
    { "asset_id": "SCADA-MTU-01", "detection_probability": 0.20, "asset_criticality": 5, "risk_score": 52.0, "risk_tier": "Medium" },
    { "asset_id": "SENSOR-NODE-88", "detection_probability": 0.20, "asset_criticality": 1, "risk_score": 20.0, "risk_tier": "Low" }
  ]
}
```

---

## 🏃 Local Execution

```bash
# 1. Run Risk Agent service on Port 8002
PYTHONPATH=. uvicorn risk_agent.main:app --host 0.0.0.0 --port 8002

# 2. Run Unit Test Suite
PYTHONPATH=. .venv/bin/python risk_agent/test_risk_agent.py
```

---

## 🐳 Docker Support

```bash
# Build Docker image
docker build -t argus-risk-agent -f risk_agent/Dockerfile .

# Run Container
docker run -d -p 8002:8002 --name argus-risk-agent \
  -e DETECTOR_API_URL=http://detector-api:8000/predict \
  argus-risk-agent
```
