#!/usr/bin/env python3
"""
ARGUS Machine-Readable Journal Experiment Registry Generator
Creates:
- configs/experiment_registry.json
- tables/experiment_registry.csv
"""

import json
from pathlib import Path
import pandas as pd

REGISTRY = [
    {
        "id": "EXP-01",
        "name": "Feature Leakage & Target Validity Forensic Audit",
        "category": "Validity Audit",
        "hypothesis": "No target-label proxy, session identifier, or post-shuffle feature exists in verified cross-domain schemas; any high-AUC anomaly is attributable to identifiable leakage mechanisms.",
        "prerequisites": "Dataset manifests, column definitions, D1/D2/D3 feature files, raw prediction files.",
        "dataset_and_split": "D1 (5.49M train, 1.18M test), D2 (10.51M train, 8.41M adapt, 2.10M calib, 2.63M test), D3 (714K test, 47K protocol flows). Positive class = Attack (1), Benign = 0.",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp01_leakage_audit.py",
        "outputs": [
            "metrics/exp01_leakage_audit.json",
            "tables/exp01_feature_audit_matrix.csv",
            "reports/exp01_leakage_audit.md"
        ],
        "metrics": ["Feature-label mutual information", "Unique tuple cardinality", "Duplicate rate", "Leakage risk status"],
        "acceptance_criteria": "All features confirmed clean of target proxies; documented audit trail for invalidated historical features (e.g., i_msg_ratio y_sub injection in REP-01).",
        "estimated_compute": "1.5 minutes CPU, ~2 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-02",
        "name": "Temporal, Session, and Group-Disjoint Split Audit",
        "category": "Data Split Validity",
        "hypothesis": "Random i.i.d. shuffling on time-series telemetry inflates performance due to packet burst correlation; chronological and group-disjoint splits reveal true operational generalization.",
        "prerequisites": "Timestamped telemetry for D2 (ToN-IoT) and D3 (IEC 104 file captures), split manifests.",
        "dataset_and_split": "D2 timestamped flows (train/calib/test) and D3 capture sessions (file-grouped 0% overlap).",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp02_group_split_audit.py",
        "outputs": [
            "metrics/exp02_split_audit.json",
            "tables/exp02_split_comparison.csv",
            "figures/exp02_grouped_vs_random_splits.png"
        ],
        "metrics": ["ROC-AUC delta (Random vs Grouped)", "MCC delta", "Session overlap ratio"],
        "acceptance_criteria": "Quantified performance delta between random shuffle and group-disjoint evaluation across models.",
        "estimated_compute": "2 minutes CPU, ~2 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-03",
        "name": "Multi-Seed Evaluation & Uncertainty Estimation (5 Seeds)",
        "category": "Statistical Rigor",
        "hypothesis": "Model performance differences between adaptation methods are statistically significant across 5 independent seeds (42, 123, 456, 789, 1011) with non-overlapping 95% bootstrap confidence intervals.",
        "prerequisites": "D1 training set, D2 adaptation/calibration/test sets, D3 native test predictions.",
        "dataset_and_split": "D1 train (subsamples 500k per seed), D2 frozen test (2,627,177 flows), D3 frozen test (714,453 flows).",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp03_multiseed_uncertainty.py",
        "outputs": [
            "metrics/exp03_multiseed_summary.json",
            "tables/exp03_multiseed_metrics.csv",
            "tables/exp03_bootstrap_ci.csv",
            "figures/exp03_multiseed_stability_errorbars.png"
        ],
        "metrics": ["Mean ± SD (F1, MCC, ROC-AUC, Balanced Accuracy, Specificity, FPR)", "95% Bootstrap CI", "Paired t-test p-values", "Cohen's d"],
        "acceptance_criteria": "5 seeds evaluated per method; 1,000 bootstrap resamples for 95% CI on test predictions.",
        "estimated_compute": "4 minutes CPU, ~3 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-04",
        "name": "ROC, PR, Threshold Sweep, and Probabilistic Calibration Analysis",
        "category": "Operational Evaluation",
        "hypothesis": "Uncalibrated models produce deceptive F1 scores due to class imbalance; Platt/isotonic calibration restores reliability and resolves the operational FPR-recall tradeoff.",
        "prerequisites": "Raw per-sample predictions for Source-only, Global CORAL, Clean CORAL, DANN, and D3 Native.",
        "dataset_and_split": "D2 frozen test (2,627,177 flows) and D3 frozen test (714,453 flows).",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp04_calibration_roc_pr.py",
        "outputs": [
            "metrics/exp04_calibration_metrics.json",
            "tables/exp04_operational_threshold_table.csv",
            "figures/exp04_roc_curves.png",
            "figures/exp04_pr_curves.png",
            "figures/exp04_calibration_reliability.png",
            "figures/exp04_operating_fpr_vs_recall.png"
        ],
        "metrics": ["ROC-AUC", "PR-AUC", "Brier Score", "ECE (Expected Calibration Error)", "Recall @ FPR <= 0.01%, 0.1%, 1.0%, 5.0%"],
        "acceptance_criteria": "Reliability diagrams plotted with 10 bins; operating points tabulated under strict low-FPR grid SOC budgets.",
        "estimated_compute": "2.5 minutes CPU, ~3 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-05",
        "name": "Domain Shift Quantification & Covariance Alignment Validation",
        "category": "Distributional Shift",
        "hypothesis": "Cross-domain failure is driven by severe class-conditional distribution shift (KS > 0.40, high PSI) which global CORAL fails to correct while class-aware CORAL reduces.",
        "prerequisites": "Feature distributions from D1, D2, and D3, CORAL alignment transformation matrices.",
        "dataset_and_split": "D1 (CICIoT2023), D2 (NF-ToN-IoT-v2), D3 (IEC 104 SCADA), 4 harmonized features.",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp05_domain_shift_coral.py",
        "outputs": [
            "metrics/exp05_domain_shift.json",
            "tables/exp05_shift_statistics.csv",
            "figures/exp05_feature_distributions_drift.png",
            "figures/exp05_covariance_distance_matrix.png"
        ],
        "metrics": ["Kolmogorov-Smirnov statistic & p-value", "Wasserstein distance", "Jensen-Shannon divergence", "Population Stability Index (PSI)", "Frobenius norm of covariance gap"],
        "acceptance_criteria": "Shift quantified per feature marginally and class-conditionally; covariance alignment confirmed before and after CORAL.",
        "estimated_compute": "2 minutes CPU, ~2 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-06",
        "name": "Cross-Domain Benchmark Comparison (Source, CORAL, DANN, Native)",
        "category": "Benchmark Evaluation",
        "hypothesis": "Clean Class-Aware CORAL significantly outperforms Source-Only, Global CORAL, and DANN on balanced cross-domain metrics (MCC, Balanced Accuracy), while DANN collapses into majority-class prediction.",
        "prerequisites": "Verified prediction arrays on D2 test set (2.63M flows) and D3 test set (714K flows).",
        "dataset_and_split": "D2 frozen test (2,627,177 flows) and D3 frozen test (714,453 flows).",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp06_benchmark_comparison.py",
        "outputs": [
            "metrics/exp06_benchmark_comparison.json",
            "tables/exp06_primary_benchmark_table.csv",
            "tables/exp06_statistical_significance.csv",
            "figures/exp06_benchmark_comparison_bars.png",
            "figures/exp06_confusion_matrices_grid.png"
        ],
        "metrics": ["Accuracy", "Balanced Accuracy", "Precision", "Recall", "Specificity", "F1", "MCC", "ROC-AUC", "PR-AUC", "DeLong test p-value", "McNemar chi2 p-value"],
        "acceptance_criteria": "Full 11-metric evaluation on all models; formal DeLong and McNemar statistical tests computed against Source-Only baseline.",
        "estimated_compute": "2 minutes CPU, ~3 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-07",
        "name": "Full Leave-One-Component-Out Pipeline Ablation",
        "category": "Ablation Study",
        "hypothesis": "Each modular component in ARGUS (Prior Correction, Class-Aware Covariance Alignment, Calibration, Threshold Tuning) contributes non-overlapping positive deltas to balanced detection.",
        "prerequisites": "D1 training set, D2 adaptation and calibration splits.",
        "dataset_and_split": "D1 source -> D2 target adaptation/calibration/test sets.",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp07_pipeline_ablation.py",
        "outputs": [
            "metrics/exp07_ablation_results.json",
            "tables/exp07_ablation_table.csv",
            "figures/exp07_ablation_component_contributions.png"
        ],
        "metrics": ["Delta Balanced Accuracy", "Delta MCC", "Delta F1", "Delta Specificity", "Delta FPR"],
        "acceptance_criteria": "Controlled step-by-step ablation: Base, +Prior, +CORAL, +Calibration, +Threshold Optimization.",
        "estimated_compute": "3 minutes CPU, ~2.5 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-08",
        "name": "Hyperparameter Sensitivity: Fusion Weights & CORAL Regularization",
        "category": "Sensitivity Analysis",
        "hypothesis": "Optimal Bayesian fusion weights (w1, w2) and CORAL regularization strength (lambda) exhibit a convex optimum on the calibration set that generalizes smoothly to test performance without sharp instability.",
        "prerequisites": "D1 and D2 trained models, calibration set predictions, test set.",
        "dataset_and_split": "D2 calibration set (2.10M flows) for parameter search, D2 frozen test set (2.63M flows) for validation.",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp08_sensitivity_analysis.py",
        "outputs": [
            "metrics/exp08_sensitivity.json",
            "tables/exp08_fusion_weight_grid.csv",
            "tables/exp08_coral_lambda_sweep.csv",
            "figures/exp08_fusion_weight_surface.png",
            "figures/exp08_coral_regularization_curve.png"
        ],
        "metrics": ["Calibration MCC/F1", "Test MCC/F1", "Parameter stability delta"],
        "acceptance_criteria": "Grid search across lambda in [0.01, 10.0] and w1, w2 in [0.0, 1.0] step 0.1 on calibration; evaluated on test.",
        "estimated_compute": "2.5 minutes CPU, ~2.5 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-09",
        "name": "Robustness under Prior Shift, Feature Missingness, and Input Noise",
        "category": "Adversarial & Stress Testing",
        "hypothesis": "Class-aware adaptation maintains superior stability compared to source-only and DANN under synthetic perturbations: missingness (up to 25%), additive noise (sigma up to 0.25), and extreme prior shifts (2% to 90% attack).",
        "prerequisites": "Trained models, D2 test dataset.",
        "dataset_and_split": "D2 test set (stratified sample of 250,000 flows for perturbation sweeps).",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp09_robustness_stress_test.py",
        "outputs": [
            "metrics/exp09_robustness_metrics.json",
            "tables/exp09_missingness_noise_table.csv",
            "figures/exp09_missingness_degradation.png",
            "figures/exp09_feature_noise_tolerance.png",
            "figures/exp09_class_prior_shift_curve.png"
        ],
        "metrics": ["MCC degradation slope", "F1 retention ratio", "ROC-AUC robustness area"],
        "acceptance_criteria": "Controlled sweeps across missing rate in [0, 0.05, 0.10, 0.15, 0.20, 0.25], noise sigma in [0, 0.05, 0.10, 0.20, 0.30], and attack prevalence in [0.02, 0.10, 0.25, 0.50, 0.72, 0.90].",
        "estimated_compute": "3 minutes CPU, ~2.5 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-10",
        "name": "Held-Out Attack-Family & External Domain Generalization",
        "category": "Granular Attack Evaluation",
        "hypothesis": "Cross-domain models exhibit severe vulnerability to stealthy/semantic attacks (Exploits, Backdoors, SCADA commands) compared to high-volume flooding attacks (DoS, DDoS).",
        "prerequisites": "Attack family annotations from NF-ToN-IoT-v2 (DoS, DDoS, reconnaissance, backdoor, injection) and IEC 104 command categories.",
        "dataset_and_split": "NF-ToN-IoT-v2 test flows categorized by attack family; IEC 104 command vs polling flows.",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp10_attack_family_breakdown.py",
        "outputs": [
            "metrics/exp10_attack_family_metrics.json",
            "tables/exp10_attack_family_detection_rates.csv",
            "figures/exp10_attack_family_recall_comparison.png"
        ],
        "metrics": ["Per-attack-family Detection Rate (Recall)", "Precision", "False Alarm Rate on Benign background"],
        "acceptance_criteria": "Disaggregated performance across at least 5 distinct attack classes; explicit identification of detection blind spots.",
        "estimated_compute": "2 minutes CPU, ~2 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-11",
        "name": "SHAP Attribution Stability & False-Alarm Error Analysis",
        "category": "Explainability & Error Analysis",
        "hypothesis": "Feature attributions (TreeSHAP) differ radically between source-trained and target-adapted models, explaining why high-ranking source features fail on the target domain; false-alarm clusters concentrate in ambiguous packet length boundaries.",
        "prerequisites": "Trained LightGBM/XGBoost models, background reference sets from D1 and D2.",
        "dataset_and_split": "D1 and D2 evaluation sets (10,000 background samples each for exact TreeSHAP).",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp11_shap_error_analysis.py",
        "outputs": [
            "metrics/exp11_shap_stability.json",
            "tables/exp11_shap_importance_ranking.csv",
            "tables/exp11_false_positive_clusters.csv",
            "figures/exp11_shap_rank_correlation.png",
            "figures/exp11_false_alarm_feature_distributions.png"
        ],
        "metrics": ["Mean absolute SHAP value per feature", "Spearman rank correlation (rho)", "False-positive cluster centroid distances"],
        "acceptance_criteria": "TreeSHAP computed on source vs adapted models; Spearman rank correlation reported; error analysis on top false positives.",
        "estimated_compute": "3.5 minutes CPU, ~2.5 GB RAM",
        "status": "READY"
    },
    {
        "id": "EXP-12",
        "name": "Computational Profiling, Memory Footprint & Cryptographic Reproducibility",
        "category": "Reproducibility & Systems",
        "hypothesis": "Tree-based adaptation methods achieve orders of magnitude faster inference and lower memory consumption than neural adaptation (DANN / FT-Transformer), making them suitable for embedded substation deployment.",
        "prerequisites": "Model files, prediction pipelines, SHA-256 fingerprinting utility.",
        "dataset_and_split": "Benchmark sample of 100,000 flows measured for throughput and latency.",
        "command": ".venv/bin/python paper/experiments/journal_completion/scripts/run_exp12_computational_profiling.py",
        "outputs": [
            "metrics/exp12_profiling_results.json",
            "tables/exp12_systems_benchmarking.csv",
            "tables/exp12_cryptographic_fingerprints.csv",
            "figures/exp12_latency_throughput_tradeoff.png"
        ],
        "metrics": ["Training wall-clock time (s)", "Inference throughput (flows/sec)", "Per-flow latency (microseconds)", "Peak RSS memory (MB)", "Model storage footprint (KB)", "SHA-256 hash"],
        "acceptance_criteria": "End-to-end hardware-measured metrics on Intel i5-1135G7 CPU; SHA-256 verified for all models and primary artifacts.",
        "estimated_compute": "2 minutes CPU, ~2 GB RAM",
        "status": "READY"
    }
]

def main():
    root = Path(__file__).resolve().parent.parent
    config_dir = root / "configs"
    table_dir = root / "tables"
    config_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    json_path = config_dir / "experiment_registry.json"
    with open(json_path, "w") as f:
        json.dump(REGISTRY, f, indent=2)
    print(f"Written: {json_path}")

    # Build CSV summary
    rows = []
    for r in REGISTRY:
        rows.append({
            "Experiment_ID": r["id"],
            "Name": r["name"],
            "Category": r["category"],
            "Prerequisites": r["prerequisites"],
            "Dataset_and_Split": r["dataset_and_split"],
            "Command": r["command"],
            "Estimated_Compute": r["estimated_compute"],
            "Status": r["status"]
        })
    df = pd.DataFrame(rows)
    csv_path = table_dir / "experiment_registry.csv"
    df.to_csv(csv_path, index=False)
    print(f"Written: {csv_path}")

if __name__ == "__main__":
    main()
