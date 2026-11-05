# ARGUS — Comprehensive Existing Repository Architecture Audit

**Audit Date:** 2026-11-02  
**Auditor:** Senior Software Architect, Research Software Engineer, ML Infrastructure Engineer  
**Repository:** `/home/bhumi/GitHub/ARGUS`  
**Git Branch:** `v2-transformer-exploratory`  
**Working State:** Pre-Restructuring Audit & Governance Baseline  
**Total Inventory:** 4,403 files | 17.40 GB total footprint  

---

## Executive Summary

An exhaustive, non-destructive audit of the entire ARGUS codebase was conducted to evaluate its current structural organization, functional boundaries, research artifacts, dependencies, and technical debt. 

ARGUS represents a sophisticated multi-agent cybersecurity platform combined with an active academic research program investigating cross-domain generalization and representation collapse in network intrusion detection. However, rapid iterative development across multiple audit cycles (Phase 1 through Phase 4, P0 engineering remediation, P1-1 supervised baselines, P2 coordinate-generalization, P2.1 validation, P2.2 statistical robustness, and P2.3 adversarial reconciliation) has resulted in severe architectural entropy, root-level pollution, and fragmented documentation.

### Core Audit Statistics (from `repository_inventory.json`)
* **Total Cataloged Files:** 4,403 (17,399.79 MB total disk footprint)
* **Active Production & Research Files:** 1,193 (27.1%)
* **Historical Evidence Files:** 1,057 (24.0%)
* **Obsolete / Abandoned / Scratch Files:** 2,151 (48.9%)
* **Redundant Files:** 2 (<0.1%)
* **Action Breakdown:**
  * **Keep in Place:** 2,188 files (core source, active frontend, formal test suites, frozen research datasets)
  * **Archive / Relocate:** 2,206 files (historical scripts, diagnostic checkpoints, one-off patches, data audits)
  * **Consolidate & Bridge:** 2 files (duplicate Excel workbooks and symlinked model weights)
  * **Delete Candidates:** 7 items (stale `frontend/` build cache, empty `demo/backend`, ephemeral logs)

### Inventory Reconciliation & 19-Category Summary (Stage A.1 Resolution)
The repository inventory contains **exactly 4,403 cataloged files**. The earlier summary table of 4,148 files omitted 5 categories totaling 449 files (`archive`: 268, `results_data`: 68, `miscellaneous`: 48, `documentation`: 34, `model`: 31) while double-counting 194 files in `results/experiments/` (already present inside `research_experiment`: 800). The mathematical proof is exact: $4,403 - 449 + 194 = 4,148$ ($449 - 194 = 255$ files).

| Category Key | Files | Size (MB) | Role & Primary Locations |
|---|---:|---:|---|
| `scratch` | 2,113 | 436.85 | Diagnostic tasks, untracked caches, historical clone (`scratch/`, `scratch_argus_clone/`) |
| `research_experiment` | 800 | 48.72 | UDA/CORAL pipelines & modern research phases (`experiments/`, `results/experiments/`) |
| `data` | 417 | 15,221.14 | External flow matrices & samples (`data/raw/`, `dataset/`, `data/samples/`) |
| `archive` | 268 | 41.56 | Historical backups and audit reports (`archive/audits/`, `archive/backups/`) |
| `source_code` | 219 | 1.82 | Core multi-agent Python package (`src/argus/`) |
| `frontend` | 77 | 1.48 | Production React 19 + TypeScript + Vite SPA (`web/`) |
| `results_data` | 68 | 12.15 | Verified domain statistics and poster plot data (`results/verified/`, `results/poster_graph_data/`) |
| `utility_script` | 57 | 0.42 | Active runners, tools, and evaluation scripts (`scripts/`) |
| `test` | 56 | 0.38 | 283 unit, integration, and security tests (`tests/`, `src/**/tests/`) |
| `audit_report` | 54 | 1.18 | Master audit, P0 defect remediation, and P1–P2.3 verification (`audit/`, `ARGUS_INDEPENDENT_AUDIT/`) |
| `research_paper` | 54 | 3.52 | Academic manuscripts, REP01 exhibits, paper figures (`paper/`) |
| `miscellaneous` | 48 | 0.85 | Root loose files, root logs, and git metadata |
| `artifacts` | 45 | 12.80 | Production checkpoints and calibrated thresholds (`artifacts/models/`, `artifacts/transforms/`) |
| `documentation` | 34 | 0.65 | Architecture, API, and platform guides (`docs/`, root markdown) |
| `temporary_patch` | 31 | 0.08 | Single-turn string replacement scripts at root (`fix_*.py`, `patch_*.py`) |
| `model` | 31 | 14.12 | Production checkpoints and intermediate weights (`models/`, checkpoint dirs) |
| `config` | 14 | 0.04 | YAML system configs and Pydantic BaseSettings (`configs/`, `config/`) |
| `deployment` | 13 | 0.03 | Multi-container Dockerfiles and compose specs (`deployment/`, root Docker files) |
| `build_artifact` | 4 | 0.01 | Stale build outputs |
| **Total** | **4,403** | **17,399.79** | **Full Repository Inventory — 100% Mathematically Reconciled** |

