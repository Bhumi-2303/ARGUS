# ARGUS Repository Audit Report

**Date**: September 24, 2026  
**Repository**: ARGUS (`c:\Users\acer\Desktop\ARGUS`)  
**Audit Scope**: Read-Only Comprehensive Repository Audit  

---

## 1. Repository Directory Tree (Depth 3)

*Note: File sizes are annotated for files exceeding 10 MB.*

```text
ARGUS/
├── .git/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .pytest_cache/
│   ├── v/
│   │   └── cache/
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   └── README.md
├── .venv/
│   ├── bin/
│   │   ├── ._python
│   │   ├── ._python3
│   │   ├── ._python3.14
│   │   ├── ._𝜋thon
│   │   ├── activate
│   │   ├── activate.csh
│   │   ├── activate.fish
│   │   ├── Activate.ps1
│   │   ├── alembic
│   │   ├── chroma
│   │   ├── dotenv
│   │   ├── f2py
│   │   ├── fastapi
│   │   ├── fonttools
│   │   ├── hf
│   │   ├── httpx
│   │   ├── huggingface-cli
│   │   ├── idna
│   │   ├── isympy
│   │   ├── jsonschema
│   │   ├── mako-render
│   │   ├── markdown-it
│   │   ├── normalizer
│   │   ├── numba
│   │   ├── numpy-config
│   │   ├── onnxruntime_test
│   │   ├── optuna
│   │   ├── pip
│   │   ├── pip3
│   │   ├── pip3.14
│   │   ├── py.test
│   │   ├── pybase64
│   │   ├── pyftmerge
│   │   ├── pyftsubset
│   │   ├── pygmentize
│   │   ├── pyproject-build
│   │   ├── pytest
│   │   ├── python
│   │   ├── python3
│   │   ├── python3.14
│   │   ├── tabulate
│   │   ├── tiny-agents
│   │   ├── torchfrtrace
│   │   ├── torchrun
│   │   ├── tqdm
│   │   ├── transformers
│   │   ├── ttx
│   │   ├── typer
│   │   ├── uvicorn
│   │   ├── watchfiles
│   │   ├── websockets
│   │   ├── wsdump
│   │   └── 𝜋thon
│   ├── include/
│   ├── lib/
│   │   ├── python3.14/
│   │   └── .DS_Store
│   ├── share/
│   │   └── man/
│   ├── .DS_Store
│   ├── .gitignore
│   └── pyvenv.cfg
├── agent/
│   └── __pycache__/
│       └── main.cpython-314.pyc
├── api/
│   └── __pycache__/
│       └── main.cpython-314.pyc
├── ARGUS_Cross_Domain_Results/
│   ├── argus_coral_data/
│   │   ├── class_aware_results/
│   │   ├── dann_results/
│   │   ├── final_clean_classaware_results/
│   │   ├── final_five_model_comparison/
│   │   ├── final_model_comparison/
│   │   ├── results/
│   │   ├── ciciot_test_features.csv (57.62 MB)
│   │   ├── ciciot_train_class_aware_coral.csv (398.84 MB)
│   │   ├── ciciot_train_clean_class_aware_coral.csv (395.94 MB)
│   │   ├── ciciot_train_coral_aligned.csv (396.46 MB)
│   │   ├── ciciot_train_features.csv (268.87 MB)
│   │   ├── coral_parameters.npz
│   │   ├── domain3_composition_summary.json
│   │   ├── iec104_test_features.csv (30.62 MB)
│   │   ├── iec104_train_adaptation.csv (97.96 MB)
│   │   ├── iec104_train_calibration.csv (24.50 MB)
│   │   ├── iec104_train_features.csv (122.46 MB)
│   │   ├── nfton_test_features.csv (132.24 MB)
│   │   ├── nfton_train_adaptation.csv (415.38 MB)
│   │   ├── nfton_train_calibration.csv (103.85 MB)
│   │   └── nfton_train_features.csv (528.94 MB)
│   └── ARGUS_RESULTS_README.txt
├── ARGUS_D1_D2_AUDIT/
│   ├── bidirectional_status.csv
│   ├── dann_reconciliation.csv
│   ├── experiment_inventory.csv
│   ├── FINAL_D1_D2_AUDIT.md
│   ├── metric_recomputation.csv
│   ├── missing_artifacts.csv
│   ├── multiseed_status.csv
│   ├── raw_prediction_inventory.csv
│   ├── reported_vs_recomputed.csv
│   └── test_set_identity.csv
├── ARGUS_D3_VALIDITY_AUDIT/
│   ├── duplicate_audit.csv
│   ├── experiment_inventory.csv
│   ├── feature_leakage_audit.csv
│   ├── FINAL_D3_VALIDITY_AUDIT.xlsx
│   ├── FINAL_D3_VALIDITY_REPORT.md
│   ├── generate_audit.py
│   ├── metric_verification.csv
│   ├── missing_experiments.csv
│   ├── raw_prediction_inventory.csv
│   ├── rep01_validity_report.md
│   ├── representation_comparison.csv
│   ├── split_audit.csv
│   └── temporal_causality_audit.csv
├── ARGUS_HEALTH_CHECK/
│   ├── REPORT.md
│   └── requirements.txt
├── ARGUS_Paper_Data/
│   ├── 2_REP01_Deliverables/
│   │   ├── configs/
│   │   ├── figures/
│   │   ├── reports/
│   │   ├── scripts/
│   │   ├── tables/
│   │   └── REP01_experiment_state.json
│   ├── 3_Entropy_Computation/
│   │   └── entropy_results.txt
│   └── README.md
├── ARGUS_PAPER_READINESS_AUDIT/
│   ├── claim_audit.csv
│   ├── evidence_matrix.csv
│   ├── experiment_inventory.csv
│   ├── figure_plan.csv
│   ├── FINAL_PAPER_READINESS_AUDIT.xlsx
│   ├── FINAL_PAPER_READINESS_REPORT.md
│   ├── generate_excel.py
│   ├── metric_audit.csv
│   ├── missing_experiments.csv
│   ├── paper_writing_plan.md
│   ├── section_readiness.csv
│   ├── statistical_audit.csv
│   └── table_plan.csv
├── artifacts/
│   ├── day4/
│   │   ├── fusion.json
│   │   └── results.json
│   ├── figures/
│   │   ├── phase3/
│   │   ├── phase4/
│   │   └── scientific_validation/
│   ├── metrics/
│   │   ├── phase3/
│   │   ├── phase4/
│   │   ├── phase4_multiseed/
│   │   ├── agent_review_behavior.csv
│   │   ├── feature_representation_comparison.csv
│   │   ├── fpr_ambiguity_analysis.csv
│   │   ├── phase4_multiseed_paper_table.csv
│   │   ├── phase4_multiseed_results.csv
│   │   ├── phase4_multiseed_summary.csv
│   │   └── risk_decision_analysis.csv
│   ├── models/
│   │   ├── phase4/
│   │   ├── model_d1_baseline.txt
│   │   ├── model_d1_coral.txt
│   │   ├── model_d2_baseline.txt
│   │   ├── model_d2_coral.txt
│   │   ├── model_d3_native.txt
│   │   ├── model_d3_protocol_aware.txt
│   │   ├── model_d3_protocol_aware_grouped.txt
│   │   ├── model_d3_protocol_combined.txt
│   │   ├── model_d3_protocol_combined_grouped.txt
│   │   ├── registry.yaml
│   │   ├── xgb_adapted.json
│   │   └── xgb_source.json
│   └── reports/
│       ├── agent_contribution_analysis.md
│       ├── feature_representation_analysis.md
│       ├── fpr_ambiguity_analysis.md
│       ├── next_phase_scientific_validation.md
│       ├── phase4_multiseed_robustness.md
│       ├── risk_aware_evaluation.md
│       └── scientific_validation_provenance.md
├── BoT-IoT dataset/
│   └── bot_iot_full_archive.zip (1.17 GB)
├── catboost_info/
│   ├── learn/
│   │   └── events.out.tfevents
│   ├── test/
│   │   └── events.out.tfevents
│   ├── tmp/
│   ├── .DS_Store
│   ├── catboost_training.json
│   ├── learn_error.tsv
│   ├── test_error.tsv
│   └── time_left.tsv
├── config/
│   ├── __init__.py
│   ├── agents.yaml
│   ├── feature_flags.yaml
│   ├── logging.yaml
│   ├── security.yaml
│   ├── settings.py
│   └── tools.yaml
├── data/
│   ├── cic_iot_2023/
│   │   └── metadata/
│   ├── CICIOT23/
│   │   └── .DS_Store
│   ├── hai/
│   │   └── metadata/
│   ├── IEC104/
│   │   ├── processed/
│   │   ├── raw/
│   │   └── Balanced_IEC104_Train_Test_CSV_Files.7z (10.85 MB)
│   ├── nf_ton_iot/
│   │   └── metadata/
│   ├── NFTONIoTV2/
│   │   └── NF-ToN-IoT-V2.parquet (199.48 MB)
│   ├── ton_iot/
│   │   └── metadata/
│   ├── .DS_Store
│   ├── CROSS_DATASET_COMPATIBILITY.md
│   ├── DATASET_ACQUISITION_REPORT.md
│   ├── DATASET_COMPLETION_REPORT.md
│   ├── DATASET_MANIFEST.json
│   ├── FINAL_DATASET_MANIFEST.json
│   └── FINAL_DATASET_READINESS.md
├── deployment/
│   ├── compose/
│   │   └── docker-compose.yml
│   └── docker/
│       ├── decision.Dockerfile
│       ├── detector.Dockerfile
│       ├── knowledge.Dockerfile
│       ├── orchestrator.Dockerfile
│       ├── risk.Dockerfile
│       └── streaming.Dockerfile
├── docs/
│   ├── api/
│   │   ├── endpoints.md
│   │   └── event_schema.md
│   ├── architecture/
│   │   ├── 00_ARGUS_MASTER_SPECIFICATION.md
│   │   ├── agent_contracts.md
│   │   ├── current_state.md
│   │   ├── decision_policy.md
│   │   ├── final_platform_audit.md
│   │   ├── incident_lifecycle.md
│   │   ├── incident_management.md
│   │   ├── model_monitoring.md
│   │   └── professional_architecture_audit.md
│   ├── deployment/
│   │   ├── ci_cd.md
│   │   └── frontend_dependency_audit.md
│   ├── development/
│   │   └── testing.md
│   ├── experiments/
│   │   ├── experiment_index.md
│   │   └── reproducibility_audit.md
│   ├── frontend/
│   │   └── frontend_architecture.md
│   ├── research/
│   │   └── data_management.md
│   ├── architecture.md
│   ├── argus_architecture_analysis.md
│   └── GIT_REPOSITORY_STATUS.md
├── experiment_execution/
│   ├── checkpoints/
│   ├── configs/
│   │   └── experiment_manifest.yaml
│   ├── figures/
│   │   ├── EXP01_PR.png
│   │   ├── EXP01_ROC.png
│   │   ├── EXP02_prior_shift.png
│   │   ├── EXP03_cardinality.png
│   │   ├── EXP04_confusion_matrix.png
│   │   ├── EXP04_PR.png
│   │   ├── EXP04_ROC.png
│   │   ├── EXP05_PR.png
│   │   ├── EXP05_ROC.png
│   │   ├── EXP06_FPR_vs_Recall.png
│   │   ├── EXP07_feature_resolution.png
│   │   ├── Figure1_Framework.png
│   │   ├── Figure2_ROC_PR_Overlay.png
│   │   └── SHAP_vs_Target_Gain.png
│   ├── logs/
│   ├── metrics/
│   │   ├── EXP01_raw_results.csv
│   │   ├── EXP01_summary.csv
│   │   ├── EXP02_prior_shift.csv
│   │   ├── EXP03_cardinality.csv
│   │   ├── EXP04_native.csv
│   │   ├── EXP04_native_summary.csv
│   │   ├── EXP05_UDA_results.csv
│   │   ├── EXP05_UDA_summary.csv
│   │   ├── EXP06_operating_points.csv
│   │   ├── EXP07_feature_resolution.csv
│   │   └── statistical_summary.csv
│   ├── neural_robustness/
│   │   ├── ablation/
│   │   ├── audit/
│   │   ├── capacity_test/
│   │   ├── checkpoints/
│   │   ├── configs/
│   │   ├── domain_adaptation/
│   │   ├── figures/
│   │   ├── logs/
│   │   ├── metrics/
│   │   ├── native_high_performance/
│   │   ├── native_representation/
│   │   ├── predictions/
│   │   ├── reports/
│   │   ├── representation_extension/
│   │   ├── scripts/
│   │   ├── tables/
│   │   ├── training_logs/
│   │   ├── validation/
│   │   ├── ._experiment_state.json
│   │   ├── ._native_representation
│   │   ├── ._representation_extension
│   │   ├── .DS_Store
│   │   └── experiment_state.json
│   ├── predictions/
│   │   ├── EXP01/
│   │   ├── EXP04/
│   │   └── EXP05/
│   ├── reports/
│   │   ├── dataset_freeze_report.md
│   │   ├── EXP01_report.md
│   │   ├── EXP02_report.md
│   │   ├── EXP03_report.md
│   │   ├── EXP04_report.md
│   │   ├── EXP05_report.md
│   │   ├── EXP06_operational_report.md
│   │   ├── EXP07_report.md
│   │   ├── explainability_report.md
│   │   ├── feature_freeze_report.md
│   │   ├── final_claim_evidence_matrix.md
│   │   ├── final_pre_paper_verdict.md
│   │   ├── repository_inventory.md
│   │   └── statistical_validation_report.md
│   ├── scripts/
│   │   ├── __pycache__/
│   │   ├── generate_figures.py
│   │   ├── generate_final_reports.py
│   │   ├── generate_shap_analysis.py
│   │   ├── generate_tables.py
│   │   ├── run_exp01.py
│   │   ├── run_exp02.py
│   │   ├── run_exp03.py
│   │   ├── run_exp04.py
│   │   ├── run_exp05.py
│   │   ├── run_exp06.py
│   │   ├── run_exp07.py
│   │   ├── setup_manifest_and_validation.py
│   │   ├── validate_all_results.py
│   │   ├── validate_datasets.py
│   │   ├── validate_features.py
│   │   └── validate_metrics.py
│   ├── tables/
│   │   ├── EXP02_prior_shift_decomposition.csv
│   │   ├── EXP03_representation_comparison.csv
│   │   ├── EXP04_feature_gain.csv
│   │   ├── EXP05_primary_benchmark.csv
│   │   ├── EXP06_operational_table.csv
│   │   ├── EXP07_feature_resolution.csv
│   │   ├── SHAP_vs_Target_Gain.csv
│   │   ├── Table1_Dataset_Characteristics.csv
│   │   ├── Table2_Primary_Benchmark.csv
│   │   ├── Table3_Harmonized_vs_Native.csv
│   │   ├── Table4_Feature_Resolution_Scaling.csv
│   │   └── Table5_Operational_Performance.csv
│   ├── validation/
│   │   ├── dataset_partition_validation.json
│   │   └── global_experiment_validation_report.md
│   ├── .DS_Store
│   ├── FINAL_MASTER_RESULTS.csv
│   └── FINAL_STATUS.md
├── experiments/
│   ├── ablations/
│   │   ├── phase4_execute.py
│   │   └── phase4_execute_fast.py
│   ├── analysis/
│   │   └── feature_resolution_study.py
│   ├── configs/
│   │   └── paths.yaml
│   └── domain_adaptation/
│       ├── coral/
│       └── dann/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── main.tsx
│   │   ├── types.ts
│   │   └── vite-env.d.ts
│   ├── .gitignore
│   ├── .nvmrc
│   ├── app.py
│   ├── audit.json
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tsconfig.node.tsbuildinfo
│   ├── vite.config.d.ts
│   ├── vite.config.js
│   └── vite.config.ts
├── knowledge_agent/
│   ├── __pycache__/
│   │   └── main.cpython-314.pyc
│   └── .DS_Store
├── LightGBM_CICIoT2023_Backup/
│   ├── excel/
│   │   ├── classification_report.xlsx
│   │   ├── correlation_matrix.xlsx
│   │   ├── dataset_profile.xlsx
│   │   ├── feature_importance.xlsx
│   │   ├── feature_name_mapping.xlsx
│   │   ├── feature_statistics.xlsx
│   │   ├── fp_fn_analysis.xlsx
│   │   ├── label_mapping.xlsx
│   │   ├── per_class_metrics.xlsx
│   │   ├── test_metrics.xlsx
│   │   └── training_history.xlsx
│   ├── logs/
│   │   ├── config.json
│   │   ├── dataset_schema_report.csv
│   │   ├── system_info.json
│   │   ├── training_history.csv
│   │   └── training_log.txt
│   ├── metrics/
│   │   ├── test_metrics.csv
│   │   └── test_metrics.json
│   ├── model/
│   │   ├── checkpoints/
│   │   ├── lightgbm_best_model.joblib (108.14 MB)
│   │   ├── lightgbm_best_model.pkl (108.14 MB)
│   │   └── lightgbm_best_model.txt (108.14 MB)
│   ├── plots/
│   │   ├── class_distribution.png
│   │   ├── class_support.png
│   │   ├── confusion_matrix.png
│   │   ├── confusion_matrix_normalized.png
│   │   ├── correlation_heatmap.png
│   │   ├── false_negative_analysis.png
│   │   ├── false_positive_analysis.png
│   │   ├── feature_boxplots.png
│   │   ├── feature_histograms.png
│   │   ├── gain_importance.png
│   │   ├── gain_vs_split_importance.png
│   │   ├── missing_value_heatmap.png
│   │   ├── overall_metrics.png
│   │   ├── per_class_metrics.png
│   │   ├── precision_recall_scatter.png
│   │   ├── split_importance.png
│   │   ├── top10_classes.png
│   │   └── worst10_classes.png
│   ├── reports/
│   │   ├── classification_report.csv
│   │   ├── classification_report.txt
│   │   ├── confusion_matrix.csv
│   │   ├── confusion_matrix_normalized.csv
│   │   ├── correlation_matrix.csv
│   │   ├── data_types.csv
│   │   ├── dataset_profile.csv
│   │   ├── feature_importance.csv
│   │   ├── feature_name_mapping.csv
│   │   ├── feature_statistics.csv
│   │   ├── feature_variance.csv
│   │   ├── fp_fn_analysis.csv
│   │   ├── label_mapping.csv
│   │   ├── missing_values.csv
│   │   ├── per_class_metrics.csv
│   │   └── preprocessing_summary.csv
│   ├── shap/
│   ├── temp/
│   │   └── eda_sample.csv (25.28 MB)
│   └── .DS_Store
├── models/
│   ├── best_model/
│   │   └── model.joblib (12.70 MB)
│   └── model_d2_coral.txt
├── orchestrator/
│   └── __pycache__/
│       └── main.cpython-314.pyc
├── phase3_results/
│   ├── checkpoints/
│   │   ├── coral_d1_d3_parameters.npz
│   │   ├── coral_d2_d3_parameters.npz
│   │   ├── dann_d1_d3_checkpoint.pt
│   │   ├── dann_d1_d3_epoch_01.pt
│   │   ├── dann_d1_d3_epoch_02.pt
│   │   ├── dann_d1_d3_epoch_03.pt
│   │   ├── dann_d1_d3_epoch_04.pt
│   │   ├── dann_d1_d3_epoch_05.pt
│   │   ├── dann_d1_d3_epoch_06.pt
│   │   ├── dann_d1_d3_epoch_07.pt
│   │   ├── dann_d1_d3_epoch_08.pt
│   │   ├── dann_d1_d3_epoch_09.pt
│   │   ├── dann_d1_d3_epoch_10.pt
│   │   ├── dann_d2_d3_checkpoint.pt
│   │   ├── dann_d2_d3_epoch_01.pt
│   │   ├── dann_d2_d3_epoch_02.pt
│   │   ├── dann_d2_d3_epoch_03.pt
│   │   ├── dann_d2_d3_epoch_04.pt
│   │   ├── dann_d2_d3_epoch_05.pt
│   │   ├── dann_d2_d3_epoch_06.pt
│   │   ├── dann_d2_d3_epoch_07.pt
│   │   ├── dann_d2_d3_epoch_08.pt
│   │   ├── dann_d2_d3_epoch_09.pt
│   │   └── dann_d2_d3_epoch_10.pt
│   ├── domain_shift/
│   │   ├── class_prior_summary.csv
│   │   └── domain_shift_statistics.csv
│   ├── experiments/
│   │   ├── D1_D3_BASELINE/
│   │   ├── D1_D3_CORAL/
│   │   ├── D1_D3_DANN/
│   │   ├── D2_D3_BASELINE/
│   │   ├── D2_D3_CORAL/
│   │   └── D2_D3_DANN/
│   ├── logs/
│   │   ├── execution.log
│   │   ├── experiment_status.json
│   │   ├── phase3_execution.log
│   │   └── progress.json
│   ├── metrics/
│   │   └── ablation_study_results.csv
│   ├── models/
│   │   ├── model_d1_baseline.txt
│   │   ├── model_d1_coral.txt
│   │   ├── model_d2_baseline.txt
│   │   └── model_d2_coral.txt
│   ├── shap/
│   │   └── shap_feature_importance.csv
│   ├── .DS_Store
│   ├── ARGUS_Phase3_Artifacts.zip
│   ├── ARGUS_Phase3_Final_Report.md
│   ├── ARGUS_Phase3_Results.xlsx
│   ├── metrics_validation_report.json
│   ├── metrics_validation_report.md
│   ├── regenerate_corrected_artifacts.py
│   └── validate_metrics.py
├── phase4_results/
│   ├── __pycache__/
│   │   └── phase4_execute.cpython-314.pyc
│   ├── checkpoints/
│   ├── coral/
│   │   └── coral_weight_optimization.csv
│   ├── dann/
│   │   └── dann_weight_optimization.csv
│   ├── experiments/
│   │   ├── A1_D1_baseline/
│   │   ├── A2_D2_baseline/
│   │   ├── A5_D1_CORAL/
│   │   ├── A6_D2_CORAL/
│   │   ├── B1_D1_prior/
│   │   ├── B2_D2_prior/
│   │   ├── C1_D1_CORAL_prior/
│   │   ├── C4_D2_CORAL_prior/
│   │   ├── D3_fusion_equal/
│   │   ├── D4_fusion_optimal/
│   │   ├── E3_fusion_CORAL/
│   │   └── E5_fusion_CORAL_prior/
│   ├── feature_resolution/
│   │   ├── ARGUS_Final_Feature_Resolution_Report.md
│   │   ├── feature_audit.csv
│   │   ├── fig1_unique_tuples.png
│   │   ├── fig2_unique_probabilities.png
│   │   ├── fig3_probability_distributions.png
│   │   ├── fig4_boundary_zoom.png
│   │   ├── fig5_mcc_vs_threshold.png
│   │   ├── fig6_f1_vs_threshold.png
│   │   ├── fig7_fpr_vs_recall.png
│   │   ├── fig8_shap_importance.png
│   │   ├── final_comparison.csv
│   │   ├── representation_cardinality.csv
│   │   └── runtime_statistics.csv
│   ├── fusion/
│   │   ├── pc_coral_weight_optimization.csv
│   │   ├── selected_weights.json
│   │   └── weight_optimization_results.csv
│   ├── logs/
│   │   └── phase4_execution.log
│   ├── metrics/
│   │   ├── ablation_analysis.csv
│   │   ├── all_results.json
│   │   ├── component_contribution.json
│   │   ├── computational_efficiency.json
│   │   ├── final_comparison.csv
│   │   └── improvement_analysis.json
│   ├── operating_point/
│   │   ├── ARGUS_Adaptive_Operating_Point_Report.md
│   │   ├── calibration_policy_results.csv
│   │   ├── f1_vs_threshold.png
│   │   ├── final_test_results.csv
│   │   ├── fnr_vs_threshold.png
│   │   ├── fpr_vs_threshold.png
│   │   ├── mcc_vs_threshold.png
│   │   ├── precision_recall.png
│   │   ├── threshold_metrics.xlsx
│   │   └── threshold_sweep.csv
│   ├── plots/
│   │   ├── component_contribution.png
│   │   ├── f1_progression.png
│   │   ├── mcc_progression.png
│   │   └── weight_optimization.png
│   ├── prior_correction/
│   │   └── prior_estimation.json
│   ├── probability_audit/
│   │   ├── ARGUS_Probability_Audit.md
│   │   ├── high_res_threshold_sweep.csv
│   │   ├── plot_a_hist_calib.png
│   │   ├── plot_b_hist_test.png
│   │   ├── plot_c_zoomed_hist.png
│   │   ├── plot_d_ecdf.png
│   │   ├── plot_e_mcc_high_res.png
│   │   ├── plot_f_recall_high_res.png
│   │   └── stage_probability_stats.csv
│   ├── .DS_Store
│   ├── adaptive_operating_point.py
│   ├── ARGUS_Final_Feature_Resolution.xlsx
│   ├── ARGUS_Phase4_Final_Report.md
│   ├── ARGUS_Phase4_Judge_Summary.md
│   ├── ARGUS_Phase4_Results.xlsx
│   ├── audit_probability_output.py
│   └── generate_phase4_reports.py
├── prompts/
│   └── decision_support_system_prompt.txt
├── results/
│   ├── ARGUS_POSTER_DATA_PACKAGE/
│   │   ├── figures/
│   │   ├── graphs/
│   │   ├── argus_agents.csv
│   │   ├── dataset_statistics.csv
│   │   ├── feature_summary.csv
│   │   ├── optional_components_status.md
│   │   ├── poster_results.csv
│   │   ├── POSTER_RESULTS_SUMMARY.md
│   │   └── shap_feature_importance.csv
│   ├── poster_figures/
│   │   └── confusion_matrices/
│   ├── poster_graph_data/
│   │   ├── 01_cross_domain_f1.csv
│   │   ├── 02_cross_domain_mcc.csv
│   │   ├── 03_fpr_fnr.csv
│   │   ├── 04_runtime.csv
│   │   └── 05_domain_transfer.csv
│   ├── argus_agents.csv
│   ├── dataset_statistics.csv
│   ├── feature_summary.csv
│   ├── optional_components_status.md
│   ├── poster_results.csv
│   ├── POSTER_RESULTS_SUMMARY.md
│   └── shap_feature_importance.csv
├── risk_agent/
│   └── __pycache__/
│       └── main.cpython-314.pyc
├── scratch/
│   └── run_1011.sh
├── scripts/
│   ├── download_model.sh
│   ├── final_eval.py
│   ├── fit_fusion.py
│   ├── format_results.py
│   ├── health_check.sh
│   ├── init_db.py
│   ├── localhost_test.sh
│   ├── seed_data.py
│   ├── start_local.sh
│   └── test_clean_clone.sh
├── src/
│   └── argus/
│       ├── __pycache__/
│       ├── agents/
│       ├── api/
│       ├── blackboard/
│       ├── bus/
│       ├── core/
│       ├── integrations/
│       ├── memory/
│       ├── monitoring/
│       ├── observability/
│       ├── orchestrator/
│       ├── policy/
│       ├── registry/
│       ├── schemas/
│       ├── security/
│       ├── services/
│       ├── tools/
│       ├── utils/
│       ├── __init__.py
│       └── main.py
├── streaming/
│   └── __pycache__/
│       ├── replay_producer.cpython-314.pyc
│       └── stream_consumer.cpython-314.pyc
├── tests/
│   ├── agents/
│   │   └── test_data_intelligence.py
│   ├── core/
│   │   └── test_trace.py
│   ├── data/
│   │   └── 1_percent_sample.parquet
│   ├── e2e/
│   │   ├── __init__.py
│   │   ├── test_day3.py
│   │   └── test_end_to_end.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── events.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_pipeline.py
│   ├── policy/
│   │   └── test_policy.py
│   ├── schemas/
│   │   └── test_event.py
│   ├── security/
│   │   └── test_security_audit.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── test_incident_service.py
│   │   ├── test_orchestrator.py
│   │   └── test_streaming.py
│   └── unit/
│       ├── __init__.py
│       ├── test_core_logic.py
│       └── test_drift.py
├── TF_ToN_IoT_LightGBM_Final/
│   ├── configs/
│   ├── data/
│   ├── models/
│   │   ├── experiment_config.json
│   │   ├── feature_names.json
│   │   ├── lightgbm_booster.txt (26.39 MB)
│   │   └── lightgbm_gpu.pkl (26.46 MB)
│   ├── outputs/
│   │   ├── confusion_matrix/
│   │   ├── errors/
│   │   ├── feature_importance/
│   │   ├── figures/
│   │   ├── logs/
│   │   ├── metrics/
│   │   ├── precision_recall/
│   │   ├── report/
│   │   ├── roc_curve/
│   │   ├── shap/
│   │   └── threshold/
│   └── .DS_Store
├── TF_ToN_IoT_XGBoost/
│   ├── configs/
│   ├── data/
│   ├── models/
│   │   ├── xgboost_model.json (21.05 MB)
│   │   └── xgboost_model.pkl (13.08 MB)
│   ├── outputs/
│   │   ├── confusion_matrix/
│   │   ├── errors/
│   │   ├── feature_importance/
│   │   ├── figures/
│   │   ├── logs/
│   │   ├── metrics/
│   │   ├── precision_recall/
│   │   ├── report/
│   │   ├── roc_curve/
│   │   ├── shap/
│   │   └── threshold/
│   └── .DS_Store
├── training/
│   ├── __pycache__/
│   │   ├── __init__.cpython-311.pyc
│   │   └── __init__.cpython-314.pyc
│   ├── archive_leaked_run/
│   │   ├── __init__.py
│   │   ├── catboost.cbm
│   │   ├── CatBoost_confusion_matrix.pdf
│   │   ├── CatBoost_confusion_matrix.png
│   │   ├── CatBoost_confusion_matrix.svg
│   │   ├── CatBoost_norm_confusion_matrix.pdf
│   │   ├── CatBoost_norm_confusion_matrix.png
│   │   ├── CatBoost_norm_confusion_matrix.svg
│   │   ├── CatBoost_pr_curve.pdf
│   │   ├── CatBoost_pr_curve.png
│   │   ├── CatBoost_pr_curve.svg
│   │   ├── CatBoost_roc_curve.pdf
│   │   ├── CatBoost_roc_curve.png
│   │   ├── CatBoost_roc_curve.svg
│   │   ├── CatBoost_shap_bar.pdf
│   │   ├── CatBoost_shap_bar.png
│   │   ├── CatBoost_shap_bar.svg
│   │   ├── CatBoost_shap_summary.pdf
│   │   ├── CatBoost_shap_summary.png
│   │   ├── CatBoost_shap_summary.svg
│   │   ├── dataset_report.xlsx
│   │   ├── encoders.pkl
│   │   ├── leaderboard.csv
│   │   ├── lightgbm.txt
│   │   ├── LightGBM_confusion_matrix.pdf
│   │   ├── LightGBM_confusion_matrix.png
│   │   ├── LightGBM_confusion_matrix.svg
│   │   ├── LightGBM_norm_confusion_matrix.pdf
│   │   ├── LightGBM_norm_confusion_matrix.png
│   │   ├── LightGBM_norm_confusion_matrix.svg
│   │   ├── LightGBM_pr_curve.pdf
│   │   ├── LightGBM_pr_curve.png
│   │   ├── LightGBM_pr_curve.svg
│   │   ├── LightGBM_roc_curve.pdf
│   │   ├── LightGBM_roc_curve.png
│   │   ├── LightGBM_roc_curve.svg
│   │   ├── LightGBM_shap_bar.pdf
│   │   ├── LightGBM_shap_bar.png
│   │   ├── LightGBM_shap_bar.svg
│   │   ├── LightGBM_shap_summary.pdf
│   │   ├── LightGBM_shap_summary.png
│   │   ├── LightGBM_shap_summary.svg
│   │   ├── metadata.json
│   │   ├── model.cbm
│   │   ├── model.txt
│   │   ├── model_exporter.py
│   │   ├── nn_training_log.csv
│   │   ├── Phase2_Summary.md
│   │   ├── Random Forest_confusion_matrix.pdf
│   │   ├── Random Forest_confusion_matrix.png
│   │   ├── Random Forest_confusion_matrix.svg
│   │   ├── Random Forest_norm_confusion_matrix.pdf
│   │   ├── Random Forest_norm_confusion_matrix.png
│   │   ├── Random Forest_norm_confusion_matrix.svg
│   │   ├── Random Forest_pr_curve.pdf
│   │   ├── Random Forest_pr_curve.png
│   │   ├── Random Forest_pr_curve.svg
│   │   ├── Random Forest_roc_curve.pdf
│   │   ├── Random Forest_roc_curve.png
│   │   ├── Random Forest_roc_curve.svg
│   │   ├── Random Forest_shap_bar.pdf
│   │   ├── Random Forest_shap_bar.png
│   │   ├── Random Forest_shap_bar.svg
│   │   ├── Random Forest_shap_summary.pdf
│   │   ├── Random Forest_shap_summary.png
│   │   ├── Random Forest_shap_summary.svg
│   │   ├── random_forest.joblib
│   │   ├── scaler.pkl
│   │   ├── training_results.xlsx
│   │   ├── xgboost.json
│   │   ├── XGBoost_confusion_matrix.pdf
│   │   ├── XGBoost_confusion_matrix.png
│   │   ├── XGBoost_confusion_matrix.svg
│   │   ├── XGBoost_norm_confusion_matrix.pdf
│   │   ├── XGBoost_norm_confusion_matrix.png
│   │   ├── XGBoost_norm_confusion_matrix.svg
│   │   ├── XGBoost_pr_curve.pdf
│   │   ├── XGBoost_pr_curve.png
│   │   ├── XGBoost_pr_curve.svg
│   │   ├── XGBoost_roc_curve.pdf
│   │   ├── XGBoost_roc_curve.png
│   │   ├── XGBoost_roc_curve.svg
│   │   ├── XGBoost_shap_bar.pdf
│   │   ├── XGBoost_shap_bar.png
│   │   ├── XGBoost_shap_bar.svg
│   │   ├── XGBoost_shap_summary.pdf
│   │   ├── XGBoost_shap_summary.png
│   │   └── XGBoost_shap_summary.svg
│   ├── configs/
│   │   ├── catboost.yaml
│   │   ├── default.yaml
│   │   ├── domain_adaptation.yaml
│   │   ├── lightgbm.yaml
│   │   ├── neural_network.yaml
│   │   ├── random_forest.yaml
│   │   ├── semantic_map.yaml
│   │   └── xgboost.yaml
│   ├── data/
│   │   ├── processed/
│   │   ├── raw/
│   │   ├── __init__.py
│   │   ├── csv_loader.py
│   │   └── dataset_inspector.py
│   ├── evaluation/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── domain_eval.py
│   │   └── evaluator.py
│   ├── exports/
│   │   ├── ciciot2023/
│   │   ├── domain_adaptation/
│   │   ├── exp_nftoniotv2_nftoniotv2/
│   │   ├── nftoniotv2/
│   │   ├── encoders.pkl
│   │   ├── metadata.json
│   │   ├── Phase2_Summary.md
│   │   ├── random_forest.joblib (12.70 MB)
│   │   └── scaler.pkl
│   ├── feature_engineering/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── feature_aligner.py
│   │   └── feature_engineer.py
│   ├── feature_selection/
│   │   ├── __init__.py
│   │   └── feature_selector.py
│   ├── graphs/
│   │   └── .gitkeep
│   ├── logs/
│   │   └── .gitkeep
│   ├── notebooks/
│   │   └── .gitkeep
│   ├── preprocessing/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── preprocessor.py
│   ├── reports/
│   │   ├── eda/
│   │   ├── figures/
│   │   ├── shap/
│   │   ├── .DS_Store
│   │   ├── __init__.py
│   │   ├── leaderboard.csv
│   │   ├── report_generator.py
│   │   └── training_results.xlsx
│   ├── scripts/
│   │   ├── __pycache__/
│   │   ├── domain_adaptation_experiment.py
│   │   ├── domain_adaptation_report.py
│   │   ├── phase2_execute.py
│   │   ├── phase3_execute.py
│   │   ├── phase3_execute_all.py
│   │   ├── phase3_execute_all_fast.py
│   │   ├── phase4_report.py
│   │   ├── preprocess_ciciot.py
│   │   └── sanity_check.py
│   ├── tests/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── test_cli.py
│   │   ├── test_config.py
│   │   ├── test_dann_model.py
│   │   ├── test_feature_aligner.py
│   │   ├── test_folder_structure.py
│   │   ├── test_gradient_reversal.py
│   │   ├── test_preprocessing.py
│   │   └── test_trainers.py
│   ├── trainers/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── base_trainer.py
│   │   ├── catboost_trainer.py
│   │   ├── dann_model.py
│   │   ├── gradient_reversal.py
│   │   ├── lightgbm_trainer.py
│   │   ├── neural_network_trainer.py
│   │   ├── random_forest_trainer.py
│   │   └── xgboost_trainer.py
│   ├── tuning/
│   │   ├── __init__.py
│   │   └── hyperparameter_tuner.py
│   ├── utils/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   ├── experiment_tracker.py
│   │   └── logger.py
│   ├── .DS_Store
│   ├── __init__.py
│   ├── README.md
│   └── train.py
├── verification/
│   ├── audit_and_retrain_grouped.py
│   ├── command_confound_report.md
│   ├── coral_alignment_report.md
│   ├── d3_native_config.json
│   ├── d3_native_threshold_sweep.csv
│   ├── dos_vs_semantic_confound_report.md
│   ├── duration_confound_report.md
│   ├── i_msg_ratio_leakage_check.md
│   ├── label_granularity_report.md
│   ├── leakage_audit_report.md
│   ├── leakage_audit_summary.json
│   ├── native_feature_recovery_report.md
│   ├── ollama_fallback_verification_report.md
│   ├── probability_distribution.png
│   ├── probability_distribution_report.md
│   ├── protocol_aware_feature_report.md
│   ├── protocol_aware_summary.json
│   ├── reproducibility_report.md
│   ├── shap_query_retrieval_report.md
│   ├── threshold_reconciliation_report.md
│   ├── train_d3_native.py
│   ├── train_d3_protocol_aware.py
│   └── u_message_shortcut_investigation_report.md
├── ._.gitignore
├── ._ARGUS_NR04_NATIVE_DELIVERABLES.zip
├── ._ARGUS_REP01_DELIVERABLES.zip
├── ._README.md
├── .dockerignore
├── .DS_Store
├── .env.example
├── .gitignore
├── append_images.py
├── ARGUS_NR04_NATIVE_DELIVERABLES.zip
├── ARGUS_paper_v2_representation_resolution.docx
├── ARGUS_REP01_DELIVERABLES.zip (15.26 MB)
├── audit_ton_iot.py
├── compile_multiseed.py
├── compute_entropy.py
├── compute_shap.py
├── create_sample.py
├── DAY_1_REPORT.md
├── DAY_3_REPORT.md
├── DAY_5_REPORT.md
├── Dockerfile
├── entropy_results.txt
├── evaluate_agent_contribution.py
├── evaluate_risk.py
├── evaluate_risk_analysis.py
├── fix_all_paths.py
├── fix_paths.py
├── fix_routers.py
├── format_dann.py
├── FUSION_PLAN.md
├── generate_d1_d2_baselines.py
├── generate_figures.py
├── generate_final_report.py
├── generate_multiseed_figures.py
├── generate_phase3.py
├── generate_phase4_report.py
├── generate_poster.py
├── generate_provenance.py
├── generate_rest.py
├── generate_token.py
├── get_cm.py
├── IDENTITY_RBAC_OIDC_READINESS_REPORT.md
├── investigate_fpr.py
├── LICENSE
├── Makefile
├── modify_docx.py
├── OIDC_JWKS_FRONTEND_SECURITY_REPORT.md
├── paper_text.txt
├── patch_decision_agent.py
├── patch_phase3.py
├── patch_phase4.py
├── PRE_COMMIT_CLASSIFICATION.md
├── pyproject.toml
├── read_docx.py
├── read_docx2.py
├── README.md
├── RECIPE.md
├── restructure.py
├── RESULTS.md
├── run_all_experiments.sh
├── run_multiseed.sh
├── run_multiseed_fast.sh
├── run_multiseed_fast2.sh
├── run_multiseed_final.sh
├── scratch_test_data.py
├── scratch_test_paths.py
├── SECURITY_HARDENING_REPORT.md
├── security_patch.py
├── temp_feature_analysis.py
├── temp_shap.py
├── temp_shift_analysis.py
├── temp_thresh.py
├── test_e2e_local.py
├── test_load.py
├── test_results.txt
├── uv.lock
├── validate_dataset.py
└── wait_for_all.sh```

