# ARGUS System Baseline & Verification Report

**Branch:** `chore/baseline`  
**Date:** 2026-11-04  
**Author / Runner:** ARGUS Agentic CI Environment  
**Standing Verification Rule:** All figures and test logs trace directly to live execution outputs and `results/verified/`.

---

## 1. Runtime Environment & Toolchain Versions

| Component | Version | Binary Path | Notes |
| :--- | :--- | :--- | :--- |
| **Operating System** | Linux 6.x (x86_64) | `/usr/bin/uname -a` | Standard containerized Linux environment |
| **Python** | `3.14.9` | `/usr/bin/python3`, `.venv/bin/python` | Matches repo `.venv` environment |
| **Node.js** | `v22.23.2` | `/home/bhumi/.nvm/versions/node/v22.23.2/bin/node` | Compatible with Vite 8.3 & React 18 |
| **npm** | `10.9.8` | `/home/bhumi/.nvm/versions/node/v22.23.2/bin/npm` | Package manager for `web/` |
| **uv** | Installed | `/usr/bin/uv` | Fast Python package resolution |
| **pip** | `26.0` (inside `.venv`) | `.venv/bin/pip` | Installed in editable mode |

---

## 2. Virtual Environment & Dependency Installation

The repository contains an existing Python 3.14 virtual environment located at `.venv/`.

### Installation Command & Output

```bash
.venv/bin/pip install --no-build-isolation --no-deps -e ".[dev,test]"
```

**Output:**
```text
Obtaining file:///home/bhumi/GitHub/ARGUS
  Checking if build backend supports build_editable ... done
  Preparing editable metadata (pyproject.toml) ... done
Building wheels for collected packages: argus
  Building editable for argus (pyproject.toml) ... done
  Created wheel for argus: filename=argus-0.1.0-py3-none-any.whl size=11335
Successfully built argus
Installing collected packages: argus
  Attempting uninstall: argus
    Found existing installation: argus 0.1.0
    Uninstalling argus-0.1.0:
      Successfully uninstalled argus-0.1.0
Successfully installed argus-0.1.0
```

> [!NOTE]
> During baseline installation within an isolated sandbox (no external PyPI network resolution), standard `pip install -e .[dev,test]` without `--no-deps` or `--no-build-isolation` attempts remote index lookups for `hatchling` and dependencies. Using `--no-build-isolation` utilizes the pre-installed `hatchling` (v1.30.1) and packages already populated in `.venv`.

---

## 3. Test Suite Execution (`pytest -q`)

### Command
```bash
.venv/bin/pytest -q
```

### Exact Summary Output
```text
........................................................................ [ 25%]
........................................................................ [ 50%]
........................................................................ [ 76%]
...................................................................      [100%]
283 passed, 832 warnings in 6.75s
```

### Test Statistics
- **Passed:** `283`
- **Failed:** `0`
- **Skipped:** `0`
- **Errors:** `0`
- **Warnings:** `832` (primarily deprecation notices: Pydantic v2 `ConfigDict` migration hints, `asyncio.iscoroutinefunction` vs `inspect.iscoroutinefunction` deprecation slated for Python 3.16, timezone-aware UTC datetime deprecations, and LightGBM TreeExplainer array formats).

---

## 4. Startup Asset Verification (`python scripts/startup_check.py`)

### Command
```bash
.venv/bin/python scripts/startup_check.py
```

### Exact Output
```text
================================================================================
                ARGUS RESEARCH STARTUP INTEGRITY VERIFICATION
================================================================================
Category     | Asset / Component                   | File Status  | Result  
--------------------------------------------------------------------------------
Artifacts    | Model D1 Baseline (LightGBM)        | EXISTS       | [ PASS ]
Artifacts    | Model D1 CORAL (LightGBM)           | EXISTS       | [ PASS ]
Artifacts    | Model D2 CORAL (LightGBM)           | EXISTS       | [ PASS ]
Artifacts    | Model D3 Native (LightGBM)          | EXISTS       | [ PASS ]
Artifacts    | Model XGBoost Source                | EXISTS       | [ PASS ]
Artifacts    | Model XGBoost Adapted               | EXISTS       | [ PASS ]
Samples      | CICIoT2023 Source Parquet           | EXISTS       | [ PASS ]
Samples      | NF-ToN-IoT-v2 Target Parquet        | EXISTS       | [ PASS ]
Results      | 5-Model Comparison CSV              | EXISTS       | [ PASS ]
Results      | DANN Test Metrics CSV               | EXISTS       | [ PASS ]
Results      | D3 Native Sweep CSV                 | EXISTS       | [ PASS ]
Results      | SHAP vs Target Gain CSV             | EXISTS       | [ PASS ]
Results      | Diagnostic CORAL CSV                | EXISTS       | [ PASS ]
Frontend     | Built Web Dist HTML                 | EXISTS       | [ PASS ]
--------------------------------------------------------------------------------
Validating Model Deserialization & Data Integrity...
Model Loader | LightGBM model_d2_coral.txt         | LOADED       | [ PASS ]
Model Loader | XGBoost xgb_adapted.json            | LOADED       | [ PASS ]
Data Loader  | CICIoT (10000 real rows)            | VALID        | [ PASS ]
Data Loader  | NF-ToN (10000 real rows)            | VALID        | [ PASS ]
================================================================================
OVERALL VERIFICATION VERDICT: PASS — All required research assets verified.
================================================================================
```

