# ARGUS — Target Repository Architecture & Migration Plan

**Document Version:** 1.0.0  
**Status:** PROPOSED (Stage A Complete — Awaiting Approval for Stage B Migration)  
**Author:** Senior Software Architect, Research Software Engineer, ML Infrastructure Engineer  
**Target Repository:** `/home/bhumi/GitHub/ARGUS`  

---

## 1. Architectural Philosophy & Design Principles

The ARGUS repository restructuring transforms a cluttered, multi-phase research codebase into an enterprise-grade academic research and production software platform.

### Core Principles
1. **Zero Runtime Disruption:** Core application modules (`src/argus`), active frontend (`web`), operational model weights (`artifacts/models`), and test suites (`tests`) retain full runtime compatibility.
2. **Absolute Scientific Integrity:** No experimental metrics, prediction parquet files, dataset checksums, or paper drafts are modified, deleted, or falsified.
3. **Clear Separation of Concerns:**
   * **Production Platform:** `src/argus` (backend), `web` (frontend), `configs` (settings), `deployment` (Docker).
   * **Scientific Evidence:** `results/experiments` (modern P1/P2 phases), `experiments` (historical benchmarks), `results/master` (master workbook).
   * **Research Publications:** `paper` (manuscript, figures, replication exhibits).
   * **Data Governance:** `data` (raw large data, sample flows, manifests).
   * **Quality Assurance:** `tests` (formal test suites), `audit` (all engineering and research audit records).
   * **Documentation:** `docs` (developer and system guides), root `README.md`, `CONTRIBUTING.md`.
   * **Archive:** `archive` (historical scripts, retired patches, scratch files).
4. **Clean Root Directory:** The root directory is strictly reserved for standard open-source project anchors: `README.md`, `LICENSE`, `CONTRIBUTING.md`, `pyproject.toml`, `uv.lock`, `Dockerfile`, `docker-compose.yml`, `Makefile`, `.gitignore`.

---

