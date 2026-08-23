# ARGUS Data Leakage & Contamination Audit

**Audit Timestamp**: 2026-08-23T08:15:13.725932+00:00

## 1. Leakage Assessment Protocol

This audit systematically examines the pipeline code (`run_ablation_experiments.py`, `validate_metrics.py`, and preprocessing scripts) to verify that the frozen $D_3$ test partition (`iec104_test_features.csv`, $N=714,453$) remained strictly unobserved during all training, tuning, scaling, and calibration phases.

## 2. Leakage Test Matrix

| Risk Dimension | Audit Test Description | Audit Finding | Verdict |
|---|---|---|:---:|
| **1. Test Labels in Calibration** | Inspect threshold calibration dataset | Threshold selection exclusively evaluated on `iec104_train_calibration.csv` ($N=580,248$, subsampled $N=50,000$). No test labels entered threshold search. | **PASS** |
| **2. Test Probabilities in Threshold Selection** | Verify grid search optimization target | The grid search $\tau \in [0.01, 0.99]$ maximized $F_1$ strictly on `val_probs` from calibration partition. Test probabilities were evaluated only *post hoc*. | **PASS** |
| **3. Test Predictions in Model Parameters** | Inspect backpropagation & loss | Loss gradients computed strictly on source training batch ($D_1$ CICIoT2023). Target test samples never passed to optimizer. | **PASS** |
| **4. Test Statistics in Preprocessing** | Inspect feature scalers (`StandardScaler`) | `StandardScaler.fit()` was called exclusively on source training subsample (`X_tr_sub`). Test set features were normalized via `.transform()` only. | **PASS** |
| **5. Test Data in Feature Scaling** | Check for global feature statistics leakage | Zero feature statistics (mean, variance, min, max) from $D_3$ test were computed or exposed during training. | **PASS** |
| **6. Test Data in Early Stopping** | Verify validation loss tracking | Early stopping monitored validation loss on $D_3$ calibration split (`val_loss_sum / val_count`). Test partition was never evaluated during training epochs. | **PASS** |
| **7. Test Data in Model Selection** | Verify checkpoint selection rule | Best checkpoint saved based on minimum calibration loss. Test set remained isolated until final evaluation inference. | **PASS** |

## 3. Leakage Audit Summary

> [!IMPORTANT]
> **LEAKAGE VERDICT: PASSED (GREEN)**
>
> Zero instances of data leakage or test contamination were detected across all 7 evaluation dimensions. The frozen $D_3$ test set remained an unadulterated blind benchmark throughout the entire experimental lifecycle.