---

## 1. Existing Directory Tree (Macro Level)

```text
ARGUS/
├── .git/                                # Git version control metadata
├── .github/workflows/ci.yml             # GitHub Actions CI/CD pipeline
├── .venv/                               # Python 3.14 virtual environment
├── ARGUS_ALL_RESEARCH_RESULTS.xlsx      # [DUPLICATE] Master research workbook (copy in results/)
├── ARGUS_INDEPENDENT_AUDIT/             # Master audit deliverables from Turn 1 (6 reports)
├── archive/                             # Existing historical archives (audits, backups, scripts)
├── artifacts/                           # Production deployment artifacts
│   ├── figures/                         # Historical figures (Day 1–4)
│   ├── metrics/                         # Historical metrics (Day 1–4)
│   ├── models/                          # Production models (D1, D2, D3, XGBoost source/adapted)
│   ├── reports/                         # Historical engineering reports
│   ├── thresholds/                      # Calibrated thresholds
│   └── transforms/                      # Feature transformers
├── audit/                               # Formal audit records
│   ├── architecture/                    # [NEW] Architectural audit & inventory
│   ├── p0/                              # P0 engineering defect remediation reports
│   └── research/                        # P1-1, P2, P2.1, P2.2, P2.3 research audit reports
├── config/                              # [ABANDONED] Contains only stale __pycache__
├── configs/                             # Production system YAML configs & settings.py
├── data/                                # Datasets, manifests, and misplaced audit notes
│   ├── interim/                         # Empty interim data directory
│   ├── processed/                       # Empty processed data directory
│   ├── raw/                             # Large raw datasets (legacy_package, ton_iot, ciciot)
│   ├── reproduction/                    # Historical reproduction notes
│   └── samples/                         # Verified demo flow samples
├── dataset/                             # Symlinked and cached datasets (parquet, zip, csv)
├── datasets -> dataset                  # Root-level convenience symlink
├── demo/backend/                        # [EMPTY] Unused directory
├── deployment/                          # Multi-container Docker deployment specs
│   ├── compose/                         # docker-compose specifications
│   └── docker/                          # Agent-specific Dockerfiles
├── docs/                                # Architecture, API, and platform documentation
│   ├── api/                             # API and event schemas
│   ├── architecture/                    # Master platform architecture & agent contracts
│   ├── deployment/                      # Deployment guides
│   ├── development/                     # Testing guides
│   ├── experiments/                     # Reproducibility audit
│   ├── frontend/                        # Frontend architecture documentation
│   └── research/                        # Data management documentation
├── experiment_execution/                # [REDUNDANT] Partial duplicate of experiments/execution
├── experiments/                         # Historical ML experiments (EXP01–EXP07, UDA, CORAL)
│   ├── ablations/                       # Phase 4 ablation scripts
│   ├── analysis/                        # Feature resolution studies
│   ├── domain_adaptation/               # Stage A–F CORAL & Stage 1–3 DANN scripts
│   ├── execution/                       # EXP01–EXP07 metrics, figures, reports
│   └── training/                        # Model trainers, notebooks, configs
├── frontend/                            # [OBSOLETE] Stale build cache from Sep 20 (node_modules/dist)
├── models/                              # [REDUNDANT] Duplicate model_d2_coral.txt & empty best_model/
├── paper/                               # Academic journal publication materials
│   ├── ARGUS_paper_v2_...docx           # Primary journal manuscript draft
│   ├── paper_text.txt                   # Plaintext transcript of paper
│   ├── ARGUS_Paper_Data/                # Figures, tables, deliverables for paper
│   └── experiments/journal_completion/  # Journal completion experiment scripts/metrics
├── prompts/                             # Decision support agent system prompts
├── reports/                             # Data governance audits & feasibility matrix
├── results/                             # Modern research experiment results & poster package
│   ├── ARGUS_ALL_RESEARCH_RESULTS.xlsx  # Authoritative master research workbook
│   ├── ARGUS_POSTER_DATA_PACKAGE/       # Poster graphs and deliverables
│   ├── experiments/                     # Modern research phases:
│   │   ├── p1_1_nfton_in_domain/        # P1-1 supervised reference baseline
│   │   ├── p2_coordinate_generalization/# P2 coordinate-generalization & ambiguity study
│   │   ├── p2_1_validation/             # P2.1 same-test-set cross-domain validation
│   │   ├── p2_2_robustness/             # P2.2 cluster bootstrap & multi-split sensitivity
│   │   └── p2_3_reconciliation/         # P2.3 adversarial reconciliation deliverables
│   ├── poster_figures/                  # Poster figures
│   ├── poster_graph_data/               # Poster plot data
│   ├── verification/                    # Historical verification runs
│   └── verified/                        # Verified metrics and domain statistics
├── scratch/                             # 100+ ad-hoc debug scripts and temporary data
├── scratch_argus_clone/                 # [OBSOLETE] Complete 2,000-file cloned repo snapshot from Sep 22
├── scratch_clone_tmp/                   # [EMPTY]
├── scratch_pip_cache/                   # [OBSOLETE] Ephemeral pip cache
├── scratch_tmp/                         # [EMPTY]
├── scripts/                             # Utility, evaluation, and research runner scripts
├── src/argus/                           # Core production Python package
│   ├── adaptation/                      # CORAL & Class-Aware CORAL algorithms
│   ├── agents/                          # 6 autonomous agents (DIA, TA, EA, KCA, RPA, DSA)
│   ├── api/                             # FastAPI application & routers
│   ├── auth/                            # OIDC, JWKS, JWT, and RBAC security
│   ├── blackboard/                      # Shared blackboard state synchronization
│   ├── bus/                             # In-memory asynchronous message bus
│   ├── core/                            # BaseAgent, BaseService, events, tracing
│   ├── data/                            # DataManager, flow simulation, telemetry parsing
│   ├── explain/                         # SHAP attribution helpers
│   ├── features/                        # Flow feature extraction
│   ├── models/                          # Model loader abstraction
│   ├── monitoring/                      # Distribution drift monitoring
│   ├── orchestrator/                    # Multi-agent execution pipeline & scheduler
│   ├── policy/                          # Fail-safe security policy engine
│   ├── registry/                        # ModelRegistry (loads D1, D2, D3, XGBoost)
│   ├── schemas/                         # Pydantic validation schemas
│   ├── security/                        # Rate limiting, error masking, security headers
│   ├── services/                        # Incident service & background agent services
│   └── v2_transformer/                  # Exploratory transformer group-token architecture
├── tests/                               # Test suite (271 directory tests / 283 full-root tests)
├── training/                            # [ABANDONED] Contains only empty __pycache__ and utils
├── verification/                        # Historical verification reports and training scripts
├── web/                                 # Production React 19 + TypeScript + Vite frontend SPA
└── [79 Root Files]                      # 31 patch scripts, 18 historical scripts, 8 root markdown files
```

