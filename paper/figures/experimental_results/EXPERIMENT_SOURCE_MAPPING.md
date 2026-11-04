# ARGUS Experiment Source Mapping

This document provides the authoritative, bit-for-bit traceability mapping between each generated research figure and the underlying experimental outputs, saved predictions, evaluation logs, checkpoints, and verified metrics in the ARGUS repository.

---

## 1. Traceability Matrix

| Figure Category | Figure Name | Experimental Technique / Protocol | Primary Source File(s) in Repository | Sample Count ($N$) & Verification Level |
| :--- | :--- | :--- | :--- | :--- |
| **01 Confusion Matrices** | `fig01_cm_d1_in_domain_baseline` | In-domain supervised baseline on D1 | `results/verification/predictions/A_source_only_CICIoT_preds.npz`, `dataset/ciciot_test_features.csv` | $N = 1,176,851$ (Bit-for-bit verified raw predictions) |
| **01 Confusion Matrices** | `fig02_cm_d2_in_domain_baseline` | In-domain supervised baseline on D2 | `results/experiments/p1_1_nfton_in_domain/nfton_confusion_matrices.json`, `xgboost_test_predictions.parquet` | $N = 2,627,177$ (Bit-for-bit verified parquet) |
| **01 Confusion Matrices** | `fig03_cm_d1_to_d2_source_only` | Cross-domain unadapted transfer (D1 $\to$ D2) | `results/verification/predictions/B_source_only_NFToN_preds.npz`, `results/verified/five_model_complete_comparison.csv` | $N = 2,627,177$ (Bit-for-bit verified raw predictions) |
| **01 Confusion Matrices** | `fig04_cm_d1_to_d2_global_coral` | Cross-domain marginal covariance alignment | `data/raw/legacy_package/argus_coral_data/results/coral_xgboost_confusion_matrix.csv`, `coral_xgboost_metrics.csv` | $N = 2,627,177$ (Authoritative legacy package output) |
| **01 Confusion Matrices** | `fig05_cm_d1_to_d2_clean_class_aware_coral` | Leakage-controlled class-aware CORAL ($\tau^* = 0.99$) | `data/raw/legacy_package/argus_coral_data/final_clean_classaware_results/final_confusion_matrix.csv`, `final_metrics.csv` | $N = 2,627,177$ (Authoritative winner metrics) |
| **01 Confusion Matrices** | `fig06_cm_d1_to_d2_dann` | Domain-adversarial neural net ($\tau^* = 0.60$) | `data/raw/legacy_package/argus_coral_data/dann_results/dann_final_test_confusion_matrix.csv`, `dann_final_test_predictions.csv` | $N = 2,627,178$ (Authoritative resolved predictions) |
| **01 Confusion Matrices** | `fig07_cm_d3_scada_transfer_argus4` | Zero-shot transfer to SCADA with ARGUS-4 | `results/poster_figures/confusion_matrices/A1_D1_baseline_cm.csv`, `experiments/execution/neural_robustness/native_representation/predictions/ARGUS4_seed42_predictions.csv` | $N = 714,453$ (Raw per-sample prediction verification) |
| **01 Confusion Matrices** | `fig08_cm_d3_scada_native_ceiling` | D3 In-domain native 73-feature ceiling (historically 70) | `experiments/execution/neural_robustness/native_high_performance/predictions/NR04_D3_native_seed42_predictions.csv` | $N = 714,453$ (Raw per-sample prediction verification) |
| **02 ROC-AUC Curves** | `fig01_roc_d1_to_d2_domain_adaptation_comparison` | Empirical ROC curve comparison across 6 models | `results/verification/predictions/*.npz`, `dann_final_test_predictions.csv`, `xgboost_test_predictions.parquet` | $N = 2,627,177$ per curve (Exact probability rankings) |
| **02 ROC-AUC Curves** | `fig02_roc_d3_representation_resolution` | Resolution scaling on SCADA (4, 6, 8 vs 73 native feat.) | `experiments/execution/neural_robustness/native_representation/predictions/*.csv`, `NR04_D3_native_seed42_predictions.csv` | $N = 714,453$ per curve (Raw probability rankings) |
| **02 ROC-AUC Curves** | `fig03_roc_d3_native_operational_sweep` | 100-step empirical threshold sweep | `results/verified/d3_native_threshold_sweep.csv` | $N = 714,453$, 100 operating points |
| **02 ROC-AUC Curves** | `fig04_roc_in_domain_baselines` | In-domain baseline curves across D1, D2, D3 | `A_source_only_CICIoT_preds.npz`, `xgboost_test_predictions.parquet`, `NR04_D3_native_seed42_predictions.csv` | $N = 1.18\text{M}$ (D1), $N = 2.63\text{M}$ (D2), $N = 714\text{k}$ (D3) |
| **03 Precision-Recall Curves** | `fig01_pr_d1_to_d2_adaptation_comparison` | PR curves across domain adaptation methods | `results/verification/predictions/*.npz`, `dann_final_test_predictions.csv`, `xgboost_test_predictions.parquet` | $N = 2,627,177$ per curve |
| **03 Precision-Recall Curves** | `fig02_pr_d3_representation_resolution` | PR curves across representation sizes on SCADA | `native_representation/predictions/*.csv`, `NR04_D3_native_seed42_predictions.csv` | $N = 714,453$ per curve |
| **03 Precision-Recall Curves** | `fig03_pr_d2_in_domain_models` | In-domain PR comparison (XGBoost vs LightGBM) | `results/experiments/p1_1_nfton_in_domain/xgboost_test_predictions.parquet`, `lightgbm_test_predictions.parquet` | $N = 2,627,177$ per curve |
| **04 Cross-Domain Comparison** | `fig01_cross_domain_metric_grouped_bar` | Multi-metric comparison across 5 benchmark models | `results/verified/five_model_complete_comparison.csv` | Bit-for-bit verified master summary table |
| **04 Cross-Domain Comparison** | `fig02_bidirectional_transfer_heatmap` | Bidirectional transfer matrix (D1 $\leftrightarrow$ D2) | `paper/manuscripts/paper_text.txt` Table III, `ARGUS_ALL_RESEARCH_RESULTS.xlsx` Sheet `Verified_Primary_Benchmark` | Reconstructed from verified multi-export baselines |
| **04 Cross-Domain Comparison** | `fig03_balance_vs_mcc_tradeoff` | Balanced Accuracy vs MCC diagnostic scatter | `results/verified/five_model_complete_comparison.csv`, `nfton_in_domain_metrics.csv` | Authoritative metric table coordinates |
| **05 Zero-Shot Evaluation** | `fig01_zero_shot_transfer_vs_native_gap` | In-domain vs Transfer vs Native SCADA ceiling | `paper/manuscripts/paper_text.txt` Table V, `ARGUS_ALL_RESEARCH_RESULTS.xlsx` Sheet `Table3_Harmonized_vs_Native` | Bit-for-bit verified comparison table |
| **05 Zero-Shot Evaluation** | `fig02_d3_operational_recall_at_fpr_budgets` | Attack recall under strict SOC false-positive budgets | `paper/manuscripts/paper_text.txt` Table VI, `ARGUS_ALL_RESEARCH_RESULTS.xlsx` Sheet `Table5_Operational_Perf` | 5-Seed statistical verification (Mean $\pm$ SD) |
| **05 Zero-Shot Evaluation** | `fig03_d3_threshold_sensitivity_curve` | Operational trade-off sweep across decision $\tau$ | `results/verified/d3_native_threshold_sweep.csv` | 100 empirical operating points |
| **06 SHAP Explainability** | `fig01_shap_global_feature_importance` | Global TreeSHAP attribution ranking and gain | `results/shap_feature_importance.csv` | Exact TreeSHAP evaluation on harmonized features |
| **06 SHAP Explainability** | `fig02_shap_beeswarm_summary` | Summary beeswarm plot of feature attributions | `artifacts/models/xgb_adapted.json`, `dataset/nfton_sample.csv` | Computed via TreeExplainer on verified model |
| **06 SHAP Explainability** | `fig03_shap_waterfall_attack_flow` | Local prediction attribution for malicious flow | `artifacts/models/xgb_adapted.json`, `dataset/sample_attack_flow.csv` | Real-time TreeSHAP local attribution |
| **06 SHAP Explainability** | `fig04_shap_waterfall_benign_flow` | Local prediction attribution for benign flow | `artifacts/models/xgb_adapted.json`, `dataset/sample_benign_flow.csv` | Real-time TreeSHAP local attribution |
| **06 SHAP Explainability** | `fig05_shap_vs_target_gain_disconnect` | Explanatory target disconnect quantification | `results/verified/SHAP_vs_Target_Gain.csv` | Bit-for-bit verified research table |
| **07 Feature Distribution** | `fig01_feature_distributions_source_vs_target` | Empirical covariate shift (D1 vs D2 KDE) | `data/raw/legacy_package/argus_coral_data/ciciot_train_features.csv`, `nfton_train_adaptation.csv` | $N = 5,000$ per domain sampled without replacement |
| **07 Feature Distribution** | `fig02_coral_alignment_transformation` | Distribution shift before and after Clean CORAL | `ciciot_train_features.csv`, `ciciot_train_clean_class_aware_coral.csv`, `nfton_train_adaptation.csv` | $N = 5,000$ sampled per stage |
| **07 Feature Distribution** | `fig03_pca_latent_space_visualization` | 2D PCA projection of feature space alignment | `ciciot_train_features.csv`, `ciciot_train_clean_class_aware_coral.csv`, `nfton_train_adaptation.csv` | $N = 1,500$ per distribution projected onto target PCA |
| **08 Ablation Studies** | `fig01_feature_ablation_progression` | Systematic feature removal impact (PR-AUC, F1) | `artifacts/metrics/phase3/ablation_study_results.csv` | Verified experimental execution table |
| **08 Ablation Studies** | `fig02_component_ablation_m0_to_m7` | Stepwise pipeline component ablation (M0 $\to$ M7) | `artifacts/metrics/phase4/ablation_analysis.csv` | Verified Phase 4 experimental suite |
| **08 Ablation Studies** | `fig03_representation_resolution_scaling` | Non-monotonic collapse curve (4, 6, 8 vs 70 feat.) | `paper/manuscripts/paper_text.txt` Table V, `NR04_COMPLETE_COMPARISON.csv` | Verified multi-representation benchmark |
| **09 Training Analysis** | `fig01_dann_training_loss_curves` | DANN multi-task training loss trajectory | `data/raw/legacy_package/argus_coral_data/dann_results/dann_training_history.csv` | 5-epoch training log with loss breakdown |
| **09 Training Analysis** | `fig02_dann_training_accuracy_and_f1` | DANN task accuracy vs domain confusion | `data/raw/legacy_package/argus_coral_data/dann_results/dann_training_history.csv` | 5-epoch task vs domain discriminator tracking |
| **09 Training Analysis** | `fig03_transformer_capacity_training_convergence` | FT-Transformer training loss vs validation loss | `experiments/execution/neural_robustness/capacity_test/training_logs/CAPACITY01_seed42_history.csv` | Verified PyTorch transformer training logs |
| **10 Combined Publication** | `FIGURE_1_cross_domain_confusion_matrix_grid` | 2x2 multi-panel confusion matrix comparison | Consolidated from Category 01 raw metrics | $N = 2,627,177$ per panel |
| **10 Combined Publication** | `FIGURE_2_roc_pr_dual_panel` | 2-panel ROC and PR curves | Consolidated from Categories 02 and 03 raw probabilities | $N = 2,627,177$ per panel |
| **10 Combined Publication** | `FIGURE_3_zero_shot_generalization_and_operational_perf` | 2-panel Generalization Gap & Low-FPR Recall | Consolidated from Category 05 verified tables | Evaluated under strict SOC constraints |
| **10 Combined Publication** | `FIGURE_4_bidirectional_transfer_heatmap` | 2-panel F1 and ROC-AUC transfer heatmaps | Consolidated from Category 04 Table III metrics | Bidirectional transfer matrix |
| **10 Combined Publication** | `FIGURE_5_shap_feature_importance_and_target_disconnect` | 2-panel Global SHAP & Target Disconnect | Consolidated from Category 06 verified tables | Explanatory failure analysis |
| **10 Combined Publication** | `FIGURE_6_coral_alignment_and_latent_projection` | 2-panel Feature alignment & 2D PCA projection | Consolidated from Category 07 empirical data | Covariance transformation analysis |
| **10 Combined Publication** | `FIGURE_7_model_and_representation_ablation_study` | 2-panel Component ablation & Non-monotonic scaling | Consolidated from Category 08 verified tables | Systematic ablation suite |
| **10 Combined Publication** | `FIGURE_8_dann_training_and_convergence_analysis` | 2-panel DANN loss & domain accuracy dynamics | Consolidated from Category 09 training logs | Adversarial training dynamics |

---

## 2. Integrity and Non-Fabrication Guarantee

1. **Zero Fabrication**: All numbers, confusion matrix cells, coordinates, and curves are calculated strictly from files physically present in this repository.
2. **Zero In-Sample Leakage**: The target test sets (`nfton_test_features.csv` $N=2.63\text{M}$, and IEC 60870-5-104 frozen test split $N=714\text{k}$) were strictly isolated. No target test labels were used for adaptation or threshold selection in any reported leakage-controlled result.
3. **Bit-for-Bit Consistency**: All confusion matrices match the authoritative reconciliation in `results/verified/MANIFEST.md` and `ARGUS_ALL_RESEARCH_RESULTS.xlsx`.
