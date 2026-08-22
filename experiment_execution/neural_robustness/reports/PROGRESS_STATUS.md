# ARGUS Neural Robustness Progress

## Existing ARGUS Pipeline
Status:
- Original LightGBM experiments: COMPLETE
- Original results: FROZEN
- Original figures: FROZEN
- Original reports: FROZEN

## Neural Experiments

| Experiment | Status | Seeds Completed | Checkpoint Exists | Metrics Exist | Predictions Exist | Figures Exist | Can Reuse? |
|---|---|---:|---|---|---|---|---|
| N0 Environment Check | COMPLETE | 1 | N/A | YES | YES | N/A | YES |
| N1 FT-Transformer ARGUS-4 D1→D3 | ARTIFACTS FINALIZED | 5 | YES | YES | YES | YES | YES |
| N2 FT-Transformer ARGUS-4 D2→D3 | ARTIFACTS FINALIZED | 5 | YES | YES | YES | YES | YES |
| N3 FT-Transformer Native SCADA | AUDITED — NO NEW TRAINING | 1 (1 partial) | YES (Seeds 42, 123) | YES (Seed 42 Validated) | YES (Seed 42) | NO | PARTIAL |
| N4 Additional Seeds | PARTIAL | 4 (N1, N2) | YES | YES | NO | NO | YES |

---

## Detailed Audit Summary

### 1. N0 Environment Check (Status: COMPLETE)
- **Environment**: Python 3.14.4, PyTorch 2.13.0, Apple Silicon M4 MPS hardware acceleration (16 GB Unified Memory, 10 CPU cores).
- **Architecture**: `FTTransformer` (NumericalFeatureTokenizer + MultiheadAttention TransformerBlocks + Head) verified.
- **Diagnostic Run**: 1,000-sample mini-batch forward/backward pass executed in 4.58s with full memory release.
- **Artifact**: `reports/N0_environment_report.md` generated.

### 2. N1 FT-Transformer ARGUS-4 D1→D3 (Status: ARTIFACTS FINALIZED)
- **Checkpoints**: `checkpoints/FTT_ARGUS4_D1_D3_seed*/best_model.pt` (all 5 seeds verified).
- **Predictions**: `predictions/NR01/D1_D3_seed42_predictions.csv` (714,453 test predictions).
- **Metrics**: `metrics/NR01_FTTransformer_ARGUS4.csv` and `summary.csv`.
- **Figures Generated**: `figures/N1_ROC.png`, `figures/N1_PR.png`, `figures/N1_confusion_matrix.png`, `figures/N1_training_curve.png` (300 DPI) + `N1_ROC.csv`, `N1_PR.csv`.
- **Tables & Reports**: `tables/N1_LightGBM_vs_FTTransformer.csv` and `reports/N1_interpretation.md`.
- **Scientific Verdict**: FT-Transformer ROC-AUC ($0.5543 \pm 0.0402$) vs LightGBM ($0.5442 \pm 0.0108$) confirms that transfer failure is driven by feature representation collapse, not model family.

### 3. N2 FT-Transformer ARGUS-4 D2→D3 (Status: ARTIFACTS FINALIZED)
- **Checkpoints**: All 5 seeds verified under `checkpoints/FTT_ARGUS4_D2_D3_seed*/best_model.pt`.
- **Predictions**: `predictions/NR01/D2_D3_seed42_predictions.csv` (714,453 test predictions).
- **Figures Generated**: `figures/N2_ROC.png`, `figures/N2_PR.png`, `figures/N2_confusion_matrix.png`, `figures/N2_training_curve.png` (300 DPI) + `N2_ROC.csv`, `N2_PR.csv`.
- **Tables & Reports**: `tables/N2_LightGBM_vs_FTTransformer.csv` and `reports/N2_interpretation.md`.
- **Scientific Verdict**: FT-Transformer ROC-AUC ($0.4877 \pm 0.0322$) vs LightGBM ($0.4381 \pm 0.0021$) confirms sub-chance conditional distribution shift between D2 and D3 across both architectures.

### 4. N3 FT-Transformer Native SCADA (Status: AUDITED — NO NEW TRAINING)
- **Checkpoints**: Seed 42 and Seed 123 checkpoints exist (`checkpoints/FTT_Native_seed42`, `FTT_Native_seed123`).
- **Predictions**: `predictions/NR02/D3_native_seed42_predictions.csv` ($N = 714,453$).
- **Metrics**: Validated directly from predictions in `validation/N3_seed42_metric_check.csv` ($\text{ROC-AUC} = 0.6425$, $\text{MCC} = 0.2363$).
- **Audit Report**: `reports/N3_COMPLETION_AUDIT.md`.
- **Action**: No new training conducted. Seed 123 checkpoint is available for direct inference.

### 5. N4 Additional Seeds (Status: PARTIAL)
- Seeds 123, 456, 789, 1011 are complete for N1 and N2.
- Seeds 456, 789, 1011 not started for N3.
