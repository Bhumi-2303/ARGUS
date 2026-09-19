# High FPR Ambiguity Investigation

## Cluster Identification
- **Duplicate-feature cluster tuple (rounded):** `pkt_mean_to_max=1.0, tcp_flag_density=0.0, log_pkt_mean=3.1355, log_pkt_max=3.1355`
- **Exact Cluster Size:** 501417 flows
- **Percentage of IEC104 Test Data:** 70.18%
- **Label Distribution:** 
  - Benign: 369972
  - Attack: 131445
- **Model Probability uniqueness:**
  - 100% of these 501417 flows share identical fused probability = 0.504138.

## Threshold Sensitivity
The cluster falls precisely around `probability = 0.504138`.
Because 70% of the dataset is identical, moving the threshold across this boundary fundamentally alters the operational behavior.
At `0.500`, the entire cluster is classified as an Attack, leading to extreme FPR but high recall.
At `0.505`, the entire cluster falls below the threshold, suppressing the FP rate but completely destroying Recall.

See `artifacts/metrics/fpr_ambiguity_analysis.csv` for exact breakdown.
