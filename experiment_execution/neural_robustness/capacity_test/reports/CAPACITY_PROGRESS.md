# ARGUS Neural Capacity Stress Test Progress

## Experiment Audit & Status Summary

| Experiment | Status | Checkpoint | Predictions | Metrics | Figures | Training History |
|---|---|---|---|---|---|---|
| CAPACITY-01 | COMPLETE | COMPLETE (`best_model.pt`, 784 KB) | COMPLETE ($N=714,453$, 44.5 MB) | COMPLETE (`metrics/CAPACITY01_seed42.csv`) | COMPLETE (300 DPI, 6 Figures + CSVs) | COMPLETE (`training_logs/CAPACITY01_seed42_history.csv`) |

---

## Controlled Capacity Experiment Summary

- **Target Scientific Question**: Does substantially increasing FT-Transformer model capacity (from ~17,473 to ~200,705 parameters, an 11.5x increase) materially improve $D1 \rightarrow D3$ cross-domain transfer when features (ARGUS-4), data partitions, scaling, calibration, and evaluation procedures remain strictly identical?
- **Baseline Model (FTT-SMALL)**: `d_token=32, n_blocks=2, n_heads=4, d_ff=64, dropout=0.1` (17,473 params, Seed 42 ROC-AUC = 0.6075).
- **Target Model (FTT-LARGE)**: `d_token=64, n_blocks=4, n_heads=8, d_ff=256, dropout=0.1` (200,705 params, Seed 42 ROC-AUC = 0.5100).
- **Finding**: Increasing capacity by 11.5x degraded ROC-AUC from 0.6075 to 0.5100 (near random chance) and PR-AUC from 0.3595 to 0.1797, while leaving MCC near zero (0.0908).
- **Scientific Verdict**: **CASE A** — Increasing model capacity does not materially improve transfer performance, strongly reinforcing that cross-domain transfer degradation is driven by representation collapse and domain covariate shift rather than neural network capacity limitations.
