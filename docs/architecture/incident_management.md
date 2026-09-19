# ARGUS Incident Management Architecture

## Overview
To evolve ARGUS from a stateless event processing pipeline into a professional cybersecurity platform, a lightweight Incident Management layer has been introduced. Rather than stopping at the `Decision` phase and losing state, the platform now natively supports tracking the entire lifecycle of a security event through its resolution.

This implementation adheres to the principle of using the simplest maintainable architecture. It introduces a fast, in-memory repository pattern without immediately coupling to a heavyweight distributed database, ensuring low overhead while satisfying the requirement for stateful operations.

## Data Model
The central entity is the `Incident`, built atop Pydantic to ensure strict typing and serialization.

An `Incident` aggregates:
- **Core identifiers:** `incident_id`, `event_id`, timestamps.
- **Context:** Severity, asset criticality, risk score/tier, model provenance.
- **Summaries:** Cached outputs from the Detector and Knowledge agents to reduce repeated lookups.
- **Approvals:** Tracking whether Human-in-the-Loop (HITL) approval is required, requested, or granted.
- **Audit Timeline:** An append-only list of `TimelineEvent` records marking state transitions and actions.

## Incident Lifecycle
Incidents must strictly progress through a defined state machine:

`DETECTED` → `TRIAGED` → `INVESTIGATING` → `CONTAINED` / `ESCALATED` → `RESOLVED` → `CLOSED`

**Valid Transitions:**
- Transition logic explicitly rejects illogical state jumps (e.g., from `DETECTED` directly to `RESOLVED` without triage/investigation). 
- `CLOSED` is a terminal state that can be reached safely from almost any previous state (in case of false positives).

## Approval Workflow
For high-impact decisions determined by the Policy Engine (e.g., `ISOLATE`), the Incident's `approval_required` flag is set to `True`.

1. The incident halts at a `PENDING` approval status.
2. The UI/Analyst uses the explicit `/incidents/{id}/approve` endpoint to grant authorization.
3. The response layer safely logs this approval in the incident's timeline. No actual disruptive network changes (like isolating a VLAN) are executed at this time, preserving operational safety.

## Audit Trail
Every incident encapsulates a `timeline`.
As the incident progresses, actions (like `incident_created`, `status_changed`, `approval_granted`) are appended. This guarantees that security auditors can easily reconstruct exactly when a decision was made and by whom.
