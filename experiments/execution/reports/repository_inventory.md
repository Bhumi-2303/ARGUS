# ARGUS Repository Component & Artifact Inventory

This inventory documents all pre-existing datasets, model checkpoints, feature pipelines, metric scripts, and experiment outputs across the repository to determine validity and reusability for the paper evidence package.

| Component | Repository Location | Existing Status | Reusable? | Reason / Action |
| :--- | :--- | :---: | :---: | :--- |
| **D1: CICIoT2023 Dataset** | `ARGUS_Cross_Domain_Results/argus_coral_data/ciciot_*.csv` | Clean (5.49M train, 1.18M test) | **YES** | Exact frozen partition with 4 harmonized features + label. |
| **D2: NF-ToN-IoT-v2 Dataset** | `ARGUS_Cross_Domain_Results/argus_coral_data/nfton_*.csv` | Clean (10.51M train, 2.63M test) | **YES** | Exact frozen partition with 4 harmonized features + label. |
| **D3: IEC 60870-5-104 Dataset** | `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_*.csv` | Clean (2.29M adapt, 571k calib, 714k test) | **YES** | Strict 3-way partition isolation; test partition completely frozen. |
| **D3: Raw SCADA Flow CSVs** | `data/IEC104/extracted_csvs/` | Clean (12 attack directories, 84 columns) | **YES** | Used for 73-feature Native SCADA model training. |
| **D1 In-Domain Model** | `LightGBM_CICIoT2023_Backup/model/` | LightGBM text & pkl dumps (>99% acc) | **YES** | Establishes in-domain baseline context (>99.3%). |
| **D2 In-Domain Model** | `TF_ToN_IoT_LightGBM_Final/models/` | LightGBM text & pkl dumps (>99.5% acc) | **YES** | Establishes in-domain baseline context (>99.5%). |
| **D3 Native Model** | `phase3_results/models/model_d3_native.txt` | LightGBM booster (73 features) | **YES** | Re-run across 5 seeds to generate mu +/- sigma summary. |
| **D1 -> D3 Transfer Baseline** | `phase3_results/models/model_d1_baseline.txt` | Single-seed checkpoint (seed=42) | **YES** | Re-run across 5 seeds (42, 123, 456, 789, 1011). |
| **D2 -> D3 Transfer Baseline** | `phase3_results/models/model_d2_baseline.txt` | Single-seed checkpoint (seed=42) | **YES** | Re-run across 5 seeds (42, 123, 456, 789, 1011). |
| **CORAL Transformation Matrix** | `ARGUS_Cross_Domain_Results/argus_coral_data/coral_parameters.npz` | Fitted on D3 adaptation set | **YES** | Valid covariance alignment on target unlabeled data. |
| **D1 -> D3 CORAL Model** | `phase3_results/models/model_d1_coral.txt` | Single-seed LightGBM checkpoint | **YES** | Re-run across 5 seeds. |
| **D2 -> D3 CORAL Model** | `phase3_results/models/model_d2_coral.txt` | Single-seed LightGBM checkpoint | **YES** | Re-run across 5 seeds. |
| **DANN Adversarial Models** | `phase3_results/checkpoints/dann_*.pt` | PyTorch checkpoints (epochs 1-10) | **YES** | 10-epoch checkpoints available for inference. |
| **Prior Shift Correction** | `phase4_results/phase4_execute.py` | Vectorized Bayesian formula | **YES** | Vectorized numpy function; deterministic and mathematically exact. |
| **Threshold Calibration** | `phase3_results/validate_metrics.py` | Grid search on D3 calibration set | **YES** | Selects threshold on calibration split only; evaluates on test. |
| **SHAP Explainer Artifacts** | `phase3_results/shap/` | TreeExplainer values and plots | **YES** | Deterministic values on source LightGBM trees. |
| **Corrupted XGBoost CSV** | `TF_ToN_IoT_XGBoost/outputs/metrics/metrics.csv` | Corrupted with function object string | **NO** | Needs regeneration with scalar numerical float values. |
| **Feature Resolution (6/8)** | `phase4_results/feature_resolution/` | Broken run (all zero predictions) | **NO** | Re-implement in EXP-07 with verified feature scaling. |
| **Multi-Agent Stubs** | `src/argus/agents/` | Software stubs / placeholders | **NO** | Excluded from ML empirical benchmark paper scope. |
