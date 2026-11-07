#!/usr/bin/env python3
"""
ARGUS P1-1: NF-ToN-IoT-v2 In-Domain Supervised Baseline Evaluation Script.

Performs:
1. Threshold Calibration on designated held-out NF-ToN calibration split (2,101,742 rows).
   - Grid search over 99 candidate thresholds (0.01 to 0.99) optimizing Matthews Correlation Coefficient (MCC).
   - Replicates the exact Clean Class-Aware CORAL calibration procedure.
2. Blind Evaluation on frozen NF-ToN test split (2,627,177 rows).
   - Evaluates XGBoost and LightGBM at threshold 0.50 and calibrated threshold.
   - Computes all required metrics and reconciles with confusion matrix.
3. Saves prediction artifacts to Parquet and metrics to CSV/JSON.
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


def compute_file_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536 * 16):
            h.update(chunk)
    return h.hexdigest()


def calculate_comprehensive_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict:
    """Calculate all audited performance metrics reconciled with confusion matrix."""
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

    # Continuous probability metrics
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


def find_best_threshold_mcc(y_true: np.ndarray, y_prob: np.ndarray):
    """
    Search 99 candidate thresholds from 0.01 to 0.99 for maximum MCC on calibration set.
    Exact reproduction of the Clean Class-Aware CORAL calibration procedure.
    """
    thresholds = np.linspace(0.01, 0.99, 99)
    best_mcc = -1.0
    best_th = 0.50
    curves = []

    for th in thresholds:
        y_pred = (y_prob >= th).astype(np.uint8)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        mcc = float(matthews_corrcoef(y_true, y_pred))
        bacc = float(balanced_accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

        curves.append({
            "threshold": float(th),
            "mcc": mcc,
            "balanced_accuracy": bacc,
            "precision": prec,
            "recall": rec,
            "specificity": spec,
            "fpr": fpr,
        })

        if mcc > best_mcc:
            best_mcc = mcc
            best_th = float(th)

    return best_th, best_mcc, curves


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate in-domain supervised models on NF-ToN calibration and test sets."
    )
    parser.add_argument(
        "--calib-data",
        type=Path,
        default=Path("data/raw/legacy_package/argus_coral_data/nfton_train_calibration.csv"),
        help="Path to NF-ToN calibration split CSV.",
    )
    parser.add_argument(
        "--test-data",
        type=Path,
        default=Path("data/raw/legacy_package/argus_coral_data/nfton_test_features.csv"),
        help="Path to NF-ToN frozen test split CSV.",
    )
    parser.add_argument(
        "--exp-dir",
        type=Path,
        default=Path("results/experiments/p1_1_nfton_in_domain"),
        help="Experiment directory containing model artifacts and outputs.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    args.exp_dir.mkdir(parents=True, exist_ok=True)

    print("================================================================================")
    print("ARGUS P1-1: NF-ToN-IoT-v2 In-Domain Baseline Evaluation & Calibration")
    print("================================================================================")
    print(f"Calibration Split : {args.calib_data}")
    print(f"Frozen Test Split : {args.test_data}")
    print(f"Experiment Dir    : {args.exp_dir}")

    # Check files exist
    xgb_path = args.exp_dir / "xgboost_nfton_in_domain.json"
    lgb_path = args.exp_dir / "lightgbm_nfton_in_domain.txt"
    for p in [args.calib_data, args.test_data, xgb_path, lgb_path]:
        if not p.exists():
            print(f"ERROR: Required file missing: {p}", file=sys.stderr)
            sys.exit(1)

    # 1. Load Trained Models
    print("\n[Step 1/5] Loading trained models...")
    xgb_model = xgb.XGBClassifier()
    xgb_model.load_model(str(xgb_path))
    print(f"  Loaded XGBoost from {xgb_path}")

    lgb_booster = lgb.Booster(model_file=str(lgb_path))
    print(f"  Loaded LightGBM from {lgb_path}")

    # 2. Ingest Calibration Set
    print("\n[Step 2/5] Loading calibration dataset...")
    t0 = time.time()
    calib_sha256 = compute_file_sha256(args.calib_data)
    df_calib = pd.read_csv(
        args.calib_data,
        dtype={
            "pkt_mean_to_max": "float32",
            "tcp_flag_density": "float32",
            "log_pkt_mean": "float32",
            "log_pkt_max": "float32",
            "label": "uint8",
        },
    )
    X_cal = df_calib[FEATURES].values
    y_cal = df_calib[TARGET].values
    n_cal = len(df_calib)
    print(f"  Loaded {n_cal:,} calibration samples in {time.time()-t0:.2f}s (SHA256: {calib_sha256[:16]}...)")

    # 3. Perform Threshold Calibration (MCC Optimization)
    print("\n[Step 3/5] Performing threshold calibration on held-out calibration split...")
    t_start_cal = time.time()
    p_cal_xgb = xgb_model.predict_proba(X_cal)[:, 1]
    best_th_xgb, best_mcc_xgb, curves_xgb = find_best_threshold_mcc(y_cal, p_cal_xgb)
    print(f"  XGBoost Calibration: Best Threshold = {best_th_xgb:.2f} (Calibration MCC = {best_mcc_xgb:.6f})")

    p_cal_lgb = lgb_booster.predict(X_cal)
    best_th_lgb, best_mcc_lgb, curves_lgb = find_best_threshold_mcc(y_cal, p_cal_lgb)
    print(f"  LightGBM Calibration: Best Threshold = {best_th_lgb:.2f} (Calibration MCC = {best_mcc_lgb:.6f})")

    calib_thresholds_meta = {
        "calibration_dataset": str(args.calib_data),
        "calibration_sha256": calib_sha256,
        "calibration_samples": n_cal,
        "selection_objective": "Maximum Matthews Correlation Coefficient (MCC)",
        "search_grid": "np.linspace(0.01, 0.99, 99)",
        "xgboost": {
            "selected_threshold": best_th_xgb,
            "calibration_mcc": best_mcc_xgb,
        },
        "lightgbm": {
            "selected_threshold": best_th_lgb,
            "calibration_mcc": best_mcc_lgb,
        },
    }
    with open(args.exp_dir / "nfton_calibration_thresholds.json", "w") as f:
        json.dump(calib_thresholds_meta, f, indent=2)

    with open(args.exp_dir / "calibration_curves.json", "w") as f:
        json.dump({"xgboost": curves_xgb, "lightgbm": curves_lgb}, f, indent=2)

    del df_calib, X_cal, y_cal, p_cal_xgb, p_cal_lgb

    # 4. Ingest Frozen Test Set
    print("\n[Step 4/5] Loading frozen test dataset...")
    t0 = time.time()
    test_sha256 = compute_file_sha256(args.test_data)
    df_test = pd.read_csv(
        args.test_data,
        dtype={
            "pkt_mean_to_max": "float32",
            "tcp_flag_density": "float32",
            "log_pkt_mean": "float32",
            "log_pkt_max": "float32",
            "label": "uint8",
        },
    )
    X_test = df_test[FEATURES].values
    y_test = df_test[TARGET].values
    n_test = len(df_test)
    print(f"  Loaded {n_test:,} frozen test samples in {time.time()-t0:.2f}s (SHA256: {test_sha256[:16]}...)")

    # 5. Evaluate Blind Test Inference
    print("\n[Step 5/5] Evaluating test set predictions...")

    # XGBoost Predictions & Evaluation
    print("  Predicting test probabilities with XGBoost...")
    t_pred_xgb = time.time()
    p_test_xgb = xgb_model.predict_proba(X_test)[:, 1]
    print(f"    Inference completed in {time.time()-t_pred_xgb:.2f}s")

    metrics_xgb_05 = calculate_comprehensive_metrics(y_test, p_test_xgb, threshold=0.50)
    metrics_xgb_cal = calculate_comprehensive_metrics(y_test, p_test_xgb, threshold=best_th_xgb)

    # LightGBM Predictions & Evaluation
    print("  Predicting test probabilities with LightGBM...")
    t_pred_lgb = time.time()
    p_test_lgb = lgb_booster.predict(X_test)
    print(f"    Inference completed in {time.time()-t_pred_lgb:.2f}s")

    metrics_lgb_05 = calculate_comprehensive_metrics(y_test, p_test_lgb, threshold=0.50)
    metrics_lgb_cal = calculate_comprehensive_metrics(y_test, p_test_lgb, threshold=best_th_lgb)

    # Save Predictions to Parquet
    print("\n  Saving test predictions to Parquet...")
    test_ids = np.arange(n_test, dtype=np.int64)

    df_xgb_preds = pd.DataFrame({
        "test_id": test_ids,
        "y_true": y_test,
        "y_prob": p_test_xgb.astype(np.float32),
        "y_pred_05": (p_test_xgb >= 0.50).astype(np.uint8),
        "y_pred_cal": (p_test_xgb >= best_th_xgb).astype(np.uint8),
    })
    xgb_pred_path = args.exp_dir / "xgboost_test_predictions.parquet"
    df_xgb_preds.to_parquet(xgb_pred_path, index=False)
    print(f"    Saved {xgb_pred_path} ({xgb_pred_path.stat().st_size / (1024*1024):.2f} MB)")
    del df_xgb_preds

    df_lgb_preds = pd.DataFrame({
        "test_id": test_ids,
        "y_true": y_test,
        "y_prob": p_test_lgb.astype(np.float32),
        "y_pred_05": (p_test_lgb >= 0.50).astype(np.uint8),
        "y_pred_cal": (p_test_lgb >= best_th_lgb).astype(np.uint8),
    })
    lgb_pred_path = args.exp_dir / "lightgbm_test_predictions.parquet"
    df_lgb_preds.to_parquet(lgb_pred_path, index=False)
    print(f"    Saved {lgb_pred_path} ({lgb_pred_path.stat().st_size / (1024*1024):.2f} MB)")
    del df_lgb_preds

    # Collect and format metrics table
    records = [
        {
            "Model": "XGBoost",
            "Training_Regime": "In-domain supervised",
            "Threshold": 0.50,
            "Threshold_Source": "Default 0.50",
            **metrics_xgb_05,
        },
        {
            "Model": "XGBoost",
            "Training_Regime": "In-domain supervised",
            "Threshold": best_th_xgb,
            "Threshold_Source": f"NF-ToN Calibrated (MCC max={best_mcc_xgb:.4f})",
            **metrics_xgb_cal,
        },
        {
            "Model": "LightGBM",
            "Training_Regime": "In-domain supervised",
            "Threshold": 0.50,
            "Threshold_Source": "Default 0.50",
            **metrics_lgb_05,
        },
        {
            "Model": "LightGBM",
            "Training_Regime": "In-domain supervised",
            "Threshold": best_th_lgb,
            "Threshold_Source": f"NF-ToN Calibrated (MCC max={best_mcc_lgb:.4f})",
            **metrics_lgb_cal,
        },
    ]

    df_metrics = pd.DataFrame(records)
    csv_path = args.exp_dir / "nfton_in_domain_metrics.csv"
    df_metrics.to_csv(csv_path, index=False)
    print(f"\n  Saved metrics CSV: {csv_path}")

    json_path = args.exp_dir / "nfton_in_domain_metrics.json"
    with open(json_path, "w") as f:
        json.dump(records, f, indent=2)
    print(f"  Saved metrics JSON: {json_path}")

    # Confusion matrices summary
    confusion_matrices = {
        "XGBoost_0.50": {
            "threshold": 0.50,
            "TP": metrics_xgb_05["TP"],
            "TN": metrics_xgb_05["TN"],
            "FP": metrics_xgb_05["FP"],
            "FN": metrics_xgb_05["FN"],
            "total": metrics_xgb_05["total_samples"],
        },
        "XGBoost_calibrated": {
            "threshold": best_th_xgb,
            "TP": metrics_xgb_cal["TP"],
            "TN": metrics_xgb_cal["TN"],
            "FP": metrics_xgb_cal["FP"],
            "FN": metrics_xgb_cal["FN"],
            "total": metrics_xgb_cal["total_samples"],
        },
        "LightGBM_0.50": {
            "threshold": 0.50,
            "TP": metrics_lgb_05["TP"],
            "TN": metrics_lgb_05["TN"],
            "FP": metrics_lgb_05["FP"],
            "FN": metrics_lgb_05["FN"],
            "total": metrics_lgb_05["total_samples"],
        },
        "LightGBM_calibrated": {
            "threshold": best_th_lgb,
            "TP": metrics_lgb_cal["TP"],
            "TN": metrics_lgb_cal["TN"],
            "FP": metrics_lgb_cal["FP"],
            "FN": metrics_lgb_cal["FN"],
            "total": metrics_lgb_cal["total_samples"],
        },
    }
    cm_path = args.exp_dir / "nfton_confusion_matrices.json"
    with open(cm_path, "w") as f:
        json.dump(confusion_matrices, f, indent=2)
    print(f"  Saved confusion matrices JSON: {cm_path}")

    # Print Summary Table
    print("\n================================================================================")
    print("EXPERIMENTAL RESULTS SUMMARY ON FROZEN NF-ToN TEST SET (N = 2,627,177)")
    print("================================================================================")
    cols_display = [
        "Model", "Threshold", "Accuracy", "Precision", "Recall", "F1_Score",
        "Balanced_Accuracy", "MCC", "ROC_AUC", "PR_AUC", "Specificity"
    ]
    df_display = df_metrics.copy()
    df_display.rename(columns={
        "accuracy": "Accuracy",
        "precision": "Precision",
        "recall": "Recall",
        "f1_score": "F1_Score",
        "balanced_accuracy": "Balanced_Accuracy",
        "mcc": "MCC",
        "roc_auc": "ROC_AUC",
        "pr_auc": "PR_AUC",
        "specificity": "Specificity",
    }, inplace=True)
    print(df_display[cols_display].to_string(index=False))
    print("================================================================================")
    print("EVALUATION SUCCESSFUL")
    print("================================================================================")


if __name__ == "__main__":
    main()
