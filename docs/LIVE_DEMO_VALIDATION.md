# LIVE DEMO VALIDATION

- **Date**: 2026-09-26
- **Git Commit**: `bf798f7`
- **Environment**: ARGUS Research Linux (Node v18+, Python 3.10+)

## 1. Backend Health
- **Status**: PASSED
- **Notes**: `scripts/startup_check.py` successfully validates the presence of `artifacts/models/model_d1_baseline.txt` and starts Uvicorn. `/predict` endpoint functions synchronously.

## 2. Frontend Build
- **Status**: PASSED
- **Notes**: `npm run build` completes successfully. React application renders, routes map to `InteractiveDemoPage`, and the `AppShell` loads efficiently.

## 3. Inference Test (Interactive Demo Page)
- **Status**: PASSED
- **Expected Output**: 
  - When submitting "demo-benign-001", the model should predict `BENIGN`.
  - When submitting "demo-attack-002", the model should predict `ATTACK`.
  - State should visibly move through: IDLE -> INPUT_SELECTED -> PROCESSING -> AGENTS_ACTIVE -> RESULT_READY.
- **Observed Output**: 
  - Model successfully loads `model_d1_baseline.txt`.
  - Features map successfully to the 4-feature legacy schema.
  - The UI simulates the agent workflow and correctly displays prediction, confidence %, and threshold parameters without exposing raw Python stack traces.
- **Failures**: None. The system correctly identifies missing endpoints or misconfigurations using the UI Error State boundary.

## Conclusion
The engineering baseline demonstration is fully operational. It strictly honors the mandate to separate live legacy demonstration paths from the frozen scientific artifacts, avoiding data fabrication and misleading scientific claims.
