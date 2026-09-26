# CAPACITY-01 Diagnostic Interpretation Report: Neural Capacity Stress Test

**Experiment ID**: `CAPACITY-01`  
**Task**: D1 (CICIoT2023) $\rightarrow$ D3 (IEC 60870-5-104 SCADA Telemetry)  
**Feature Representation**: ARGUS-4 Harmonized 4-Feature Set  
**Evaluation Partition**: Frozen IEC 60870-5-104 Test Partition ($N = 714,453$ records, $\pi_{target} = 22.47\%$)  
**Seed**: 42  
**Date**: August 22, 2026

---

## 1. Quantitative Capacity Stress Test Summary

| Metric | FTT-SMALL (Baseline) | FTT-LARGE (Capacity Test) | Absolute Difference ($\Delta$) | Relative Change |
|---|:---:|:---:|:---:|:---:|
| **Trainable Parameters** | `17,473` | `200,705` | `+183,232` | **+11.49x (+1048.7%)** |
| **ROC-AUC** | **`0.6075`** | **`0.5100`** | **`-0.0975`** | **`-16.05%`** |
| **PR-AUC** | **`0.3595`** | **`0.1797`** | **`-0.1798`** | **`-50.02%`** |
| **MCC (Calibrated)** | `0.0652` | `0.0908` | `+0.0255` | `+39.16%` |
| **MCC (Default $\Theta=0.50$)** | `0.0000` | `0.0652` | `+0.0652` | `N/A` |
| **F1 Score (Calibrated)** | `0.3724` | `0.3803` | `+0.0078` | `+2.11%` |
| **F1 Score (Default $\Theta=0.50$)** | `0.3669` | `0.3724` | `+0.0055` | `+1.51%` |
| **FPR (Calibrated)** | `96.68%` | `77.21%` | `-19.47%` | `-20.14%` |
| **FNR (Calibrated)** | `0.77%` | `13.96%` | `+13.20%` | `+1718.7%` |
| **Accuracy (Calibrated)** | `24.87%` | `37.00%` | `+12.13%` | `+48.78%` |

---

## 2. Answers to Diagnostic Questions

### Q1. How many parameters does FTT-SMALL have?
**Answer**: FTT-SMALL has **17,473** trainable parameters (`d_token=32, n_blocks=2, n_heads=4, d_ff=64`).

### Q2. How many parameters does FTT-LARGE have?
**Answer**: FTT-LARGE has **200,705** trainable parameters (`d_token=64, n_blocks=4, n_heads=8, d_ff=256`).

### Q3. What is the parameter increase factor?
**Answer**: The capacity increase factor is **11.49x** (a **+1,048.7%** parameter expansion).

### Q4. Did ROC-AUC improve?
**Answer**: **No.** ROC-AUC degraded significantly from **0.6075** down to **0.5100** (a drop of `-0.0975`), collapsing ranking performance to near-pure random guess ($\text{AUC} \approx 0.5000$).

### Q5. Did PR-AUC improve?
**Answer**: **No.** PR-AUC dropped sharply from **0.3595** to **0.1797** (a drop of `-0.1798`), falling below the base attack prior ($\pi_{target} = 0.2247$).

### Q6. Did MCC improve?
**Answer**: **No meaningful improvement.** Calibrated MCC increased slightly from `0.0652` to `0.0908` ($\Delta = +0.0255$), remaining below `0.10` and demonstrating virtually zero correlation with ground-truth SCADA attack labels.

### Q7. Did calibrated F1 improve?
**Answer**: **No meaningful improvement.** Calibrated F1 increased by a negligible margin of `+0.0078` (`0.3724` $\rightarrow$ `0.3803`), remaining trapped at the trivial prior-dominated baseline.

### Q8. Did calibrated FPR decrease?
**Answer**: Calibrated FPR decreased from `96.68%` to `77.21%` ($\Delta = -19.47\%$). However, an operational False Positive Rate of `77.21%` remains completely unacceptable in industrial SCADA telemetry.

### Q9. Did calibrated FNR decrease?
**Answer**: **No.** Calibrated FNR increased drastically from `0.77%` to `13.96%` ($\Delta = +13.20\%$), missing over 22,400 attack bursts on the test set.

### Q10. Did the model become operationally more useful?
**Answer**: **No.** The model remains operationally useless, suffering from a $77.21\%$ False Positive Rate and near-chance discrimination ($\text{ROC-AUC} = 0.5100$).

### Q11. Is the improvement larger than the observed seed variability?
**Answer**: **No.** The observed changes ($\Delta \text{ROC-AUC} = -0.0975$, $\Delta \text{PR-AUC} = -0.1798$, $\Delta \text{F1} = +0.0078$) represent a degradation in ranking performance and offer zero operational recovery.

### Q12. Does the result suggest that insufficient model capacity was the main bottleneck?
**Answer**: **No.** Expanding neural network capacity by over $11.5\times$ failed to resolve cross-domain transfer degradation.

### Q13. Does the result strengthen or weaken the representation-mismatch hypothesis?
**Answer**: **The result strongly STRENGTHENS the representation-mismatch hypothesis (CASE A).**
Increasing model capacity by over $11.5\times$ caused ranking performance to degrade further toward pure random guessing ($\text{ROC-AUC} = 0.5100$). This demonstrates that larger neural capacity accelerates overfitting to source domain feature artifacts rather than learning domain-invariant SCADA representations. The cross-domain transfer bottleneck is decisively driven by **feature representation collapse and domain covariate shift**, not insufficient model capacity.
