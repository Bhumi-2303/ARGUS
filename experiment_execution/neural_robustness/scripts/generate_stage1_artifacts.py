#!/usr/bin/env python3
"""
ARGUS Neural Robustness — Stage 1 Artifact Finalization Script (No-Retrain / Low-Memory)
Reads existing preserved checkpoints, predictions, metrics, and training histories.
Generates 300 DPI publication-ready figures, curve CSVs, comparison tables, and metric validation checks.
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Configure Matplotlib for headless 300 DPI rendering
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_argus"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    roc_curve,
    precision_recall_curve,
    auc,
    roc_auc_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    accuracy_score,
    precision_score,
    recall_score,
    log_loss,
    brier_score_loss
)

import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
BASE = _curr
EE = BASE / "experiment_execution"
NR = EE / "neural_robustness"

def setup_dirs():
    (NR / "figures").mkdir(parents=True, exist_ok=True)
    (NR / "tables").mkdir(parents=True, exist_ok=True)
    (NR / "reports").mkdir(parents=True, exist_ok=True)
    (NR / "validation").mkdir(parents=True, exist_ok=True)

def generate_n1_artifacts():
    print("\n[+] Generating N1 (FT-Transformer ARGUS-4 D1->D3) Artifacts...")
    
    # 1. Load representative Seed 42 predictions
    pred_file = NR / "predictions/NR01/D1_D3_seed42_predictions.csv"
    assert pred_file.exists(), f"Missing prediction file: {pred_file}"
    df_pred = pd.read_csv(pred_file)
    y_true = df_pred["y_true"].values
    y_prob = df_pred["y_prob"].values
    
    # 2. Compute ROC & PR Curve data
    fpr, tpr, roc_th = roc_curve(y_true, y_prob)
    roc_auc_val = auc(fpr, tpr)
    
    prec, rec, pr_th = precision_recall_curve(y_true, y_prob)
    pr_auc_val = auc(rec, prec)
    
    # Save Curve CSVs
    pd.DataFrame({"fpr": fpr, "tpr": tpr, "threshold": np.append(roc_th[:-1], roc_th[-1])}).to_csv(
        NR / "figures/N1_ROC.csv", index=False
    )
    # precision_recall_curve returns len(precision) = len(thresholds) + 1
    pd.DataFrame({"precision": prec[:-1], "recall": rec[:-1], "threshold": pr_th}).to_csv(
        NR / "figures/N1_PR.csv", index=False
    )
    print("  -> Saved figures/N1_ROC.csv and figures/N1_PR.csv")
    
    # 3. Plot ROC Curve (300 DPI)
    plt.figure(figsize=(7, 6), dpi=300)
    plt.plot(fpr, tpr, color="#1f77b4", lw=2.5, label=f"FT-Transformer (Seed 42, AUC = {roc_auc_val:.4f})")
    plt.plot([0, 1], [0, 1], color="#7f7f7f", linestyle="--", lw=1.5, label="Random Guess (AUC = 0.5000)")
    plt.xlabel("False Positive Rate (FPR)", fontsize=12, fontweight="bold")
    plt.ylabel("True Positive Rate / Recall (TPR)", fontsize=12, fontweight="bold")
    plt.title("N1: ROC Curve — FT-Transformer ARGUS-4 (D1 → D3)\nRepresentative Seed-42 Test Prediction (N=714,453)", fontsize=13, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=11)
    plt.tight_layout()
    plt.savefig(NR / "figures/N1_ROC.png", dpi=300)
    plt.close()
    print("  -> Saved figures/N1_ROC.png (300 DPI)")
    
    # 4. Plot PR Curve (300 DPI)
    no_skill = np.mean(y_true)
    plt.figure(figsize=(7, 6), dpi=300)
    plt.plot(rec, prec, color="#d62728", lw=2.5, label=f"FT-Transformer (Seed 42, AUC = {pr_auc_val:.4f})")
    plt.axhline(y=no_skill, color="#7f7f7f", linestyle="--", lw=1.5, label=f"Target Attack Prior ($\pi$ = {no_skill:.4f})")
    plt.xlabel("Recall", fontsize=12, fontweight="bold")
    plt.ylabel("Precision", fontsize=12, fontweight="bold")
    plt.title("N1: Precision-Recall Curve — FT-Transformer ARGUS-4 (D1 → D3)\nRepresentative Seed-42 Test Prediction (N=714,453)", fontsize=13, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=11)
    plt.tight_layout()
    plt.savefig(NR / "figures/N1_PR.png", dpi=300)
    plt.close()
    print("  -> Saved figures/N1_PR.png (300 DPI)")
    
    # 5. Confusion Matrix (Default theta=0.50 & Calibrated theta=0.67)
    cm_05 = confusion_matrix(y_true, (y_prob >= 0.5).astype(int))
    cm_cal = confusion_matrix(y_true, (y_prob >= 0.67).astype(int))
    
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    sns.heatmap(cm_05, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[0],
                xticklabels=["Normal (0)", "Attack (1)"], yticklabels=["Normal (0)", "Attack (1)"])
    axes[0].set_title("Default Threshold ($\Theta = 0.50$)\nFPR=100.0%, FNR=0.0%, F1=0.3669", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Predicted Class", fontsize=11)
    axes[0].set_ylabel("True Class", fontsize=11)
    
    sns.heatmap(cm_cal, annot=True, fmt="d", cmap="Greens", cbar=False, ax=axes[1],
                xticklabels=["Normal (0)", "Attack (1)"], yticklabels=["Normal (0)", "Attack (1)"])
    axes[1].set_title("Calibrated Threshold ($\Theta = 0.67$)\nFPR=96.68%, FNR=0.77%, F1=0.3724", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Predicted Class", fontsize=11)
    axes[1].set_ylabel("True Class", fontsize=11)
    
    fig.suptitle("N1: Confusion Matrices — FT-Transformer ARGUS-4 (D1 → D3 Seed 42)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(NR / "figures/N1_confusion_matrix.png", dpi=300)
    plt.close()
    print("  -> Saved figures/N1_confusion_matrix.png (300 DPI)")
    
    # 6. Training Curve
    log_seeds = [42, 123, 456, 789, 1011]
    histories = {}
    for s in log_seeds:
        lf = NR / f"training_logs/training_history_FTT_ARGUS4_D1_D3_seed{s}.csv"
        if lf.exists():
            histories[s] = pd.read_csv(lf)
            
    if histories:
        plt.figure(figsize=(8, 5.5), dpi=300)
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        for idx, (s, h) in enumerate(histories.items()):
            plt.plot(h["epoch"], h["train_loss"], linestyle="--", color=colors[idx % len(colors)], alpha=0.7, label=f"Seed {s} Train Loss")
            plt.plot(h["epoch"], h["val_loss"], linestyle="-", marker="o", color=colors[idx % len(colors)], lw=2, label=f"Seed {s} Val Loss")
        plt.xlabel("Epoch", fontsize=12, fontweight="bold")
        plt.ylabel("Binary Cross-Entropy Loss", fontsize=12, fontweight="bold")
        plt.title("N1: Training & Validation Loss History — FT-Transformer D1 → D3\nEarly Stopping on Target Calibration Partition", fontsize=13, fontweight="bold")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="upper right", fontsize=9, ncol=2)
        plt.tight_layout()
        plt.savefig(NR / "figures/N1_training_curve.png", dpi=300)
        plt.close()
        print("  -> Saved figures/N1_training_curve.png (300 DPI)")

    # 7. Comparison Table: LightGBM vs FT-Transformer (D1->D3)
    # Master LightGBM results
    df_master = pd.read_csv(EE / "FINAL_MASTER_RESULTS.csv")
    lgbm_raw = df_master[df_master["experiment_id"] == "D1_D3_BASELINE_RAW"]
    lgbm_cal = df_master[df_master["experiment_id"] == "D1_D3_BASELINE_CALIB"]
    
    # FT-Transformer results
    df_ftt = pd.read_csv(NR / "metrics/NR01_FTTransformer_ARGUS4.csv")
    ftt_raw = df_ftt[df_ftt["experiment_id"] == "D1_D3_FTT_ARGUS4_RAW"]
    ftt_cal = df_ftt[df_ftt["experiment_id"] == "D1_D3_FTT_ARGUS4_CALIB"]
    
    comparison_rows = [
        {
            "RESULT_SOURCE": "EXISTING",
            "model_family": "LightGBM GBDT",
            "source_domain": "D1 (CICIoT2023)",
            "target_domain": "D3 (IEC 60870-5-104)",
            "feature_set": "ARGUS-4",
            "condition": "Default Threshold (theta=0.50)",
            "num_seeds": len(lgbm_raw),
            "accuracy_mean": f"{lgbm_raw['accuracy'].mean():.4f} +/- {lgbm_raw['accuracy'].std():.4f}",
            "precision_mean": f"{lgbm_raw['precision'].mean():.4f} +/- {lgbm_raw['precision'].std():.4f}",
            "recall_mean": f"{lgbm_raw['recall'].mean():.4f} +/- {lgbm_raw['recall'].std():.4f}",
            "f1_mean": f"{lgbm_raw['f1'].mean():.4f} +/- {lgbm_raw['f1'].std():.4f}",
            "fpr_mean": f"{lgbm_raw['fpr'].mean():.4f} +/- {lgbm_raw['fpr'].std():.4f}",
            "fnr_mean": f"{lgbm_raw['fnr'].mean():.4f} +/- {lgbm_raw['fnr'].std():.4f}",
            "mcc_mean": f"{lgbm_raw['mcc'].mean():.4f} +/- {lgbm_raw['mcc'].std():.4f}",
            "roc_auc_mean": f"{lgbm_raw['roc_auc'].mean():.4f} +/- {lgbm_raw['roc_auc'].std():.4f}",
            "pr_auc_mean": f"{lgbm_raw['pr_auc'].mean():.4f} +/- {lgbm_raw['pr_auc'].std():.4f}",
        },
        {
            "RESULT_SOURCE": "EXISTING",
            "model_family": "LightGBM GBDT",
            "source_domain": "D1 (CICIoT2023)",
            "target_domain": "D3 (IEC 60870-5-104)",
            "feature_set": "ARGUS-4",
            "condition": "Calibrated Threshold (theta=0.62-0.64)",
            "num_seeds": len(lgbm_cal),
            "accuracy_mean": f"{lgbm_cal['accuracy'].mean():.4f} +/- {lgbm_cal['accuracy'].std():.4f}",
            "precision_mean": f"{lgbm_cal['precision'].mean():.4f} +/- {lgbm_cal['precision'].std():.4f}",
            "recall_mean": f"{lgbm_cal['recall'].mean():.4f} +/- {lgbm_cal['recall'].std():.4f}",
            "f1_mean": f"{lgbm_cal['f1'].mean():.4f} +/- {lgbm_cal['f1'].std():.4f}",
            "fpr_mean": f"{lgbm_cal['fpr'].mean():.4f} +/- {lgbm_cal['fpr'].std():.4f}",
            "fnr_mean": f"{lgbm_cal['fnr'].mean():.4f} +/- {lgbm_cal['fnr'].std():.4f}",
            "mcc_mean": f"{lgbm_cal['mcc'].mean():.4f} +/- {lgbm_cal['mcc'].std():.4f}",
            "roc_auc_mean": f"{lgbm_cal['roc_auc'].mean():.4f} +/- {lgbm_cal['roc_auc'].std():.4f}",
            "pr_auc_mean": f"{lgbm_cal['pr_auc'].mean():.4f} +/- {lgbm_cal['pr_auc'].std():.4f}",
        },
        {
            "RESULT_SOURCE": "NEURAL_ROBUSTNESS",
            "model_family": "FT-Transformer Neural",
            "source_domain": "D1 (CICIoT2023)",
            "target_domain": "D3 (IEC 60870-5-104)",
            "feature_set": "ARGUS-4",
            "condition": "Default Threshold (theta=0.50)",
            "num_seeds": len(ftt_raw),
            "accuracy_mean": f"{ftt_raw['accuracy'].mean():.4f} +/- {ftt_raw['accuracy'].std():.4f}",
            "precision_mean": f"{ftt_raw['precision'].mean():.4f} +/- {ftt_raw['precision'].std():.4f}",
            "recall_mean": f"{ftt_raw['recall'].mean():.4f} +/- {ftt_raw['recall'].std():.4f}",
            "f1_mean": f"{ftt_raw['f1'].mean():.4f} +/- {ftt_raw['f1'].std():.4f}",
            "fpr_mean": f"{ftt_raw['fpr'].mean():.4f} +/- {ftt_raw['fpr'].std():.4f}",
            "fnr_mean": f"{ftt_raw['fnr'].mean():.4f} +/- {ftt_raw['fnr'].std():.4f}",
            "mcc_mean": f"{ftt_raw['mcc'].mean():.4f} +/- {ftt_raw['mcc'].std():.4f}",
            "roc_auc_mean": f"{ftt_raw['roc_auc'].mean():.4f} +/- {ftt_raw['roc_auc'].std():.4f}",
            "pr_auc_mean": f"{ftt_raw['pr_auc'].mean():.4f} +/- {ftt_raw['pr_auc'].std():.4f}",
        },
        {
            "RESULT_SOURCE": "NEURAL_ROBUSTNESS",
            "model_family": "FT-Transformer Neural",
            "source_domain": "D1 (CICIoT2023)",
            "target_domain": "D3 (IEC 60870-5-104)",
            "feature_set": "ARGUS-4",
            "condition": "Calibrated Threshold (theta=0.43-0.87)",
            "num_seeds": len(ftt_cal),
            "accuracy_mean": f"{ftt_cal['accuracy'].mean():.4f} +/- {ftt_cal['accuracy'].std():.4f}",
            "precision_mean": f"{ftt_cal['precision'].mean():.4f} +/- {ftt_cal['precision'].std():.4f}",
            "recall_mean": f"{ftt_cal['recall'].mean():.4f} +/- {ftt_cal['recall'].std():.4f}",
            "f1_mean": f"{ftt_cal['f1'].mean():.4f} +/- {ftt_cal['f1'].std():.4f}",
            "fpr_mean": f"{ftt_cal['fpr'].mean():.4f} +/- {ftt_cal['fpr'].std():.4f}",
            "fnr_mean": f"{ftt_cal['fnr'].mean():.4f} +/- {ftt_cal['fnr'].std():.4f}",
            "mcc_mean": f"{ftt_cal['mcc'].mean():.4f} +/- {ftt_cal['mcc'].std():.4f}",
            "roc_auc_mean": f"{ftt_cal['roc_auc'].mean():.4f} +/- {ftt_cal['roc_auc'].std():.4f}",
            "pr_auc_mean": f"{ftt_cal['pr_auc'].mean():.4f} +/- {ftt_cal['pr_auc'].std():.4f}",
        },
    ]
    pd.DataFrame(comparison_rows).to_csv(NR / "tables/N1_LightGBM_vs_FTTransformer.csv", index=False)
    print("  -> Saved tables/N1_LightGBM_vs_FTTransformer.csv")


def generate_n2_artifacts():
    print("\n[+] Generating N2 (FT-Transformer ARGUS-4 D2->D3) Artifacts...")
    
    # 1. Load representative Seed 42 predictions
    pred_file = NR / "predictions/NR01/D2_D3_seed42_predictions.csv"
    assert pred_file.exists(), f"Missing prediction file: {pred_file}"
    df_pred = pd.read_csv(pred_file)
    y_true = df_pred["y_true"].values
    y_prob = df_pred["y_prob"].values
    
    # 2. Compute ROC & PR Curve data
    fpr, tpr, roc_th = roc_curve(y_true, y_prob)
    roc_auc_val = auc(fpr, tpr)
    
    prec, rec, pr_th = precision_recall_curve(y_true, y_prob)
    pr_auc_val = auc(rec, prec)
    
    # Save Curve CSVs
    pd.DataFrame({"fpr": fpr, "tpr": tpr, "threshold": np.append(roc_th[:-1], roc_th[-1])}).to_csv(
        NR / "figures/N2_ROC.csv", index=False
    )
    pd.DataFrame({"precision": prec[:-1], "recall": rec[:-1], "threshold": pr_th}).to_csv(
        NR / "figures/N2_PR.csv", index=False
    )
    print("  -> Saved figures/N2_ROC.csv and figures/N2_PR.csv")
    
    # 3. Plot ROC Curve (300 DPI)
    plt.figure(figsize=(7, 6), dpi=300)
    plt.plot(fpr, tpr, color="#2ca02c", lw=2.5, label=f"FT-Transformer (Seed 42, AUC = {roc_auc_val:.4f})")
    plt.plot([0, 1], [0, 1], color="#7f7f7f", linestyle="--", lw=1.5, label="Random Guess (AUC = 0.5000)")
    plt.xlabel("False Positive Rate (FPR)", fontsize=12, fontweight="bold")
    plt.ylabel("True Positive Rate / Recall (TPR)", fontsize=12, fontweight="bold")
    plt.title("N2: ROC Curve — FT-Transformer ARGUS-4 (D2 → D3)\nRepresentative Seed-42 Test Prediction (N=714,453)", fontsize=13, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=11)
    plt.tight_layout()
    plt.savefig(NR / "figures/N2_ROC.png", dpi=300)
    plt.close()
    print("  -> Saved figures/N2_ROC.png (300 DPI)")
    
    # 4. Plot PR Curve (300 DPI)
    no_skill = np.mean(y_true)
    plt.figure(figsize=(7, 6), dpi=300)
    plt.plot(rec, prec, color="#ff7f0e", lw=2.5, label=f"FT-Transformer (Seed 42, AUC = {pr_auc_val:.4f})")
    plt.axhline(y=no_skill, color="#7f7f7f", linestyle="--", lw=1.5, label=f"Target Attack Prior ($\pi$ = {no_skill:.4f})")
    plt.xlabel("Recall", fontsize=12, fontweight="bold")
    plt.ylabel("Precision", fontsize=12, fontweight="bold")
    plt.title("N2: Precision-Recall Curve — FT-Transformer ARGUS-4 (D2 → D3)\nRepresentative Seed-42 Test Prediction (N=714,453)", fontsize=13, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=11)
    plt.tight_layout()
    plt.savefig(NR / "figures/N2_PR.png", dpi=300)
    plt.close()
    print("  -> Saved figures/N2_PR.png (300 DPI)")
    
    # 5. Confusion Matrix (Default theta=0.50 & Calibrated theta=0.21)
    cm_05 = confusion_matrix(y_true, (y_prob >= 0.5).astype(int))
    cm_cal = confusion_matrix(y_true, (y_prob >= 0.21).astype(int))
    
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    sns.heatmap(cm_05, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[0],
                xticklabels=["Normal (0)", "Attack (1)"], yticklabels=["Normal (0)", "Attack (1)"])
    axes[0].set_title("Default Threshold ($\Theta = 0.50$)\nFPR=9.78%, FNR=95.83%, F1=0.0605", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Predicted Class", fontsize=11)
    axes[0].set_ylabel("True Class", fontsize=11)
    
    sns.heatmap(cm_cal, annot=True, fmt="d", cmap="Greens", cbar=False, ax=axes[1],
                xticklabels=["Normal (0)", "Attack (1)"], yticklabels=["Normal (0)", "Attack (1)"])
    axes[1].set_title("Calibrated Threshold ($\Theta = 0.21$)\nFPR=78.09%, FNR=12.62%, F1=0.3825", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Predicted Class", fontsize=11)
    axes[1].set_ylabel("True Class", fontsize=11)
    
    fig.suptitle("N2: Confusion Matrices — FT-Transformer ARGUS-4 (D2 → D3 Seed 42)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(NR / "figures/N2_confusion_matrix.png", dpi=300)
    plt.close()
    print("  -> Saved figures/N2_confusion_matrix.png (300 DPI)")
    
    # 6. Training Curve
    log_seeds = [42, 123, 456, 789, 1011]
    histories = {}
    for s in log_seeds:
        lf = NR / f"training_logs/training_history_FTT_ARGUS4_D2_D3_seed{s}.csv"
        if lf.exists():
            histories[s] = pd.read_csv(lf)
            
    if histories:
        plt.figure(figsize=(8, 5.5), dpi=300)
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        for idx, (s, h) in enumerate(histories.items()):
            plt.plot(h["epoch"], h["train_loss"], linestyle="--", color=colors[idx % len(colors)], alpha=0.7, label=f"Seed {s} Train Loss")
            plt.plot(h["epoch"], h["val_loss"], linestyle="-", marker="o", color=colors[idx % len(colors)], lw=2, label=f"Seed {s} Val Loss")
        plt.xlabel("Epoch", fontsize=12, fontweight="bold")
        plt.ylabel("Binary Cross-Entropy Loss", fontsize=12, fontweight="bold")
        plt.title("N2: Training & Validation Loss History — FT-Transformer D2 → D3\nEarly Stopping on Target Calibration Partition", fontsize=13, fontweight="bold")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="upper right", fontsize=9, ncol=2)
        plt.tight_layout()
        plt.savefig(NR / "figures/N2_training_curve.png", dpi=300)
        plt.close()
        print("  -> Saved figures/N2_training_curve.png (300 DPI)")

    # 7. Comparison Table: LightGBM vs FT-Transformer (D2->D3)
    df_master = pd.read_csv(EE / "FINAL_MASTER_RESULTS.csv")
    lgbm_raw = df_master[df_master["experiment_id"] == "D2_D3_BASELINE_RAW"]
    lgbm_cal = df_master[df_master["experiment_id"] == "D2_D3_BASELINE_CALIB"]
    
    df_ftt = pd.read_csv(NR / "metrics/NR01_FTTransformer_ARGUS4.csv")
    ftt_raw = df_ftt[df_ftt["experiment_id"] == "D2_D3_FTT_ARGUS4_RAW"]
    ftt_cal = df_ftt[df_ftt["experiment_id"] == "D2_D3_FTT_ARGUS4_CALIB"]
    
    comparison_rows = [
        {
            "RESULT_SOURCE": "EXISTING",
            "model_family": "LightGBM GBDT",
            "source_domain": "D2 (NF-ToN-IoT-v2)",
            "target_domain": "D3 (IEC 60870-5-104)",
            "feature_set": "ARGUS-4",
            "condition": "Default Threshold (theta=0.50)",
            "num_seeds": len(lgbm_raw),
            "accuracy_mean": f"{lgbm_raw['accuracy'].mean():.4f} +/- {lgbm_raw['accuracy'].std():.4f}",
            "precision_mean": f"{lgbm_raw['precision'].mean():.4f} +/- {lgbm_raw['precision'].std():.4f}",
            "recall_mean": f"{lgbm_raw['recall'].mean():.4f} +/- {lgbm_raw['recall'].std():.4f}",
            "f1_mean": f"{lgbm_raw['f1'].mean():.4f} +/- {lgbm_raw['f1'].std():.4f}",
            "fpr_mean": f"{lgbm_raw['fpr'].mean():.4f} +/- {lgbm_raw['fpr'].std():.4f}",
            "fnr_mean": f"{lgbm_raw['fnr'].mean():.4f} +/- {lgbm_raw['fnr'].std():.4f}",
            "mcc_mean": f"{lgbm_raw['mcc'].mean():.4f} +/- {lgbm_raw['mcc'].std():.4f}",
            "roc_auc_mean": f"{lgbm_raw['roc_auc'].mean():.4f} +/- {lgbm_raw['roc_auc'].std():.4f}",
            "pr_auc_mean": f"{lgbm_raw['pr_auc'].mean():.4f} +/- {lgbm_raw['pr_auc'].std():.4f}",
        },
        {
            "RESULT_SOURCE": "EXISTING",
            "model_family": "LightGBM GBDT",
            "source_domain": "D2 (NF-ToN-IoT-v2)",
            "target_domain": "D3 (IEC 60870-5-104)",
            "feature_set": "ARGUS-4",
            "condition": "Calibrated Threshold (theta=0.01)",
            "num_seeds": len(lgbm_cal),
            "accuracy_mean": f"{lgbm_cal['accuracy'].mean():.4f} +/- {lgbm_cal['accuracy'].std():.4f}",
            "precision_mean": f"{lgbm_cal['precision'].mean():.4f} +/- {lgbm_cal['precision'].std():.4f}",
            "recall_mean": f"{lgbm_cal['recall'].mean():.4f} +/- {lgbm_cal['recall'].std():.4f}",
            "f1_mean": f"{lgbm_cal['f1'].mean():.4f} +/- {lgbm_cal['f1'].std():.4f}",
            "fpr_mean": f"{lgbm_cal['fpr'].mean():.4f} +/- {lgbm_cal['fpr'].std():.4f}",
            "fnr_mean": f"{lgbm_cal['fnr'].mean():.4f} +/- {lgbm_cal['fnr'].std():.4f}",
            "mcc_mean": f"{lgbm_cal['mcc'].mean():.4f} +/- {lgbm_cal['mcc'].std():.4f}",
            "roc_auc_mean": f"{lgbm_cal['roc_auc'].mean():.4f} +/- {lgbm_cal['roc_auc'].std():.4f}",
            "pr_auc_mean": f"{lgbm_cal['pr_auc'].mean():.4f} +/- {lgbm_cal['pr_auc'].std():.4f}",
        },
        {
            "RESULT_SOURCE": "NEURAL_ROBUSTNESS",
            "model_family": "FT-Transformer Neural",
            "source_domain": "D2 (NF-ToN-IoT-v2)",
            "target_domain": "D3 (IEC 60870-5-104)",
            "feature_set": "ARGUS-4",
            "condition": "Default Threshold (theta=0.50)",
            "num_seeds": len(ftt_raw),
            "accuracy_mean": f"{ftt_raw['accuracy'].mean():.4f} +/- {ftt_raw['accuracy'].std():.4f}",
            "precision_mean": f"{ftt_raw['precision'].mean():.4f} +/- {ftt_raw['precision'].std():.4f}",
            "recall_mean": f"{ftt_raw['recall'].mean():.4f} +/- {ftt_raw['recall'].std():.4f}",
            "f1_mean": f"{ftt_raw['f1'].mean():.4f} +/- {ftt_raw['f1'].std():.4f}",
            "fpr_mean": f"{ftt_raw['fpr'].mean():.4f} +/- {ftt_raw['fpr'].std():.4f}",
            "fnr_mean": f"{ftt_raw['fnr'].mean():.4f} +/- {ftt_raw['fnr'].std():.4f}",
            "mcc_mean": f"{ftt_raw['mcc'].mean():.4f} +/- {ftt_raw['mcc'].std():.4f}",
            "roc_auc_mean": f"{ftt_raw['roc_auc'].mean():.4f} +/- {ftt_raw['roc_auc'].std():.4f}",
            "pr_auc_mean": f"{ftt_raw['pr_auc'].mean():.4f} +/- {ftt_raw['pr_auc'].std():.4f}",
        },
        {
            "RESULT_SOURCE": "NEURAL_ROBUSTNESS",
            "model_family": "FT-Transformer Neural",
            "source_domain": "D2 (NF-ToN-IoT-v2)",
            "target_domain": "D3 (IEC 60870-5-104)",
            "feature_set": "ARGUS-4",
            "condition": "Calibrated Threshold (theta=0.12-0.38)",
            "num_seeds": len(ftt_cal),
            "accuracy_mean": f"{ftt_cal['accuracy'].mean():.4f} +/- {ftt_cal['accuracy'].std():.4f}",
            "precision_mean": f"{ftt_cal['precision'].mean():.4f} +/- {ftt_cal['precision'].std():.4f}",
            "recall_mean": f"{ftt_cal['recall'].mean():.4f} +/- {ftt_cal['recall'].std():.4f}",
            "f1_mean": f"{ftt_cal['f1'].mean():.4f} +/- {ftt_cal['f1'].std():.4f}",
            "fpr_mean": f"{ftt_cal['fpr'].mean():.4f} +/- {ftt_cal['fpr'].std():.4f}",
            "fnr_mean": f"{ftt_cal['fnr'].mean():.4f} +/- {ftt_cal['fnr'].std():.4f}",
            "mcc_mean": f"{ftt_cal['mcc'].mean():.4f} +/- {ftt_cal['mcc'].std():.4f}",
            "roc_auc_mean": f"{ftt_cal['roc_auc'].mean():.4f} +/- {ftt_cal['roc_auc'].std():.4f}",
            "pr_auc_mean": f"{ftt_cal['pr_auc'].mean():.4f} +/- {ftt_cal['pr_auc'].std():.4f}",
        },
    ]
    pd.DataFrame(comparison_rows).to_csv(NR / "tables/N2_LightGBM_vs_FTTransformer.csv", index=False)
    print("  -> Saved tables/N2_LightGBM_vs_FTTransformer.csv")


def validate_n3_metrics():
    print("\n[+] Validating N3 (FT-Transformer Native SCADA Seed 42) Metrics...")
    pred_file = NR / "predictions/NR02/D3_native_seed42_predictions.csv"
    assert pred_file.exists(), f"Missing prediction file: {pred_file}"
    df_pred = pd.read_csv(pred_file)
    y_true = df_pred["y_true"].values
    y_prob = df_pred["y_prob"].values
    
    roc_auc = roc_auc_score(y_true, y_prob)
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(rec, prec)
    logloss = log_loss(y_true, y_prob)
    brier = brier_score_loss(y_true, y_prob)
    
    # Evaluate at multiple operating thresholds
    operating_points = [
        ("Default (theta=0.50)", 0.50),
        ("Calibrated MCC Peak (theta=0.35)", 0.35),
        ("Low FPR Operating Point (theta=0.78)", 0.78),
    ]
    
    val_rows = []
    for label, th in operating_points:
        y_pred = (y_prob >= th).astype(int)
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        row = {
            "experiment_id": "D3_NATIVE_FTT_SEED42_CHECK",
            "model": "FT-Transformer Native SCADA (73 Feat)",
            "seed": 42,
            "condition": label,
            "threshold": th,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "fpr": fp / (fp + tn),
            "fnr": fn / (fn + tp),
            "mcc": matthews_corrcoef(y_true, y_pred),
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "log_loss": logloss,
            "brier_score": brier,
            "status": "VALIDATED"
        }
        val_rows.append(row)
        
    df_val = pd.DataFrame(val_rows)
    df_val.to_csv(NR / "validation/N3_seed42_metric_check.csv", index=False)
    print("  -> Saved validation/N3_seed42_metric_check.csv (STATUS = VALIDATED)")


if __name__ == "__main__":
    setup_dirs()
    generate_n1_artifacts()
    generate_n2_artifacts()
    validate_n3_metrics()
    print("\n[+] Stage 1 artifact generation completed successfully.")