## 2. Target Directory Layout

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
├── .env.example                         # Environment configuration template
│
├── src/                                 # [CORE PLATFORM] Production Python Package
│   └── argus/
│       ├── adaptation/                  # CORAL & Class-Aware CORAL algorithms
│       ├── agents/                      # 6 autonomous agents (DIA, TA, EA, KCA, RPA, DSA)
│       ├── api/                         # FastAPI application & endpoints
│       ├── auth/                        # OIDC, JWKS, JWT, and RBAC security
│       ├── blackboard/                  # Shared state synchronization
│       ├── bus/                         # In-memory message bus
│       ├── core/                        # BaseAgent, BaseService, events, tracing
│       ├── data/                        # DataManager, flow simulation, telemetry parsing
│       ├── explain/                     # SHAP attribution helpers
│       ├── features/                    # Flow feature extraction
│       ├── models/                      # Model loader abstraction
│       ├── monitoring/                  # Distribution drift monitoring
│       ├── orchestrator/                # Multi-agent execution pipeline & scheduler
│       ├── policy/                      # Fail-safe security policy engine
│       ├── registry/                    # ModelRegistry (loads D1, D2, D3, XGBoost)
│       ├── schemas/                     # Pydantic validation schemas
│       ├── security/                    # Rate limiting, error masking, security headers
│       ├── services/                    # Incident service & background agent services
│       └── v2_transformer/              # Exploratory transformer group-token architecture
│
├── web/                                 # [FRONTEND] React 19 + TypeScript + Vite SPA
│   ├── src/                             # UI components, 3D topology, hooks, stores
│   ├── public/                          # Static assets
│   ├── package.json                     # Node.js dependencies
│   ├── vite.config.ts                   # Bundler configuration
│   └── dist/                            # Production compiled assets (mounted by FastAPI)
│
├── paper/                               # [RESEARCH PUBLICATIONS] Academic Manuscripts & Exhibits
│   ├── manuscripts/                     # Word/docx & text manuscript drafts
│   ├── data/                            # Figures, tables, and REP01 replication exhibits
│   └── experiments/                     # Journal completion experimental scripts & metrics
│
├── results/                             # [SCIENTIFIC EVIDENCE] Recomputed Metrics & Deliverables
│   ├── experiments/                     # Modern research phases (P1-1, P2, P2.1, P2.2, P2.3)
│   │   ├── p1_1_nfton_in_domain/        # P1-1 supervised reference baseline
│   │   ├── p2_coordinate_generalization/# P2 coordinate-generalization & ambiguity study
│   │   ├── p2_1_validation/             # P2.1 same-test-set cross-domain validation
│   │   ├── p2_2_robustness/             # P2.2 cluster bootstrap & multi-split sensitivity
│   │   └── p2_3_reconciliation/         # P2.3 adversarial reconciliation deliverables
│   ├── master/                          # Authoritative master Excel workbook
│   ├── poster/                          # Poster package, figures, and data tables
│   └── verified/                        # Verified domain statistics and threshold sweeps
│
├── experiments/                         # [EXPERIMENT ARCHIVE] Historical Benchmarks & UDA
│   ├── domain_adaptation/               # Stage A–F CORAL & Stage 1–3 DANN adaptation pipelines
│   ├── execution/                       # EXP01–EXP07 benchmarks
│   ├── training/                        # Model trainers, hyperparameter tuning
│   └── ablations/                       # Phase 4 ablation experiments
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
│   ├── evaluate_nfton_in_domain_baseline.py
│   ├── p2_1_same_test_comparison.py
│   ├── p2_2_statistical_audit.py
│   ├── p2_3_reconciliation_audit.py
│   ├── start_demo.py
│   ├── verify_ui_numbers.py
│   └── ...                              # All active research and demo utilities
│
├── tests/                               # [TEST SUITES] 283 Full-Project Tests
│   ├── unit/                            # Unit tests for core logic, registry, D3 inference
│   ├── integration/                     # Pipeline integration and agent coordination
│   ├── security/                        # OIDC, RBAC, path traversal, error masking
│   └── e2e/                             # End-to-end security incident lifecycle tests
│
├── audit/                               # [INDEPENDENT AUDITS] Evidentiary Verification Records
│   ├── architecture/                    # Repository audits, target specs, inventory JSON
│   ├── independent/                     # Turn 1 master audit reports (EVIDENCE_REGISTER, etc.)
│   ├── p0/                              # P0 engineering defect remediation & closure
│   ├── research/                        # P1-1, P2, P2.1, P2.2, P2.3 research reports
│   └── historical/                      # Consolidated historical audits from root & data/
│
├── docs/                                # [DOCUMENTATION] Engineering & System Guides
│   ├── PROJECT_STRUCTURE.md             # Guide to directory layout and ownership
│   ├── ARCHITECTURE.md                  # Software and multi-agent system architecture
│   ├── RESEARCH_OVERVIEW.md             # Research questions, datasets, and benchmark status
│   ├── DEVELOPMENT_SETUP.md             # Environment setup and developer workflow
│   ├── EXPERIMENT_REPRODUCIBILITY.md    # Step-by-step reproduction guide
│   └── DATA_AND_MODEL_GOVERNANCE.md     # Data and checkpoint conventions
│
└── archive/                             # [ARCHIVED ARTIFACTS] Retired Scripts, Patches, & Clones
    ├── scripts/                         # Retired patch scripts, one-off tools, root scripts
    ├── scratch/                         # Previous scratch scripts and cloned repo snapshot
    └── docs_history/                    # Historical restructuring checklists and moves