---

## 5. UI Numerical Integrity Verification (`python scripts/verify_ui_numbers.py`)

### Command
```bash
.venv/bin/python scripts/verify_ui_numbers.py
```

### Exact Output
```text
================================================================================
        ARGUS FINAL NUMERICAL INTEGRITY VERIFICATION (CSV vs API)
================================================================================

Verifying Table: five_model_complete_comparison | CSV Path: results/verified/five_model_complete_comparison.csv
  [ PASS ] All 5 rows and numerical metrics match source CSV 100%.

Verifying Table: dann_final_test_metrics        | CSV Path: results/verified/dann_final_test_metrics.csv
  [ PASS ] All 12 rows and numerical metrics match source CSV 100%.

Verifying Table: d3_native_threshold_sweep      | CSV Path: results/verified/d3_native_threshold_sweep.csv
  [ PASS ] All 99 rows and numerical metrics match source CSV 100%.

Verifying Table: SHAP_vs_Target_Gain            | CSV Path: results/verified/SHAP_vs_Target_Gain.csv
  [ PASS ] All 4 rows and numerical metrics match source CSV 100%.

Verifying Table: diagnostic_class_aware_coral   | CSV Path: results/diagnostic/diagnostic_class_aware_coral.csv
  [ PASS ] All 1 rows and numerical metrics match source CSV 100%.

================================================================================
        ARGUS SYSTEM TOPOLOGY STRING VERIFICATION (/api/v1/agents/topology)
================================================================================
Crawled 10 topology nodes and 8 edge connections.
  Node [orchestrator      ]: 'Orchestrator Engine' | Type: engine | Impl: full
  Node [message_bus       ]: 'Event Message Bus' | Type: bus | Impl: full
  Node [api_gateway       ]: 'API Gateway' | Type: gateway | Impl: full
  Node [policy_engine     ]: 'Policy Engine' | Type: engine | Impl: full
  Node [data_intelligence ]: 'Data Intelligence Agent' | Type: agent | Impl: full
  Node [threat_analysis   ]: 'Threat Analysis Agent' | Type: agent | Impl: full
  Node [explainability    ]: 'Explainability Agent' | Type: agent | Impl: full
  Node [risk_prediction   ]: 'Risk Prediction Agent' | Type: agent | Impl: full
  Node [decision_support  ]: 'Decision Support Agent' | Type: agent | Impl: full
  Node [knowledge_context ]: 'Knowledge Context Agent' | Type: agent | Impl: full
  [ PASS ] All 10 topology node labels, responsibilities, and implementation flags verified.

================================================================================
        ARGUS PROTOCOL LIMITS PAGE TEXT VERIFICATION
================================================================================
  [ PASS ] Protocol Limits Page explicitly states all required open verification discrepancies accurately.

================================================================================
        ARGUS UI RENDER LOGIC VERIFICATION (ModelComparisonPage.tsx)
================================================================================
  [ PASS ] No identical repeated fallback values (like 0.0000 or 95/5) found in ModelComparisonPage.tsx
```

---

## 6. Web Application Build & Lint

