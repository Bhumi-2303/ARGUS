# ARGUS NR-04: Strict Zero-Leakage Audit Checklist

**Audit Date**: August 25, 2026  
**Target Test Set**: `iec104_test_features.csv` ($N = 714,453$)  
**Status**: **ALL 9 ITEMS VERIFIED — ZERO LEAKAGE (PASS)**  

---

| Item | Checklist Verification Point | Status | Evidence / Implementation |
| :---: | :--- | :---: | :--- |
| **1** | Test labels never used in training | **PASS** | Model trained strictly on $D_3$ training split ($N=250,000$ subsample). |
| **2** | Test labels never used in threshold calibration | **PASS** | Optimal threshold $\theta^*$ determined strictly on $D_3$ calibration split ($N=571,563$). |
| **3** | Test statistics never used for scaling | **PASS** | `StandardScaler` mean and std fitted exclusively on training split. |
| **4** | Test samples never used for feature selection | **PASS** | 70 features selected based on numeric/variance criteria on training data. |
| **5** | Test performance never used for model selection | **PASS** | Best architecture (FTT-LARGE) chosen strictly via validation ROC-AUC / AP. |
| **6** | Early stopping never used test performance | **PASS** | Validation loss monitored on validation subset ($N=50,000$). |
| **7** | Class weights derived only from training data | **PASS** | Positive weighting calculated exclusively from training label proportions. |
| **8** | SHAP analysis performed after model freezing | **PASS** | Attribution computed post-training on a frozen evaluation checkpoint. |
| **9** | Final test evaluated only after model selection | **PASS** | Test set evaluated exactly once after freezing all model weights. |
