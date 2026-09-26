# N1 Diagnostic Interpretation Report: FT-Transformer vs LightGBM (D1 → D3 Transfer)

**Experiment ID**: `NR-01` (N1 Component)  
**Source Domain**: D1 (CICIoT2023)  
**Target Domain**: D3 (IEC 60870-5-104 SCADA Telemetry)  
**Feature Set**: ARGUS-4 Harmonized 4-Feature Set  
**Seeds Evaluated**: 5 Seeds (`[42, 123, 456, 789, 1011]`)  
**Target Test Set**: Frozen $N = 714,453$ records ($\pi_{target} = 22.47\%$)

---

## 1. Quantitative Benchmark Comparison

| Metric | LightGBM GBDT (Existing Frozen Baseline) | FT-Transformer Neural (New Robustness Run) | Absolute Difference ($\Delta$) | Relative Change |
|---|:---:|:---:|:---:|:---:|
| **ROC-AUC** | $0.5442 \pm 0.0108$ | $0.5543 \pm 0.0402$ | $+0.0101$ | $+1.86\%$ |
| **PR-AUC** | $0.4643 \pm 0.1405$ | $0.2071 \pm 0.0875$ | $-0.2572$ | $-55.40\%$ |
| **MCC (Calibrated)** | $0.0650 \pm 0.0000$ | $0.0659 \pm 0.0015$ | $+0.0009$ | $+1.38\%$ |
| **MCC (Default $\Theta=0.50$)** | $0.0463 \pm 0.0000$ | $0.0522 \pm 0.0292$ | $+0.0059$ | $+12.74\%$ |
| **F1 Score (Calibrated)** | $0.3724 \pm 0.0000$ | $0.3725 \pm 0.0002$ | $+0.0001$ | $+0.03\%$ |
| **FPR (Calibrated)** | $0.9668 \pm 0.0000$ | $0.9664 \pm 0.0010$ | $-0.0004$ | $-0.04\%$ |
| **FNR (Calibrated)** | $0.0077 \pm 0.0000$ | $0.0077 \pm 0.0000$ | $0.0000$ | $0.00\%$ |
| **Accuracy (Calibrated)** | $0.2487 \pm 0.0000$ | $0.2490 \pm 0.0007$ | $+0.0003$ | $+0.12\%$ |

---

## 2. Structured Analysis & Research Questions

### Q1. What is the FT-Transformer mean ROC-AUC?
**Answer**: The FT-Transformer achieves a mean ROC-AUC of **$0.5543 \pm 0.0402$** across 5 random seeds on the frozen D3 test set.

### Q2. What is the LightGBM ROC-AUC?
**Answer**: The baseline LightGBM GBDT achieves a mean ROC-AUC of **$0.5442 \pm 0.0108$** across 5 random seeds.

### Q3. What is the difference in ROC-AUC?
**Answer**: The difference is **$+0.0101$** ($+1.86\%$). This margin is well within the 1-standard-deviation error bounds ($\pm 0.0402$) of the FT-Transformer model, indicating no statistically meaningful separation from random/near-chance discrimination ($\text{AUC} \approx 0.50$).

### Q4. What is the FT-Transformer mean MCC?
**Answer**: Under target calibration ($\Theta = 0.43 - 0.87$), FT-Transformer achieves an MCC of **$0.0659 \pm 0.0015$** (and $0.0522 \pm 0.0292$ at default $\Theta = 0.50$).

### Q5. What is the LightGBM MCC?
**Answer**: Under target calibration ($\Theta = 0.62 - 0.64$), LightGBM achieves an MCC of **$0.0650 \pm 0.0000$** (and $0.0463 \pm 0.0000$ at default $\Theta = 0.50$).

### Q6. What is the difference in MCC?
**Answer**: The difference is **$+0.0009$** under calibrated thresholding. Both architectures exhibit extreme near-zero Matthews Correlation Coefficients ($\text{MCC} < 0.07$), demonstrating near-total breakdown in correlation between predictions and ground-truth SCADA attacks.

### Q7. Does FT-Transformer materially improve transfer?
**Answer**: **No.** Both model architectures suffer identical operational pathology:
1. False Positive Rate remains catastrophically high ($\text{FPR} = 96.64\%$ for FT-Transformer vs $96.68\%$ for LightGBM).
2. The calibrated model classifies almost all target traffic as attack to achieve high recall, collapsing precision to $\approx 22.9\%$ (matching the base attack prior $\pi_{target} = 22.47\%$).
3. At default threshold ($\Theta = 0.50$), FT-Transformer exhibits $\text{FPR} = 97.34\%$ and $\text{F1} = 0.3713$.

### Q8. Does the result support or weaken the representation-mismatch hypothesis?
**Answer**: **The result strongly SUPPORTS the representation-mismatch hypothesis.**
Replacing the non-linear gradient boosted decision tree (LightGBM) with a state-of-the-art self-attention neural architecture (FT-Transformer with numerical tokenization, multi-head attention, and deep feed-forward blocks) does **not** rescue cross-domain transfer performance. The failure mode ($\text{ROC-AUC} \approx 0.54 - 0.55$, $\text{MCC} \approx 0.065$, $\text{FPR} > 96\%$) is virtually identical across both model families.

This provides empirical confirmation that the cross-domain transfer bottleneck is caused by the **loss of discriminative state-space information in the 4-feature harmonized representation and severe cross-domain covariate/prior shift**, rather than inductive biases or capacity limits of the GBDT model family.
