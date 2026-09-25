# EXP-02: Bayesian Prior-Shift Deconstruction Report

## Executive Summary
This experiment isolates the mathematical mechanics of **Class-Prior Shift** versus **Distributional Divergence**. It proves that:
1. Source attack base rates ($P_{S1}=97.64\%$, $P_{S2}=72.58\%$) dictate the direction of zero-shot failure:
   - D1 $\to$ D3 transfer causes **False Positive Saturation** ($\text{FPR} = 98.32%$, $\text{Recall} = 99.62%$).
   - D2 $\to$ D3 transfer causes **False Negative Saturation** ($\text{FNR} = 93.63%$, $\text{Recall} = 6.37%$).
2. Threshold calibration and Bayesian prior correction mathematically adjust operating point trade-offs (moving F1 from $0.1091 \to 0.3648$) **without changing underlying class ranking separation** ($\text{ROC-AUC}$ remains strictly identical at $0.4409$).

## Prior-Shift Decomposition Table

| transfer_scenario           | variant                               |   threshold |   accuracy |   precision |    recall |        f1 |       fpr |        fnr |         mcc |   roc_auc |   brier_score |
|:----------------------------|:--------------------------------------|------------:|-----------:|------------:|----------:|----------:|----------:|-----------:|------------:|----------:|--------------:|
| D1 -> D3 (CICIoT -> SCADA)  | 1. Raw Baseline (θ=0.50)              |        0.5  |   0.236844 |   0.226954  | 0.996156  | 0.369683  | 0.983172  | 0.00384402 |  0.0462688  |  0.539025 |      0.756051 |
| D1 -> D3 (CICIoT -> SCADA)  | 2. Threshold Calibrated Only (θ=0.63) |        0.63 |   0.24866  |   0.229221  | 0.992275  | 0.372413  | 0.966807  | 0.00772542 |  0.0650284  |  0.539025 |      0.756051 |
| D1 -> D3 (CICIoT -> SCADA)  | 3. Prior Correction Only (θ=0.50)     |        0.5  |   0.24866  |   0.229221  | 0.992275  | 0.372413  | 0.966807  | 0.00772542 |  0.0650284  |  0.539025 |      0.74851  |
| D1 -> D3 (CICIoT -> SCADA)  | 4. Prior Correction + Calib (θ=0.95)  |        0.95 |   0.25047  |   0.229534  | 0.991359  | 0.372761  | 0.964208  | 0.00864126 |  0.0667603  |  0.539025 |      0.74851  |
| D2 -> D3 (ToN-IoT -> SCADA) | 1. Raw Baseline (θ=0.50)              |        0.5  |   0.766179 |   0.378765  | 0.0636974 | 0.109055  | 0.030272  | 0.936303   |  0.073166   |  0.44099  |      0.222396 |
| D2 -> D3 (ToN-IoT -> SCADA) | 2. Threshold Calibrated Only (θ=0.01) |        0.01 |   0.244624 |   0.224911  | 0.965703  | 0.364849  | 0.964314  | 0.0342971  |  0.00313776 |  0.44099  |      0.222396 |
| D2 -> D3 (ToN-IoT -> SCADA) | 3. Prior Correction Only (θ=0.50)     |        0.5  |   0.764642 |   0.264178  | 0.0266714 | 0.0484512 | 0.0215256 | 0.973329   |  0.0144246  |  0.44099  |      0.22182  |
| D2 -> D3 (ToN-IoT -> SCADA) | 4. Prior Correction + Calib (θ=0.05)  |        0.05 |   0.755495 |   0.349022  | 0.1021    | 0.157985  | 0.0551789 | 0.8979     |  0.0790299  |  0.44099  |      0.22182  |
| D2 -> D3 CORAL Aligned      | 1. Raw Baseline (θ=0.50)              |        0.5  |   0.272625 |   0.229007  | 0.945492  | 0.36871   | 0.922342  | 0.0545078  |  0.0372692  |  0.48602  |      0.454546 |
| D2 -> D3 CORAL Aligned      | 2. Threshold Calibrated Only (θ=0.68) |        0.68 |   0.343663 |   0.239613  | 0.884087  | 0.377038  | 0.812929  | 0.115913   |  0.0788636  |  0.48602  |      0.454546 |
| D2 -> D3 CORAL Aligned      | 3. Prior Correction Only (θ=0.50)     |        0.5  |   0.677152 |   0.0836884 | 0.043929  | 0.0576152 | 0.139368  | 0.956071   | -0.123503   |  0.48602  |      0.203215 |
| D2 -> D3 CORAL Aligned      | 4. Prior Correction + Calib (θ=0.19)  |        0.19 |   0.343663 |   0.239613  | 0.884087  | 0.377038  | 0.812929  | 0.115913   |  0.0788636  |  0.48602  |      0.203215 |

## Scientific Takeaway for Paper
Threshold optimization cannot be claimed as an improvement in model feature representation or domain adaptation. It simply shifts the operating point along a fixed, poorly separated ROC curve.
