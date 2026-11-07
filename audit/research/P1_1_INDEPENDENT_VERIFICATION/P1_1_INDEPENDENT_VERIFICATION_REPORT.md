# ARGUS P1-1 — Independent Scientific Verification and Closure Audit Report

**Audit Type**: Independent Scientific & Reproducibility Verification  
**Experiment**: ARGUS P1-1 NF-ToN-IoT-v2 In-Domain Supervised Baseline  
**Auditor**: Independent Machine Learning Research Auditor  
**Date**: 2026-11-01  
**Audit Decision**: **`PASS WITH QUALIFICATIONS`**  
**Repository**: `/home/bhumi/GitHub/ARGUS`  
**Git Branch**: `v2-transformer-exploratory`  
**Git Commit**: `63224da92eafec6a1ab1d4ffc7625d19744c05eb`  

---

## 1. Executive Summary & Audit Verdict

An exhaustive, adversarial audit of the ARGUS P1-1 in-domain supervised baseline experiment was performed. The scope encompassed data partition provenance, coordinate degeneracy and group leakage, training execution, calibration mathematics, independent test metric recalculation, historical comparison parity, and peer-review scrutiny of scientific conclusions.

### Final Status: **`PASS WITH QUALIFICATIONS`**

### Verdict Breakdown:
- **Technical Implementation & Arithmetic Integrity**: **`PASS`**. 
  Every reported metric, threshold, confusion matrix count, and plot was independently recalculated and verified against saved Parquet predictions and Booster models. There is **zero numerical discrepancy** between independent recalculation and reported figures. Deterministic inference samples reproduced model outputs with zero error.
- **Experimental Evaluation Parity**: **`PASS`**. 
  Row-for-row verification against historical artifacts (`dann_final_test_predictions.csv` and `final_clean_classaware_results/`) proved that all models (Source-Only, Global CORAL, Clean Class-Aware CORAL, DANN, and In-Domain Supervised) evaluated the exact same 2,627,177 frozen test observations in identical sequence.
- **Partition & Duplicate Structure**: **`QUALIFIED (HIGH DUPLICATE OVERLAP)`**. 
  The legacy NF-ToN partition was generated via stratified random row-level sampling. Because the feature space is compressed to 4 statistical dimensions, **98.67% of test rows share coordinates with training rows**. Furthermore, **79.04% of training rows** map to 4D coordinates containing conflicting ground-truth labels (both benign and attack).
- **Scientific Claims & Conclusions**: **`QUALIFIED (NARROWING REQUIRED)`**. 
  Three of four major conceptual claims in the P1-1 report require formal qualification:
  1. The 4-feature model cannot be claimed as an "upper bound" (it is restricted to 4 features out of 43+ native features).
  2. Ratio division of scalar MCC values cannot be mathematically claimed as "% of correlation recovered".
  3. Duplicate flow collapse does *not* affect models symmetrically; random-split coordinate repetition enables in-domain base-rate memorization while penalizing cross-domain transfer.

---

## 2. Dataset Provenance and Partition Verification

