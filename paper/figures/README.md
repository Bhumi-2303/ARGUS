# ARGUS Publication Figures (`paper/figures/`)

This directory houses all publication figures, system architecture diagrams, methodological illustrations, and empirical evaluation plots for the ARGUS academic research paper.

---

## Directory Organization

```text
paper/figures/
├── README.md                      # Directory guide and figure formatting guidelines
├── FIGURE_INDEX.md                # Master catalog with metadata, evidence tiers, and SHA-256 hashes
├── architecture/                  # Multi-agent platform architecture and frozen-test protocols
│   ├── fig01_argus_system_architecture.(svg/png)
│   └── fig02_evaluation_pipeline.(svg/png)
├── methodology/                   # Feature harmonization, resolution scaling, and CORAL alignment
│   ├── fig01_feature_harmonization.(svg/png)
│   └── fig02_coral_alignment_concept.(svg/png)
├── system_implementation/         # Live SOC monitoring console and telemetry inspection
│   └── fig01_live_monitoring_platform.(svg/png)
└── experimental_results/          # Complete empirical results figures (137 files across 10 sections)
    ├── 01_confusion_matrices/     # Confusion matrices across in-domain and cross-domain baselines
    ├── 02_roc_curves/             # ROC curves and operational threshold sweeps
    ├── 03_precision_recall_curves/# Precision-Recall curves and average precision benchmarks
    ├── 04_cross_domain_comparison/# Grouped bar charts, transfer heatmaps, and MCC trade-offs
    ├── 05_zero_shot_evaluation/   # SCADA zero-shot transfer vs native ceiling comparisons
    ├── 06_shap_explainability/    # TreeSHAP beeswarm summaries, waterfalls, and target disconnects
    ├── 07_latent_space_projections/# PCA projections and covariance alignment transformations
    ├── 08_ablation_studies/       # Feature ablation progressions and resolution scaling curves
    ├── 09_training_analysis/      # DANN loss curves, convergence diagnostics, and transformer depth
    ├── 10_publication_figures/    # Camera-ready multi-panel journal composite figures (FIGURE 1 - 8)
    ├── TOP_8_FOR_PROFESSOR/       # Standalone high-res PNG package for supervisory review
    └── FIGURE_INDEX.md            # Detailed sub-index for experimental results
```

---

## Figure Standards

1. **Evidence Classification Tiers**:
   - **Tier 1 (Empirical Evidence)**: Figures derived directly from reproducible frozen test set evaluations and quantitative benchmarks (`FIG-PUB-01` through `FIG-PUB-08`).
   - **Tier 2 (Synthetic / Aggregated Evidence)**: Probes and diagnostic representations synthesized across intermediate experimental runs.
   - **Tier 3 (Illustrative / Methodological Visuals)**: Conceptual architectural overviews, methodological flowcharts, protocol schematics, and UI/SOC interface previews (`FIG-ARCH-01`, `FIG-ARCH-02`, `FIG-METH-01`, `FIG-METH-02`, `FIG-SYS-01`).
2. **Dual Format Availability**: All conceptual and experimental figures are provided in high-resolution raster format (minimum 300 DPI PNG) for drafts and presentations, and camera-ready vector format (SVG/PDF) for journal typesetting.
3. **Empirical Integrity**: No experimental curve, confusion matrix, or attribution is synthetically smoothed or simulated. All plots strictly reflect underlying frozen test set inferences.
4. **Traceability**: Every experimental figure is mapped to its underlying experiment run and source metrics in [`paper/PUBLICATION_TRACEABILITY.md`](file:///home/bhumi/GitHub/ARGUS/paper/PUBLICATION_TRACEABILITY.md).
