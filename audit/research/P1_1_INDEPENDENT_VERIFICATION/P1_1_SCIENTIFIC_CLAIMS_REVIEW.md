# ARGUS P1-1 — Scientific Claims and Interpretation Audit

**Date**: 2026-11-01  
**Auditor**: Independent Machine Learning Research Auditor  
**Audit Scope**: Rigorous Peer-Review Evaluation of Key Scientific Claims in P1-1 Report  

---

## 1. Overview of Claims Audited

This audit evaluates four primary scientific assertions made in the P1-1 in-domain baseline report. Each claim was scrutinized against statistical principles, experimental evidence, and machine learning theory.

---

## 2. Granular Evaluation of Scientific Claims

### Claim 1: *"Clean Class-Aware CORAL recovers only 46.3% of target-domain discriminative correlation."*

- **Audit Classification**: **`UNSUPPORTED (METHODOLOGICALLY FLAWED)`**
- **Evidence & Audit Analysis**:
  - The P1-1 report calculated:
    $$\frac{\text{MCC}_{\text{CORAL}}}{\text{MCC}_{\text{In-Domain}}} = \frac{0.385503}{0.831966} = 46.336\%$$
  - The Matthews Correlation Coefficient is a bounded scalar correlation metric defined on $[-1, 1]$. Like Pearson's $r$ or Spearman's $\rho$, MCC is not an additive or ratio-scale measure of "recovered correlation percentage."
  - Ratio operations on correlation coefficients lack statistical meaning. For instance:
    - Source-Only XGBoost had an MCC of **-0.0311**.
    - Clean Class-Aware CORAL improved MCC to **+0.3855** (a shift of +0.4166 points across the zero-correlation boundary).
    - If one naively took a ratio relative to Source-Only, the improvement would be negative or undefined.
  - Furthermore, correlation does not scale linearly with mutual information or classification capacity.
- **Scientifically Defensible Replacement**:
  > *"Clean Class-Aware CORAL achieves an MCC of 0.3855 on the target domain (improving from -0.0311 under zero-shot transfer), which remains 0.4465 points lower than the 0.8320 MCC achieved under direct target-domain supervision on the identical 4-feature representation."*

---

### Claim 2: *"Cross-domain degradation is an intrinsic feature geometry rank inversion."*

- **Audit Classification**: **`PARTIALLY SUPPORTED`**
- **Evidence & Audit Analysis**:
  - **Supported Aspect**: The test set ROC-AUC drops from **0.9691** (in-domain) to **0.5970** (Clean Class-Aware CORAL) and **0.3230** (Source-Only). Because ROC-AUC is completely invariant to monotonic score scaling and decision threshold selection, an ROC-AUC of 0.3230 confirms that Source-Only suffers from true rank inversion (benign instances are assigned systematically higher attack scores than attacks).
  - **Unsupported / Speculative Aspect**: Attributing this degradation to an "intrinsic feature geometry rank inversion" makes an unverified causal assertion about manifold structure. The actual mechanism is covariate shift $P(x)$ combined with severe conditional probability shift $P(y \mid x)$ between CIC-IoT-2023 and NF-ToN-IoT-v2 across the 4 statistical summary features. Covariance alignment (CORAL) only matches second moments ($E[xx^T]$); it cannot correct conditional label inversion without target supervision.
- **Scientifically Defensible Replacement**:
  > *"Cross-domain transfer results in severe ranking degradation (ROC-AUC drops from 0.9691 in-domain to 0.5970 for CORAL and 0.3230 for Source-Only). Because ROC-AUC is threshold-independent, this confirms that performance loss is driven by underlying feature distribution and conditional probability shifts between domains, rather than suboptimal threshold calibration."*

---

### Claim 3: *"The in-domain supervised baseline demonstrates the upper bound of target-domain performance."*

- **Audit Classification**: **`UNSUPPORTED`**
- **Evidence & Audit Analysis**:
  - The models in P1-1 were restricted to **only 4 harmonized statistical features** (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`) to maintain direct parity with CORAL.
  - The native NF-ToN-IoT-v2 dataset contains over 43 NetFlow v2 features, including connection durations, inter-arrival times, byte rates, TCP window sizes, ICMP/DNS flags, and port metadata.
  - Compressing the dataset into 4 features creates an artificial information bottleneck: as proven in our duplicate audit, **79.04% of training rows** map to 4D coordinates that have conflicting benign and attack labels. This creates a high Bayes error floor (~6.7% minimum error) specific to the 4-feature representation.
  - An in-domain supervised model trained on the full native feature space would resolve these ambiguous clusters and achieve substantially higher accuracy and MCC.
  - Therefore, this model represents an **in-domain reference for the 4-feature harmonized space**, not an upper bound for target-domain intrusion detection.
- **Scientifically Defensible Replacement**:
  > *"The in-domain supervised models establish a target-domain performance reference under the identical 4-feature harmonized constraint, demonstrating the achievable supervised performance within this feature subspace rather than an unconstrained theoretical ceiling."*

---

### Claim 4: *"Duplicate flow collapse affects all models symmetrically."*

- **Audit Classification**: **`UNSUPPORTED`**
- **Evidence & Audit Analysis**:
  - Our partition duplicate audit revealed that **98.67% of test rows share identical 4D feature vectors with rows in the training set**.
  - In-domain supervised models and cross-domain transferred models interact with these duplicated coordinates in fundamentally asymmetrical ways:
    1. **In-Domain Models**: Directly observe the target domain's empirical label distribution $P_{\text{Target}}(y \mid x)$ during training. For repeated coordinates, gradient boosting simply memorizes the empirical majority class of that coordinate cluster in the training set. Because the test set was sampled uniformly at random from the same master distribution, the test set empirical distribution matches the training set, directly boosting in-domain test accuracy.
    2. **Cross-Domain Models**: Trained on source domain D1 (CIC-IoT-2023). For the exact same statistical coordinates, the source domain's class ratio $P_{\text{Source}}(y \mid x)$ may be completely inverted.
  - Consequently, coordinate repetition inflates in-domain supervised test performance via random-split base-rate memorization, while penalizing transferred models whenever domain priors diverge. The effect is strictly asymmetric.
- **Scientifically Defensible Replacement**:
  > *"Duplicate and near-duplicate feature vectors across the random train/test split affect in-domain and cross-domain models asymmetrically: in-domain models benefit from observing target-domain class base rates at repeated coordinates, whereas cross-domain models suffer from prior and conditional distribution shifts at those same coordinates."*

---

## 3. Summary of Claim Verdicts

| Claim # | Claim Topic | Audit Verdict | Recommended Action |
|---|---|---|---|
| **Claim 1** | Ratio of MCC interpreted as "% correlation recovered" | **UNSUPPORTED** | Replace with absolute delta ($+0.4465$ MCC gap) |
| **Claim 2** | ROC-AUC degradation as "feature geometry rank inversion" | **PARTIALLY SUPPORTED** | Restate as threshold-independent conditional & covariate shift |
| **Claim 3** | 4-feature in-domain model as "upper bound" | **UNSUPPORTED** | Reframe as "in-domain reference within 4-feature constraint" |
| **Claim 4** | Duplicate flow collapse as "symmetric impact" | **UNSUPPORTED** | Document asymmetric benefit of random split to in-domain models |
