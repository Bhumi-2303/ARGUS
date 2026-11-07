#!/usr/bin/env python3
"""
ARGUS P1-1: NF-ToN-IoT-v2 In-Domain Baseline Visualization Script.

Generates 6 publication-quality figures from actual test predictions and verified historical results:
- fig01_performance_comparison.png: Multi-model grouped comparison (XGB, LGBM, CORAL, Source-only)
- fig02_roc_curves.png: Test set ROC curves for XGBoost and LightGBM
- fig03_precision_recall_curves.png: Test set PR curves for XGBoost and LightGBM
- fig04_confusion_matrices.png: 2x2 grid of confusion matrices (uncalibrated & calibrated)
- fig05_threshold_analysis.png: Threshold sensitivity curves (calibration vs. test)
- fig06_calibration_quality.png: Reliability diagrams and Brier score calibration plots
"""

import json
import math
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    auc,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)

# Set publication style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})

EXP_DIR = Path("results/experiments/p1_1_nfton_in_domain")
FIG_DIR = EXP_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    print("Loading test predictions and experiment metrics...")
    df_xgb = pd.read_parquet(EXP_DIR / "xgboost_test_predictions.parquet")
    df_lgb = pd.read_parquet(EXP_DIR / "lightgbm_test_predictions.parquet")
    with open(EXP_DIR / "nfton_calibration_thresholds.json") as f:
        calib_meta = json.load(f)
    with open(EXP_DIR / "calibration_curves.json") as f:
        calib_curves = json.load(f)
    with open(EXP_DIR / "nfton_in_domain_metrics.json") as f:
        in_domain_metrics = json.load(f)

    # Load verified five-model comparison
    historical_path = Path("results/verified/five_model_complete_comparison.csv")
    df_historical = pd.read_csv(historical_path) if historical_path.exists() else None

    return df_xgb, df_lgb, calib_meta, calib_curves, in_domain_metrics, df_historical


def plot_fig01_performance_comparison(in_domain_metrics, df_historical):
    print("Generating Figure 1: Performance Comparison...")
    # Gather comparison models
    # Clean Class-Aware CORAL and Source-only
    coral_row = df_historical[df_historical["Model"].str.contains("Clean Class-aware", na=False)].iloc[0]
    source_row = df_historical[df_historical["Model"].str.contains("Source-only", na=False)].iloc[0]
    dann_row = df_historical[df_historical["Model"].str.contains("DANN", na=False)].iloc[0]

    xgb_cal = [m for m in in_domain_metrics if m["Model"] == "XGBoost" and m["Threshold"] != 0.5][0]
    lgb_cal = [m for m in in_domain_metrics if m["Model"] == "LightGBM" and m["Threshold"] != 0.5][0]

    models = [
        "Source-Only XGBoost",
        "DANN (Adapted)",
        "Clean Class-Aware CORAL",
        "XGBoost (In-Domain Supervised)",
        "LightGBM (In-Domain Supervised)",
    ]
    metrics_keys = ["balanced_accuracy", "mcc", "roc_auc", "pr_auc"]
    metrics_labels = ["Balanced Accuracy", "MCC", "ROC-AUC", "PR-AUC"]

    data = {
        "Source-Only XGBoost": [
            source_row["Balanced_Accuracy"],
            source_row["MCC"],
            source_row["ROC_AUC"],
            source_row["PR_AUC"],
        ],
        "DANN (Adapted)": [
            dann_row["Balanced_Accuracy"],
            dann_row["MCC"],
            dann_row["ROC_AUC"],
            dann_row["PR_AUC"],
        ],
        "Clean Class-Aware CORAL": [
            coral_row["Balanced_Accuracy"],
            coral_row["MCC"],
            coral_row["ROC_AUC"],
            coral_row["PR_AUC"],
        ],
        "XGBoost (In-Domain Supervised)": [
            xgb_cal["balanced_accuracy"],
            xgb_cal["mcc"],
            xgb_cal["roc_auc"],
            xgb_cal["pr_auc"],
        ],
        "LightGBM (In-Domain Supervised)": [
            lgb_cal["balanced_accuracy"],
            lgb_cal["mcc"],
            lgb_cal["roc_auc"],
            lgb_cal["pr_auc"],
        ],
    }

    x = np.arange(len(metrics_labels))
    width = 0.16
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ["#7f7f7f", "#9467bd", "#e377c2", "#1f77b4", "#2ca02c"]
    for i, (model_name, vals) in enumerate(data.items()):
        offset = (i - 2) * width
        rects = ax.bar(x + offset, vals, width, label=model_name, color=colors[i], edgecolor="black", linewidth=0.8)
        # Add value labels on top of bars
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3 if height >= 0 else -10),
                textcoords="offset points",
                ha="center",
                va="bottom" if height >= 0 else "top",
                fontsize=8,
                rotation=0,
            )

    ax.set_ylabel("Metric Value")
    ax.set_title("NF-ToN-IoT-v2 Test Set Performance: Cross-Domain vs. In-Domain Supervised Baselines")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_labels, fontweight="bold")
    ax.set_ylim(-0.15, 1.08)
    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.legend(loc="upper left", framealpha=0.95)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig01_performance_comparison.png", dpi=300)
    plt.close(fig)