---

## 2. File and Directory Inventory by Functional Category

### 2.1 Core Application Source (`src/argus/`)
* **File Count:** 219 files | **Status:** Active | **Ownership:** Engineering Team
* **Key Components:**
  * `agents/`: Autonomous agent definitions implementing Data Intelligence, Threat Analysis, Explainability, Knowledge Context, Risk Prediction, and Decision Support.
  * `api/`: FastAPI web application mounting endpoints for `/predict`, `/explain`, `/stream`, `/onboard`, and mounting the production SPA from `web/dist`.
  * `auth/` & `security/`: Production-grade security layer implementing fail-closed OIDC/JWKS authentication, RBAC, constant-time token comparison, rate limiting, and audit logging.
  * `orchestrator/`: Pipeline coordinator managing topological DAG execution, retries, and event tracing across agents.
  * `registry/`: `ModelRegistry` resolving model artifacts from `artifacts/models/`.
  * `data/`: `DataManager` handling flow streaming, telemetry parsing, and D3 native 73-feature mapping.
* **Health:** High. All modules import cleanly; 283/283 tests pass.

### 2.2 Production Frontend (`web/`)
* **File Count:** 77 files | **Status:** Active | **Ownership:** Frontend Engineering
* **Tech Stack:** React 19, TypeScript, Vite, TailwindCSS, Three.js / React Three Fiber (3D cyber topology visualization), ECharts, Lucide Icons.
* **Build Target:** Outputs compiled bundle to `web/dist`, which is served by FastAPI in production.
* **Health:** Builds cleanly (`npm run build`). Fully decoupled from backend source code.

