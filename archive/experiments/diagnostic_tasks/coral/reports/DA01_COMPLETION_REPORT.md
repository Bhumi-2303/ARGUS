# ARGUS DA-01: Final Experiment Completion Report

**Experiment**: `DA-01` (FTT-SMALL + CORAL Representation Alignment Test)  
**Completion Date**: August 23, 2026  
**Status**: **EXPERIMENT COMPLETED — PUBLICATION READY**  
**Execution Environment**: Apple M4 (16 GB Unified Memory), PyTorch MPS  

---

## 1. Executive Summary

Experiment `DA-01` executed a strictly controlled, memory-safe, reproducible domain adaptation test on the existing **FTT-SMALL** neural architecture (17,473 parameters) applying **Correlation Alignment (CORAL)** to align source (D1 CICIoT2023) covariance to target (D3 IEC 60870-5-104) covariance.

### Key Findings:
1. **Mathematical Alignment Success**: Second-order covariance discrepancy was reduced by **99.9959%** (||C_s - C_t||_F: 2.6009 -> 0.0001).
2. **Downstream Transfer Failure (Negative Result)**: Downstream cross-domain target ranking degraded from **ROC-AUC = 0.6075** (B0 baseline) to **ROC-AUC = 0.4441** (B1 CORAL) on Seed 42, with 5-seed mean ROC-AUC of **0.4497 ± 0.0176** (p = 0.0028).
3. **Operational SOC Stagnation**: At calibrated threshold θ* = 0.57, the false positive rate remained unacceptable at **96.68%**, and at operational budget FPR ≤ 1.0%, attack recall was **0.00%**.
4. **Scientific Value**: Unambiguously proves that second-order covariance alignment alone is mathematically insufficient to resolve cross-domain transfer failure under the 4-feature ARGUS representation.

---

## 2. Experimental Artifact Summary

All artifacts have been verified, checksummed, and saved under:
`experiment_execution/neural_robustness/domain_adaptation/`

- **Checkpoints**: 5 PyTorch models (`DA01_FTT_CORAL_seed{42,123,456,789,1011}/best_model.pt`)
- **Predictions**: 5 CSV files of 714,453 rows each (`predictions/DA01_seed*.csv`)
- **Statistics**: 4 CSV tables + 1 NPZ file (`statistics/`)
- **Tables**: 4 comprehensive comparison and operational CSV tables (`tables/`)
- **Figures**: 7 publication-quality 300 DPI figures + 4 underlying curve CSVs (`figures/`)
- **Reports**: Environment check, interpretation, claim evidence matrix, and file manifest (`reports/`)

---

## 3. Paper-Safe Conclusion

> *"In the controlled evaluation of Correlation Alignment (DA-01), second-order source-to-target covariance alignment reduced feature covariance discrepancy by 99.9959%, yet resulted in significant cross-domain ranking degradation (mean ROC-AUC decreased from 0.5543 to 0.4497, p=0.0028). Under operational SOC false-alarm budgets (FPR ≤ 1.0%), attack detection remained at 0.00%. These findings demonstrate that linear covariance alignment is fundamentally insufficient to resolve cross-domain covariate shift under the 4-feature compact representation."*

---

## 4. Next Recommended Experiment

- **Stage 3B (DA-02: DANN Adversarial Adaptation)**: Test non-linear adversarial domain adaptation via gradient reversal to explore if higher-order non-linear domain invariance can be learned.
- **Stage 4 (Native Feature Study)**: Investigate protocol-specific SCADA telemetry recovery.
