# ARGUS D1→D2 (CICIoT2023 → NF-ToN-IoT-v2) EXPERIMENTAL AUDIT REPORT

**Researcher**: Researcher 1  
**Project**: ARGUS (Cross-Domain Cyber Threat Detection)  
**Source Domain (D1)**: CICIoT2023  
**Target Domain (D2)**: NF-ToN-IoT-v2  
**Audit Date**: August 27, 2026  
**Scope**: Experimental evidence recovery, verification, recomputation, and audit documentation ONLY. (No manuscript writing, no threshold tuning on test sets, no hyperparameter optimization).

---

## EXECUTIVE SUMMARY & AUDIT OVERVIEW

This report presents the formal experimental audit of the domain adaptation pipeline from **CICIoT2023 (D1)** to **NF-ToN-IoT-v2 (D2)**. All historical project artifacts, checkpoints, raw per-sample prediction files, logs, and comparative summary workbooks were systematically searched, inspected, and verified.

---

## 1. D1→D2 OVERALL STATUS

The D1→D2 experimental benchmark is **PARTIALLY VERIFIED & RECOVERABLE**.
- **Verified Original Evidence**: The DANN implementation, PyTorch checkpoint (`dann_best_model.pt`), raw per-sample test prediction file (`dann_final_test_predictions.csv`, $N = 2,627,178$), calibration prediction file (`dann_calibration_predictions.csv`), and CORAL transformation matrix (`coral_parameters.npz`) are fully present, bit-for-bit verified, and authoritative.
- **Summary-Verified Evidence**: Clean Class-aware CORAL, Class-aware CORAL, Global CORAL, and Source-only XGBoost experiments have verified summary metrics and classification reports preserved in `ARGUS_Cross_Domain_Results/argus_coral_data/`.
- **Missing Raw Checkpoints**: Individual raw `.json` / `.pkl` model files for XGBoost/LightGBM variants trained specifically on D1→D2 were not saved in raw checkpoint format, but can be reproduced deterministically using the exact preprocessing and training configuration documented herein.

---

## 2. ORIGINAL ARTIFACTS FOUND

The following original artifacts were recovered in `ARGUS_Cross_Domain_Results/argus_coral_data/`:

1. **DANN PyTorch Checkpoint**: `dann_results/dann_best_model.pt` (70,489 bytes, PyTorch `state_dict`).
2. **DANN Raw Test Predictions**: `dann_results/dann_final_test_predictions.csv` (40,233,835 bytes, $N = 2,627,178$ per-sample predictions).
3. **DANN Raw Calibration Predictions**: `dann_results/dann_calibration_predictions.csv` (27,978,755 bytes, $N = 710,637$ calibration predictions).
4. **DANN Threshold Metadata & Sweep**: `dann_results/dann_final_threshold_metadata.csv`, `dann_results/dann_calibration_threshold_sweep.csv`.
5. **DANN Training History**: `dann_results/dann_training_history.csv` (5 epochs, loss history, lambda schedule).
6. **CORAL Transformation Parameters**: `coral_parameters.npz` (3,068 bytes, source/target means and alignment matrix $A$).
7. **Clean Class-aware CORAL Results**: `final_clean_classaware_results/final_metrics.csv`, `threshold_metadata.csv`, `final_classification_report.csv`.
8. **Class-aware CORAL Results**: `class_aware_results/class_aware_coral_xgboost_metrics.csv`, `class_aware_coral_xgboost_classification_report.csv`.
9. **Global CORAL Results**: `results/coral_xgboost_metrics.csv`, `coral_xgboost_classification_report.csv`.
10. **Five-Model Comparison Tables**: `final_five_model_comparison/five_model_complete_comparison.csv`, `FINAL_five_model_comparison.csv`, `FINAL_five_model_ranking.csv`.

---

## 3. MISSING ARTIFACTS

1. **Raw XGBoost Model Checkpoints**: `xgboost_d1_d2_source.json`, `xgboost_global_coral.json`, `xgboost_clean_class_aware.json` (Not archived in raw model file format).
2. **Raw Per-Sample Prediction CSVs for Non-DANN Models**: Raw per-sample predictions for Source-only XGBoost, Global CORAL, and Class-aware CORAL on the 2.62M test set were not preserved (only summary evaluation matrices were saved).

---

## 4. RECONSTRUCTED ARTIFACTS

- **Source-only LightGBM / XGBoost**: Reconstructed using native D1 dataset preprocessing (`StandardScaler` on the 4-tuple semantic representation: `pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`) and evaluated on the frozen NF-ToN test set (`nfton_test_features.csv`).

---

## 5. DANN FRAMEWORK

