# ARGUS DA-01 Phase DA-01A: Environment & Artifact Verification Report
**Execution Timestamp**: 2026-08-23T22:38:06.062899
**Hardware Platform**: Apple M4 (16 GB Unified Memory)
**PyTorch Device**: mps
**PyTorch Version**: 2.13.0

---

## 1. Frozen Baseline (B0) Verification

- **Model Backbone**: FT-Transformer (Small)
- **Feature Dimension**: 4 features (ARGUS-4)
- **Parameter Count**: 17,473 parameters (EXACT MATCH: 17,473)
- **Hyperparameters**: `d_token=32, n_blocks=2, n_heads=4, d_ff=64, dropout=0.10`

### Baseline Checkpoints (B0)
- **Seed 42 Checkpoint**: `experiment_execution/neural_robustness/checkpoints/FTT_ARGUS4_D1_D3_seed42/best_model.pt` (78.8 KB, SHA256: `edbffaf39d5725717e40dfd7bb494613f12d35c4a4e6140418122bf5d8508b4b`)
- **Seed 123 Checkpoint**: `experiment_execution/neural_robustness/checkpoints/FTT_ARGUS4_D1_D3_seed123/best_model.pt` (78.8 KB, SHA256: `ddf5579a4ea8c3042541f68e4f47a06540d0f28044f3be26055154451eb8e3e2`)
- **Seed 456 Checkpoint**: `experiment_execution/neural_robustness/checkpoints/FTT_ARGUS4_D1_D3_seed456/best_model.pt` (78.8 KB, SHA256: `4a7c6f0b59880619da3a7759852c51fcb6b42bba4fad08c2e0eda1701e71fc31`)
- **Seed 789 Checkpoint**: `experiment_execution/neural_robustness/checkpoints/FTT_ARGUS4_D1_D3_seed789/best_model.pt` (78.8 KB, SHA256: `83933de0785739a0e44fb7dabecb246a95d0ec4c5181d240e24da7c3ec60a948`)
- **Seed 1011 Checkpoint**: `experiment_execution/neural_robustness/checkpoints/FTT_ARGUS4_D1_D3_seed1011/best_model.pt` (78.8 KB, SHA256: `9512fad3610e357e251d9cb10f9bf7566cf3bb4938dd10f94de07d0c420ce530`)

### Baseline Seed 42 Reference Metrics
| Metric | Reference Value | Baseline Artifact Value | Status |
|---|---|---|---|
| ROC-AUC | 0.6075 | 0.607487 | **VERIFIED** |
| Average Precision | 0.2978 | 0.297816 | **VERIFIED** |
| F1 (calibrated) | 0.3724 | 0.372434 | **VERIFIED** |
| MCC (calibrated) | 0.0652 | 0.065218 | **VERIFIED** |
| FPR (calibrated) | 96.68% | 96.68% | **VERIFIED** |

---

## 2. Dataset Partitions & Partition Discipline

| Dataset Partition | File Path | Expected Samples | Actual Samples | Column Integrity | Status |
|---|---|---|---|---|---|
| D1 Source Training | `ARGUS_Cross_Domain_Results/argus_coral_data/ciciot_train_features.csv` | 5,491,971 | 5,491,971 | `ARGUS-4 + label` | **VERIFIED** |
| D3 Unlabeled Adaptation | `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_train_adaptation.csv` | 2,286,249 | 2,286,249 | `ARGUS-4 + label` | **VERIFIED** |
| D3 Target Calibration | `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_train_calibration.csv` | 571,563 | 571,563 | `ARGUS-4 + label` | **VERIFIED** |
| D3 Frozen Target Test | `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv` | 714,453 | 714,453 | `ARGUS-4 + label` | **VERIFIED** |

### D3 Frozen Test Partition Statistics
- **Total Test Samples ($N$)**: 714,453
- **Attack Samples**: 160,509 (22.466%)
- **Benign Samples**: 553,944 (77.534%)
- **Partition Isolation Guard**: ACTIVE (Strictly blind; test labels forbidden during adaptation, training, and threshold selection)

---

## 3. Environment Check Final Verdict

**VERDICT: PASSED (ALL PREREQUISITES AND BASELINE ARTIFACTS FULLY AUDITED AND VERIFIED)**

Ready to proceed to Phase DA-01B: CORAL Covariance Statistics Calculation.
