# ARGUS DA-01: Paper Claim Evidence Matrix

| Claim ID | Paper Claim Description | Evidence Artifact | Empirical Values | Status | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DA-C1** | CORAL reduces source-target covariance discrepancy. | `statistics/DA01_coral_alignment_statistics.csv`, `figures/DA01_covariance_distance.png` | ||C_s - C_t||_F reduced from 2.6009 to 0.0001 (99.9959% reduction). | **GREEN** | **FULLY SUPPORTED** |
| **DA-C2** | CORAL does not improve neural cross-domain ranking (D1 -> D3). | `tables/DA01_FTT_BASELINE_vs_CORAL.csv`, `figures/DA01_ROC_comparison.png` | Mean ROC-AUC dropped from 0.5543 to 0.4497 (p=0.0028); Mean AP dropped from 0.2576 to 0.2264 (p=0.0416). | **GREEN** | **FULLY SUPPORTED (NEGATIVE RESULT)** |
| **DA-C3** | CORAL does not improve operational SOC performance under low-FPR constraints. | `tables/DA01_operating_points.csv`, `figures/DA01_FPR_vs_recall.png` | At FPR ≤ 1.0%, attack recall is 0.00% (Precision=0.0%, F1=0.0%, MCC=0.0%). Calibrated FPR is 96.68%. | **GREEN** | **FULLY SUPPORTED (NEGATIVE RESULT)** |
| **DA-C4** | Covariance alignment alone cannot overcome the ARGUS-4 representation bottleneck. | `reports/DA01_interpretation.md`, `tables/DA01_MULTI_SEED_RESULTS.csv` | Multi-seed stability (σ=0.0176) confirms systematic structural failure of linear 2nd-order alignment. | **GREEN** | **FULLY SUPPORTED** |

---

### Audit Criteria Definition:
- **GREEN**: Fully substantiated by audited empirical data and reproducible artifacts.
- **YELLOW**: Partially substantiated, subject to boundary conditions or sample variance.
- **RED**: Unsubstantiated, contradicted by empirical findings, or invalid methodology.
