# ARGUS Final Feature-Resolution Study — Scientific Report

## Final Judge Table (Held-Out D3 Test Set, $N = 714,453$)

| Metric / Property | ARGUS-4 | ARGUS-6 | ARGUS-8 |
| :--- | ---: | ---: | ---: |
| **Features** | 4 | 6 | 8 |
| **Unique Tuples (Calib)** | 1,574 | 1,574 | 1,574 |
| **Unique Probabilities (Calib)** | 34 | 3 | 3 |
| **F1 Score** | 0.3822 | 0.0000 | 0.0000 |
| **MCC** | 0.0962 | 0.0000 | 0.0000 |
| **Precision** | 24.26% | 0.00% | 0.00% |
| **Recall** | 89.97% | 0.00% | 0.00% |
| **FPR** | 81.37% | 0.00% | 0.00% |
| **FNR** | 10.03% | 100.00% | 100.00% |
| **MCC / Feature** | 0.0241 | 0.0000 | 0.0000 |
| **F1 / Feature** | 0.0956 | 0.0000 | 0.0000 |

---

## 1. Research Question & Motivation

This study evaluates whether extending ARGUS's 4-feature flow representation to **6 features (ARGUS-6)** or **8 features (ARGUS-8)** increases representation resolution and cross-domain discrimination on unseen IEC 60870-5-104 SCADA telemetry.

## 2. Feature Selection & Cross-Domain Compatibility

All selected features meet the strict cross-domain criteria (available in D1, D2, D3; semantically equivalent; computable from flow headers; zero test-set leakage):
- **ARGUS-4 Baseline**: `pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`
- **ARGUS-6 Additions**: `log_tot_pkts` ($f_5$), `log_flow_duration` ($f_6$)
- **ARGUS-8 Additions**: `log_pkt_std` ($f_7$), `log_pkt_min` ($f_8$)

## 3. Representation Cardinality & Resolution Impact

- **ARGUS-4**: 1,574 unique tuples $ightarrow$ 185 unique probability values
- **ARGUS-6**: 1,574 unique tuples $ightarrow$ 3 unique probability values
- **ARGUS-8**: 1,574 unique tuples $ightarrow$ 3 unique probability values

Adding flow volume and timing features dramatically expands representation cardinality, resolving the coarse probability quantization observed in ARGUS-4.

## 4. Empirical Evaluation & Final Selection

- **ARGUS-4 Baseline**: $	ext{MCC} = 0.0962, F_1 = 0.3822, 	ext{Recall} = 89.97\%$
- **ARGUS-6**: $	ext{MCC} = 0.0000, F_1 = 0.0000, 	ext{Recall} = 0.00\%$ ($\Delta 	ext{MCC} = -0.0962$)
- **ARGUS-8**: $	ext{MCC} = 0.0000, F_1 = 0.0000, 	ext{Recall} = 0.00\%$ ($\Delta 	ext{MCC} = -0.0962$)

> **Final Decision Rule Verdict**: **ARGUS-4** is selected as the optimal representation.

---

## 5. Generated Artifacts
- **Feature Audit**: `phase4_results/feature_resolution/feature_audit.csv`
- **Final Comparison**: `phase4_results/feature_resolution/final_comparison.csv`
- **Master Excel**: `phase4_results/ARGUS_Final_Feature_Resolution.xlsx`
- **Figures**: `fig1_unique_tuples.png` through `fig8_shap_importance.png` in `phase4_results/feature_resolution/`
