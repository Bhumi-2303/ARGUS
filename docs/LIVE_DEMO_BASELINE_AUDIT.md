# LIVE DEMO BASELINE AUDIT

## 1. Current frontend entry point
- **Location**: `web/` (React SPA)
- **Entry**: `web/src/main.tsx` initializing `App.tsx` and routing.
- **Features**: Includes multiple fully implemented UI pages (`LiveMonitorPage`, `TopologyPage`, `ExplainabilityPage`, `ModelComparisonPage`, `SystemOverviewPage`).

## 2. Current backend/API entry point
- **Location**: `src/argus/api/` (FastAPI)
- **Entry**: `src/argus/api/main.py`
- **Features**: Exposes routers for `/health`, `/predict`, `/stream`, `/explain`, `/models`, and `/agents`. Connects to a `global_bus` for server-sent events (SSE).

## 3. Existing ARGUS agents
- **Threat Analysis Agent**: `src/argus/agents/threat_analysis/agent.py`. Runs inference, calculates confidence, gathers evidence, and uses a Publisher tool to emit results to a message bus.
- **Decision Agent**: `src/argus/services/decision_agent/main.py` (and potentially inside `agents/`).

## 4. Existing model/inference path
- **Loader**: `src/argus/registry/model_registry.py` and `src/argus/models/loader.py`
- **Inference**: Uses `xgboost` and `lightgbm` via `model_registry.predict()`. The backend expects a 4-feature legacy schema (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`) which conflicts with our V2 11D neural representation.

## 5. Available model artifacts
- **Location**: `artifacts/models/`
- **Models**:
  - `model_d1_baseline.txt` (LightGBM)
  - `model_d2_coral.txt` (LightGBM)
  - `model_d3_native.txt`
  - `xgb_adapted.json`, `xgb_source.json` (XGBoost)
- **Note**: These are strictly legacy (Phase 1) tree-based checkpoints. PyTorch V2 checkpoints are NOT natively deployed here.

## 6. Available sample input data
- **Generator**: `scripts/make_demo_samples.py`
- **Dependency**: Looks for `ARGUS_Cross_Domain_Results/argus_coral_data/*.csv`.
- **Status**: The script expects legacy legacy pre-V2 data paths which may not exist or align with the current clean data pipeline.

## 7. Existing endpoints
- `POST /predict`: Sync prediction.
- `GET /stream/events`: SSE stream for the Live Monitor.
- `GET /models`: List loaded artifacts.
- `GET /agents/health`: Agent diagnostic status.

## 8. Existing configuration
- Managed via `os.getenv` in `main.py` (e.g., `ARGUS_HOST`, `ARGUS_PORT`, `ARGUS_MODE`).
- API uses strict CORS rules.

## 9. Existing deployment/run commands
- `scripts/startup_check.py`: Validates model artifacts exist.
- `scripts/start_demo.py`: Builds the `web/dist` via NPM and launches `uvicorn` serving the API and static frontend simultaneously on port 8000.

## 10. Missing components required for a live demo
1. **Valid Sample Data**: The `make_demo_samples.py` points to a missing legacy directory and extracts only 4 legacy features. Needs to be pointed to a valid dataset/fixture.
2. **Schema Mismatch Warning**: The deployed legacy models use a 4-feature schema, whereas our frozen scientific experiments established an 11-feature baseline. The demo MUST use the legacy models + legacy 4-feature schema since the V2 PyTorch models have no inference integration path in the codebase.
3. **Demo Data Ingestion**: A script to pump events into the `/predict` or `/stream` endpoints to simulate live traffic for the UI Monitor.