### 2.3 Formal Test Suite (`tests/` and `src/**/tests/`)
* **File Count:** 56 test files (283 test functions) | **Status:** Active | **Ownership:** QA / Security
* **Breakdown:**
  * Root `tests/`: 271 passing tests covering security (OIDC, RBAC, path traversal, error masking, adversarial verification), E2E workflows, schemas, policy engine, and services.
  * Internal `src/argus/**/tests/`: 12 passing tests verifying agent pipelines and orchestrator DAG failure modes.
* **Health:** 100% pass rate (283 passed, 0 failed, 0 skipped).

### 2.4 Research Manuscripts & Publication Deliverables (`paper/`)
* **File Count:** 54 files | **Status:** Active Research | **Ownership:** Research Lead
* **Key Contents:**
  * `paper/ARGUS_paper_v2_representation_resolution.docx`: Authoritative journal paper manuscript.
  * `paper/paper_text.txt`: Plaintext transcript for NLP analysis and reference checks.
  * `paper/ARGUS_Paper_Data/`: Primary figures, tables, and REP01 replication deliverables.
  * `paper/experiments/journal_completion/`: Scripts, configs, and metrics specifically supporting journal paper submission.
* **Health:** Critical scientific asset. Must remain pristine and easily discoverable.

### 2.5 Modern Research Experiment Results (`results/experiments/`)
* **File Count:** 194 files | **Status:** Authoritative Research Evidence | **Ownership:** Research Team
* **Breakdown:**
  * `p1_1_nfton_in_domain/`: In-domain LightGBM and XGBoost baselines on NF-ToN-IoT-v2.
  * `p2_coordinate_generalization/`: Coordinate-disjoint partitioning, seen vs. unseen evaluation, and label ambiguity distributions.
  * `p2_1_validation/`: Same-test-set cross-domain evaluation comparing Clean CORAL, Global CORAL, DANN, and Disjoint Supervised models on $N = 1,970,428$ flows.
  * `p2_2_robustness/`: Cluster bootstrap ($K = 35,131$), 5-seed multi-split evaluation, D1-D2 conditional shift robustness, threshold transfer analysis.
  * `p2_3_reconciliation/`: Adversarial reconciliation manifests, cryptographic partition hashes, paired model bootstrap distributions, and test suite reconciliation.
* **Health:** Fully reproducible with cryptographic manifests.

### 2.6 Historical ML Experiments (`experiments/`)
* **File Count:** 800 files | **Status:** Historical Reference | **Ownership:** Research Team
* **Key Contents:**
  * `domain_adaptation/`: 6-stage CORAL pipeline and 3-stage DANN PyTorch training pipeline.
  * `execution/`: Historical experiments EXP01 through EXP07 (prior shift, cardinality, feature resolution).
  * `training/`: Scikit-learn, XGBoost, and LightGBM model trainers and feature aligners.
