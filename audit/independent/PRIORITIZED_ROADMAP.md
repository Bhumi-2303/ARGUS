# ARGUS Prioritized Engineering & Research Roadmap

**Audit Date**: November 1, 2026  
**Auditor Role**: Senior Research Engineer, Software Architect & MLOps Engineer  
**Objective**: Practical, sequenced execution plan to transition ARGUS from its current prototype state to a publication-ready, hardened research platform.

---

## 1. Summary Execution Matrix

```text
[ TODAY ] ──► P0: CRITICAL BLOCKERS (Fix broken model loading & security test failures)
                 │
                 ▼
              P1: ESSENTIAL RESEARCH EXPERIMENTS (Target baseline, few-shot curves, stats)
                 │
                 ▼
              P2: ENGINEERING & MLOPS HARDENING (App factory, DANN packaging, bundle splits)
                 │
                 ▼
              P3: DOCUMENTATION & PAPER FINALIZATION (LaTeX conversion, journal submission)
                 │
              [ JOURNAL PUBLICATION READY ]
```

| Priority Tier | Focus Area | Total Tasks | Estimated Effort | Impact on Publication / Production |
| :--- | :--- | :---: | :---: | :--- |
| **P0 — Critical Blockers** | Broken model loading & failing test suite | 3 | 1–2 days | Resolves runtime crashes and restores 100% test pass rate |
| **P1 — Essential Research** | Baseline completion & statistical rigor | 4 | 3–5 days | Eliminates fatal scientific vulnerabilities before journal submission |
| **P2 — Engineering & MLOps** | Architecture refinement & packaging | 4 | 2–3 days | Eliminates code bloat, secures SPA routing, optimizes bundles |
| **P3 — Documentation** | Paper polishing & public artifact release | 4 | 2–3 days | Produces IEEE-formatted manuscript and public zenodo bundle |

---

## 2. P0 — Critical Blockers

### Task P0-1: Resolve ModelRegistry 73-Feature Mismatch for `model_d3_native`
- **Task Description**: Update `src/argus/registry/model_registry.py` to support variable feature-dimension models. Specifically, configure `model_d3_native` with its actual 73 native flow feature names, or guard its single-sample inference path to require the 73-feature vector rather than the 4-feature vector.
- **Reason**: Currently, calling `reg.predict('model_d3_native', test_feats)` crashes with `LightGBMError: The number of features in data (4) is not the same as it was in training data (73)`. This breaks model serving for native SCADA evaluation.
- **Dependencies**: None.
- **Expected Deliverable**: Updated `src/argus/registry/model_registry.py` supporting native 73-feature inference alongside 4-feature harmonized models.
- **Verification Criteria**:
  ```bash
  .venv/bin/python -c "from argus.registry.model_registry import ModelRegistry; reg = ModelRegistry(); reg.load_all(); print(reg.get_status_dict())"
  ```
  Must load and predict without throwing `LightGBMError`.

### Task P0-2: Fix Static Frontend SPA Catch-All Route in `main.py`
- **Task Description**: In `src/argus/api/main.py` (lines 280–305), modify `serve_spa` to inspect the normalized request path before serving `index.html`. Explicitly reject any path containing directory traversal tokens (`..`), path escaping characters, or paths matching system directories with HTTP 400 or 404 rather than falling back to `index.html` (HTTP 200).
- **Reason**: `tests/security/test_adversarial_verification.py::test_path_traversal_all_vectors_rejected` fails because `GET /api/v1/results/../../../../etc/passwd` is normalized by the HTTP client and caught by `serve_spa`, returning `index.html` with HTTP 200 OK instead of HTTP 400/404.
- **Dependencies**: None.
- **Expected Deliverable**: Hardened `serve_spa` route handler that rejects non-SPA resource paths.
- **Verification Criteria**:
  ```bash
  /usr/bin/pytest tests/security/test_adversarial_verification.py -k "test_path_traversal_all_vectors_rejected"
  ```
  Must exit with 0 failures (PASS).

### Task P0-3: Implement App Factory Pattern for Dynamic Settings & CORS Isolation
- **Task Description**: Refactor `src/argus/api/main.py` to use an application factory function `create_app(settings=None)` rather than instantiating `app = FastAPI(...)` as a global module-level singleton.
- **Reason**: `tests/security/test_adversarial_verification.py::test_cors_rejects_unauthorized_origins` fails because the global `app` instance was initialized at import time with development CORS regex, and the test's `mock_prod_environment` fixture cannot update Starlette's already-compiled middleware stack.
- **Dependencies**: None.
- **Expected Deliverable**: Factory-based app creation allowing isolated test environments.
- **Verification Criteria**:
  ```bash
  /usr/bin/pytest tests/security/test_adversarial_verification.py -k "test_cors_rejects_unauthorized_origins"
  ```
  Must exit with 0 failures (PASS), bringing total test suite to 183 passed, 0 failed (100% pass rate).

