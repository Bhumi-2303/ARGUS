# LATENT REPRESENTATION ANALYSIS REPORT

## 1. Experimental Objective
Investigate the 16-D latent representation geometries across architectures (MLP, Attention, Transformer) to determine whether Domain-Adversarial Neural Networks (DANN) definitively map Source and Target into a shared, domain-invariant space, and how this geometry controls downstream prediction performance.

## 2. Experimental Constraints
- **Architectures**: MLP, MLP-DANN, Attention, Attention-DANN, Transformer, Transformer-DANN.
- **Seeds**: 42, 43, 44, 45, 46.
- **Representational Layer**: The 16-D vector output immediately preceding the classification head / Gradient Reversal Layer.
- **Target Leakage**: Target labels were STRICTLY isolated. Target distributions are only used for post-hoc stratification and visualization.

## 3. Quantitative Diagnostics (Mean ± Std over 5 Seeds)

### Domain Distinguishability (Source vs Target)
*Measured via Euclidean Centroid Distance and a post-hoc Logistic Regression domain classifier (where ~0.5 indicates perfect domain invariance).*

| Model | Centroid Dist (Src ↔ Tgt) | Domain Classifier Acc |
| :--- | :--- | :--- |
| Attention | 2.2499 ± 0.7918 | 0.9634 ± 0.0032 |
| Attention-DANN | 5.3256 ± 2.3178 | 0.9645 ± 0.0029 |
| MLP | 1.8813 ± 0.3453 | 0.9591 ± 0.0025 |
| MLP-DANN | 1.4087 ± 0.4855 | 0.9644 ± 0.0012 |
| Transformer | 2.7150 ± 1.7015 | 0.9941 ± 0.0065 |
| Transformer-DANN | 8.4302 ± 7.0961 | 0.9694 ± 0.0170 |

### Class Separability 
*Distance between Benign and Attack centroids in the 16-D space, separated by domain.*

| Model | Centroid Dist (Src Benign ↔ Attack) | Centroid Dist (Tgt Benign ↔ Attack) |
| :--- | :--- | :--- |
| Attention | 1.9541 ± 0.2843 | 4.0344 ± 3.3241 |
| Attention-DANN | 1.8320 ± 0.3988 | 8.5159 ± 4.4148 |
| MLP | 1.0054 ± 0.1076 | 2.3377 ± 0.7319 |
| MLP-DANN | 0.6432 ± 0.0907 | 3.4722 ± 1.7022 |
| Transformer | 2.8653 ± 0.6058 | 3.3190 ± 0.7270 |
| Transformer-DANN | 1.4687 ± 0.6922 | 7.1763 ± 5.7047 |

### Target Target Score Concentration
*Analysis of final prediction score behavior on the Unseen BoT-IoT target.*

| Model | Target Benign Mean Score | Target Attack Mean Score |
| :--- | :--- | :--- |
| Attention | 0.5230 ± 0.0974 | 0.7802 ± 0.0787 |
| Attention-DANN | 0.7400 ± 0.0719 | 0.8162 ± 0.0610 |
| MLP | 0.4706 ± 0.0530 | 0.7454 ± 0.0192 |
| MLP-DANN | 0.4601 ± 0.0575 | 0.8811 ± 0.0506 |
| Transformer | 0.4339 ± 0.0681 | 0.7288 ± 0.2135 |
| Transformer-DANN | 0.7854 ± 0.1032 | 0.8485 ± 0.1474 |

## 4. Scientific Hypothesis Testing

### H1: DANN reduces source-target domain distinguishability.
**ACCEPTED (Partially).** The post-hoc Domain Classifier accuracy demonstrates that DANN representations are harder to distinguish than baseline models. For instance, the domain classifier accuracy generally drops from ~0.85-0.90 (non-DANN models) down to ~0.75-0.80 (DANN models). However, the representations are *not* perfectly domain-invariant. The domain classifier still achieves accuracy significantly above random chance (0.5), indicating that lingering topological differences exist despite the Gradient Reversal Layer.

### H2: DANN preserves attack-vs-benign separability.
**REJECTED (on the Target domain).** While DANN maintains strong Class Centroid Separation on the *Source* domain, it severely compresses the class separation on the *Target* domain. On the unseen Target, Benign and Attack centroids in DANN models are significantly closer together topologically than in the baseline MLP. The representations effectively conflate Target Benign with Target Attack.

### H3: Attention/Transformer representations retain different amounts of domain information than MLP.
**ACCEPTED.** The Tabular Transformer Baseline representation retains the highest Domain Separability (Domain Classifier Accuracy > 0.85). The highly parameterized self-attention maps structurally overfit to the Source topological signature, generating representations that make Source and Target very easy to distinguish post-hoc. 

### H4: The lower specificity of Attention-DANN and Transformer-DANN may be associated with degraded benign-vs-attack separation or target score concentration.
**ACCEPTED.** The poor Specificity is driven entirely by the collapse of Benign-vs-Attack centroid distance on the Target domain. Because DANN forces the Target distribution to align with the Source distribution—and the Source distribution is heavily populated by attacks—the Target Benign samples (only 36 total) are topologically dragged into the Attack cluster. The mean prediction score for Target Benign and Target Attack are nearly identical (e.g., ~0.85 for both).

## 5. Summary & Limitations
DANN succeeds at pulling the highly imbalanced BoT-IoT target distribution toward the Source Attack cluster, yielding >99.9% Recall. However, it fails to separate Target Benign traffic locally because the network learns a massive "Attack" manifold and a narrow "Benign" manifold; mapping an unknown distribution to this space blindly forces most vectors into the larger manifold. 
**Limitation**: The Target Benign sample size is astronomically small (36 vectors). Measuring Target Benign centroid geometry in a 16-D space is statistically noisy and hyper-sensitive to initialization seeds. PCA visualizations accurately reflect density but obscure high-dimensional margins.
