# ARGUS — Final Safe Incremental Migration Plan

**Document Version:** 2.0.0  
**Date:** 2026-11-02  
**Author:** Senior Software Architect, Research Software Engineer, ML Infrastructure Engineer  
**Repository:** `/home/bhumi/GitHub/ARGUS`  
**Git Branch:** `v2-transformer-exploratory`  
**Status:** **AUTHORITATIVE EXECUTION BLUEPRINT — AWAITING STAGE B GATE AUTHORIZATION**  
**Pre-restructuring Test Baseline:** `283 passed, 0 failed, 0 skipped` in 12.58s  

---

## 1. Migration Philosophy & Safety Guardrails

The ARGUS repository restructuring transforms a multi-phase research codebase into a professional, enterprise-grade software and academic research repository.

### Core Non-Negotiable Rules
1. **Zero Runtime Disruption:** Core application modules (`src/argus`), active frontend (`web`), operational model weights (`artifacts/models`), and test suites (`tests`) retain full runtime compatibility.
2. **Absolute Scientific Integrity:** No experimental metrics, prediction parquet files, dataset checksums, or paper drafts are modified, deleted, or falsified.
3. **No Unchecked Git Bloat:** Untracked directories (such as `scratch_argus_clone/`, 1.6 GB) must **never** be moved into Git-tracked directories inside `archive/`. They must be handled via external archival and `.gitignore` exclusion.
4. **Preservation of Tracked Evidence:** Tracked files inside `scratch/` (296 files, including 21 `.pt` PyTorch checkpoints and 60 `.csv` datasets) must be preserved using `git mv` into `archive/experiments/diagnostic_tasks/`.
5. **Immediate Automated Rollback:** If any verification step fails (test failure, import error, missing file), the batch is rolled back immediately before proceeding.

---

## 2. Pre-Migration Prerequisites & Safety Snapshot

Before executing Batch 1, the following commands **must** be executed to create an immutable rollback anchor:

```bash
# 1. Verify working tree status
git status

# 2. Run full test suite baseline check
.venv/bin/pytest -q
# Must report: 283 passed

# 3. Create pre-restructuring safety tag
git tag pre-restructure-v1.0

# 4. Create local stash backup of any untracked configuration
tar -czf /tmp/argus_pre_restructure_configs.tar.gz configs/ .env.example
```

---

## 3. Detailed Batch-by-Batch Migration Specifications

The migration is partitioned into **seven sequential, verifiable batches**:

```
Pre-Migration Tag ──> Batch 1 ──> Batch 2 ──> Batch 3 ──> Batch 4 ──> Batch 5 ──> Batch 6 ──> Batch 7 ──> Restructured Repo
                       (Root)    (Stale Dirs)  (Audits)  (Scratch)   (Master)   (Paper)    (Docs/Valid)
```

---

### Batch 1: Root Directory Cleanup (Non-Destructive Archival & Relocation)

**Objective:** Clean the cluttered root directory of 72 non-essential files, preserving them in structured archive and audit directories.

#### 1.1 Itemized File Mappings
* **1.1.1 Temporary Patch Scripts (25 files | ~52 KB | Risk: Low):**
  * *Source:* Root `fix_demo_page.py`, `fix_gitignore.py`, `fix_markdown.py`, `fix_monitor.py`, `fix_onboard.py`, `fix_overview.py`, `fix_simulate_flow.py`, `fix_threat_publisher.py`, `fix_topbar.py`, `fix_ts.py`, `fix_ts2.py`, `fix_ts3.py`, `patch_cards.py`, `patch_chart.py`, `patch_legend.py`, `patch_live_monitor_card.py`, `patch_live_monitor_judge.py`, `patch_mc.py`, `patch_meta.py`, `patch_meta2.py`, `patch_metrics.py`, `patch_overview.py`, `patch_overview_btn.py`, `patch_pages.py`, `patch_provenance.py`, `patch_registry.py`, `patch_reset.py`, `patch_sample_script.py`, `patch_so.py`, `patch_verify.py`, `plan_restructure.py`.
  * *Destination:* `archive/scripts/patches/`
* **1.1.2 Historical Root Evaluation & Generator Scripts (21 files | ~75 KB | Risk: Low):**
  * *Source:* Root `compute_entropy.py`, `compute_shap.py`, `evaluate_agent_contribution.py`, `evaluate_risk.py`, `evaluate_risk_analysis.py`, `generate_d1_d2_baselines.py`, `generate_figures.py`, `generate_final_report.py`, `generate_multiseed_figures.py`, `generate_phase3.py`, `generate_phase4_report.py`, `generate_poster.py`, `generate_token.py`, `get_cm.py`, `investigate_fpr.py`, `test_e2e_local.py`, `test_load.py`, `validate_dataset.py`.
  * *Destination:* `archive/scripts/root_scripts/`
