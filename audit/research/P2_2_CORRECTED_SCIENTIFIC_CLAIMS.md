# ARGUS P2.2 — Final Corrected Scientific Claims and Publication Constraints

**Document:** `audit/research/P2_2_CORRECTED_SCIENTIFIC_CLAIMS.md`  
**Audit Phase:** ARGUS P2.2 — Final Statistical Robustness and Publication Readiness  
**Auditor Role:** Independent Senior ML Research Auditor  
**Date:** November 2, 2026  
**Status:** Authoritative Publication Standard  
**Repository:** `/home/bhumi/GitHub/ARGUS`  

---

## 1. Executive Policy on Publication Claims

This document defines the authoritative scientific claims permitted in the ARGUS journal manuscript. Following the P2.1 benchmark correction and P2.2 multi-split robustness audit, previous unsupported statements and over-generalizations are strictly prohibited. Every claim must align with directly verified empirical evidence, model-specific metrics, and cluster-robust statistical inference.

---

## 2. Master Evaluation of Scientific Claims

| # | Scientific Claim / Statement | Formal Audit Classification | Empirical Evidence & Methodology | Publication Status |
|---|---|---|---|---|
| **1** | *"In-domain performance degrades significantly under coordinate-disjoint evaluation."* | **Supported (with Qualifications)** | Evaluated across 5 independent group-disjoint splits, XGBoost MCC is $0.4550 \pm 0.2303$ (range: 0.1351 to 0.6735) and LightGBM MCC is $0.3545 \pm 0.1753$ (range: 0.0840 to 0.5592), down from historical in-domain baseline MCC of 0.6127–0.6698 on repeated coordinates. | **Approved for Publication** |
| **2** | *"All in-domain models maintain ROC-AUC approximately 0.78."* | **Unsupported (Corrected)** | In the benchmark disjoint test partition, **only XGBoost achieves ROC-AUC = 0.7754** (PR-AUC = 0.8845). **LightGBM achieves ROC-AUC = 0.6510** (PR-AUC = 0.8425). Across 5 independent splits, XGBoost ROC-AUC is $0.7878 \pm 0.0337$, while LightGBM ROC-AUC is $0.7395 \pm 0.0739$. Conflating both models under "ROC-AUC ~ 0.78" is false and prohibited. | **Retracted & Separated** |
| **3** | *"Clean Class-Aware CORAL wins the coordinate-disjoint benchmark."* | **Unsupported (Prohibited)** | On the identical 1,970,428 coordinate-disjoint test partition, Clean CORAL achieves MCC = **0.0795** ($\tau = 0.99$) and **0.0504** ($\tau = 0.50$), trailing in-domain XGBoost (MCC = **0.2539**) and LightGBM (MCC = **0.3298**). P2's claim resulted from an invalid cross-partition comparison. | **Strictly Prohibited** |
| **4** | *"Universal failure of domain adaptation across IoT domains."* | **Unsupported (Prohibited)** | Domain adaptation methods (Clean CORAL, Global CORAL, DANN) failed to transfer between CIC-IoT-2023 and NF-ToN-IoT-v2 under the 4 engineered flow features. However, claiming *universal failure* across all domain adaptation algorithms, architectures, and IoT datasets is an unwarranted extrapolation. | **Strictly Prohibited** |
| **5** | *"94.61% is the theoretical Bayes ceiling (5.39% irreducible error floor)."* | **Unsupported (Prohibited)** | 94.61% is an empirical in-sample purity metric of coordinate clusters under lossy 4D projection. Under disjoint evaluation, coordinate lookup coverage is **0.00%**, and lookup accuracy drops to **72.58%** (class prevalence). It does not represent the theoretical Bayes rate of underlying network flows. | **Strictly Prohibited** |
| **6** | *"Universal domain-wide concept drift between CIC-IoT-2023 and NF-ToN-IoT-v2."* | **Unsupported (Prohibited)** | Class inversion occurred on 21 of 27 shared coordinates ($p < 10^{-7}$). However, 27 coordinates represent $< 0.02\%$ of unique coordinates in either domain. Extrapolating universal concept drift across the unobserved 99.98% manifold is statistically invalid. | **Strictly Prohibited** |
| **7** | *"LightGBM statistically significantly outperforms XGBoost on novel coordinates."* | **Partially Supported (Qualified)** | LightGBM achieved higher point MCC (0.3298 vs 0.2539) on the benchmark test split, but a paired cluster-bootstrap test yields $\Delta\text{MCC} = +0.0758$ with 95% CI `[-0.0162, +0.2251]` ($p = 0.1400$), which is **not statistically significant**. Group-accuracy tests cannot substitute for MCC significance tests. Across 5 independent splits, XGBoost mean MCC is actually higher ($0.4550 \pm 0.2303$ vs $0.3545 \pm 0.1753$). | **Qualified & Contextualized** |
| **8** | *"Decision threshold optimization is probability calibration."* | **Unsupported (Corrected)** | Threshold tuning chooses a decision boundary $\tau \in [0.01, 0.99]$ on uncalibrated model scores. It does not alter probability reliability or produce calibrated posterior probabilities $P(Y=1 \mid \hat{p})$. | **Retracted & Corrected** |