Authoritative data files in [`data/raw/legacy_package/argus_coral_data/`](file:///home/bhumi/GitHub/ARGUS/data/raw/legacy_package/argus_coral_data/) were audited via chunked SHA-256 computation and exhaustive row scanning:

| Dataset Partition | File Path | Actual Rows ($N$) | Benign ($y=0$) | Attack ($y=1$) | Attack Prevalence | SHA-256 Digest | Status |
|---|---|---:|---:|---:|---:|---|---|
| **Training (Adaptation)** | [`nfton_train_adaptation.csv`](file:///home/bhumi/GitHub/ARGUS/data/raw/legacy_package/argus_coral_data/nfton_train_adaptation.csv) | **8,406,962** | 2,304,821 | 6,102,141 | 72.5844% | `63de394798c89f342348e2a57eeb9cdf09f3bae71bc723ae779eb4d23fd0fb22` | **VERIFIED UNMODIFIED** |
| **Calibration** | [`nfton_train_calibration.csv`](file:///home/bhumi/GitHub/ARGUS/data/raw/legacy_package/argus_coral_data/nfton_train_calibration.csv) | **2,101,742** | 576,206 | 1,525,536 | 72.5844% | `c1574c73ea80f30d51eb9473182fbfdf2d4a1547f42481a0c66baab2c7e3f101` | **VERIFIED UNMODIFIED** |
| **Frozen Test** | [`nfton_test_features.csv`](file:///home/bhumi/GitHub/ARGUS/data/raw/legacy_package/argus_coral_data/nfton_test_features.csv) | **2,627,177** | 720,257 | 1,906,920 | 72.5844% | `23325cb206a525f5087287d4c385579caa73abf64c5fcbe80a6c5b881a7733f7` | **VERIFIED UNMODIFIED** |
| **Full Training Sum** | [`nfton_train_features.csv`](file:///home/bhumi/GitHub/ARGUS/data/raw/legacy_package/argus_coral_data/nfton_train_features.csv) | **10,508,704** | 2,881,027 | 7,627,677 | 72.5844% | `2b5221e51b31e369e7c972a84a7f115bb49670cf35d666b8f3f5c71c99539f75` | **VERIFIED UNMODIFIED** |

### Verification Findings:
1. **Mathematical Partition Identity**:
   $$\text{Adaptation Rows } (8,406,962) + \text{Calibration Rows } (2,101,742) = 10,508,704 \equiv \text{nfton\_train\_features.csv}$$
   The adaptation partition represents exactly **80.0000%** of the full training data; calibration represents exactly **20.0000%**.
2. **Stratification Uniformity**:
   All partitions possess an identical attack prevalence of **72.5844%** ($\pm 0.0001\%$), confirming stratified random row-level partitioning.
3. **Absence of Corruptions**:
   Zero NaN values, zero infinite values, and zero out-of-range floats detected across all features.
4. **Data Leakage Check**:
   No test rows or labels were present in the training or calibration files. Test data was accessed solely during final blind evaluation.

---

## 3. Duplicate and Group Leakage Forensic Audit

A comprehensive hash-mapping audit of 4D feature vectors across the 13.1 million rows was conducted. Complete metrics are recorded in [`P1_1_PARTITION_AND_DUPLICATE_AUDIT.json`](file:///home/bhumi/GitHub/ARGUS/audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_PARTITION_AND_DUPLICATE_AUDIT.json) and analyzed in [`P1_1_LEAKAGE_AUDIT.md`](file:///home/bhumi/GitHub/ARGUS/audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_LEAKAGE_AUDIT.md).

### 3.1 Empirical Duplicate Counts
- **Test Set**: 2,627,177 rows contain only **102,188 unique feature vectors** (96.11% duplicate rate).
- **Training Adaptation Set**: 8,406,962 rows contain only **202,194 unique feature vectors** (97.59% duplicate rate).
- **Cross-Split Repetition**: **2,592,203 test rows (98.67%)** share identical 4D feature vectors with rows in the training adaptation set. Only **31,143 test rows (1.19%)** have novel feature coordinates.

### 3.2 Label Conflict and Bayes Floor
- Network traffic features compressed to 4 coarse statistical variables map different services, hosts, and protocols to identical coordinates.
- In Training: **16,456 feature vectors (8.14%)** carry conflicting labels (both $y=0$ and $y=1$), covering **6,644,645 rows (79.04% of training)**.
- In Test: **5,538 feature vectors (5.42%)** carry conflicting labels, covering **1,989,306 rows (75.72% of test)**.
- **Significance**: Under cross-entropy loss, gradient boosted trees partition these 202,194 unique coordinates and predict the empirical majority label of each cluster. The test accuracy of 93.3% reflects this Bayes optimal resolution of the conflicting 4D clusters.

---

## 4. Training Implementation & Deterministic Inference Verification

Audit of [`scripts/train_nfton_in_domain_baseline.py`](file:///home/bhumi/GitHub/ARGUS/scripts/train_nfton_in_domain_baseline.py), [`xgboost_nfton_in_domain.json`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p1_1_nfton_in_domain/xgboost_nfton_in_domain.json), and [`lightgbm_nfton_in_domain.txt`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p1_1_nfton_in_domain/lightgbm_nfton_in_domain.txt):

1. **Training Sample Fidelity**: Both models were fitted on all 8,406,962 rows of `nfton_train_adaptation.csv`. No subsampling, row filtering, or synthetic oversampling was performed.
2. **Feature Integrity**: Exactly the 4 harmonized features were fed in order `['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']`. Target label was strictly excluded from inputs.
3. **Model Topologies**:
   - XGBoost: 100 boosted rounds (`max_depth = 8`, `tree_method = 'hist'`, `binary:logistic`, unweighted).
   - LightGBM: 100 boosted trees (`num_leaves = 63`, `max_depth = 8`, `binary`, unweighted).
4. **Deterministic Inference Reproduction**:
   Independent probability prediction was executed on a test sample of 5,000 observations using the saved model artifacts:
   - XGBoost maximum absolute error vs. saved Parquet: **`0.0000000000`**
   - LightGBM maximum absolute error vs. saved Parquet: **`0.0000000297`** (single-precision float precision limit)
   - **Verdict**: Serialized models match saved prediction artifacts 100%.

---

## 5. Calibration and Threshold Selection Audit

Audit of [`scripts/evaluate_nfton_in_domain_baseline.py`](file:///home/bhumi/GitHub/ARGUS/scripts/evaluate_nfton_in_domain_baseline.py) and [`nfton_calibration_thresholds.json`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p1_1_nfton_in_domain/nfton_calibration_thresholds.json):

1. **Isolation**: Calibration was executed strictly on `nfton_train_calibration.csv` ($N = 2,101,742$) with zero access to test labels.
2. **Objective**: Evaluated 99 thresholds $\tau \in [0.01, 0.99]$ optimizing Matthews Correlation Coefficient (MCC).
3. **Independent Mathematical Verification**:
   Running a safe independent grid search on the calibration set yielded:
   - XGBoost: $\tau^* = 0.57$ (Calibration MCC = **0.831923**) $\to$ **100% MATCH**
   - LightGBM: $\tau^* = 0.55$ (Calibration MCC = **0.831797**) $\to$ **100% MATCH**
4. **Probability Calibration vs. Threshold Tuning**:
   - The reported procedure is **decision threshold tuning**, not probability calibration (Platt scaling or isotonic regression).
   - The test set Brier score was independently verified as **0.0526** (XGBoost) and **0.0522** (LightGBM), confirming that raw logistic probabilities are naturally well-calibrated.

---

## 6. Metric Recalculation and Numerical Parity Table

All metrics were independently recalculated directly from [`xgboost_test_predictions.parquet`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p1_1_nfton_in_domain/xgboost_test_predictions.parquet), [`lightgbm_test_predictions.parquet`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p1_1_nfton_in_domain/lightgbm_test_predictions.parquet), and [`nfton_test_features.csv`](file:///home/bhumi/GitHub/ARGUS/data/raw/legacy_package/argus_coral_data/nfton_test_features.csv). Full audit table saved to [`P1_1_METRIC_RECALCULATION.csv`](file:///home/bhumi/GitHub/ARGUS/audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_METRIC_RECALCULATION.csv).

| Model | Operating Threshold | Metric Recalculated | Reported Value | Recalculated Audit Value | Discrepancy | Verification Status |
|---|---:|---|---:|---:|---:|---|
| **XGBoost** | 0.50 (Default) | Accuracy | 0.933536 | 0.933536 | 0.000000 | **MATCH** |
| | | Balanced Accuracy | 0.907730 | 0.907730 | 0.000000 | **MATCH** |
| | | Precision | 0.944746 | 0.944746 | 0.000000 | **MATCH** |
| | | Recall | 0.964862 | 0.964862 | 0.000000 | **MATCH** |
| | | Specificity | 0.850598 | 0.850598 | 0.000000 | **MATCH** |
| | | F1-Score | 0.954698 | 0.954698 | 0.000000 | **MATCH** |
| | | MCC | 0.830667 | 0.830667 | 0.000000 | **MATCH** |
| | | ROC-AUC | 0.969069 | 0.969069 | 0.000000 | **MATCH** |
| | | PR-AUC (Trapz) | 0.985973 | 0.985973 | 0.000000 | **MATCH** |
| | | Average Precision | 0.984600 | 0.984600 | 0.000000 | **MATCH** |
| | | TP / TN / FP / FN | 1839914 / 612649 / 107608 / 67006 | 1839914 / 612649 / 107608 / 67006 | 0 | **MATCH** |
| **XGBoost** | **0.57 (Calibrated)** | Accuracy | 0.933191 | 0.933191 | 0.000000 | **MATCH** |
| | | Balanced Accuracy | 0.915564 | 0.915564 | 0.000000 | **MATCH** |
| | | Precision | 0.953426 | 0.953426 | 0.000000 | **MATCH** |
| | | Recall | 0.954588 | 0.954588 | 0.000000 | **MATCH** |
| | | Specificity | 0.876541 | 0.876541 | 0.000000 | **MATCH** |
| | | F1-Score | 0.954006 | 0.954006 | 0.000000 | **MATCH** |
| | | MCC | 0.831966 | 0.831966 | 0.000000 | **MATCH** |
| | | TP / TN / FP / FN | 1820322 / 631335 / 88922 / 86598 | 1820322 / 631335 / 88922 / 86598 | 0 | **MATCH** |
| **LightGBM** | 0.50 (Default) | Accuracy | 0.933204 | 0.933204 | 0.000000 | **MATCH** |
| | | Balanced Accuracy | 0.908104 | 0.908104 | 0.000000 | **MATCH** |
| | | MCC | 0.829979 | 0.829979 | 0.000000 | **MATCH** |
| | | ROC-AUC | 0.969625 | 0.969625 | 0.000000 | **MATCH** |
| | | PR-AUC (Trapz) | 0.986307 | 0.986307 | 0.000000 | **MATCH** |
| | | Average Precision | 0.984914 | 0.984914 | 0.000000 | **MATCH** |
| **LightGBM** | **0.55 (Calibrated)** | Accuracy | 0.932893 | 0.932893 | 0.000000 | **MATCH** |
| | | Balanced Accuracy | 0.916052 | 0.916052 | 0.000000 | **MATCH** |
| | | Precision | 0.954169 | 0.954169 | 0.000000 | **MATCH** |
| | | Recall | 0.953337 | 0.953337 | 0.000000 | **MATCH** |
| | | Specificity | 0.878767 | 0.878767 | 0.000000 | **MATCH** |
| | | MCC | 0.831508 | 0.831508 | 0.000000 | **MATCH** |
| | | TP / TN / FP / FN | 1817938 / 632938 / 87319 / 88982 | 1817938 / 632938 / 87319 / 88982 | 0 | **MATCH** |

### Numerical Difference: PR-AUC vs. Average Precision:
- **XGBoost**: PR-AUC = 0.985973 vs. AP = 0.984600 ($\Delta = +0.001373$)
- **LightGBM**: PR-AUC = 0.986307 vs. AP = 0.984914 ($\Delta = +0.001393$)
- *Explanation*: PR-AUC applies trapezoidal interpolation between discrete points on the PR curve, which slightly overestimates area during linear segments between precision points. Average Precision (`average_precision_score`) uses standard step-function weighting $\sum_k (R_k - R_{k-1}) P_k$. The small difference ($\approx 0.14\%$) confirms minimal curve interpolation variance.

---

## 7. Historical Comparison Fairness Audit

Audited against [`dann_final_test_predictions.csv`](file:///home/bhumi/GitHub/ARGUS/data/raw/legacy_package/argus_coral_data/dann_results/dann_final_test_predictions.csv) and [`results/verified/five_model_complete_comparison.csv`](file:///home/bhumi/GitHub/ARGUS/results/verified/five_model_complete_comparison.csv). Full analysis in [`P1_1_COMPARISON_FAIRNESS.md`](file:///home/bhumi/GitHub/ARGUS/audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_COMPARISON_FAIRNESS.md).

### 7.1 Master Comparison Table

| Model Architecture | Training & Adaptation Regime | Threshold | Accuracy | Precision | Recall | F1 | Balanced Acc | Specificity | MCC | ROC-AUC | PR-AUC |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Source-Only XGBoost** | Zero-shot transfer (D1 $\to$ D2) | 0.50 | 0.7207 | 0.7247 | 0.9919 | 0.8375 | 0.4972 | 0.0025 | -0.0311 | 0.3230 | 0.6392 |
| **Global CORAL + XGBoost** | Unsupervised adaptation (D1 $\to$ D2) | 0.50 | 0.6347 | 0.7013 | 0.8652 | 0.7747 | 0.4448 | 0.0244 | -0.1610 | 0.2852 | 0.6215 |
| **DANN (Neural)** | Adversarial adaptation (D1 $\to$ D2) | 0.60 | 0.7259 | 0.7259 | 0.9998 | 0.8412 | 0.5002 | 0.0006 | 0.0129 | 0.3321 | 0.6422 |
| **Clean Class-Aware CORAL** | Supervised adaptation (D1 $\to$ D2) | 0.99 | 0.6191 | 0.9400 | 0.5076 | 0.6592 | 0.7109 | **0.9143** | 0.3855 | 0.5970 | 0.8313 |
| **XGBoost (In-Domain)** | **In-domain supervised** | **0.57** | **0.9332** | **0.9534** | **0.9546** | **0.9540** | **0.9156** | 0.8765 | **0.8320** | **0.9691** | **0.9860** |
| **LightGBM (In-Domain)** | **In-domain supervised** | **0.55** | **0.9329** | **0.9542** | **0.9533** | **0.9538** | **0.9161** | 0.8788 | **0.8315** | **0.9696** | **0.9863** |

### 7.2 Apples-to-Apples Evaluation Parity:
1. **Row-by-Row Sequence**: The test set row labels in `dann_final_test_predictions.csv` match `nfton_test_features.csv` with **zero mismatches out of 2,627,177 rows**.
2. **Feature & Preprocessing Space**: Exactly 4 harmonized statistical features without scaling.
3. **Training Distinction**: The models must be presented as **different supervision regimes**. The comparison measures the *performance penalty of cross-domain transfer relative to in-domain supervision*, not a direct algorithmic contest.

---

## 8. Audit of Scientific Interpretations

Detailed in [`P1_1_SCIENTIFIC_CLAIMS_REVIEW.md`](file:///home/bhumi/GitHub/ARGUS/audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_SCIENTIFIC_CLAIMS_REVIEW.md):

| Claim # | Tested Claim Statement | Audit Verdict | Mandatory Correction / Replacement |
|---|---|---|---|
| **Claim 1** | *"CORAL recovers only 46.3% of target-domain discriminative correlation."* | **UNSUPPORTED** | Division of scalar MCC values is statistically meaningless. Replace with: *"Clean Class-Aware CORAL achieves MCC 0.3855, which is 0.4465 points lower than in-domain supervision (MCC 0.8320)."* |
| **Claim 2** | *"Cross-domain degradation is an intrinsic feature geometry rank inversion."* | **PARTIALLY SUPPORTED** | Ranking degradation is real (ROC-AUC drops to 0.3230 in Source-Only), but geometry claim is speculative. Restate as threshold-independent conditional shift $P(y \mid x)$ and covariate shift $P(x)$. |
| **Claim 3** | *"The in-domain supervised baseline demonstrates the upper bound of target-domain performance."* | **UNSUPPORTED** | 4-feature model is constrained by severe coordinate overlap and 79% conflicting labels. Reframe as *"target-domain reference within the 4-feature harmonized subspace."* |
| **Claim 4** | *"Duplicate flow collapse affects all models symmetrically."* | **UNSUPPORTED** | Asymmetric impact: in-domain models benefit from random-split base-rate memorization at repeated coordinates (98.67% test row match), while cross-domain models suffer from prior shifts. |

---

## 9. Required Actions Prior to Journal Submission

1. **Reframe Performance Claims**: Update all paper manuscripts to describe P1-1 as an "in-domain 4-feature reference" rather than a theoretical performance upper bound.
2. **Remove MCC Ratio Arithmetic**: Express differences in correlation as absolute metric gaps ($\Delta \text{MCC} = -0.4465$).
3. **Disclose Random-Split Coordinate Overlap**: In the experimental methodology section, explicitly state that low-dimensional statistical feature extraction produces coordinate degeneracy where 98.67% of test flows share 4D coordinates with training flows.
4. **Conduct Coordinate-Deduplicated Sensitivity Study (Recommended P2)**: Evaluate performance on the 31,143 test rows that possess strictly novel 4D coordinates to measure out-of-coordinate generalization.

---

## 10. Auditor Sign-Off & Status Categorization

### Categorization of Findings:
- **Directly Verified**:
  - Exact row counts, class distributions, and SHA-256 digests of all partitions.
  - Absence of test labels during model training and threshold calibration.
  - Recomputed metrics matching reported CSV/JSON down to 6 decimal places.
  - Row-for-row test set identity between historical DANN and new in-domain predictions.
  - Replicated calibration thresholds ($\tau^* = 0.57$ XGBoost, $\tau^* = 0.55$ LightGBM).
- **Inferred from Data Geometry**:
  - The legacy partition was created via stratified random row-level sampling (inferred from identical 72.5844% class ratios across all files).
  - In-domain models act as empirical posterior lookups for the 98.67% repeated coordinates.
- **Could Not Be Verified**:
  - Original temporal timestamps, IP addresses, and flow session IDs (stripped in the legacy CORAL package).
  - True chronological or device-isolated generalization on NF-ToN-IoT-v2.

### Final Decision: **`PASS WITH QUALIFICATIONS`**
The empirical experiment is mathematically sound, reproducible, and transparently archived. With the scientific qualifications applied, P1-1 is cleared for research closure.
