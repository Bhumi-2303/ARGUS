# ARGUS NR-03: Stage 1 Existing Artifact Audit Report

**Audit Date**: 2026-08-25 11:08:50  
**Target Domain**: IEC 60870-5-104 SCADA Telemetry ($D_3$, $N=714,453$)  
**Status**: **AUDIT PASSED (REUSABLE ARTIFACTS VERIFIED)**  

---

## 1. Frozen Test Partition Integrity
- **Path**: `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv`
- **Total Test Rows**: **714,453**
- **Test Set Isolation**: Guaranteed. Test partition is completely isolated from feature selection, scaling parameter estimation, early stopping, and threshold selection.

---

## 2. Existing Baseline Artifact Inventory

| Artifact ID | Model Family | Features | Training Type | Test Rows | ROC-AUC | Average Precision ($AP$) | Status |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| `NR01_ARGUS4_Transfer` | FT-Transformer | 4 | Cross-Domain Transfer ($D_1 \to D_3$) | 714,453 | 0.6075 | 0.2978 | **PASS** |
| `NR02_Native_InDomain` | FT-Transformer | 70 | In-Domain Target Ceiling ($D_3 \to D_3$) | 714,453 | 0.6425 | 0.3666 | **PASS** |
| `EXP01_ARGUS4_GBDT` | LightGBM | 4 | Cross-Domain Transfer ($D_1 \to D_3$) | 714,453 | 0.6087 | 0.2989 | **PASS** |
| `EXP04_Native_GBDT` | LightGBM | 70 | In-Domain Target Ceiling ($D_3 \to D_3$) | 714,453 | 0.6744 | 0.4066 | **PASS** |

---

## 3. Native Feature Dimensionality Verification
- **Raw IEC 104 Column Count**: 73 features listed in specification/config.
- **Model Input Dimension**: **70 features** (filtered out constant columns, timestamp strings, and IP identifiers).
- **Control Consistency**: The FT-Transformer tokenizer automatically maps each of the 70 numeric inputs to embedding tokens ($d_{\text{token}}=32$) before feeding into the identical 2-block transformer backbone.
