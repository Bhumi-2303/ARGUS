# ARGUS Project Directory Structure (`docs/PROJECT_STRUCTURE.md`)

This document provides a comprehensive structural reference for the ARGUS repository. It details the purpose, ownership, and contents of each top-level directory and explains how the software engineering system interacts with the empirical scientific research artifacts.

---

## 1. Top-Level Repository Overview

```text
ARGUS/
├── .github/                       # GitHub Actions workflows and CI/CD pipelines
├── artifacts/                     # Cryptographically verified model weights and manifests
├── audit/                         # Restructuring audit reports, verification trails, and release reviews
├── configs/                       # Platform runtime configurations, agent settings, and paths
├── dataset/                       # Curated sample flows, Parquet datasets, and data catalogs
├── docs/                          # Architecture guides, research manuals, setup, and security docs
├── experiments/                   # Research experiment configs, execution outputs, and scaling runs
├── paper/                         # Academic publication layer (manuscript, tables, figures, bibliography)
├── results/                       # Authoritative benchmarks, master research Excel, verified metrics
├── scripts/                       # Operational tools, demo runners, verification utilities
├── src/argus/                     # Production Python package (FastAPI backend & multi-agent pipeline)
├── tests/                         # Full automated pytest test suite (unit, integration, security, e2e)
├── web/                           # Production React 19 + TypeScript + Three.js frontend
├── CONTRIBUTING.md                 # Developer contribution guidelines and quality gates
├── LICENSE                        # MIT open-source license
├── Makefile                       # Unified make targets (demo, test, lint, build)
├── pyproject.toml                 # Package dependencies, optional extras, and build settings
└── README.md                      # Central landing page and executive summary
```

---

## 2. Directory Deep-Dive

### `src/argus/` — Production Backend & Agentic Platform
Contains the production Python codebase implementing the autonomous multi-agent defense system.

- **`agents/`**: Implementations of the six autonomous sequential agents:
  - `data_intelligence.py` (`DIA`): Telemetry schema validation and 4-feature extraction.
  - `threat_analysis.py` (`TAA`): Domain-adapted model inference and calibrated thresholding.
  - `explainability.py` (`EA`): Exact TreeSHAP feature attributions and ranking.
  - `knowledge_context.py` (`KCA`): MITRE ATT&CK for ICS and CISA CVE contextualization.
  - `risk_prediction.py` (`RPA`): Multi-factor ICS operational risk scoring ($0\text{--}100$).
  - `decision_support.py` (`DSA`): Deterministic mitigation playbooks and approval workflows.
- **`orchestrator/`**: Sequential pipeline execution engine managing the shared `PipelineContext`. Handles error propagation and agent skip logic.
- **`api/`**: FastAPI v1 REST and WebSocket routes:
  - `/api/v1/agents/trace`: Executes full real 6-agent sequential pipeline on flow telemetry.
  - `/api/v1/models/`: Model registry status, supported features, and health checks.
  - `/api/v1/shift/`: Real-time Kolmogorov-Smirnov and PSI distribution shift analysis.
  - `/ws/telemetry`: Streaming SCADA and IoT telemetry WebSocket.
- **`registry/`**: `ModelRegistry` catalog managing executable models (`model_d1_baseline`, `model_d2_coral`, `model_d3_native`, `xgb_source`, `xgb_adapted`), feature definitions (`D3_NATIVE_FEATURES`, 73 features), and offline research status.
- **`security/`**: Defensive middleware, Content Security Policy (CSP), OWASP HTTP headers, and CORS restrictions.
- **`auth/`**: Role-Based Access Control (RBAC), JWT validation, and security audit loggers.
- **`shift/`**: Distribution drift estimators (two-sample KS-test, Population Stability Index).

---

### `web/` — Production Frontend Dashboard
Modern single-page application built with React 19, TypeScript, TailwindCSS, and Three.js / React Three Fiber.

- **`src/features/topology/`**: Interactive 3D WebGL / 2D SVG canvas rendering the multi-agent graph (10 nodes, 8 edges). Features real-time flow execution animations and WebSocket telemetry traces.
- **`src/features/analysis/`**: Telemetry inspection and live prediction interface. Supports drag-and-drop flow CSV ingestion and instant multi-agent execution.
- **`src/features/explain/`**: TreeSHAP feature importance beeswarms, force plots, and source vs target attribution comparison.
- **`src/features/results/`**: Ground-truth evaluation tables, ROC-AUC comparison curves, and domain shift metrics.
- **`src/features/overview/`**: Executive summary, research methodology, transfer failure explanations, and architectural blueprints.
- **`dist/`**: Compiled, optimized static bundle served directly by the FastAPI backend on `http://localhost:8000`.

---

### `artifacts/` — Verified Model Weights & Manifests
Storage for binary model artifacts, scalers, and integrity metadata.