---

## 2. Classification of Top-Level Folders & Files

Every top-level directory and file in the repository root has been categorized into one of seven strict classifications:

| Item Name | Type | Classification | Description / Purpose |
| :--- | :--- | :--- | :--- |
| `src/` | Folder | **SOURCE CODE** | Core ARGUS framework package (`argus.agents`, `argus.bus`, `argus.core`, `argus.orchestrator`, `argus.services`) |
| `agent/` | Folder | **SOURCE CODE** | Base agent definitions and logic |
| `api/` | Folder | **SOURCE CODE** | FastAPI application routers, endpoints, and server initializers |
| `config/` | Folder | **SOURCE CODE** | System configuration files, YAML settings, and environment specs |
| `knowledge_agent/` | Folder | **SOURCE CODE** | Knowledge Retrieval Agent module (RAG & documentation querying) |
| `orchestrator/` | Folder | **SOURCE CODE** | Agent Orchestrator engine & process coordinator |
| `risk_agent/` | Folder | **SOURCE CODE** | Risk Assessment & Evaluation Agent module |
| `streaming/` | Folder | **SOURCE CODE** | Event streaming and flow processing pipelines |
| `pyproject.toml` | File | **SOURCE CODE** | Python project build metadata and dependency specification |
| `Dockerfile` | File | **SOURCE CODE** | Containerization configuration for deployable microservices |
| `Makefile` | File | **SOURCE CODE** | Build and task automation shortcuts |
| `experiments/` | Folder | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Domain adaptation, feature resolution, and ablation experiment scripts |
| `experiment_execution/` | Folder | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Multi-seed execution harnesses, neural robustness runs, and script benchmarks |
| `scripts/` | Folder | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Result formatting, evaluation scripts, and model fitting helpers |
| `training/` | Folder | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Model trainers (XGBoost, LightGBM, DANN), config files, and training scripts |
| `verification/` | Folder | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Verification and audit scripts (`train_d3_native.py`, threshold sweeps) |
| `tests/` | Folder | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Unit and end-to-end integration tests |
| `audit_ton_iot.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Dedicated script for auditing ToN-IoT dataset splits |
| `compile_multiseed.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Multi-seed result aggregator script |
| `compute_entropy.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Information-theoretic entropy calculation script |
| `compute_shap.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | SHAP feature attribution generation script |
| `evaluate_agent_contribution.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Agent contribution evaluation harness |
| `evaluate_risk.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Risk engine evaluation script |
| `evaluate_risk_analysis.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Risk analysis validation script |
| `generate_d1_d2_baselines.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Baseline result generator script for D1->D2 transfer |
| `generate_figures.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Publication figure generation script |
| `generate_final_report.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Report generation script |
| `generate_multiseed_figures.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Multi-seed figure generation script |
| `generate_phase3.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Phase 3 evaluation generator script |
| `generate_phase4_report.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Phase 4 evaluation generator script |
| `generate_poster.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Academic poster data/figure generator script |
| `generate_provenance.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Experiment provenance tracker script |
| `generate_rest.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Auxiliary reporting script |
| `generate_token.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Security token generator helper |
| `get_cm.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Confusion matrix calculation script |
| `investigate_fpr.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | False positive rate investigation script |
| `run_all_experiments.sh` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Shell script executing full experiment suite |
| `run_multiseed*.sh` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Shell scripts running multi-seed benchmarks |
| `test_e2e_local.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Local end-to-end integration test script |
| `test_load.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | API load test script |
| `validate_dataset.py` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Dataset integrity validation script |
| `wait_for_all.sh` | File | **EXPERIMENT NOTEBOOKS/SCRIPTS** | Process sync shell helper |
| `results/` | Folder | **RESULTS (CSV/JSON/PNG)** | Consolidated experiment result tables, poster figures, and metric CSVs |
| `phase3_results/` | Folder | **RESULTS (CSV/JSON/PNG)** | Phase 3 cross-domain evaluation results, SHAP plots, predictions, and checkpoints |
| `phase4_results/` | Folder | **RESULTS (CSV/JSON/PNG)** | Phase 4 multi-source fusion, prior correction, and threshold sweep outputs |
| `ARGUS_Cross_Domain_Results/` | Folder | **RESULTS (CSV/JSON/PNG)** | Primary cross-domain benchmark results (D1->D2 CORAL, DANN, XGBoost comparison) |
| `ARGUS_D1_D2_AUDIT/` | Folder | **RESULTS (CSV/JSON/PNG)** | Audit reports and metric reconciliations for D1->D2 transfer |
| `ARGUS_D3_VALIDITY_AUDIT/` | Folder | **RESULTS (CSV/JSON/PNG)** | Data split and validity audit outputs for Domain 3 (IEC 104) |
| `ARGUS_HEALTH_CHECK/` | Folder | **RESULTS (CSV/JSON/PNG)** | Infrastructure and pipeline health diagnostic outputs |
| `ARGUS_PAPER_READINESS_AUDIT/` | Folder | **RESULTS (CSV/JSON/PNG)** | Scientific readiness audit reports and gap analyses |
| `entropy_results.txt` | File | **RESULTS (CSV/JSON/PNG)** | Entropy computation summary output file |
| `test_results.txt` | File | **RESULTS (CSV/JSON/PNG)** | Test suite execution summary output file |
| `models/` | Folder | **MODEL ARTIFACTS** | Serialized model files (`model.joblib`, `model_d2_coral.txt`) |
| `TF_ToN_IoT_LightGBM_Final/` | Folder | **MODEL ARTIFACTS** | Trained LightGBM booster model (`lightgbm_booster.txt`, `lightgbm_gpu.pkl`) & outputs |
| `TF_ToN_IoT_XGBoost/` | Folder | **MODEL ARTIFACTS** | Trained XGBoost model (`xgboost_model.json`, `xgboost_model.pkl`) & outputs |
| `LightGBM_CICIoT2023_Backup/` | Folder | **MODEL ARTIFACTS** | Backup LightGBM models trained on CICIoT2023 (`lightgbm_best_model.joblib`, `.pkl`) |
| `catboost_info/` | Folder | **MODEL ARTIFACTS** | CatBoost training logs and temporary model output artifacts |
| `data/` | Folder | **RAW DATA** | Raw and processed datasets (IEC104 7z/csvs, NF-ToN-IoT-v2 Parquet) |
| `BoT-IoT dataset/` | Folder | **RAW DATA** | Raw BoT-IoT dataset archive (`bot_iot_full_archive.zip` - 1.20 GB) |
| `ARGUS_Paper_Data/` | Folder | **RAW DATA** | Packaged paper deliverables, figures, and table datasets |
| `docs/` | Folder | **PAPER/DOCS** | System documentation and architecture guides |
| `prompts/` | Folder | **PAPER/DOCS** | LLM prompt templates for knowledge/risk agents |
| `README.md` | File | **PAPER/DOCS** | Project overview and quickstart guide |
| `RESULTS.md` | File | **PAPER/DOCS** | Top-level summary of empirical experiment results |
| `RECIPE.md` | File | **PAPER/DOCS** | Experimental setup and recipe recovery document |
| `FUSION_PLAN.md` | File | **PAPER/DOCS** | Plan for model fusion and prior correction experiments |
| `DAY_1_REPORT.md` | File | **PAPER/DOCS** | Day 1 execution report |
| `DAY_3_REPORT.md` | File | **PAPER/DOCS** | Day 3 execution report |
| `DAY_5_REPORT.md` | File | **PAPER/DOCS** | Day 5 execution report |
| `SECURITY_HARDENING_REPORT.md` | File | **PAPER/DOCS** | Infrastructure security audit and hardening report |
| `IDENTITY_RBAC_OIDC_READINESS_REPORT.md` | File | **PAPER/DOCS** | Identity & RBAC security readiness report |
| `OIDC_JWKS_FRONTEND_SECURITY_REPORT.md` | File | **PAPER/DOCS** | OIDC & JWKS frontend security assessment |
| `PRE_COMMIT_CLASSIFICATION.md` | File | **PAPER/DOCS** | Pre-commit git classification guidelines |
| `paper_text.txt` | File | **PAPER/DOCS** | Raw manuscript text draft |
| `ARGUS_paper_v2_representation_resolution.docx` | File | **PAPER/DOCS** | Word document manuscript draft on representation resolution |
| `LICENSE` | File | **PAPER/DOCS** | License file |
| `frontend/` | Folder | **SOURCE CODE** / **DEAD/TEMP** | Streamlit UI interface (`app.py`), styling, and components |
| `artifacts/` | Folder | **DEAD/DUPLICATE/TEMP** | Auxiliary execution outputs, figures, and models |
| `scratch/` | Folder | **DEAD/DUPLICATE/TEMP** | Temporary scratch space for one-off scripts and debug code |
| `.venv/` | Folder | **DEAD/DUPLICATE/TEMP** | Local Python virtual environment directory |
| `.pytest_cache/` | Folder | **DEAD/DUPLICATE/TEMP** | Pytest runtime cache directory |
| `.git/` | Folder | **DEAD/DUPLICATE/TEMP** | Git repository version control data |
| `.github/` | Folder | **DEAD/DUPLICATE/TEMP** | GitHub Actions workflows and CI configurations |
| `.dockerignore`, `.gitignore`, `.env.example`, `uv.lock` | Files | **SOURCE CODE** / **CONFIG** | Project configuration and build lockfiles |
| `._*` (`._README.md`, `._ARGUS_*.zip`) | Files | **DEAD/DUPLICATE/TEMP** | macOS split-fork metadata files |
| `.DS_Store` | File | **DEAD/DUPLICATE/TEMP** | macOS Finder metadata file |
| `ARGUS_NR04_NATIVE_DELIVERABLES.zip` | File | **DEAD/DUPLICATE/TEMP** | Duplicate ZIP archive of NR04 deliverables (6.75 MB) |
| `ARGUS_REP01_DELIVERABLES.zip` | File | **DEAD/DUPLICATE/TEMP** | Duplicate ZIP archive of REP01 deliverables (15.26 MB) |
| `fix_all_paths.py`, `fix_paths.py`, `fix_routers.py` | Files | **DEAD/DUPLICATE/TEMP** | Temporary path patching scripts |
| `patch_decision_agent.py`, `patch_phase3.py`, `patch_phase4.py` | Files | **DEAD/DUPLICATE/TEMP** | Temporary monkey-patch scripts |
| `temp_*.py` (`temp_feature_analysis.py`, etc.) | Files | **DEAD/DUPLICATE/TEMP** | One-off temporary feature and threshold analysis scripts |
| `scratch_*.py` (`scratch_test_data.py`, etc.) | Files | **DEAD/DUPLICATE/TEMP** | Temporary scratch testing scripts |
| `read_docx.py`, `read_docx2.py`, `modify_docx.py` | Files | **DEAD/DUPLICATE/TEMP** | One-off scripts for inspecting/editing docx draft |
| `security_patch.py`, `restructure.py` | Files | **DEAD/DUPLICATE/TEMP** | One-off refactoring and security patching scripts |

---

## 3. Python Entry Points & Architecture Connectivity

### A. Component Mapping & Interconnections

```
                      ┌─────────────────────────────────┐
                      │    frontend/app.py (Streamlit)  │
                      └────────────────┬────────────────┘
                                       │ REST API HTTP Calls
                                       ▼
                      ┌─────────────────────────────────┐
                      │       api/main.py (FastAPI)     │
                      └────────────────┬────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────────┐               ┌──────────────────────────────────┐