* **Health:** Functional historical archive. Should be preserved without disrupting paths.

### 2.7 Datasets & Data Governance (`data/` and `dataset/`)
* **File Count:** 417 files (15.2 GB) | **Status:** Managed Data Assets | **Ownership:** Data Engineering
* **Key Contents:**
  * `data/raw/legacy_package/argus_coral_data/`: Gigabyte-scale CSV feature matrices for CIC-IoT-2023 and NF-ToN-IoT-v2 (2.8 GB).
  * `data/samples/`: Verified sample flows for API demonstration.
  * `dataset/`: Parquet representations (`ciciot.parquet`, `nfton.parquet`) and download archives.
* **Health:** Stable. External large files must remain in place to avoid bloating Git history.

### 2.8 Audit Documentation (`audit/` and `ARGUS_INDEPENDENT_AUDIT/`)
* **File Count:** 54 files | **Status:** Quality Assurance & Verification Records | **Ownership:** Auditor
* **Breakdown:**
  * `ARGUS_INDEPENDENT_AUDIT/`: Turn 1 comprehensive audit reports (Master report, evidence register, gap analysis, roadmap).
  * `audit/p0/`: P0 defect remediation reports, file changelogs, test evidence, and closure review.
  * `audit/research/`: P1-1, P2, P2.1, P2.2, and P2.3 scientific verification reports.
  * `audit/architecture/`: [This Audit] Existing repository audit, machine-readable inventory, and target architecture.
* **Health:** High evidentiary value. Needs consolidation under a single `audit/` hierarchy.

---

## 3. Duplicate and Redundant File Analysis

The audit identified significant structural redundancy that confuses developers and researchers:

| Redundant Artifact | Location 1 (Authoritative) | Location 2 (Redundant / Stale) | Finding & Recommendation |
|---|---|---|---|
| **Master Research Excel** | `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx` | `ARGUS_ALL_RESEARCH_RESULTS.xlsx` (Root) | Exact duplicate (75,463 bytes, SHA-256 `f4ddc451...`, 17 sheets). Generated by `scripts/generate_master_research_excel.py` lines 20-21. Consolidate into `results/`; link root copy. |
| **Model D2 CORAL** | `artifacts/models/model_d2_coral.txt` | `models/model_d2_coral.txt` | Exact duplicate (713,743 bytes, SHA-256 `c71055c8...`). `artifacts/models/` is actively loaded by `ModelRegistry`, while `models/` is referenced by `docker-compose.yml:82`, `detector.Dockerfile:30`, and `scripts/start_local.sh:27`. Retain `artifacts/models/` as primary; establish a relative symlink from `models/` to avoid breaking container and startup scripts. |
| **Stale Frontend Build** | `web/` (Active React 19 app) | `frontend/` (Stale Sep 20 build) | `frontend/` contains only `dist`, `node_modules`, and `tsconfig.tsbuildinfo` from an abandoned build. Safely remove. |
| **Neural Robustness Audit** | `experiments/execution/neural_robustness/` | `experiment_execution/neural_robustness/` | Redundant folder copy. Consolidate into `experiments/execution/`. |
| **Empty Directories** | — | `demo/backend/`, `config/`, `scratch_clone_tmp/`, `scratch_tmp/`, `models/best_model/` | Empty or contains only `__pycache__`. Prune safely. |
| **Cloned Repo Snapshot** | Root workspace | `scratch_argus_clone/` (23,807 files, 1.60 GB) | Untracked Git clone from Sep 22. All 10 files referenced by `generate_master_research_excel.py` already exist identically in `experiments/execution/` and `archive/audits/`. Do NOT move to tracked Git archive (would bloat git history by 1.6 GB). Exclude via `.gitignore` and archive externally. |
| **Tracked Scratch Evidence** | Root workspace | `scratch/` (383 files, 387.52 MB, 296 tracked) | Contains 21 `.pt` PyTorch checkpoints, 60 `.csv` datasets, 41 `.png` figures, and 125 diagnostic scripts tracked in Git. Relocate tracked evidence to `archive/experiments/diagnostic_tasks/` and `archive/scripts/scratch/` via `git mv`. Move sample data `data_32.csv` to `data/raw/bot_iot/`. Retain `scratch/` in `.gitignore` as ephemeral workspace. |
| **Pip Cache** | Root workspace | `scratch_pip_cache/` (599 files, 599.42 MB) | Untracked wheel cache. Prune local disk; retain in `.gitignore`. |
| **Misplaced Data Audits** | `audit/` | 12 `ARGUS_*_20260925_*.md` files in `data/` | Audit reports dumped in the data folder. Relocate to `audit/historical/data_audits/`. |