---

## 3. P1 — Essential Research Experiments

### Task P1-1: Execute In-Domain Target Supervised Baseline on NF-ToN
- **Task Description**: Train standard XGBoost and LightGBM models directly on `data/raw/legacy_package/argus_coral_data/nfton_train_adaptation.csv` ($N = 8,406,962$) and evaluate on `nfton_test_features.csv` ($N = 2,627,177$).
- **Reason**: Essential for scientific validity. Reviewers at IEEE TDSC will demand to know the target in-domain performance ceiling to judge the utility of Clean Class-Aware CORAL (which also accesses the 8.41M target adaptation labels).
- **Dependencies**: Python environment with XGBoost / LightGBM.
- **Expected Deliverable**: New results file `results/verified/nfton_in_domain_supervised_metrics.csv` and updated Table II in the manuscript.
- **Verification Criteria**: Metrics must be reproducible using a standalone script `scripts/train_nfton_in_domain_baseline.py`.

### Task P1-2: Execute Few-Shot Target Label Efficiency Sweep
- **Task Description**: Evaluate Clean Class-Aware CORAL under constrained target label budgets:
  $$k \in \{10, 50, 100, 500, 1000, 5000, 10000, 100000\}$$
  target labels drawn stratified from `nfton_train_adaptation.csv` across 5 random seeds.
- **Reason**: Class-Aware CORAL is only a compelling research contribution if it succeeds with *few* target labels. Evaluating across label budgets proves how many target examples are needed to achieve MCC $> +0.30$.
- **Dependencies**: `ciciot_train_features.csv`, `nfton_train_adaptation.csv`.
- **Expected Deliverable**: New figure and table: "Few-Shot Target Label Efficiency Curve ($k$ vs MCC)".
- **Verification Criteria**: Script `scripts/run_few_shot_coral_sweep.py` executed across 5 seeds with standard deviation error bars.

### Task P1-3: Pairwise Hypothesis Testing (DeLong & McNemar Tests)
- **Task Description**: Compute formal statistical tests comparing Clean Class-Aware CORAL against Source-Only XGBoost, Global CORAL, and DANN on the frozen 2.63M test set predictions:
  1. DeLong test for ROC-AUC difference.
  2. McNemar test for paired binary prediction discordance ($\chi^2$ and $p$-value).
- **Reason**: Top-tier journal reviewers require formal statistical tests ($p < 0.001$) to confirm that empirical improvements are statistically significant and not random fluctuations.
- **Dependencies**: Prediction arrays in `predictions_raw/`.
- **Expected Deliverable**: Table III in manuscript: "Pairwise Statistical Significance Tests".
- **Verification Criteria**: Output CSV reporting $z$-statistics, $\chi^2$ statistics, and two-tailed $p$-values.

### Task P1-4: Implement and Run Missing Journal Completion Scripts (EXP-05 to EXP-12)
- **Task Description**: Write and execute the remaining 8 experiment scripts outlined in `paper/experiments/journal_completion/tables/experiment_registry.csv`:
  - `run_exp05_domain_shift_coral.py` (KS and Wasserstein metrics)
  - `run_exp07_pipeline_ablation.py` (Leave-one-component-out)
  - `run_exp08_sensitivity_analysis.py` (CORAL regularization sweep)
  - `run_exp09_robustness_stress_test.py` (Noise and feature dropout)
  - `run_exp10_attack_family_breakdown.py` (Granular per-attack class recall)
  - `run_exp11_shap_error_analysis.py` (SHAP stability across seeds)
  - `run_exp12_computational_profiling.py` (Inference throughput and latency)
- **Reason**: Completes the empirical data suite promised in the journal completion registry.
- **Dependencies**: `run_exp01` through `run_exp04` helper modules.
- **Expected Deliverable**: 8 executed scripts with corresponding output CSVs in `paper/experiments/journal_completion/tables/`.
- **Verification Criteria**: All 12 experiments in `experiment_registry.csv` marked as `COMPLETE` with reproducible execution logs.

---

## 4. P2 — Important Engineering Improvements

### Task P2-1: Package PyTorch DANN Checkpoint into ModelRegistry
- **Task Description**: Implement a lightweight PyTorch inference wrapper for `dann_best_model.pt` (located in `data/raw/legacy_package/argus_coral_data/dann_results/`) and wire it into `src/argus/registry/model_registry.py` under model name `dann`.
- **Reason**: Currently, `model_registry.py` registers DANN as `status: unavailable`, claiming no verified weights exist, even though `dann_best_model.pt` (70.5 kB) is physically present on disk.
- **Dependencies**: PyTorch runtime in `.venv`.
- **Expected Deliverable**: Active DANN model booster enabling live inference in API and UI.
- **Verification Criteria**:
  ```bash
  .venv/bin/python -c "from argus.registry.model_registry import ModelRegistry; reg = ModelRegistry(); reg.load_all(); print(reg.predict('dann', {'pkt_mean_to_max': 0.5, 'tcp_flag_density': 0.1, 'log_pkt_mean': 5.0, 'log_pkt_max': 7.0}))"
  ```
  Must return probability without error.

