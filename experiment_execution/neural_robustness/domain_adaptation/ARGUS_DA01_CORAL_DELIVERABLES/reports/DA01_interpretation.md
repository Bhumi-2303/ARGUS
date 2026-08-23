# ARGUS Domain Adaptation DA-01: Scientific Interpretation & Evaluation Report

**Experiment ID**: `DA-01`  
**Model Family**: FT-Transformer (FTT-SMALL, 17,473 parameters)  
**Adaptation Strategy**: Second-Order Covariance Alignment (CORAL, D1 -> D3)  
**Target Domain**: IEC 60870-5-104 SCADA Telemetry (D3, N=714,453)  
**Audit Date**: August 23, 2026  
**Primary Finding**: **Negative Result — Covariance Alignment Alone Fails to Overcome Cross-Domain Representation Collapse**

---

## 1. Executive Summary & Core Comparison

This experiment tested hypothesis **H1**: whether explicit source-to-target covariance alignment using CORAL (A = C_s^(-1/2) * C_t^(1/2)) can improve cross-domain transfer of the neural FTT-SMALL baseline without increasing model capacity or accessing target test labels.

### Primary Comparison Summary Table

| Metric | B0: FTT-SMALL Baseline | B1: FTT-SMALL + CORAL | Absolute Delta (Δ) | Relative Change (%) | Multi-Seed Stability (Mean ± Std) | Empirical Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ROC-AUC (Seed 42)** | **0.6075** | **0.4441** | -0.1634 | -26.90% | 0.4497 ± 0.0176 | **Severe Degradation (Inversion < 0.50)** |
| **Average Precision (Seed 42)** | **0.2978** | **0.2115** | -0.0863 | -28.98% | 0.2264 ± 0.0155 | **Substantial Degradation** |
| **F1 (Calibrated)** | **0.3724** | **0.3724** | 0.0000 | 0.00% | 0.3724 ± 0.0000 | **Pathological Prior Lock** |
| **MCC (Calibrated)** | **0.0652** | **0.0652** | 0.0000 | 0.00% | 0.0652 ± 0.0000 | **Near-Zero Discrimination** |
| **FPR (Calibrated)** | **96.68%** | **96.68%** | 0.0000 | 0.00% | 96.68% ± 0.00% | **Operationally Unusable** |
| **FNR (Calibrated)** | **0.77%** | **0.77%** | 0.0000 | 0.00% | 0.77% ± 0.00% | **Prior-Dominance Artifact** |

---

## 2. In-Depth Answers to Scientific Questions (Q1 – Q10)

### Q1. Did CORAL improve ROC-AUC?
**Answer**: **NO.**  
CORAL severely degraded global ranking discrimination. On Seed 42, ROC-AUC fell from **0.6075** (B0) to **0.4441** (B1), an absolute drop of -0.1634 (-26.90%). Across all 5 seeds, mean ROC-AUC dropped from **0.5543 ± 0.0402** to **0.4497 ± 0.0176**, demonstrating a statistically significant ranking inversion (p = 0.0028).

### Q2. Did CORAL improve Average Precision (AP)?
**Answer**: **NO.**  
Audited step-function Average Precision dropped from **0.2978** (B0) to **0.2115** (B1) on Seed 42, falling below the attack base rate prior (22.47%). The 5-seed mean AP fell from **0.2576 ± 0.0245** to **0.2264 ± 0.0155** (p = 0.0416).

### Q3. Did CORAL improve MCC?
**Answer**: **NO.**  
At the optimal calibrated threshold, MCC remained identical at **0.0652** across both B0 and B1. This reflects a state of zero discriminative utility where the classifier simply predicts positive for nearly all samples.

### Q4. Did CORAL reduce FPR?
**Answer**: **NO.**  
At the calibrated decision threshold, FPR remained locked at **96.68%** (535,558 false alarms out of 553,944 benign flows). At default threshold θ=0.50, FPR was 100.0%.

### Q5. Did CORAL improve the FPR ≤ 1.0% operating region?
**Answer**: **NO.**  
Under the strict SOC operational constraint (FPR ≤ 1.0%), FTT-SMALL + CORAL achieved **0.00% attack recall** (Precision = 0.0%, Recall = 0.0%, F1 = 0.0%, MCC = 0.0%). The model provides zero operational attack detection at acceptable false alarm rates.

### Q6. Did CORAL actually reduce source-target covariance discrepancy?
**Answer**: **YES (CONFIRMED MATHEMATICALLY).**  
Phase DA-01B/C validated that CORAL achieved an outstanding **99.9959% reduction** in Frobenius covariance distance (||C_s - C_t||_F decreased from **2.600892** to **0.000106**). Thus, representation failure occurred *despite* near-perfect second-order covariance alignment.

### Q7. Is the improvement statistically stable across seeds?
**Answer**: **YES, THE NEGATIVE RESULT IS STATISTICALLY ROBUST.**  
Across all five random seeds (42, 123, 456, 789, 1011), ROC-AUC ranged strictly between **0.4308 and 0.4785** (standard deviation σ = 0.0176). The performance degradation is highly consistent and statistically significant (t = -6.44, p = 0.0028).

### Q8. Does CORAL overcome the ARGUS-4 representation bottleneck?
**Answer**: **NO.**  
The 4-feature representation (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`) suffers from irreversible class-conditional overlap when mapped into target space. Linear covariance transformation preserves this conditional overlap.

### Q9. Is the improvement sufficient to challenge the existing transfer ceiling?
**Answer**: **NO.**  
The cross-domain transfer ceiling remains unbreached. LightGBM (AP = 0.3204, ROC-AUC = 0.6582) and Native SCADA models (F1 = 0.9995, ROC-AUC = 0.9999) decisively outperform cross-domain neural transfer.

### Q10. What does the result imply for the next experiment?
**Answer**: **IMPLICATION FOR NEXT STAGE.**  
Unsupervised linear second-order alignment (CORAL) is mathematically insufficient. The pipeline requires either non-linear adversarial domain alignment (DANN / Gradient Reversal) or protocol-native feature recovery.

---

## 3. Methodological Integrity & Leakage Discipline

- **Zero Test Leakage**: The frozen D3 test partition (N=714,453) was strictly isolated. Target covariance was estimated solely on D3 adaptation telemetry without labels.
- **Audited Metrics**: Evaluated using continuous ranking Average Precision (AP) without trapezoidal distortion.
- **Negative Result Policy**: Preserved with complete scientific fidelity without hyperparameter hacking.
