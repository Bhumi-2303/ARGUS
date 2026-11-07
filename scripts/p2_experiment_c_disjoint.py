#!/usr/bin/env python3
"""
ARGUS P2: Experiment C — Coordinate-Disjoint Supervised Evaluation.

Protocol:
1. Constructs a strictly group-aware split where NO 4D feature coordinate appears
   in more than one partition (Train 70%, Calibration 15%, Test 15%).
2. Documents partition sizes, attack rates, coordinate group counts in group_split_manifest.json.
3. Trains fresh XGBoost and LightGBM models on the coordinate-disjoint training partition
   across 3 random seeds (42, 123, 456) using identical hyperparameters to P1-1.
4. Selects optimal decision threshold on disjoint calibration partition optimizing MCC.
5. Blindly evaluates exactly once on coordinate-disjoint test partition.
6. Computes 13 standard classification metrics + 95% bootstrap CIs.
7. Saves models, predictions parquet, and coordinate_disjoint_metrics.csv.
"""

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
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
import xgboost as xgb
import lightgbm as lgb

FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
TARGET = "label"

OUTPUT_DIR = Path("results/experiments/p2_coordinate_generalization")
DATA_DIR = Path("data/raw/legacy_package/argus_coral_data")


def compute_file_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536 * 16):
            h.update(chunk)
    return h.hexdigest()


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict:
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


def find_optimal_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> tuple[float, float]:
    """Grid search over 99 thresholds to optimize MCC on calibration data."""
    best_th = 0.50
    best_mcc = -1.0
    for th in np.linspace(0.01, 0.99, 99):
        yp = (y_prob >= th).astype(np.uint8)
        # Fast vectorized confusion matrix
        tp = np.sum((y_true == 1) & (yp == 1))
        tn = np.sum((y_true == 0) & (yp == 0))
        fp = np.sum((y_true == 0) & (yp == 1))
        fn = np.sum((y_true == 1) & (yp == 0))
        denom = math.sqrt(float(tp + fp)) * math.sqrt(float(tp + fn)) * math.sqrt(float(tn + fp)) * math.sqrt(float(tn + fn))
        mcc = float((tp * tn - fp * fn) / denom) if denom > 0 else 0.0
        if mcc > best_mcc:
            best_mcc = mcc
            best_th = float(th)
    return best_th, best_mcc