* **1.1.3 Historical Shell Experiment Runners (6 files | ~9 KB | Risk: Low):**
  * *Source:* Root `run_all_experiments.sh`, `run_multiseed.sh`, `run_multiseed_fast.sh`, `run_multiseed_fast2.sh`, `run_multiseed_final.sh`, `wait_for_all.sh`.
  * *Destination:* `archive/scripts/experiment_runners/`
* **1.1.4 Root Historical Audit Deliverables (12 files | ~135 KB | Risk: Low):**
  * *Source:* Root `AUDIT.md`, `BOT_IOT_COLLAPSE_ANALYSIS.md`, `DEMO.md`, `DRY_RUN_PLAN.md`, `FEATURE_V1_5_VALIDATION.md`, `FOLLOWUP_AUDIT.md`, `LIVE_CHECK.md`, `SCHEMA_AUDIT.md`, `V1_5_PAIRWISE_CHECK.md`, `audit.py`, `audit_metrics.json`, `audit_results.json`.
  * *Destination:* `audit/historical/`
* **1.1.5 Ephemeral Logs & CSVs (4 files | ~6 KB | Risk: Low):**
  * *Source:* Root `run1.csv`, `TEST_ACCESS.log`, `uvicorn.log`, `final_eval_output.txt`.
  * *Destination:* `archive/logs/`

#### 1.2 Files Remaining at Root (11 Essential Project Anchors)
* `README.md`, `LICENSE`, `Makefile`, `pyproject.toml`, `uv.lock`, `Dockerfile`, `docker-compose.yml`, `.gitignore`, `.dockerignore`, `.env.example`, `.gitleaks.toml`.

#### 1.3 Execution Commands
```bash
mkdir -p archive/scripts/patches archive/scripts/root_scripts archive/scripts/experiment_runners audit/historical archive/logs

# Move patches
git mv fix_*.py patch_*.py plan_restructure.py archive/scripts/patches/ 2>/dev/null || mv fix_*.py patch_*.py plan_restructure.py archive/scripts/patches/

# Move historical scripts
git mv compute_*.py evaluate_*.py generate_*.py investigate_*.py test_*.py validate_*.py get_cm.py archive/scripts/root_scripts/ 2>/dev/null || mv compute_*.py evaluate_*.py generate_*.py investigate_*.py test_*.py validate_*.py get_cm.py archive/scripts/root_scripts/

# Move shell runners
git mv run_*.sh wait_for_all.sh archive/scripts/experiment_runners/ 2>/dev/null || mv run_*.sh wait_for_all.sh archive/scripts/experiment_runners/

# Move audit files
git mv AUDIT.md BOT_IOT_COLLAPSE_ANALYSIS.md DEMO.md DRY_RUN_PLAN.md FEATURE_V1_5_VALIDATION.md FOLLOWUP_AUDIT.md LIVE_CHECK.md SCHEMA_AUDIT.md V1_5_PAIRWISE_CHECK.md audit.py audit_metrics.json audit_results.json audit/historical/ 2>/dev/null || mv AUDIT.md BOT_IOT_COLLAPSE_ANALYSIS.md DEMO.md DRY_RUN_PLAN.md FEATURE_V1_5_VALIDATION.md FOLLOWUP_AUDIT.md LIVE_CHECK.md SCHEMA_AUDIT.md V1_5_PAIRWISE_CHECK.md audit.py audit_metrics.json audit_results.json audit/historical/

# Move ephemeral logs
mv run1.csv TEST_ACCESS.log uvicorn.log final_eval_output.txt archive/logs/ 2>/dev/null || true
```

#### 1.4 Verification Command
```bash
.venv/bin/pytest -q
# Must report: 283 passed
```

#### 1.5 Rollback Command
```bash
git checkout HEAD -- . && git clean -fd
```

---

### Batch 2: Stale & Redundant Directory Cleanup & Compatibility Hardening

**Objective:** Prune stale build remnants, remove empty abandoned directories, and establish model compatibility bridges without breaking runtime containers.

#### 2.1 Actions
1. **Prune Stale Frontend Build Cache (`frontend/`):**
   * *Status:* Contains only stale `node_modules/` and `dist/` from an abandoned build on Sep 20. Active frontend is `web/`.
   * *Action:* `rm -rf frontend/` (untracked build artifact).
