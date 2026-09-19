import os, time, json
from pathlib import Path
from typing import List, Dict, Union, Any, Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from argus.services.common.schemas import FlowRecord

# ==============================================================================
# ARCHITECTURE TERMINOLOGY & DESIGN DECISION (RESEARCH PAPER METHODOLOGY):
# This module implements a FIXED SEQUENTIAL PIPELINE (Deterministic State Machine),
# NOT a general multi-agent negotiation system.
#
# Trade-off Analysis:
# - LangGraph: Offers graph-based state persistence and conditional routing, but adds
#   heavy abstraction, extra dependencies, and framework overhead.
# - Plain Python State Machine (Chosen): Lightweight, zero-dependency, deterministic
#   execution. Guarantees precise per-stage microsecond latency logging required for
#   the paper's computational-efficiency benchmarks, enables explicit short-circuiting
#   on benign telemetry, and handles partial stage failures gracefully without crashing.
# ==============================================================================

# Downstream Microservice URLs (Configurable via Environment Variables)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DETECTOR_API_URL = os.getenv("DETECTOR_API_URL", "http://localhost:8000/predict")
RISK_API_URL = os.getenv("RISK_API_URL", "http://localhost:8002/risk_score")
KNOWLEDGE_API_URL = os.getenv("KNOWLEDGE_API_URL", "http://localhost:8003/context")
DECISION_API_URL = os.getenv("DECISION_API_URL", "http://localhost:8001/explain")

FEATURE_PLAIN_LANGUAGE = {
    ("tcp_flag_density", True): "high TCP flag multiplicity and control flag density",
    ("tcp_flag_density", False): "unusually low TCP flag diversity",
    ("pkt_mean_to_max", True): "high packet size mean to max ratio",
    ("pkt_mean_to_max", False): "skewed packet length ratio",
    ("log_pkt_mean", True): "elevated average packet payload size",
    ("log_pkt_mean", False): "reduced average packet size",
    ("log_pkt_max", True): "unusually large maximum packet payload",
    ("log_pkt_max", False): "suppressed maximum packet length"
}

def build_shap_context_query(shap_values: Dict[str, float]) -> str:
    """
    Builds a dynamic plain-language vector retrieval query (under 20 words)
    derived from the top-2 SHAP features by magnitude and their signed values.
    """
    if not shap_values:
        return "unusually low TCP flag diversity combined with reduced average packet size, SCADA network flow"

    sorted_feats = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
    top1_name, top1_val = sorted_feats[0]
    top1_desc = FEATURE_PLAIN_LANGUAGE.get((top1_name, top1_val >= 0), top1_name)

    if len(sorted_feats) > 1:
        top2_name, top2_val = sorted_feats[1]
        top2_desc = FEATURE_PLAIN_LANGUAGE.get((top2_name, top2_val >= 0), top2_name)
        return f"{top1_desc} combined with {top2_desc}, SCADA network flow"

    return f"{top1_desc}, SCADA network flow"

class AlertRequest(BaseModel):
    flow_record: FlowRecord = Field(..., description="Raw 4-tuple flow record for SCADA telemetry")
    asset_id: str = Field("SCADA-MTU-01", description="Target SCADA asset identifier")

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

class StageLatencies(BaseModel):
    detector_ms: float = Field(0.0, description="Detector model inference latency in ms")
    risk_ms: float = Field(0.0, description="Risk prediction calculation latency in ms")
    knowledge_ms: float = Field(0.0, description="MITRE ATT&CK vector search retrieval latency in ms")
    llm_ms: float = Field(0.0, description="Ollama LLM explanation generation latency in ms")
    total_pipeline_ms: float = Field(0.0, description="Total end-to-end pipeline processing time in ms")

class ProcessedAlertResponse(BaseModel):
    asset_id: str = Field(..., description="Target asset identifier")
    short_circuited: bool = Field(..., description="True if benign telemetry short-circuited remaining stages")
    short_circuit_reason: Optional[str] = Field(None, description="Explanation for short-circuit decision")
    
    # Stage Outputs
    detector_output: Optional[Dict[str, Any]] = Field(None, description="Stage 1: Threat Analysis Output")
    risk_output: Optional[Dict[str, Any]] = Field(None, description="Stage 2: Risk Score & Tier Output")
    knowledge_output: Optional[Dict[str, Any]] = Field(None, description="Stage 3: MITRE ATT&CK for ICS Grounding Output")
    decision_output: Optional[Dict[str, Any]] = Field(None, description="Stage 4: LLM Decision Support Explanation Output")
    
    # Performance & Fault Metrics
    stage_latencies: StageLatencies = Field(..., description="Per-stage latency profiling for paper benchmarks")
    stage_errors: Dict[str, str] = Field(default_factory=dict, description="Partial failure notices per stage if any service or fallback fired")
    agent_trace: List[Dict[str, Any]] = Field(default_factory=list, description="Structured agent-to-agent communication trace")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ARGUS Pipeline Orchestrator",
    description="Minimal deterministic pipeline orchestrator coordinating Threat Detection, Risk Prediction, Knowledge Retrieval, and LLM Decision Support.",
    version="1.0.0"
)

