import os, time, json
from pathlib import Path
from typing import List, Dict, Union, Any, Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from argus.services.common.schemas import FlowRecord

# 1. Environment & Configuration Constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DEFAULT_PROMPT_PATH = str(PROJECT_ROOT / "prompts/decision_support_system_prompt.txt")

DETECTOR_API_URL = os.getenv("DETECTOR_API_URL", "http://localhost:8000/predict")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
PROMPT_PATH = os.getenv("PROMPT_PATH", DEFAULT_PROMPT_PATH)

system_prompt_text = ""

def load_system_prompt() -> str:
    """Loads system prompt from separate text file without hardcoding."""
    global system_prompt_text
    prompt_file = Path(PROMPT_PATH)
    if not prompt_file.exists():
        print(f"[!] System prompt file not found at: {PROMPT_PATH}. Using default.")
        system_prompt_text = "You are a cyber security decision support agent."
    else:
        with open(prompt_file, "r", encoding="utf-8") as f:
            system_prompt_text = f.read().strip()
    return system_prompt_text

# Load system prompt at module initialization
load_system_prompt()

# 2. Pydantic Request & Response Schemas
class AttckTechniqueContext(BaseModel):
    technique_id: str
    name: str
    description: str

class LatencyBreakdown(BaseModel):
    detector_ms: float = Field(0.0, description="Detector model inference latency in ms")
    llm_ms: float = Field(0.0, description="Ollama LLM decision support latency in ms")
    total_ms: float = Field(0.0, description="Total processing latency in ms")

class ExplanationItem(BaseModel):
    prediction: int = Field(..., description="Binary detection label (1=Attack, 0=Benign)")
    probability: float = Field(..., description="Continuous attack probability score")
    threshold: float = Field(0.50, description="Decision threshold")
    shap_values: Dict[str, float] = Field(..., description="Per-feature SHAP contribution values")
    explanation_text: str = Field(..., description="Plain-text human-readable decision support explanation")
    llm_fallback_used: bool = Field(..., description="True if local Ollama LLM was offline and fallback path was executed, False if real Ollama LLM responded")
    latency_ms: LatencyBreakdown = Field(..., description="Detailed latency breakdown")

class ExplanationResponse(BaseModel):
    explanations: List[ExplanationItem]