---

## 3. Mandatory Replacement Wording for Manuscript Sections

### Section 4.1: In-Domain Generalization & Partition Variance
> *"To eliminate coordinate repetition artifacts, models were evaluated across five independently generated coordinate-disjoint partitions. In-domain supervised XGBoost achieved a mean test MCC of $0.4550 \pm 0.2303$ (range: 0.1351 to 0.6735; mean ROC-AUC = $0.7878 \pm 0.0337$), while LightGBM achieved a mean test MCC of $0.3545 \pm 0.1753$ (range: 0.0840 to 0.5592; mean ROC-AUC = $0.7395 \pm 0.0739$). In the primary benchmark partition, XGBoost achieved MCC = 0.2539 (ROC-AUC = 0.7754, PR-AUC = 0.8845) and LightGBM achieved MCC = 0.3298 (ROC-AUC = 0.6510, PR-AUC = 0.8425). Although LightGBM attained higher point MCC on the primary partition, the paired cluster-bootstrap difference was not statistically significant ($\Delta\text{MCC} = +0.0758$, 95% CI: `[-0.0162, +0.2251]`, $p = 0.1400$), and XGBoost demonstrated superior overall discrimination (ROC-AUC 0.7754 vs 0.6510)."*

### Section 4.2: Cross-Domain Transfer vs. In-Domain Disjoint Baselines
> *"When evaluated on the identical 1,970,428-sample coordinate-disjoint test partition, all cross-domain transfer models suffered severe performance degradation. Historical Clean Class-Aware CORAL attained an MCC of 0.0795 at its historical calibrated threshold ($\tau = 0.99$) and 0.0504 at default threshold ($\tau = 0.50$), trailing in-domain supervised models by 0.17 to 0.25 in MCC. Source-Only XGBoost collapsed to MCC = 0.0060, DANN collapsed to MCC = 0.0000 (predicting positive for all instances), and Global CORAL achieved MCC = -0.0554 (performing worse than random guessing). The earlier suggestion that domain adaptation outperformed disjoint supervised baselines was a methodological artifact resulting from evaluating models on disparate test partitions."*

### Section 4.3: Threshold Transferability Analysis
> *"Selecting decision thresholds on calibration data to maximize F1 score exhibited severe out-of-sample instability when transferred to coordinate-disjoint test data. Because the calibration set exhibited 72.58% attack prevalence, the calibration optimizer selected extreme thresholds ($\tau^* \in [0.11, 0.88]$). When transferred to novel coordinate clusters in the test set, these extreme thresholds caused substantial performance drops (up to -0.33 in MCC), collapsing specificity or recall. The default threshold ($\tau = 0.50$) demonstrated substantially greater stability across independent partitions."*

### Section 5.1: Localized Conditional Shift vs. Universal Concept Drift
> *"Direct cross-domain comparison between CIC-IoT-2023 and NF-ToN-IoT-v2 identified exactly 27 shared 4D coordinates at float64 precision. Among these, 21 coordinates (77.8%) exhibited statistically significant class-label inversion ($p < 10^{-7}$, Fisher's exact test $p < 0.05$ on 20/27, mean $|\Delta P| = 0.6727$). However, these 27 coordinates account for less than 0.02% of unique coordinate clusters in either domain. Furthermore, inspection of the network traffic reveals that identical coordinates arise from repeated homogeneous flood attack sessions (e.g., 709k packets of identical length and flag structure) rather than independent flow observations. While this confirms localized conditional distribution shift $P_{D1}(Y|X) \neq P_{D2}(Y|X)$, it cannot be extrapolated to assert universal domain-wide concept drift across the broader continuous manifold."*

---

## 4. Summary of Model-Specific Metrics for Publication Tables

### Table 1: Primary Coordinate-Disjoint Test Partition ($N = 1,970,428$)
*Exact recomputed values from `results/experiments/p2_1_validation/P2_1_SAME_TEST_CROSS_DOMAIN_COMPARISON.csv`.*

