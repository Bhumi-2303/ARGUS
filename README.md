# ARGUS — Autonomous Risk-aware Grid Understanding & Security

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https.python.org)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

ARGUS is an AI-powered cybersecurity platform for Smart Grid Infrastructure (SCADA/ICS & IoT telemetry) designed to investigate and mitigate cross-domain transfer failure and representation collapse.

---

## 📁 Repository Directory Layout

```text
argus/
├── README.md                 # Master project documentation & guide
├── AUDIT.md                  # Comprehensive repository audit report
├── pyproject.toml            # Single dependency source & package build config
├── Makefile                  # Build & execution automation tasks
├── .gitignore                # Git exclusion rules
├── configs/                  # System YAML configurations (paths, features, thresholds)
│   └── default.yaml
├── data/
│   ├── raw/                  # Untouched raw dataset storage (git-ignored)
│   └── samples/              # Stratified demo samples
├── artifacts/
│   ├── models/               # Trained GBDT (XGBoost, LightGBM) and DANN checkpoints
│   ├── transforms/           # Serialized CORAL covariance transformation parameters
│   └── thresholds/           # Frozen threshold sweep metadata & calibration curves
├── results/
│   ├── verified/             # Authoritative evaluation CSVs (one per table) + MANIFEST.md
│   └── diagnostic/           # Post-hoc & diagnostic evaluation outputs
├── src/argus/                # Production Python package
│   ├── features/             # Harmonized 4-feature extraction implementation
│   ├── models/               # Model loader & inference predictor wrappers
│   ├── adaptation/           # Domain adaptation engines (CORAL, Class-Aware CORAL, DANN)
│   ├── shift/                # Domain shift analytics (KS-test, PSI, domain classifiers)
│   ├── explain/              # SHAP attribution & explainability helpers
│   ├── orchestrator/         # Asyncio multi-agent orchestrator engine
│   └── api/                  # FastAPI REST server & router endpoints
├── experiments/              # Executable research experiment scripts & harnesses
├── web/                      # Web frontend interface (under construction)
├── tests/                    # Unit and integration test suite
├── paper/                    # Academic manuscript drafts & publication assets
└── archive/                  # Legacy scripts, old reports, and archived Streamlit frontend
    └── README.md             # Inventory of archived items & Streamlit UI features list
```

---

## 🚀 Getting Started

### 1. Installation & Environment Setup

Install ARGUS in editable mode using `pip` or `uv`:

```bash
# Using Makefile
make setup

# Or directly using pip
pip install -e .[dev,test]
```

Verify the installation:

```bash
make demo
# Or: python -c "import argus; print(argus.__version__)"
```

### 2. Running the FastAPI Backend

Launch the development API server:

```bash
make api
```

The API will be available at `http://localhost:8000` with interactive OpenAPI documentation at `http://localhost:8000/docs`.

### 3. Running Tests

Run the unit and integration test suite:

```bash
make test
```

---

## 📊 Empirical Data & Results Provenance

All authoritative experimental results backing the manuscript tables are preserved in [`results/verified/`](results/verified/):
- **`five_model_complete_comparison.csv`**: Master D1→D2 benchmark table comparing Source-only XGBoost, Global CORAL, Diagnostic Class-aware CORAL, Clean Class-aware CORAL, and DANN.
- **`dann_final_test_metrics.csv`**: Bit-for-bit verified performance metrics for the DANN model ($\text{ROC-AUC} = 0.3321$).
- **`d3_native_threshold_sweep.csv`**: Operational decision threshold curves for Domain 3 SCADA traffic.
- **`SHAP_vs_Target_Gain.csv`**: Quantified SHAP explainability disconnect between source importance and target gain.

See [`results/verified/MANIFEST.md`](results/verified/MANIFEST.md) for full protocol details.

---

## 🐳 Production & Air-Gapped OT Deployment

ARGUS is engineered for air-gapped SCADA/OT network environments where zero external internet access is permitted. All compiled React static assets, verified model artifacts, and sample datasets are self-contained in a single production Docker container.

### 1. Local & Air-Gapped Docker Deployment

Build the multi-stage image online, then deploy in an isolated/air-gapped network with zero network egress:

```bash
# Copy and configure environment variables
cp .env.example .env

# Build production multi-stage Docker image
docker compose build

# Run in an isolated network without internet egress
docker compose up -d

# Run deployment smoke test suite
python scripts/smoke_test_deployment.py
```

The application will be live at `http://localhost:8000` with the React SPA frontend served directly from FastAPI.

### 2. Configuration & Modes (`.env`)

- **`ARGUS_MODE=demo`**: Seeded deterministic flow replay harness.
- **`ARGUS_MODE=production`**: Production mode expecting a live SCADA OT feed adapter.
- **`ARGUS_PORT=8000`**: Custom HTTP port binding.
- **`ARGUS_ALLOWED_ORIGINS`**: Locked CORS allowed origins list.

### 3. Optional Cloud Deployment (Fly.io / Render / VMs)

The self-contained Docker image can optionally be deployed to cloud platforms or edge VMs:

```bash
# Deploy to Fly.io
fly launch --dockerfile Dockerfile

# Or deploy to Render / AWS ECS / Azure Container Instances using the multi-stage Dockerfile
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

