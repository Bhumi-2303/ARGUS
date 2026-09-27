# ARGUS Verified Results Manifest

This directory contains the consolidated, authoritative, and bit-for-bit verified evaluation results backing the primary empirical findings and publication tables of the ARGUS project.

---

## Verified Result Files Index

| File Name | Backed Publication Table / Figure | Protocol Status | Rationale & Verification |
| :--- | :--- | :--- | :--- |
| **`five_model_complete_comparison.csv`** | **Master D1→D2 Benchmark Table** (Table 2 & Table 6) | **Leakage-Controlled** | Master evaluation summary comparing Source-only XGBoost, Global CORAL, Diagnostic Class-aware CORAL, Clean Class-aware CORAL, and DANN on the frozen 2.62M NF-ToN test set. |
| **`dann_final_test_metrics.csv`** | **D1→D2 DANN Authoritative Performance** (Section 6) | **Leakage-Controlled** | Bit-for-bit verified metric table matching raw per-sample DANN predictions ($N = 2,627,178$, $\text{ROC-AUC} = 0.332096$, $\text{MCC} = 0.012855$, $F_1 = 0.841157$). |
| **`dann_final_test_predictions.csv`** | **D1→D2 Raw Per-Sample Predictions** | **Leakage-Controlled** | Full $N = 2,627,178$ per-sample probability predictions for the DANN model evaluated on frozen `nfton_test_features.csv`. |
| **`d3_native_threshold_sweep.csv`** | **D3 Native Operational Curves & Operating Points** (Figure 4 & Table 5) | **Zero-Leakage Frozen** | Complete decision threshold sweep on Domain 3 (IEC 60870-5-104) evaluating FPR vs Recall operational trade-offs under target calibration density. |
| **`SHAP_vs_Target_Gain.csv`** | **SHAP vs Target Gain Disconnect** (Figure 5 & Table 10) | **Zero-Leakage Frozen** | Quantifies feature importance disconnect where top source-domain feature (`log_pkt_max`, 37.5%) provides negligible predictive gain in SCADA target domain. |

---

## Data Protocol Summary

1. **Adaptation Partition**: Used for unsupervised or class-conditional covariance alignment ($N = 8.41\text{M}$ for D2; $N = 2.29\text{M}$ for D3).
2. **Calibration Partition**: Used exclusively for decision threshold selection $\theta^*$ (e.g. $\text{argmax MCC}$ on $N = 2.10\text{M}$ for D2; $N = 571\text{k}$ for D3).
3. **Frozen Test Partition**: Isolated held-out test set used strictly for final reported metrics ($N = 2.63\text{M}$ for D2; $N = 714\text{k}$ for D3). No test set labels or feature statistics were accessed during adaptation or threshold selection.

---

## Metric Discrepancy & Verification Log

| Metric | Raw Prediction Value (`dann_final_test_predictions.csv`) | Narrative Summary Draft (`ARGUS_RESULTS_README.txt`) | Authoritative Source & Resolution Rationale |
| :--- | :--- | :--- | :--- |
| **Source-only XGBoost Metrics** | **Manually appended** | **Missing row from 5-Model Comparison** | **`five_model_complete_comparison.csv` (2026-09-27)** — Discovered that the CSV was missing the Source-only XGBoost baseline entirely due to manual assembly of the CSV file. Restored metrics using `FINAL_D1_D2_AUDIT.md` as provenance (MCC = -0.031074). |
| **DANN ROC-AUC** | **`0.33209554`** | `0.522573` | **`dann_final_test_predictions.csv` (Raw per-sample probabilities)** — Recomputed ROC-AUC across $N=2,627,177$ samples yields $0.33209554$ exactly. Narrative summary draft in `ARGUS_RESULTS_README.txt` was an unverified early draft. |
| **DANN Specificity** | **`0.00064560`** ($0.06456\%$) | `0.010842` ($1.084\%$) | **`dann_final_test_predictions.csv` (Raw predictions confusion matrix)** — $TN=465$, $FP=719,792$. Specificity is near-zero ($0.00064560 < 0.05$), confirming complete representation collapse. |
| **DANN MCC** | **`0.01285487`** | `0.088505` | **`dann_final_test_predictions.csv` (Raw predictions)** — Recomputed MCC equals $0.01285487$, confirming loss of discriminative power. |

