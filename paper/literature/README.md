# Literature Grounding & Theoretical Taxonomy (`paper/literature/`)

This directory houses the comprehensive literature review, conceptual taxonomies, and citation source notes supporting the ARGUS research paper: **"Cross-Domain Generalization Failure in IoT/SCADA Intrusion Detection: Representation Resolution and Class-Aware Adaptation"**.

---

## 1. Directory Organization

```text
paper/literature/
├── README.md                      # Overview of literature categories and verification status
└── LITERATURE_REVIEW.md           # Comprehensive critical survey of foundational literature and gaps
```

---

## 2. Literature Categories & Verification Status

| Category | Primary Works | Relevance to ARGUS | Verification Status |
| :--- | :--- | :--- | :---: |
| **NIDS Closed-World Evaluation Failures** | Sommer & Paxson (2010), Apruzzese et al. (2022) | Fundamental motivation: why ML NIDS fails upon deployment across environments | **Reviewed & Verified** |
| **Standardized Network Flow Schemas** | Sarhan et al. (2022), Neto et al. (2023) | Basis for feature harmonization (NetFlow-v9, 4-feature common core) | **Reviewed & Verified** |
| **Dataset Shift & Covariate Shift Theory** | Moreno-Torres et al. (2012) | Mathematical framing of prior shift ($P(y)$) vs covariate shift ($P(x)$) | **Reviewed & Verified** |
| **Unsupervised Domain Adaptation (UDA)** | Sun & Saenko (2016), Ganin & Lempitsky (2015) | Core baseline adaptation algorithms (CORAL covariance alignment, DANN) | **Reviewed & Verified** |
| **High-Performance Tabular Classifiers** | Chen & Guestrin (2016), Ke et al. (2017), Gorishniy et al. (2021) | Production tree ensembles (XGBoost, LightGBM) and deep tabular FT-Transformer | **Reviewed & Verified** |
| **Model Interpretability & Feature Attribution** | Lundberg & Lee (2017) | TreeSHAP local and global attribution across source and target domains | **Reviewed & Verified** |
| **Few-Shot UDA & Class-Conditional Alignment** | Long et al. (2018), Tzeng et al. (2017) | Literature expansion identified during senior audit to justify class-aware CORAL | **Pending Verification** |
| **Industrial SCADA Security Benchmarks** | Shin et al. (HAI 2021), Electra (2023) | Benchmark grounding for IEC 60870-5-104 power grid telemetry | **Pending Verification** |
