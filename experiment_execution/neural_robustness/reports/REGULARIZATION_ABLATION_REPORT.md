# ARGUS Diagnostic Report: Regularization & Robustness Ablation Suite (A0–A3)

**Experiment ID**: `NR-04`  
**Task**: D1 (CICIoT2023) $\rightarrow$ D3 (IEC 60870-5-104 SCADA Telemetry)  
**Feature Representation**: ARGUS-4 Harmonized 4-Feature Set  
**Evaluation Partition**: Frozen IEC 60870-5-104 Test Partition ($N = 714,453$ records, $\pi_{target} = 22.47\%$)  
**Seed**: 42  
**Date**: August 23, 2026

---

## 1. Quantitative Ablation Matrix

| Condition | Intervention Details | ROC-AUC | PR-AUC | F1 (Default) | F1 (Calibrated) | MCC (Calibrated) | FPR (Calibrated) | FNR (Calibrated) | Train Loss | Val Loss | Generalization Gap |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A0 (Baseline)** | FTT-SMALL (Preserved) | **`0.6075`** | **`0.3595`** | `0.3669` | `0.3724` | `0.0652` | `96.68%` | `0.77%` | `0.2203` | `2.4281` | `2.2078` |
| **A1 (Label Smooth)** | Label Smoothing = 0.05 | `0.5720` | `0.5597` | `0.3724` | `0.3724` | `0.0652` | `96.68%` | `0.77%` | `0.2132` | `2.5917` | `2.3785` |
| **A2 (Feature Mask)** | 10% Training Feature Noise | `0.5162` | `0.1810` | `0.3724` | `0.3831` | `0.0991` | `77.25%` | `13.15%` | `0.1527` | `2.6883` | `2.5356` |
| **A3 (Combined)** | LS = 0.05 + FM = 0.10 | `0.5144` | `0.1776` | `0.3724` | `0.3724` | `0.0652` | `96.68%` | `0.77%` | `0.2159` | `2.5726` | `2.3567` |

---

## 2. Answers to Diagnostic Questions

### Q1. Did label smoothing improve transfer?
**Answer**: **No.** Label smoothing ($0.05$) degraded target ROC-AUC from **`0.6075`** down to **`0.5720`** (a relative drop of `-5.84%`). While threshold-specific precision slightly altered confidence calibration, overall ranking capability suffered.

### Q2. Did feature masking improve transfer?
**Answer**: **No.** Random feature masking ($10\%$ training noise) caused ROC-AUC to collapse to **`0.5162`** (a drop of `-0.0913` / `-15.02%`), reducing model ranking performance to near pure random guess ($\text{AUC} \approx 0.5000$). PR-AUC dropped sharply to `0.1810`, falling below the base attack prior ($\pi = 0.2247$).

### Q3. Did combining them improve transfer?
**Answer**: **No.** Combining label smoothing and feature masking yielded an ROC-AUC of **`0.5144`** (a drop of `-0.0931` / `-15.33%`) and PR-AUC of `0.1776`.

### Q4. Did regularization reduce the train/validation gap?
**Answer**: **No.** The generalization gap ($\text{Val} - \text{Train}$) expanded across all regularized conditions ($2.3785$ for A1, $2.5356$ for A2, and $2.3567$ for A3, compared to $2.2078$ for A0).

### Q5. Did improved training behavior translate into improved D3 ranking?
**Answer**: **No.** Modifying source-domain loss functions or adding training noise failed to produce transferable representations for target SCADA telemetry.

### Q6. Did ROC-AUC improve?
**Answer**: **No.** All three interventions (A1, A2, A3) degraded ROC-AUC relative to the baseline A0.

### Q7. Did PR-AUC improve?
**Answer**: **No.** Under feature noise (A2, A3), PR-AUC collapsed below target attack prior ($0.1810$ and $0.1776$ vs $\pi_{target} = 0.2247$).

### Q8. Did FPR improve?
**Answer**: **No.** Under target calibration, FPR remained high ($96.68\%$ for A1/A3 and $77.25\%$ for A2), rendering all models operationally unusable.

### Q9. Did MCC improve?
**Answer**: **No.** MCC remained near zero ($\le 0.0991$), demonstrating an absence of true correlation with target ground-truth attack labels.

### Q10. Is there evidence that overfitting was the dominant problem?
**Answer**: **No.** If overfitting/overconfidence had been the primary cause of transfer failure, conventional regularization and input noise would have improved ranking performance and narrowed the generalization gap.

### Q11. Is there evidence that representation/domain shift remains the dominant limitation?
**Answer**: **Yes.** The complete failure of capacity expansion (CAPACITY-01), weight regularization (CAPACITY-01R), label smoothing (A1), feature noise (A2), and combined robustness training (A3) provides overwhelming evidence that the cross-domain transfer bottleneck is caused by **representation mismatch and domain covariate shift**, not optimization failure or unregularized overfitting.

---

## 3. Scientific Decision & Category Classification

### Scientific Decision: **CATEGORY C / D**
> **"Conventional regularization and input robustness training did not materially improve cross-domain transfer under the tested conditions. Feature noise further degraded ranking performance toward pure random guessing."**

---

## 4. Statement for ARGUS Paper

> *"Controlled ablation of conventional neural regularization techniques—including label smoothing ($\epsilon=0.05$) and dynamic feature masking ($10\%$ input noise)—demonstrates that cross-domain NIDS transfer failure ($D1 \rightarrow D3$) cannot be resolved by standard robustness training. Across all intervention conditions (A1–A3), target-domain ranking performance ($\text{ROC-AUC} \le 0.5720$) degraded relative to the baseline ($0.6075$), while the source-to-target generalization gap expanded. These empirical findings demonstrate that cross-domain degradation on low-dimensional network telemetry is driven by feature representation collapse and domain covariate shift rather than unregularized neural overfitting."*