```

---

## 3. Migration Action Plan (Incremental Batches)

To guarantee that the repository remains 100% executable and that no changes are irreversible, the migration is structured into **seven discrete, verifiable batches**:

### Batch 1: Root Directory Cleanup (Non-destructive Archival & Relocation)
1. **Archive Temporary Patch Scripts:**  
   Move 31 loose `patch_*.py`, `fix_*.py`, and `plan_restructure.py` files to `archive/scripts/patches/`.
2. **Archive Historical Evaluation Scripts:**  
   Move 18 historical evaluation scripts (`compute_entropy.py`, `compute_shap.py`, `evaluate_risk.py`, `generate_d1_d2_baselines.py`, `generate_figures.py`, etc.) to `archive/scripts/root_scripts/`.
3. **Archive Historical Shell Runners:**  
   Move 6 root shell scripts (`run_all_experiments.sh`, `run_multiseed*.sh`, `wait_for_all.sh`) to `archive/scripts/experiment_runners/`.
4. **Relocate Root Audit Markdown Files:**  
   Move 8 loose audit documents (`AUDIT.md`, `BOT_IOT_COLLAPSE_ANALYSIS.md`, `DEMO.md`, `DRY_RUN_PLAN.md`, `FEATURE_V1_5_VALIDATION.md`, `FOLLOWUP_AUDIT.md`, `LIVE_CHECK.md`, `SCHEMA_AUDIT.md`, `V1_5_PAIRWISE_CHECK.md`) and `audit.py`, `audit_metrics.json`, `audit_results.json` to `audit/historical/`.
5. **Archive Ephemeral Logs & CSVs:**  
   Move `run1.csv`, `TEST_ACCESS.log`, `uvicorn.log`, `final_eval_output.txt` to `archive/logs/`.
*Verification:* Run `git status`, test suite `pytest -q`, and check root cleanliness.

### Batch 2: Stale & Redundant Directory Cleanup & Compatibility Bridging
1. **Prune Stale Frontend Build:**  
   Safely remove `frontend/` (contains only stale Sep 20 `node_modules` and `dist`; the active, working frontend is `web/`).
2. **Prune Abandoned Empty Directories:**  
   Remove `demo/backend/`, `config/` (contains only stale `__pycache__`), `scratch_clone_tmp/`, `scratch_tmp/`, and `training/`.
3. **Establish Model Compatibility Bridge:**  
   Do not delete `models/model_d2_coral.txt` without bridging, as `deployment/compose/docker-compose.yml:82`, `deployment/docker/detector.Dockerfile:30`, and `scripts/start_local.sh:27` depend on it. Retain `artifacts/models/` as the primary source of truth, and replace `models/model_d2_coral.txt` with a relative symlink to `../artifacts/models/model_d2_coral.txt`.
*Verification:* Verify `ModelRegistry` continues loading all models cleanly; verify symlink resolves; run test suite.

### Batch 3: Audit Documentation Consolidation
1. **Consolidate Independent Audit:**  
   Move the Turn 1 audit folder `ARGUS_INDEPENDENT_AUDIT/` to `audit/independent/`.
2. **Relocate Misplaced Data Audits:**  
   Move the 12 misplaced audit files in `data/` (`ARGUS_*_20260925_*.md` and `.json`) to `audit/historical/data_audits/`.
*Verification:* Verify `audit/` contains `architecture/`, `independent/`, `p0/`, `research/`, and `historical/`.

### Batch 4: Scratch Space Archival & Selective Relocation
1. **Preserve Tracked Diagnostic Deliverables in `scratch/`:**  
   Relocate `scratch/diag_task/` (21 `.pt` PyTorch checkpoints, 60 `.csv` datasets, 41 `.png` figures) to `archive/experiments/diagnostic_tasks/` using `git mv`.
2. **Relocate Tracked One-Off Scripts in `scratch/`:**  
   Relocate tracked scripts to `archive/scripts/scratch/` using `git mv`.
3. **Relocate Untracked Sample Dataset:**  
   Move untracked `scratch/BoT-IoT dataset/csv/data_32.csv` (197 MB) to `data/raw/bot_iot/data_32.csv`. Update path in `src/argus/v2_transformer/train_plumbing.py` line 182.
4. **Update `scripts/generate_master_research_excel.py` References:**  
   Update the 10 paths in `scripts/generate_master_research_excel.py` to point to their verified canonical locations in `experiments/execution/` and `archive/audits/` (all 10 files are bit-identical).
5. **Handle Untracked Clones and Caches:**  
   Do NOT move `scratch_argus_clone/` (1.60 GB) into Git-tracked space (would bloat Git history by 1.6 GB). Exclude via `.gitignore` and archive externally. Prune `scratch_pip_cache/` (599 MB). Keep `scratch/` in `.gitignore` as ephemeral workspace.
*Verification:* Verify `train_plumbing.py` imports cleanly; check git status; run test suite.

### Batch 5: Master Workbook & Redundant Deliverables Consolidation
1. **Consolidate Master Research Excel:**  
   Designate `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx` (SHA-256 `f4ddc451...`, 17 sheets) as authoritative; archive root copy `ARGUS_ALL_RESEARCH_RESULTS.xlsx` to `archive/results/` and replace root copy with a symbolic link to `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`.
2. **Consolidate Duplicate Execution Folder:**  
   Consolidate `experiment_execution/` into `experiments/execution/` and archive `experiment_execution/`.
*Verification:* Verify SHA-256 of `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`; run test suite.

### Batch 6: Paper Directory Structuring
1. **Organize Paper Subdirectories:**  
   Within `paper/`, create:
   * `paper/manuscripts/`: Move `ARGUS_paper_v2_representation_resolution.docx` and `paper_text.txt`.
   * `paper/data/`: Move `ARGUS_Paper_Data/`.
   * Keep `paper/experiments/journal_completion/` in place.
*Verification:* Verify manuscript files are preserved with original checksums.

### Batch 7: Documentation Generation & Polish
1. **Create/Update Core Governance Documents:**
   * Root `README.md` — Professional academic & engineering overview.
   * `docs/PROJECT_STRUCTURE.md` — Complete directory and ownership guide.
   * `docs/ARCHITECTURE.md` — Platform architecture and agent contracts.
   * `docs/RESEARCH_OVERVIEW.md` — Research questions, benchmark status, and findings.
   * `docs/DEVELOPMENT_SETUP.md` — Local setup and development instructions.
   * `docs/EXPERIMENT_REPRODUCIBILITY.md` — Step-by-step reproduction instructions.
   * `docs/DATA_AND_MODEL_GOVERNANCE.md` — Conventions for datasets, models, and manifests.
   * `CONTRIBUTING.md` — Repository governance and contribution standards.
   * `audit/architecture/MIGRATION_LOG.md` — Detailed step-by-step log of all actions taken.
   * `audit/architecture/POST_RESTRUCTURE_VALIDATION.md` — Final validation results across engineering, testing, and research.
*Verification:* Run complete test suite (283 tests), verify backend startup, verify frontend build, check git status.

---

## 4. Preservation & Non-Negotiable Boundaries

The following files and paths are **STRICTLY PROTECTED** and will **NOT** be moved, renamed, or modified:
1. `src/argus/**`: Complete application package remains unchanged.
2. `web/**`: Active React 19 frontend remains at repository root (mounted by FastAPI at `web/dist`).
3. `artifacts/models/**`: Model checkpoint paths hardcoded in `ModelRegistry` remain intact.
4. `models/model_d2_coral.txt`: Compatibility bridge maintained for Docker and startup scripts via relative symlink.
5. `data/raw/**`: External large datasets remain in place without staging into Git.
6. `results/experiments/**`: All P1-1, P2, P2.1, P2.2, and P2.3 research results and manifests remain untouched.
7. `tests/**`: Complete test suite remains intact; discovery via `pytest` continues discovering all 283 tests.
8. `scripts/p2_*` and `scripts/evaluate_*`: Primary research runner scripts remain accessible in `scripts/`.
9. `prompts/**`: Runtime system prompts used by `decision_agent/main.py` remain at repository root.
10. `Dockerfile` and `docker-compose.yml`: Multi-stage production container definitions and compose specs remain valid.
11. `LICENSE` & `pyproject.toml` & `uv.lock`: MIT License (Copyright 2026 Bhavini Chauhan) and `uv` deterministic dependency management remain authoritative.

---

## 5. Stage A.1 Status & Migration Approval Gate

Stage A.1 is complete.  
* Corrections & Reconciliation: [`audit/architecture/STAGE_A1_CORRECTIONS.md`](file:///home/bhumi/GitHub/ARGUS/audit/architecture/STAGE_A1_CORRECTIONS.md)
* Authoritative Migration Blueprint: [`audit/architecture/FINAL_MIGRATION_PLAN.md`](file:///home/bhumi/GitHub/ARGUS/audit/architecture/FINAL_MIGRATION_PLAN.md)
* Updated Existing Audit: [`audit/architecture/EXISTING_REPOSITORY_AUDIT.md`](file:///home/bhumi/GitHub/ARGUS/audit/architecture/EXISTING_REPOSITORY_AUDIT.md)
* Machine-Readable Inventory: [`audit/architecture/repository_inventory.json`](file:///home/bhumi/GitHub/ARGUS/audit/architecture/repository_inventory.json)

**Approval Recommendation:** `READY WITH QUALIFICATIONS`  
Awaiting explicit user authorization to proceed with Stage B execution.