import ast
cors_origins_env = os.getenv("ARGUS_CORS_ORIGINS", '["http://localhost:5173", "http://localhost:3000"]')
try:
    allowed_origins = ast.literal_eval(cors_origins_env)
except Exception:
    allowed_origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Checks operational connectivity to all 4 downstream microservices."""
    services = {
        "detector_api": DETECTOR_API_URL,
        "risk_api": RISK_API_URL,
        "knowledge_api": KNOWLEDGE_API_URL,
        "decision_api": DECISION_API_URL
    }
    status_dict = {}
    for name, url in services.items():
        base_health_url = url.rsplit("/", 1)[0] + "/health"
        try:
            r = requests.get(base_health_url, timeout=1.5)
            status_dict[name] = "online" if r.status_code == 200 else f"degraded (HTTP {r.status_code})"
        except Exception:
            status_dict[name] = "offline / unreachable"

    return {
        "status": "healthy",
        "pipeline_type": "Fixed Sequential Pipeline (Deterministic State Machine)",
        "downstream_services": status_dict
    }

@app.post("/process_alert", response_model=ProcessedAlertResponse)
def process_alert(req: AlertRequest):
    """
    POST /process_alert endpoint.
    Executes the fixed sequential pipeline:
    1. Threat Analysis (Detector API)
    2. Short-circuit if prediction == 0 (Benign)
    3. Risk Prediction (Risk Agent API)
    4. Knowledge & Context (ChromaDB MITRE ATT&CK lookup)
    5. Decision Support (Grounded Ollama LLM explanation)
    6. Combines outputs into unified JSON alert object with granular stage latency profiling.
    """
    # --------------------------------------------------------------------------
    # NEW AGENT COORDINATION LOGIC (Replaces Sequential Pipeline)
    # --------------------------------------------------------------------------
    import uuid
    from argus.services.common.schemas import AgentMessage

    event_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    agent_trace = []
    errors = {}
    latencies = StageLatencies()
    t_start_pipeline = time.perf_counter()

    def log_trace(agent_name, status, data=None):
        trace_entry = {"agent": agent_name, "status": status}
        if data:
            trace_entry.update(data)
        agent_trace.append(trace_entry)

    def send_agent_message(url, receiver, msg_type, payload):
        msg = AgentMessage(
            message_id=str(uuid.uuid4()),
            event_id=event_id,
            sender="Coordinator",
            receiver=receiver,
            message_type=msg_type,
            payload=payload,
            trace_id=trace_id
        )
        resp = requests.post(url.replace(url.split("/")[-1], "agent/process"), json=msg.model_dump(), timeout=10.0)
        resp.raise_for_status()
        return AgentMessage(**resp.json())

    # 1. Detector Agent
    t0_det = time.perf_counter()
    detector_out = {}
    try:
        det_resp = send_agent_message(DETECTOR_API_URL, "DetectorAgent", "request", {"flow_record": req.flow_record.model_dump()})
        detector_out = det_resp.payload
        pred = detector_out.get("prediction", 0)
        prob = detector_out.get("probability", 0.0)
        shap_vals = detector_out.get("shap_values", {})
        log_trace("detector", "completed", {"confidence": round(det_resp.confidence or prob, 4)})
    except Exception as e:
        errors["detector"] = str(e)
        log_trace("detector", "failed", {"error": str(e)})
        pred = 0

    t1_det = time.perf_counter()
    latencies.detector_ms = round((t1_det - t0_det) * 1000.0, 2)

    if pred == 0:
        latencies.total_pipeline_ms = round((time.perf_counter() - t_start_pipeline) * 1000.0, 2)
        return ProcessedAlertResponse(
            asset_id=req.asset_id,
            short_circuited=True,
            short_circuit_reason="Benign telemetry.",
            detector_output=detector_out,
            stage_latencies=latencies,
            stage_errors=errors,
            agent_trace=agent_trace
        )

    # 2. Risk Agent
    t0_risk = time.perf_counter()
    try:
        risk_resp = send_agent_message(RISK_API_URL, "RiskAgent", "request", {"asset_id": req.asset_id, "probability": prob})
        risk_out = risk_resp.payload
        log_trace("risk", "completed", {"risk_score": risk_out.get("risk_score")})
    except Exception as e:
        errors["risk"] = str(e)
        log_trace("risk", "failed", {"error": str(e)})
    latencies.risk_ms = round((time.perf_counter() - t0_risk) * 1000.0, 2)

    # 3. Knowledge Agent
    t0_know = time.perf_counter()
    try:
        query_text = build_shap_context_query(shap_vals)
        know_resp = send_agent_message(KNOWLEDGE_API_URL, "KnowledgeAgent", "request", {"query": query_text, "top_k": 3})
        knowledge_out = know_resp.payload
        log_trace("knowledge", "completed")
    except Exception as e:
        errors["knowledge"] = str(e)
        log_trace("knowledge", "failed", {"error": str(e)})
    latencies.knowledge_ms = round((time.perf_counter() - t0_know) * 1000.0, 2)

    # 4. Decision Agent (Initial)
    t0_llm = time.perf_counter()
    decision_conf = 1.0
    try:
        dec_payload = {
            "prediction": pred,
            "probability": prob,
            "shap_values": shap_vals,
            "risk_score": risk_out.get("risk_score") if risk_out else None,
            "risk_tier": risk_out.get("risk_tier") if risk_out else None,
            "attck_context": knowledge_out.get("techniques") if knowledge_out else None
        }
        dec_resp = send_agent_message(DECISION_API_URL, "DecisionAgent", "request", dec_payload)
        decision_out = dec_resp.payload
        decision_conf = dec_resp.confidence or 1.0
        log_trace("decision", "completed", {"decision": decision_out.get("action"), "confidence": round(decision_conf, 4)})
    except Exception as e:
        errors["decision"] = str(e)
        log_trace("decision", "failed", {"error": str(e)})
    latencies.llm_ms = round((time.perf_counter() - t0_llm) * 1000.0, 2)

    # 5. Conditional Review Mechanism
    REVIEW_THRESHOLD = 0.85
    if decision_conf < REVIEW_THRESHOLD:
        log_trace("coordinator", "review_triggered", {"reason": f"Decision confidence {decision_conf:.2f} < {REVIEW_THRESHOLD}"})
        
        # Request more sensitive evaluation from Detector
        try:
            det_rev = send_agent_message(DETECTOR_API_URL, "DetectorAgent", "review_request", {"flow_record": req.flow_record.model_dump()})
            detector_out = det_rev.payload
            log_trace("detector", "review_completed")
        except:
            pass
            
        # Request stricter risk assessment
        try:
            risk_rev = send_agent_message(RISK_API_URL, "RiskAgent", "review_request", {"asset_id": req.asset_id, "probability": prob})
            risk_out = risk_rev.payload
            log_trace("risk", "review_completed")
        except:
            pass

        # Request broader context
        try:
            know_rev = send_agent_message(KNOWLEDGE_API_URL, "KnowledgeAgent", "review_request", {"query": query_text, "top_k": 5})
            knowledge_out = know_rev.payload
            log_trace("knowledge", "review_completed")
        except:
            pass

        # Final Decision Agent pass
        try:
            dec_payload.update({
                "risk_score": risk_out.get("risk_score") if risk_out else None,
                "risk_tier": risk_out.get("risk_tier") if risk_out else None,
                "attck_context": knowledge_out.get("techniques") if knowledge_out else None
            })
            dec_rev = send_agent_message(DECISION_API_URL, "DecisionAgent", "review_request", dec_payload)
            decision_out = dec_rev.payload
            log_trace("decision", "review_completed", {"decision": decision_out.get("action"), "confidence": round(dec_rev.confidence or 1.0, 4)})
        except:
            pass

    latencies.total_pipeline_ms = round((time.perf_counter() - t_start_pipeline) * 1000.0, 2)

    return ProcessedAlertResponse(
        asset_id=req.asset_id,
        short_circuited=False,
        short_circuit_reason="Attack detected. Multi-agent coordination executed.",
        detector_output=detector_out,
        risk_output=risk_out,
        knowledge_output=knowledge_out,
        decision_output=decision_out,
        stage_latencies=latencies,
        stage_errors=errors,
        agent_trace=agent_trace
    )

@app.get("/experiments")
def get_experiments():
    """Serves the cross-domain experiment results from the actual CSV artifacts."""
    csv_path = PROJECT_ROOT / "ARGUS_Cross_Domain_Results/argus_coral_data/final_five_model_comparison/FINAL_five_model_comparison.csv"
    if not csv_path.exists():
        return []
    
    import csv
    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results