- **`models/`**:
  - `model_d1_baseline.json`: XGBoost baseline model trained on D1 (CICIoT2023).
  - `model_d2_coral.json`: XGBoost model adapted to D2 via Class-Aware CORAL ($\tau^* = 0.99$).
  - `model_d3_native.txt`: Native SCADA LightGBM booster with 73 native features.
  - `xgb_source.json`, `xgb_adapted.json`: Baseline and adapted comparison models.
  - `INTEGRITY_MANIFEST.json`: Cryptographic SHA-256 manifest checked at server startup.

---

### `paper/` — Academic Research & Publication Layer
Houses the academic research paper materials, traceable tables, publication figures, and manuscript source files.

- **`manuscripts/`**: Manuscript text files (`paper_text.txt`, Word DOCX transcripts).
- **`tables/`**: Publication CSV tables and indices:
  - `TABLE_INDEX.md`: Central catalog with descriptions and evidence tiers.
  - `Table_I_Domains_And_Profiles.csv`: Dataset characteristics and class balance.
  - `Table_II_Partition_Sizes_And_Balance.csv`: Observation pool accounting ($13,135,881$ total).
  - `Table_III_Bidirectional_D1_D2_Cross_Domain.csv`: In-domain vs cross-domain transfer metrics.
  - `Table_IV_Random_Row_Domain_Adaptation.csv`: D1 $\to$ D2 domain adaptation benchmark ($N=2,627,177$).
  - `Table_IV_Leakage_Controlled_Domain_Adaptation.csv`: Backwards-compatible symlink.
  - `Table_V_Feature_Resolution_Scaling.csv`: Representation resolution sweep ($4, 6, 8, 73$ features).
  - `Table_VI_Operational_Performance_FPR_Budgets.csv`: Attack recall under strict FPR constraints.
- **`figures/`**: Publication figures organized into high-res PNG and vector SVG/PDF formats:
  - `FIGURE_INDEX.md`: Master catalog with SHA-256 hashes and evidence tiers (Tier 1 Empirical, Tier 3 Illustrative).
  - `architecture/`: Multi-agent system architecture and evaluation pipeline schematics.
  - `methodology/`: Feature harmonization and CORAL covariance alignment diagrams.
  - `system_implementation/`: Live SOC interface screenshots.
  - `experimental_results/`: 137 empirical plots across 10 analytical sections.
- **`PUBLICATION_TRACEABILITY.md`**: Formal 7-link lineage matrix mapping every table and figure to its underlying script, configuration, dataset, and raw prediction file.
- **`RESEARCH_SUPERVISOR_HANDOFF.md`**: Guide for academic advisors and independent auditors.

---

### `results/` — Authoritative Research Metrics
- **`ARGUS_ALL_RESEARCH_RESULTS.xlsx`**: Authoritative master workbook containing 17 worksheets with all historical and validated research metrics (SHA-256 `f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1`).
- **`verified/`**: Canonical CSV exports backing publication tables and model registry validation.
- **`experiments/`**: Detailed validation outputs for Phase 1 (in-domain), Phase 2 (coordinate generalization), Phase 2.1 (UDA comparison), Phase 2.2 (robustness), and Phase 2.3 (coordinate reconciliation).

---

### `experiments/` — Research Experiment Configurations & Runs
Structured experimental infrastructure for reproducing specific research milestones:
- `configs/`: YAML experiment definitions.
- `domain_adaptation/`: CORAL and DANN adaptation pipelines.
- `execution/`: Neural robustness benchmarks, feature resolution sweeps, and operational sweeps.
- `feature_scaling/`: Resolution experiments investigating ARGUS-4, ARGUS-6, ARGUS-8, and native representations.

---

### `dataset/` — Centralized Datasets & Telemetry Samples
- `sample_attack_flow.csv`: Curated malicious flow for interactive UI testing.
- `sample_benign_flow.csv`: Normal operational flow for baseline validation.
- `ciciot.parquet`: 10,000 verified flows from CICIoT2023 (D1).
- `nfton.parquet`: 10,000 verified flows from NF-ToN-IoT-v2 (D2).
- `README.md`: Dataset usage and schema documentation.

---

### `audit/` — Forensic Reports & Restructuring History
- `BATCH_7_FINAL_RELEASE_READINESS_REPORT.md`: Comprehensive final release readiness report.
- Stage-by-stage restructuring reports for Batches 1 through 6.
- Architecture audits, dependency audits, and coordinate generalization reconciliation logs.

---

### `tests/` — Automated Testing Suite
- `unit/`: Unit tests for model registry, Pydantic schemas, and agents.
- `e2e/`: End-to-end integration tests executing genuine 6-agent inference.
- `security/`: HTTP security headers, CORS origins, and RBAC permission checks.
- `agents/`: Dedicated test suites for each individual agent.
