# ARGUS Results Directory (`results/`)

This directory is the authoritative repository of scientific results, empirical metrics, statistical audit deliverables, and publication artifacts for ARGUS.

---

## 1. Directory Structure

```text
results/
├── ARGUS_ALL_RESEARCH_RESULTS.xlsx # Authoritative Master Research Workbook (17 sheets)
├── experiments/                    # Modern research phase deliverables (P1–P2.3)
│   ├── p1_1_nfton_in_domain/       # Supervised NF-ToN reference baseline
│   ├── p2_coordinate_generalization/# Coordinate overlap, label ambiguity & disjoint splits
│   ├── p2_1_validation/            # Same-test-set cross-domain validation & DeLong tests
│   ├── p2_2_robustness/            # 5 independent coordinate splits & cluster bootstrap
│   └── p2_3_reconciliation/        # Adversarial reconciliation & partition identity audit
├── verified/                       # Authoritative production benchmark tables (SHA-verified)
│   ├── five_model_complete_comparison.csv # Authoritative 5-model comparison
│   ├── dann_final_test_metrics.csv        # DANN final test set performance
│   ├── d3_native_threshold_sweep.csv      # D3 native 99-step threshold curve
│   ├── SHAP_vs_Target_Gain.csv            # Feature attribution vs target gain
│   └── domain_statistics.json             # Dataset flow counts and priors
├── verification/                   # Prediction NPZ archives (8 evaluation models)
│   └── predictions/                # Raw arrays (A/B/C/D baselines, CORAL, DANN)
├── diagnostic/                     # Diagnostic evaluation outputs
│   └── diagnostic_class_aware_coral.csv
├── ARGUS_POSTER_DATA_PACKAGE/      # IEEE/conference poster data package
│   ├── figures/                    # Confusion matrices and ROC curves
│   ├── graphs/                     # Metric CSVs (F1, MCC, FPR, runtime)
│   └── POSTER_RESULTS_SUMMARY.md   # Executive poster summary
├── poster_figures/                 # Publication confusion matrix CSVs
└── poster_graph_data/              # Publication metric series CSVs
```

---

## 2. Research Phase Mapping & Provenance

| Research Phase | Directory | Key Deliverables | Reproducibility Manifest |
| :--- | :--- | :--- | :--- |
| **P1-1 In-Domain Baseline** | [`results/experiments/p1_1_nfton_in_domain/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p1_1_nfton_in_domain/) | `nfton_in_domain_metrics.csv`, `xgboost_test_predictions.parquet`, `lightgbm_test_predictions.parquet`, 6 figures | `training_metadata.json` |
| **P2 Coordinate Generalization** | [`results/experiments/p2_coordinate_generalization/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_coordinate_generalization/) | `coordinate_disjoint_metrics.csv`, `coordinate_disjoint_predictions.parquet`, `bayes_ceiling_summary.json`, 8 figures | `p2_reproducibility_manifest.json` |
| **P2.1 Same-Test Validation** | [`results/experiments/p2_1_validation/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_1_validation/) | `P2_1_SAME_TEST_CROSS_DOMAIN_COMPARISON.csv`, `P2_1_CORAL_MCC_RECONCILIATION.json`, `P2_1_STATISTICAL_VALIDATION.json` | `P2_1_REPRODUCIBILITY_MANIFEST.json` |
| **P2.2 Robustness & Uncertainty**| [`results/experiments/p2_2_robustness/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_2_robustness/) | `P2_2_INDEPENDENT_SPLIT_METRICS.csv`, `P2_2_CLUSTER_BOOTSTRAP_RESULTS.json`, `P2_2_PAIRED_MODEL_COMPARISONS.json` | `P2_2_REPRODUCIBILITY_MANIFEST.json` |
| **P2.3 Adversarial Reconciliation**| [`results/experiments/p2_3_reconciliation/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/) | `P2_3_PARTITION_IDENTITY.json`, `P2_3_PREDICTION_ARTIFACT_RECONCILIATION.csv`, `P2_3_METRIC_RECOMPUTATION.csv` | `P2_3_REPRODUCIBILITY_MANIFEST.json` |

---

## 3. Master Research Workbook

The master research spreadsheet is located at:
[`results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`](file:///home/bhumi/GitHub/ARGUS/results/ARGUS_ALL_RESEARCH_RESULTS.xlsx)
- **File Size**: 75,463 bytes
- **SHA-256**: `f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1`
- **Total Worksheets**: 17 sheets
  1. `Executive_Summary`
  2. `Verified_Primary_Benchmark`
  3. `Master_Experiment_Execution`
  4. `Table1_Dataset_Profiles`
  5. `Table2_Primary_Benchmark`
  6. `Table3_Harmonized_vs_Native`
  7. `Table4_Feature_Scaling`
  8. `Table5_Operational_Perf`
  9. `MultiSeed_Statistical_Analysis`
  10. `Representation_Ablation_REP01`
  11. `D3_Native_Threshold_Sweep`
  12. `Phase4_Experiment_Suite`
  13. `Phase4_Calibration_&_Fusion`
  14. `Phase3_Domain_Shift_&_Ablation`
  15. `Explainability_&_SHAP_Audit`
  16. `MultiAgent_System_Metrics`
  17. `Research_Audit_&_Integrity`

---

## 4. Scientific Status Classification

1. **Verified Primary Benchmark Results**:
   - `results/verified/five_model_complete_comparison.csv`: Verified on the 2,627,177 NF-ToN test set.
   - `results/experiments/p2_3_reconciliation/`: Authoritative reconciliation resolving sample ordering and threshold alignment.
2. **Cluster-Bootstrap Uncertainty**:
   - `results/experiments/p2_2_robustness/P2_2_CLUSTER_BOOTSTRAP_RESULTS.json`: 1,000 resamples accounting for intra-cluster coordinate correlation.
3. **Exploratory & Negative Controls**:
   - `results/diagnostic/diagnostic_class_aware_coral.csv`: Highlights degradation modes under uncalibrated operational thresholds.
