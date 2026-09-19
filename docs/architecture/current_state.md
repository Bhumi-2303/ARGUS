> Note: Features documented here indicate what is strictly **IMPLEMENTED** unless explicitly tagged as **PLANNED**.

# Current Architecture State

## 1. Detector Implementation
The detector is implemented as a fast FastAPI service (`src/argus/services/detector`) handling array data, utilizing LightGBM/FT-Transformer models. It communicates anomaly probabilities and returns SHAP values for explainability. The `threat_analysis` agent consumes these outputs.

## 2. Risk Implementation
Risk analysis is performed by the `risk_prediction` agent. It takes anomaly scores and assigns risk scores (0-100), along with categorical severity and impact estimation based on asset priority.

## 3. Knowledge Implementation
The `knowledge_context` agent maps threat indicators to MITRE techniques, CVEs, and CISA advisories. It returns contextual knowledge and mitigations.

## 4. Decision Implementation
Decision logic is split between a `decision_agent` service and `decision_support` agent. It evaluates the risk and threat context to recommend mitigations.

## 5. Explainability Implementation
Explainability uses SHAP values calculated in the detector. The output includes top feature drivers and LLM-assisted human-readable explanations within the pipeline.

## 6. Existing Orchestrator
The orchestrator (`src/argus/services/orchestrator/`) routes events sequentially through the agents via the blackboard pattern or message bus. It is deterministic.

## 7. Frontend API Contracts
API endpoints exist in `src/argus/api/routers` for agents, health, tasks, incidents, and monitoring, using Pydantic schemas.

## 8. Monitoring / Drift
Drift detection is implemented in `src/argus/monitoring/drift.py` to analyze batch drift.

## 9. Logging / Audit
Audit and logging capabilities are present in `src/argus/security/audit.py`.

## 10. Incident / Alert Models
`src/argus/schemas/incident.py` and `src/argus/services/incident_service.py` handle basic incident state tracking (e.g. TRIAGED, RESOLVED).

## 11. Authentication / Authorization Assumptions
Middleware exists in `src/argus/security/` for auth, secrets, masking, but relies on assumed tokens.

## 12. Tests
The test suite in `tests/` covers unit and integration logic, totaling approximately 60 passing tests.