---

## 4. Root Directory Clutter Analysis

The repository root currently contains **79 scattered files** that obscure the primary project entry points:

### 4.1 Temporary Patch Scripts (31 files — 0 references across codebase)
* Examples: `fix_demo_page.py`, `fix_monitor.py`, `fix_onboard.py`, `fix_overview.py`, `fix_simulate_flow.py`, `fix_topbar.py`, `fix_ts.py`, `patch_cards.py`, `patch_chart.py`, `patch_legend.py`, `patch_live_monitor_card.py`, `patch_mc.py`, `patch_meta.py`, `patch_overview.py`, `patch_registry.py`, `patch_reset.py`, `patch_so.py`, `patch_verify.py`.
* **Finding:** These are one-off, single-turn string replacement utilities executed during prior fixes. They are never imported or invoked by CI/CD, tests, or application logic.
* **Recommendation:** Relocate to `archive/scripts/patches/`.

### 4.2 Historical Experiment Runners (6 shell scripts)
* Examples: `run_all_experiments.sh`, `run_multiseed.sh`, `run_multiseed_fast.sh`, `run_multiseed_fast2.sh`, `run_multiseed_final.sh`, `wait_for_all.sh`.
* **Finding:** Superseded by modular scripts in `scripts/` and `results/experiments/`.
* **Recommendation:** Relocate to `archive/scripts/experiment_runners/`.

### 4.3 Historical One-Off Evaluation Scripts (18 Python scripts)
* Examples: `compute_entropy.py`, `compute_shap.py`, `evaluate_agent_contribution.py`, `evaluate_risk.py`, `generate_d1_d2_baselines.py`, `generate_figures.py`, `generate_final_report.py`, `generate_poster.py`, `investigate_fpr.py`, `test_e2e_local.py`, `test_load.py`.
* **Finding:** Historical evaluation scripts from Day 1–4, referenced only in historical audit text.
* **Recommendation:** Relocate to `archive/scripts/root_scripts/`.

### 4.4 Scattered Root Markdown Files (8 files)
* Examples: `AUDIT.md`, `BOT_IOT_COLLAPSE_ANALYSIS.md`, `DEMO.md`, `DRY_RUN_PLAN.md`, `FEATURE_V1_5_VALIDATION.md`, `FOLLOWUP_AUDIT.md`, `LIVE_CHECK.md`, `SCHEMA_AUDIT.md`, `V1_5_PAIRWISE_CHECK.md`.
* **Recommendation:** Relocate to `audit/historical/`.

---

## 5. Dependency & Path Analysis

Before executing any structural reorganization, critical runtime dependencies were audited:

### 5.1 Python Package and Imports
* `pyproject.toml` defines package root as `packages = ["src/argus"]`.
* All internal imports use absolute package references: `from argus.core.base_agent import BaseAgent`, `from argus.registry.model_registry import ModelRegistry`.
* Moving non-`src` directories will **NOT** break internal Python package imports.

### 5.2 Model Loading Paths (`ModelRegistry`)
* `src/argus/registry/model_registry.py` lines 47–116 hardcode:
  * `artifacts/models/model_d1_baseline.txt`
  * `artifacts/models/model_d2_coral.txt`
  * `artifacts/models/model_d3_native.txt`
  * `artifacts/models/xgb_source.json`
  * `artifacts/models/xgb_adapted.json`
* **Non-Negotiable Rule:** `artifacts/models/` must remain in place or have symlink fallbacks to prevent breaking live model inference.

### 5.3 Frontend SPA Static Mount
* `src/argus/api/main.py` lines 406–407 mount:
  * `os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../web/dist"))`
