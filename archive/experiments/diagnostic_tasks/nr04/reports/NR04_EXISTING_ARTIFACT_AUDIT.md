# ARGUS NR-04: Existing Native SCADA Artifact Audit Report

**Audit Date**: 2026-08-25 21:12:44  
**Target Domain**: IEC 60870-5-104 SCADA Telemetry ($D_3$, $N=714,453$)  
**Status**: **AUDIT PASSED (REUSABLE ARTIFACTS VERIFIED)**  

---

## 1. Frozen Test Partition Integrity
- **Target Path**: `data/IEC104/extracted_csvs/` & `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv`
- **Total Test Rows**: **714,453**
- **Attack Prior**: **22.466%** ($160,509$ attack flows / $553,944$ benign flows)
- **Leakage Isolation**: Complete. Test partition is strictly isolated from preprocessing, scaling, early stopping, hyperparameter selection, and threshold calibration.

---

## 2. Existing Baseline Inventory

| Artifact ID | Architecture | Features | Training Type | Test Rows | ROC-AUC | Average Precision | Status |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| `NR02_FTT_SMALL_Native` | FT-Transformer (Small) | 70 | In-Domain Ceiling | 714,453 | 0.6425 | 0.3666 | **PASS** |
| `EXP04_LightGBM_Native` | LightGBM GBDT | 70 | In-Domain Ceiling | 714,453 | 0.6744 | 0.4066 | **PASS** |
| `NR01_FTT_ARGUS4` | FT-Transformer (Small) | 4 | Cross-Domain Transfer | 714,453 | 0.6075 | 0.2978 | **PASS** |
| `EXP01_LightGBM_ARGUS4` | LightGBM GBDT | 4 | Cross-Domain Transfer | 714,453 | 0.6087 | 0.2989 | **PASS** |

---

## 3. Preprocessing Audit
- **Raw IEC 104 Flow Columns**: 84 total header columns.
- **Excluded Non-Feature Identifiers**: 14 columns (`Flow ID`, `Src IP`, `Dst IP`, `Timestamp`, `Label`, `Src Port`, `Dst Port`, `Protocol`, etc.).
- **Model Input Features**: **70 valid numeric features** (zero constant variance, fully imputable).
- **Transformation**: `StandardScaler` fitted strictly on training partition ($N=250,000$ stratified subsample).