def plot_fig02_roc_curves(df_xgb, df_lgb):
    print("Generating Figure 2: ROC Curves...")
    fig, ax = plt.subplots(figsize=(8, 7))

    y_true = df_xgb["y_true"].values
    fpr_xgb, tpr_xgb, _ = roc_curve(y_true, df_xgb["y_prob"].values)
    auc_xgb = auc(fpr_xgb, tpr_xgb)

    fpr_lgb, tpr_lgb, _ = roc_curve(y_true, df_lgb["y_prob"].values)
    auc_lgb = auc(fpr_lgb, tpr_lgb)

    ax.plot(fpr_xgb, tpr_xgb, color="#1f77b4", lw=2, label=f"XGBoost In-Domain (AUC = {auc_xgb:.4f})")
    ax.plot(fpr_lgb, tpr_lgb, color="#2ca02c", lw=2, linestyle="--", label=f"LightGBM In-Domain (AUC = {auc_lgb:.4f})")
    ax.plot([0, 1], [0, 1], color="grey", lw=1.2, linestyle=":", label="Chance (AUC = 0.5000)")

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.02])
    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Recall / Detection Rate)")
    ax.set_title("Receiver Operating Characteristic (ROC) on Frozen NF-ToN Test Set (N = 2,627,177)")
    ax.legend(loc="lower right", framealpha=0.95)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig02_roc_curves.png", dpi=300)
    plt.close(fig)


def plot_fig03_precision_recall_curves(df_xgb, df_lgb):
    print("Generating Figure 3: Precision-Recall Curves...")
    fig, ax = plt.subplots(figsize=(8, 7))

    y_true = df_xgb["y_true"].values
    prior = float(y_true.mean())

    p_xgb, r_xgb, _ = precision_recall_curve(y_true, df_xgb["y_prob"].values)
    pr_auc_xgb = auc(r_xgb, p_xgb)
    ap_xgb = average_precision_score(y_true, df_xgb["y_prob"].values)

    p_lgb, r_lgb, _ = precision_recall_curve(y_true, df_lgb["y_prob"].values)
    pr_auc_lgb = auc(r_lgb, p_lgb)
    ap_lgb = average_precision_score(y_true, df_lgb["y_prob"].values)

    ax.plot(r_xgb, p_xgb, color="#1f77b4", lw=2, label=f"XGBoost In-Domain (AP = {ap_xgb:.4f}, PR-AUC = {pr_auc_xgb:.4f})")
    ax.plot(r_lgb, p_lgb, color="#2ca02c", lw=2, linestyle="--", label=f"LightGBM In-Domain (AP = {ap_lgb:.4f}, PR-AUC = {pr_auc_lgb:.4f})")
    ax.axhline(prior, color="grey", lw=1.2, linestyle=":", label=f"Prevalence Prior (Attack = {prior*100:.1f}%)")

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.5, 1.02])
    ax.set_xlabel("Recall (Detection Rate)")
    ax.set_ylabel("Precision (Positive Predictive Value)")
    ax.set_title("Precision-Recall (PR) Curves on Frozen NF-ToN Test Set (N = 2,627,177)")
    ax.legend(loc="lower left", framealpha=0.95)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig03_precision_recall_curves.png", dpi=300)
    plt.close(fig)