### Task P2-2: Frontend Bundle Chunk Code-Splitting
- **Task Description**: Update `web/vite.config.ts` to implement manual chunking for `@react-three/fiber`, `three`, `echarts`, and `lucide-react`. Use `React.lazy()` for `TopologyPage` and `ModelComparisonPage`.
- **Reason**: Vite build currently warns that production chunks `TopologyPage` (965 kB) and `esm-DaNYU2BO` (1.13 MB) exceed the recommended 500 kB size limit.
- **Dependencies**: Node 22 / Vite in `web/`.
- **Expected Deliverable**: Optimized bundle with all chunks under 450 kB.
- **Verification Criteria**:
  ```bash
  cd web && npm run build
  ```
  Must complete without chunk size warnings.

### Task P2-3: Root Directory Cleanup & Script Consolidation
- **Task Description**: Migrate the 25+ root-level patch scripts (`patch_*.py`, `fix_*.py`) and scratch directories (`scratch_argus_clone/`, `scratch_pip_cache/`) into `archive/scripts/` or `archive/backups/`.
- **Reason**: Cluttered root directory complicates new developer onboarding, repository audits, and git status tracking.
- **Dependencies**: Git tracking.
- **Expected Deliverable**: Clean root directory containing only standard configuration files (`pyproject.toml`, `README.md`, `Dockerfile`, `Makefile`, etc.).
- **Verification Criteria**: `ls -la` in root shows zero temporary patch scripts.

### Task P2-4: Persistent Database Sink for Security Audit Logs
- **Task Description**: Connect `src/argus/security/sink.py` to a persistent SQLite or PostgreSQL storage backend for audit logs, rather than dropping logs in-memory when the application restarts.
- **Reason**: Compliance with industrial ICS security standards (NIST SP 800-82, IEC 62443).
- **Dependencies**: SQLAlchemy / SQLite configuration.
- **Expected Deliverable**: Persistent audit log table storing all authentication and flow simulation events.
- **Verification Criteria**: Audit logs persist across server restarts.

---

## 5. P3 — Documentation & Presentation Improvements

### Task P3-1: Formal Mathematical Notation Harmonization in Paper Draft
- **Task Description**: Convert `paper/paper_text.txt` into a formal LaTeX manuscript using the IEEE Computer Society template (`ieeetran.cls`). Add formal definitions for class-aware covariance alignment, prior shift Bayesian adjustment, and threshold calibration.
- **Reason**: Essential for professional submission to IEEE TDSC / TIFS.
- **Dependencies**: Text from `paper/paper_text.txt`.
- **Expected Deliverable**: Compilable LaTeX project in `paper/latex/`.
- **Verification Criteria**: `pdflatex argus_paper.tex` compiles with zero errors into a 14-page double-column PDF.

### Task P3-2: Update README Terminology to "Supervised Domain Adaptation"
- **Task Description**: Update `README.md` to explicitly state that Clean Class-Aware CORAL operates in a supervised domain adaptation regime (utilizing labeled target adaptation splits), avoiding ambiguity with unsupervised methods.
- **Reason**: Prevents misunderstandings by industry practitioners and peer reviewers.
- **Dependencies**: None.
- **Expected Deliverable**: Updated `README.md` Section 1 and Section 2.
- **Verification Criteria**: README accurately documents target label requirements.

### Task P3-3: Public Dataset & Checkpoint Zenodo Packaging
- **Task Description**: Prepare a Zenodo data archive containing frozen CSV splits, trained model artifacts, and evaluation logs with persistent DOIs.
- **Reason**: Fulfills IEEE reproducibility requirements for open science.
- **Dependencies**: Frozen files in `results/verified/` and `dataset/`.
- **Expected Deliverable**: Script `scripts/package_zenodo_release.sh` generating verifiable tarballs with SHA-256 manifests.
- **Verification Criteria**: Checksum verification passes on unpacked archive.

### Task P3-4: Consolidate Duplicate Excel Results Workbooks
- **Task Description**: Remove redundant root `ARGUS_ALL_RESEARCH_RESULTS.xlsx` and keep only `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`, updating references in documentation.
- **Reason**: Eliminates untracked file ambiguity in git working tree.
- **Dependencies**: None.
- **Expected Deliverable**: Single authoritative master results workbook.
- **Verification Criteria**: `git status` reports clean working directory.