│ orchestrator/orchestrator.py  │               │ src/argus/services/orchestrator/ │
│  (Process Coordinator Engine) │               │      main.py (Microservice)      │
└───────────────┬───────────────┘               └─────────────────┬────────────────┘
                │ Event Bus Pub/Sub                               │ Async HTTP
                ▼                                                 ▼
┌───────────────────────────────┐               ┌──────────────────────────────────┐
│      src/argus/bus/           │               │     Autonomous Agent Modules     │
│   memory.py / redis.py        │◄─────────────►│  • Data Intelligence Agent       │
│    (Message Bus Engine)       │               │  • Risk Assessment Agent         │
└───────────────────────────────┘               │  • Knowledge Retrieval Agent     │
                                                └──────────────────────────────────┘
```

1. **Streamlit Interface**:
   - `frontend/app.py`: Interactive user dashboard for monitoring threats, querying knowledge base, displaying SHAP attributions, and viewing risk assessment metrics.
2. **FastAPI Applications**:
   - `api/main.py`: Primary REST API server mounting endpoint routers (`api/routers/auth.py`, `analysis.py`, `decisions.py`, `agents.py`, `health.py`, `streaming.py`).
   - `src/argus/services/orchestrator/main.py`: Standalone microservice FastAPI app for orchestrator agent management (`app = FastAPI(...)`).
   - `src/argus/services/risk_assessment/main.py`: Standalone microservice FastAPI app for risk evaluation (`app = FastAPI(...)`).
3. **Orchestrator**:
   - `orchestrator/orchestrator.py` & `src/argus/orchestrator/engine.py`: Core pipeline manager that receives security event models (`SecurityEvent`), delegates tasks to specialized sub-agents, monitors status, and aggregates final risk decisions.
4. **Autonomous Agents**:
   - `agent/agent.py` & `src/argus/agents/base.py`: Base agent class definition.
   - `src/argus/agents/data_intelligence/agent.py`: Extracts statistical features from raw telemetry using `src/argus/agents/data_intelligence/tools/feature_extractor.py`.
   - `risk_agent/risk_agent.py` & `src/argus/agents/risk_assessment/agent.py`: Evaluates threat level, severity, and risk scores.
   - `knowledge_agent/knowledge_agent.py` & `src/argus/agents/knowledge_retrieval/agent.py`: Queries security domain knowledge base via RAG.
5. **Message Bus**:
   - `src/argus/bus/memory.py`: In-memory pub/sub message bus (`InMemoryMessageBus`).
   - `src/argus/bus/redis.py`: Redis-backed event bus for asynchronous inter-agent communication.

### B. Complete List of Files Importing Streamlit

Search query: `import streamlit` / `from streamlit` across entire codebase (excluding `.venv`):
- **`frontend/app.py`** (Line 3: `import streamlit as st`)

*No other file in the repository imports Streamlit.*

---

## 4. Location & Paths of Key System Artifacts

| Artifact Category | Description | Exact Repository File Paths |
| :--- | :--- | :--- |
| **Trained XGBoost / LightGBM Models** | Serialized gradient boosting models | • `LightGBM_CICIoT2023_Backup/model/lightgbm_best_model.joblib` (108.14 MB)<br>• `LightGBM_CICIoT2023_Backup/model/lightgbm_best_model.pkl` (108.14 MB)<br>• `LightGBM_CICIoT2023_Backup/model/lightgbm_best_model.txt` (108.14 MB)<br>• `TF_ToN_IoT_XGBoost/models/xgboost_model.json` (21.05 MB)<br>• `TF_ToN_IoT_XGBoost/models/xgboost_model.pkl` (13.08 MB)<br>• `TF_ToN_IoT_LightGBM_Final/models/lightgbm_booster.txt` (26.39 MB)<br>• `TF_ToN_IoT_LightGBM_Final/models/lightgbm_gpu.pkl` (26.46 MB)<br>• `phase3_results/models/model_d1_coral.txt`<br>• `phase3_results/models/model_d2_coral.txt`<br>• `models/model_d2_coral.txt`<br>• `models/best_model/model.joblib` (12.70 MB)<br>• `training/exports/exp_nftoniotv2_nftoniotv2/models/XGBoost.json` & `LightGBM.txt` |
| **CORAL Transform Parameters** | Covariance alignment parameters | • `ARGUS_Cross_Domain_Results/argus_coral_data/coral_parameters.npz` (D1->D2 parameters)<br>• `phase3_results/checkpoints/coral_d1_d3_parameters.npz`<br>• `phase3_results/checkpoints/coral_d2_d3_parameters.npz` |
| **DANN Checkpoint** | Domain Adversarial Neural Network PyTorch weights | • `ARGUS_Cross_Domain_Results/argus_coral_data/dann_results/dann_best_model.pt` (D1->D2 DANN)<br>• `phase3_results/checkpoints/dann_d1_d3_checkpoint.pt` (D1->D3 DANN)<br>• `phase3_results/checkpoints/dann_d2_d3_checkpoint.pt` (D2->D3 DANN)<br>• `training/exports/domain_adaptation/nftoniotv2_to_ciciot2023/models/dann_model.pt` |
| **Four-Feature Extraction Code** | Feature extraction implementations (`pkt_mean_to_max`, `log_pkt_mean`, `log_pkt_max`, `tcp_flag_density`) | • `src/argus/agents/data_intelligence/tools/feature_extractor.py`<br>• `verification/train_d3_native.py` (L120-L141)<br>• `RECIPE.md` (L3-L9) |
| **Threshold Metadata** | Decision threshold selection sweeps and metadata | • `ARGUS_Cross_Domain_Results/argus_coral_data/final_clean_classaware_results/threshold_metadata.csv`<br>• `ARGUS_Cross_Domain_Results/argus_coral_data/dann_results/dann_final_threshold_metadata.csv`<br>• `ARGUS_Cross_Domain_Results/argus_coral_data/dann_results/dann_calibration_threshold_sweep.csv`<br>• `TF_ToN_IoT_LightGBM_Final/outputs/threshold/threshold_results.csv`<br>• `phase4_results/operating_point/threshold_sweep.csv` & `threshold_metrics.xlsx`<br>• `verification/threshold_reconciliation_report.md` |
| **SHAP Outputs** | SHAP feature importance CSVs, summary plots, and attribution tables | • `results/shap_feature_importance.csv`<br>• `phase3_results/shap/shap_feature_importance.csv`<br>• `artifacts/figures/phase3/shap_summary_plot.png`<br>• `phase4_results/feature_resolution/fig8_shap_importance.png`<br>• `experiment_execution/figures/SHAP_vs_Target_Gain.png`<br>• `experiment_execution/tables/SHAP_vs_Target_Gain.csv`<br>• `TF_ToN_IoT_XGBoost/outputs/shap/shap_summary.png`<br>• `TF_ToN_IoT_LightGBM_Final/outputs/shap/shap_summary.png` & `shap_importance.csv` |

---

## 5. "Clean Class-aware CORAL" Technical Details

### A. Target-Domain Class Assignment Methodology
From code inspection (`ARGUS_RESULTS_README.txt`, `FINAL_D1_D2_AUDIT.md`, `RECIPE.md`, and `scripts/fit_fusion.py`):
- **Diagnostic "Class-aware CORAL"** (Post-hoc analysis): Leaked the **true ground-truth labels of the target test set** (`nfton_test_features.csv`) to compute target class-conditional mean and covariance matrices C_{t,y=0} and C_{t,y=1}. *This was strictly used for post-hoc upper-bound diagnostic analysis and is flagged as test-label leakage.*
- **"Clean Class-aware CORAL"** (Leakage-Controlled): Used **true ground-truth labels from the target adaptation split** (`nfton_train_adaptation.csv` / `ciciot_train_clean_class_aware_coral.csv`). Class-conditional statistics were estimated exclusively on the adaptation split (a labeled subset of target training data), and the optimal decision boundary (theta* = 0.99) was selected strictly on the **target calibration split** (`nfton_train_calibration.csv`) to maximize MCC. **No test set labels or test set feature statistics were accessed during covariance estimation or threshold selection.**

### B. NF-ToN Split Specification
The NF-ToN-IoT-v2 dataset was split into three strictly isolated partitions using iterative stratified splitting (`train_test_split(..., test_size=0.80, random_state=42, stratify=y)`):
1. **Target Adaptation Split**: N = 8,406,962 rows (80% of train set, 72.58% attack prior). Used for CORAL class-conditional covariance estimation.
2. **Target Calibration Split**: N = 2,101,742 rows (20% of train set, 72.58% attack prior). Used for decision threshold selection (theta* = 0.99).
3. **Frozen Target Test Split**: N = 2,627,177 rows (`nfton_test_features.csv`, 72.58% attack prior). Reserved strictly for final frozen model evaluation.

---

## 6. Duplicate Result Files & Authoritative Identification

| Duplicate Group | File Paths | Authoritative File | Rationale / Resolution |
| :--- | :--- | :--- | :--- |
| **Five-Model Metric Summaries** | • `ARGUS_Cross_Domain_Results/argus_coral_data/final_five_model_comparison/best_model_by_metric.csv`<br>• `ARGUS_Cross_Domain_Results/argus_coral_data/final_model_comparison/best_model_by_metric.csv` | `final_five_model_comparison/best_model_by_metric.csv` | Contains the complete comparison across all 5 models (Source-only, Global CORAL, Diagnostic Class-aware CORAL, Clean Class-aware CORAL, DANN). |
| **Five-Model Ranking Tables** | • `ARGUS_Cross_Domain_Results/argus_coral_data/final_five_model_comparison/five_model_complete_comparison.csv`<br>• `ARGUS_Cross_Domain_Results/argus_coral_data/FINAL_five_model_comparison.csv` | `final_five_model_comparison/five_model_complete_comparison.csv` | Full bit-for-bit verified metric table matching raw per-sample DANN prediction recomputations. |
| **DANN Evaluation Conflict** | • `ARGUS_RESULTS_README.txt` (Result Set A: ROC-AUC = 0.5226)<br>• `ARGUS_Cross_Domain_Results/argus_coral_data/dann_results/dann_final_test_metrics.csv` & `dann_final_test_predictions.csv` (Result Set B: ROC-AUC = 0.3321) | **Result Set B** (`dann_final_test_metrics.csv` & `dann_final_test_predictions.csv`) | Independent recomputation directly from the 2,627,178 raw per-sample predictions (`dann_final_test_predictions.csv`) yields Result Set B bit-for-bit (ROC-AUC=0.332096, MCC=0.012855, F1=0.841157). Result Set A in `ARGUS_RESULTS_README.txt` is an invalid/superseded draft transcription error. |
| **Domain Adaptation (DA01) Deliverables** | • `experiment_execution/neural_robustness/domain_adaptation/tables/DA01_*.csv`<br>• `experiment_execution/neural_robustness/domain_adaptation/ARGUS_DA01_CORAL_DELIVERABLES/tables/DA01_*.csv` | `ARGUS_DA01_CORAL_DELIVERABLES/` | Canonical packaged release folder for DA01 domain adaptation deliverables. |
| **Representation Extension (REP01) Tables** | • `experiment_execution/neural_robustness/representation_extension/tables/REP01_*.csv`<br>• `ARGUS_Paper_Data/2_REP01_Deliverables/tables/REP01_*.csv` | `ARGUS_Paper_Data/2_REP01_Deliverables/` | Canonical packaged release folder for REP01 deliverables. |
| **IEC104 Extracted Feature Datasets** | • `data/IEC104/processed/iec104_test_features.csv` (32.11 MB)<br>• `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv` (32.11 MB) | Identical files | Both files are bit-for-bit identical (N = 714,453). |

---

## 7. Proposed Cleanup List (No Execution Performed)

### A. Files Safe to Delete
*These files represent temporary scratch space, dead code, macOS split-fork metadata, or build/test runtime caches:*

1. **macOS Metadata & Split-Fork Files**:
   - `._.gitignore`, `._ARGUS_NR04_NATIVE_DELIVERABLES.zip`, `._ARGUS_REP01_DELIVERABLES.zip`, `._README.md`, `.DS_Store`
   - `experiment_execution/neural_robustness/representation_extension/figures/._*`
   - `experiment_execution/neural_robustness/native_high_performance/figures/._*`, `tables/._*`
2. **Temporary Scratch Scripts at Root**:
   - `temp_feature_analysis.py`, `temp_shap.py`, `temp_shift_analysis.py`, `temp_thresh.py`
   - `scratch_test_data.py`, `scratch_test_paths.py`
   - `read_docx.py`, `read_docx2.py`, `modify_docx.py`
   - `create_sample.py`, `append_images.py`
3. **Root Build / Test Scratch Outputs**:
   - `entropy_results.txt`, `test_results.txt`
4. **Temporary Caches**:
   - `.pytest_cache/`, `catboost_info/`

### B. Files Safe to Archive
*These files contain large redundant binary archives, intermediate predictions, or backup models that are preserved elsewhere:*

1. **Duplicate / Redundant ZIP Archives**:
   - `ARGUS_NR04_NATIVE_DELIVERABLES.zip` (6.75 MB)
   - `ARGUS_REP01_DELIVERABLES.zip` (15.26 MB)
   - `BoT-IoT dataset/bot_iot_full_archive.zip` (1.20 GB)
2. **Backup / Redundant Large Model Files**:
   - `LightGBM_CICIoT2023_Backup/` (3x 108 MB duplicate `.joblib`, `.pkl`, `.txt` files)
3. **Intermediate Large Prediction CSVs**:
   - `experiment_execution/predictions/EXP01/*.csv`, `EXP04/*.csv`, `EXP05/*.csv` (14–15 MB each)
   - `phase3_results/experiments/*/*.csv` (11–17 MB each)
4. **Unused Virtual Environment Directory**:
   - `.venv/` (Can be regenerated reproducibly via `uv sync` or `pyproject.toml`)

### C. Files Unsure About (User Decision Required)
*These files may be actively used or required for current manuscript preparation:*

1. `ARGUS_paper_v2_representation_resolution.docx` (1.12 MB): Active manuscript draft in Word format.
2. `ARGUS_D1_D2_AUDIT/`, `ARGUS_D3_VALIDITY_AUDIT/`, `ARGUS_HEALTH_CHECK/`, `ARGUS_PAPER_READINESS_AUDIT/`: Diagnostic audit folders containing historical evidence logs.
3. `BoT-IoT dataset/`: Extracted flow directory; need confirmation if BoT-IoT benchmarking is actively planned.
4. `training/archive_leaked_run/`: Historical training outputs from early runs kept for provenance verification.

---
