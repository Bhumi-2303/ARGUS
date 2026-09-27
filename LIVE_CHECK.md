# ARGUS Live System Check Runbook

This runbook allows a human operator to verify that the ARGUS agent topology and real-time inference pipelines are running correctly, using verified components rather than mock placeholders.

## Prerequisites
Ensure you are in the root of the ARGUS repository. All required data artifacts and models must be present in `artifacts/models`, `artifacts/transforms`, and `data/samples/`. The startup routine automatically gates execution and will fail loudly if anything is missing.

## Step 1: Launch the Unified System
We have consolidated the API, the multi-agent orchestrator, and the React frontend into a single execution boundary. 

Run the following command:
```bash
make demo
```
*(Alternatively: `python scripts/start_demo.py`)*

**What a correct result looks like:**
The terminal will display startup logs. You should see logs indicating that the artifact verification passed (`startup_artifact_verification_passed`), models loaded successfully, and the agents/orchestrator initialized (`async_agent_orchestrator_started`). The server will host the UI at `http://localhost:8000`.

## Step 2: Verify Agent Topology 
Navigate your browser to:
**http://localhost:8000/topology**

**What to check:**
1. The animated System Topology map should display exactly the agents configured in the source code.
2. Check the Agent Nodes for their implementation status. 
   - **Data Intelligence Agent**: Should appear as fully implemented.
   - **Threat Analysis Agent**: Should appear as fully implemented.
   - **Risk Prediction Agent**: Must display a grey "not implemented" or "stub" badge.
   - **Knowledge Context Agent**: Must display a grey "not implemented" or "stub" badge.
   - **Decision Support Agent**: Must display a grey "not implemented" or "stub" badge.

*Why this is correct:* We have removed fake data generation from the stubs. Agents without real ML/logic models honestly report themselves as stubs.

## Step 3: Trigger a Real Flow Trace
On the **System Topology** page, locate and click the **"Trigger simulated flow"** button.

**What to check:**
1. The animated data packet should trace a specific route: `API Gateway -> Message Bus -> Orchestrator -> Data Intelligence -> Threat Analysis -> Risk/Knowledge -> Decision Support`.
2. Look at the trace logs emitted in the sidebar/bottom sheet. 
3. Verify that the Threat Analysis step explicitly logs the usage of a real verified model (e.g., `model_d2_coral` or `xgb_adapted` with a specific probability value), rather than generic placeholder text. 
4. Verify that downstream agents (Risk, Knowledge, Decision) log that they are returning `not_implemented`.

## Step 4: Verify Live Monitor Discrepancy (FLAG)
Navigate your browser to:
**http://localhost:8000/live**

**🚨 CRITICAL DISCREPANCY FLAG 🚨**
The Live Monitor page displays real-time flow classifications (e.g., the CORAL Aligned XGBoost cards computing probabilities at 10+ flows per second). **However, this view currently bypasses the Agent Orchestrator chain.** 

If you trace the code execution for `/api/v1/agents/stream`, the WebSocket directly invokes `model_registry.predict()` inside a tight generator loop to achieve high-throughput SSE (Server-Sent Events) streaming. It does *not* dispatch a `task_routed` event to the `ThreatAnalysisAgent` over the Message Bus.

**What this means:** 
The Threat Analysis Agent and the Live Monitor use the *exact same underlying ML models* (loaded from the exact same unified `ModelRegistry`), so the predictions themselves are mathematically identical. However, architecturally, they are calling the registry via two separate code paths. 

*Recommendation:* Before we can certify this as a strictly "Unified System", the Live Monitor's SSE endpoint must be refactored to subscribe to the Message Bus's `events.threat.high` topics published by the `ThreatAnalysisAgent`, rather than querying the `ModelRegistry` directly. For now, the visual stream proves the *models* work, but it does not prove the *agent chain* can handle high-throughput streaming.