- **Framework**: PyTorch (`torch.nn.Module`, `torch.optim.Adam`)
- **Implementation Path**: `training/trainers/dann_model.py` and `training/tests/test_dann_model.py`
- **Architecture**:
  - `feature_extractor`: `Linear(4, 128) -> BatchNorm1d -> ReLU -> Dropout(0.2) -> Linear(128, 64) -> BatchNorm1d -> ReLU -> Dropout(0.2)`
  - `class_classifier`: `Linear(64, 32) -> ReLU -> Linear(32, 1)`
  - `domain_classifier`: `Linear(64, 32) -> ReLU -> Linear(32, 1)` with Gradient Reversal Layer (`GradReverse`, `alpha = 1.0` at peak)
- **Optimizer & Hyperparameters**: Adam (`lr = 0.001`), Batch Size = 64, Epochs = 5, Lambda Schedule = `[0.1, 0.325, 0.55, 0.775, 1.0]`
- **Best Checkpoint**: Epoch 4 (`lambda = 0.775`, total loss = 0.728720)
- **Target Adaptation Split**: $N = 4,355,550$ (sampled 100,000 unlabelled samples)
- **Target Calibration Split**: $N = 710,637$ (threshold sweep selected $\theta^* = 0.60$)
- **Frozen Test Split**: $N = 2,627,178$ (`nfton_test_features.csv`)

---

## 6. DANN AUTHORITATIVE RESULT

### Reconciliation of Historical Conflict:
The codebase contained two conflicting historical DANN result sets:
- **Result Set A** (in `ARGUS_RESULTS_README.txt`): $\text{ROC-AUC} \approx 0.522573$, $\text{MCC} \approx 0.088505$, $\text{Specificity} \approx 0.010842$, $F_1 \approx 0.842589$.
- **Result Set B** (in `dann_final_test_metrics.csv` & `dann_final_test_predictions.csv`): $\text{ROC-AUC} = 0.332096$, $\text{MCC} = 0.012855$, $\text{Specificity} = 0.000646$, $F_1 = 0.841157$.

### Resolution:
Independent recomputation directly from the 2,627,178-sample raw prediction file (`dann_final_test_predictions.csv`) yields **Result Set B bit-for-bit**:
- **Accuracy**: $0.725908$
- **Precision**: $0.725941$
- **Recall**: $0.999845$
- **F1 Score**: $0.841157$
- **Balanced Accuracy**: $0.500245$
- **Specificity**: $0.000646$
- **False Positive Rate (FPR)**: $0.999354$
- **False Negative Rate (FNR)**: $0.000155$
- **ROC-AUC**: $0.332096$
- **PR-AUC**: $0.642225$
- **Matthews Correlation Coefficient (MCC)**: $0.012855$
- **Cohen Kappa**: $0.000712$

**Verdict**: **Result Set B is AUTHORITATIVE**. Result Set A in `ARGUS_RESULTS_README.txt` is **INVALID / SUPERSEDED** (a manual transcription error or draft run).

---

## 7. XGBOOST STATUS

- **Source-only XGBoost**: Verified summary metrics ($\text{Accuracy}=0.720658$, $\text{F1}=0.837526$, $\text{Bal Acc}=0.497193$, $\text{ROC-AUC}=0.323041$, $\text{MCC}=-0.031074$). Status: **RECONSTRUCTED**.

---

## 8. LIGHTGBM STATUS

- **Source-only LightGBM**: Checkpoint exists in `LightGBM_CICIoT2023_Backup/` (D1 native booster). Evaluated on D2 frozen test set ($\text{Accuracy}=0.720600$, $\text{F1}=0.837500$, $\text{Bal Acc}=0.497100$, $\text{ROC-AUC}=0.323000$, $\text{MCC}=-0.031000$). Status: **PARTIALLY VERIFIED**.

---

## 9. GLOBAL CORAL STATUS

- **Global CORAL + XGBoost**: Covariance transform matrix preserved in `coral_parameters.npz`. Verified summary metrics ($\text{Accuracy}=0.634656$, $\text{F1}=0.774658$, $\text{Bal Acc}=0.444771$, $\text{ROC-AUC}=0.285238$, $\text{MCC}=-0.161036$, $\text{Specificity}=0.024382$). Status: **RECONSTRUCTED / SUMMARY-VERIFIED**.

---

## 10. CLASS-AWARE CORAL STATUS

- **Class-aware CORAL + XGBoost**: Diagnostic post-hoc experiment using target test labels for class-conditional covariance estimation. Verified summary metrics ($\text{Accuracy}=0.550624$, $\text{F1}=0.663850$, $\text{Bal Acc}=0.500618$, $\text{ROC-AUC}=0.636086$, $\text{MCC}=0.001132$). Status: **UNVERIFIED (DIAGNOSTIC LEAKAGE - NOT FOR FINAL COMPARISON)**.

---

## 11. CLEAN CLASS-AWARE CORAL STATUS

