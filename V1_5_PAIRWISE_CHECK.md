# V1.5 Pairwise Domain Separability Check

## 1. Domain Separability Comparison
To determine whether V1.5's catastrophic domain leakage (99.90%) is driven solely by BoT-IoT's flood traffic, we re-ran the exact Random Forest domain-classifier methodology (max_depth=5, 100,000 balanced samples) on the CICIoT2023 vs NF-ToN-IoT-v2 pair *only*.

| Feature Space | Domains Classified | Domain Separability Accuracy |
| :--- | :--- | :--- |
| Original 4-Feature | CICIoT2023 vs NF-ToN-IoT | **98.88%** |
| V1.5 Extended (7-Feature) | CICIoT2023 vs NF-ToN-IoT | **99.92%** |
| Original 4-Feature | All Three Domains | *87.16%* (Reference) |
| V1.5 Extended (7-Feature) | All Three Domains | *99.90%* (Reference) |

*Note on 4-feature leakage:* The original 4-feature space is already highly separable (98.88%) between the two primary datasets. The drop to 87.16% when including BoT-IoT occurs because BoT-IoT collapses into a single dense bucket that partially overlaps with the other domains, confusing the 3-class classifier.

## 2. Feature Importance Breakdown
Extracting the feature importances from the pairwise (CICIoT vs NF-ToN) V1.5 classifier reveals exactly which variables drive the split:

| Feature | Importance | Feature Group |
| :--- | :--- | :--- |
| `log_total_pkts` | **35.14%** | V1.5 New |
| `log_byte_rate` | **25.83%** | V1.5 New |
| `log_duration` | **14.52%** | V1.5 New |
| `tcp_flag_density` | 14.20% | Base 4 |
| `log_pkt_mean` | 5.33% | Base 4 |
| `pkt_mean_to_max` | 2.71% | Base 4 |
| `log_pkt_max` | 2.28% | Base 4 |

**Cumulative Importance of New Features:** **75.49%**

## 3. Pairwise Unique-Vector Diversity Check
We confirmed that concatenating CICIoT2023 and NF-ToN-IoT-v2 under V1.5 maintains the high diversity observed individually:
*   **Combined Pairwise Diversity (V1.5):** 671,406 unique vectors out of 1,870,305 total records (**35.90%**)

## 4. Conclusion
Because the three new V1.5 features entirely usurp the model's split decisions (accounting for >75% of feature importance) and successfully push pairwise leakage to near-perfect accuracy (99.92%), we conclude:

**(b) V1.5 introduces meaningful new domain leakage even between CICIoT and NF-ToN alone — the problem is the features themselves, not BoT-IoT.**