def compute_fast_bootstrap_cis(y_true: np.ndarray, y_prob: np.ndarray, threshold: float, n_bootstraps: int = 500, seed: int = 42) -> dict:
    """Fast vectorized bootstrap confidence intervals."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    subsample_size = min(n, 100000)

    accs, mccs, baccs, f1s = [], [], [], []
    for _ in range(n_bootstraps):
        idx = rng.choice(n, size=subsample_size, replace=True)
        yt = y_true[idx]
        yp = (y_prob[idx] >= threshold).astype(np.uint8)

        tp = np.sum((yt == 1) & (yp == 1))
        tn = np.sum((yt == 0) & (yp == 0))
        fp = np.sum((yt == 0) & (yp == 1))
        fn = np.sum((yt == 1) & (yp == 0))

        tot = tp + tn + fp + fn
        if tot == 0:
            continue
        acc = (tp + tn) / tot
        denom = math.sqrt(float(tp + fp)) * math.sqrt(float(tp + fn)) * math.sqrt(float(tn + fp)) * math.sqrt(float(tn + fn))
        mcc = (tp * tn - fp * fn) / denom if denom > 0 else 0.0
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        bacc = 0.5 * (tpr + tnr)
        f1 = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0

        accs.append(acc)
        mccs.append(mcc)
        baccs.append(bacc)
        f1s.append(f1)

    return {
        "accuracy_ci_lower": float(np.percentile(accs, 2.5)),
        "accuracy_ci_upper": float(np.percentile(accs, 97.5)),
        "mcc_ci_lower": float(np.percentile(mccs, 2.5)),
        "mcc_ci_upper": float(np.percentile(mccs, 97.5)),
        "balanced_accuracy_ci_lower": float(np.percentile(baccs, 2.5)),
        "balanced_accuracy_ci_upper": float(np.percentile(baccs, 97.5)),
        "f1_score_ci_lower": float(np.percentile(f1s, 2.5)),
        "f1_score_ci_upper": float(np.percentile(f1s, 97.5)),
    }


def main():
    print("=" * 80)
    print("ARGUS P2: Experiment C — Coordinate-Disjoint Supervised Evaluation")
    print("=" * 80)
    t_init = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load entire NF-ToN pool to construct group split
    print("\n[Step 1/6] Loading full NF-ToN data pool for coordinate-disjoint partitioning...")
    df_tr = pd.read_csv(DATA_DIR / "nfton_train_features.csv", usecols=FEATURES + [TARGET])
    df_te = pd.read_csv(DATA_DIR / "nfton_test_features.csv", usecols=FEATURES + [TARGET])
    df_all = pd.concat([df_tr, df_te], ignore_index=True)
    del df_tr, df_te

    total_pool_rows = len(df_all)
    print(f"  Total NF-ToN records pooled: {total_pool_rows:,}")

    # Group by coordinate
    print("  Aggregating unique 4D coordinate groups...")
    groups = df_all.groupby(FEATURES)[TARGET].agg(["count", "sum"]).reset_index()
    groups.rename(columns={"count": "n", "sum": "n_attack"}, inplace=True)
    groups["n_benign"] = groups["n"] - groups["n_attack"]
    n_unique_groups = len(groups)
    total_att = groups["n_attack"].sum()
    target_att_rate = total_att / total_pool_rows
    print(f"  Unique 4D coordinates: {n_unique_groups:,} | Attack prevalence: {target_att_rate*100:.2f}%")

    # Target partition ratios: 70% Train, 15% Calibration, 15% Test
    target_ratios = {"train": 0.70, "cal": 0.15, "test": 0.15}
    target_n = {k: total_pool_rows * r for k, r in target_ratios.items()}

    # Sort descending by group size
    groups = groups.sort_values(by="n", ascending=False).reset_index(drop=True)

    # Place top 2 massive groups into Train to avoid dominating small Cal/Test bins
    assigned = {"train": [0, 1], "cal": [], "test": []}
    counts = {
        "train": {
            "n": int(groups.loc[0, "n"] + groups.loc[1, "n"]),
            "att": int(groups.loc[0, "n_attack"] + groups.loc[1, "n_attack"]),
            "ben": int(groups.loc[0, "n_benign"] + groups.loc[1, "n_benign"]),
        },
        "cal": {"n": 0, "att": 0, "ben": 0},
        "test": {"n": 0, "att": 0, "ben": 0},
    }

    # Greedy multi-objective assignment for remaining groups
    print("  Assigning coordinate groups with greedy fill and attack-prevalence balancing...")
    g_records = groups.iloc[2:].to_dict(orient="records")
    for offset, row in enumerate(g_records):
        idx = offset + 2
        gn = row["n"]
        ga = row["n_attack"]
        gb = row["n_benign"]

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
        counts[best_p]["ben"] += gb

    # Assign partition label to groups DataFrame
    groups["partition"] = "unassigned"
    for p, indices in assigned.items():
        groups.loc[indices, "partition"] = p

    # Verify zero leakage across coordinate groups
    train_coords = set(map(tuple, groups.loc[groups["partition"] == "train", FEATURES].values))
    cal_coords = set(map(tuple, groups.loc[groups["partition"] == "cal", FEATURES].values))
    test_coords = set(map(tuple, groups.loc[groups["partition"] == "test", FEATURES].values))

    assert len(train_coords.intersection(cal_coords)) == 0, "LEAKAGE: Train and Cal share coordinates!"
    assert len(train_coords.intersection(test_coords)) == 0, "LEAKAGE: Train and Test share coordinates!"
    assert len(cal_coords.intersection(test_coords)) == 0, "LEAKAGE: Cal and Test share coordinates!"
    print("  [PASS] ZERO coordinate overlap verified across Train, Cal, and Test!")

    # Partition statistics
    split_stats = {}
    for p in ["train", "cal", "test"]:
        c = counts[p]
        pct = c["n"] / total_pool_rows * 100
        att_pct = c["att"] / c["n"] * 100
        n_grps = len(assigned[p])
        split_stats[p] = {
            "rows": c["n"],
            "row_percentage": float(pct),
            "groups": n_grps,
            "group_percentage": float(n_grps / n_unique_groups * 100),
            "attack_rows": c["att"],
            "benign_rows": c["ben"],
            "attack_prevalence": float(c["att"] / c["n"]),
        }
        print(f"  - {p.upper():<5}: {c['n']:,} rows ({pct:.2f}%) | {n_grps:,} coords ({n_grps/n_unique_groups*100:.2f}%) | "
              f"Attack: {c['att']:,} ({att_pct:.2f}%)")

    # Save manifest
    manifest_data = {
        "manifest_version": "1.0.0",
        "experiment": "ARGUS P2 Coordinate-Disjoint Supervised Benchmark",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "partition_strategy": "strictly_group_aware_multi_objective_bin_packing",
        "features": FEATURES,
        "target": TARGET,
        "total_records": total_pool_rows,
        "total_unique_coordinates": n_unique_groups,
        "partitions": split_stats,
        "zero_coordinate_overlap_verified": True,
    }
    manifest_path = OUTPUT_DIR / "group_split_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"  Saved group split manifest to: {manifest_path}")

    # 2. Map row-level partition assignments
    print("\n[Step 2/6] Mapping row-level partition memberships...")
    df_all = df_all.merge(groups[FEATURES + ["partition"]], on=FEATURES, how="left")

    train_mask = (df_all["partition"] == "train").values
    cal_mask = (df_all["partition"] == "cal").values
    test_mask = (df_all["partition"] == "test").values

    X_train = df_all.loc[train_mask, FEATURES].values.astype(np.float32)
    y_train = df_all.loc[train_mask, TARGET].values.astype(np.uint8)

    X_cal = df_all.loc[cal_mask, FEATURES].values.astype(np.float32)
    y_cal = df_all.loc[cal_mask, TARGET].values.astype(np.uint8)

    X_test = df_all.loc[test_mask, FEATURES].values.astype(np.float32)
    y_test = df_all.loc[test_mask, TARGET].values.astype(np.uint8)

    print(f"  Train: X={X_train.shape}, y={y_train.shape}")
    print(f"  Cal:   X={X_cal.shape}, y={y_cal.shape}")
    print(f"  Test:  X={X_test.shape}, y={y_test.shape}")
    del df_all  # Free memory

    # 3. Model Training & Evaluation across seeds
    seeds = [42, 123, 456]
    results_list = []
    parquet_predictions = {"y_true": y_test}

    for seed in seeds:
        print(f"\n[Step 3/6 - Seed {seed}] Training XGBoost on coordinate-disjoint partition...")
        xgb_params = {
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 8,
            "tree_method": "hist",
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "random_state": seed,
            "n_jobs": -1,
        }
        t0 = time.time()
        xgb_model = xgb.XGBClassifier(**xgb_params)
        xgb_model.fit(X_train, y_train)
        xgb_train_time = time.time() - t0
        xgb_path = OUTPUT_DIR / f"xgboost_disjoint_seed{seed}.json"
        xgb_model.save_model(str(xgb_path))
        print(f"  XGBoost seed {seed} trained in {xgb_train_time:.1f}s -> Saved to {xgb_path.name}")

        # Calibration on disjoint calibration set
        xgb_cal_prob = xgb_model.predict_proba(X_cal)[:, 1]
        best_th_xgb, best_mcc_cal_xgb = find_optimal_threshold(y_cal, xgb_cal_prob)
        print(f"  XGBoost calibration: Optimal threshold = {best_th_xgb:.2f} (Cal MCC = {best_mcc_cal_xgb:.4f})")

        # Test evaluation
        xgb_test_prob = xgb_model.predict_proba(X_test)[:, 1]
        parquet_predictions[f"xgb_prob_seed{seed}"] = xgb_test_prob
        parquet_predictions[f"xgb_pred_05_seed{seed}"] = (xgb_test_prob >= 0.50).astype(np.uint8)
        parquet_predictions[f"xgb_pred_cal_seed{seed}"] = (xgb_test_prob >= best_th_xgb).astype(np.uint8)

        # Default th=0.50
        m_xgb_05 = compute_metrics(y_test, xgb_test_prob, threshold=0.50)
        ci_xgb_05 = compute_fast_bootstrap_cis(y_test, xgb_test_prob, threshold=0.50, seed=seed)
        results_list.append({
            "model": "XGBoost",
            "seed": seed,
            "threshold_rule": "default_0.50",
            "threshold": 0.50,
            "training_duration_seconds": xgb_train_time,
            **m_xgb_05,
            **ci_xgb_05,
        })

        # Calibrated threshold
        m_xgb_cal = compute_metrics(y_test, xgb_test_prob, threshold=best_th_xgb)
        ci_xgb_cal = compute_fast_bootstrap_cis(y_test, xgb_test_prob, threshold=best_th_xgb, seed=seed)
        results_list.append({
            "model": "XGBoost",
            "seed": seed,
            "threshold_rule": f"calibrated_{best_th_xgb:.2f}",
            "threshold": best_th_xgb,
            "training_duration_seconds": xgb_train_time,
            **m_xgb_cal,
            **ci_xgb_cal,
        })
        print(f"  XGBoost Seed {seed} Test Results: th=0.50 MCC={m_xgb_05['mcc']:.4f} BAcc={m_xgb_05['balanced_accuracy']:.4f} | "
              f"th={best_th_xgb:.2f} MCC={m_xgb_cal['mcc']:.4f} BAcc={m_xgb_cal['balanced_accuracy']:.4f}")

        # Train LightGBM
        print(f"\n[Step 4/6 - Seed {seed}] Training LightGBM on coordinate-disjoint partition...")
        lgb_params = {
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 8,
            "num_leaves": 63,
            "objective": "binary",
            "metric": "binary_logloss",
            "random_state": seed,
            "verbose": -1,
            "n_jobs": -1,
        }
        t0 = time.time()
        lgb_model = lgb.LGBMClassifier(**lgb_params)
        lgb_model.fit(X_train, y_train)
        lgb_train_time = time.time() - t0
        lgb_path = OUTPUT_DIR / f"lightgbm_disjoint_seed{seed}.txt"
        lgb_model.booster_.save_model(str(lgb_path))
        print(f"  LightGBM seed {seed} trained in {lgb_train_time:.1f}s -> Saved to {lgb_path.name}")

        # Calibration on disjoint calibration set
        lgb_cal_prob = lgb_model.predict_proba(X_cal)[:, 1]
        best_th_lgb, best_mcc_cal_lgb = find_optimal_threshold(y_cal, lgb_cal_prob)
        print(f"  LightGBM calibration: Optimal threshold = {best_th_lgb:.2f} (Cal MCC = {best_mcc_cal_lgb:.4f})")

        # Test evaluation
        lgb_test_prob = lgb_model.predict_proba(X_test)[:, 1]
        parquet_predictions[f"lgb_prob_seed{seed}"] = lgb_test_prob
        parquet_predictions[f"lgb_pred_05_seed{seed}"] = (lgb_test_prob >= 0.50).astype(np.uint8)
        parquet_predictions[f"lgb_pred_cal_seed{seed}"] = (lgb_test_prob >= best_th_lgb).astype(np.uint8)

        # Default th=0.50
        m_lgb_05 = compute_metrics(y_test, lgb_test_prob, threshold=0.50)
        ci_lgb_05 = compute_fast_bootstrap_cis(y_test, lgb_test_prob, threshold=0.50, seed=seed)
        results_list.append({
            "model": "LightGBM",
            "seed": seed,
            "threshold_rule": "default_0.50",
            "threshold": 0.50,
            "training_duration_seconds": lgb_train_time,
            **m_lgb_05,
            **ci_lgb_05,
        })

        # Calibrated threshold
        m_lgb_cal = compute_metrics(y_test, lgb_test_prob, threshold=best_th_lgb)
        ci_lgb_cal = compute_fast_bootstrap_cis(y_test, lgb_test_prob, threshold=best_th_lgb, seed=seed)
        results_list.append({
            "model": "LightGBM",
            "seed": seed,
            "threshold_rule": f"calibrated_{best_th_lgb:.2f}",
            "threshold": best_th_lgb,
            "training_duration_seconds": lgb_train_time,
            **m_lgb_cal,
            **ci_lgb_cal,
        })
        print(f"  LightGBM Seed {seed} Test Results: th=0.50 MCC={m_lgb_05['mcc']:.4f} BAcc={m_lgb_05['balanced_accuracy']:.4f} | "
              f"th={best_th_lgb:.2f} MCC={m_lgb_cal['mcc']:.4f} BAcc={m_lgb_cal['balanced_accuracy']:.4f}")

    # 4. Save metrics table
    print("\n[Step 5/6] Saving coordinate-disjoint metrics table...")
    metrics_df = pd.DataFrame(results_list)
    csv_path = OUTPUT_DIR / "coordinate_disjoint_metrics.csv"
    metrics_df.to_csv(csv_path, index=False)
    print(f"  Saved disjoint metrics table to: {csv_path}")

    # 5. Save predictions parquet
    print("\n[Step 6/6] Saving coordinate-disjoint predictions to Parquet...")
    parquet_df = pd.DataFrame(parquet_predictions)
    parquet_path = OUTPUT_DIR / "coordinate_disjoint_predictions.parquet"
    parquet_df.to_parquet(parquet_path, index=False)
    print(f"  Saved predictions parquet ({len(parquet_df):,} rows) to: {parquet_path}")

    # Multi-seed aggregate summary
    print("\n" + "=" * 80)
    print("COORDINATE-DISJOINT SUPERVISED EVALUATION SUMMARY (Across 3 Seeds):")
    print("=" * 80)
    for model_name in ["XGBoost", "LightGBM"]:
        sub = metrics_df[(metrics_df["model"] == model_name) & (metrics_df["threshold_rule"].str.startswith("calibrated"))]
        mcc_mean = sub["mcc"].mean()
        mcc_std = sub["mcc"].std()
        bacc_mean = sub["balanced_accuracy"].mean()
        bacc_std = sub["balanced_accuracy"].std()
        f1_mean = sub["f1_score"].mean()
        f1_std = sub["f1_score"].std()
        roc_mean = sub["roc_auc"].mean()
        roc_std = sub["roc_auc"].std()
        print(f"  [{model_name} Calibrated] MCC: {mcc_mean:.4f} ± {mcc_std:.4f} | "
              f"BAcc: {bacc_mean*100:.2f}% ± {bacc_std*100:.2f}% | "
              f"F1: {f1_mean:.4f} ± {f1_std:.4f} | "
              f"ROC-AUC: {roc_mean:.4f} ± {roc_std:.4f}")

    print(f"\nExperiment C completed in {time.time()-t_init:.1f}s.")


if __name__ == "__main__":
    main()
