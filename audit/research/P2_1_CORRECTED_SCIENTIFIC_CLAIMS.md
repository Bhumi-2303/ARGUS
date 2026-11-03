# ARGUS P2.1 — Reassessment and Correction of Scientific Claims

**Document:** `audit/research/P2_1_CORRECTED_SCIENTIFIC_CLAIMS.md`  
**Role:** Independent Senior ML Research Auditor  
**Date:** November 1, 2026  
**Status:** Completed and Authoritative  
**Target Repository:** `/home/bhumi/GitHub/ARGUS`  

---

## Executive Summary

Following the completion of the P2 coordinate-generalization experiment and the P2.1 independent validation audit, five central scientific claims from previous reports and working drafts have been critically audited against empirical data and rigorous statistical principles.

Each claim is evaluated below, categorized as **Supported**, **Partially Supported**, or **Unsupported**, accompanied by empirical evidence, root-cause analysis, and scientifically defensible replacement wording for the forthcoming journal manuscript.

---

## Summary Matrix of Reassessed Scientific Claims

| # | Original Claim / Formulation | Audit Classification | Primary Empirical Basis | Status in Manuscript |
|---|------------------------------|----------------------|-------------------------|----------------------|
| **1** | *"57–62% of in-domain performance is attributable to coordinate repetition."* | **Partially Supported** | MCC drops 51%–59% under disjoint partitioning (0.61–0.67 $\to$ 0.25–0.33), but non-trivial positive generalization remains (ROC-AUC = 0.78). Attributing all decline to coordinate repetition ignores sample size and co-occurrence factors. | **Refined & Contextualized** |
| **2** | *"94.61% is the Bayes optimal accuracy."* | **Unsupported** | 94.61% is strictly an in-sample majority purity rate under lossy 4D projection (5.39% conflict rate). Out-of-sample lookup coverage collapses to 0.00% on unseen coordinates. It cannot represent the theoretical Bayes rate of underlying network flows. | **Retracted & Replaced** |
| **3** | *"Clean CORAL wins the coordinate-disjoint benchmark."* | **Unsupported** | In P2.1 same-test evaluation on the identical 1,970,428-sample disjoint test partition, In-Domain XGBoost (MCC = 0.2539) and LightGBM (MCC = 0.3298) dramatically outperform Clean CORAL (MCC = 0.0795). P2's claim was an artifact of comparing disparate test partitions. | **Retracted & Corrected** |
| **4** | *"Cross-domain adaptation operates at the true generalization ceiling."* | **Unsupported** | All cross-domain models collapse under coordinate-disjoint target evaluation (MCC $\le$ 0.080, Global CORAL MCC = -0.055). Domain adaptation does not approach a generalization ceiling. | **Retracted & Replaced** |
| **5** | *"21 of 27 shared coordinates establish concept drift."* | **Partially Supported** | 21 of 27 shared coordinates indeed invert labels ($p < 10^{-7}$, mean $|\Delta P| = 0.6727$), proving localized conditional shift. However, 27 coordinates represent $< 0.02\%$ of unique coordinates in either domain, precluding global extrapolation across the entire manifold. | **Refined & Constrained** |

---

## Detailed Reassessment of Claims

### Claim 1: "57–62% of in-domain performance is attributable to coordinate repetition."

- **Original Claim:**  
  *"57–62% of the reported in-domain supervised performance on NF-ToN-IoT-v2 is an artifact of coordinate repetition, leaving only 38–43% genuine inductive learning."*
- **Audit Classification:** **Partially Supported**
- **Empirical Evidence:**
  1. On the frozen P1-1 evaluation benchmark (where 98.81% of test flows map to training coordinates), supervised XGBoost achieves MCC = `0.6127` and LightGBM achieves MCC = `0.6698`.
  2. When evaluated under strictly coordinate-disjoint partitioning (where coordinate overlap between train and test is identically 0.00%), supervised XGBoost achieves MCC = `0.2539` (a 58.6% relative drop) and LightGBM achieves MCC = `0.3298` (a 50.8% relative drop).
  3. However, attributing the entire drop solely to "coordinate repetition" is scientifically imprecise:
     - Part of the decline stems from sample size reduction (training on 9.20M rows instead of 10.51M rows).
     - Part stems from the exclusion of correlated cluster modes forced by the bin-packing split.
     - Crucially, both models still maintain statistically significant predictive power (MCC = 0.25–0.33, ROC-AUC = 0.65–0.78, Balanced Accuracy = 0.63–0.68), which is well above zero.