### Frontend Build (`cd web && npm run build`)
```text
> web@0.0.0 build
> tsc -b && vite build

vite v8.3.1 building client environment for production...
✓ 3121 modules transformed.
dist/index.html                                 0.46 kB │ gzip:   0.30 kB
dist/assets/index-DXd7Q9iR.css                 51.78 kB │ gzip:   9.21 kB
dist/assets/arrow-right-BI0D4hvL.js             0.19 kB │ gzip:   0.17 kB
dist/assets/play-BubAiSED.js                    0.21 kB │ gzip:   0.19 kB
dist/assets/circle-check-D2SBWEMm.js            0.23 kB │ gzip:   0.20 kB
dist/assets/git-branch-0GzECU5e.js              0.25 kB │ gzip:   0.20 kB
dist/assets/activity-BHAQ5e5D.js                0.26 kB │ gzip:   0.22 kB
dist/assets/zap-Bum93faG.js                     0.30 kB │ gzip:   0.23 kB
dist/assets/crosshair-BUguJaAO.js               0.38 kB │ gzip:   0.24 kB
dist/assets/layers-Bd47vorI.js                  0.47 kB │ gzip:   0.27 kB
dist/assets/useMutation-CNIfFfst.js             2.30 kB │ gzip:   0.94 kB
dist/assets/ProvenanceBadge-BnkkGZBn.js         5.07 kB │ gzip:   1.79 kB
dist/assets/ExplainabilityPage-R-GaFPVF.js      8.04 kB │ gzip:   2.77 kB
dist/assets/OverviewPage-DG18S4ju.js           15.04 kB │ gzip:   3.53 kB
dist/assets/InputAnalysisPage-Ge4T48K3.js      21.01 kB │ gzip:   5.21 kB
dist/assets/ResultsPage-C3-zeHp6.js            34.24 kB │ gzip:   8.19 kB
dist/assets/index-DSkNt4SU.js                 320.89 kB │ gzip: 100.95 kB
dist/assets/TopologyPage-Cjrl2aoz.js          965.69 kB │ gzip: 256.58 kB
dist/assets/esm-DaNYU2BO.js                 1,135.23 kB │ gzip: 377.20 kB
✓ built in 875ms
```
- **Exit Code:** `0` (Success)

### Frontend Lint (`cd web && npm run lint`)
```text
> web@0.0.0 lint
> oxlint

Found 34 warnings and 0 errors.
Finished in 40ms on 38 files with 116 rules using 8 threads.
```
- **Exit Code:** `0` (Success, 0 errors, 34 warnings mostly around unused icon imports and fast-refresh component exports).

---

## 7. Demo Launch (`make demo`), Startup Errors & Endpoint Verification

### Startup Error Observed

When initiating `make demo` on the target machine, the following error occurred:

```text
Starting ARGUS Platform Server...
Serving API and Web Frontend at: http://localhost:8000

INFO:     Started server process [26]
INFO:     Waiting for application startup.
...
INFO:     Application startup complete.
ERROR:    [Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
make: *** [Makefile:16: demo] Error 3
```

**Root Cause:**  
Host port `8000` was occupied by a previously running external Docker container (`arogyavajra-api` running on `0.0.0.0:8000->8000/tcp`).

### Clean Execution (with Port 8000 Available)

Once port 8000 was temporarily released:
1. `make demo` booted cleanly.
2. Verified all 5 production models in `ModelRegistry` loaded successfully (`model_d1_baseline`, `model_d2_coral`, `model_d3_native`, `xgb_source`, `xgb_adapted`).
3. DANN was registered as `unavailable` (conforming to documented majority-class collapse safeguards).
4. All 6 autonomous agents registered to the message bus: `agent_dia` (DIA), `agent_threat_analysis`, `agent_risk_prediction`, `agent_kca` (KCA), and `agent_dsa` (DSA).
5. Orchestrator started and Uvicorn bound to `http://0.0.0.0:8000`.

### Endpoint Check: `GET /health`

```bash
curl -s -i http://localhost:8000/health
```

**Response:**
```http
HTTP/1.1 200 OK
date: Wed, 04 Nov 2026 15:04:56 GMT
server: uvicorn
content-length: 228
content-type: application/json
x-frame-options: DENY
x-content-type-options: nosniff
referrer-policy: strict-origin-when-cross-origin
permissions-policy: geolocation=(), camera=(), microphone=(), payment=(), usb=()
content-security-policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:; worker-src 'self' blob:; child-src 'self' blob:; frame-ancestors 'none'; object-src 'none'; base-uri 'self'; form-action 'self'
x-request-id: req-012ff7c8d9ee

{
  "status": "healthy",
  "uptime_seconds": 38.43,
  "timestamp": "2026-11-04T15:04:57.296491+00:00",
  "models_loaded": {
    "model_d1_baseline": true,
    "model_d2_coral": true,
    "model_d3_native": true,
    "xgb_source": true,
    "xgb_adapted": true,
    "dann": false
  }
}
```

