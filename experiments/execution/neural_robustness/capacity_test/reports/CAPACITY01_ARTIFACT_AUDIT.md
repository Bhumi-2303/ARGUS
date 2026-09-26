# CAPACITY-01 Artifact Audit Report

**Audit Date**: August 22, 2026  
**Target File**: `predictions/CAPACITY01_seed42_predictions.csv`  
**Evaluation Target Partition**: Frozen IEC 60870-5-104 Test Partition ($N = 714,453$ records, $\pi_{target} = 22.47\%$)  
**Audit Status**: **PASSED (100% VERIFIED & CONSISTENT)**

---

## 1. Audit & Recomputation Verification Matrix

| Verification Item | Stored Artifact Metric | Recomputed Metric | Absolute Difference ($\Delta$) | Audit Verdict |
|---|:---:|:---:|:---:|:---:|
| **Test Record Count ($N$)** | $714,453$ | $714,453$ | $0$ | **PASS** |
| **Ground Truth Attacks** | $160,509$ | $160,509$ | $0$ | **PASS** |
| **Ground Truth Normals** | $553,944$ | $553,944$ | $0$ | **PASS** |
| **ROC-AUC** | $0.509999$ | $0.509999$ | $0.000000$ | **PASS** |
| **PR-AUC** | $0.179683$ | $0.179683$ | $0.000000$ | **PASS** |
| **Default Threshold ($\Theta=0.50$) TN** | $18,386$ | $18,386$ | $0$ | **PASS** |
| **Default Threshold ($\Theta=0.50$) FP** | $535,558$ | $535,558$ | $0$ | **PASS** |
| **Default Threshold ($\Theta=0.50$) FN** | $1,229$ | $1,229$ | $0$ | **PASS** |
| **Default Threshold ($\Theta=0.50$) TP** | $159,280$ | $159,280$ | $0$ | **PASS** |
| **Default Threshold Accuracy** | $0.248674$ | $0.248674$ | $0.000000$ | **PASS** |
| **Default Threshold F1** | $0.372434$ | $0.372434$ | $0.000000$ | **PASS** |
| **Default Threshold MCC** | $0.065218$ | $0.065218$ | $0.000000$ | **PASS** |
| **Default Threshold FPR** | $0.966809$ | $0.966809$ | $0.000000$ | **PASS** |
| **Default Threshold FNR** | $0.007657$ | $0.007657$ | $0.000000$ | **PASS** |
| **Calibrated Threshold ($\Theta=0.99$) TN** | $126,238$ | $126,238$ | $0$ | **PASS** |
| **Calibrated Threshold ($\Theta=0.99$) FP** | $427,706$ | $427,706$ | $0$ | **PASS** |
| **Calibrated Threshold ($\Theta=0.99$) FN** | $22,410$ | $22,410$ | $0$ | **PASS** |
| **Calibrated Threshold ($\Theta=0.99$) TP** | $138,099$ | $138,099$ | $0$ | **PASS** |
| **Calibrated Threshold Accuracy** | $0.369985$ | $0.369985$ | $0.000000$ | **PASS** |
| **Calibrated Threshold F1** | $0.380274$ | $0.380274$ | $0.000000$ | **PASS** |
| **Calibrated Threshold MCC** | $0.090759$ | $0.090759$ | $0.000000$ | **PASS** |
| **Calibrated Threshold FPR** | $0.772111$ | $0.772111$ | $0.000000$ | **PASS** |
| **Calibrated Threshold FNR** | $0.139618$ | $0.139618$ | $0.000000$ | **PASS** |

---

## 2. Independent Audit Conclusion

1. **Prediction Integrity**: `predictions/CAPACITY01_seed42_predictions.csv` contains exact, uncorrupted predictions ($N = 714,453$) generated from the FTT-LARGE checkpoint on Seed 42.
2. **Metric Consistency**: Recomputed scalar metrics, confusion matrices, ROC curves, and PR curves match stored metrics with zero discrepancy ($\Delta = 0.000000$).
3. **Audit Verdict**: **PASS**. Retraining or prediction regeneration is NOT required. CAPACITY-01 artifacts are verified intact.
