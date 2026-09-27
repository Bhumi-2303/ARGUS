# ARGUS Agent Topology & Code Implementation Report

This report confirms the current implementation status of the five conceptual agent roles, mapping them to their actual code artifacts and verifying the routing logic of the central orchestrator.

## 1. Agent Role to Implementation Mapping
The codebase strictly relies on the modules located in `src/argus/agents/`. No placeholders or hallucinated stubs were created to fill gaps.

| Conceptual Role | Actual Agent Module | Status |
| :--- | :--- | :--- |
| **Data Intelligence** | `src/argus/agents/data_intelligence/agent.py` | **REAL**: Implements an active pipeline to ingest, clean, normalize, and extract features from CSV/Parquet flow data. |
| **Threat Analysis** | `src/argus/agents/threat_analysis/agent.py` | **REAL (Updated)**: Previously a stub. Now wired directly to the verified `model_registry`, utilizing source-only XGBoost and Clean Class-aware CORAL for predictions. |
| **Risk Prediction** | `src/argus/agents/risk_prediction/agent.py` | **STUB**: Contains basic rule-based impact mapping but relies on mocked heuristics. Emits `implementation_status="not_implemented"`. |
| **Knowledge & Context** | `src/argus/agents/knowledge_context/agent.py` | **STUB**: Queries local mocked JSON databases for MITRE/CVE/CISA lookups. Emits `implementation_status="not_implemented"`. |
| **Decision Support / Explainability** | `src/argus/agents/decision_support/agent.py` & `src/argus/agents/explainability/agent.py` | **STUB**: Decision logic returns mocked priority/urgency actions. Emits `implementation_status="not_implemented"`. |

## 2. Threat Analysis Agent Updates
To ensure the Threat Analysis Agent uses only verified components:
1. **Inference Logic Replaced**: Removed mock prediction bounds and integrated `ModelRegistry` directly via `model_registry.predict()`. The agent evaluates flows against the verified artifacts loaded from `artifacts/models`.
2. **Schema Update**: Extended the `ThreatAnalysisResult` and standard `EventMessage` schemas to mandate a `protocol_status` field (e.g., `verified`, `diagnostic`, `native`, or `not_implemented`).
3. **Telemetry Alignment**: The agent explicitly publishes `ThreatEvent` messages onto the Blackboard and Message Bus mapped strictly to the required payload schema, preventing discrepancies with API outputs.

## 3. Orchestrator Routing & Telemetry Trace
Both the HTTP pipeline (`src/argus/services/orchestrator/main.py`) and the Async DAG Orchestrator (`src/argus/orchestrator/orchestrator.py`) enforce the following routing sequence:
1. **Data Intelligence Agent** (`preprocess`)
2. **Threat Analysis Agent** (`analyze`)
3. **Risk Prediction Agent** & **Knowledge Context Agent** (Parallel `predict` & `knowledge`)
4. **Decision Support Agent** (`decision` - dependent on Risk and Knowledge outputs)

Below is the verified event trace for a single correlation flow submitted to the asyncio DAG orchestrator, proving successful propagation of `task_routed` and `task_completed` events end-to-end:

```json
{"task_id": "dcf51bf1-e15b-4bc1-9a1a-9324c888cbba", "event": "task_scheduled", "timestamp": "2026-09-26T17:15:08.110212Z"}
{"task_type": "preprocess", "agent_id": "agent_dia", "event": "task_routed", "timestamp": "2026-09-26T17:15:08.110382Z"}
{"task_id": "dcf51bf1-e15b-4bc1-9a1a-9324c888cbba", "status": "completed", "event": "task_completed", "timestamp": "2026-09-26T17:15:09.111575Z"}

{"task_id": "28f25653-c860-4f01-88ff-8ced51412164", "event": "task_scheduled_after_dependencies", "timestamp": "2026-09-26T17:15:09.111412Z"}
{"task_type": "analyze", "agent_id": "agent_threat_analysis", "event": "task_routed", "timestamp": "2026-09-26T17:15:09.111732Z"}
{"task_id": "28f25653-c860-4f01-88ff-8ced51412164", "status": "completed", "event": "task_completed", "timestamp": "2026-09-26T17:15:10.113473Z"}

{"task_id": "fa1e9e8e-63aa-4de0-8d84-8ee1544bfdef", "event": "task_scheduled_after_dependencies", "timestamp": "2026-09-26T17:15:10.113258Z"}
{"task_id": "ee84b49a-1c80-4446-bcb6-6d1ff78345b2", "event": "task_scheduled_after_dependencies", "timestamp": "2026-09-26T17:15:10.113415Z"}

{"task_type": "predict", "agent_id": "agent_risk_prediction", "event": "task_routed", "timestamp": "2026-09-26T17:15:10.113598Z"}
{"task_type": "knowledge", "agent_id": "agent_kca", "event": "task_routed", "timestamp": "2026-09-26T17:15:11.115771Z"}
{"task_id": "fa1e9e8e-63aa-4de0-8d84-8ee1544bfdef", "status": "completed", "event": "task_completed", "timestamp": "2026-09-26T17:15:11.115326Z"}
{"task_id": "ee84b49a-1c80-4446-bcb6-6d1ff78345b2", "status": "completed", "event": "task_completed", "timestamp": "2026-09-26T17:15:11.115624Z"}

{"task_id": "fd9a3cee-7485-4cfa-8831-85df30499568", "event": "task_scheduled_after_dependencies", "timestamp": "2026-09-26T17:15:11.115547Z"}
{"task_type": "decision", "agent_id": "agent_dsa", "event": "task_routed", "timestamp": "2026-09-26T17:15:12.117272Z"}
{"task_id": "fd9a3cee-7485-4cfa-8831-85df30499568", "status": "completed", "event": "task_completed", "timestamp": "2026-09-26T17:15:12.117174Z"}
```
