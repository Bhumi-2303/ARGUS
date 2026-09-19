# ARGUS Decision Policy Architecture

## Overview
In a production cybersecurity environment, machine learning predictions must not dictate security actions directly without oversight. We have explicitly separated the decision pipeline into five distinct stages:

**Detector → Risk Engine → Policy Engine → Decision → Response**

### Why this separation exists
1. **Detector vs. Action Conflict**: Historically, a detector generating a positive prediction (`pred == 1`) might implicitly or directly trigger an `INVESTIGATE` action through downstream heuristics. However, an anomaly on a low-criticality asset with minimal risk should not waste analyst time. The Risk Engine translates statistical predictions into impact, and the Policy Engine translates impact into authoritative, deterministic actions.
2. **LLM Non-Authoritative Rule**: The LLM (via the Knowledge Agent) is strictly confined to providing context, explainability, and analyst summaries. It **does not** act as the policy engine. If the LLM generates hallucinations or goes offline entirely, the deterministic Policy Engine continues to execute isolated security policies safely.
3. **Auditability and Governance**: Security actions require compliance trails. By externalizing the Policy Engine, all actions are tied to a versioned `policy_id` and explicitly evaluate `requires_human_approval` before passing intent to the Response layer.

## Target Architecture Components

* **Detector**: Yields probabilities and structural anomaly confidence directly from the ML models (e.g. XGBoost, LightGBM).
* **Risk Engine**: Determines operational and business risk, synthesizing asset criticality and threat context.
* **Policy Engine**: A deterministic ruleset (e.g., `src/argus/policy/engine.py`) that strictly outputs standard actions (`MONITOR`, `INVESTIGATE`, `ESCALATE`, `ISOLATE`).
* **Decision**: Formulates the structured output containing the authorized action, the hit policy, and the HITL (Human-in-the-Loop) gate requirement.
* **Response**: Executes the approved action (e.g., raising tickets, automated isolations).

## Fail-Safe 
The Policy Engine is designed to fail securely. If upstream context engines (Risk, Knowledge, LLM, or Explainability) are unavailable or return malformed data, the Policy Engine defaults to `MONITOR`. It will strictly avoid escalating privileges or executing disruptive infrastructure isolation in uncertain system states.
