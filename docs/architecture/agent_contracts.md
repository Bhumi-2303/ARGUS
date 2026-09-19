> Note: Features documented here indicate what is strictly **IMPLEMENTED** unless explicitly tagged as **PLANNED**.

# Agent Contracts

## Detector Agent
- **Version:** 1.0.0
- **Input:** Raw OT/IT telemetry (array/batch).
- **Output:** Anomaly probability, categorical threat label, SHAP values.
- **Responsibility:** Real-time multi-model anomaly detection (LightGBM/FT-Transformer).
- **Failure Behavior:** Fallback to safe mode (probability=0) or forward raw telemetry to review.
- **Timeout Behavior:** 100ms timeout per batch; returns UNKNOWN.
- **Provenance:** Trained on CICIoT2023 / NF-ToN-IoT, aligned via CORAL.

## Risk Agent (`risk_prediction`)
- **Version:** 1.0.0
- **Input:** Detector probability, asset criticality, historical context.
- **Output:** Risk Score (0-100), severity tier, impact estimation.
- **Responsibility:** Evaluate contextual risk of a detected anomaly based on asset importance.
- **Failure Behavior:** Defaults to Risk Score = 50 (Unknown), Severity = MEDIUM.
- **Timeout Behavior:** 2s timeout.

## Knowledge Context Agent (`knowledge_context`)
- **Version:** 1.0.0
- **Input:** Threat indicators, anomaly labels.
- **Output:** MITRE ATT&CK techniques, CVEs, CISA advisories.
- **Responsibility:** Enrich raw alerts with external threat intelligence and actionable context.
- **Failure Behavior:** Returns empty knowledge arrays; does not block pipeline.
- **Timeout Behavior:** 3s timeout.

## Explainability Module
- **Version:** 1.0.0
- **Input:** SHAP values, telemetry features.
- **Output:** Top feature drivers, LLM-generated human-readable summary.
- **Responsibility:** Translate raw model attribution into security operation summaries.
- **Failure Behavior:** Returns raw top features without LLM summary.
- **Timeout Behavior:** 5s timeout.

## Policy Engine (Deterministic)
- **Version:** 1.0.0
- **Input:** Risk tier, asset criticality, threat category, detector confidence.
- **Output:** Policy decision (e.g. MONITOR, INVESTIGATE, ESCALATE, ISOLATE), required approval state.
- **Responsibility:** Authoritatively map risk and context to deterministic mitigation actions.
- **Failure Behavior:** Defaults to MONITOR (fail-safe).
- **Timeout Behavior:** < 50ms timeout.

## Decision Agent (`decision_support`)
- **Version:** 1.0.0
- **Input:** Policy decision, full event context.
- **Output:** Final response command, ticket creation, orchestration trigger.
- **Responsibility:** Execute the action dictated by the Policy Engine.
- **Failure Behavior:** Logs error, escalates to human operator.
- **Timeout Behavior:** 2s timeout.

## Execution Trace & Orchestrator
- **Responsibility:** Deterministically route events between agents/modules, record execution times and provenance.