### Endpoint Check: `POST /api/v1/agents/trace`

```bash
curl -s -i -X POST "http://localhost:8000/api/v1/agents/trace" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "pkt_mean_to_max": 0.99,
      "tcp_flag_density": 0.95,
      "log_pkt_mean": 8.5,
      "log_pkt_max": 9.1
    },
    "model_name": "model_d2_coral"
  }'
```

**Response:**
```http
HTTP/1.1 200 OK
date: Wed, 04 Nov 2026 15:05:59 GMT
server: uvicorn
content-length: 3272
content-type: application/json
x-frame-options: DENY
x-content-type-options: nosniff
referrer-policy: strict-origin-when-cross-origin
permissions-policy: geolocation=(), camera=(), microphone=(), payment=(), usb=()
content-security-policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:; worker-src 'self' blob:; child-src 'self' blob:; frame-ancestors 'none'; object-src 'none'; base-uri 'self'; form-action 'self'
cache-control: no-store, no-cache, must-revalidate, max-age=0
pragma: no-cache
x-request-id: req-1d0c2510ea82

{
  "correlation_id": "flow-3c3d627c",
  "flow_status": "completed",
  "total_events": 8,
  "events": [
    {
      "event_id": "d8bcb4d1",
      "correlation_id": "flow-3c3d627c",
      "source_node": "api_gateway",
      "target_node": "message_bus",
      "event_type": "api_trigger",
      "timestamp": "2026-11-04T15:05:59.766775+00:00",
      "summary": "Received simulation request.",
      "payload": {}
    },
    {
      "event_id": "cdf94e84",
      "correlation_id": "flow-3c3d627c",
      "source_node": "message_bus",
      "target_node": "orchestrator",
      "event_type": "orchestrate",
      "timestamp": "2026-11-04T15:05:59.766775+00:00",
      "summary": "Orchestrator began execution.",
      "payload": {}
    },
    {
      "event_id": "ef7083ed",
      "correlation_id": "flow-3c3d627c",
      "source_node": "orchestrator",
      "target_node": "data_intelligence",
      "event_type": "agent_executed",
      "timestamp": "2026-11-04T15:05:59.772374+00:00",
      "summary": "DATA_INTELLIGENCE: SUCCESS — features: 4 total",
      "payload": {
        "stage": "DATA_INTELLIGENCE",
        "status": "SUCCESS",
        "duration_ms": 0.883,
        "input": "fields: 4 total",
        "output": "features: 4 total",
        "model_version": null,
        "error": null
      }
    },
    {
      "event_id": "30aab7ef",
      "correlation_id": "flow-3c3d627c",
      "source_node": "data_intelligence",
      "target_node": "threat_analysis",
      "event_type": "agent_executed",
      "timestamp": "2026-11-04T15:05:59.773295+00:00",
      "summary": "THREAT_ANALYSIS: SUCCESS — threat_level=low, confidence=0.3647",
      "payload": {
        "stage": "THREAT_ANALYSIS",
        "status": "SUCCESS",
        "duration_ms": 9.993,
        "input": "event_id=evt-20c98798, model=model_d2_coral",
        "output": "threat_level=low, confidence=0.3647",
        "model_version": "model_d2_coral",
        "error": null
      }
    },
    {
      "event_id": "6347a5c7",
      "correlation_id": "flow-3c3d627c",
      "source_node": "threat_analysis",
      "target_node": "explainability",
      "event_type": "agent_executed",
      "timestamp": "2026-11-04T15:05:59.786983+00:00",
      "summary": "EXPLAINABILITY: SUCCESS — top_feature=log_pkt_mean, impact=-1.3597",
      "payload": {
        "stage": "EXPLAINABILITY",
        "status": "SUCCESS",
        "duration_ms": 3.306,
        "input": "model=model_d2_coral",
        "output": "top_feature=log_pkt_mean, impact=-1.3597",
        "model_version": "model_d2_coral",
        "error": null
      }
    },
    {
      "event_id": "a1eea1e3",
      "correlation_id": "flow-3c3d627c",
      "source_node": "explainability",
      "target_node": "knowledge_context",
      "event_type": "agent_executed",
      "timestamp": "2026-11-04T15:05:59.790324+00:00",
      "summary": "KNOWLEDGE_CONTEXT: SUCCESS — mitre=0, cves=0, conf=0.00",
      "payload": {
        "stage": "KNOWLEDGE_CONTEXT",
        "status": "SUCCESS",
        "duration_ms": 1.553,
        "input": "attack_type=benign",
        "output": "mitre=0, cves=0, conf=0.00",
        "model_version": null,
        "error": null
      }
    },
    {
      "event_id": "ef97b3dc",
      "correlation_id": "flow-3c3d627c",
      "source_node": "knowledge_context",
      "target_node": "risk_prediction",
      "event_type": "agent_executed",
      "timestamp": "2026-11-04T15:05:59.791937+00:00",
      "summary": "RISK_PREDICTION: SUCCESS — risk=20, sev=LOW",
      "payload": {
        "stage": "RISK_PREDICTION",
        "status": "SUCCESS",
        "duration_ms": 1.505,
        "input": "threat=low",
        "output": "risk=20, sev=LOW",
        "model_version": null,
        "error": null
      }
    },
    {
      "event_id": "53e41ee6",
      "correlation_id": "flow-3c3d627c",
      "source_node": "risk_prediction",
      "target_node": "decision_support",
      "event_type": "agent_executed",
      "timestamp": "2026-11-04T15:05:59.793472+00:00",
      "summary": "DECISION_SUPPORT: SUCCESS — recs=1, pri=4",
      "payload": {
        "stage": "DECISION_SUPPORT",
        "status": "SUCCESS",
        "duration_ms": 1.019,
        "input": "risk=20",
        "output": "recs=1, pri=4",
        "model_version": null,
        "error": null
      }
    }
  ]
}
```