| Model Name | Threshold ($\tau$) | Accuracy | Precision | Recall | F1 Score | Balanced Acc | Specificity | MCC | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|---|
| **In-Domain Disjoint LightGBM** | 0.50 (def) | 0.7105 | 0.8322 | 0.7530 | 0.7906 | 0.6755 | 0.5980 | **0.3298** | **0.6510** | **0.8425** |
| **In-Domain Disjoint XGBoost** | 0.50 (def) | 0.6895 | 0.8023 | 0.7593 | 0.7802 | 0.6320 | 0.5047 | **0.2539** | **0.7754** | **0.8845** |
| **Clean Class-Aware CORAL** | 0.99 (hist) | 0.3594 | 0.8156 | 0.1517 | 0.2559 | 0.5305 | 0.9092 | **0.0795** | **0.4695** | **0.7093** |
| **Clean Class-Aware CORAL** | 0.50 (def) | 0.3722 | 0.7740 | 0.1908 | 0.3061 | 0.5217 | 0.8525 | **0.0504** | **0.4695** | **0.7093** |
| **Source-Only XGBoost** | 0.50 (def) | 0.7259 | 0.7259 | 1.0000 | 0.8412 | 0.5000 | 0.0001 | **0.0060** | **0.5402** | **0.7516** |
| **DANN** | 0.60 (hist) | 0.7258 | 0.7258 | 1.0000 | 0.8411 | 0.5000 | 0.0000 | **0.0000** | **0.5000** | **0.7258** |
| **Global CORAL + XGBoost** | 0.50 (def) | 0.6912 | 0.7200 | 0.9402 | 0.8155 | 0.4862 | 0.0322 | **-0.0554** | **0.4175** | **0.6702** |

### Table 2: Multi-Split Partition Stability Across 5 Independent Group Splits ($\tau = 0.50$)
*Source: `results/experiments/p2_2_robustness/P2_2_INDEPENDENT_SPLIT_METRICS.csv`.*

| Model Architecture | Metric | Mean $\pm$ Std Dev | Minimum | Maximum | Partition Seed 42 | Partition Seed 101 | Partition Seed 202 | Partition Seed 303 | Partition Seed 404 |
|---|---|---|---|---|---|---|---|---|---|
| **XGBoost** | **MCC** | **0.4550 $\pm$ 0.2303** | 0.1351 | 0.6735 | 0.6735 | 0.6119 | 0.1351 | 0.2932 | 0.5616 |
| **XGBoost** | **ROC-AUC** | **0.7878 $\pm$ 0.0337** | 0.7311 | 0.8166 | 0.8091 | 0.8166 | 0.7311 | 0.7952 | 0.7870 |
| **XGBoost** | **F1 Score** | **0.8356 $\pm$ 0.0941** | 0.6693 | 0.9161 | 0.9161 | 0.9066 | 0.6693 | 0.7892 | 0.8967 |
| **LightGBM** | **MCC** | **0.3545 $\pm$ 0.1753** | 0.0840 | 0.5592 | 0.3121 | 0.0840 | 0.4202 | 0.3968 | 0.5592 |
| **LightGBM** | **ROC-AUC** | **0.7395 $\pm$ 0.0739** | 0.6196 | 0.8040 | 0.8040 | 0.6196 | 0.7953 | 0.7297 | 0.7487 |
| **LightGBM** | **F1 Score** | **0.7868 $\pm$ 0.0987** | 0.6385 | 0.8872 | 0.8062 | 0.6385 | 0.8242 | 0.7777 | 0.8872 |

---

## 5. Prohibited Formulations in Publication Drafts

Authors and contributors are formally instructed to remove any phrasing resembling the following:
1. ❌ *"Clean CORAL beats in-domain models on coordinate-disjoint data."* $\to$ **Forbidden.** (CORAL MCC is 0.0795 vs in-domain 0.2539–0.3298 on identical test rows).
2. ❌ *"All in-domain models achieve ROC-AUC ~ 0.78."* $\to$ **Forbidden.** (XGBoost is 0.7754; LightGBM is 0.6510).
3. ❌ *"5.39% is the theoretical irreducible error floor / 94.61% is the Bayes ceiling."* $\to$ **Forbidden.** (It is an in-sample cluster collision rate).
4. ❌ *"Universal domain adaptation failure in IoT."* $\to$ **Forbidden.** (Must be constrained to D1 $\to$ D2 transfer under 4-feature representation).
5. ❌ *"Pervasive domain-wide concept drift across the feature space."* $\to$ **Forbidden.** (Must be restricted to localized shift on 27 shared coordinates accounting for $< 0.02\%$ support).
6. ❌ *"Probability calibration improved / worsened the models."* $\to$ **Forbidden.** (Threshold tuning was applied, not probability calibration).
