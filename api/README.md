# ARGUS Cross-Domain Intrusion Detection API

A lightweight FastAPI service wrapping the trained cross-domain intrusion detection model for the **ARGUS project** (targeting the IEC 60870-5-104 SCADA domain).

---

## 🚀 Features

- **Startup Model Loading**: Loads trained LightGBM model and `shap.TreeExplainer` once during application startup (via lifespan context manager).
- **Target Domain Calibration**: Calibrated decision threshold at $\theta = 0.50$.
- **Per-Request SHAP Explanation**: Returns exact feature contribution scores (`shap_values`) alongside detection probability.
- **Strict 4-Feature Schema**: Expects inputs in exact order: `pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`.
- **Zero Cloud Dependencies**: Fully local execution.

---

## 📌 Endpoints

### 1. `GET /health`
Returns service health, model status, path, and target domain metadata.

**Example Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "/Users/tirthkosambia/Documents/ARGUS/phase3_results/models/model_d2_coral.txt",
  "target_domain": "IEC 60870-5-104 (SCADA)",
  "threshold": 0.50,
  "features": [
    "pkt_mean_to_max",
    "tcp_flag_density",
    "log_pkt_mean",
    "log_pkt_max"
  ]
}
```

### 2. `POST /predict`
Accepts a JSON array of flow records (or a single flow record object). Returns detection probability, binary prediction at $\theta=0.50$, and per-feature SHAP values.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '[
       {
         "pkt_mean_to_max": 0.95,
         "tcp_flag_density": 1.0,
         "log_pkt_mean": 4.2,
         "log_pkt_max": 4.3
       }
     ]'
```

**Example Response**:
```json
{
  "predictions": [
    {
      "prediction": 1,
      "probability": 0.569761,
      "threshold": 0.50,
      "shap_values": {
        "pkt_mean_to_max": 0.297223,
        "tcp_flag_density": -1.637493,
        "log_pkt_mean": -0.828386,
        "log_pkt_max": 0.584339
      }
    }
  ]
}
```

---

## 🛠️ Local Running

```bash
# 1. Install dependencies
pip install -r api/requirements.txt

# 2. Run with uvicorn from repository root
PYTHONPATH=. uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🐳 Docker Support

```bash
# Build Docker image
docker build -t argus-detector-api -f api/Dockerfile .

# Run container
docker run -d -p 8000:8000 --name argus-api argus-detector-api
```