---

## 8. Continuous Integration Analysis (`.github/workflows/ci.yml`)

A thorough audit of `.github/workflows/ci.yml` reveals the following pipeline coverage:

### What CI Covers:

1. **Python Linting & Formatting:**
   - Runs `ruff check src/ tests/ configs/`
   - Runs `ruff format --check src/ tests/ configs/`
   - Runs `mypy src/argus/ --ignore-missing-imports` (Note: configured with `continue-on-error: true`).
2. **Backend Tests:**
   - Runs `pytest tests/ --tb=short -v` on Python 3.11 with `PYTHONPATH=src:tests:.`.
   - Runs `python scripts/verify_ui_numbers.py` to assert numerical integrity against `results/verified/`.
3. **Frontend Compilation & Auditing:**
   - Runs `npm ci` (Node 22)
   - Runs `npm audit --audit-level=high`
   - Runs `npm run build` (`tsc -b && vite build`)
4. **Container & Docker Validation:**
   - Runs `docker compose config -q`
   - Runs Docker Build smoke test with Buildx (`argus/detector-api:ci-test`)
   - Scans image with AquaSecurity Trivy (`CRITICAL,HIGH` severity, exit on failure)
5. **Security Scanning & SAST:**
   - Runs `pip-audit .` for vulnerable Python dependencies.
   - Runs `bandit -r src/ configs/ -ll -ii` (Bandit AST static analysis).
   - Runs `gitleaks` secret scanner (`gitleaks/gitleaks-action@v2`).
   - Runs dedicated security test suite (`pytest tests/security/ -v`).

### What CI Does NOT Cover:

1. **Frontend Linting (`npm run lint` / `oxlint`):**
   - CI runs `npm run build` and `npm audit`, but does **NOT** run `npm run lint` (which catches oxlint/eslint errors and warnings in frontend code).
2. **Playwright E2E Browser Testing:**
   - Tests exist under `web/e2e/smoke.spec.ts`, `web/e2e/monitor-min-n.spec.ts`, and `web/tests/e2e/smoke.spec.ts`, but Playwright is **never executed** in any CI job.
3. **Startup Asset Check (`scripts/startup_check.py`):**
   - CI runs `scripts/verify_ui_numbers.py` but skips `scripts/startup_check.py` (which verifies deserialization of all 5 production models and raw test parquets).
4. **Live API Server Smoke Tests (`make demo` / curl validation):**
   - CI does not execute a live end-to-end trace request (`/api/v1/agents/trace`) or check `/health` against a running Uvicorn daemon.
5. **Python Version Matrix Testing:**
   - CI exclusively pins `PYTHON_VERSION: '3.11'`. It does not test on Python 3.12 or 3.14 (the active local development environment).
6. **Enforced Type Checking:**
   - In `lint`, MyPy has `continue-on-error: true`, meaning type errors are surfaced in logs but will never fail the CI build.
