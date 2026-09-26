# CAPACITY-01 Historical Evidence Freeze Manifest

**Freeze Timestamp**: August 22, 2026  
**Status**: **FROZEN & IMMUTABLE BASELINE EVIDENCE**

---

## 1. Frozen Model Specifications

- **Experiment ID**: `CAPACITY-01`
- **Model Architecture**: FT-Transformer Large (FTT-LARGE)
- **Hyperparameters**: `d_token=64, n_blocks=4, n_heads=8, d_ff=256, dropout=0.10`
- **Trainable Parameters**: `200,705` parameters
- **Random Seed**: `42`
- **Source Dataset**: D1 (CICIoT2023 Train, $N=5,491,971$, subsampled $500,000$ stratified)
- **Target Calibration Dataset**: D3 (IEC 60870-5-104 Calibration split, $N=571,563$, val sub-split $50,000$)
- **Target Test Dataset**: Frozen D3 Test Partition ($N=714,453$ records, $\pi_{target} = 22.47\%$)
- **Feature Set**: ARGUS-4 Harmonized (`["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]`)
- **Scaling**: `StandardScaler` fit on D1 training data

---

## 2. Frozen Verified Performance Metrics

- **ROC-AUC**: **$0.509999$**
- **PR-AUC**: **$0.179683$**
- **Default Threshold ($\Theta = 0.50$)**:
  - $\text{F1} = 0.372434$, $\text{MCC} = 0.065218$, $\text{FPR} = 96.68\%$, $\text{FNR} = 0.77\%$, $\text{Accuracy} = 24.87\%$
- **Calibrated Threshold ($\Theta = 0.9900$, derived from target calibration partition)**:
  - $\text{F1} = 0.380274$, $\text{MCC} = 0.090759$, $\text{FPR} = 77.21\%$, $\text{FNR} = 13.96\%$, $\text{Accuracy} = 37.00\%$

---

## 3. Preserved Historical Evidence Files

- `configs/CAPACITY01_config.json`
- `checkpoints/CAPACITY01_seed42/best_model.pt`
- `training_logs/CAPACITY01_seed42_history.csv`
- `predictions/CAPACITY01_seed42_predictions.csv`
- `metrics/CAPACITY01_seed42.csv`
- `metrics/CAPACITY01_SMALL_vs_LARGE.csv`
- `figures/CAPACITY01_SMALL_vs_LARGE.png`
- `reports/CAPACITY01_interpretation.md`
- `validation/CAPACITY01_recomputed_metrics.csv`
- `reports/CAPACITY01_ARTIFACT_AUDIT.md`

All files listed above are historical evidence and must NOT be altered or overwritten.