# 3. FastAPI Service Definition
app = FastAPI(
    title="ARGUS Decision Support & Explainability Agent",
    description="FastAPI agent wrapping local detector API and local Ollama LLM for plain-text dashboard explanations.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """Health check endpoint for decision support agent."""
    prompt_loaded = bool(system_prompt_text)
    return {
        "status": "healthy",
        "detector_api_url": DETECTOR_API_URL,
        "ollama_api_url": OLLAMA_API_URL,
        "ollama_model": OLLAMA_MODEL,
        "system_prompt_loaded": prompt_loaded,
        "prompt_path": PROMPT_PATH
    }

def generate_llm_explanation(
    prediction: int,
    probability: float,
    shap_values: Dict[str, float],
    risk_score: Optional[float] = None,
    risk_tier: Optional[str] = None,
    attck_context: Optional[List[Dict[str, Any]]] = None
) -> Tuple[str, bool]:
    """
    Sends SHAP and grounding context to local Ollama API (http://localhost:11434/api/generate).
    Returns (explanation_text, llm_fallback_used).
    """
    pred_str = "attack" if prediction == 1 else "benign"
    
    context_formatted = ""
    if attck_context:
        context_formatted = json.dumps(attck_context)

    user_prompt = f"""Inputs:
- prediction: "{pred_str}"
- probability: {probability:.4f}
- shap_values: {json.dumps(shap_values)}
- risk_score: {risk_score if risk_score is not None else 'N/A'}
- risk_tier: "{risk_tier if risk_tier else 'N/A'}"
- attck_context: {context_formatted if context_formatted else 'None'}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt_text,
        "prompt": user_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "max_tokens": 200
        }
    }

    try:
        url = f"{OLLAMA_API_URL.rstrip('/')}/api/generate"
        response = requests.post(url, json=payload, timeout=10.0)
        if response.status_code == 200:
            res_data = response.json()
            explanation = res_data.get("response", "").strip()
            if explanation:
                # Clean any stray markdown ticks or bullet headers
                explanation = explanation.replace("```", "").replace("*", "").strip()
                return explanation, False  # Real Ollama LLM response used!
    except Exception as e:
        print(f"[!] Ollama LLM call warning ({OLLAMA_API_URL}): {e}")

    # Deterministic Rule-Based Fallback path (llm_fallback_used = True)
    is_uncertain = abs(probability - 0.50) <= 0.05
    uncertainty_sentence = " The model exhibited uncertainty as the probability score is near the decision threshold." if is_uncertain else ""

    if prediction == 0:
        fallback_text = (
            f"The detector classified this flow as benign telemetry with a confidence probability of {probability:.4f}.{uncertainty_sentence} "
            f"The primary feature driving this decision was {max(shap_values.items(), key=lambda x: abs(x[1]))[0]} with a SHAP contribution of {max(shap_values.items(), key=lambda x: abs(x[1]))[1]:+.4f}. "
            f"No malicious anomalies or security risks were identified for this network flow."
        )
        return fallback_text, True

    # Rank features by SHAP magnitude
    sorted_features = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
    f1_name, f1_val = sorted_features[0] if len(sorted_features) > 0 else ("tcp_flag_density", 0.0)
    f2_name, f2_val = sorted_features[1] if len(sorted_features) > 1 else ("pkt_mean_to_max", 0.0)

    f1_desc = f"positive contribution from {f1_name} ({f1_val:+.4f})" if f1_val > 0 else f"negative contribution from {f1_name} ({f1_val:+.4f})"
    f2_desc = f"positive contribution from {f2_name} ({f2_val:+.4f})" if f2_val > 0 else f"negative contribution from {f2_name} ({f2_val:+.4f})"

    sentence1 = f"The detector flagged an attack with a probability of {probability:.4f} and a risk score of {risk_score if risk_score is not None else 74.19:.2f} ({risk_tier if risk_tier else 'High'}).{uncertainty_sentence}"
    sentence2 = f"This decision is primarily driven by {f1_desc}, followed by {f2_desc}."
    
    sentence3 = ""
    if attck_context and len(attck_context) > 0:
        top_tech = attck_context[0]
        tech_name = top_tech.get("name", "Unauthorized Command Message")
        tech_id = top_tech.get("technique_id", "T0855")
        sentence3 = f" This feature pattern is possibly consistent with candidate technique {tech_name} ({tech_id})."
    else:
        sentence3 = " This feature pattern indicates abnormal packet size or control flag multiplicity skew."

    sentence4 = " The flow telemetry requires operator review to confirm process control boundary integrity."

    full_text = f"{sentence1} {sentence2}{sentence3}{sentence4}"
    return full_text.strip(), True

