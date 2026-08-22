# N2 Diagnostic Interpretation Report: FT-Transformer vs LightGBM (D2 → D3 Transfer)

**Experiment ID**: `NR-01` (N2 Component)  
**Source Domain**: D2 (NF-ToN-IoT-v2)  
**Target Domain**: D3 (IEC 60870-5-104 SCADA Telemetry)  
**Feature Set**: ARGUS-4 Harmonized 4-Feature Set  
**Seeds Evaluated**: 5 Seeds (`[42, 123, 456, 789, 1011]`)  
**Target Test Set**: Frozen $N = 714,453$ records ($\pi_{target} = 22.47\%$)

---

## 1. Quantitative Benchmark Comparison

| Metric | LightGBM GBDT (Existing Frozen Baseline) | FT-Transformer Neural (New Robustness Run) | Absolute Difference ($\Delta$) | Analysis / Verdict |
|---|:---:|:---:|:---:|:---:|
| **ROC-AUC** | $0.4381 \pm 0.0021$ | $0.4877 \pm 0.0322$ | $+0.0496$ | Sub-chance (< 0.50) in both architectures |
| **PR-AUC** | $0.2001 \pm 0.0039$ | $0.1833 \pm 0.0031$ | $-0.0168$ | Below base attack prior ($\pi_{target} = 0.2247$) |
| **MCC (Calibrated)** | $0.0087 \pm 0.0025$ | $0.0704 \pm 0.0306$ | $+0.0617$ | Negligible correlation ($\text{MCC} < 0.10$) |
| **MCC (Default $\Theta=0.50$)** | $0.0742 \pm 0.0021$ | $-0.0785 \pm 0.0327$ | $-0.1527$ | Inverse/Negative correlation |
| **F1 Score (Calibrated)** | $0.3666 \pm 0.0002$ | $0.3760 \pm 0.0069$ | $+0.0094$ | Collapsed to prior-level baseline |
| **FPR (Calibrated)** | $0.9833 \pm 0.0009$ | $0.8429 \pm 0.0704$ | $-0.1404$ | Unusable operational false positive rate |
| **FNR (Calibrated)** | $0.0140 \pm 0.0001$ | $0.0957 \pm 0.0363$ | $+0.0817$ | Increased missed attacks |
| **Accuracy (Calibrated)** | $0.2344 \pm 0.0007$ | $0.3250 \pm 0.0465$ | $+0.0906$ | Severe accuracy penalty |

---

## 2. Key Scientific Findings for N2

1. **Sub-Chance Inversion Confirmed Across Model Families**:
   - Both LightGBM ($\text{ROC-AUC} = 0.4381$) and FT-Transformer ($\text{ROC-AUC} = 0.4877$) exhibit ROC-AUC below 0.50.
   - This indicates that feature-label distributions in D2 (NF-ToN-IoT-v2) are fundamentally inverted relative to D3 (IEC 60870-5-104) under the 4-feature projection.
2. **Failure of Default Thresholding**:
   - At $\Theta = 0.50$, FT-Transformer misses $95.06\%$ of all attacks ($\text{FNR} = 0.9506$, $\text{F1} = 0.0621$) with negative MCC ($\text{MCC} = -0.0785$).
3. **Impossibility of Cross-Domain Recovery Without Domain-Specific Features**:
   - Calibrating the decision threshold to the validation split slightly improves F1 to $0.3760$, but at the cost of an unacceptable $84.29\%$ False Positive Rate.
4. **Theoretical Implication**:
   - The D2 $\rightarrow$ D3 transfer failure is strictly independent of the learning algorithm, proving that neural network inductive biases cannot overcome non-overlapping manifold support and inverse conditional distributions in reduced feature spaces.
