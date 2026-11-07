# ARGUS P2.3 — Adversarial Reconciliation of P2.1 and P2.2 Results

**Audit Status:** `PASS WITH QUALIFICATIONS`  
**Auditor Role:** Senior ML Research Auditor & Independent Scientific Reviewer  
**Repository:** `/home/bhumi/GitHub/ARGUS`  
**Git Branch:** `v2-transformer-exploratory`  
**Python Environment:** Python 3.14.9 (`.venv/bin/python3`)  
**Evaluation Dataset:** NF-ToN-IoT-v2 (13,135,881 total pool flows; 1,970,428 coordinate-disjoint test flows)  
**Test Suite Status:** **283 passed, 0 failed** across all unit, security, and integration suites  

---

## Executive Summary & Authoritative Determination

An adversarial, evidence-based reconciliation audit of the P2.1 and P2.2 experimental results in ARGUS was conducted. The investigation traced all raw datasets, model checkpoints, inference pipelines, prediction arrays, statistical bootstrapping procedures, and test suite definitions.

### Key Audit Findings

1. **Exact Partition Identity Verified Bit-for-Bit**:
   P2.1 and P2.2 evaluated on the **exact same coordinate-disjoint test partition** ($N = 1,970,428$ observations, $K = 35,131$ unique 4D coordinate clusters, attack prevalence = $72.5844\%$). Reconstructing the greedy multi-objective bin-packing partition across the entire 13,135,881 NF-ToN pool confirms bit-level identity against the saved prediction artifact `coordinate_disjoint_predictions.parquet` (`np.array_equal == True`). The SHA-256 hashes of test row indices, labels, features, and group IDs match 100%.