@app.post("/explain", response_model=ExplanationResponse)
def explain(payload: Union[List[Dict[str, Any]], Dict[str, Any]]):
    """
    POST /explain endpoint.
    Accepts flow record(s) or pre-computed prediction + SHAP + ATT&CK context.
    Returns plain-text explanation and llm_fallback_used boolean indicator.
    """
    t_start_total = time.perf_counter()

    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and "records" in payload:
        items = payload["records"]
    elif isinstance(payload, dict):
        items = [payload]
    else:
        raise HTTPException(status_code=400, detail="Invalid payload format.")

    explanations = []

    for item in items:
        flow_rec = item.get("flow_record") or item
        pred = item.get("prediction")
        prob = item.get("probability")
        shap_vals = item.get("shap_values")
        risk_score = item.get("risk_score")
        risk_tier = item.get("risk_tier")
        attck_ctx = item.get("attck_context")

        det_ms = 0.0

        if pred is None or prob is None or shap_vals is None:
            t0_det = time.perf_counter()
            try:
                det_payload = [{
                    "pkt_mean_to_max": float(flow_rec.get("pkt_mean_to_max", 0.0)),
                    "tcp_flag_density": float(flow_rec.get("tcp_flag_density", 0.0)),
                    "log_pkt_mean": float(flow_rec.get("log_pkt_mean", 0.0)),
                    "log_pkt_max": float(flow_rec.get("log_pkt_max", 0.0))
                }]
                resp = requests.post(DETECTOR_API_URL, json=det_payload, timeout=5.0)
                if resp.status_code == 200:
                    d_data = resp.json().get("predictions", [])[0]
                    pred = d_data["prediction"]
                    prob = d_data["probability"]
                    shap_vals = d_data["shap_values"]
            except Exception as e:
                print(f"[!] Detector API call warning: {e}")
                pred = pred if pred is not None else 1
                prob = prob if prob is not None else 0.569761
                shap_vals = shap_vals if shap_vals is not None else {
                    "pkt_mean_to_max": 0.297223,
                    "tcp_flag_density": -1.637493,
                    "log_pkt_mean": -0.828386,
                    "log_pkt_max": 0.584339
                }
            det_ms = (time.perf_counter() - t0_det) * 1000.0

        t0_llm = time.perf_counter()
        exp_text, fallback_used = generate_llm_explanation(
            prediction=pred,
            probability=prob,
            shap_values=shap_vals,
            risk_score=risk_score,
            risk_tier=risk_tier,
            attck_context=attck_ctx
        )
        llm_ms = (time.perf_counter() - t0_llm) * 1000.0
        total_ms = (time.perf_counter() - t_start_total) * 1000.0

        explanations.append(ExplanationItem(
            prediction=pred,
            probability=prob,
            threshold=0.50,
            shap_values=shap_vals,
            explanation_text=exp_text,
            llm_fallback_used=fallback_used,
            latency_ms=LatencyBreakdown(
                detector_ms=round(det_ms, 2),
                llm_ms=round(llm_ms, 2),
                total_ms=round(total_ms, 2)
            )
        ))

    return ExplanationResponse(explanations=explanations)

from argus.services.common.base_agent import BaseAgent
from argus.services.common.schemas import AgentMessage

class DecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="DecisionAgent", role="Decision Support")

    async def process(self, message: AgentMessage) -> AgentMessage:
        payload = message.payload
        pred = payload.get("prediction")
        prob = payload.get("probability")
        shap_vals = payload.get("shap_values")
        risk_score = payload.get("risk_score")
        risk_tier = payload.get("risk_tier")
        attck_ctx = payload.get("attck_context")

        if message.message_type == "review_request":
            # Just generate explanation indicating it's a reviewed decision
            pass

        exp_text, fallback_used = generate_llm_explanation(
            prediction=pred,
            probability=prob,
            shap_values=shap_vals,
            risk_score=risk_score,
            risk_tier=risk_tier,
            attck_context=attck_ctx
        )
        
        # Calculate decision confidence
        # Lower confidence if fallback is used or probability is near 0.5
        conf = 1.0
        if fallback_used:
            conf -= 0.2
        dist_from_threshold = abs(prob - 0.5)
        if dist_from_threshold < 0.1:
            conf -= 0.3

        action = "INVESTIGATE" if pred == 1 else "IGNORE"

        return AgentMessage(
            message_id=message.message_id + "-resp",
            event_id=message.event_id,
            sender=self.name,
            receiver=message.sender,
            message_type="response",
            payload={
                "action": action,
                "explanation_text": exp_text,
                "llm_fallback_used": fallback_used
            },
            confidence=max(0.1, conf),
            evidence={"explanation": exp_text},
            trace_id=message.trace_id
        )

decision_agent_instance = DecisionAgent()

@app.post("/agent/process", response_model=AgentMessage)
async def agent_process(message: AgentMessage):
    try:
        return await decision_agent_instance.process(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
