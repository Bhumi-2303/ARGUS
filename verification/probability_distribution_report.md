# ARGUS Probability Distribution & Discriminative Power Analysis Report

**Target Domain**: IEC 60870-5-104 SCADA Telemetry (Domain 3)  
**Model Artifact**: `phase3_results/models/model_d2_coral.txt` (Raw D2 CORAL) & E5 Fusion (D1+D2 CORAL + Prior Correction)  
**Test Set**: $N = 714,453$ Labeled SCADA Test Telemetry Records  
**Calibration Set**: $N = 571,563$ (Used for Threshold Sweep)  
**Audit Date**: August 21, 2026  

> [!CAUTION]
> **The model's raw probability outputs are near-degenerate. ROC-AUC is at or below random chance. The high recall reported in all ARGUS experiments is a consequence of probability quantization and threshold placement, NOT of genuine class-separating signal. This section documents the finding honestly for the paper.**

---

## 1. Probability Value Distribution (Full Test Set, $N = 714,453$)

### 1.1 Distinct Probability Values

The raw D2 CORAL model (`model_d2_coral.txt`) produces only **89 distinct probability values** across the entire 714,453-sample SCADA test set (rounded to 6 decimal places).

### 1.2 Top 20 Most Frequent Probability Values

| Probability ($\hat{p}$) | Row Count | Fraction of Dataset | Benign Rows | Attack Rows | Attack Rate |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **$0.758727$** | **$501,417$** | **$70.18\%$** | $369,972$ | $131,445$ | $26.2\%$ |
| $0.934454$ | $63,171$ | $8.84\%$ | $62,281$ | $890$ | $1.4\%$ |
| $0.669136$ | $55,744$ | $7.80\%$ | $49,512$ | $6,232$ | $11.2\%$ |
| $0.921886$ | $21,082$ | $2.95\%$ | $14,921$ | $6,161$ | $29.2\%$ |
| $0.189074$ | $13,884$ | $1.94\%$ | $10,633$ | $3,251$ | $23.4\%$ |
| $0.671465$ | $8,165$ | $1.14\%$ | $7,757$ | $408$ | $5.0\%$ |
| $0.479947$ | $6,696$ | $0.94\%$ | $4,943$ | $1,753$ | $26.2\%$ |
| $0.326708$ | $5,154$ | $0.72\%$ | $3,780$ | $1,374$ | $26.7\%$ |
| $0.019699$ | $4,591$ | $0.64\%$ | $4,317$ | $274$ | $6.0\%$ |
| $0.016253$ | $4,473$ | $0.63\%$ | $4,218$ | $255$ | $5.7\%$ |
| $0.162597$ | $3,724$ | $0.52\%$ | $3,503$ | $221$ | $5.9\%$ |
| $0.662254$ | $2,591$ | $0.36\%$ | $235$ | $2,356$ | $90.9\%$ |
| $0.684063$ | $2,507$ | $0.35\%$ | $1,518$ | $989$ | $39.4\%$ |
| $0.303410$ | $2,385$ | $0.33\%$ | $1,732$ | $653$ | $27.4\%$ |
| $0.005341$ | $2,360$ | $0.33\%$ | $2,225$ | $135$ | $5.7\%$ |
| $0.016436$ | $2,329$ | $0.33\%$ | $2,203$ | $126$ | $5.4\%$ |
| $0.009071$ | $2,245$ | $0.31\%$ | $2,082$ | $163$ | $7.3\%$ |
| $0.028746$ | $2,235$ | $0.31\%$ | $2,085$ | $150$ | $6.7\%$ |
| $0.622614$ | $1,651$ | $0.23\%$ | $1,314$ | $337$ | $20.4\%$ |
| $0.521417$ | $1,243$ | $0.17\%$ | $888$ | $355$ | $28.6\%$ |

**Top 20 values account for $707,647 / 714,453$ ($99.05\%$) of all test rows.**

### 1.3 Dominant Mode Analysis

The single probability value $\hat{p} = 0.758727$ absorbs:
- **$70.18\%$** of the entire test set ($501,417$ rows)
- **$66.8\%$** of all benign rows ($369,972 / 553,944$)
- **$81.9\%$** of all attack rows ($131,445 / 160,509$)

