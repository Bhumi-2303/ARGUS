# LIVE DEMO BASELINE

## 1. Architecture
The ARGUS Demo Baseline is structured as a full-stack web application bridging an air-gapped environment with our locally hosted legacy models.
- **Frontend**: React (Vite, TypeScript, TailwindCSS) running as an SPA. Features an interactive "Interactive Demo" page (`/demo`) to run single-sample inferences.
- **Backend**: FastAPI running on Uvicorn. Exposes a `/predict` synchronous endpoint, and handles API routing for agents.
- **Inference Engine**: Relies on `src/argus/registry/model_registry.py` wrapping LightGBM/XGBoost. It currently leverages the verified Phase 1 legacy `model_d1_baseline` due to architectural constraints forbidding the use of the PyTorch V2 scripts.

## 2. How to start backend
Start the full stack (backend + static SPA delivery) using the provided launcher:
```bash
python scripts/start_demo.py
```
This automatically initiates Uvicorn on `0.0.0.0:8000`.

## 3. How to start frontend
The frontend is built and served statically by the backend script. For active UI development with Hot-Module-Reloading:
```bash
cd web
npm install
npm run dev
```

## 4. Required environment variables
- `ARGUS_HOST`: Bind host (default: `0.0.0.0`)
- `ARGUS_PORT`: Port (default: `8000`)
- `ARGUS_MODE`: Environment mode (default: `demo`)
- `ARGUS_ALLOWED_ORIGINS`: CORS array (default allows localhost).

## 5. Model requirements
- Verified artifact: `artifacts/models/model_d1_baseline.txt`
- Checkpoint models must match the strict 4-feature legacy schema (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`).

## 6. Sample-data requirements
- The demo UI provides hardcoded JSON fixtures (`demo-benign-001`, `demo-attack-002`) compliant with the legacy schema.
- To simulate live bulk telemetry stream monitoring, run `scripts/make_demo_samples.py` (ensure you have the legacy `ARGUS_Cross_Domain_Results/argus_coral_data/` source directory available).

## 7. Exact demo workflow
1. Open the UI via browser at `http://localhost:8000`.
2. Navigate to the **Interactive Demo** (`/demo`) section from the sidebar.
3. Choose either the Benign TCP or Malicious UDP demo sample.
4. Click **Run Detection**.
5. Observe the Pipeline State traverse through: Input Received -> Data Intelligence -> Threat Analysis -> Decision Output.
6. Observe the final prediction, probability/confidence score, and inspect the raw feature attributes.
7. Repeat inference dynamically without reloading the page.

## 8. Known limitations
- **Schema Mismatch**: The backend operates on the Phase 1 4-feature schema (`model_d1_baseline`). Our rigorous Phase 2 experiments proved this schema is insufficient, formulating an 11D robust neural representation. This demo *does not* reflect the neural V2 architecture.
- **No Active Sub-Agents**: While the `ThreatAnalysisAgent` class exists, the synchronous `/predict` endpoint calls `model_registry` directly to avoid websocket delays. The pipeline state in the interactive UI is a simulated orchestration trace of the monolithic backend response.

## 9. What is real vs simulated
- **Real**: The model inference execution (`model_d1_baseline.txt` is legitimately classifying the vectors).
- **Real**: The probability boundaries and prediction thresholds.
- **Simulated**: The "Agent Activation" UI loading steps are artificially paced (using `setTimeout`) to allow human visibility into the conceptual lifecycle, as local monolithic inference completes in < 5ms.
- **Simulated**: The sample dataset fixtures are synthetically crafted subsets designed specifically to demonstrate the legacy model boundaries.

## 10. Troubleshooting
- If inference fails, ensure `model_d1_baseline.txt` exists in `artifacts/models/`.
- If the UI is blank, verify that `npm run build` completed inside `web/` and `web/dist/index.html` exists.
- If CORS issues arise from HMR development, ensure `ARGUS_ALLOWED_ORIGINS` includes your dev port (e.g. `http://localhost:5173`).
