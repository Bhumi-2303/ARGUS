# ARGUS P1-1 — Forensic Leakage, Duplicate, and Group Partition Audit

**Date**: 2026-11-01  
**Auditor**: Independent Machine Learning Research Auditor  
**Audit Target**: NF-ToN-IoT-v2 Partitions & Harmonized 4-Feature Space  
**Status**: `QUALIFIED_FINDING (HIGH DUPLICATE OVERLAP DETECTED)`  

---

## 1. Executive Summary

This mandatory forensic audit evaluated potential data leakage, repeated flow vectors, and group structure across the three NF-ToN-IoT-v2 partitions:
- `nfton_train_adaptation.csv` ($N = 8,406,962$)
- `nfton_train_calibration.csv` ($N = 2,101,742$)
- `nfton_test_features.csv` ($N = 2,627,177$)

### Major Audit Discoveries:
1. **Severe Coordinate Degeneracy in 4D Feature Space**:
   - Compressing network flows into only four statistical features (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`) causes massive collapse of distinct flows into identical points.
   - Out of 2,627,177 test rows, there are only **102,188 unique feature vectors** (96.11% duplicate rate).
   - Out of 8,406,962 training rows, there are only **202,194 unique feature vectors** (97.59% duplicate rate).
2. **Cross-Partition Coordinate Overlap**:
   - **2,592,203 test rows (98.67% of the test set)** share identical 4-feature coordinates with observations in the training adaptation set.
   - Only **31,143 test rows (1.19%)** represent novel feature coordinates that never appeared in training or calibration.
3. **High Empirical Label Conflict Rate**:
   - Because diverse network traffic patterns (different protocols, services, and attack types) share identical packet size and flag ratios, identical 4D feature vectors frequently carry **conflicting ground-truth labels**.
   - In the training set, **6,644,645 rows (79.04% of training)** map to feature vectors that are labeled as *both* Benign ($y=0$) and Attack ($y=1$).
   - In the test set, **1,989,306 rows (75.72% of test)** map to conflicting feature vectors.
4. **Stratified Random Row Splitting**:
   - All three files exhibit an identical attack prior of **72.5844%**, confirming that the legacy partition was generated via row-level stratified random sampling, without grouping by IP address, connection session, device, or capture timestamp.

---

## 2. Partition Geometry & Duplicate Flow Analysis

| Metric | Training (Adaptation) | Calibration | Frozen Test |
|---|---:|---:|---:|
| Total Rows | 8,406,962 | 2,101,742 | 2,627,177 |
| Benign Rows ($y=0$) | 2,304,821 (27.42%) | 576,206 (27.42%) | 720,257 (27.42%) |
| Attack Rows ($y=1$) | 6,102,141 (72.58%) | 1,525,536 (72.58%) | 1,906,920 (72.58%) |
| Unique Feature Vectors | 202,194 | 89,325 | 102,188 |
| Duplicate Rows | 8,204,768 (97.59%) | 2,012,417 (95.75%) | 2,524,989 (96.11%) |
| Conflicting Vectors (0 & 1) | 16,456 (8.14%) | 4,394 (4.92%) | 5,538 (5.42%) |
| Rows with Conflicting Vectors | **6,644,645 (79.04%)** | **1,578,200 (75.09%)** | **1,989,306 (75.72%)** |
| Pure Benign Vectors | 41,779 | 18,531 | 21,060 |
| Pure Attack Vectors | 143,959 | 66,400 | 75,590 |

---

## 3. Cross-Partition Overlap & Information Leakage Mechanics

### 3.1 Overlap Quantification
- Test unique vectors: 102,188
- Test vectors present in Training: 69,733 (68.24% of unique vectors)
- Test vectors present in Training or Calibration: 72,894 (71.33% of unique vectors)
- Novel test vectors never seen in training: 29,294 (28.67% of unique vectors)
- **Test rows matching a training coordinate: 2,592,203 rows (98.67%)**
- **Test rows with novel coordinates: 31,143 rows (1.19%)**

### 3.2 Mechanism of Performance Inflation in Supervised Learning
In standard tabular learning, when 98.67% of test instances share coordinates with training instances under a row-level random split:
1. For any coordinate point $\mathbf{x}$, the Bayes optimal prediction under cross-entropy is the empirical posterior:
   $$\hat{P}(y=1 \mid \mathbf{x}) \approx \frac{\sum_{i \in \text{Train}, \mathbf{x}_i=\mathbf{x}} \mathbb{I}(y_i=1)}{N_{\mathbf{x}}}$$
2. Deep trees (e.g., `max_depth = 8`, `num_leaves = 63`) have sufficient capacity to partition these 202,194 unique coordinates and memorize their empirical majority label in the training set.
3. Because the training and test splits were sampled uniformly at random from the same master collection, the test set empirical distribution $P_{\text{Test}}(y \mid \mathbf{x})$ matches $P_{\text{Train}}(y \mid \mathbf{x})$ almost perfectly.
4. Consequently, the supervised models achieve a high apparent accuracy (93.3%) by acting as an empirical nearest-neighbor / base-rate lookup table for repeated flow coordinates.

### 3.3 Asymmetric Impact on Cross-Domain Models
Crucially, this mechanism **does not benefit transferred models**:
- Source-Only XGBoost and CORAL models were trained on CIC-IoT-2023 (D1), where the conditional distribution $P_{D1}(y \mid \mathbf{x})$ is radically different from $P_{D2}(y \mid \mathbf{x})$.
- For example, a packet size ratio of 1.0 with zero flag density may be 99% benign in D1, but 80% attack in D2 (due to differing service profiles or attack tooling).
- When transferred to D2, the cross-domain model predicts according to $P_{D1}(y \mid \mathbf{x})$, resulting in massive misclassifications.
- **Auditor Conclusion**: It is scientifically incorrect to claim that duplicate flow collapse affects all models symmetrically. In-domain supervised models benefit from random split leakage of target base rates, whereas cross-domain models are penalized by prior shift at those identical coordinates.

---

## 4. Assessment of Split Methodology (Grouped vs. Random)

1. **Available Metadata**:
   - The files in `data/raw/legacy_package/argus_coral_data/` contain only the 4 statistical features and binary `label`. Flow IDs, IP addresses, ports, and timestamps were stripped during creation of the legacy package.
   - In the broader repository, `data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet` contains 12 raw NetFlow columns (`L4_SRC_PORT`, `L4_DST_PORT`, `PROTOCOL`, `IN_BYTES`, `OUT_BYTES`, `FLOW_DURATION_MILLISECONDS`, etc.), but does not map 1:1 to the 13.1-million-row legacy split.
2. **Evaluation Protocol Integrity**:
   - The P1-1 experiment correctly preserved the frozen test split (`nfton_test_features.csv`) without modifications, strictly honoring the non-negotiable execution rules.
   - The experiment did not introduce this duplicate structure; it inherited it from the legacy ARGUS benchmark protocol.

---

## 5. Auditor Recommendations for Future Research (Pre-Publication)

Before submitting these findings to peer-reviewed venues, the following experimental extensions are strongly recommended:

1. **Grouped / Time-Series Robustness Benchmark (P2)**:
   - Perform a temporally or session-grouped split on NF-ToN-IoT-v2 using raw timestamps or IP subnet groups if full raw PCAPs or extended NetFlow tables are available.
   - Measure the performance drop of in-domain supervised models on truly unseen network flow regimes.
2. **Coordinate-Deduplicated Evaluation (P2)**:
   - Evaluate model predictions on the subset of 31,143 test rows that possess strictly novel 4D coordinates.
   - Report whether in-domain models maintain their 93.3% accuracy on out-of-training coordinates, or whether accuracy drops toward the 72.6% majority class baseline.
3. **Caveat in Research Text**:
   - Explicitly document in all papers and thesis chapters that the high in-domain performance (MCC 0.8320) is partially facilitated by identical flow coordinate repetition resulting from random row-level splitting of low-dimensional flow telemetry.