At this value, the local attack rate is $26.2\%$ — nearly identical to the dataset base rate of $22.5\%$. The model assigns the same probability to benign and attack flows indiscriminately for $70\%$ of the data.

---

## 2. Probability Distribution Histogram

![Probability Distribution: Benign vs Attack](file:///Users/tirthkosambia/Documents/ARGUS/verification/probability_distribution.png)

The histogram and CDF panels confirm near-total overlap between the benign and attack probability distributions. The class-conditional CDFs are essentially superimposed.

---

## 3. ROC-AUC (Threshold-Independent Discriminative Signal)

| Model / Configuration | Test Set ROC-AUC | Calibration Set ROC-AUC | Interpretation |
| :--- | :--- | :--- | :--- |
| **Raw D2 CORAL** (`model_d2_coral.txt`) | **$0.4860$** | **$0.4859$** | **Below random chance ($0.50$)** |
| **E5 Fused CORAL + Prior Correction** | **$0.5017$** | **$0.5012$** | **At random chance** |

> [!IMPORTANT]
> A ROC-AUC of $0.486$ means the model is **less discriminative than a coin flip**. The E5 fusion with prior correction marginally lifts this to $0.5017$, which is statistically indistinguishable from random ordering. **There is no class-separating signal in these probability outputs, at any threshold.**

---

## 4. E5 Threshold Sweep on Calibration Set ($N = 571,563$)

Re-running the same threshold sweep logic from `adaptive_operating_point.py` on E5's fused, prior-corrected calibration set probabilities:

| Threshold ($\theta$) | Recall | FPR | Precision | $F_1$ | MCC | Balanced Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| $0.01$ | $0.9964$ | $0.9839$ | $0.2269$ | $0.3696$ | $0.0454$ | $0.5062$ |
| $0.05$ | $0.9787$ | $0.9560$ | $0.2288$ | $0.3709$ | $0.0491$ | $0.5114$ |
| $0.10$ | $0.9787$ | $0.9558$ | $0.2288$ | $0.3709$ | $0.0493$ | $0.5114$ |
| $0.20$ | $0.9787$ | $0.9558$ | $0.2288$ | $0.3709$ | $0.0493$ | $0.5114$ |
| $0.30$ | $0.9762$ | $0.9538$ | $0.2287$ | $0.3706$ | $0.0472$ | $0.5112$ |
| $0.40$ | $0.9762$ | $0.9538$ | $0.2287$ | $0.3706$ | $0.0472$ | $0.5112$ |
| **$0.50$** | **$0.9617$** | **$0.8715$** | **$0.2423$** | **$0.3871$** | **$0.1212$** | **$0.5451$** |
| $0.55$ | $0.1137$ | $0.1815$ | $0.1535$ | $0.1306$ | $-0.0761$ | $0.4661$ |
| $0.60$ | $0.1136$ | $0.1815$ | $0.1535$ | $0.1306$ | $-0.0761$ | $0.4661$ |
| $0.75$ | $0.1094$ | $0.1783$ | $0.1509$ | $0.1268$ | $-0.0779$ | $0.4655$ |
| $0.90$ | $0.0681$ | $0.1432$ | $0.1211$ | $0.0872$ | $-0.0943$ | $0.4625$ |

**Best $F_1 = 0.3871$ at $\theta = 0.50$.** No other threshold produces a substantially better trade-off.

### 4.1 Comparison to C4\_D2\_CORAL\_prior ($\theta^* = 0.19$)

The single-source D2 CORAL with prior correction (Phase 3, `C4_D2_CORAL_prior`) selected $\theta^* = 0.19$ and achieved $\text{Recall} = 88.41\%$, $\text{FPR} = 37.70\%$, $\text{MCC} = 0.0789$. That improvement was possible because prior correction on the single D2 source shifted enough probability mass below $0.50$ to create a meaningful decision boundary at $\theta = 0.19$.

For E5, the fusion and prior correction produce a **cliff at $\theta = 0.50$**: Recall drops from $96.17\%$ to $11.37\%$ as $\theta$ crosses $0.50$. The sweep is flat from $\theta = 0.05$ through $\theta = 0.49$ (Recall $\approx 97.6\%$, FPR $\approx 95.5\%$) and flat again from $\theta = 0.55$ through $\theta = 0.95$ (Recall $\approx 11\%$, FPR $\approx 18\%$). **There is no intermediate threshold that achieves substantially lower FPR while retaining useful recall.** The probability distribution has an enormous mass spike at $\hat{p} \approx 0.50$, and the model simply cannot rank attack flows higher than benign flows.

> [!IMPORTANT]
> **This is a signal problem, not a calibration problem.** No threshold selection strategy can extract discriminative performance from a model whose ROC-AUC is $0.50$. Recalibration, prior correction, and fusion do not create class separation — they can only re-center an existing separation. Here, there is no separation to re-center.

---

## 5. Root Cause Diagnosis

The fundamental issue is **feature resolution collapse**: the 4-feature representation (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`) produces only $1,574$ unique feature tuples across $571,563$ calibration samples and only $89$ unique output probabilities. The LightGBM tree ensemble quantizes the feature space into a small number of leaf nodes, and because the feature space itself has extremely low cardinality on the SCADA target domain, the model cannot distinguish attack from benign traffic.

This is consistent with the domain adaptation setting: the model was trained on NF-ToN-IoT-v2 (Domain 2), where the same features likely have higher cardinality. On the SCADA/IEC 60870-5-104 target domain, the network traffic is highly homogeneous, and 4 packet-level statistical features do not carry enough information to discriminate intrusion events.

---

## 6. Implications for Paper

### What Can Be Claimed
1. The deployed pipeline **exactly reproduces** the reported research metrics ($0 / 1,000$ prediction divergences, verified in `verification/reproducibility_report.md`).
2. The CORAL alignment, threshold, and inference preprocessing are all **verified correct** (`verification/coral_alignment_report.md`, `verification/threshold_reconciliation_report.md`).
3. The system architecture (streaming pipeline, microservices, explainability, risk scoring) is **fully functional and deployable**.

### What Cannot Be Claimed
1. That the detector has **meaningful intrusion detection capability** on the SCADA target domain. The ROC-AUC of $0.486–0.502$ indicates the probability outputs do not separate classes better than random.
2. That the $96\%$ recall figure represents **useful detection performance**. It is achieved at $87\%$ FPR because the model assigns most rows (both benign and attack) the same above-threshold probability ($0.758727$). The high recall is an artifact of probability quantization, not genuine discrimination.
3. That threshold recalibration can fix this. The sweep confirms no threshold substantially improves the FPR-Recall trade-off for E5.

### Recommended Paper Framing
> *"The Full ARGUS pipeline (E5\_fusion\_CORAL\_prior) achieves $96.08\%$ attack recall on the SCADA target domain at $\theta = 0.50$, but at a false positive rate of $87.08\%$ ($F_1 = 0.387$, $\text{MCC} = 0.121$, $\text{ROC-AUC} = 0.502$). Probability distribution analysis reveals that the 4-feature representation produces only 89 distinct probability values across 714,453 test samples, with a single mode ($\hat{p} = 0.759$) absorbing $70\%$ of both classes indiscriminately. This indicates that the feature set lacks sufficient resolution to discriminate SCADA intrusion events from benign operational telemetry in this cross-domain transfer setting, representing a fundamental feature engineering limitation rather than a model calibration deficiency."*

---

## 7. Verification Chain Summary

| Verification Report | File | Verdict |
| :--- | :--- | :--- |
| Threshold Reconciliation | [threshold_reconciliation_report.md](file:///Users/tirthkosambia/Documents/ARGUS/verification/threshold_reconciliation_report.md) | **EXACT MATCH ($\theta = 0.50$)** |
| CORAL Feature Alignment | [coral_alignment_report.md](file:///Users/tirthkosambia/Documents/ARGUS/verification/coral_alignment_report.md) | **EXACT MATCH (Raw target features correct)** |
| End-to-End Reproducibility | [reproducibility_report.md](file:///Users/tirthkosambia/Documents/ARGUS/verification/reproducibility_report.md) | **EXACT MATCH ($0 / 1,000$ divergences)** |
| Probability Distribution & Signal | This report | **ROC-AUC $= 0.486$ (Raw) / $0.502$ (E5 Fused) — No class-separating signal** |
