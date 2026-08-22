import os, json, yaml
from pathlib import Path

BASE = Path('/Users/tirthkosambia/Documents/ARGUS')
EE = BASE / 'experiment_execution'

# 1. Repository Inventory Report
inv_content = """# ARGUS Repository Component & Artifact Inventory

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
"""
(EE / 'reports/repository_inventory.md').write_text(inv_content)

# 2. Experiment Manifest YAML
manifest = {
    'project_name': 'ARGUS_Empirical_Evidence_Pipeline',
    'version': '1.0.0',
    'dataset_versions': {
        'D1': {'name': 'CICIoT2023', 'total_rows': 6668822, 'attack_prior': 0.976421},
        'D2': {'name': 'NF-ToN-IoT-v2', 'total_rows': 13135881, 'attack_prior': 0.725844},
        'D3': {'name': 'IEC 60870-5-104', 'total_rows': 3572265, 'attack_prior': 0.224734}
    },
    'feature_sets': {
        'ARGUS-4': ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max'],
        'ARGUS-6': ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max', 'log_tot_pkts', 'log_flow_duration'],
        'ARGUS-8': ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max', 'log_tot_pkts', 'log_flow_duration', 'log_pkt_std', 'log_pkt_min'],
        'Native-73': '73_CIC_Flow_Features'
    },
    'splits': {
        'D1': {'train': 5491971, 'test': 1176851},
        'D2': {'train': 10508704, 'test': 2627177, 'adaptation': 8406962, 'calibration': 2101742},
        'D3': {'train_total': 2857812, 'adaptation': 2286249, 'calibration': 571563, 'test': 714453}
    },
    'seeds': [42, 123, 456, 789, 1011],
    'models': {
        'lightgbm': {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'learning_rate': 0.05,
            'num_leaves': 31,
            'max_depth': 6,
            'min_child_samples': 20,
            'num_boost_round': 200,
            'verbose': -1
        }
    },
    'metrics': ['accuracy', 'precision', 'recall', 'f1', 'macro_f1', 'fpr', 'fnr', 'mcc', 'roc_auc', 'pr_auc', 'log_loss', 'brier_score'],
    'operational_fpr_constraints': [0.001, 0.005, 0.01, 0.05, 'unconstrained'],
    'experiments': {
        'EXP-01': 'Multi-Seed Transfer Baseline & Dummy Comparison',
        'EXP-02': 'Bayesian Prior-Shift Deconstruction Matrix',
        'EXP-03': 'Representation State-Space Cardinality & Entropy Audit',
        'EXP-04': 'Native SCADA Performance Ceiling Benchmark',
        'EXP-05': 'Multi-Seed Domain Adaptation & Multi-Source Fusion Benchmark',
        'EXP-06': 'Operational Constrained False-Alarm Operating Point Evaluation',
        'EXP-07': 'Repaired Feature-Resolution Expansion Sweep (4 vs 6 vs 8 vs 73)'
    }
}
with open(EE / 'configs/experiment_manifest.yaml', 'w') as f:
    yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

print('[OK] Step 1 Inventory & Step 2 Manifest generated.')
