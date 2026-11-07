#!/usr/bin/env python3
"""
ARGUS P2: Experiment A — Seen vs Unseen Coordinate Analysis.

Evaluates the saved P1-1 in-domain supervised models (XGBoost and LightGBM)
on the frozen NF-ToN test set segmented by coordinate novelty:
  1. Seen in adaptation training (N = 2,592,203)
  2. Seen in calibration but not adaptation (N = 3,831)
  3. Unseen in both (N = 31,143)
  4. Overall test set (N = 2,627,177)

Evaluation is conducted at:
  - Default threshold (0.50)
  - Calibrated threshold from P1-1 (XGBoost 0.57, LightGBM 0.55)
Without re-tuning thresholds on the test subsets.
"""

import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    auc,
    average_precision_score,
    balanced_accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from scipy import stats

FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
TARGET = "label"

OUTPUT_DIR = Path("results/experiments/p2_coordinate_generalization")
DATA_DIR = Path("data/raw/legacy_package/argus_coral_data")
P1_1_DIR = Path("results/experiments/p1_1_nfton_in_domain")


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict:
    """Calculate all 13 standard classification metrics."""
    y_pred = (y_prob >= threshold).astype(np.uint8)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    total = int(tn + fp + fn + tp)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    bacc = float(balanced_accuracy_score(y_true, y_pred))
    kappa = float(cohen_kappa_score(y_true, y_pred))
    mcc = float(matthews_corrcoef(y_true, y_pred))

    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = float("nan")

    try:
        ap = float(average_precision_score(y_true, y_prob))
    except Exception:
        ap = float("nan")

    try:
        p_curve, r_curve, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = float(auc(r_curve, p_curve))
    except Exception:
        pr_auc = float("nan")

    return {
        "total_samples": total,
        "TP": int(tp),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "balanced_accuracy": bacc,
        "cohen_kappa": kappa,
        "mcc": mcc,
        "specificity": spec,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "roc_auc": roc_auc,
        "average_precision": ap,
        "pr_auc": pr_auc,
    }


