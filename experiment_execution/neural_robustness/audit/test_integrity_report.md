# ARGUS Test Set & Data Integrity Audit Report

**Audit Timestamp**: 2026-08-23T08:14:48.678017+00:00

## 1. Frozen Ground Truth Partition Verification

- **File**: `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv`
- **Total Rows ($N$)**: `714,453` (Exact requirement: `714,453`)
- **Positive Class (Attacks)**: `160,509`
- **Negative Class (Benign)**: `553,944`
- **Ground Truth Attack Prior ($\pi_{target}$)**: `0.224660` (`22.4660%`)

## 2. Condition-by-Condition Integrity Matrix

| Condition | Total Rows | Label Alignment | Duplicate Sequence Indices | NaNs / Infs | Prob Range | Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **A0_BASELINE** | `714,453` | `PASS (100% Match)` | `0` | `0 / 0` | `[0.6614, 0.9623]` | **`PASS`** |
| **A1_LABEL_SMOOTHING** | `714,453` | `PASS (100% Match)` | `0` | `0 / 0` | `[0.3671, 0.9680]` | **`PASS`** |
| **A2_FEATURE_MASKING** | `714,453` | `PASS (100% Match)` | `0` | `0 / 0` | `[0.3149, 0.9727]` | **`PASS`** |
| **A3_COMBINED** | `714,453` | `PASS (100% Match)` | `0` | `0 / 0` | `[0.3244, 0.9681]` | **`PASS`** |

## 3. Structural Integrity Verdict

> [!IMPORTANT]
> **VERDICT: PASSED (GREEN)**
>
> All four condition prediction files contain exactly 714,453 predictions in strict 1-to-1 sequence correspondence with the frozen D3 test partition, zero duplicates, zero NaNs or Infs, bounded probabilities in [0, 1], and 100% exact sample-for-sample label alignment.
