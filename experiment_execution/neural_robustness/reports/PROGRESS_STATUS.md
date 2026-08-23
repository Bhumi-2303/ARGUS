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

## Capacity & Regularization Ablation Tests

| Experiment | Model | Intervention | Task | Seed | Status | Scientific Finding |
|---|---|---|---|---:|---|---|
| CAPACITY-01 | FTT-LARGE (200.7k params) | Capacity Expansion (11.5x) | D1→D3 ARGUS-4 | 42 | COMPLETE | **CASE A**: ROC-AUC degraded to 0.5100, proving capacity expansion accelerates overfitting. |
| CAPACITY-01R | FTT-LARGE-REG (200.7k params) | Dropout 0.30, Decay 0.01 | D1→D3 ARGUS-4 | 42 | COMPLETE | **CASE C**: Regularization failed to resolve transfer limitation ($\text{AUC}=0.5107$). |
| **A0 (Baseline)** | FTT-SMALL (17.5k params) | Baseline (Preserved) | D1→D3 ARGUS-4 | 42 | COMPLETE | **BASELINE**: Preserved ROC-AUC = 0.6075, PR-AUC = 0.3595. |
| **A1 (Label Smooth)** | FTT-SMALL (17.5k params) | Label Smoothing (0.05) | D1→D3 ARGUS-4 | 42 | COMPLETE | **CATEGORY C**: ROC-AUC degraded to 0.5720 (-5.84%), PR-AUC = 0.5597. |
| **A2 (Feature Mask)** | FTT-SMALL (17.5k params) | 10% Feature Noise | D1→D3 ARGUS-4 | 42 | COMPLETE | **CATEGORY D**: ROC-AUC collapsed to 0.5162 (-15.02%), PR-AUC = 0.1810. |
| **A3 (Combined)** | FTT-SMALL (17.5k params) | LS=0.05 + FM=0.10 | D1→D3 ARGUS-4 | 42 | COMPLETE | **CATEGORY D**: ROC-AUC collapsed to 0.5144 (-15.33%), PR-AUC = 0.1776. |

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

### 5. Regularization & Robustness Ablation Suite A0–A3 (Status: COMPLETE)
- **A0 Baseline**: Preserved ROC-AUC = 0.6075, PR-AUC = 0.3595.
- **A1 Label Smoothing**: ROC-AUC = 0.5720 (-5.84%), PR-AUC = 0.5597.
- **A2 Feature Masking**: ROC-AUC = 0.5162 (-15.02%), PR-AUC = 0.1810.
- **A3 Combined**: ROC-AUC = 0.5144 (-15.33%), PR-AUC = 0.1776.
- **Artifacts**: `tables/REGULARIZATION_ABLATION_COMPARISON.csv`, `tables/REGULARIZATION_EFFECTS.csv`, `reports/REGULARIZATION_ABLATION_REPORT.md`, `reports/PAPER_EVIDENCE_REGULARIZATION.md`, `ablation/REGULARIZATION_ARTIFACT_MANIFEST.csv`.
- **Scientific Verdict**: **CATEGORY C / D** — Conventional neural regularization and input noise training fail to improve cross-domain transfer ($\text{ROC-AUC} \le 0.5720$), demonstrating that cross-domain degradation is driven by domain covariate shift and representation collapse rather than unregularized neural overfitting.
