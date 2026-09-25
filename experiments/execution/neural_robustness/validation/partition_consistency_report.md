# Partition Consistency Audit Report

**Target Evaluation Domain**: IEC 60870-5-104 SCADA Telemetry (Domain 3 / D3)  
**Audit Date**: August 22, 2026

---

## 1. Frozen Data Partitions

All experiments (both historical LightGBM and new FT-Transformer neural robustness runs) use the exact frozen data partitions established in :

- **Source Domain D1 (CICIoT2023)**:
  - Train: ,491,971$ rows
  - Test: ,176,851$ rows
- **Source Domain D2 (NF-ToN-IoT-v2)**:
  - Train: ,508,704$ rows
  - Test: ,627,177$ rows
  - Adaptation sub-split: ,406,962$ rows
  - Calibration sub-split: ,101,742$ rows
- **Target Domain D3 (IEC 60870-5-104)**:
  - Train Total: ,857,812$ rows
  - Adaptation sub-split: ,286,249$ rows (\%$)
  - Calibration sub-split: ,563$ rows (\%$)
  - **Frozen Test Partition**: ** = 714,453$ rows** (Attack Prior $\pi_{target} = 22.47\%$)

---

## 2. Partition Rules Enforced for FT-Transformer Neural Runs

1. **Zero Data Leakage**: The  = 714,453$ D3 test set is strictly frozen and evaluated **exactly once** after model training/early stopping is completed.
2. **Model Selection**: Early stopping and learning rate scheduling use **validation/calibration partitions ONLY**.
3. **Scaler & Normalization Fitting**: StandardScaler/MinMaxScaler objects are fit strictly on training/adaptation data and applied to calibration and test data without re-fitting.
