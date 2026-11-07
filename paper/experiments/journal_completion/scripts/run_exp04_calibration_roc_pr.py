#!/usr/bin/env python3
"""
EXP-04: Full ROC, Precision-Recall, Operating Threshold, and Calibration Analysis
==================================================================================
Evaluates exact ROC/PR curves, Brier scores, Expected Calibration Error (ECE),
reliability diagrams, and operational SOC FPR-constrained thresholds (FPR <= 0.01% to 5.0%).
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_curve, precision_recall_curve, roc_auc_score, average_precision_score,
    brier_score_loss, confusion_matrix, f1_score, matthews_corrcoef, precision_score, recall_score
)
from sklearn.calibration import calibration_curve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
METRICS_DIR = BASE_DIR / "metrics"
TABLES_DIR = BASE_DIR / "tables"
FIGURES_DIR = BASE_DIR / "figures"
LOGS_DIR = BASE_DIR / "logs"

for d in [METRICS_DIR, TABLES_DIR, FIGURES_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def compute_ece(y_true, y_prob, n_bins=10):
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        mask = (y_prob >= bin_lower) & (y_prob < bin_upper) if i < n_bins - 1 else (y_prob >= bin_lower) & (y_prob <= bin_upper)
        bin_count = np.sum(mask)
        if bin_count > 0:
            bin_acc = np.mean(y_true[mask])
            bin_conf = np.mean(y_prob[mask])
            ece += (bin_count / n) * np.abs(bin_acc - bin_conf)
    return float(ece)

def evaluate_soc_budgets(y_true, y_prob, fpr_targets=[0.0001, 0.001, 0.01, 0.05]):
    # fpr = fp / (tn + fp)
    neg_idx = np.where(y_true == 0)[0]
    pos_idx = np.where(y_true == 1)[0]
    n_neg = len(neg_idx)
    n_pos = len(pos_idx)
    
    # Sort negative scores to find thresholds
    neg_scores = np.sort(y_prob[neg_idx])
    
    budget_results = []
    for target_fpr in fpr_targets:
        # We allow at most int(target_fpr * n_neg) false positives
        max_fp = int(target_fpr * n_neg)
        if max_fp == 0:
            # Threshold must be higher than all negatives except 0
            th = neg_scores[-1] + 1e-6
        else:
            th = neg_scores[-max_fp]
            
        y_pred = (y_prob >= th).astype(int)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        actual_fpr = fp / (tn + fp)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = f1_score(y_true, y_pred, zero_division=0)
        mcc = matthews_corrcoef(y_true, y_pred)
        
        budget_results.append({
            "target_fpr": target_fpr,
            "target_fpr_label": f"FPR <= {target_fpr*100:.2f}%",
            "operating_threshold": round(float(th), 4),
            "actual_fpr": round(float(actual_fpr), 6),
            "attack_recall": round(float(recall), 4),
            "precision": round(float(precision), 4),
            "f1_score": round(float(f1), 4),
            "mcc": round(float(mcc), 4),
            "false_alarms": int(fp),
            "detected_attacks": int(tp)
        })
    return budget_results

def main():
    print("[*] Running EXP-04: Full ROC, PR, Threshold, and Calibration Analysis...")
    
    # 1. Load D2 Ground Truth (2,627,177 flows)
    print("  Loading D2 ground truth labels...")
    y_d2 = pd.read_csv("data/raw/legacy_package/argus_coral_data/nfton_test_features.csv", usecols=['label'])['label'].values
    
    # 2. Load D1->D2 Model Predictions
    p_source = np.load("results/verification/predictions/B_source_only_NFToN_preds.npz")['proba']
    p_global = np.load("results/verification/predictions/Global_CORAL_preds.npz")['proba']
    p_clean = np.load("results/verification/predictions/Clean_Class_Aware_CORAL_preds.npz")['proba']
    p_dann = pd.read_csv("data/raw/legacy_package/argus_coral_data/dann_results/dann_final_test_predictions.csv")['probability'].values
    
    # 3. Load D3 Native Model Predictions (714,453 flows)
    print("  Loading D3 native model predictions...")
    df_d3 = pd.read_csv("experiments/execution/neural_robustness/native_high_performance/predictions/NR04_D3_native_seed42_predictions.csv")
    y_d3 = df_d3['true_label'].values
    p_d3 = df_d3['predicted_probability'].values
    
    models = {
        "Source-Only XGBoost (D1->D2)": (y_d2, p_source, "#D9534F"),
        "Global CORAL (D1->D2)": (y_d2, p_global, "#F0AD4E"),
        "Clean Class-Aware CORAL (D1->D2)": (y_d2, p_clean, "#2E75B6"),
        "DANN (D1->D2)": (y_d2, p_dann, "#9C27B0"),
        "Native SCADA Model (D3 in-domain)": (y_d3, p_d3, "#1B365D")
    }
    
    metrics_summary = []
    operational_tables = []
    
    plt.style.use("seaborn-v0_8-whitegrid")
    
    # Setup Figure 1: ROC Curves
    fig_roc, ax_roc = plt.subplots(figsize=(7, 6), dpi=300)
    # Setup Figure 2: PR Curves
    fig_pr, ax_pr = plt.subplots(figsize=(7, 6), dpi=300)
    # Setup Figure 3: Calibration Curves
    fig_cal, ax_cal = plt.subplots(figsize=(7, 6), dpi=300)
    
    for name, (y_true, y_prob, color) in models.items():
        print(f"  Evaluating {name}...")
        # Metrics
        roc_auc = roc_auc_score(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)
        brier = brier_score_loss(y_true, y_prob)
        ece = compute_ece(y_true, y_prob, n_bins=10)
        
        metrics_summary.append({
            "model": name,
            "samples": len(y_true),
            "roc_auc": round(float(roc_auc), 4),
            "pr_auc": round(float(pr_auc), 4),
            "brier_score": round(float(brier), 4),
            "expected_calibration_error": round(float(ece), 4)
        })
        
        # ROC Curve (subsampled for smooth plotting)
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        sub_idx = np.linspace(0, len(fpr) - 1, min(1000, len(fpr))).astype(int)
        ax_roc.plot(fpr[sub_idx], tpr[sub_idx], label=f"{name} (AUC={roc_auc:.3f})", color=color, lw=2)
        
        # PR Curve
        prec, rec, _ = precision_recall_curve(y_true, y_prob)
        sub_idx_pr = np.linspace(0, len(prec) - 1, min(1000, len(prec))).astype(int)
        ax_pr.plot(rec[sub_idx_pr], prec[sub_idx_pr], label=f"{name} (AP={pr_auc:.3f})", color=color, lw=2)
        
        # Calibration Curve
        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy='uniform')
        ax_cal.plot(prob_pred, prob_true, marker='o', label=f"{name} (ECE={ece:.3f})", color=color, lw=1.5)
        
        # SOC Budgets
        budgets = evaluate_soc_budgets(y_true, y_prob)
        for b in budgets:
            operational_tables.append({"model": name, **b})
            
    # Finalize ROC Figure
    ax_roc.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.7, label="Chance Baseline (AUC=0.500)")
    ax_roc.set_xlim([-0.02, 1.02])
    ax_roc.set_ylim([-0.02, 1.02])
    ax_roc.set_xlabel("False Positive Rate (FPR)", fontsize=11)
    ax_roc.set_ylabel("True Positive Rate (Recall)", fontsize=11)
    ax_roc.set_title("Receiver Operating Characteristic (ROC) Overlay", fontsize=12, fontweight="bold", pad=12)
    ax_roc.legend(frameon=True, loc="lower right", fontsize=9)
    plt.tight_layout()
    fig_roc.savefig(FIGURES_DIR / "exp04_roc_curves.png")
    plt.close(fig_roc)
    print(f"[+] Saved ROC figure: {FIGURES_DIR / 'exp04_roc_curves.png'}")
    
    # Finalize PR Figure
    ax_pr.set_xlim([-0.02, 1.02])
    ax_pr.set_ylim([-0.02, 1.02])
    ax_pr.set_xlabel("Recall (Detection Rate)", fontsize=11)
    ax_pr.set_ylabel("Precision (Positive Predictive Value)", fontsize=11)
    ax_pr.set_title("Precision-Recall (PR) Curves Overlay", fontsize=12, fontweight="bold", pad=12)
    ax_pr.legend(frameon=True, loc="lower left", fontsize=9)
    plt.tight_layout()
    fig_pr.savefig(FIGURES_DIR / "exp04_pr_curves.png")
    plt.close(fig_pr)
    print(f"[+] Saved PR figure: {FIGURES_DIR / 'exp04_pr_curves.png'}")
    
    # Finalize Calibration Figure
    ax_cal.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.7, label="Perfect Calibration")
    ax_cal.set_xlim([-0.02, 1.02])
    ax_cal.set_ylim([-0.02, 1.02])
    ax_cal.set_xlabel("Mean Predicted Probability", fontsize=11)
    ax_cal.set_ylabel("Empirical Fraction of Positives", fontsize=11)
    ax_cal.set_title("Calibration Reliability Diagrams (10 Bins)", fontsize=12, fontweight="bold", pad=12)
    ax_cal.legend(frameon=True, loc="upper left", fontsize=9)
    plt.tight_layout()
    fig_cal.savefig(FIGURES_DIR / "exp04_calibration_reliability.png")
    plt.close(fig_cal)
    print(f"[+] Saved Calibration figure: {FIGURES_DIR / 'exp04_calibration_reliability.png'}")
    
    # Figure 4: Operational Low-FPR Recall Comparison
    df_op = pd.DataFrame(operational_tables)
    fig_soc, ax_soc = plt.subplots(figsize=(8, 4.5), dpi=300)
    sns.barplot(data=df_op, x="target_fpr_label", y="attack_recall", hue="model", ax=ax_soc)
    ax_soc.set_title("Operational Detection Recall Under Strict False-Alarm Budgets", fontsize=12, fontweight="bold", pad=12)
    ax_soc.set_ylabel("Attack Recall", fontsize=11)
    ax_soc.set_xlabel("SOC False Positive Rate Constraint", fontsize=11)
    ax_soc.set_ylim(0, 1.05)
    ax_soc.legend(title="Model", frameon=True, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    fig_soc.savefig(FIGURES_DIR / "exp04_operating_fpr_vs_recall.png")
    plt.close(fig_soc)
    print(f"[+] Saved SOC curve figure: {FIGURES_DIR / 'exp04_operating_fpr_vs_recall.png'}")
    
    # Save Tables & Metrics
    df_op.to_csv(TABLES_DIR / "exp04_operational_threshold_table.csv", index=False)
    pd.DataFrame(metrics_summary).to_csv(TABLES_DIR / "exp04_calibration_summary.csv", index=False)
    
    with open(METRICS_DIR / "exp04_calibration_metrics.json", "w") as f:
        json.dump({
            "experiment_id": "EXP-04",
            "metrics": metrics_summary,
            "operational_budgets": operational_tables
        }, f, indent=2)
    print(f"[+] EXP-04 Complete! Output tables and figures saved.")

if __name__ == "__main__":
    main()
