# ARGUS Pre-Experiment Pipeline Inventory & Hash Manifest

**Audit Date**: August 22, 2026  
**Status**: Frozen Baseline Inventory Verified ( = 81$ Files)

---

## 1. Baseline Pipeline Overview

This manifest records the immutable state of all historical LightGBM experiments, tables, figures, predictions, and reports in  prior to launching the FT-Transformer neural robustness experiment.

- **Total Existing Artifacts**: 81 files
- **Primary Model Family**: LightGBM GBDT (, , , )
- **Random Seeds Evaluated**:  (5 seeds)
- **Target Evaluation Partition**: IEC 60870-5-104 Test Set ( = 714,453$ records, Attack Prior $\pi_{target} pprox 22.47\%$)

---

## 2. Representation & Model Inventory

### 2.1 Evaluated Feature Representations
1. **ARGUS-4 (Harmonized 4-Feature Set)**:
   - : Mean to max packet size ratio
   - : TCP flag multiplicity sum
   - : 
   - : 
2. **Native SCADA (Native-73 Representation)**:
   - 73 raw/engineered flow statistics extracted from target IEC 60870-5-104 telemetry (, , , etc.).

### 2.2 Existing LightGBM Checkpoints & Master Outputs
-  (87 benchmark result rows)
- 
-  ( = 714,453$)
-  ( = 714,453$)
-  ( = 714,453$)
-  ( = 714,453$)
-  ( = 714,453$)

---

## 3. Cryptographic Verification Manifest
All 81 pre-experiment files have been hashed using SHA-256 and recorded in . Any mutation of historical evidence will be flagged immediately by checksum verification.
