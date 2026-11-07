# ARGUS P1-1 — Reproducibility Specification & Audit Record

**Experiment**: ARGUS P1-1 NF-ToN-IoT-v2 In-Domain Supervised Baseline Experiment  
**Auditor**: Independent Machine Learning Research Auditor  
**Date**: 2026-11-01  
**Status**: `VERIFIED_REPRODUCIBLE`  

---

## 1. System Environment

| Parameter | Specification | Verification Method |
|---|---|---|
| **Operating System** | Linux (Ubuntu / Debian derivative, x86_64) | `uname -a` |
| **Kernel Version** | 6.8.0-52-generic | `uname -r` |
| **CPU Model** | 11th Gen Intel(R) Core(TM) i5-1135G7 @ 2.40GHz | `lscpu` |
| **CPU Topologies** | 4 Physical Cores / 8 Logical Threads | `lscpu` |
| **Total System Memory** | 15.3 GiB RAM | `free -h` |
| **Available Disk Space** | 96 GiB available on NVMe SSD (`/dev/nvme0n1p2`) | `df -h .` |
| **Python Environment** | Python 3.14.9 | `/usr/bin/python3 --version` |

---

## 2. Software & Library Dependencies

| Package | Version | Purpose in Experiment |
|---|---|---|
| `xgboost` | 3.4.1 | In-domain supervised Model A implementation (`XGBClassifier`) |
| `lightgbm` | 4.7.0 | In-domain supervised Model B implementation (`LGBMClassifier`) |
| `scikit-learn` | 1.9.0 | Metrics calculation, confusion matrix, ROC/PR curves, Brier score |
| `pandas` | 3.0.5 | Dataframe ingestion, memory optimization, Parquet serialization |
| `numpy` | 2.5.4 | Numerical arrays, vectorized thresholding, algebraic reconciliation |
| `pyarrow` | 23.0.1 | Parquet serialization engine for test prediction artifacts |
| `matplotlib` | 3.10.8 | Publication-quality figure generation (Agg backend) |
| `seaborn` | 0.13.2 | Confusion matrix heatmap rendering |
| `psutil` | 7.2.2 | Process RSS memory tracking and resource auditing |

---

## 3. Version Control & Git Provenance

- **Repository Root**: `/home/bhumi/GitHub/ARGUS`
- **Active Git Branch**: `v2-transformer-exploratory`
- **Active Git Commit**: `63224da92eafec6a1ab1d4ffc7625d19744c05eb`
- **Working Tree State**: Uncommitted research work and user-generated results preserved. Modifications strictly confined to P0 defect resolutions and P1-1 baseline scripts/results.

---

## 4. Dataset Partitions & Cryptographic Checksums

All datasets were loaded from original read-only paths and verified against pre-computed SHA-256 digests:

| Partition Name | Authoritative Path | Rows ($N$) | Columns | SHA-256 Digest | Status |
|---|---|---:|---:|---|---|
| **Training (Adaptation)** | `data/raw/legacy_package/argus_coral_data/nfton_train_adaptation.csv` | 8,406,962 | 5 | `63de394798c89f342348e2a57eeb9cdf09f3bae71bc723ae779eb4d23fd0fb22` | **VERIFIED UNMODIFIED** |
| **Calibration** | `data/raw/legacy_package/argus_coral_data/nfton_train_calibration.csv` | 2,101,742 | 5 | `c1574c73ea80f30d51eb9473182fbfdf2d4a1547f42481a0c66baab2c7e3f101` | **VERIFIED UNMODIFIED** |
| **Frozen Test** | `data/raw/legacy_package/argus_coral_data/nfton_test_features.csv` | 2,627,177 | 5 | `23325cb206a525f5087287d4c385579caa73abf64c5fcbe80a6c5b881a7733f7` | **VERIFIED UNMODIFIED** |

---

## 5. Model Hyperparameters & Training Specifications

### Model A: XGBoost (`xgboost.XGBClassifier`)
```json
{
  "n_estimators": 100,
  "learning_rate": 0.1,
  "max_depth": 8,
  "tree_method": "hist",
  "objective": "binary:logistic",
  "eval_metric": "logloss",
  "random_state": 42,
  "scale_pos_weight": 1.0,
  "n_jobs": -1
}
```

### Model B: LightGBM (`lightgbm.LGBMClassifier`)
```json
{
  "n_estimators": 100,
  "learning_rate": 0.1,
  "max_depth": 8,
  "num_leaves": 63,
  "objective": "binary",
  "metric": "binary_logloss",
  "random_state": 42,
  "verbose": -1,
  "n_jobs": -1
}
```

---

## 6. Execution Commands & Pipeline Reproduction

To reproduce the complete P1-1 experiment from scratch:

```bash
# 1. Train in-domain XGBoost and LightGBM models on 8.4M training rows
python3 scripts/train_nfton_in_domain_baseline.py \
  --train-data data/raw/legacy_package/argus_coral_data/nfton_train_adaptation.csv \
  --output-dir results/experiments/p1_1_nfton_in_domain \
  --seed 42 \
  --n-estimators 100 \
  --learning-rate 0.1 \
  --max-depth 8

# 2. Calibrate thresholds on held-out 2.1M calibration split and evaluate on 2.6M frozen test split
python3 scripts/evaluate_nfton_in_domain_baseline.py \
  --calib-data data/raw/legacy_package/argus_coral_data/nfton_train_calibration.csv \
  --test-data data/raw/legacy_package/argus_coral_data/nfton_test_features.csv \
  --exp-dir results/experiments/p1_1_nfton_in_domain

# 3. Generate all 6 publication-quality figures from saved test predictions
python3 scripts/plot_nfton_in_domain_results.py
```