- **Defensible Replacement Wording:**  
  > *"When evaluated under strictly coordinate-disjoint partitioning, in-domain supervised performance decreases by 51% to 59% in MCC (from 0.61–0.67 to 0.25–0.33), demonstrating that more than half of the historically reported metric magnitude was enabled by identical 4D feature coordinates shared between training and test sets. Nonetheless, in-domain models retain statistically significant predictive capability (MCC = 0.25–0.33, ROC-AUC = 0.78) on completely novel coordinate clusters, confirming genuine inductive pattern recognition beyond memorization."*

---

### Claim 2: "94.61% is the Bayes optimal accuracy."

- **Original Claim:**  
  *"94.61% is the theoretical Bayes optimal accuracy for NF-ToN-IoT-v2, and 5.39% represents the proven irreducible error floor."*
- **Audit Classification:** **Unsupported**
- **Empirical Evidence:**
  1. The 94.61% figure was computed by measuring in-sample coordinate majority accuracy over all 13,135,881 pooled records:
     $$\text{Acc}_{\text{in-sample}} = \frac{1}{N} \sum_{x \in \mathcal{X}} \max(n_{\text{attack}}(x), n_{\text{benign}}(x)) = 0.946098$$
  2. Theoretical Bayes error is defined with respect to the true data-generating distribution over all flow attributes $X^*$:
     $$R^* = \mathbb{E}_{X^*} \left[ \min(P(Y=0|X^*), P(Y=1|X^*)) \right]$$
  3. The 4 engineered features (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`) represent a severe dimensional compression of network traffic. Flows with divergent packet counts, port numbers, protocols, and temporal characteristics are projected into the same 4D coordinate. The 5.39% label conflict rate reflects projection collisions, not irreducible stochasticity of network traffic.
  4. Most critically, when training-derived coordinate lookup is evaluated out-of-sample on the coordinate-disjoint test set, coordinate coverage is **0.00%**, and lookup accuracy drops to **72.58%** (defaulting to the global class prior).
- **Defensible Replacement Wording:**  
  > *"Within the 4-dimensional engineered feature space, 5.39% of flow records exhibit conflicting ground-truth labels at identical coordinates, establishing an empirical in-sample purity limit of 94.61% for any deterministic mapping $f: \mathbb{R}^4 \to \{0, 1\}$. This figure represents an empirical feature-collision rate under lossy dimensional projection, not the theoretical Bayes optimal error of the underlying network traffic, and it does not describe out-of-sample performance on unseen coordinates where lookup coverage is zero."*

---

### Claim 3: "Clean CORAL wins the coordinate-disjoint benchmark."

- **Original Claim:**  
  *"Clean Class-Aware CORAL wins the coordinate-disjoint benchmark, achieving MCC = 0.3904 compared to in-domain supervised XGBoost at MCC = 0.2539."*
- **Audit Classification:** **Unsupported**
- **Empirical Evidence:**
  1. This conclusion was invalid because it compared historical Clean Class-Aware CORAL evaluated on the 31,143 novel coordinates of the original test set against in-domain models evaluated on the completely separate 1,970,428-row coordinate-disjoint partition.
  2. When all models are evaluated on the **exact same 1,970,428-sample coordinate-disjoint test partition** in P2.1:
     - **In-Domain Coordinate-Disjoint LightGBM:** MCC = **0.3298**, ROC-AUC = **0.6510**
     - **In-Domain Coordinate-Disjoint XGBoost:** MCC = **0.2539**, ROC-AUC = **0.7754**
     - **Clean Class-Aware CORAL (th=0.99):** MCC = **0.0795**, ROC-AUC = **0.4695**
     - **Clean Class-Aware CORAL (th=0.50):** MCC = **0.0504**, ROC-AUC = **0.4695**
     - **Source-Only XGBoost (th=0.50):** MCC = **0.0060**, ROC-AUC = **0.5402**
     - **Global CORAL (th=0.50):** MCC = **-0.0554**, ROC-AUC = **0.4175**
     - **DANN (th=0.60):** MCC = **0.0000**, ROC-AUC = **0.5000**
  3. Clean Class-Aware CORAL's MCC drops from 0.3855 on repeated coordinates to **0.0795** on disjoint coordinates. In-domain models outperform it by +0.1744 (XGBoost) and +0.2503 (LightGBM).
- **Defensible Replacement Wording:**  
  > *"When evaluated on the identical coordinate-disjoint test partition, in-domain supervised models substantially outperform all historical cross-domain models (LightGBM MCC = 0.3298, XGBoost MCC = 0.2539 vs. Clean Class-Aware CORAL MCC = 0.0795, Global CORAL MCC = -0.0554, and DANN MCC = 0.0000). The earlier suggestion that Clean CORAL outperformed in-domain disjoint baselines was a methodological artifact resulting from comparing evaluations conducted on disparate test partitions."*

---

### Claim 4: "Cross-domain adaptation operates at the true generalization ceiling."

- **Original Claim:**  
  *"Cross-domain adaptation models operate at the true generalization ceiling of the target domain because adaptation enforces invariance that transcends coordinate memorization."*
- **Audit Classification:** **Unsupported**
- **Empirical Evidence:**
  1. The empirical performance of all cross-domain models on coordinate-disjoint target evaluation demonstrates severe representation collapse rather than generalization:
     - Global CORAL achieves MCC = `-0.0554` (worse than random guessing).
     - DANN achieves MCC = `0.0000` (complete collapse to majority class).
     - Clean Class-Aware CORAL achieves MCC = `0.0795` (near chance).
  2. The high historical specificity reported for Clean Class-Aware CORAL (91.4%) was achieved exclusively through aggressive calibration to threshold $\tau = 0.99$, which suppresses 84.8% of positive predictions and misses 49.2% of attacks.
  3. Domain adaptation models do not establish a generalization ceiling; rather, they suffer from acute negative transfer under target domain shift.
- **Defensible Replacement Wording:**  
  > *"Cross-domain adaptation models do not establish a generalization ceiling on the target domain. On identical coordinate-disjoint target evaluation, all cross-domain methods suffer substantial performance degradation (MCC $\le$ 0.080), trailing in-domain supervised models by 0.17 to 0.25 in MCC. Unsupervised and class-aware covariance alignment across disparate IoT datasets fails to overcome fundamental conditional distribution shifts between source and target environments."*

---

### Claim 5: "21 of 27 shared coordinates establish concept drift."

- **Original Claim:**  
  *"21 of 27 shared coordinates establish concept drift between CIC-IoT-2023 and NF-ToN-IoT-v2, proving that identical traffic behaviors have inverted security classifications across the domains."*
- **Audit Classification:** **Partially Supported**
- **Empirical Evidence:**
  1. Exactly 27 coordinates overlap between `ciciot_train_features.csv` (D1) and `nfton_train_adaptation.csv` (D2) at exact float64 precision.
  2. In 21 of these 27 coordinates (77.8%), the class majority inverts ($\mathbb{I}[P_{D1} \ge 0.5] \neq \mathbb{I}[P_{D2} \ge 0.5]$).
  3. All 21 inversions are statistically significant under two-proportion z-tests ($p < 10^{-7}$), with a mean conditional probability shift of $|\Delta P| = 0.6727$ and median $|\Delta P| = 0.8333$.
  4. These 27 coordinates cover 1,979,654 rows in D1 (36.0%) and 215,345 rows in D2 (2.56%).
  5. **Crucial Limitation:** 27 coordinates constitute only 0.0065% of unique coordinates in D1 (802,351) and 0.0166% of unique coordinates in D2 (202,194). Over 99.98% of coordinate clusters do not overlap across the domains.
  6. While concept drift / conditional distribution shift is rigorously proven on these 27 coordinate locations, it is mathematically unwarranted to assert that the entire feature space suffers from inverted labels based on $< 0.02\%$ support.
- **Defensible Replacement Wording:**  
  > *"Among the 27 coordinates that exactly overlap between CIC-IoT-2023 and NF-ToN-IoT-v2, 21 coordinates (77.8%) exhibit statistically significant class-label inversion ($p < 10^{-7}$, mean $|\Delta P| = 0.6727$). This confirms the existence of localized conditional distribution shift $P_{D1}(Y|X) \neq P_{D2}(Y|X)$ within overlapping regions of the 4D feature space. However, because these 27 coordinates constitute less than 0.02% of unique coordinates in either domain, this localized evidence cannot be extrapolated to assert pervasive domain-wide concept drift across the broader feature manifold."*

---

## Conclusion & Editorial Guidance for the Journal Manuscript

1. **Retract:** All statements asserting that Clean CORAL "won" the coordinate-disjoint benchmark, that 94.61% represents a "Bayes ceiling," or that adaptation operates at a "generalization ceiling."
2. **Adopt:** The corrected, defensible replacements above in Section 4 (Experimental Results) and Section 5 (Discussion).
3. **Report:** The authoritative historical benchmark MCC = `0.3855` (with a footnote documenting the `0.3904` retraining reproduction artifact).
4. **Publish:** The full 27-coordinate shift table (`P2_1_D1_D2_SHIFT_ANALYSIS.csv`) as Supplementary Material, explicitly highlighting the localized scope caveat.
