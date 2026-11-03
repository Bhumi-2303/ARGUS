#!/usr/bin/env python3
"""
ARGUS P2.2: Multi-Split Evaluation and Threshold Transfer Analysis.

Generates 5 independently seeded coordinate-disjoint train/cal/test partitions:
  - Preserves documented split constraints: Train ~70%, Cal ~15%, Test ~15%
  - Preserves class attack prevalence balancing (~72.58%)
  - Strictly verifies ZERO coordinate overlap across partitions in every split

For each split:
  - Trains in-domain XGBoost and LightGBM
  - Evaluates at default threshold 0.50
  - Tunes decision threshold on calibration split ONLY (maximizing F1)
  - Evaluates calibration-selected threshold on the untouched test partition
  - Reports all 13 metrics + confusion matrices + partition stats

Outputs:
  - results/experiments/p2_2_robustness/P2_2_INDEPENDENT_SPLIT_METRICS.csv
  - results/experiments/p2_2_robustness/P2_2_THRESHOLD_TRANSFER_ANALYSIS.csv
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb
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

FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
TARGET = "label"
DATA_DIR = Path("data/raw/legacy_package/argus_coral_data")
OUTPUT_DIR = Path("results/experiments/p2_2_robustness")
SEEDS = [42, 101, 202, 303, 404]


def compute_all_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict:
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
        "threshold": float(threshold),
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


def tune_threshold_on_calibration(y_cal: np.ndarray, p_cal: np.ndarray, metric="f1") -> tuple[float, float]:
    """Sweeps thresholds in [0.01, 0.99] to find threshold that maximizes metric on calibration data."""
    thresholds = np.linspace(0.01, 0.99, 99)
    best_th = 0.50
    best_score = -1.0

    for th in thresholds:
        pred = (p_cal >= th).astype(np.uint8)
        if metric == "f1":
            score = f1_score(y_cal, pred, zero_division=0)
        elif metric == "mcc":
            score = matthews_corrcoef(y_cal, pred)
        else:
            raise ValueError(f"Unknown metric {metric}")

        if score > best_score:
            best_score = score
            best_th = float(th)

    return best_th, best_score


def main():
    print("=" * 80)
    print("ARGUS P2.2: Multi-Split Independent Robustness Evaluation")
    print("=" * 80)
    t_start = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load full NF-ToN data pool
    print("\n[Step 1/4] Loading full NF-ToN data pool (13.14M rows)...")
    df_tr = pd.read_csv(DATA_DIR / "nfton_train_features.csv", usecols=FEATURES + [TARGET])
    df_te = pd.read_csv(DATA_DIR / "nfton_test_features.csv", usecols=FEATURES + [TARGET])
    df_all = pd.concat([df_tr, df_te], ignore_index=True)
    del df_tr, df_te

    total_pool_rows = len(df_all)
    print("  Aggregating unique 4D coordinate groups...")
    groups = df_all.groupby(FEATURES)[TARGET].agg(["count", "sum"]).reset_index()
    groups.rename(columns={"count": "n", "sum": "n_attack"}, inplace=True)
    groups["n_benign"] = groups["n"] - groups["n_attack"]
    n_unique_groups = len(groups)
    target_att_rate = groups["n_attack"].sum() / total_pool_rows
    print(f"  Pooled rows: {total_pool_rows:,} | Unique coordinate groups: {n_unique_groups:,} | Attack rate: {target_att_rate:.4%}")

    target_ratios = {"train": 0.70, "cal": 0.15, "test": 0.15}
    target_n = {k: total_pool_rows * r for k, r in target_ratios.items()}

    split_metrics_records = []
    threshold_transfer_records = []

    # 2. Iterate over 5 independent seeds
    for split_idx, split_seed in enumerate(SEEDS, 1):
        print("\n" + "-" * 80)
        print(f"Executing Independent Split {split_idx}/5 (Seed: {split_seed})...")
        print("-" * 80)

        # Shuffle groups using stable permutation with seed
        rng = np.random.RandomState(split_seed)
        perm = rng.permutation(len(groups))
        g_s = groups.iloc[perm].copy().reset_index(drop=True)
        g_s.sort_values(by="n", ascending=False, inplace=True, kind="stable")
        g_s.reset_index(drop=True, inplace=True)

        # Place top 2 massive groups into Train to avoid dominating Cal/Test bins
        assigned = {"train": [0, 1], "cal": [], "test": []}
        counts = {
            "train": {
                "n": int(g_s.loc[0, "n"] + g_s.loc[1, "n"]),
                "att": int(g_s.loc[0, "n_attack"] + g_s.loc[1, "n_attack"]),
            },
            "cal": {"n": 0, "att": 0},
            "test": {"n": 0, "att": 0},
        }

        g_records = g_s.iloc[2:].to_dict(orient="records")
        for offset, row in enumerate(g_records):
            idx = offset + 2
            gn = row["n"]
            ga = row["n_attack"]

            best_p = None
            best_loss = float("inf")
            for p in ["train", "cal", "test"]:
                new_n = counts[p]["n"] + gn
                fill_ratio = new_n / target_n[p]
                new_att = counts[p]["att"] + ga
                new_rate = new_att / new_n if new_n > 0 else 0.0

                loss = fill_ratio * 2.0 + abs(new_rate - target_att_rate) * 5.0
                if loss < best_loss:
                    best_loss = loss
                    best_p = p

            assigned[best_p].append(idx)
            counts[best_p]["n"] += gn
            counts[best_p]["att"] += ga

        g_s["partition"] = "unassigned"
        for p, indices in assigned.items():
            g_s.loc[indices, "partition"] = p

        # Verify zero coordinate overlap
        train_groups = set(zip(*(g_s.loc[assigned["train"], c] for c in FEATURES)))
        cal_groups = set(zip(*(g_s.loc[assigned["cal"], c] for c in FEATURES)))
        test_groups = set(zip(*(g_s.loc[assigned["test"], c] for c in FEATURES)))

        overlap_tr_cal = len(train_groups.intersection(cal_groups))
        overlap_tr_te = len(train_groups.intersection(test_groups))
        overlap_cal_te = len(cal_groups.intersection(test_groups))
        assert overlap_tr_cal == 0 and overlap_tr_te == 0 and overlap_cal_te == 0, "Coordinate overlap detected!"

        print(f"  Partition counts: Train={counts['train']['n']:,} ({len(train_groups):,} groups), "
              f"Cal={counts['cal']['n']:,} ({len(cal_groups):,} groups), "
              f"Test={counts['test']['n']:,} ({len(test_groups):,} groups)")
        print(f"  Attack rates: Train={counts['train']['att']/counts['train']['n']:.4%}, "
              f"Cal={counts['cal']['att']/counts['cal']['n']:.4%}, "
              f"Test={counts['test']['att']/counts['test']['n']:.4%}")
        print("  Zero coordinate overlap verified: True (0 shared groups)")

        # Map partitions back to df_all
        df_split = df_all.merge(g_s[FEATURES + ["partition"]], on=FEATURES, how="left")

        train_mask = (df_split["partition"] == "train").values
        cal_mask = (df_split["partition"] == "cal").values
        test_mask = (df_split["partition"] == "test").values

        X_train = df_split.loc[train_mask, FEATURES].values.astype(np.float32)
        y_train = df_split.loc[train_mask, TARGET].values.astype(np.uint8)

        X_cal = df_split.loc[cal_mask, FEATURES].values.astype(np.float32)
        y_cal = df_split.loc[cal_mask, TARGET].values.astype(np.uint8)

        X_test = df_split.loc[test_mask, FEATURES].values.astype(np.float32)
        y_test = df_split.loc[test_mask, TARGET].values.astype(np.uint8)
        del df_split

        # ---------------------------------------------------------------------
        # Train & Evaluate XGBoost
        # ---------------------------------------------------------------------
        print(f"  [Split {split_idx}] Training XGBoost on {len(y_train):,} samples...")
        t0_model = time.time()
        m_xgb = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=8,
            learning_rate=0.1,
            tree_method="hist",
            subsample=1.0,
            colsample_bytree=1.0,
            random_state=split_seed,
            n_jobs=-1,
            eval_metric="logloss",
        )
        m_xgb.fit(X_train, y_train)
        print(f"    Fitted XGBoost in {time.time() - t0_model:.1f}s")

        p_cal_xgb = m_xgb.predict_proba(X_cal)[:, 1].astype(np.float32)
        p_test_xgb = m_xgb.predict_proba(X_test)[:, 1].astype(np.float32)

        # Tune threshold on calibration ONLY
        best_th_f1_xgb, cal_f1_score_xgb = tune_threshold_on_calibration(y_cal, p_cal_xgb, metric="f1")
        cal_f1_at_05_xgb = f1_score(y_cal, (p_cal_xgb >= 0.50).astype(np.uint8), zero_division=0)
        cal_mcc_at_05_xgb = matthews_corrcoef(y_cal, (p_cal_xgb >= 0.50).astype(np.uint8))
        cal_mcc_at_tuned_xgb = matthews_corrcoef(y_cal, (p_cal_xgb >= best_th_f1_xgb).astype(np.uint8))

        # Evaluate on Test at default 0.50
        xgb_05_metrics = compute_all_metrics(y_test, p_test_xgb, threshold=0.50)
        xgb_05_metrics.update({
            "split_seed": split_seed,
            "split_index": split_idx,
            "model_family": "XGBoost",
            "threshold_rule": "default_0.50",
            "train_rows": len(y_train),
            "cal_rows": len(y_cal),
            "test_rows": len(y_test),
            "train_groups": len(train_groups),
            "cal_groups": len(cal_groups),
            "test_groups": len(test_groups),
            "test_attack_prevalence": float(np.mean(y_test)),
            "coordinate_overlap_verified": 0,
        })
        split_metrics_records.append(xgb_05_metrics)

        # Evaluate on Test at calibration-selected threshold
        xgb_cal_metrics = compute_all_metrics(y_test, p_test_xgb, threshold=best_th_f1_xgb)
        xgb_cal_metrics.update({
            "split_seed": split_seed,
            "split_index": split_idx,
            "model_family": "XGBoost",
            "threshold_rule": f"calibration_selected_{best_th_f1_xgb:.2f}",
            "train_rows": len(y_train),
            "cal_rows": len(y_cal),
            "test_rows": len(y_test),
            "train_groups": len(train_groups),
            "cal_groups": len(cal_groups),
            "test_groups": len(test_groups),
            "test_attack_prevalence": float(np.mean(y_test)),
            "coordinate_overlap_verified": 0,
        })
        split_metrics_records.append(xgb_cal_metrics)

        # Record threshold transfer analysis
        threshold_transfer_records.append({
            "split_seed": split_seed,
            "split_index": split_idx,
            "model_family": "XGBoost",
            "calibration_optimal_threshold": best_th_f1_xgb,
            "cal_f1_at_05": cal_f1_at_05_xgb,
            "cal_f1_at_tuned": cal_f1_score_xgb,
            "cal_mcc_at_05": cal_mcc_at_05_xgb,
            "cal_mcc_at_tuned": cal_mcc_at_tuned_xgb,
            "test_f1_at_05": xgb_05_metrics["f1_score"],
            "test_f1_at_tuned": xgb_cal_metrics["f1_score"],
            "test_mcc_at_05": xgb_05_metrics["mcc"],
            "test_mcc_at_tuned": xgb_cal_metrics["mcc"],
            "test_accuracy_at_05": xgb_05_metrics["accuracy"],
            "test_accuracy_at_tuned": xgb_cal_metrics["accuracy"],
            "test_specificity_at_05": xgb_05_metrics["specificity"],
            "test_specificity_at_tuned": xgb_cal_metrics["specificity"],
            "test_recall_at_05": xgb_05_metrics["recall"],
            "test_recall_at_tuned": xgb_cal_metrics["recall"],
            "delta_test_mcc_tuned_minus_05": xgb_cal_metrics["mcc"] - xgb_05_metrics["mcc"],
            "delta_test_f1_tuned_minus_05": xgb_cal_metrics["f1_score"] - xgb_05_metrics["f1_score"],
        })

        print(f"    XGBoost: Test MCC(0.50)={xgb_05_metrics['mcc']:.4f}, ROC-AUC={xgb_05_metrics['roc_auc']:.4f} | "
              f"Tuned th={best_th_f1_xgb:.2f} -> Test MCC={xgb_cal_metrics['mcc']:.4f}")

        # ---------------------------------------------------------------------
        # Train & Evaluate LightGBM
        # ---------------------------------------------------------------------
        print(f"  [Split {split_idx}] Training LightGBM on {len(y_train):,} samples...")
        t0_model = time.time()
        m_lgb = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=8,
            learning_rate=0.1,
            random_state=split_seed,
            n_jobs=-1,
            verbose=-1,
        )
        m_lgb.fit(X_train, y_train)
        print(f"    Fitted LightGBM in {time.time() - t0_model:.1f}s")

        p_cal_lgb = m_lgb.predict_proba(X_cal)[:, 1].astype(np.float32)
        p_test_lgb = m_lgb.predict_proba(X_test)[:, 1].astype(np.float32)

        best_th_f1_lgb, cal_f1_score_lgb = tune_threshold_on_calibration(y_cal, p_cal_lgb, metric="f1")
        cal_f1_at_05_lgb = f1_score(y_cal, (p_cal_lgb >= 0.50).astype(np.uint8), zero_division=0)
        cal_mcc_at_05_lgb = matthews_corrcoef(y_cal, (p_cal_lgb >= 0.50).astype(np.uint8))
        cal_mcc_at_tuned_lgb = matthews_corrcoef(y_cal, (p_cal_lgb >= best_th_f1_lgb).astype(np.uint8))

        lgb_05_metrics = compute_all_metrics(y_test, p_test_lgb, threshold=0.50)
        lgb_05_metrics.update({
            "split_seed": split_seed,
            "split_index": split_idx,
            "model_family": "LightGBM",
            "threshold_rule": "default_0.50",
            "train_rows": len(y_train),
            "cal_rows": len(y_cal),
            "test_rows": len(y_test),
            "train_groups": len(train_groups),
            "cal_groups": len(cal_groups),
            "test_groups": len(test_groups),
            "test_attack_prevalence": float(np.mean(y_test)),
            "coordinate_overlap_verified": 0,
        })
        split_metrics_records.append(lgb_05_metrics)

        lgb_cal_metrics = compute_all_metrics(y_test, p_test_lgb, threshold=best_th_f1_lgb)
        lgb_cal_metrics.update({
            "split_seed": split_seed,
            "split_index": split_idx,
            "model_family": "LightGBM",
            "threshold_rule": f"calibration_selected_{best_th_f1_lgb:.2f}",
            "train_rows": len(y_train),
            "cal_rows": len(y_cal),
            "test_rows": len(y_test),
            "train_groups": len(train_groups),
            "cal_groups": len(cal_groups),
            "test_groups": len(test_groups),
            "test_attack_prevalence": float(np.mean(y_test)),
            "coordinate_overlap_verified": 0,
        })
        split_metrics_records.append(lgb_cal_metrics)

        threshold_transfer_records.append({
            "split_seed": split_seed,
            "split_index": split_idx,
            "model_family": "LightGBM",
            "calibration_optimal_threshold": best_th_f1_lgb,
            "cal_f1_at_05": cal_f1_at_05_lgb,
            "cal_f1_at_tuned": cal_f1_score_lgb,
            "cal_mcc_at_05": cal_mcc_at_05_lgb,
            "cal_mcc_at_tuned": cal_mcc_at_tuned_lgb,
            "test_f1_at_05": lgb_05_metrics["f1_score"],
            "test_f1_at_tuned": lgb_cal_metrics["f1_score"],
            "test_mcc_at_05": lgb_05_metrics["mcc"],
            "test_mcc_at_tuned": lgb_cal_metrics["mcc"],
            "test_accuracy_at_05": lgb_05_metrics["accuracy"],
            "test_accuracy_at_tuned": lgb_cal_metrics["accuracy"],
            "test_specificity_at_05": lgb_05_metrics["specificity"],
            "test_specificity_at_tuned": lgb_cal_metrics["specificity"],
            "test_recall_at_05": lgb_05_metrics["recall"],
            "test_recall_at_tuned": lgb_cal_metrics["recall"],
            "delta_test_mcc_tuned_minus_05": lgb_cal_metrics["mcc"] - lgb_05_metrics["mcc"],
            "delta_test_f1_tuned_minus_05": lgb_cal_metrics["f1_score"] - lgb_05_metrics["f1_score"],
        })

        print(f"    LightGBM: Test MCC(0.50)={lgb_05_metrics['mcc']:.4f}, ROC-AUC={lgb_05_metrics['roc_auc']:.4f} | "
              f"Tuned th={best_th_f1_lgb:.2f} -> Test MCC={lgb_cal_metrics['mcc']:.4f}")

    # 3. Save CSV deliverables
    print("\n[Step 3/4] Saving deliverables to results/experiments/p2_2_robustness/...")
    df_split_metrics = pd.DataFrame(split_metrics_records)
    csv_split_metrics = OUTPUT_DIR / "P2_2_INDEPENDENT_SPLIT_METRICS.csv"
    df_split_metrics.to_csv(csv_split_metrics, index=False)
    print(f"  Saved Split Metrics Table: {csv_split_metrics} ({len(df_split_metrics)} rows)")

    df_thresh_transfer = pd.DataFrame(threshold_transfer_records)
    csv_thresh_transfer = OUTPUT_DIR / "P2_2_THRESHOLD_TRANSFER_ANALYSIS.csv"
    df_thresh_transfer.to_csv(csv_thresh_transfer, index=False)
    print(f"  Saved Threshold Transfer Analysis: {csv_thresh_transfer} ({len(df_thresh_transfer)} rows)")

    # 4. Print aggregate summary stats across 5 splits
    print("\n" + "=" * 80)
    print("SUMMARY OF PARTITION VARIATION (DEFAULT THRESHOLD 0.50) ACROSS 5 SEEDS")
    print("=" * 80)
    df_05 = df_split_metrics[df_split_metrics["threshold_rule"] == "default_0.50"]
    for model_name in ["XGBoost", "LightGBM"]:
        sub = df_05[df_05["model_family"] == model_name]
        print(f"\n{model_name} (5 Independent Group Splits, th=0.50):")
        print(f"  MCC:       {sub['mcc'].mean():.4f} +/- {sub['mcc'].std():.4f} [Min: {sub['mcc'].min():.4f}, Max: {sub['mcc'].max():.4f}]")
        print(f"  Accuracy:  {sub['accuracy'].mean():.4f} +/- {sub['accuracy'].std():.4f}")
        print(f"  F1 Score:  {sub['f1_score'].mean():.4f} +/- {sub['f1_score'].std():.4f}")
        print(f"  ROC-AUC:   {sub['roc_auc'].mean():.4f} +/- {sub['roc_auc'].std():.4f} [Min: {sub['roc_auc'].min():.4f}, Max: {sub['roc_auc'].max():.4f}]")
        print(f"  PR-AUC:    {sub['pr_auc'].mean():.4f} +/- {sub['pr_auc'].std():.4f}")
        print(f"  Spec:      {sub['specificity'].mean():.4f} +/- {sub['specificity'].std():.4f}")

    print(f"\nTotal Multi-Split Execution Time: {time.time() - t_start:.2f}s")


if __name__ == "__main__":
    main()