* **Non-Negotiable Rule:** `web/` must remain at the repository root (or be symlinked) to ensure the FastAPI production container and local dev server continue serving the SPA without route failure.

### 5.4 Docker & CI/CD Expectations
* `Dockerfile` explicitly copies: `COPY src/ ./src/`, `COPY configs/ ./configs/`, `COPY artifacts/ ./artifacts/`, `COPY results/ ./results/`, `COPY data/ ./data/`, `COPY prompts/ ./prompts/`, `COPY --from=frontend-builder /web/dist ./web/dist`.
* `.github/workflows/ci.yml` runs:
  * `pytest tests/` with `PYTHONPATH: src:tests:.`
  * `python scripts/verify_ui_numbers.py`
  * `cd web && npm run build`
* **Non-Negotiable Rule:** Core top-level directories (`src/`, `web/`, `tests/`, `configs/`, `artifacts/`, `results/`, `data/`) must remain operational.

---

## 6. Key Architectural Risks & Mitigation Strategies

| Risk Identified | Potential Impact | Architectural Mitigation Strategy |
|---|---|---|
| **Model Path Breakage** | API inference fails if model checkpoints are relocated. | Keep `artifacts/models/` as the primary operational model directory; use symlinks if consolidated. |
| **Static SPA Mount Failure** | FastAPI raises 404 on frontend assets if `web/dist` moves. | Retain `web/` at root; do not rename to `application/frontend/` without updating `main.py` and Dockerfile. |
| **CI/CD Pipeline Failure** | GitHub Actions fails linting, testing, or building. | Ensure `.github/workflows/ci.yml` commands remain 100% valid. Verify with local CI simulation. |
| **Reproducibility Manifest Invalidation** | SHA-256 manifests fail if results or scripts are altered. | Keep `results/experiments/` untouched; preserve all P1/P2 script filenames in `scripts/`. |
| **Git Bloat from Large Datasets** | Moving `data/raw/` could accidentally stage gigabytes of binary CSVs into Git. | Explicitly verify `.gitignore` excludes large CSVs; never move `data/raw/` into tracked space. |

---

## 7. Recommended Target Architecture

The target architecture organizes ARGUS into clean, discoverable functional domains while preserving operational stability:

