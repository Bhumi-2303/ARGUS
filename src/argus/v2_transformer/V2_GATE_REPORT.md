# V2 Group-Token Transformer Gate Report

## 1. Domain Separability Check (Learned Embeddings)
We extracted the `[CLS]` token continuous embeddings from the trained Transformer for 30,000 samples across the three domains. We trained a Random Forest (`max_depth=5`) on these learned representations to predict the domain.

*   **Pairwise (CICIoT vs NF-ToN):** 99.99%
*   **3-Way (CICIoT vs NF-ToN vs BoT-IoT):** 99.95%

*Finding:* This is **worse** (more leaky) than both the original 4-feature space (98.88% / 87.16%) and the V1.5 space (99.92% / 99.90%). The combination of the explicit Timing token (which we already proved was leaky) and the structural sequence-length artifact (masking the Directional token in CICIoT) allows the transformer to perfectly cluster domains.

## 2. Per-Domain Diversity / Degeneracy Check
To measure if the transformer avoids the BoT-IoT collapse, we computed "effective unique vectors" by rounding the 32-dimensional continuous `[CLS]` embeddings to 2 decimal places and counting unique states.

*   **CICIoT2023:** 4,564 / 30,000 (15.21% unique)
*   **NF-ToN-IoT-v2:** 4,577 / 30,000 (15.26% unique)
*   **BoT-IoT:** 19 / 30,000 (**0.06% unique**)

*Finding:* The architecture completely fails to resolve the BoT-IoT degeneracy. Because BoT-IoT flood traffic contains identical values across all raw packet and volumetric fields, the resulting token embeddings remain identical, collapsing 30,000 flows into effectively 19 distinct transformer representations. 

## 3. Cross-Domain Seed Stability
We ran the supervised training across 3 random seeds (42, 123, 456) to measure cross-domain variance.

*   **CICIoT -> NF-ToN B.Acc:** 0.5000 ± 0.0000 (Model simply predicts Attack for everything).
*   **NF-ToN -> CICIoT B.Acc:** 0.1741 ± 0.1834

*Finding:* The baseline cross-domain generalization is not only catastrophically low but also highly unstable across seeds (variance of ±18% on NF-ToN -> CICIoT), confirming that the model arbitrarily relies on domain-specific spurious correlations that shift entirely based on weight initialization.

## 4. Verdict: NO-GO
**NO-GO.**

Do not proceed to class-conditional alignment or group-level shift diagnostics on this architecture. 

**Justification:**
1.  **Masking acts as a Domain Fingerprint:** The attention-masking design creates a sequence-length artifact that makes the representations 99.99% domain-separable. 
2.  **BoT-IoT Collapse Persists:** The group-token design simply passes the exact same degenerate raw values into linear layers, resulting in the exact same degenerate downstream embeddings for BoT-IoT (0.06% diversity).
3.  **Fundamental Tension Unsolved:** This V2 direction suffers from the exact same fatal flaws as the V1.5 feature expansion. It does not solve the discriminative-vs-domain-invariant tension, but merely shifts it into the transformer's embedding space. 

This research thread should stop here pending a fundamentally different mechanism for handling structural dataset disparity.
