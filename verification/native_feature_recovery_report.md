# ARGUS Native SCADA Feature Recovery & Discriminative Power Report

**Target Domain**: IEC 60870-5-104 SCADA Telemetry (Domain 3)  
**Model Artifact**: `phase3_results/models/model_d3_native.txt` (`model_d3_native`)  
**Comparison Models**: `model_d2_coral.txt` (Raw D2 CORAL) & E5 Fused (D1+D2 CORAL + Prior Correction)  
**Dataset**: $N = 3,572,265$ Full CIC Flow Telemetry Records ($2,286,250$ Train / $571,562$ Calib / $714,453$ Test)  
**Audit Date**: August 21, 2026  

---

## 1. Executive Summary

Reintroducing the full 73-feature native representation from the IEC 60870-5-104 CIC flow telemetry **substantially recovers discriminative signal**, increasing ROC-AUC on the held-out test set from **$0.4860$** (random chance baseline) to **$0.6744$**.

Feature resolution collapse is mitigated:
- **Unique Feature Tuples**: Expands from $1,574$ (in the 4-harmonized feature set) to **$800,955$** (in the 73-feature native set).
- **Unique Probability Values**: Expands from $89$ discrete values to **$30,822$** unique probabilities.

---

## 2. Before / After Performance Comparison

| Metric | `model_d2_coral.txt` (Harmonized 4-Feat) | E5 Fused CORAL (Harmonized 4-Feat) | `model_d3_native.txt` (Native 73-Feat, $\theta=0.50$) | `model_d3_native.txt` (Native 73-Feat, $\theta^*=0.78$) |
| :--- | :---: | :---: | :---: | :---: |
| **Features Used** | 4 | 4 | 73 | 73 |
| **ROC-AUC (Test)** | **$0.4860$** | **$0.5017$** | **$0.6744$** | **$0.6744$** |
| **Distinct Probability Values** | 89 | 183 | 30,822 | 30,822 |
| **Unique Feature Tuples** | 1,574 | 1,574 | 800,955 | 800,955 |
| **Threshold ($\theta$)** | 0.50 | 0.50 | 0.50 | 0.78 (Best MCC) |
| **Recall (Sensitivity)** | $94.55\%$ | $96.17\%$ | $96.31\%$ | $8.38\%$ |
| **False Positive Rate (FPR)** | $92.23\%$ | $87.15\%$ | $71.36\%$ | **$0.07\%$** |
| **Precision** | $22.88\%$ | $24.23\%$ | $28.11\%$ | **$97.01\%$** |
| **$F_1$ Score** | $0.368$ | $0.387$ | $0.435$ | $0.154$ |
| **MCC** | $-0.046$ | $0.121$ | $0.247$ | **$0.251$** |
| **Accuracy** | $30.82\%$ | $32.48\%$ | $43.85\%$ | **$79.36\%$** |

---

## 3. Side-by-Side Confusion Matrices (Test Set, $N = 714,453$)

### 3.1 E5 Fused (4-Feature Harmonized, $\theta=0.50$)
```
                Predicted Benign    Predicted Attack
True Benign          67,736            486,208       (FPR: 87.75%)
True Attack           6,146            154,363       (Recall: 96.17%)
```

### 3.2 Native SCADA Model `model_d3_native` ($\theta=0.50$)
```
                Predicted Benign    Predicted Attack
True Benign         158,680            395,264       (FPR: 71.36%)
True Attack           5,924            154,585       (Recall: 96.31%)
```

### 3.3 Native SCADA Model `model_d3_native` ($\theta^*=0.78$, High Precision Operating Point)
```
                Predicted Benign    Predicted Attack
True Benign         553,530                414       (FPR: 0.07%)
True Attack         147,060             13,449       (Recall: 8.38%, Precision: 97.01%)
```

---

## 4. Calibration Set Threshold Sweep ($\theta = 0.01 \dots 0.95$)

Sweep conducted on $N = 571,562$ calibration samples:

| Threshold ($\theta$) | Recall | FPR | Precision | $F_1$ Score | MCC |
| :---: | :---: | :---: | :---: | :---: | :---: |
| $0.05$ | $99.98\%$ | $87.66\%$ | $24.84\%$ | $0.3979$ | $0.1748$ |
| $0.15$ | $98.96\%$ | $79.76\%$ | $26.44\%$ | $0.4174$ | $0.2190$ |
| $0.30$ | $97.42\%$ | $72.86\%$ | $27.92\%$ | $0.4341$ | $0.2490$ |
| $0.45$ | $96.88\%$ | $71.96\%$ | $28.06\%$ | $0.4352$ | $0.2493$ |
| **$0.50$** | **$96.36\%$** | **$71.36\%$** | **$28.12\%$** | **$0.4354$** | **$0.2479$** |
| **$0.52$** | **$96.01\%$** | **$70.82\%$** | **$28.25\%$** | **$0.4365$** (Best $F_1$) | **$0.2488$** |
| $0.60$ | $9.65\%$ | $0.62\%$ | $81.90\%$ | $0.1727$ | $0.2348$ |
| **$0.78$** | **$8.38\%$** | **$0.07\%$** | **$97.01\%$** | **$0.1543$** | **$0.2513$** (Best MCC) |

---

## 5. Key Feature Importance Drivers (LightGBM Gain)

The top 10 feature drivers of class separation in `model_d3_native`:

1. `Fwd Header Len` ($3,211,584.48$ gain) — Forward TCP header length
2. `Init Bwd Win Byts` ($765,181.37$ gain) — Initial backward TCP window size
3. `Bwd Header Len` ($449,202.34$ gain) — Backward TCP header length
4. `fwd_pkt_ratio` ($370,400.04$ gain) — Engineered ratio of forward to total packets
5. `Flow IAT Min` ($319,989.54$ gain) — Minimum inter-arrival time
6. `Fwd Pkt Len Mean` ($286,460.05$ gain) — Mean forward packet size
7. `Fwd IAT Min` ($206,075.13$ gain) — Minimum forward inter-arrival time
8. `Flow IAT Mean` ($190,970.57$ gain) — Mean inter-arrival time
9. `TotLen Bwd Pkts` ($120,880.09$ gain) — Total backward payload bytes
10. `Active Min` ($120,615.18$ gain) — Minimum active duration before idle

### Previously Excluded Domain-Specific Features Analysis
- `pkt_range_ratio` ranked **#53** (gain: $1,125.56$)
- `log_flow_activity` ranked **#51** (gain: $1,289.78$)
- `pkt_min_to_max` ranked **#56** (gain: $47.83$)

The primary missing signal in the 4-feature harmonized subset was **TCP header structure (`Fwd/Bwd Header Len`, `Init Bwd Win Byts`) and directional flow ratios (`fwd_pkt_ratio`)**, which are present in native flow exports but were stripped during cross-domain feature reduction.

---

## 6. Scientific & Methodological Conclusion

1. **Feature Reduction Trade-off**: Restricting the feature set to 4 harmonized packet statistics for cross-domain alignment degraded test ROC-AUC from **0.6744 to 0.4860**, causing severe feature resolution collapse ($1,574$ feature tuples across $3.57\text{M}$ flows).
2. **Native Classifier Performance**: A native SCADA-only classifier (`model_d3_native`) recovers non-random discriminative signal ($\text{ROC-AUC} = 0.6744$) and provides flexible operating choices:
   - **Balanced / High Recall ($\theta = 0.50$)**: $96.31\%$ Recall, $71.36\%$ FPR, $F_1 = 0.435$.
   - **Low False Alarm / High Precision ($\theta = 0.78$)**: $97.01\%$ Precision, $0.07\%$ FPR, $8.38\%$ Recall.
3. **Paper Recommendation**: Present `model_d3_native` alongside `model_d2_coral` to illustrate the fundamental trade-off between cross-domain generalizability/harmonization and native target-domain discriminative capacity.