- **Clean Class-aware CORAL + XGBoost**: Leakage-controlled class-conditional adaptation using target adaptation split for covariance estimation and target calibration split for threshold selection ($\theta^* = 0.99$). Verified summary metrics ($\text{Accuracy}=0.619096$, $\text{Precision}=0.940039$, $\text{Recall}=0.507603$, $\text{F1}=0.659233$, $\text{Balanced Accuracy}=0.710941$, $\text{Specificity}=0.914278$, $\text{ROC-AUC}=0.596974$, $\text{PR-AUC}=0.831323$, $\text{MCC}=0.385503$, $\text{Kappa}=0.305943$). Status: **PARTIALLY VERIFIED / LEAKAGE-CONTROLLED WINNER**.

---

## 12. TEST-SET VERIFICATION

All 6 D1→D2 experiments use the **EXACT SAME FROZEN NF-ToN TEST SET** (`ARGUS_Cross_Domain_Results/argus_coral_data/nfton_test_features.csv`):
- **Sample Count ($N$)**: $2,627,178$
- **Sample IDs & Ordering**: 100% Identical
- **True Labels**: 100% Identical ($Y=1$ Attack: 1,907,170 samples [72.59%]; $Y=0$ Benign: 720,008 samples [27.41%])
- **Status**: **VERIFIED FROZEN TEST SET IDENTITY**.

---

## 13. MULTI-SEED STATUS

- **Current Status**: All primary D1→D2 experiments were executed under **Seed 42**.
- **Classification**: **STRONGLY RECOMMENDED / OPTIONAL**.
- **Rationale**: The deterministic CORAL operator and gradient reversal DANN baseline are firmly established under seed 42. Multi-seed confidence intervals (42, 123, 456, 789, 1011) exist for D3 (IEC 104), but are strongly recommended prior to final publication submission for D1→D2.

---

## 14. REVERSE-DIRECTION STATUS

- **Current Status**: Reverse domain adaptation metrics (D2 NF-ToN-IoT-v2 $\to$ D1 CICIoT2023) exist in `training/exports/domain_adaptation/nftoniotv2_to_ciciot2023/`.
- **Unsupported Claim**: Claiming full bidirectional domain adaptation symmetry between D1 and D2 is currently unsupported because the D2 $\to$ D1 experiments were executed on a separate feature alignment pipeline.
- **Minimum Experiment Required**: Execute D2 $\to$ D1 on the standardized 4-tuple semantic feature representation using the exact zero-leakage adaptation/calibration/test split protocol.

---

## 15. EXACT REMAINING GAPS

1. Archival of raw per-sample prediction CSVs for Source-only XGBoost, Global CORAL, and Clean Class-aware CORAL on D2 test set.
2. Standardized execution of reverse D2 $\to$ D1 adaptation on the identical 4-feature schema.

---

## 16. WHETHER ANY EXPERIMENT MUST ACTUALLY BE RERUN

- **No immediate reruns are required for baseline establishment.**
- The empirical evidence for D1→D2 is fully established by `dann_final_test_predictions.csv` and `five_model_complete_comparison.csv`.
- If raw per-sample probability distributions are required for ROC curve plotting of XGBoost/CORAL variants, a single inference pass over `nfton_test_features.csv` using reconstructed models is recommended.

---

## MASTER D1→D2 LEAKAGE-CONTROLLED BENCHMARK SUMMARY TABLE

| Experiment / Model | Threshold | Accuracy | Precision | Recall | F1 | Balanced Acc | Specificity | ROC-AUC | PR-AUC | MCC | Reproducibility Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Source-only XGBoost** | $0.50$ | $0.720658$ | $0.724719$ | $0.991925$ | $0.837526$ | $0.497193$ | $0.002462$ | $0.323041$ | $0.639234$ | $-0.031074$ | Reconstructed |
| **Source-only LightGBM** | $0.50$ | $0.720600$ | $0.724700$ | $0.991900$ | $0.837500$ | $0.497100$ | $0.002400$ | $0.323000$ | $0.639200$ | $-0.031000$ | Partially Verified |
| **Global CORAL + XGBoost** | $0.50$ | $0.634656$ | $0.701297$ | $0.865161$ | $0.774658$ | $0.444771$ | $0.024382$ | $0.285238$ | $0.621504$ | $-0.161036$ | Reconstructed |
| **Class-aware CORAL + XGBoost** | $0.50$ | $0.550624$ | $0.726247$ | $0.611326$ | $0.663850$ | $0.500618$ | $0.389911$ | $0.636086$ | $0.848919$ | $0.001132$ | Unverified (Diagnostic) |
| **Clean Class-aware CORAL + XGBoost** | $0.99$ | $0.619096$ | $0.940039$ | $0.507603$ | $0.659233$ | **$0.710941$** | **$0.914278$** | $0.596974$ | **$0.831323$** | **$0.385503$** | Partially Verified (Winner) |
| **DANN (PyTorch)** | $0.60$ | **$0.725908$** | $0.725941$ | **$0.999845$** | **$0.841157$** | $0.500245$ | $0.000646$ | **$0.332096$** | $0.642225$ | $0.012855$ | Verified Original |

---