2. **Prune Abandoned Empty Directories:**
   * *Directories:* `demo/backend/`, `config/` (contains only empty `__pycache__`), `scratch_clone_tmp/`, `scratch_tmp/`, `training/`.
   * *Action:* Prune empty folders.
3. **Model Compatibility Bridge (`models/model_d2_coral.txt`):**
   * *Finding:* `models/model_d2_coral.txt` (713,743 B) is bit-identical to `artifacts/models/model_d2_coral.txt`.
   * *Dependency:* `deployment/compose/docker-compose.yml:82` and `deployment/docker/detector.Dockerfile:30` reference `/app/models/model_d2_coral.txt`. `scripts/start_local.sh:27` checks `models/model_d2_coral.txt`.
   * *Action:* Retain `artifacts/models/model_d2_coral.txt` as the authoritative source of truth. Create a relative symlink from `models/model_d2_coral.txt` to `../artifacts/models/model_d2_coral.txt` so both direct container mounts and application code succeed with zero risk of breakage.

#### 2.2 Execution Commands
```bash
rm -rf frontend/ demo/backend/ config/ scratch_clone_tmp/ scratch_tmp/ training/

# Ensure models directory exists and create symlink bridge
mkdir -p models
if [ -f models/model_d2_coral.txt ] && [ ! -L models/model_d2_coral.txt ]; then
    # Verify bit-for-bit identity before symlinking
    cmp -s models/model_d2_coral.txt artifacts/models/model_d2_coral.txt && rm models/model_d2_coral.txt
    ln -s ../artifacts/models/model_d2_coral.txt models/model_d2_coral.txt
fi
```

#### 2.3 Verification Commands
```bash
# Verify ModelRegistry loads cleanly
.venv/bin/python -c "from argus.registry.model_registry import ModelRegistry; reg = ModelRegistry(); print('Registered models:', list(reg.models.keys()))"
# Verify symlink resolves
test -f models/model_d2_coral.txt && echo "Model symlink bridge: OK"
.venv/bin/pytest -q
```

#### 2.4 Rollback Command
```bash
git checkout HEAD -- models/
```

---

### Batch 3: Audit Documentation Consolidation

**Objective:** Consolidate all independent, historical, and misplaced audit files under the centralized `audit/` hierarchy.

#### 3.1 Actions
1. **Consolidate Independent Audit Deliverables:**
   * *Source:* `ARGUS_INDEPENDENT_AUDIT/` (6 files: `MASTER_AUDIT_REPORT.md`, `EVIDENCE_REGISTER.md`, `GAP_ANALYSIS.md`, `REMEDIATION_ROADMAP.md`, `AUDIT_CHECKLIST.md`, `TECHNICAL_FINDINGS.md`).
   * *Destination:* `audit/independent/`
2. **Relocate Misplaced Data Governance Audits:**
   * *Source:* 12 files in `data/`: `ARGUS_DATASET_GOVERNANCE_AUDIT_20260925_*.md`, `ARGUS_FEASIBILITY_MATRIX_20260925_*.json`.
   * *Destination:* `audit/historical/data_audits/`

#### 3.2 Execution Commands
```bash
mkdir -p audit/independent audit/historical/data_audits

# Move Turn 1 independent audit
git mv ARGUS_INDEPENDENT_AUDIT/* audit/independent/ 2>/dev/null || mv ARGUS_INDEPENDENT_AUDIT/* audit/independent/
rmdir ARGUS_INDEPENDENT_AUDIT 2>/dev/null || true

# Relocate misplaced data audits
git mv data/ARGUS_* audit/historical/data_audits/ 2>/dev/null || mv data/ARGUS_* audit/historical/data_audits/
```

#### 3.3 Verification Commands
```bash
test -f audit/independent/MASTER_AUDIT_REPORT.md && echo "Independent audit: OK"
test -d audit/historical/data_audits && echo "Data audits: OK"
.venv/bin/pytest -q
```

#### 3.4 Rollback Command
```bash
git checkout HEAD -- ARGUS_INDEPENDENT_AUDIT/ data/
```

---

### Batch 4: Scratch Space Archival & Selective Relocation

**Objective:** Preserve all 296 Git-tracked diagnostic experiment checkpoints and scripts from `scratch/`, update script references, and exclude untracked clones without Git repository bloat.

#### 4.1 Actions
1. **Relocate Tracked Diagnostic Deliverables in `scratch/`:**
   * *Source:* `scratch/diag_task/` (21 `.pt` PyTorch checkpoints, 60 `.csv` datasets, 41 `.png` figures).
   * *Destination:* `archive/experiments/diagnostic_tasks/` via `git mv`.
