#!/usr/bin/env python3
"""
ARGUS P2.1: Critical Task — Same-Test-Set Cross-Domain Comparison.

Evaluates historical cross-domain models and in-domain coordinate-disjoint models
on the EXACT SAME coordinate-disjoint test partition (N = 1,970,428):
  1. Source-Only XGBoost (tau = 0.50)
  2. Global CORAL + XGBoost (tau = 0.50)
  3. Clean Class-Aware CORAL + XGBoost (tau = 0.99)
  4. DANN (tau = 0.60)
  5. In-Domain Coordinate-Disjoint XGBoost (tau = 0.50 and tau = 0.87)
  6. In-Domain Coordinate-Disjoint LightGBM (tau = 0.50 and tau = 0.10)

Recalculates all 13 performance metrics + confusion matrix counts on the identical test rows.
Outputs: results/experiments/p2_1_validation/P2_1_SAME_TEST_CROSS_DOMAIN_COMPARISON.csv
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
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
P2_DIR = Path("results/experiments/p2_coordinate_generalization")
OUTPUT_DIR = Path("results/experiments/p2_1_validation")


# --- DANN PyTorch Network Definition ---
class DummyModule(nn.Module):
    pass


class DANNNetwork(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=64, latent_dim=32, dropout=0.1):
        super().__init__()
        self.feature_extractor = DummyModule()
        self.feature_extractor.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, latent_dim),
            nn.BatchNorm1d(latent_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(latent_dim, 16),
        )
        self.attack_classifier = DummyModule()
        self.attack_classifier.network = nn.Sequential(
            nn.Linear(16, 16),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(16, 1),
        )

    def forward(self, x: torch.Tensor):
        features = self.feature_extractor.network(x)
        logits = self.attack_classifier.network(features).squeeze(-1)
        return logits


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


def main():
    print("=" * 80)
    print("ARGUS P2.1: Same-Test-Set Cross-Domain Benchmark Comparison")
    print("=" * 80)
    t_start = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load the coordinate-disjoint test partition
    print("\n[Step 1/7] Loading full NF-ToN pool and reconstructing coordinate-disjoint test partition...")
    df_tr = pd.read_csv(DATA_DIR / "nfton_train_features.csv", usecols=FEATURES + [TARGET])
    df_te = pd.read_csv(DATA_DIR / "nfton_test_features.csv", usecols=FEATURES + [TARGET])
    df_all = pd.concat([df_tr, df_te], ignore_index=True)
    del df_tr, df_te

    # Load group split manifest
    with open(P2_DIR / "group_split_manifest.json", "r") as f:
        manifest = json.load(f)

    # Group by coordinate exactly as in P2 Experiment C
    groups = df_all.groupby(FEATURES)[TARGET].agg(["count", "sum"]).reset_index()
    groups.rename(columns={"count": "n", "sum": "n_attack"}, inplace=True)
    groups["n_benign"] = groups["n"] - groups["n_attack"]

    # Reconstruct the greedy partition identically (seed 42)
    print("  Reconstructing greedy bin-packing partition...")
    total_pool_rows = len(df_all)
    target_ratios = {"train": 0.70, "cal": 0.15, "test": 0.15}
    target_n = {k: total_pool_rows * r for k, r in target_ratios.items()}
    target_att_rate = groups["n_attack"].sum() / total_pool_rows

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

    df_all = df_all.merge(groups[FEATURES + ["partition"]], on=FEATURES, how="left")
    test_mask = (df_all["partition"] == "test").values

    X_test = df_all.loc[test_mask, FEATURES].values.astype(np.float32)
    y_test = df_all.loc[test_mask, TARGET].values.astype(np.uint8)
    del df_all, groups

    # Verify against saved parquet
    saved_parquet = pd.read_parquet(P2_DIR / "coordinate_disjoint_predictions.parquet")
    saved_y = saved_parquet["y_true"].values.astype(np.uint8)
    assert len(y_test) == len(saved_y), f"Length mismatch: {len(y_test)} vs {len(saved_y)}"
    match_rate = np.mean(y_test == saved_y)
    assert match_rate == 1.0, f"Label mismatch rate: {1.0 - match_rate}"
    print(f"  Verified coordinate-disjoint test partition: N = {len(y_test):,}, attack rate = {np.mean(y_test):.4%}")

    results = []

    # 2. Model 1: Source-Only XGBoost
    print("\n[Step 2/7] Evaluating Source-Only XGBoost (tau=0.50)...")
    m_src = xgb.Booster()
    m_src.load_model("artifacts/models/xgb_source.json")
    dtest = xgb.DMatrix(X_test, feature_names=FEATURES)
    p_src = m_src.predict(dtest).astype(np.float32)
    m_src_metrics = compute_all_metrics(y_test, p_src, threshold=0.50)
    m_src_metrics.update({
        "model_name": "Source-Only XGBoost",
        "model_category": "cross_domain",
        "adaptation_method": "None (Source Only)",
        "source_data": "CIC-IoT-2023",
        "threshold_type": "default_0.50",
    })
    results.append(m_src_metrics)
    print(f"  Source-Only: Acc={m_src_metrics['accuracy']:.4f}, F1={m_src_metrics['f1_score']:.4f}, MCC={m_src_metrics['mcc']:.4f}, Spec={m_src_metrics['specificity']:.4f}")

    # 3. Model 2: Global CORAL + XGBoost
    print("\n[Step 3/7] Training & Evaluating Global CORAL + XGBoost (tau=0.50)...")
    df_coral = pd.read_csv(DATA_DIR / "ciciot_train_coral_aligned.csv")
    X_coral = df_coral[FEATURES].values.astype(np.float32)
    y_coral = df_coral[TARGET].values.astype(np.uint8)
    del df_coral

    m_coral = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1,
        eval_metric="logloss",
    )
    m_coral.fit(X_coral, y_coral)
    p_coral = m_coral.predict_proba(X_test)[:, 1].astype(np.float32)
    del X_coral, y_coral, m_coral

    m_coral_metrics = compute_all_metrics(y_test, p_coral, threshold=0.50)
    m_coral_metrics.update({
        "model_name": "Global CORAL + XGBoost",
        "model_category": "cross_domain",
        "adaptation_method": "Global CORAL Feature Alignment",
        "source_data": "CIC-IoT-2023 aligned to NF-ToN",
        "threshold_type": "default_0.50",
    })
    results.append(m_coral_metrics)
    print(f"  Global CORAL: Acc={m_coral_metrics['accuracy']:.4f}, F1={m_coral_metrics['f1_score']:.4f}, MCC={m_coral_metrics['mcc']:.4f}, Spec={m_coral_metrics['specificity']:.4f}")

    # 4. Model 3: Clean Class-Aware CORAL + XGBoost
    print("\n[Step 4/7] Evaluating Clean Class-Aware CORAL + XGBoost (tau=0.99)...")
    m_clean = xgb.Booster()
    m_clean.load_model("artifacts/models/xgb_adapted.json")
    p_clean = m_clean.predict(dtest).astype(np.float32)
    m_clean_metrics = compute_all_metrics(y_test, p_clean, threshold=0.99)
    m_clean_metrics.update({
        "model_name": "Clean Class-Aware CORAL + XGBoost",
        "model_category": "cross_domain",
        "adaptation_method": "Clean Class-Aware CORAL",
        "source_data": "CIC-IoT-2023 aligned to NF-ToN",
        "threshold_type": "calibrated_0.99",
    })
    results.append(m_clean_metrics)
    print(f"  Clean CORAL (th=0.99): Acc={m_clean_metrics['accuracy']:.4f}, F1={m_clean_metrics['f1_score']:.4f}, MCC={m_clean_metrics['mcc']:.4f}, Spec={m_clean_metrics['specificity']:.4f}")

    # Also evaluate Clean CORAL at default 0.50 for transparency
    m_clean_def_metrics = compute_all_metrics(y_test, p_clean, threshold=0.50)
    m_clean_def_metrics.update({
        "model_name": "Clean Class-Aware CORAL + XGBoost (th=0.50)",
        "model_category": "cross_domain",
        "adaptation_method": "Clean Class-Aware CORAL",
        "source_data": "CIC-IoT-2023 aligned to NF-ToN",
        "threshold_type": "default_0.50",
    })
    results.append(m_clean_def_metrics)

    # 5. Model 4: DANN PyTorch Model
    print("\n[Step 5/7] Evaluating DANN PyTorch Model (tau=0.60)...")
    dann_ckpt = torch.load(DATA_DIR / "dann_results/dann_best_model.pt", map_location="cpu", weights_only=True)
    adapt_mean = dann_ckpt["adapt_mean"]
    adapt_std = dann_ckpt["adapt_std"]

    X_test_dann = ((X_test - adapt_mean) / adapt_std).astype(np.float32)

    dann_model = DANNNetwork(input_dim=4, hidden_dim=64, latent_dim=32, dropout=0.10)
    dann_model.load_state_dict(dann_ckpt["model_state_dict"], strict=False)
    dann_model.eval()

    batch_size = 65536
    p_dann_list = []
    with torch.no_grad():
        for b_start in range(0, len(X_test_dann), batch_size):
            b_end = min(b_start + batch_size, len(X_test_dann))
            b_x = torch.tensor(X_test_dann[b_start:b_end])
            logits = dann_model(b_x)
            p_dann_list.append(torch.sigmoid(logits).numpy())

    p_dann = np.concatenate(p_dann_list).astype(np.float32)
    del dann_model, dann_ckpt, X_test_dann

    m_dann_metrics = compute_all_metrics(y_test, p_dann, threshold=0.60)
    m_dann_metrics.update({
        "model_name": "DANN",
        "model_category": "cross_domain",
        "adaptation_method": "Domain-Adversarial Neural Network",
        "source_data": "CIC-IoT-2023 adapted to NF-ToN",
        "threshold_type": "calibrated_0.60",
    })
    results.append(m_dann_metrics)
    print(f"  DANN (th=0.60): Acc={m_dann_metrics['accuracy']:.4f}, F1={m_dann_metrics['f1_score']:.4f}, MCC={m_dann_metrics['mcc']:.4f}, Spec={m_dann_metrics['specificity']:.4f}")

    # Also evaluate DANN at default 0.50 for transparency
    m_dann_def_metrics = compute_all_metrics(y_test, p_dann, threshold=0.50)
    m_dann_def_metrics.update({
        "model_name": "DANN (th=0.50)",
        "model_category": "cross_domain",
        "adaptation_method": "Domain-Adversarial Neural Network",
        "source_data": "CIC-IoT-2023 adapted to NF-ToN",
        "threshold_type": "default_0.50",
    })
    results.append(m_dann_def_metrics)

    # 6. Model 5: In-Domain Coordinate-Disjoint XGBoost
    print("\n[Step 6/7] Evaluating Coordinate-Disjoint XGBoost (P2 seed 42, th=0.50 & th=0.87)...")
    p_disjoint_xgb = saved_parquet["xgb_prob_seed42"].values.astype(np.float32)

    # Threshold 0.50
    m_xgb_def_metrics = compute_all_metrics(y_test, p_disjoint_xgb, threshold=0.50)
    m_xgb_def_metrics.update({
        "model_name": "Coordinate-Disjoint XGBoost (th=0.50)",
        "model_category": "in_domain_coordinate_disjoint",
        "adaptation_method": "Supervised (Coordinate-Disjoint Train Partition)",
        "source_data": "NF-ToN-IoT-v2 Disjoint Train",
        "threshold_type": "default_0.50",
    })
    results.append(m_xgb_def_metrics)

    # Threshold 0.87 (calibrated)
    m_xgb_cal_metrics = compute_all_metrics(y_test, p_disjoint_xgb, threshold=0.87)
    m_xgb_cal_metrics.update({
        "model_name": "Coordinate-Disjoint XGBoost (th=0.87)",
        "model_category": "in_domain_coordinate_disjoint",
        "adaptation_method": "Supervised (Coordinate-Disjoint Train Partition)",
        "source_data": "NF-ToN-IoT-v2 Disjoint Train",
        "threshold_type": "calibrated_0.87",
    })
    results.append(m_xgb_cal_metrics)
    print(f"  Disjoint XGB (th=0.50): Acc={m_xgb_def_metrics['accuracy']:.4f}, F1={m_xgb_def_metrics['f1_score']:.4f}, MCC={m_xgb_def_metrics['mcc']:.4f}, Spec={m_xgb_def_metrics['specificity']:.4f}")
    print(f"  Disjoint XGB (th=0.87): Acc={m_xgb_cal_metrics['accuracy']:.4f}, F1={m_xgb_cal_metrics['f1_score']:.4f}, MCC={m_xgb_cal_metrics['mcc']:.4f}, Spec={m_xgb_cal_metrics['specificity']:.4f}")

    # 7. Model 6: In-Domain Coordinate-Disjoint LightGBM
    print("\n[Step 7/7] Evaluating Coordinate-Disjoint LightGBM (P2 seed 42, th=0.50 & th=0.10)...")
    p_disjoint_lgb = saved_parquet["lgb_prob_seed42"].values.astype(np.float32)

    # Threshold 0.50
    m_lgb_def_metrics = compute_all_metrics(y_test, p_disjoint_lgb, threshold=0.50)
    m_lgb_def_metrics.update({
        "model_name": "Coordinate-Disjoint LightGBM (th=0.50)",
        "model_category": "in_domain_coordinate_disjoint",
        "adaptation_method": "Supervised (Coordinate-Disjoint Train Partition)",
        "source_data": "NF-ToN-IoT-v2 Disjoint Train",
        "threshold_type": "default_0.50",
    })
    results.append(m_lgb_def_metrics)

    # Threshold 0.10 (calibrated)
    m_lgb_cal_metrics = compute_all_metrics(y_test, p_disjoint_lgb, threshold=0.10)
    m_lgb_cal_metrics.update({
        "model_name": "Coordinate-Disjoint LightGBM (th=0.10)",
        "model_category": "in_domain_coordinate_disjoint",
        "adaptation_method": "Supervised (Coordinate-Disjoint Train Partition)",
        "source_data": "NF-ToN-IoT-v2 Disjoint Train",
        "threshold_type": "calibrated_0.10",
    })
    results.append(m_lgb_cal_metrics)
    print(f"  Disjoint LGB (th=0.50): Acc={m_lgb_def_metrics['accuracy']:.4f}, F1={m_lgb_def_metrics['f1_score']:.4f}, MCC={m_lgb_def_metrics['mcc']:.4f}, Spec={m_lgb_def_metrics['specificity']:.4f}")
    print(f"  Disjoint LGB (th=0.10): Acc={m_lgb_cal_metrics['accuracy']:.4f}, F1={m_lgb_cal_metrics['f1_score']:.4f}, MCC={m_lgb_cal_metrics['mcc']:.4f}, Spec={m_lgb_cal_metrics['specificity']:.4f}")

    # Output to CSV
    df_results = pd.DataFrame(results)
    # Order columns logically
    lead_cols = ["model_name", "model_category", "adaptation_method", "source_data", "threshold_type", "threshold", "total_samples"]
    cm_cols = ["TP", "TN", "FP", "FN"]
    metric_cols = [c for c in df_results.columns if c not in lead_cols + cm_cols]
    df_results = df_results[lead_cols + cm_cols + metric_cols]

    out_csv = OUTPUT_DIR / "P2_1_SAME_TEST_CROSS_DOMAIN_COMPARISON.csv"
    df_results.to_csv(out_csv, index=False)
    print(f"\nSaved Same-Test-Set Comparison to: {out_csv}")
    print(f"Total execution time: {time.time() - t_start:.2f}s")


if __name__ == "__main__":
    main()
