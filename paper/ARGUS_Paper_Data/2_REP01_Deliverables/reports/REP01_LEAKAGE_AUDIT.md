# ARGUS REP-01: Strict Zero-Leakage Audit Checklist

**Audit Date**: August 26, 2026  
**Target Domain**: IEC 60870-5-104 ($D_3$)  
**Status**: **ALL 9 ITEMS VERIFIED — ZERO LEAKAGE (PASS)**  

---

| Item | Checklist Verification Point | Status | Evidence / Implementation |
| :---: | :--- | :---: | :--- |
| **1** | Test labels never used in training | **PASS** | Evaluated models trained strictly on training split ($N=250,000$ subsample). |
| **2** | Test labels never used in threshold calibration | **PASS** | Optimal threshold $\theta^*$ determined strictly on validation split ($N=57,156$). |
| **3** | Test statistics never used for scaling | **PASS** | `StandardScaler` fitted exclusively on training split. |
| **4** | Causal temporal features only (no future lookahead) | **PASS** | Rolling window packet/byte rates use strictly causal backward windows ($t-10 \dots t$). |
| **5** | Test samples never used for feature selection | **PASS** | Representation definitions derived a priori from SCADA protocol specifications. |
| **6** | Early stopping never used test performance | **PASS** | Monitored exclusively on validation loss. |
| **7** | No raw label proxies or shortcut features | **PASS** | Excluded all identifier columns (`Flow ID`, IP addresses, ports, sequence IDs). |
| **8** | SHAP analysis performed after freezing model | **PASS** | Gradient attributions computed post-training on a frozen evaluation checkpoint. |
| **9** | Final test evaluated once after model freezing | **PASS** | Held-out test set evaluated exactly once without post-hoc tuning. |