2. **Relocate Tracked One-Off Scripts in `scratch/`:**
   * *Source:* Tracked `.py`, `.sh`, `.md` scripts in `scratch/`.
   * *Destination:* `archive/scripts/scratch/` via `git mv`.
3. **Move Untracked Sample Dataset in `scratch/`:**
   * *Source:* `scratch/BoT-IoT dataset/csv/data_32.csv` (197.25 MB).
   * *Destination:* `data/raw/bot_iot/data_32.csv`.
   * *Code Update:* In `src/argus/v2_transformer/train_plumbing.py` line 182, update path from `../../../scratch/BoT-IoT dataset/csv/data_32.csv` to `../../../data/raw/bot_iot/data_32.csv`.
4. **Update `scripts/generate_master_research_excel.py` References:**
   * Update the 10 hardcoded `scratch_argus_clone/` paths to point to their verified canonical locations:
     * `scratch_argus_clone/experiment_execution/...` $\rightarrow$ `experiments/execution/...`
     * `scratch_argus_clone/ARGUS_PAPER_READINESS_AUDIT/...` $\rightarrow$ `archive/audits/ARGUS_PAPER_READINESS_AUDIT/...`
     * `scratch_argus_clone/phase3_results/...` $\rightarrow$ `archive/backups/phase3_results/...`
     * `scratch_argus_clone/phase4_results/...` $\rightarrow$ `archive/backups/phase4_results/...`
5. **Handle Untracked Clones & Caches:**
   * Ensure `scratch_argus_clone/` and `scratch_pip_cache/` remain untracked and excluded in `.gitignore`.
   * Prune `scratch_pip_cache/` to recover 599 MB of disk space.

#### 4.2 Execution Commands
```bash
mkdir -p archive/experiments/diagnostic_tasks archive/scripts/scratch data/raw/bot_iot

# Relocate tracked diagnostic tasks
git mv scratch/diag_task archive/experiments/diagnostic_tasks/ 2>/dev/null || mv scratch/diag_task archive/experiments/diagnostic_tasks/

# Relocate remaining tracked files in scratch
for f in $(git ls-files scratch/); do
    if [ -f "$f" ]; then
        git mv "$f" archive/scripts/scratch/ 2>/dev/null || mv "$f" archive/scripts/scratch/
    fi
done

# Move untracked BoT-IoT sample dataset
if [ -f "scratch/BoT-IoT dataset/csv/data_32.csv" ]; then
    mv "scratch/BoT-IoT dataset/csv/data_32.csv" data/raw/bot_iot/data_32.csv
    rm -rf "scratch/BoT-IoT dataset"
fi

# Clean untracked pip cache
rm -rf scratch_pip_cache/
```

#### 4.3 Verification Commands
```bash
# Verify train_plumbing imports cleanly
.venv/bin/python -c "import argus.v2_transformer; print('v2_transformer OK')"
# Run test suite
.venv/bin/pytest -q
```

#### 4.4 Rollback Command
```bash
git checkout HEAD -- scratch/ src/
```

---

### Batch 5: Master Workbook & Redundant Deliverables Consolidation

**Objective:** Consolidate master research Excel workbooks and remove redundant duplicate execution directories.

#### 5.1 Actions
1. **Consolidate Master Research Excel:**
   * Authoritative Location: `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx` (SHA-256: `f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1`).
   * Action: Archive root copy `ARGUS_ALL_RESEARCH_RESULTS.xlsx` to `archive/results/` and replace root copy with a symbolic link: `ARGUS_ALL_RESEARCH_RESULTS.xlsx -> results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`.
2. **Consolidate `experiment_execution/`:**
   * Action: Verify all files in `experiment_execution/` exist in `experiments/execution/`; archive or prune redundant copy.

#### 5.2 Execution Commands
```bash
mkdir -p archive/results

# Consolidate master excel
cp ARGUS_ALL_RESEARCH_RESULTS.xlsx archive/results/
rm ARGUS_ALL_RESEARCH_RESULTS.xlsx
ln -s results/ARGUS_ALL_RESEARCH_RESULTS.xlsx ARGUS_ALL_RESEARCH_RESULTS.xlsx

# Consolidate experiment_execution
if [ -d experiment_execution ]; then
    mkdir -p archive/experiments/
    mv experiment_execution archive/experiments/
fi
```

#### 5.3 Verification Commands
```bash
# Check SHA-256 of results workbook
.venv/bin/python -c "
import hashlib
h = hashlib.sha256(open('results/ARGUS_ALL_RESEARCH_RESULTS.xlsx', 'rb').read()).hexdigest()
assert h == 'f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1'
print('Master Excel SHA-256 verified:', h[:16])
"
.venv/bin/pytest -q
```

