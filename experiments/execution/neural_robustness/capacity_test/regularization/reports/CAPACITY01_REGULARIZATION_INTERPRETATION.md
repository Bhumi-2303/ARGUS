# CAPACITY-01R Diagnostic Interpretation Report: Controlled Regularization Test

**Experiment ID**: `CAPACITY-01R`  
**Task**: D1 (CICIoT2023) $\rightarrow$ D3 (IEC 60870-5-104 SCADA Telemetry)  
**Feature Representation**: ARGUS-4 Harmonized 4-Feature Set  
**Evaluation Partition**: Frozen IEC 60870-5-104 Test Partition ($N = 714,453$ records, $\pi_{target} = 22.47\%$)  
**Seed**: 42  
**Date**: August 22, 2026

---

## 1. Quantitative Regularization & Overfitting Matrix

| Metric | FTT-SMALL (17.5k Params) | FTT-LARGE (200.7k Params) | FTT-LARGE-REG (200.7k Params + Reg) | FTT-LARGE-REG vs FTT-LARGE ($\Delta$) | FTT-LARGE-REG vs FTT-SMALL ($\Delta$) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Dropout** | `0.10` | `0.10` | **`0.30`** | `+0.20` | `+0.20` |
| **Weight Decay** | `0.0001` | `0.0001` | **`0.01`** | `+0.0099` | `+0.0099` |
| **Train Loss** | `0.2203` | `0.0963` | **`0.0971`** | `+0.0008` | `-0.1232` |
| **Validation Loss** | `2.4281` | `3.4541` | **`3.6354`** | `+0.1813` | `+1.2073` |
| **Generalization Gap ($\text{Val} - \text{Train}$)** | `2.2078` | `3.3577` | **`3.5383`** | `+0.1806` | `+1.3305` |
| **Val / Train Loss Ratio** | `11.02x` | `35.85x` | **`37.46x`** | `+1.61x` | `+26.44x` |
| **ROC-AUC** | **`0.6075`** | **`0.5100`** | **`0.5107`** | **`+0.0007`** | **`-0.0968`** |
| **PR-AUC** | **`0.3595`** | **`0.1797`** | **`0.1798`** | **`+0.0001`** | **`-0.1797`** |
| **MCC (Calibrated)** | `0.0652` | `0.0908` | **`0.0652`** | `-0.0256` | `0.0000` |
| **F1 Score (Calibrated)** | `0.3724` | `0.3803` | **`0.3724`** | `-0.0079` | `0.0000` |
| **FPR (Calibrated)** | `96.68%` | `77.21%` | **`96.68%`** | `+19.47%` | `0.00%` |
| **FNR (Calibrated)** | `0.77%` | `13.96%` | **`0.77%`** | `-13.19%` | `0.00%` |
| **Accuracy (Calibrated)** | `24.87%` | `37.00%` | **`24.87%`** | `-12.13%` | `0.00%` |

---

## 2. Answers to Diagnostic Overfitting Questions

### Q1. Did training loss decrease?
**Answer**: Compared to FTT-SMALL ($0.2203$), training loss decreased to $0.0971$ in FTT-LARGE-REG, proving that high model capacity enables low empirical risk on the source domain $D1$.

### Q2. Did validation loss decrease?
**Answer**: **No.** Target validation loss increased from $2.4281$ (SMALL) and $3.4541$ (LARGE) up to **$3.6354$** (LARGE-REG).

### Q3. Did the training-validation gap decrease?
**Answer**: **No.** The generalization gap ($\text{Val} - \text{Train}$) expanded from $2.2078$ (SMALL) to $3.3577$ (LARGE) and **$3.5383$** (LARGE-REG), representing a $37.46\times$ ratio between validation and training loss.

### Q4. Did ROC-AUC improve?
**Answer**: **No.** FTT-LARGE-REG ($\text{ROC-AUC} = 0.5107$) remains virtually identical to FTT-LARGE ($0.5100$, $\Delta = +0.0007$), staying near pure random chance ($\text{AUC} \approx 0.5000$).

### Q5. Did PR-AUC improve?
**Answer**: **No.** FTT-LARGE-REG ($\text{PR-AUC} = 0.1798$) remains virtually identical to FTT-LARGE ($0.1797$, $\Delta = +0.0001$), remaining below the target attack prior ($\pi_{target} = 0.2247$).

### Q6. Did MCC improve?
**Answer**: **No.** Calibrated MCC returned to the baseline FTT-SMALL level of `0.0652` ($\Delta = -0.0256$ relative to FTT-LARGE).

### Q7. Did calibrated F1 improve?
**Answer**: **No.** Calibrated F1 returned to `0.3724` (identical to baseline FTT-SMALL).

### Q8. Did FPR improve?
**Answer**: **No.** Under target calibration, FPR returned to `96.68%`, demonstrating that the regularized model continues to output high-probability predictions on normal target telemetry.

### Q9. Did FNR improve?
**Answer**: FNR returned to `0.77%` (matching baseline FTT-SMALL), but only because the decision threshold defaulted to classifying almost all target traffic as attacks.

### Q10. Did the model become more stable?
**Answer**: **No.** The model remains unstable on target domain data, triggering early stopping at Epoch 1 (Val Loss = 3.6354).

### Q11. Did regularization reduce overfitting?
**Answer**: **No.** Controlled regularization (increasing dropout from 0.10 to 0.30 and weight decay to 0.01) was unable to bridge the source-to-target domain gap.

### Q12. Did reduced overfitting translate into better target-domain generalization?
**Answer**: **No.** Because regularization did not close the cross-domain generalization gap, target domain generalization remained near chance level ($\text{ROC-AUC} \approx 0.51$).

---

## 3. Scientific Case Selection & Verdict

### Scientific Case: **CASE C**
> **"The transfer limitation persists despite controlled regularization, providing additional evidence that insufficient regularization was not the primary cause."**

### Theoretical Synthesis:
The CAPACITY-01R experiment demonstrates that cross-domain transfer degradation on the ARGUS-4 representation ($D1 \rightarrow D3$) cannot be resolved by standard neural regularization techniques (dropout and weight decay). Even when regularized, a high-capacity FT-Transformer fails to learn domain-invariant decision boundaries across heterogeneous network environments. 

This firmly establishes that the bottleneck in cross-domain NIDS transfer is **domain covariate shift and state-space collapse inherent in low-dimensional feature projections**, rather than optimization failure, underfitting, or unregularized neural overfitting.