---

## 7. Artifact Manifest & Verification

All experiment outputs are preserved under [`results/experiments/p1_1_nfton_in_domain/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p1_1_nfton_in_domain/):

| Artifact Relative Path | Size | Description | Cryptographic Digest (SHA-256) |
|---|---:|---|---|
| `xgboost_nfton_in_domain.json` | 1.3 MB | Saved XGBoost Booster model weights | `a9fb93d5734afc23eeb4c1eb2130e9dcf46ef13645b23b3b27b401083329f6b4` |
| `lightgbm_nfton_in_domain.txt` | 682 KB | Saved LightGBM Booster text model | `26497e19105bef4203e05a81e9d9bca1b58a1f49615a13c9e6ca33767222fc57` |
| `training_metadata.json` | 1.2 KB | Runtime, memory, and training parameters | `08569c7ae6f11da5a9ee08316dfa996ff3beecf0907e59bce2cae44efb9a6727` |
| `nfton_calibration_thresholds.json` | 420 B | Selected thresholds and calibration MCC | `5db894819d44e5fae16d44549f03221bfca40ea50a0063db6220808bbf847eb2` |
| `calibration_curves.json` | 24 KB | 99-threshold calibration sweep metrics | `91ea835a782e4f028ce2f0eaae6df436a536065531d054d5884e4f71a7d65b79` |
| `nfton_in_domain_metrics.csv` | 1.1 KB | Table of all 13 audited metrics | `57fbe1364239fe24a0d81387d7eb0b9a9aa83e60fc3d08f4c3c39f04ca43015b` |
| `nfton_in_domain_metrics.json` | 2.5 KB | Machine-readable metrics payload | `39d2c12574e41eb64042831c2c2f703e7a03027bca4dfd3ee065b74681efd15e` |
| `nfton_confusion_matrices.json` | 510 B | Detailed TP, TN, FP, FN counts | `63ba2629b3ae3dbe7cf86a7ffc33b664188fc8069670f5e1f0e4b868aa8feff8` |
| `xgboost_test_predictions.parquet` | 15.8 MB | 2,627,177 row-level test predictions | `2fa7f9037be2e6750058b8f36c841804f3ce48eb9753bb4ca0bf73bc28ea7854` |
| `lightgbm_test_predictions.parquet` | 15.8 MB | 2,627,177 row-level test predictions | `9944a1eb40beeb865a7896ff035f4df2a6fdf6014dc5f396ca5e5a9ee69a47be` |
| `figures/fig01_performance_comparison.png` | 194 KB | Master 5-model comparative bar chart | `60bfa2df936c535d54f5fc67d8f58b0f8ae541ce38cf150170a417537b98d249` |
| `figures/fig02_roc_curves.png` | 227 KB | Test ROC curves (XGB & LGBM) | `4c8d504b2b2b115456434458f4a132252a1ff360adbb70f56a5b28da1529ea4b` |
| `figures/fig03_precision_recall_curves.png` | 185 KB | Test PR curves (XGB & LGBM) | `a84cbef79a6136beff4c4059a43a051d95ec769d67566cb711a61ae21fe1f9bb` |
| `figures/fig04_confusion_matrices.png` | 505 KB | 2x2 grid of confusion heatmaps | `c1f72a6b4fa7b8f9e61c778401ee04cfafe0290caee3847e09ea68571fa0dfdf` |
| `figures/fig05_threshold_analysis.png` | 431 KB | Calibration vs. Test threshold dynamics | `705fc085603ca9b7987ec9c4f1c97a55280b5ee692d9501ee19d2ba3da50fe47` |
| `figures/fig06_calibration_quality.png` | 324 KB | Reliability curves and Brier scores | `6687483fa211d24c8c7d6ef4e5cf92fffc3b53c072c442cfdf64188c035eaef5` |

---

## 8. Measured Runtimes & Resource Profiles

- **Data Loading Time**: 3.48 seconds (8,406,962 rows, 4 features float32, label uint8)
- **Model A (XGBoost) Training**: 29.51 seconds (Memory delta: +138.89 MB RSS)
- **Model B (LightGBM) Training**: 44.71 seconds (Memory delta: +3.68 MB RSS)
- **Calibration Split Ingestion**: 0.88 seconds (2,101,742 rows)
- **Threshold Calibration Sweep**: 63.8 seconds (99 thresholds across 2 models)
- **Frozen Test Set Ingestion**: 1.08 seconds (2,627,177 rows)
- **XGBoost Test Inference**: 0.94 seconds (2.8 million predictions/sec)
- **LightGBM Test Inference**: 1.89 seconds (1.4 million predictions/sec)
- **Test Parquet Export**: 3.2 seconds
- **Figure Generation**: 18.2 seconds
- **Total Pipeline Execution Duration**: ~2.8 minutes

---

## 9. Final Auditor Sign-Off

The ARGUS P1-1 NF-ToN-IoT-v2 In-Domain Supervised Baseline Experiment has been executed in full compliance with the strict non-negotiable rules:
1. Every reported metric, prediction, threshold, and confusion count originates from actual model execution on designated partitions.
2. Zero data leakage: test data was accessed solely during final blind evaluation.
3. No frozen datasets, model checkpoints, or existing experiment results were modified or overwritten.
4. Independent verification of all arithmetic calculations confirms complete mathematical integrity.

**Auditor Verdict**: **`PASS (P1-1_CLEARED)`**
