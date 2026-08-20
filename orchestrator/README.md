# ARGUS Pipeline Orchestrator

Minimal, deterministic pipeline orchestrator microservice for the **ARGUS project**. It coordinates Threat Detection, Risk Prediction, MITRE ATT&CK for ICS Knowledge Retrieval, and LLM Decision Support into a single structured alert output.

---

## 🔬 Architectural Trade-Off Analysis: LangGraph vs. Plain Python State Machine

For paper methodology justification, we evaluated two architectural paradigms:

### Option A: LangGraph Framework
- **Pros**: Graph-based node execution, built-in state persistence, conditional branching abstractions.
- **Cons**: Adds heavy framework dependencies, introduces non-trivial abstraction overhead (~15–30ms per turn), and complicates deterministic microsecond-level stage latency profiling.

### Option B: Plain Python Deterministic State Machine (CHOSEN)
- **Pros**: Zero external framework dependencies, lightweight, deterministic execution flow. Guarantees exact, uncorrupted microsecond-level stage latency logging (`detector_ms`, `risk_ms`, `knowledge_ms`, `llm_ms`, `total_pipeline_ms`) required for academic paper performance tables.
- **Cons**: Requires explicit handling of service HTTP requests and partial fallbacks in Python.

> 📝 **Terminology Alignment**:
> In accordance with the ARGUS system architecture paper claims, this orchestrator is formally specified as a **Fixed Sequential Pipeline (Deterministic State Machine)**, **NOT** a general multi-agent negotiation framework.

---

## ⚡ Key Pipeline Design Decisions

1. **Short-Circuit Execution on Benign Telemetry**:
   - If Stage 1 (Threat Analysis) returns `prediction == 0` (Benign SCADA Telemetry at $\theta=0.50$), the orchestrator **immediately short-circuits the pipeline**, skipping Risk Prediction, Knowledge Retrieval, and LLM explanation.
   - *Rationale*: In high-throughput industrial control systems (ICS), processing benign traffic through LLM/RAG stages introduces unnecessary computational overhead.

2. **Grounding Knowledge Retrieval into LLM Decision Support**:
   - When an attack is flagged (`prediction == 1`), Stage 3 retrieves top-3 grounded MITRE ATT&CK for ICS technique references (e.g. `T0855: Unauthorized Command Message`, `T0869: Standard Application Layer Protocol`) and injects them directly into Stage 4 (Decision Support), ensuring explanations are grounded in official ICS threat taxonomy rather than generic language.

3. **Fault Tolerance & Partial Failure Handling**:
   - If any downstream stage fails (e.g., local Ollama service offline), the pipeline captures the stage error in `stage_errors` and returns partial results without crashing the pipeline.

---

## 📌 Endpoints

### 1. `GET /health`
Returns connectivity status of all 4 downstream microservices.

### 2. `POST /process_alert`
Runs the complete sequential pipeline and returns a unified JSON alert object.

**Example Request**:
```bash
curl -X POST "http://localhost:8004/process_alert" \
     -H "Content-Type: application/json" \
     -d '{
       "asset_id": "SCADA-MTU-01",
       "flow_record": {
         "pkt_mean_to_max": 0.95,
         "tcp_flag_density": 1.0,
         "log_pkt_mean": 4.2,
         "log_pkt_max": 4.3
       }
     }'
```

**Example Response**:
```json
{
  "asset_id": "SCADA-MTU-01",
  "short_circuited": false,
  "short_circuit_reason": "Attack detected (prediction=1). Full multi-stage pipeline executed.",
  "detector_output": {
    "prediction": 1,
    "probability": 0.569761,
    "threshold": 0.50,
    "shap_values": { "pkt_mean_to_max": 0.297223, "tcp_flag_density": -1.637493, "log_pkt_mean": -0.828386, "log_pkt_max": 0.584339 }
  },
  "risk_output": {
    "asset_id": "SCADA-MTU-01",
    "risk_score": 74.19,
    "risk_tier": "High",
    "formula_explanation": "Risk Score = (0.60 * 0.5698 + 0.40 * (5/5.0)) * 100 = 74.19 [High]"
  },
  "knowledge_output": {
    "query": "SCADA cyberattack anomaly on SCADA-MTU-01...",
    "techniques": [
      { "technique_id": "T0866", "name": "Exploitation of Remote Services" },
      { "technique_id": "T1692.002", "name": "Reporting Message" },
      { "technique_id": "T0869", "name": "Standard Application Layer Protocol" }
    ]
  },
  "decision_output": {
    "prediction": 1,
    "probability": 0.569761,
    "explanation_text": "[ATTACK ALERT] Detector assigned a probability of 0.5698... [Grounded MITRE ATT&CK ICS References: T0866: Exploitation of Remote Services, T1692.002: Reporting Message, T0869: Standard Application Layer Protocol]"
  },
  "stage_latencies": {
    "detector_ms": 5.05,
    "risk_ms": 2.00,
    "knowledge_ms": 97.95,
    "llm_ms": 8.41,
    "total_pipeline_ms": 113.49
  },
  "stage_errors": {}
}
```

---

## 🏃 Local Execution

```bash
# 1. Start all 4 microservices
PYTHONPATH=. uvicorn api.main:app --port 8000 &
PYTHONPATH=. uvicorn agent.main:app --port 8001 &
PYTHONPATH=. uvicorn risk_agent.main:app --port 8002 &
PYTHONPATH=. uvicorn knowledge_agent.main:app --port 8003 &

# 2. Run Pipeline Orchestrator on Port 8004
PYTHONPATH=. uvicorn orchestrator.main:app --host 0.0.0.0 --port 8004

# 3. Run Pipeline Test Suite
PYTHONPATH=. .venv/bin/python orchestrator/test_orchestrator.py
```
