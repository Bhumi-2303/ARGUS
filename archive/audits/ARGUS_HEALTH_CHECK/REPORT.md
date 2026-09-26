# ARGUS Health Check Report

## Executive Summary
- **Runs**: Python 3.14 on Linux, module imports (torch, xgboost) are clean, and end-to-end framework execution (e.g. `generate_poster.py`) exits cleanly with 100% metric reproducibility.
- **Broken**: The primary cross-domain datasets, raw prediction CSVs, and model checkpoints were aggressively wiped from history (`ARGUS_HISTORY_REMOVE.txt`), breaking all local metric recomputation.
- **Broken**: Explicit label leakage (`y_sub * 0.25`) exists in protocol-aware feature generation (`i_msg_ratio`), though ablation shows the signal survives its removal.
- **Blocks Module**: Transfer probabilities are degenerate (a single value of 0.759 dominates 70% of rows), preventing calibrated risk scores.
- **Blocks Module**: All 5 autonomous defense agents are non-functional stubs overriding `BaseAgent`, missing core reasoning logic.

---

## 1. Component Status

| Component | Status | Evidence | File Paths |
| :--- | :--- | :--- | :--- |
| **Environment** | 🟢 GREEN | Python 3.14.7, 7.5GB RAM, 159G free disk. Imports succeed. | `ARGUS_HEALTH_CHECK/requirements.txt` |
| **Data Inventory** | 🔴 RED | Raw predictions and datasets completely deleted by filter-repo. | `ARGUS_HISTORY_REMOVE.txt` |
| **Reproducibility** | 🟢 GREEN | `generate_poster.py` runs twice identically; previous audit confirms 0/1000 divergences. | `generate_poster.py` |
| **Data Integrity (Frozen)**| 🟡 YELLOW | Feature space quantization confirmed (only 1574 unique tuples across 571k rows). | `verification/probability_distribution_report.md` |
| **Metric Recomputation** | 🔴 RED | Cannot recompute from raw files (they are missing). Known discrepancy: DANN 0.3321 vs 0.5226. | `ARGUS_D1_D2_AUDIT/reported_vs_recomputed.csv` |
| **Leakage Scan** | 🔴 RED | `y_sub` used directly in `i_msg_ratio`. Rolling features computed post-shuffle. | `scripts/run_rep01_experiments.py` |
| **Module Readiness** | 🔴 RED | Threat, Risk, Decision, Context, and Data agents are all stubs. | `src/argus/agents/**/agent.py` |
| **Documentation Drift** | 🟡 YELLOW | DANN ROC-AUC 0.5226 remains in recomputed CSVs and is noted as stale. | `ARGUS_D1_D2_AUDIT/reported_vs_recomputed.csv` |

---

## 2. Ranked Blockers

1. **Agent Implementation (STUBs)**
   - *Issue*: The 5-day module requires functioning agents, but `src/argus/agents/*/agent.py` contain only empty `BaseAgent` class definitions.
   - *Command*: `cat src/argus/agents/threat_analysis/agent.py | grep -E "class|def|TODO"`
2. **Probability Degeneracy (Risk Module Blocker)**
   - *Issue*: 70% of the D2 CORAL transfer model's predictions output exactly $\hat{p} = 0.758727$, rendering downstream risk calibration impossible.
   - *Command*: Checked via documentation in `verification/probability_distribution_report.md`. (Raw probabilities are missing).
3. **Data & Checkpoint Erasure**
   - *Issue*: Raw datasets, predictions, and `.pt` checkpoints were permanently removed to save space, preventing local 1% sample execution and recomputation.
   - *Command*: `cat ARGUS_HISTORY_REMOVE.txt`

---

## 3. Missing Files
The following files are expected for a full audit but are missing (verified via `find` and `ARGUS_HISTORY_REMOVE.txt`):
- `dann_final_test_predictions.csv` (MISSING)
- `source_xgb_predictions.csv` (MISSING)
- `final_clean_classaware_results/predictions.csv` (MISSING)
- All `.pt` model checkpoints (e.g., DANN checkpoints) (MISSING)
- *Note: `DA01_covariance_matrices.npz` (CORAL parameters) and `reported_vs_recomputed.csv` ARE present.*

---

## 4. Leakage Scan Results
- **a. Feature-building Label Touch**: [OBSERVED] `df_r2["i_msg_ratio"] = np.clip((df_sub["Tot Fwd Pkts"].values * 0.45 + (y_sub * 0.25)) ...)` in `run_rep01_experiments.py:255`.
- **b. Rolling Features Post-Shuffle**: [OBSERVED] `train_test_split` occurs at line 213, and `rolling(window=10)` is applied at line 267 on the already shuffled indices.
- **c. Test Set Tuning**: [NOT CHECKED] Could not run hyperparameter scripts due to missing raw datasets.
- **d. Class-aware CORAL Labels**: [INFERRED] Test labels were explicitly used to estimate target class-conditional covariances (confirmed via `FINAL_PAPER_READINESS_REPORT.md` Section 5). This contradicts "Target_Labels_Used_For_Training = No".
- **e. Protocol Feature Removal Survival**: [INFERRED] Yes, `FINAL_PAPER_READINESS_REPORT.md` Section 9 confirms ROC-AUC = 0.9999 survives independent ablation of `i_msg_ratio`.

---

## 5. Decisions Needed From Me
1. Do you have a cloud backup of the raw datasets and `.pt` checkpoints, or should the module development proceed strictly using synthetic/dummy test files?
2. Since the cross-domain probabilities are heavily degenerate (flat at 0.759), should we implement Platt scaling/Isotonic regression in the Risk Agent, or stick to native D3 models for the demo?
3. Which of the 5 agent stubs should be prioritized for implementation first for the 5-day module demo?
4. Do you want to fix the `run_rep01_experiments.py` script to remove the `y_sub` label leakage, or simply report the ablated results?
5. The historical DANN ROC-AUC (0.5226) is definitively invalid; should I mass-replace it across all documentation drafts with 0.3321?
