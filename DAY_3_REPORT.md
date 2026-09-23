# ARGUS Day 3 Report: Explainability & Orchestration

## 1. Explainability Agent
- **Location:** `src/argus/agents/explainability/agent.py`
- **Implementation:** Integrated TreeSHAP (via `shap`) for feature attributions, falling back to XGBoost's native `pred_contribs=True` if `shap` is unavailable. 
- **Methodology:** 
  - Generates per-flow feature attributions for both the source model and the adapted model (processing CORAL-transformed features).
  - Computes the global mean absolute attribution across features.
  - Implemented the "explanation stability" metric, calculating the Spearman correlation coefficient of feature importance ranks between the two models.
  - **Note:** As specified, with only four features this ranking comparison is coarse. The pipeline does not assume the ranks agree.

## 2. Orchestrator State Machine
- **Location:** `src/argus/orchestrator/state_machine.py`
- **Implementation:** Built a plain Python state machine class (`OrchestratorStateMachine`), eschewing heavy external frameworks for direct control flow.
- **Order of Execution:** 
  1. `validate`
  2. `DataIntelligence`
  3. `ThreatAnalysis`
  4. `Explainability`
  5. `Fusion` (placeholder for Day 4)
  6. Final JSON report generation
- **Handling Unimplemented Agents:** Any agent explicitly not provided (or marked uninitialized) is strictly captured in the `not_implemented_agents` list within the output report, preventing silent failures or skipped steps without tracking.

## 3. Batch Replay Utility
- **Location:** `src/argus/utils/batch_replay.py`
- **Implementation:** Uses PyArrow (`pyarrow.parquet`) to read a provided Parquet dataset in distinct, sequential batches.
- **Documentation:** Explicitly documented in its module docstring as a *batch replay* utility and not a real-time stream consumer.

## 4. End-to-End Tests
- **Location:** `tests/e2e/test_day3.py`
- **Implementation:** Runs the orchestrated pipeline across the full batch replay output (simulating the 1% sample).
- **Checks Performed:** 
  - Execution runs twice consecutively.
  - Compares the resulting JSON byte-for-byte to guarantee determinism in the pipeline operations.
  - Tests the error path natively by injecting a mock agent that intentionally raises an exception, ensuring the state machine gracefully lands in the `ERROR` state with logged details.
