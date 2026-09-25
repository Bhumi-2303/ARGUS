# ARGUS Domain Adaptation Report

**Source Dataset:** nftoniotv2
**Target Dataset:** ciciot2023
**Generated:** 2026-08-12T19:03:55.705583

---

## Executive Summary

This report evaluates three approaches to cross-dataset threat detection:
1. **Baseline (Exp 1):** Train on source with zero-padded features — no adaptation
2. **Aligned Baseline (Exp 2):** Map both datasets to a Unified Feature Schema
3. **DANN (Exp 3):** Domain-Adversarial Neural Network with gradient reversal

## Results

| Experiment    | Model    | Approach                    |       F1 |   Balanced_Accuracy |   Accuracy |        MCC |      Kappa |   ROC_AUC |   PR_AUC |   Training_Time_s |   Inference_Time_s |   domain_auc |   domain_auc_std |
|:--------------|:---------|:----------------------------|---------:|--------------------:|-----------:|-----------:|-----------:|----------:|---------:|------------------:|-------------------:|-------------:|-----------------:|
| Exp1_Baseline | xgboost  | Zero-Padded (No Adaptation) | 0.493745 |            0.5      |   0.975291 |  0         |  0         |  0.5      | 0.987645 |          1.24239  |          1.27184   |   nan        |    nan           |
| Exp1_Baseline | lightgbm | Zero-Padded (No Adaptation) | 0.493745 |            0.5      |   0.975291 |  0         |  0         |  0.5      | 0.987645 |          2.39995  |          2.53186   |   nan        |    nan           |
| Exp2_Aligned  | xgboost  | UFS-Aligned Features        | 0.244926 |            0.418839 |   0.302219 | -0.0549788 | -0.0113391 |  0.275406 | 0.946234 |          0.818081 |          0.0271931 |   nan        |    nan           |
| Exp2_Aligned  | lightgbm | UFS-Aligned Features        | 0.573597 |            0.791039 |   0.873632 |  0.263232  |  0.181675  |  0.834245 | 0.962737 |          2.24332  |          0.076206  |   nan        |    nan           |
| Exp3_DANN     | DANN     | Domain-Adversarial NN       | 0.477406 |            0.733396 |   0.725013 |  0.160197  |  0.0756279 |  0.827828 | 0.994924 |        nan        |        nan         |     0.999705 |      0.000257614 |

## Domain Invariance Analysis

**Aligned Features (Exp 2):** Domain AUC = 0.9999
  - POOR - Features are still domain-specific (AUC > 0.75)

**DANN Representations (Exp 3):** Domain AUC = 0.9997
  - POOR - Features are still domain-specific (AUC > 0.75)

## Key Insight

If the DANN's domain classifier AUC is closer to 0.5 than the aligned baseline's,
AND the DANN's task F1 is higher than the aligned baseline's,
then domain adaptation is working: the model has learned domain-invariant threat representations.

This is the evidence needed to position ARGUS as a **domain-adaptive cyber-defense architecture**.

## Figures

![Comparison Chart](training/exports/domain_adaptation/nftoniotv2_to_ciciot2023/figures/comparison_chart.png)

![Domain Auc Comparison](training/exports/domain_adaptation/nftoniotv2_to_ciciot2023/figures/domain_auc_comparison.png)

![Dann Training Curves](training/exports/domain_adaptation/nftoniotv2_to_ciciot2023/figures/dann_training_curves.png)

![Tsne Representations](training/exports/domain_adaptation/nftoniotv2_to_ciciot2023/figures/tsne_representations.png)
