# ARGUS Decision Support & Explainability Agent

FastAPI Decision Support AI Agent for the **ARGUS project**. It interfaces with the local Detector API (`POST http://localhost:8000/predict`) and a local Ollama LLM instance (`http://localhost:11434`, default model: `llama3.2`) to translate SHAP values into human-readable operational explanations for SCADA security analysts.

---

## 🚀 Features

- **System Prompt File Isolation**: System prompt loaded from `prompts/decision_support_system_prompt.txt` (never hardcoded in Python).
- **Separate Latency Logging**: Records `detector_ms`, `llm_ms`, and `total_ms` for research paper computational efficiency tables.
- **Local Ollama Integration**: Connects to `http://localhost:11434/api/generate` with zero cloud calls.
- **Graceful Offline Fallback**: If Ollama is offline or not running, returns structured fallback explanations so API calls never break.
- **Microservice Architecture**: Exposes `POST /explain` on port 8001.

---

## 📌 Endpoints

### 1. `GET /health`
Returns service status, prompt file state, and configured URLs.

**Example Response**:
```json
{
  "status": "healthy",
  "detector_api_url": "http://localhost:8000/predict",
  "ollama_api_url": "http://localhost:11434",
  "ollama_model": "llama3.2",
  "system_prompt_loaded": true,
  "prompt_path": "/Users/tirthkosambia/Documents/ARGUS/prompts/decision_support_system_prompt.txt"
}
```

### 2. `POST /explain`
Accepts flow record(s), queries Detector API for predictions/SHAP values, queries local Ollama LLM for explanation, and logs latency breakdown.

**Example Request**:
```bash
curl -X POST "http://localhost:8001/explain" \
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
  "explanations": [
    {
      "prediction": 1,
      "probability": 0.569761,
      "threshold": 0.50,
      "shap_values": {
        "pkt_mean_to_max": 0.297223,
        "tcp_flag_density": -1.637493,
        "log_pkt_mean": -0.828386,
        "log_pkt_max": 0.584339
      },
      "explanation_text": "[ATTACK ALERT] Cyberattack detected with 56.98% probability. The primary feature driving the decision is 'pkt_mean_to_max' (+0.2972 SHAP score), indicating a high ratio of packet mean to max length typical of SCADA polling flood anomalies.",
      "latency_ms": {
        "detector_ms": 8.19,
        "llm_ms": 450.60,
        "total_ms": 458.79
      }
    }
  ]
}
```

---

## 🏃 Local Execution

```bash
# 1. Run Detector API (Port 8000)
PYTHONPATH=. uvicorn api.main:app --host 0.0.0.0 --port 8000

# 2. Ensure Ollama is running locally (Port 11434)
ollama run llama3.2

# 3. Run Decision Support Agent (Port 8001)
PYTHONPATH=. uvicorn agent.main:app --host 0.0.0.0 --port 8001
```

---

## 🐳 Docker Deployment

```bash
# Build Docker image for Agent
docker build -t argus-decision-agent -f agent/Dockerfile .

# Run Container
docker run -d -p 8001:8001 --name argus-agent \
  -e DETECTOR_API_URL=http://detector-api:8000/predict \
  -e OLLAMA_API_URL=http://host.docker.internal:11434 \
  -e OLLAMA_MODEL=llama3.2 \
  argus-decision-agent
```
