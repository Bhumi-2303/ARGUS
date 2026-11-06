"""Optional ADK/LLM Analyst Narrator for ARGUS.

Summarizes already-computed incident outputs into an executive incident briefing.

SAFETY & COMPLIANCE INVARIANTS:
1. OFF by default.
2. NEVER on the detection path (pure post-processing / on-demand narration).
3. NEVER alters risk scores, threat levels, or remediation decisions.
4. Clean zero-dependency fallback to deterministic summary when no API key is provided
   or when LLM network calls fail.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger("argus.integrations.adk.narrator")


class IncidentNarrative(BaseModel):
    """Structured security incident narrative and briefing."""

    incident_id: str
    title: str
    narrative_markdown: str
    executive_summary: str
    key_findings: List[str]
    is_llm_generated: bool
    fallback_reason: Optional[str] = None

    # Read-only verification anchors — guaranteed 100% identical to computed pipeline results
    verified_risk_score: int = Field(description="Immutable copy of pipeline risk score.")
    verified_severity: str = Field(description="Immutable copy of pipeline severity level.")
    verified_threat_level: str = Field(description="Immutable copy of pipeline threat level.")
    verified_decision_actions: List[str] = Field(
        description="Immutable copy of prescribed actions."
    )
    generated_at: str


class IncidentNarrator:
    """Narrates and summarizes already-computed ARGUS security incident outputs."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        timeout_seconds: float = 5.0,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("ARGUS_GEMINI_MODEL", "gemini-2.5-flash")
        self.timeout_seconds = timeout_seconds
        self.logger = logger.bind(model=self.model, has_api_key=bool(self.api_key))

    def _extract_facts(self, incident: Any) -> Dict[str, Any]:
        """Safely extract verified facts from an Incident object, PipelineContext, or dict."""
        if hasattr(incident, "model_dump"):
            data = incident.model_dump()
        elif isinstance(incident, dict):
            data = incident
        elif hasattr(incident, "__dict__"):
            data = vars(incident)
        else:
            data = {}

        # Handle PipelineContext object
        if "features" in data and "threat" in data:
            threat = data.get("threat")
            threat_level = getattr(threat, "threat_level", "UNKNOWN")
            if hasattr(threat_level, "value"):
                threat_level = threat_level.value
            confidence = getattr(threat, "confidence", 0.0)

            risk = data.get("risk")
            risk_score = getattr(risk, "risk_score", 0)
            severity = getattr(risk, "severity", "LOW")
            if hasattr(severity, "value"):
                severity = severity.value

            decision = data.get("decision")
            actions = getattr(decision, "recommended_actions", [])

            explanation = data.get("explanation") or {}
            top_feat = explanation.get("top_feature", "unknown")
            top_impact = explanation.get("top_feature_impact", 0.0)

            knowledge = data.get("knowledge") or {}
            mitre = getattr(knowledge, "mitre_techniques", []) or knowledge.get(
                "mitre_techniques", []
            )

            return {
                "incident_id": data.get("correlation_id", "FLOW-SIM"),
                "threat_level": str(threat_level),
                "confidence": float(confidence),
                "risk_score": int(risk_score),
                "severity": str(severity),
                "top_feature": str(top_feat),
                "top_feature_impact": float(top_impact),
                "mitre_techniques": [str(m) for m in mitre],
                "recommended_actions": [str(a) for a in actions],
                "source_ip": "internal",
                "destination_ip": "grid-asset",
            }

        # Standard Incident or Incident dict
        threat_level = data.get("threat_level", "UNKNOWN")
        if hasattr(threat_level, "value"):
            threat_level = threat_level.value

        severity = data.get("severity", "LOW")
        if hasattr(severity, "value"):
            severity = severity.value

        return {
            "incident_id": str(data.get("incident_id", "INC-UNKNOWN")),
            "threat_level": str(threat_level),
            "confidence": float(data.get("confidence", 0.0)),
            "risk_score": int(data.get("risk_score", 0)),
            "severity": str(severity),
            "top_feature": str(data.get("top_feature", "flow_rate")),
            "top_feature_impact": float(data.get("top_feature_impact", 0.0)),
            "mitre_techniques": [str(t) for t in data.get("mitre_techniques", [])],
            "recommended_actions": [str(a) for a in data.get("recommended_actions", [])],
            "source_ip": str(data.get("source_ip", "N/A")),
            "destination_ip": str(data.get("destination_ip", "N/A")),
        }

    def _generate_deterministic_narrative(
        self, facts: Dict[str, Any], fallback_reason: Optional[str] = None
    ) -> IncidentNarrative:
        """Generate a complete, structured analyst narrative deterministically."""
        now_iso = datetime.now(timezone.utc).isoformat()
        inc_id = facts["incident_id"]
        t_level = facts["threat_level"]
        conf = facts["confidence"]
        r_score = facts["risk_score"]
        sev = facts["severity"]
        top_f = facts["top_feature"]
        top_imp = facts["top_feature_impact"]
        mitre = facts["mitre_techniques"]
        actions = facts["recommended_actions"]

        status_note = (
            f"> [!NOTE]\n> **Narrator Mode:** Deterministic Fallback Engine.\n> **Reason:** {fallback_reason}\n"
            if fallback_reason
            else "> [!NOTE]\n> **Narrator Mode:** Deterministic Rule-Based Engine (Verified Zero-Hallucination).\n"
        )

        exec_summary = (
            f"ARGUS detected a {t_level} severity event (confidence: {conf:.1%}) "
            f"classified with an operational cyber-physical risk score of {r_score}/100 ({sev}). "
            f"Top contributing flow metric is '{top_f}' (SHAP impact: {top_imp:+.4f})."
        )

        key_findings = [
            f"Operational Risk Assessment: {r_score}/100 ({sev} Severity)",
            f"ML Classifier Threat Classification: {t_level} ({conf:.1%} confidence)",
            f"TreeSHAP Root Feature Driver: '{top_f}' with attribution weight {top_imp:+.4f}",
            f"Threat Intelligence: {len(mitre)} MITRE ATT&CK technique(s) mapped ({', '.join(mitre) if mitre else 'None'})",
            f"Decision Guidance: {len(actions)} containment and remediation action(s) generated",
        ]

        actions_md = (
            "\n".join([f"- **Action {i + 1}:** {a}" for i, a in enumerate(actions)])
            if actions
            else "- *No automated remediation required for benign traffic.*"
        )
        mitre_md = (
            f"Mapped Techniques: `{', '.join(mitre)}`"
            if mitre
            else "No active adversarial MITRE tactics identified."
        )

        markdown = f"""# Security Incident Briefing: {inc_id}

{status_note}
### Executive Summary
{exec_summary}

### Attribution & Explainability (TreeSHAP)
Analysis of the incoming telemetry batch isolates **`{top_f}`** as the highest-gain anomaly indicator, contributing an attribution delta of **`{top_imp:+.4f}`** to the classifier decision boundary.

### Threat Context & MITRE ATT&CK
{mitre_md}

### Prescribed Operational Response
{actions_md}

---
*Verified Baseline Invariant: Operational risk score is frozen at {r_score}/100 ({sev}). Decision actions are strictly authoritative.*
"""

        return IncidentNarrative(
            incident_id=inc_id,
            title=f"Incident Analysis: {inc_id} ({sev})",
            narrative_markdown=markdown.strip(),
            executive_summary=exec_summary,
            key_findings=key_findings,
            is_llm_generated=False,
            fallback_reason=fallback_reason,
            verified_risk_score=r_score,
            verified_severity=sev,
            verified_threat_level=t_level,
            verified_decision_actions=actions,
            generated_at=now_iso,
        )

    async def narrate_incident(self, incident: Any) -> IncidentNarrative:
        """Narrate an incident using Google Gemini if available, or fall back cleanly."""
        facts = self._extract_facts(incident)

        # Clean fallback if no API key is provided
        if not self.api_key:
            return self._generate_deterministic_narrative(
                facts,
                fallback_reason="No Google Gemini API key configured (GEMINI_API_KEY / GOOGLE_API_KEY unset).",
            )

        # Attempt live LLM narration with strict guardrails
        try:
            return await self._call_gemini_narrator(facts)
        except Exception as exc:
            self.logger.warning("llm_narration_failed_falling_back", error=str(exc))
            return self._generate_deterministic_narrative(
                facts,
                fallback_reason=f"Live LLM call failed ({type(exc).__name__}: {str(exc)}). Fallen back to deterministic briefing.",
            )

    async def _call_gemini_narrator(self, facts: Dict[str, Any]) -> IncidentNarrative:
        """Call Gemini generateContent API with strict fact-anchoring prompt."""
        prompt = f"""You are an executive cybersecurity narrator for the ARGUS platform.
Summarize the following verified security incident for SOC analysts.

STRICT SAFETY AND FIDELITY RULES:
1. Rely ONLY on the verified computed metrics below.
2. Do NOT invent new vulnerabilities, IP addresses, or unstated facts.
3. You MUST PRESERVE the exact risk score ({facts["risk_score"]}/100), severity ({facts["severity"]}), and actions.
4. Output professional Markdown with Executive Summary, Attribution Breakdown, and Prescribed Actions.

VERIFIED FACTS:
- Incident ID: {facts["incident_id"]}
- Threat Classification: {facts["threat_level"]} (Confidence: {facts["confidence"]:.2%})
- Operational Risk Score: {facts["risk_score"]}/100 ({facts["severity"]})
- Top Contributing Feature: {facts["top_feature"]} (SHAP Impact: {facts["top_feature_impact"]:+.4f})
- MITRE Techniques: {", ".join(facts["mitre_techniques"]) or "None"}
- Prescribed Actions: {"; ".join(facts["recommended_actions"]) or "None"}
- Source -> Destination: {facts["source_ip"]} -> {facts["destination_ip"]}
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            res_data = resp.json()

        candidates = res_data.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates returned from Gemini API.")

        parts = candidates[0].get("content", {}).get("parts", [])
        narrative_text = "".join([p.get("text", "") for p in parts]).strip()

        if not narrative_text:
            raise ValueError("Empty narrative text returned by LLM.")

        now_iso = datetime.now(timezone.utc).isoformat()
        exec_summary = (
            f"ARGUS detected a {facts['threat_level']} threat ({facts['confidence']:.1%} confidence) "
            f"with an operational risk score of {facts['risk_score']}/100 ({facts['severity']})."
        )

        return IncidentNarrative(
            incident_id=facts["incident_id"],
            title=f"Incident Analysis: {facts['incident_id']} ({facts['severity']})",
            narrative_markdown=narrative_text,
            executive_summary=exec_summary,
            key_findings=[
                f"Risk Score: {facts['risk_score']}/100 ({facts['severity']})",
                f"Threat Level: {facts['threat_level']}",
                f"Top Feature: {facts['top_feature']} ({facts['top_feature_impact']:+.4f})",
            ],
            is_llm_generated=True,
            fallback_reason=None,
            # Invariant anchors: Always maintain exact pipeline values
            verified_risk_score=facts["risk_score"],
            verified_severity=facts["severity"],
            verified_threat_level=facts["threat_level"],
            verified_decision_actions=facts["recommended_actions"],
            generated_at=now_iso,
        )