2. **Root Cause of Purported P2.2 Discrepancies**:
   The purported numerical contradictions between P2.1 and P2.2 cited in the audit request—specifically:
   - Clean Class-Aware CORAL MCC reported as 0.3458 (versus P2.1 MCC 0.0504 / 0.0795)
   - XGBoost accuracy reported as 0.7423 (versus P2.1 accuracy 0.6895)
   - LightGBM accuracy reported as 0.7441 (versus P2.1 accuracy 0.7105)
   - Purported 1,466,613 bootstrap groups (versus P2.1 35,131 groups)
   **originated entirely from conversational text hallucinations in the LLM chat summary of P2.2**. They **never existed in any script, model checkpoint, or on-disk data artifact**.
   The actual on-disk P2.2 report ([`audit/research/P2_2_FINAL_STATISTICAL_ROBUSTNESS_REPORT.md`](file:///home/bhumi/GitHub/ARGUS/audit/research/P2_2_FINAL_STATISTICAL_ROBUSTNESS_REPORT.md)) and JSON deliverable ([`results/experiments/p2_2_robustness/P2_2_CLUSTER_BOOTSTRAP_RESULTS.json`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_2_robustness/P2_2_CLUSTER_BOOTSTRAP_RESULTS.json)) record the exact same numbers as P2.1:
   - Clean Class-Aware CORAL ($\tau = 0.50$): Accuracy = **0.3722**, MCC = **0.0504**
   - Clean Class-Aware CORAL ($\tau = 0.99$): Accuracy = **0.3594**, MCC = **0.0795**
   - In-Domain Disjoint XGBoost ($\tau = 0.50$): Accuracy = **0.6895**, MCC = **0.2539**, ROC-AUC = **0.7754**
   - In-Domain Disjoint LightGBM ($\tau = 0.50$): Accuracy = **0.7105**, MCC = **0.3298**, ROC-AUC = **0.6510**
   - Coordinate group count: exactly **35,131** groups.

3. **Reconciliation of Cluster-Bootstrap Methodology**:
   The primary cluster bootstrap in both P2.1 and P2.2 resampled the $K = 35,131$ coordinate groups with replacement ($B = 1,000$ resamples) preserving cluster structure and joint label distributions. The spurious figure of "1,466,613 groups" is impossible: the entire 13.1M NF-ToN pool contains only 257,870 unique coordinate groups in total.

4. **Paired Model Comparisons on Benchmark Test Partition**:
   Paired cluster-robust bootstrap comparisons over the identical 35,131 groups reveal:
   - **LightGBM vs. XGBoost ($\tau = 0.50$)**: $\Delta\text{MCC} = +0.0758$ (95% CI: `[-0.0162, +0.2251]`, $p = 0.140$, not statistically significant).
   - **Clean CORAL vs. LightGBM ($\tau = 0.50$)**: $\Delta\text{MCC} = -0.2794$ (95% CI: `[-0.6506, +0.0785]`, $p = 0.154$).
   - **Clean CORAL vs. XGBoost ($\tau = 0.50$)**: $\Delta\text{MCC} = -0.2035$ (95% CI: `[-0.5855, +0.1511]`, $p = 0.324$).
   - Observation-level log-loss and Brier score with clustered sandwich standard errors favor XGBoost over LightGBM ($p = 0.124$ and $p = 0.116$, respectively).

5. **Clarification on Multi-Split Sensitivity Partitions**:
   In P2.2, five supplementary random seed partitions (seeds 42, 101, 202, 303, 404) were generated to evaluate split sensitivity. Across these 5 splits, XGBoost MCC varied from 0.1351 to 0.6735 ($\mu = 0.4550 \pm 0.2303$) and LightGBM MCC varied from 0.0840 to 0.5592 ($\mu = 0.3545 \pm 0.1753$). These splits were clearly demarcated in `P2_2_INDEPENDENT_SPLIT_METRICS.csv` as a sensitivity audit, not a substitution for the primary benchmark test set.

6. **Test Suite Count Reconciliation (283 vs. 271 Tests)**:
   The difference between 283 tests and 271 tests is **100% explained by pytest discovery scope**:
   - `pytest` (project root discovery) finds 283 tests: 271 in `tests/` + 12 in `src/**/tests/`.
   - `pytest tests/` (directory-scoped argument) only targets `tests/`, collecting 271 tests.
   - **Zero tests were deleted, removed, disabled, or renamed.** All 283 tests pass with 0 failures.

---

## 1. Exact Partition Identity Verification

To definitively establish whether P2.1 and P2.2 evaluated on the identical test partition, the full NF-ToN pool ($N = 13,135,881$) was re-aggregated from `nfton_train_features.csv` and `nfton_test_features.csv`. The greedy multi-objective bin-packing algorithm was executed to assign all 257,870 unique coordinate groups into Train (70%), Calibration (15%), and Test (15%) partitions under seed 42.

The resulting test partition was compared against `results/experiments/p2_coordinate_generalization/coordinate_disjoint_predictions.parquet`.

### Table 1: Cryptographic Hashes of Benchmark Test Partition ($N = 1,970,428$)

| Partition Property | Value / Dimensions | Format / Type | SHA-256 Digest |
|---|---|---|---|
| **Ordered Test Row Indices** | 1,970,428 indices | `int64` array | `3d704050854460426b3cf14d4d7575b17594fd19a39da42f4e110a2942fe4d6d` |
| **Ordered Test Ground Truth (`y_true`)** | 1,970,428 labels | `uint8` array | `2be847b2334cc27ba4e062e76f622dac9ece769e5f797391547e84b48214b01f` |
| **Ordered Test Feature Matrix (`X_test`)** | $1,970,428 \times 4$ | `float32` array | `616177a0b9df628d82838ec65892cb0ef7347aa0c5227a8edcee753ba81893bd` |
| **Ordered Coordinate Group IDs** | 1,970,428 group IDs | `int64` array | `2a89a4518bdea9dd7cfc680bca757d1d6fdc167a89a42234bf447b4686561969` |

### Partition Summary Metrics
- **Total NF-ToN Pool Rows:** 13,135,881
- **Total Unique Coordinate Groups in Pool:** 257,870
- **Train Partition:** 9,195,024 flows (187,526 groups, 69.999% pool volume)
- **Calibration Partition:** 1,970,429 flows (35,213 groups, 15.000% pool volume)
- **Test Partition:** 1,970,428 flows (35,131 groups, 15.000% pool volume)
- **Test Attack Prevalence:** $72.58438\%$ (1,430,223 attack flows; 540,205 benign flows)
- **Coordinate-Disjoint Verification:** **0 overlapping coordinates between Train, Calibration, and Test partitions** ($J = 0.0000$).

**Verdict on Partition Identity:** **IDENTICAL BIT-FOR-BIT**. P2.1 and P2.2 evaluated on the exact same dataset, row ordering, and coordinate clusters.

---

## 2. Reconciled Prediction Artifact Registry

Every model checkpoint, inference script, and prediction artifact across P2.1 and P2.2 was mapped and cryptographically verified:

### Table 2: Model Checkpoint and Prediction Array Provenance

| Model Name | Category | Model Checkpoint Path | Checkpoint SHA-256 | Inference Script | Prediction Artifact Path | Prediction Array SHA-256 |
|---|---|---|---|---|---|---|
| **In-Domain Disjoint XGBoost** | In-Domain Supervised | `results/experiments/p2_coordinate_generalization/xgboost_disjoint_seed42.json` | `22f6343c4e362dc2` | `scripts/p2_experiment_c_disjoint.py` | `results/.../coordinate_disjoint_predictions.parquet` (`xgb_prob_seed42`) | `ddb1090362a96fce` |
| **In-Domain Disjoint LightGBM** | In-Domain Supervised | `results/experiments/p2_coordinate_generalization/lightgbm_disjoint_seed42.txt` | `1a7ebb93ac7bc8e9` | `scripts/p2_experiment_c_disjoint.py` | `results/.../coordinate_disjoint_predictions.parquet` (`lgb_prob_seed42`) | `e6a6d3b30a9cc189` |
| **Clean Class-Aware CORAL + XGBoost** | Cross-Domain | `artifacts/models/xgb_adapted.json` | `6697c214a3c83fb1` | `scripts/p2_1_same_test_comparison.py` | Direct Inference (`p_clean`) | `16b6b302569efa95` |
| **Global CORAL + XGBoost** | Cross-Domain | `data/.../ciciot_train_coral_aligned.csv` | `445f8154a52d7bfb` | `scripts/p2_1_same_test_comparison.py` | Direct Inference (`p_coral`) | `efd181191fbc2c78` |
| **Source-Only XGBoost** | Cross-Domain | `artifacts/models/xgb_source.json` | `bca5465ace699d1c` | `scripts/p2_1_same_test_comparison.py` | Direct Inference (`p_src`) | `a438033cda13e867` |
| **DANN PyTorch Network** | Cross-Domain | `data/.../dann_best_model.pt` | `9e226d4bfde9121a` | `scripts/p2_1_same_test_comparison.py` | Direct Inference (`p_dann`) | `50a7cf495c84727a` |

*Full 64-character SHA-256 hashes are recorded in `results/experiments/p2_3_reconciliation/P2_3_PREDICTION_ARTIFACT_RECONCILIATION.csv`.*

---

## 3. Metric Recomputation & Explanation of All Differences

All 13 performance metrics and 4 confusion matrix quadrants were recomputed from the verified prediction arrays and ground truth labels.

### Table 3: Side-by-Side Metric Recomputation and Reconciliation

| Model Name | Threshold ($\tau$) | Recomputed Accuracy | P2.1 Reported Accuracy | P2.2 On-Disk Accuracy | P2.2 Chat Claimed Accuracy | Recomputed MCC | P2.1 Reported MCC | P2.2 On-Disk MCC | P2.2 Chat Claimed MCC | Recomputed ROC-AUC | P2.1 / P2.2 On-Disk ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **In-Domain Disjoint LightGBM** | 0.50 (def) | **0.7105** | 0.7105 | 0.7105 | *0.7441* | **0.3298** | 0.3298 | 0.3298 | 0.3298 | **0.6510** | 0.6510 |
| **In-Domain Disjoint LightGBM** | 0.10 (cal) | **0.7397** | 0.7397 | 0.7397 | — | **0.1909** | 0.1909 | 0.1909 | — | **0.6510** | 0.6510 |
| **In-Domain Disjoint XGBoost** | 0.50 (def) | **0.6895** | 0.6895 | 0.6895 | *0.7423* | **0.2539** | 0.2539 | 0.2539 | 0.2539 | **0.7754** | 0.7754 |
| **In-Domain Disjoint XGBoost** | 0.87 (cal) | **0.4037** | 0.4037 | 0.4037 | — | **0.1729** | 0.1729 | 0.1729 | — | **0.7754** | 0.7754 |
| **Clean Class-Aware CORAL** | 0.50 (def) | **0.3722** | 0.3722 | 0.3722 | — | **0.0504** | 0.0504 | 0.0504 | *0.3458* | **0.4695** | 0.4695 |
| **Clean Class-Aware CORAL** | 0.99 (cal) | **0.3594** | 0.3594 | 0.3594 | — | **0.0795** | 0.0795 | 0.0795 | — | **0.4695** | 0.4695 |
| **Global CORAL + XGBoost** | 0.50 (def) | **0.6912** | 0.6912 | 0.6912 | — | **-0.0554**| -0.0554| -0.0554| — | **0.4175** | 0.4175 |
| **Source-Only XGBoost** | 0.50 (def) | **0.7259** | 0.7259 | 0.7259 | — | **0.0060** | 0.0060 | 0.0060 | — | **0.5402** | 0.5402 |
| **DANN** | 0.50 (def) | **0.7258** | 0.7258 | 0.7258 | — | **0.0000** | 0.0000 | 0.0000 | — | **0.5000** | 0.5000 |
| **DANN** | 0.60 (cal) | **0.7258** | 0.7258 | 0.7258 | — | **0.0000** | 0.0000 | 0.0000 | — | **0.5000** | 0.5000 |

### Table 4: Recomputed Confusion Matrices ($N = 1,970,428$)

| Model Name | Threshold | True Negative (TN) | False Positive (FP) | False Negative (FN) | True Positive (TP) | Total |
|---|---|---|---|---|---|---|
| **In-Domain Disjoint LightGBM** | 0.50 | 323,039 | 217,166 | 353,294 | 1,076,929 | 1,970,428 |
| **In-Domain Disjoint LightGBM** | 0.10 | 28,104 | 512,101 | 804 | 1,429,419 | 1,970,428 |
| **In-Domain Disjoint XGBoost** | 0.50 | 272,664 | 267,541 | 344,312 | 1,085,911 | 1,970,428 |
| **In-Domain Disjoint XGBoost** | 0.87 | 508,981 | 31,224 | 1,143,714 | 286,509 | 1,970,428 |
| **Clean Class-Aware CORAL** | 0.50 | 460,532 | 79,673 | 1,157,355 | 272,868 | 1,970,428 |
| **Clean Class-Aware CORAL** | 0.99 | 491,148 | 49,057 | 1,213,226 | 216,997 | 1,970,428 |
| **Global CORAL + XGBoost** | 0.50 | 17,382 | 522,823 | 85,561 | 1,344,662 | 1,970,428 |
| **Source-Only XGBoost** | 0.50 | 38 | 540,167 | 8 | 1,430,215 | 1,970,428 |
| **DANN** | 0.60 | 0 | 540,205 | 0 | 1,430,223 | 1,970,428 |

### Resolution of Specific Audit Questions

1. **Clean Class-Aware CORAL MCC: Where did 0.3458 come from?**
   - **Finding:** Clean Class-Aware CORAL achieved MCC **0.0504** ($\tau = 0.50$) and **0.0795** ($\tau = 0.99$).
   - **Root Cause:** The purported MCC of 0.3458 was an ungrounded conversational hallucination in the LLM chat summary of P2.2. No script, model, or artifact in the repository ever generated MCC 0.3458 for Clean CORAL on this partition. (The nearest numerical artifact was XGBoost calibrated MCC on seed 42 in the multi-split analysis, which was 0.3434).

2. **XGBoost Accuracy: 0.6895 vs. 0.7423?**
   - **Finding:** True authoritative accuracy on the benchmark coordinate-disjoint test partition is **0.6895** (MCC = 0.2539, ROC-AUC = 0.7754).
   - **Root Cause:** 0.7423 was hallucinated in the chat text. Both P2.1 and P2.2 on-disk reports record Accuracy = 0.6895.

3. **LightGBM Accuracy: 0.7105 vs. 0.7441?**
   - **Finding:** True authoritative accuracy on the benchmark coordinate-disjoint test partition is **0.7105** (MCC = 0.3298, ROC-AUC = 0.6510).
   - **Root Cause:** 0.7441 was hallucinated in the chat text (likely conflating calibrated precision 0.7441 from the P2 report line 221). Both P2.1 and P2.2 on-disk reports record Accuracy = 0.7105.

4. **Model-Specific ROC-AUC Distinction Confirmed**:
   - Disjoint XGBoost ROC-AUC: **0.775369** (PR-AUC = **0.884525**)
   - Disjoint LightGBM ROC-AUC: **0.650954** (PR-AUC = **0.842526**)
   - Disjoint models must never be reported as sharing a uniform ROC-AUC $\approx 0.78$.

---

## 4. Reconciled Cluster-Bootstrap Methodology

### Group Count Audit: 35,131 Groups vs. 1,466,613 Groups
- **Test Partition Group Count:** Exactly **35,131 unique coordinate clusters**.
- **Full Pool Group Count:** Exactly **257,870 unique coordinate clusters** across all 13,135,881 rows.
- **Audit Finding on "1,466,613 Groups":** This purported figure is mathematically impossible, as it exceeds the total unique coordinate groups in the entire NF-ToN dataset by $5.7\times$. The actual cluster bootstrap script (`scripts/p2_2_statistical_audit.py`) operated strictly on $K = 35,131$ groups.

### Resampling Integrity
- **Resampling Unit:** Unique coordinate clusters ($K = 35,131$), sampled with replacement via Multinomial distribution ($B = 1,000$ resamples, seed = 42).
- **Cluster Structure Preservation:** All flows sharing the exact same 4D coordinate are resampled together as a cluster, preserving the heavy-tailed cluster size distribution (ranging from 1 flow to 744,302 flows).
- **Degenerate Replicate Check:** **0 / 1,000 degenerate replicates** across all models.

### Table 5: Cluster-Robust 95% Confidence Intervals ($B = 1,000$ Resamples, $K = 35,131$ Groups)

| Model Name | Threshold | Metric | Point Estimate | Bootstrap Mean | Bootstrap Std Err | Cluster-Robust 95% CI |
|---|---|---|---|---|---|---|
| **In-Domain Disjoint LightGBM** | 0.50 | **MCC** | **0.3298** | 0.3344 | 0.0560 | **[0.2307, 0.4468]** |
| **In-Domain Disjoint LightGBM** | 0.50 | **Accuracy** | **0.7105** | 0.7161 | 0.0359 | **[0.6475, 0.7891]** |
| **In-Domain Disjoint LightGBM** | 0.50 | **Balanced Acc** | **0.6755** | 0.6752 | 0.0396 | **[0.6019, 0.7550]** |
| **In-Domain Disjoint LightGBM** | 0.50 | **Specificity** | **0.5980** | 0.5921 | 0.0718 | **[0.4578, 0.7329]** |
| **In-Domain Disjoint LightGBM** | 0.50 | **F1 Score** | **0.7906** | 0.7963 | 0.0268 | **[0.7441, 0.8504]** |
| **In-Domain Disjoint XGBoost** | 0.50 | **MCC** | **0.2539** | 0.2538 | 0.0526 | **[0.1554, 0.3607]** |
| **In-Domain Disjoint XGBoost** | 0.50 | **Accuracy** | **0.6895** | 0.6938 | 0.0371 | **[0.6234, 0.7686]** |
| **In-Domain Disjoint XGBoost** | 0.50 | **Balanced Acc** | **0.6320** | 0.6315 | 0.0373 | **[0.5627, 0.7077]** |
| **In-Domain Disjoint XGBoost** | 0.50 | **Specificity** | **0.5047** | 0.4991 | 0.0683 | **[0.3707, 0.6366]** |
| **In-Domain Disjoint XGBoost** | 0.50 | **F1 Score** | **0.7802** | 0.7850 | 0.0279 | **[0.7303, 0.8413]** |
| **Clean Class-Aware CORAL** | 0.50 | **MCC** | **0.0504** | 0.0571 | 0.1770 | **[-0.2783, 0.4124]** |
| **Clean Class-Aware CORAL** | 0.50 | **Accuracy** | **0.3722** | 0.3885 | 0.0877 | **[0.2285, 0.5735]** |
| **Clean Class-Aware CORAL** | 0.99 | **MCC** | **0.0795** | 0.0822 | 0.1760 | **[-0.2514, 0.4357]** |
| **Clean Class-Aware CORAL** | 0.99 | **Accuracy** | **0.3594** | 0.3758 | 0.0898 | **[0.2117, 0.5654]** |

---

## 5. Paired Model Comparisons via Cluster Bootstrap

To rigorously test whether differences between models are statistically significant, paired cluster bootstrap resampling was executed across the identical coordinate groups.

### Table 6: Paired Model Comparisons on Benchmark Test Partition

| Model Comparison | Point Difference ($\Delta\text{MCC}$) | Bootstrap Mean Diff | Bootstrap Std Err | Cluster-Robust 95% CI | Empirical Two-Sided $p$-value | Statistically Significant ($\alpha = 0.05$)? |
|---|---|---|---|---|---|---|
| **Clean CORAL vs. LightGBM ($\tau = 0.50$)** | **-0.2794** | -0.2773 | 0.1886 | **[-0.6506, +0.0785]** | **0.154** | **No** (CI includes 0) |
| **Clean CORAL vs. XGBoost ($\tau = 0.50$)** | **-0.2035** | -0.1967 | 0.1916 | **[-0.5855, +0.1511]** | **0.324** | **No** (CI includes 0) |
| **LightGBM vs. XGBoost ($\tau = 0.50$)** | **+0.0758** | +0.0806 | 0.0610 | **[-0.0162, +0.2251]** | **0.140** | **No** (CI includes 0) |
| **Clean CORAL ($\tau = 0.99$) vs. LightGBM** | **-0.2502** | -0.2522 | 0.1857 | **[-0.6359, +0.0937]** | **0.180** | **No** (CI includes 0) |
| **Clean CORAL ($\tau = 0.99$) vs. XGBoost** | **-0.1744** | -0.1716 | 0.1919 | **[-0.5572, +0.1817]** | **0.384** | **No** (CI includes 0) |

### Observation-Level Likelihood / Loss Tests (Clustered Sandwich Variance)
- **Log-Loss Difference (XGBoost vs. LightGBM):**  
  $\Delta\text{Loss} = -0.1300$ (XGBoost has lower log-loss; $0.5444$ vs. $0.6745$).  
  Clustered Sandwich SE: $0.0845$; $z = -1.5386$; $p = \mathbf{0.1239}$ (not statistically significant at $\alpha = 0.05$).
- **Brier Score Difference (XGBoost vs. LightGBM):**  
  $\Delta\text{Brier} = -0.0446$ (XGBoost has lower mean squared probability error; $0.1819$ vs. $0.2265$).  
  Clustered Sandwich SE: $0.0284$; $z = -1.5713$; $p = \mathbf{0.1161}$ (not statistically significant at $\alpha = 0.05$).

### Scientific Interpretation
- While in-domain supervised models achieve higher point estimates than cross-domain CORAL ($\text{MCC} = 0.3298$ and $0.2539$ vs. $0.0504$), the paired cluster-robust confidence intervals span zero due to the substantial clustering variance inherent in network flow traffic.
- Under rigorous cluster-robust inference, **the null hypothesis that in-domain and cross-domain models perform equivalently on unseen coordinate clusters cannot be rejected at the 5% significance level**. Claims of categorical domain adaptation collapse must be qualified by this clustering uncertainty.

---

## 6. Audit of Coordinate Overlap and Leakage Terminology

The audit investigated the precise nature of coordinate repetition across the NF-ToN dataset and established essential scientific distinctions:

### Conceptual Distinctions
1. **Exact Duplicate Observations:**
   Observations where all feature values $(x_1, \dots, x_d)$ **and the ground-truth label $y$** are identical.
2. **Repeated Four-Feature Coordinates:**
   Observations where the 4 feature coordinates $(x_1, x_2, x_3, x_4)$ are identical, regardless of whether their labels match.
3. **Repeated Coordinates with Conflicting Labels (Label Ambiguity):**
   Observations mapping to the exact same 4D coordinate that possess both `label = 0` (benign) and `label = 1` (attack) across different occurrences in the dataset. In NF-ToN, **75.72% of test observations belong to coordinates with conflicting labels**.
4. **Shared Capture / Session Records:**
   Observations originating from the same physical TCP/UDP connection, network device, or packet capture session.

### Methodological Limitation Regarding "Data Leakage" Claims
- The feature datasets (`nfton_train_features.csv` and `nfton_test_features.csv`) contain **only the 4 transformed feature columns and the binary label**. They lack timestamps, IP 5-tuples (source IP, source port, destination IP, destination port, protocol), and session/flow identifiers.
- Because distinct physical flows frequently project onto identical continuous feature values (e.g., standard single-packet scans, fixed MTU transfers, or TCP SYN-ACK handshakes), coordinate overlap represents **feature-space coarse-graining and dimensional compression**, not necessarily session-level copy-paste leakage.
- **Prohibition:** ARGUS research papers must **not characterize repeated 4D coordinates as train-test data leakage without empirical proof of shared session/capture provenance**. The phenomenon must be described accurately as *coordinate repetition* or *feature ambiguity*.

---

## 7. Test Suite Reconciliation (283 vs. 271 Tests)

The test suite discrepancy reported between P2.1 (283 tests) and P2.2 (271 tests) was audited.

### Reconciliation Finding
The numerical change is **entirely an artifact of pytest CLI test discovery scope**:
- When pytest is run with directory scoping (`.venv/bin/python3 -m pytest tests/`), it only discovers test files inside the top-level `tests/` directory, collecting **271 tests**.
- When pytest is run from the workspace root without directory restrictions (`.venv/bin/python3 -m pytest`), it discovers all test files in the project, including 12 internal agent and orchestrator test cases located under `src/`, collecting **283 tests**.

### Table 7: The 12 Internal Agent Tests Located in `src/`

| # | Test File Path | Test Identifier | Status |
|---|---|---|---|
| 1 | `src/argus/agents/decision_support/tests/test_agent.py` | `test_agent_pipeline` | PASSED |
| 2 | `src/argus/agents/decision_support/tests/test_decision_rules.py` | `test_playbook_selection` | PASSED |
| 3 | `src/argus/agents/decision_support/tests/test_decision_rules.py` | `test_recommendation_and_priority` | PASSED |
| 4 | `src/argus/agents/risk_prediction/tests/test_agent.py` | `test_agent_pipeline` | PASSED |
| 5 | `src/argus/agents/risk_prediction/tests/test_agent_integration.py` | `test_agent_full_pipeline` | PASSED |
| 6 | `src/argus/agents/risk_prediction/tests/test_agent_integration.py` | `test_agent_missing_data_pipeline` | PASSED |
| 7 | `src/argus/agents/risk_prediction/tests/test_risk_rules.py` | `test_critical_asset_analyzer` | PASSED |
| 8 | `src/argus/agents/risk_prediction/tests/test_risk_rules.py` | `test_risk_scorer` | PASSED |
| 9 | `src/argus/agents/threat_analysis/tests/test_agent.py` | `test_agent_initialization` | PASSED |
| 10 | `src/argus/agents/threat_analysis/tests/test_agent.py` | `test_agent_validate` | PASSED |
| 11 | `src/argus/orchestrator/tests/test_pipeline_integration.py` | `test_full_argus_agent_pipeline` | PASSED |
| 12 | `src/argus/orchestrator/tests/test_pipeline_integration.py` | `test_full_argus_agent_pipeline_failure` | PASSED |

**Test Suite Verification:**
- Command: `.venv/bin/python3 -m pytest -q`
- Result: **283 passed, 0 failed, 0 skipped, 832 non-fatal library warnings in 8.16s**
- **Zero tests were deleted, removed, disabled, or renamed.**

---

## 8. Cryptographic Deliverables Manifest

All required deliverables have been generated, validated, and placed in `results/experiments/p2_3_reconciliation/`:

### Table 8: Deliverables Manifest

| Deliverable File | Size (Bytes) | SHA-256 Digest | Purpose |
|---|---|---|---|
| [`P2_3_PARTITION_IDENTITY.json`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/P2_3_PARTITION_IDENTITY.json) | 1,836 | `ed2fb81e60d7523e970ecdba9135c00c8bde69de51799860a501d64b13d85a44` | Bit-for-bit partition verification and SHA-256 hashes of test data |
| [`P2_3_PREDICTION_ARTIFACT_RECONCILIATION.csv`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/P2_3_PREDICTION_ARTIFACT_RECONCILIATION.csv) | 2,986 | `2fcd1c0ffe284f6d65dbd093a1a28c341b3a81382f8cbf07585ead04315fc737` | Checkpoint, inference script, and prediction array provenance table |
| [`P2_3_METRIC_RECOMPUTATION.csv`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/P2_3_METRIC_RECOMPUTATION.csv) | 5,872 | `32f112eaab6889b32c8f0cf744fe852aeafa8ec4deb06ce99413dc253aa266f7` | Complete recomputation of all 13 metrics and reconciliation explanations |
| [`P2_3_BOOTSTRAP_RECONCILIATION.json`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/P2_3_BOOTSTRAP_RECONCILIATION.json) | 9,598 | `5b9ee01080e6c7a5537c1616b3f2b1cb18a73213d9f57781924f45ab24308b78` | Cluster bootstrap reconciliation (K = 35,131 groups, B = 1,000 resamples) |
| [`P2_3_PAIRED_MODEL_COMPARISONS.json`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/P2_3_PAIRED_MODEL_COMPARISONS.json) | 5,519 | `2ac2bac62b6aa62b31b33abb898a1a63961c72e9c3126cfb095a0bde23dc0715` | Paired cluster bootstrap differences and observation loss tests |
| [`P2_3_TEST_SUITE_RECONCILIATION.json`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/P2_3_TEST_SUITE_RECONCILIATION.json) | 1,968 | `f6cd8aadc5563367addd5b7de2226488d6ecd659a2dc168c3a78a3bc63e8a14a` | Discovery scope audit reconciling 283 vs. 271 test counts |
| [`P2_3_REPRODUCIBILITY_MANIFEST.json`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/P2_3_REPRODUCIBILITY_MANIFEST.json) | 4,142 | `0e0cb828bb7c83f9825b12ee960411894d075d9e5175cf643f01905869aeb875` | Cryptographic manifest of all artifacts, inputs, and scripts |

---

## 9. Final Scientific Decision and Audit Verdict

### Final Verdict: `PASS WITH QUALIFICATIONS`

### Scientific Justification

1. **Reconciliation Complete & Definitive:**
   The exact partition identity, prediction pipelines, metric computations, and test counts between P2.1 and P2.2 have been completely reconciled and verified against raw data and model checkpoints. The apparent numerical contradictions were conclusively proven to be ungrounded text hallucinations in the LLM chat summary of P2.2, contrasting with 100% verified consistency across all committed on-disk code, reports, and JSON artifacts.

2. **Qualifications Required for Publication:**
   - **Clustering Uncertainty:** Because network flow coordinates exhibit severe heavy-tailed clustering, paired cluster-robust confidence intervals for model differences span zero. Scientific publications must not claim statistically significant superiority of in-domain models over cross-domain models under coordinate-disjoint splitting without disclosing the paired cluster bootstrap $p$-values ($p = 0.154$ and $p = 0.324$).
   - **Leakage Terminology Constraint:** Due to the absence of flow timestamps and 5-tuple network metadata, coordinate repetition must not be labeled as "session data leakage." It must be accurately described as coordinate repetition and feature-space ambiguity.
   - **Separate Metric Reporting:** XGBoost ($\text{ROC-AUC} = 0.7754$, $\text{MCC} = 0.2539$) and LightGBM ($\text{ROC-AUC} = 0.6510$, $\text{MCC} = 0.3298$) exhibit distinct inductive behaviors and must be reported separately.
