> Note: Features documented here indicate what is strictly **IMPLEMENTED** unless explicitly tagged as **PLANNED**.

# Incident Lifecycle

The ARGUS incident lifecycle provides a structured, auditable workflow for managing security incidents.

## Incident States
- **DETECTED:** The initial state when a threat or anomaly is identified.
- **TRIAGED:** The event has been contextualized and prioritized by Risk/Knowledge agents.
- **INVESTIGATING:** Security operators are actively analyzing the incident.
- **ESCALATED:** The incident requires higher-level intervention or cross-team collaboration.
- **CONTAINED:** Mitigation actions (e.g., isolation) have been executed successfully.
- **RESOLVED:** The root cause is addressed and the system is back to normal operations.
- **CLOSED:** The incident is archived.

## Human Approval Lifecycle
High-impact actions (such as ISOLATE) require explicit approval before containment.
- **PENDING:** Waiting for a security operator to approve.
- **APPROVED:** Action authorized by an operator.
- **REJECTED:** Operator denied the recommended action.
- **NOT_REQUIRED:** Action is low-risk (e.g., MONITOR) and does not need approval.

## Audit and Traceability
Every transition generates a Timeline Event (action, actor, details, timestamp), ensuring strict traceability and compliance suitable for critical infrastructure environments.
