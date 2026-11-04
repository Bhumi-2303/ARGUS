# ARGUS Methodology Documentation (`paper/methodology/`)

This directory houses the comprehensive mathematical formulations, feature definitions, dataset descriptions, and evaluation protocols supporting the ARGUS research paper.

---

## Methodology Module Index

```text
paper/methodology/
├── README.md                                  # Directory guide and module roadmap
├── 01_DATASETS_AND_PREPROCESSING.md           # Dataset environments, flow counts, priors, and splits
├── 02_FEATURE_HARMONIZATION.md                # Feature synthesis: ARGUS-4, 6, 8, and native 70 schemas
├── 03_DOMAIN_ADAPTATION_FORMULATION.md        # Mathematical definitions of CORAL, Class-Aware, Prior Shift, DANN
└── 04_EVALUATION_PROTOCOLS_AND_METRICS.md     # Fixed FPR budgets, MCC, cluster bootstrap, and SHAP protocols
```

---

## Core Scientific Principles

1. **Mathematical Rigor**: All algorithms (Global CORAL, Class-Aware CORAL, Prior Correction, DANN) are formalized with explicit matrix operations, loss functions, and probability transformations.
2. **Leakage Control**: Test sets are strictly frozen and evaluated blind. No target test labels are used for model training, feature alignment, or threshold selection in any reported finding.
3. **Operational Grounding**: Performance is evaluated under realistic SOC operational constraints rather than isolated aggregate F1 metrics.
