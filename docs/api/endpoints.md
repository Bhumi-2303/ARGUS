# ARGUS API Contracts

## `GET /api/v1/incidents/`
Returns a list of incidents tracking the `Incident` schema.

## `GET /api/v1/incidents/{id}`
Returns a specific incident.

## `PATCH /api/v1/incidents/{id}/status`
Updates incident status (e.g. `DETECTED` -> `TRIAGED`).

## `POST /api/v1/incidents/{id}/approve`
Approves a high-risk mitigation action.

## `GET /api/v1/health`
Returns `SystemHealth` status.

## `POST /api/v1/agent/process`
Accepts `AgentMessage` (Internal only).

## `POST /api/v1/detector/predict`
Accepts `FlowRecord`, returns binary prediction, probability, threshold, and `shap_values`.

## *Planned Endpoints (Frontend Dependencies)*
- `GET /api/v1/audit/`
- `GET /api/v1/explanations/`
- `GET /api/v1/models/`
- `GET /api/v1/network/nodes/`
- `GET /api/v1/network/connections/`