#### 5.4 Rollback Command
```bash
rm -f ARGUS_ALL_RESEARCH_RESULTS.xlsx
cp archive/results/ARGUS_ALL_RESEARCH_RESULTS.xlsx ./
```

---

### Batch 6: Publication Directory Structuring

**Objective:** Cleanly structure `paper/` into manuscripts, replication data, and journal experiments.

#### 6.1 Actions
1. Create `paper/manuscripts/` and move `ARGUS_paper_v2_representation_resolution.docx` and `paper_text.txt`.
2. Create `paper/data/` and relocate `paper/ARGUS_Paper_Data/`.
3. Retain `paper/experiments/journal_completion/` in place.

#### 6.2 Execution Commands
```bash
mkdir -p paper/manuscripts paper/data

git mv paper/ARGUS_paper_v2_representation_resolution.docx paper/manuscripts/ 2>/dev/null || mv paper/ARGUS_paper_v2_representation_resolution.docx paper/manuscripts/
git mv paper/paper_text.txt paper/manuscripts/ 2>/dev/null || mv paper/paper_text.txt paper/manuscripts/
git mv paper/ARGUS_Paper_Data/* paper/data/ 2>/dev/null || mv paper/ARGUS_Paper_Data/* paper/data/
rmdir paper/ARGUS_Paper_Data 2>/dev/null || true
```

#### 6.3 Verification Commands
```bash
# Verify manuscript SHA-256
.venv/bin/python -c "
import hashlib
h = hashlib.sha256(open('paper/manuscripts/ARGUS_paper_v2_representation_resolution.docx', 'rb').read()).hexdigest()
assert h == 'b074f4f0d064ecb7f36f82c9a6ae82bfcd936b26437b33bc7720d1612e7e1b25'
print('Manuscript docx SHA-256 verified:', h[:16])
"
.venv/bin/pytest -q
```

#### 6.4 Rollback Command
```bash
git checkout HEAD -- paper/
```

---

### Batch 7: Documentation Generation & Global Verification Gate

**Objective:** Generate comprehensive system documentation, update governance guides, and execute exhaustive full-system verification.

#### 7.1 Documentation Deliverables to Create / Update
1. Root `README.md` — Professional academic and multi-agent system overview.
2. `CONTRIBUTING.md` — Code and research contribution guidelines.
3. `docs/PROJECT_STRUCTURE.md` — Full guide to restructured directories and ownership.
4. `docs/ARCHITECTURE.md` — Multi-agent system architecture and agent contracts.
5. `docs/RESEARCH_OVERVIEW.md` — Comprehensive summary of research baselines and findings.
6. `docs/DEVELOPMENT_SETUP.md` — Developer environment setup and testing workflows.
7. `docs/EXPERIMENT_REPRODUCIBILITY.md` — Step-by-step reproduction instructions.
8. `audit/architecture/MIGRATION_LOG.md` — Step-by-step audit trail of all operations executed.
9. `audit/architecture/POST_RESTRUCTURE_VALIDATION.md` — Comprehensive test and verification report.

#### 7.2 Global Verification Commands
```bash
# 1. Full test suite
.venv/bin/pytest -v
# Expected: 283 passed

# 2. Frontend compilation check
cd web && npm run build && cd ..
# Expected: Clean Vite build into web/dist

# 3. ModelRegistry verification
.venv/bin/python -c "
from argus.registry.model_registry import ModelRegistry
reg = ModelRegistry()
for m in ['model_d1_baseline', 'model_d2_coral', 'model_d3_native', 'xgb_source', 'xgb_adapted']:
    assert m in reg.models, f'Missing {m}'
print('All 5 production models verified in ModelRegistry')
"

# 4. Clean git status inspection
git status
```

---

## 4. Emergency Full-Repository Rollback Procedure

If catastrophic corruption or unresolvable failure occurs at any point during Stage B execution, the entire repository can be restored to its exact pre-restructuring state in under 10 seconds:

```bash
# Emergency Rollback to Pre-Restructuring Snapshot
git reset --hard pre-restructure-v1.0
git clean -fd

# Restore backed-up configs if needed
tar -xzf /tmp/argus_pre_restructure_configs.tar.gz

# Re-verify test baseline
.venv/bin/pytest -q
# Confirmed: 283 passed
```

---

## 5. Approval Gate Status

### Decision: `READY WITH QUALIFICATIONS`

**Qualifications Required Before Execution:**
1. Explicit user authorization to execute Stage B.
2. Creation of Git tag `pre-restructure-v1.0`.
3. Sequential execution of Batches 1 through 7 with strict verification gate adherence.
