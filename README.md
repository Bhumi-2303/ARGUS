# ARGUS — Autonomous Risk-aware Grid Understanding & Security

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://python.org)
[![Backend Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Frontend Stack](https://img.shields.io/badge/Frontend-React%20%7C%20Vite%20%7C%20TailwindCSS-61DAFB.svg)](https://react.dev)
[![Test Suite](https://img.shields.io/badge/Tests-78%20Passing-success.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**ARGUS** is an AI-powered cybersecurity platform for Smart Grid Infrastructure (SCADA/ICS & IoT network telemetry) engineered to investigate and mitigate cross-domain transfer failure and representation collapse under strict zero-leakage protocols.

---

## 📌 Executive Summary & Key Research Findings

1. **Severe Cross-Domain Generalization Collapse**: Models trained on enterprise IoT traffic (**CICIoT2023 / D1**) achieve $>97\%$ in-domain F1, but collapse to near-chance or majority-class predictions when evaluated across domains on smart home IoT (**NF-ToN-IoT-v2 / D2**) and industrial SCADA (**IEC 60870-5-104 / D3**).
2. **Clean Class-Aware CORAL is the Leakage-Controlled Winner**:
   - Aligning class-conditional second-order statistics on target adaptation splits (without touching test labels) and calibrating decision thresholds ($\tau^* = 0.99$) on disjoint calibration splits achieves:
     - **Balanced Accuracy**: $71.09\%$
     - **Matthews Correlation Coefficient (MCC)**: $+0.3855$
     - **Precision**: $94.00\%$
     - **Specificity**: $91.43\%$
3. **Domain-Adversarial Neural Network (DANN) Degeneracy**:
   - Evaluated against raw prediction exports ($N = 2,627,177$), DANN achieves $\text{ROC-AUC} = 0.3321$ and $\text{Specificity} = 0.06\%$, demonstrating complete collapse into majority-class prediction rather than domain invariance.
4. **Representation Resolution Drives Transfer Feasibility**:
   - Extending compact 4-feature representations to SCADA traffic (D3) fails non-monotonically (an 8-feature representation collapses to $\text{ROC-AUC} = 0.445$).
   - Only D3's native 70-feature flow representation restores non-trivial discriminability ($\text{ROC-AUC} = 0.6744$).

---

## 📁 Repository Directory Layout

```text
argus/
├── README.md                 # Master project documentation & architecture guide
├── AUDIT.md                  # Comprehensive repository audit report
├── pyproject.toml            # Unified Python dependency specification & package config
├── Makefile                  # Build, test, and execution tasks
├── .gitignore                # Production git exclusion rules
├── configs/                  # System YAML configurations (paths, features, thresholds)
│   └── default.yaml
├── data/
│   ├── raw/                  # Heavy raw datasets (git-ignored)
│   ├── samples/              # Verified demo samples (ciciot.parquet, nfton.parquet)
│   └── reproduction/         # Forensic reproducibility scripts & audits
├── artifacts/
│   ├── models/               # Trained models (XGBoost, LightGBM, registry.yaml)
│   ├── transforms/           # CORAL covariance transformation matrices
│   └── day4/                 # Calibration and model fusion parameters
├── results/
│   ├── verified/             # Authoritative evaluation CSVs, JSON stats, & MANIFEST.md
│   └── diagnostic/           # Post-hoc exploratory & diagnostic ablation tables
├── src/argus/                # Production Python core package
│   ├── api/                  # FastAPI REST API routers (health, models, predict, shift, results)
│   ├── agents/               # Multi-agent orchestrators (threat analysis, risk, decision)
│   ├── data/                 # Data manager, test case suite, & domain metadata
│   ├── features/             # Harmonized 4-feature extraction & contracts
│   ├── models/               # Model loaders, booster wrappers, & predictors
│   ├── registry/             # Model registry & metadata catalog
│   ├── schemas/              # Pydantic v2 API schemas & contracts
│   └── shift/                # KS-statistic, PSI, and drift analytics engines
├── tests/                    # Comprehensive unit, integration, & metric assertion tests
├── web/                      # React 18 + Vite + TypeScript production frontend dashboard
│   ├── src/
│   │   ├── api/              # Strongly-typed API client connecting to FastAPI
│   │   ├── components/       # Shared UI components (AppShell, Card, ProvenanceBadge)
│   │   └── features/         # Application modules (Topology, Comparison, Shift, Analysis)
│   └── package.json
└── scripts/                  # Operational utility scripts (verification, data generation)
```

---

## 🚀 Getting Started

### 1. Installation & Environment Setup

Install ARGUS in editable mode using `pip`:

```bash
# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package in development mode
pip install -e .[dev,test]
```

### 2. Running the FastAPI Backend

Launch the backend API server:

```bash
uvicorn argus.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI Swagger docs will be accessible at `http://localhost:8000/docs`.

### 3. Running the Web Dashboard

In a separate terminal, launch the React development frontend:

```bash
cd web
npm install
npm run dev
```

The UI dashboard will run at `http://localhost:5173`, proxied directly to the FastAPI backend.

### 4. Running the Test Suite

Execute the full automated test suite (78 tests):

```bash
PYTHONPATH=.:src pytest
```

---

## 🌐 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health status, model loading checks, and readiness flags |
| `GET` | `/api/v1/models` | Available model metadata, calibrated decision thresholds ($\tau$), and provenance |
| `POST` | `/api/v1/predict` | Live inference for flow vectors; returns probability, binary prediction, and threshold |
| `GET` | `/api/v1/results/{table}` | Access verified benchmark tables (`five_model_complete_comparison`, `dann_final_test_metrics`, etc.) |
| `GET` | `/api/v1/shift` | Quantified KS drift statistics, PSI metrics, and feature distribution shift across domains |
| `GET` | `/api/v1/data/domains` | Dynamic domain configurations and empirical attack ratios loaded from verified test sets |
| `GET` | `/api/v1/data/test-cases` | Deterministic benchmark test cases for live pipeline verification |

---

## 📊 Authoritative Empirical Results

All experimental numbers backing the publication tables are preserved in [`results/verified/`](results/verified/):

### D1 (CICIoT2023) $\to$ D2 (NF-ToN-IoT-v2) Leakage-Controlled Comparison ($N = 2,627,177$)

| Model | $\tau$ | Accuracy | Precision | Recall | F1 | Bal. Acc. | Specificity | MCC | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Clean Class-Aware CORAL + XGBoost** | **0.99** | **0.6191** | **0.9400** | 0.5076 | 0.6592 | **0.7109** | **0.9143** | **+0.3855** | 0.5970 | **Verified Winner** |
| Source-Only XGBoost | 0.50 | 0.7207 | 0.7247 | 0.9919 | 0.8375 | 0.4972 | 0.0025 | -0.0311 | 0.3230 | Unadapted Baseline |
| Global CORAL + XGBoost | 0.50 | 0.6347 | 0.7013 | 0.8652 | 0.7747 | 0.4448 | 0.0244 | -0.1610 | 0.2852 | Marginal Alignment Only |
| DANN | 0.60 | 0.7259 | 0.7259 | 0.9998 | 0.8412 | 0.5002 | 0.0006 | +0.0129 | 0.3321 | Majority-Class Collapse |
| *Diagnostic Class-Aware CORAL* | *0.50* | *0.5506* | *0.7262* | *0.6113* | *0.6638* | *0.5006* | *0.3899* | *+0.0011* | *0.6361* | *Diagnostic (Used Target Test Labels)* |

See [`results/verified/MANIFEST.md`](results/verified/MANIFEST.md) for data lineage, cryptographic hashes, and methodology details.

---

## 🐳 Air-Gapped Production & OT Deployment

ARGUS is engineered for air-gapped industrial SCADA/OT network environments where external internet access is prohibited. The application builds into a self-contained multi-stage Docker container serving both compiled React SPA assets and the FastAPI inference engine:

```bash
# 1. Build self-contained image
docker compose build

# 2. Run container in isolated network without internet egress
docker compose up -d

# 3. Verify deployment health
python scripts/smoke_test_deployment.py
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