def plot_fig04_confusion_matrices(df_xgb, df_lgb, calib_meta):
    print("Generating Figure 4: Confusion Matrices...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    th_xgb = calib_meta["xgboost"]["selected_threshold"]
    th_lgb = calib_meta["lightgbm"]["selected_threshold"]
    y_true = df_xgb["y_true"].values

    configs = [
        (df_xgb["y_prob"].values >= 0.50, f"XGBoost (Threshold = 0.50)\nAccuracy = 93.35%, MCC = 0.8307", axes[0, 0]),
        (df_xgb["y_prob"].values >= th_xgb, f"XGBoost (Calibrated Threshold = {th_xgb:.2f})\nAccuracy = 93.32%, MCC = 0.8320", axes[0, 1]),
        (df_lgb["y_prob"].values >= 0.50, f"LightGBM (Threshold = 0.50)\nAccuracy = 93.32%, MCC = 0.8300", axes[1, 0]),
        (df_lgb["y_prob"].values >= th_lgb, f"LightGBM (Calibrated Threshold = {th_lgb:.2f})\nAccuracy = 93.29%, MCC = 0.8315", axes[1, 1]),
    ]

    for y_pred, title, ax in configs:
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        cm_norm = cm.astype(float) / cm.sum(axis=1)[:, np.newaxis] * 100
        labels = [
            [f"TN\n{cm[0, 0]:,}\n({cm_norm[0, 0]:.1f}%)", f"FP\n{cm[0, 1]:,}\n({cm_norm[0, 1]:.1f}%)"],
            [f"FN\n{cm[1, 0]:,}\n({cm_norm[1, 0]:.1f}%)", f"TP\n{cm[1, 1]:,}\n({cm_norm[1, 1]:.1f}%)"],
        ]
        sns.heatmap(
            cm,
            annot=labels,
            fmt="",
            cmap="Blues",
            cbar=False,
            ax=ax,
            annot_kws={"size": 11, "weight": "bold"},
        )
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Predicted Label")
        ax.set_ylabel("True Ground Truth Label")
        ax.set_xticklabels(["Benign (0)", "Attack (1)"])
        ax.set_yticklabels(["Benign (0)", "Attack (1)"])

    plt.suptitle("Confusion Matrices on Frozen NF-ToN-IoT-v2 Test Set (N = 2,627,177)", fontsize=14, y=0.98)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig04_confusion_matrices.png", dpi=300)
    plt.close(fig)


def plot_fig05_threshold_analysis(calib_curves, calib_meta, df_xgb):
    print("Generating Figure 5: Threshold Sensitivity Analysis...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: Calibration Set Curves
    curves_xgb = pd.DataFrame(calib_curves["xgboost"])
    th_selected = calib_meta["xgboost"]["selected_threshold"]

    ax1.plot(curves_xgb["threshold"], curves_xgb["mcc"], color="#d62728", lw=2, label="MCC (Objective)")
    ax1.plot(curves_xgb["threshold"], curves_xgb["balanced_accuracy"], color="#1f77b4", lw=1.8, label="Balanced Accuracy")
    ax1.plot(curves_xgb["threshold"], curves_xgb["recall"], color="#2ca02c", lw=1.8, linestyle="--", label="Recall")
    ax1.plot(curves_xgb["threshold"], curves_xgb["specificity"], color="#ff7f0e", lw=1.8, linestyle="--", label="Specificity")
    ax1.plot(curves_xgb["threshold"], curves_xgb["fpr"], color="#9467bd", lw=1.5, linestyle=":", label="FPR")
    ax1.axvline(th_selected, color="black", linestyle="-.", lw=1.5, label=f"Selected Threshold ({th_selected:.2f})")

    ax1.set_xlabel("Decision Threshold")
    ax1.set_ylabel("Metric Value")
    ax1.set_title("Calibration Set Threshold Sweep (N = 2,101,742)")
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([-0.05, 1.05])
    ax1.legend(loc="lower left", framealpha=0.95, fontsize=9)

    # Panel 2: Test Set Sweep for Comparison (Demonstrating Generalization)
    thresholds = np.linspace(0.05, 0.95, 37)
    y_true = df_xgb["y_true"].values
    y_prob = df_xgb["y_prob"].values
    test_mcc, test_bacc, test_rec, test_spec, test_fpr = [], [], [], [], []

    for th in thresholds:
        yp = (y_prob >= th).astype(np.uint8)
        cm = confusion_matrix(y_true, yp, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        denom = (
            math.sqrt(float(tp + fp))
            * math.sqrt(float(tp + fn))
            * math.sqrt(float(tn + fp))
            * math.sqrt(float(tn + fn))
        )
        test_mcc.append(float((float(tp) * float(tn) - float(fp) * float(fn)) / denom) if denom > 0 else 0.0)
        test_rec.append(float(tp / (tp + fn)))
        test_spec.append(float(tn / (tn + fp)))
        test_bacc.append(0.5 * (test_rec[-1] + test_spec[-1]))
        test_fpr.append(float(fp / (fp + tn)))

    ax2.plot(thresholds, test_mcc, color="#d62728", lw=2, label="Test MCC")
    ax2.plot(thresholds, test_bacc, color="#1f77b4", lw=1.8, label="Test Balanced Accuracy")
    ax2.plot(thresholds, test_rec, color="#2ca02c", lw=1.8, linestyle="--", label="Test Recall")
    ax2.plot(thresholds, test_spec, color="#ff7f0e", lw=1.8, linestyle="--", label="Test Specificity")
    ax2.plot(thresholds, test_fpr, color="#9467bd", lw=1.5, linestyle=":", label="Test FPR")
    ax2.axvline(th_selected, color="black", linestyle="-.", lw=1.5, label=f"Frozen Calibrated ({th_selected:.2f})")

    ax2.set_xlabel("Decision Threshold")
    ax2.set_ylabel("Metric Value")
    ax2.set_title("Frozen Test Set Performance vs. Threshold (N = 2,627,177)")
    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([-0.05, 1.05])
    ax2.legend(loc="lower left", framealpha=0.95, fontsize=9)

    plt.suptitle("Threshold Calibration Dynamics: Calibration Sweep vs. Frozen Test Generalization", fontsize=13)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig05_threshold_analysis.png", dpi=300)
    plt.close(fig)


def plot_fig06_calibration_quality(df_xgb, df_lgb):
    print("Generating Figure 6: Probability Calibration & Reliability Diagrams...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    y_true = df_xgb["y_true"].values
    prob_xgb = df_xgb["y_prob"].values
    prob_lgb = df_lgb["y_prob"].values

    # Compute Brier scores
    brier_xgb = brier_score_loss(y_true, prob_xgb)
    brier_lgb = brier_score_loss(y_true, prob_lgb)

    # Reliability curves (10 bins)
    fraction_pos_xgb, mean_prob_xgb = calibration_curve(y_true, prob_xgb, n_bins=10, strategy="uniform")
    fraction_pos_lgb, mean_prob_lgb = calibration_curve(y_true, prob_lgb, n_bins=10, strategy="uniform")

    ax1.plot([0, 1], [0, 1], color="grey", linestyle=":", lw=1.5, label="Perfect Calibration")
    ax1.plot(mean_prob_xgb, fraction_pos_xgb, marker="s", color="#1f77b4", lw=2, label=f"XGBoost (Brier = {brier_xgb:.4f})")
    ax1.plot(mean_prob_lgb, fraction_pos_lgb, marker="o", color="#2ca02c", lw=2, linestyle="--", label=f"LightGBM (Brier = {brier_lgb:.4f})")

    ax1.set_xlabel("Mean Predicted Probability")
    ax1.set_ylabel("Empirical Fraction of Positives (Attacks)")
    ax1.set_title("Reliability Diagram (Calibration Curve)")
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.0])
    ax1.legend(loc="upper left", framealpha=0.95)

    # Probability histograms
    ax2.hist(prob_xgb, bins=30, alpha=0.6, color="#1f77b4", label="XGBoost Probabilities", density=True)
    ax2.hist(prob_lgb, bins=30, alpha=0.6, color="#2ca02c", label="LightGBM Probabilities", density=True)
    ax2.set_xlabel("Predicted Probability of Attack P(y=1)")
    ax2.set_ylabel("Probability Density")
    ax2.set_title("Test Set Predicted Probability Distributions")
    ax2.legend(loc="upper center", framealpha=0.95)

    plt.suptitle("Probability Calibration Analysis on Frozen Test Set (N = 2,627,177)", fontsize=13)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig06_calibration_quality.png", dpi=300)
    plt.close(fig)


def main():
    print("================================================================================")
    print("ARGUS P1-1: Generating Publication-Quality Figures")
    print("================================================================================")
    df_xgb, df_lgb, calib_meta, calib_curves, in_domain_metrics, df_historical = load_data()

    plot_fig01_performance_comparison(in_domain_metrics, df_historical)
    plot_fig02_roc_curves(df_xgb, df_lgb)
    plot_fig03_precision_recall_curves(df_xgb, df_lgb)
    plot_fig04_confusion_matrices(df_xgb, df_lgb, calib_meta)
    plot_fig05_threshold_analysis(calib_curves, calib_meta, df_xgb)
    plot_fig06_calibration_quality(df_xgb, df_lgb)

    print("\nAll 6 publication figures generated successfully in:")
    print(f"  {FIG_DIR.resolve()}")
    for f in FIG_DIR.glob("*.png"):
        print(f"    {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    print("================================================================================")


if __name__ == "__main__":
    main()