def compute_bootstrap_cis(
    y_true: np.ndarray, y_prob: np.ndarray, threshold: float, n_bootstraps: int = 500, seed: int = 42
) -> dict:
    """Compute 95% bootstrap confidence intervals for key metrics."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    metrics_acc = []
    metrics_mcc = []
    metrics_bacc = []
    metrics_f1 = []

    # If dataset is very large, subsample for bootstrapping to keep runtime fast
    subsample_size = min(n, 100000)

    for _ in range(n_bootstraps):
        idx = rng.choice(n, size=subsample_size, replace=True)
        yt_boot = y_true[idx]
        yp_boot = (y_prob[idx] >= threshold).astype(np.uint8)

        # Check for single class
        if len(np.unique(yt_boot)) < 2:
            continue

        metrics_acc.append(accuracy_score(yt_boot, yp_boot))
        metrics_mcc.append(matthews_corrcoef(yt_boot, yp_boot))
        metrics_bacc.append(balanced_accuracy_score(yt_boot, yp_boot))
        metrics_f1.append(f1_score(yt_boot, yp_boot, zero_division=0))

    ci_dict = {}
    for name, arr in [("accuracy", metrics_acc), ("mcc", metrics_mcc), ("balanced_accuracy", metrics_bacc), ("f1_score", metrics_f1)]:
        if len(arr) > 0:
            low = float(np.percentile(arr, 2.5))
            high = float(np.percentile(arr, 97.5))
            ci_dict[f"{name}_ci_lower"] = low
            ci_dict[f"{name}_ci_upper"] = high
        else:
            ci_dict[f"{name}_ci_lower"] = float("nan")
            ci_dict[f"{name}_ci_upper"] = float("nan")
    return ci_dict


def main():
    print("=" * 80)
    print("ARGUS P2: Experiment A — Seen vs Unseen Coordinate Analysis")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load coordinates from training, calibration, and test splits
    print("\n[Step 1/5] Extracting 4D coordinates across partitions...")
    t0 = time.time()
    
    print("  Loading adaptation training coordinates...")
    df_adapt = pd.read_csv(DATA_DIR / "nfton_train_adaptation.csv", usecols=FEATURES)
    adapt_coords = set(map(tuple, df_adapt.drop_duplicates().values))
    print(f"  Adaptation unique coordinates: {len(adapt_coords):,}")
    del df_adapt

    print("  Loading calibration coordinates...")
    df_cal = pd.read_csv(DATA_DIR / "nfton_train_calibration.csv", usecols=FEATURES)
    cal_coords = set(map(tuple, df_cal.drop_duplicates().values))
    print(f"  Calibration unique coordinates: {len(cal_coords):,}")
    del df_cal

    print("  Loading test features and coordinates...")
    df_test = pd.read_csv(DATA_DIR / "nfton_test_features.csv")
    test_tuples = list(map(tuple, df_test[FEATURES].values))
    y_true_all = df_test[TARGET].values.astype(np.uint8)
    print(f"  Test rows: {len(test_tuples):,}")

    # 2. Segment test rows
    print("\n[Step 2/5] Segmenting test rows by coordinate overlap status...")
    mask_seen_adapt = np.array([t in adapt_coords for t in test_tuples], dtype=bool)
    mask_seen_cal_only = np.array([(t not in adapt_coords and t in cal_coords) for t in test_tuples], dtype=bool)
    mask_unseen_both = np.array([(t not in adapt_coords and t not in cal_coords) for t in test_tuples], dtype=bool)
    mask_overall = np.ones(len(test_tuples), dtype=bool)

    n_adapt = int(mask_seen_adapt.sum())
    n_cal_only = int(mask_seen_cal_only.sum())
    n_unseen = int(mask_unseen_both.sum())
    n_total = len(test_tuples)

    print(f"  - Seen in adaptation:        {n_adapt:,} ({n_adapt/n_total*100:.2f}%)")
    print(f"  - Seen in calibration only:  {n_cal_only:,} ({n_cal_only/n_total*100:.2f}%)")
    print(f"  - Unseen in both:            {n_unseen:,} ({n_unseen/n_total*100:.2f}%)")
    print(f"  - Total test observations:   {n_total:,}")

    assert n_adapt == 2592203, f"Expected 2,592,203 seen in adapt, got {n_adapt}"
    assert n_cal_only == 3831, f"Expected 3,831 seen in cal only, got {n_cal_only}"
    assert n_unseen == 31143, f"Expected 31,143 unseen, got {n_unseen}"
    print("  [PASS] Subset partitions verified against audit checksums.")

    # Save masks for downstream scripts
    np.savez_compressed(
        OUTPUT_DIR / "test_coordinate_masks.npz",
        mask_seen_adapt=mask_seen_adapt,
        mask_seen_cal_only=mask_seen_cal_only,
        mask_unseen_both=mask_unseen_both,
    )
    print(f"  Saved boolean partition masks to {OUTPUT_DIR / 'test_coordinate_masks.npz'}")

    # 3. Load saved P1-1 predictions
    print("\n[Step 3/5] Loading P1-1 model predictions...")
    xgb_preds_df = pd.read_parquet(P1_1_DIR / "xgboost_test_predictions.parquet")
    lgb_preds_df = pd.read_parquet(P1_1_DIR / "lightgbm_test_predictions.parquet")

    # Verify alignment
    np.testing.assert_array_equal(xgb_preds_df["y_true"].values, y_true_all)
    np.testing.assert_array_equal(lgb_preds_df["y_true"].values, y_true_all)
    print("  Prediction ground truths align with test set.")

    # Calibrated thresholds from P1-1
    tau_xgb = 0.57
    tau_lgb = 0.55

    subsets = {
        "seen_in_adaptation": mask_seen_adapt,
        "seen_in_calibration_only": mask_seen_cal_only,
        "unseen_in_both": mask_unseen_both,
        "overall_test": mask_overall,
    }

    models = {
        "XGBoost": {
            "y_prob": xgb_preds_df["y_prob"].values,
            "tau_cal": tau_xgb,
        },
        "LightGBM": {
            "y_prob": lgb_preds_df["y_prob"].values,
            "tau_cal": tau_lgb,
        },
    }

    # 4. Evaluate each model on each subset
    print("\n[Step 4/5] Evaluating performance across subsets...")
    results = []

    for model_name, model_data in models.items():
        y_prob = model_data["y_prob"]
        tau_cal = model_data["tau_cal"]

        for subset_name, mask in subsets.items():
            yt_sub = y_true_all[mask]
            yp_sub = y_prob[mask]
            n_sub = len(yt_sub)
            n_att_sub = int(yt_sub.sum())
            att_prev = n_att_sub / n_sub if n_sub > 0 else 0.0

            # Evaluate at threshold 0.50
            m_05 = compute_metrics(yt_sub, yp_sub, threshold=0.50)
            ci_05 = compute_bootstrap_cis(yt_sub, yp_sub, threshold=0.50)

            row_05 = {
                "model": model_name,
                "subset": subset_name,
                "threshold_rule": "default_0.50",
                "threshold": 0.50,
                "attack_prevalence": att_prev,
                **m_05,
                **ci_05,
            }
            results.append(row_05)

            # Evaluate at calibrated threshold
            m_cal = compute_metrics(yt_sub, yp_sub, threshold=tau_cal)
            ci_cal = compute_bootstrap_cis(yt_sub, yp_sub, threshold=tau_cal)

            row_cal = {
                "model": model_name,
                "subset": subset_name,
                "threshold_rule": f"calibrated_{tau_cal:.2f}",
                "threshold": tau_cal,
                "attack_prevalence": att_prev,
                **m_cal,
                **ci_cal,
            }
            results.append(row_cal)

            print(
                f"  [{model_name}] {subset_name:<26} (N={n_sub:>9,}) | "
                f"th=0.50 MCC={m_05['mcc']:.4f} BAcc={m_05['balanced_accuracy']:.4f} F1={m_05['f1_score']:.4f} | "
                f"th={tau_cal:.2f} MCC={m_cal['mcc']:.4f} BAcc={m_cal['balanced_accuracy']:.4f} F1={m_cal['f1_score']:.4f}"
            )

    # 5. Statistical hypothesis tests comparing seen vs unseen
    print("\n[Step 5/5] Conducting statistical significance tests (Seen vs Unseen)...")
    stat_summary = {}

    for model_name, model_data in models.items():
        y_prob = model_data["y_prob"]
        tau_cal = model_data["tau_cal"]

        # Probability distribution comparison
        prob_seen = y_prob[mask_seen_adapt]
        prob_unseen = y_prob[mask_unseen_both]

        # Kolmogorov-Smirnov test on predicted probabilities
        ks_stat, ks_pval = stats.ks_2samp(prob_seen, prob_unseen)

        # Accuracy comparison (Two-proportion z-test)
        acc_seen = accuracy_score(y_true_all[mask_seen_adapt], (prob_seen >= tau_cal).astype(int))
        acc_unseen = accuracy_score(y_true_all[mask_unseen_both], (prob_unseen >= tau_cal).astype(int))

        count = np.array([int(acc_seen * n_adapt), int(acc_unseen * n_unseen)])
        nobs = np.array([n_adapt, n_unseen])
        p_pool = count.sum() / nobs.sum()
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_adapt + 1 / n_unseen))
        z_stat = (acc_seen - acc_unseen) / se
        p_val_z = 2 * (1 - stats.norm.cdf(abs(z_stat)))

        stat_summary[model_name] = {
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_pval),
            "acc_seen": float(acc_seen),
            "acc_unseen": float(acc_unseen),
            "acc_difference": float(acc_seen - acc_unseen),
            "two_prop_z_statistic": float(z_stat),
            "two_prop_pvalue": float(p_val_z),
            "statistically_significant": bool(p_val_z < 0.001),
        }

        print(f"  [{model_name}] KS stat: {ks_stat:.4f} (p={ks_pval:.2e}), Acc Diff: {acc_seen-acc_unseen:.4f} (z={z_stat:.2f}, p={p_val_z:.2e})")

    # Save results to CSV
    metrics_df = pd.DataFrame(results)
    csv_path = OUTPUT_DIR / "seen_unseen_metrics.csv"
    metrics_df.to_csv(csv_path, index=False)
    print(f"\nSaved metrics table to: {csv_path}")

    # Save summary JSON
    summary_data = {
        "experiment": "ARGUS P2 Experiment A: Seen vs Unseen Coordinate Analysis",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "partition_sizes": {
            "seen_in_adaptation": n_adapt,
            "seen_in_calibration_only": n_cal_only,
            "unseen_in_both": n_unseen,
            "overall_test": n_total,
        },
        "subset_attack_prevalences": {
            "seen_in_adaptation": float(y_true_all[mask_seen_adapt].mean()),
            "seen_in_calibration_only": float(y_true_all[mask_seen_cal_only].mean()),
            "unseen_in_both": float(y_true_all[mask_unseen_both].mean()),
            "overall_test": float(y_true_all.mean()),
        },
        "statistical_tests": stat_summary,
        "key_findings": {
            "xgboost_mcc_drop": float(
                metrics_df[(metrics_df["model"] == "XGBoost") & (metrics_df["subset"] == "seen_in_adaptation") & (metrics_df["threshold_rule"] == "calibrated_0.57")]["mcc"].values[0]
                - metrics_df[(metrics_df["model"] == "XGBoost") & (metrics_df["subset"] == "unseen_in_both") & (metrics_df["threshold_rule"] == "calibrated_0.57")]["mcc"].values[0]
            ),
            "lightgbm_mcc_drop": float(
                metrics_df[(metrics_df["model"] == "LightGBM") & (metrics_df["subset"] == "seen_in_adaptation") & (metrics_df["threshold_rule"] == "calibrated_0.55")]["mcc"].values[0]
                - metrics_df[(metrics_df["model"] == "LightGBM") & (metrics_df["subset"] == "unseen_in_both") & (metrics_df["threshold_rule"] == "calibrated_0.55")]["mcc"].values[0]
            ),
        },
    }

    json_path = OUTPUT_DIR / "coordinate_overlap_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"Saved overlap summary JSON to: {json_path}")
    print(f"\nExperiment A completed in {time.time()-t0:.1f}s.")


if __name__ == "__main__":
    main()