```text
ARGUS/
├── README.md                            # Comprehensive, professional project overview
├── CONTRIBUTING.md                      # Code & research contribution guidelines
├── LICENSE                              # MIT License
├── Makefile                             # Unified dev workflow commands
├── pyproject.toml                       # Python package specification & test config
├── uv.lock                              # Deterministic dependency lockfile
├── Dockerfile                           # Multi-stage hardened production container
├── docker-compose.yml                   # Service composition specification
├── .gitignore                           # Git exclusion rules
│
├── src/                                 # [CORE PLATFORM] Production Python Package
│   └── argus/                           # Unaltered modular architecture (agents, api, auth, etc.)
│
├── web/                                 # [FRONTEND] React 19 + TypeScript + Vite SPA
│   ├── src/                             # UI components, 3D topology, hooks, stores
│   ├── public/                          # Static assets
│   ├── package.json                     # Node.js dependencies
│   └── vite.config.ts                   # Bundler configuration
│
├── paper/                               # [RESEARCH PUBLICATIONS] Academic Manuscripts & Exhibits
│   ├── manuscripts/                     # Word/docx & text manuscript drafts
│   ├── data/                            # Figures, tables, and REP01 replication exhibits
│   └── experiments/                     # Journal completion experimental scripts & metrics
│
├── results/                             # [SCIENTIFIC EVIDENCE] Recomputed Metrics & Deliverables
│   ├── experiments/                     # Modern research phases (P1-1, P2, P2.1, P2.2, P2.3)
│   ├── master/                          # Master Excel workbook (ARGUS_ALL_RESEARCH_RESULTS.xlsx)
│   ├── poster/                          # Poster figures, tables, and summaries
│   └── verified/                        # Verified domain statistics and threshold sweeps
│
├── experiments/                         # [EXPERIMENT ARCHIVE] Historical Benchmarks & UDA
│   ├── domain_adaptation/               # CORAL & DANN adaptation pipelines
│   ├── execution/                       # EXP01–EXP07 benchmarks
│   └── training/                        # Model trainers, hyperparameter tuning
│
├── data/                                # [DATA ASSETS] Raw, Processed, and Sample Datasets
│   ├── raw/                             # Large external datasets (CIC-IoT, NF-ToN, HAI, BoT-IoT)
│   ├── samples/                         # Verified demo flow samples
│   ├── manifests/                       # Dataset manifests and checksums
│   └── dataset/                         # Parquet formats & download archives
│
├── artifacts/                           # [RUNTIME ARTIFACTS] Production Checkpoints & Transformers
│   ├── models/                          # Active LightGBM and XGBoost checkpoints & registry.yaml
│   ├── thresholds/                      # Operational decision thresholds
│   └── transforms/                      # Flow normalization parameters
│
├── configs/                             # [CONFIGURATION] Production System Settings
│   ├── settings.py                      # Pydantic BaseSettings platform configuration
│   └── *.yaml                           # Agents, security, logging, feature flags
│
├── scripts/                             # [OPERATIONAL SCRIPTS] Verified Runners & Utilities
│   ├── research/                        # Active P1/P2 experiment runners & validation tools
│   ├── demo/                            # Live demonstration and stream simulation scripts
│   └── maintenance/                     # Seed scripts, health checks, dataset downloaders
│
├── tests/                               # [TEST SUITES] 283 Full-Project Tests
│   ├── unit/                            # Unit tests for core logic, registry, D3 inference
│   ├── integration/                     # Pipeline integration and agent coordination
│   ├── security/                        # OIDC, RBAC, path traversal, error masking
│   └── e2e/                             # End-to-end security incident lifecycle tests
│
├── audit/                               # [INDEPENDENT AUDITS] Evidentiary Verification Records
│   ├── architecture/                    # Repository audits, target specs, inventory JSON
│   ├── independent/                     # Turn 1 master audit reports (Turn 1 deliverables)
│   ├── p0/                              # P0 engineering defect remediation & closure
│   ├── research/                        # P1-1, P2, P2.1, P2.2, P2.3 research reports
│   └── historical/                      # Consolidated historical audits from root & data/
│
├── docs/                                # [DOCUMENTATION] Engineering & System Guides
│   ├── PROJECT_STRUCTURE.md             # Guide to directory layout and ownership
│   ├── ARCHITECTURE.md                  # Software and multi-agent system architecture
│   ├── RESEARCH_OVERVIEW.md             # Research questions, datasets, and benchmark status
│   └── ...                              # API schemas, security policies, threat models
│
└── archive/                             # [ARCHIVED ARTIFACTS] Retired Scripts, Patches, & Clones
    ├── scripts/                         # Retired patch scripts, one-off tools, root scripts
    ├── scratch/                         # Previous scratch scripts and cloned repo snapshot
    └── docs_history/                    # Historical restructuring checklists and moves
```

---

## 8. Summary Audit Conclusion

The audit demonstrates that the core ARGUS platform (`src/argus`), active frontend (`web`), modern research experiments (`results/experiments`), and formal test suite (`tests`) are **sound, high-performing, and fully functional**. 

The primary problems are structural:
1. 79 loose files polluting the root directory.
2. An obsolete 2,100-file cloned repository inside `scratch_argus_clone/`.
3. Stale build directories (`frontend/`).
4. Misplaced audit files dumped into `data/`.
5. Duplication between root files and subdirectories (`ARGUS_ALL_RESEARCH_RESULTS.xlsx`, `models/model_d2_coral.txt`).

**Stage A is complete.** The machine-readable inventory has been generated at [`audit/architecture/repository_inventory.json`](file:///home/bhumi/GitHub/ARGUS/audit/architecture/repository_inventory.json). The migration plan is documented in [`audit/architecture/TARGET_ARCHITECTURE.md`](file:///home/bhumi/GitHub/ARGUS/audit/architecture/TARGET_ARCHITECTURE.md).

No files have been moved, deleted, or renamed. Awaiting user approval to proceed with Stage B (Safe Incremental Migration).
