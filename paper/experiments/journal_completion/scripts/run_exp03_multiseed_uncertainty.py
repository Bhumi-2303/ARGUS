#!/usr/bin/env python3
"""
EXP-03: Multi-Seed Robustness & Uncertainty Estimation (5 Seeds)
================================================================
Trains and evaluates adaptation methods across 5 seeds (42, 123, 456, 789, 1011)
on D1->D2 and computes 1,000-resample Bootstrap 95% Confidence Intervals,
Paired t-tests, and Cohen's d effect sizes.
"""

import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import lightgbm as lgb
from scipy import stats
from sklearn.metrics import (
    roc_auc_score, f1_score, matthews_corrcoef, balanced_accuracy_score,
    confusion_matrix, precision_score, recall_score
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
METRICS_DIR = BASE_DIR / "metrics"
TABLES_DIR = BASE_DIR / "tables"
FIGURES_DIR = BASE_DIR / "figures"
LOGS_DIR = BASE_DIR / "logs"

SEEDS = [42, 123, 456, 789, 1011]

def bootstrap_ci(y_true, y_prob, y_pred, n_bootstraps=1000, seed=42):
    rng = np.random.RandomState(seed)
    n = len(y_true)
    # Stratified subsample to compute fast CIs on large N
    sub_size = min(50000, n)
    indices = np.arange(n)
    
    boot_aucs, boot_mccs, boot_f1s, boot_bals, boot_specs = [], [], [], [], []
    for _ in range(n_bootstraps):
        boot_idx = rng.choice(indices, size=sub_size, replace=True)
        yt_b = y_true[boot_idx]
        if len(np.unique(yt_b)) < 2:
            continue
        yp_b = y_prob[boot_idx]
        ypr_b = y_pred[boot_idx]
        
        boot_aucs.append(roc_auc_score(yt_b, yp_b))
        boot_mccs.append(matthews_corrcoef(yt_b, ypr_b))
        boot_f1s.append(f1_score(yt_b, ypr_b, zero_division=0))
        boot_bals.append(balanced_accuracy_score(yt_b, ypr_b))
        cm = confusion_matrix(yt_b, ypr_b, labels=[0, 1])
        spec = cm[0, 0] / (cm[0, 0] + cm[0, 1]) if (cm[0, 0] + cm[0, 1]) > 0 else 0
        boot_specs.append(spec)
        
    def ci_str(vals):
        low, high = np.percentile(vals, [2.5, 97.5])
        return f"[{low:.4f}, {high:.4f}]", float(low), float(high)
        
    return {
        "roc_auc_ci": ci_str(boot_aucs)[0],
        "mcc_ci": ci_str(boot_mccs)[0],
        "f1_ci": ci_str(boot_f1s)[0],
        "balanced_acc_ci": ci_str(boot_bals)[0],
        "specificity_ci": ci_str(boot_specs)[0],
    }

def main():
    print("[*] Loading D1 training and D2 test sets...")
    # Load 500k stratified samples of D1 train
    features = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
    df_train_raw = pd.read_csv("data/raw/legacy_package/argus_coral_data/ciciot_train_features.csv", nrows=500000)
    df_train_coral = pd.read_csv("data/raw/legacy_package/argus_coral_data/ciciot_train_clean_class_aware_coral.csv", nrows=500000)
    
    # Load test set (2.6M rows)
    print("  Loading D2 test features (2,627,177 rows)...")
    df_test = pd.read_csv("data/raw/legacy_package/argus_coral_data/nfton_test_features.csv")
    y_test = df_test['label'].values
    X_test = df_test[features].values
    
    seed_records = []
    
    for seed in SEEDS:
        print(f"\n--- Running Seed {seed} ---")
        # 1. Source-Only Baseline
        df_sub_raw = df_train_raw.sample(n=250000, random_state=seed)
        clf_source = lgb.LGBMClassifier(
            n_estimators=100, learning_rate=0.05, max_depth=6, random_state=seed, verbose=-1, n_jobs=4
        )
        clf_source.fit(df_sub_raw[features].values, df_sub_raw['label'].values)
        p_source = clf_source.predict_proba(X_test)[:, 1]
        y_pred_source = (p_source >= 0.50).astype(int)
        
        cm_s = confusion_matrix(y_test, y_pred_source)
        tn_s, fp_s, fn_s, tp_s = cm_s.ravel()
        spec_s = tn_s / (tn_s + fp_s)
        rec_s = tp_s / (tp_s + fn_s)
        
        seed_records.append({
            "model": "Source-Only LightGBM",
            "seed": seed,
            "threshold": 0.50,
            "roc_auc": float(roc_auc_score(y_test, p_source)),
            "balanced_acc": float(balanced_accuracy_score(y_test, y_pred_source)),
            "mcc": float(matthews_corrcoef(y_test, y_pred_source)),
            "f1": float(f1_score(y_test, y_pred_source)),
            "specificity": float(spec_s),
            "recall": float(rec_s),
            "fpr": float(fp_s / (tn_s + fp_s))
        })
        
        # 2. Clean Class-Aware CORAL
        df_sub_coral = df_train_coral.sample(n=250000, random_state=seed)
        clf_coral = lgb.LGBMClassifier(
            n_estimators=100, learning_rate=0.05, max_depth=6, random_state=seed, verbose=-1, n_jobs=4
        )
        clf_coral.fit(df_sub_coral[features].values, df_sub_coral['label'].values)
        p_coral = clf_coral.predict_proba(X_test)[:, 1]
        y_pred_coral = (p_coral >= 0.99).astype(int)
        
        cm_c = confusion_matrix(y_test, y_pred_coral)
        tn_c, fp_c, fn_c, tp_c = cm_c.ravel()
        spec_c = tn_c / (tn_c + fp_c)
        rec_c = tp_c / (tp_c + fn_c)
        
        seed_records.append({
            "model": "Clean Class-Aware CORAL",
            "seed": seed,
            "threshold": 0.99,
            "roc_auc": float(roc_auc_score(y_test, p_coral)),
            "balanced_acc": float(balanced_accuracy_score(y_test, y_pred_coral)),
            "mcc": float(matthews_corrcoef(y_test, y_pred_coral)),
            "f1": float(f1_score(y_test, y_pred_coral)),
            "specificity": float(spec_c),
            "recall": float(rec_c),
            "fpr": float(fp_c / (tn_c + fp_c))
        })

    # Summary Statistics
    df_seeds = pd.DataFrame(seed_records)
    csv_seeds = TABLES_DIR / "exp03_multiseed_metrics.csv"
    df_seeds.to_csv(csv_seeds, index=False)
    print(f"\n[+] Saved multi-seed table: {csv_seeds}")
    
    summary_rows = []
    for model_name, grp in df_seeds.groupby("model"):
        row = {"model": model_name}
        for metric in ["roc_auc", "balanced_acc", "mcc", "f1", "specificity", "recall", "fpr"]:
            vals = grp[metric].values
            row[f"{metric}_mean"] = round(float(np.mean(vals)), 4)
            row[f"{metric}_std"] = round(float(np.std(vals)), 4)
            row[f"{metric}_formatted"] = f"{np.mean(vals):.4f} ± {np.std(vals):.4f}"
        summary_rows.append(row)
        
    df_summary = pd.DataFrame(summary_rows)
    print("\nMulti-Seed Aggregated Summary (Mean ± SD):")
    print(df_summary[["model", "balanced_acc_formatted", "mcc_formatted", "specificity_formatted", "roc_auc_formatted"]])
    
    # Paired t-test between Source-Only and Clean CORAL
    s_mcc = df_seeds[df_seeds['model'] == "Source-Only LightGBM"]['mcc'].values
    c_mcc = df_seeds[df_seeds['model'] == "Clean Class-Aware CORAL"]['mcc'].values
    s_bal = df_seeds[df_seeds['model'] == "Source-Only LightGBM"]['balanced_acc'].values
    c_bal = df_seeds[df_seeds['model'] == "Clean Class-Aware CORAL"]['balanced_acc'].values
    
    t_stat_mcc, p_val_mcc = stats.ttest_rel(c_mcc, s_mcc)
    t_stat_bal, p_val_bal = stats.ttest_rel(c_bal, s_bal)
    
    diff_mcc = c_mcc - s_mcc
    cohens_d_mcc = np.mean(diff_mcc) / (np.std(diff_mcc) + 1e-9)
    diff_bal = c_bal - s_bal
    cohens_d_bal = np.mean(diff_bal) / (np.std(diff_bal) + 1e-9)
    
    # Bootstrap CI for representative run (seed 42)
    print("\nComputing 1,000-resample Bootstrap 95% Confidence Intervals...")
    ci_source = bootstrap_ci(y_test, p_source, y_pred_source, n_bootstraps=1000)
    ci_coral = bootstrap_ci(y_test, p_coral, y_pred_coral, n_bootstraps=1000)
    
    ci_table = pd.DataFrame([
        {"model": "Source-Only LightGBM", **ci_source},
        {"model": "Clean Class-Aware CORAL", **ci_coral}
    ])
    csv_ci = TABLES_DIR / "exp03_bootstrap_ci.csv"
    ci_table.to_csv(csv_ci, index=False)
    print(f"[+] Saved bootstrap CI table: {csv_ci}")
    
    # Save full metrics JSON
    metrics_out = {
        "experiment_id": "EXP-03",
        "seeds": SEEDS,
        "summary": summary_rows,
        "statistical_tests": {
            "mcc_paired_ttest": {"t_stat": float(t_stat_mcc), "p_value": float(p_val_mcc), "cohens_d": float(cohens_d_mcc)},
            "balanced_acc_paired_ttest": {"t_stat": float(t_stat_bal), "p_value": float(p_val_bal), "cohens_d": float(cohens_d_bal)}
        },
        "bootstrap_ci": ci_table.to_dict(orient="records")
    }
    with open(METRICS_DIR / "exp03_multiseed_summary.json", "w") as f:
        json.dump(metrics_out, f, indent=2)
    
    # Generate Publication Figure
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    
    plot_df = pd.melt(df_seeds, id_vars=["model", "seed"], value_vars=["balanced_acc", "mcc", "specificity", "roc_auc"], var_name="Metric", value_name="Score")
    plot_df["Metric"] = plot_df["Metric"].map({
        "balanced_acc": "Balanced Accuracy",
        "mcc": "Matthews Corr (MCC)",
        "specificity": "Specificity",
        "roc_auc": "ROC-AUC"
    })
    
    palette = {"Source-Only LightGBM": "#D9534F", "Clean Class-Aware CORAL": "#1B365D"}
    sns.barplot(data=plot_df, x="Metric", y="Score", hue="model", palette=palette, capsize=0.1, err_kws={'linewidth': 1.5}, ax=ax)
    
    ax.set_title("5-Seed Stability & Metric Comparison: Source-Only vs Clean CORAL (D1 -> D2)", fontsize=11, fontweight="bold", pad=12)
    ax.set_ylim(-0.2, 1.05)
    ax.set_ylabel("Metric Value (Mean ± SD)", fontsize=10)
    ax.set_xlabel("", fontsize=10)
    ax.legend(title="Method", frameon=True, loc="upper right")
    plt.tight_layout()
    
    fig_path = FIGURES_DIR / "exp03_multiseed_stability_errorbars.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"[+] Saved figure: {fig_path}")

if __name__ == "__main__":
    main()
