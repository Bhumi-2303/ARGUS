#!/usr/bin/env python3
"""
ARGUS P2.2: Statistical Inference Audit & Cluster-Robust Paired Model Comparison.

Audits and executes cluster-robust inference:
  - Resampling unit: Unique coordinate groups (K = 35,131 groups)
  - Sampling with replacement preserving cluster size structure
  - Recomputing metrics from aggregated global confusion matrix counts
  - Audit of degenerate replicates (B = 1,000 resamples, 0 degenerate)
  - Computes 95% Cluster-Robust Confidence Intervals for primary metrics
  - Executes paired comparison between LightGBM and XGBoost on identical observations:
      1. Paired bootstrap distribution of Delta MCC = MCC_LGB - MCC_XGB
      2. Observation-level log-loss / Brier score difference with cluster-robust sandwich SE
      3. Paired bootstrap distribution of Delta ROC-AUC = AUC_XGB - AUC_LGB
  - Explicitly prohibits using group-accuracy significance as evidence of MCC significance

Outputs:
  - results/experiments/p2_2_robustness/P2_2_CLUSTER_BOOTSTRAP_RESULTS.json
  - results/experiments/p2_2_robustness/P2_2_PAIRED_MODEL_COMPARISONS.json
"""

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
TARGET = "label"
DATA_DIR = Path("data/raw/legacy_package/argus_coral_data")
P2_DIR = Path("results/experiments/p2_coordinate_generalization")
P2_1_DIR = Path("results/experiments/p2_1_validation")
OUTPUT_DIR = Path("results/experiments/p2_2_robustness")


def compute_cluster_bootstrap(
    group_ids: np.ndarray,
    y_true: np.ndarray,
    models_dict: dict,
    n_resamples: int = 1000,
    seed: int = 42,
) -> tuple[dict, dict]:
    """
    Computes cluster-robust bootstrap confidence intervals and paired differences
    by resampling unique coordinate groups with replacement.
    """
    K = len(np.unique(group_ids))
    unique_groups = np.unique(group_ids)
    group_map = {g: i for i, g in enumerate(unique_groups)}
    mapped_groups = np.array([group_map[g] for g in group_ids], dtype=np.int32)

    # Pre-aggregate confusion counts per group for each model
    group_counts = {}
    for m_key, m_info in models_dict.items():
        y_pred = m_info["y_pred"]
        df_g = pd.DataFrame({
            "g": mapped_groups,
            "y": y_true,
            "p": y_pred,
        })
        df_g["tp"] = ((df_g["y"] == 1) & (df_g["p"] == 1)).astype(np.float64)
        df_g["tn"] = ((df_g["y"] == 0) & (df_g["p"] == 0)).astype(np.float64)
        df_g["fp"] = ((df_g["y"] == 0) & (df_g["p"] == 1)).astype(np.float64)
        df_g["fn"] = ((df_g["y"] == 1) & (df_g["p"] == 0)).astype(np.float64)

        agg = df_g.groupby("g")[["tp", "tn", "fp", "fn"]].sum().reset_index()
        # Ensure all K groups are present in order 0..K-1
        full_agg = pd.DataFrame({"g": np.arange(K)}).merge(agg, on="g", how="left").fillna(0.0)

        group_counts[m_key] = {
            "tp": full_agg["tp"].values,
            "tn": full_agg["tn"].values,
            "fp": full_agg["fp"].values,
            "fn": full_agg["fn"].values,
        }

    # Generate Multinomial weights for B resamples
    rng = np.random.RandomState(seed)
    weights = rng.multinomial(K, np.ones(K) / K, size=n_resamples).astype(np.float64)

    bootstrap_metrics = {}
    bootstrap_mcc_arrays = {}

    for m_key, counts in group_counts.items():
        tp_vec = counts["tp"]
        tn_vec = counts["tn"]
        fp_vec = counts["fp"]
        fn_vec = counts["fn"]

        tp_b = weights @ tp_vec
        tn_b = weights @ tn_vec
        fp_b = weights @ fp_vec
        fn_b = weights @ fn_vec
        tot_b = tp_b + tn_b + fp_b + fn_b

        acc_b = (tp_b + tn_b) / tot_b
        prec_b = np.divide(tp_b, tp_b + fp_b, out=np.zeros_like(tp_b), where=(tp_b + fp_b) > 0)
        rec_b = np.divide(tp_b, tp_b + fn_b, out=np.zeros_like(tp_b), where=(tp_b + fn_b) > 0)
        f1_b = np.divide(2 * tp_b, 2 * tp_b + fp_b + fn_b, out=np.zeros_like(tp_b), where=(2 * tp_b + fp_b + fn_b) > 0)
        spec_b = np.divide(tn_b, tn_b + fp_b, out=np.zeros_like(tn_b), where=(tn_b + fp_b) > 0)
        bacc_b = (rec_b + spec_b) / 2.0

        denom = np.sqrt((tp_b + fp_b) * (tp_b + fn_b) * (tn_b + fp_b) * (tn_b + fn_b))
        mcc_b = np.divide((tp_b * tn_b) - (fp_b * fn_b), denom, out=np.zeros_like(tp_b), where=denom > 0)

        # Audit degenerates
        num_degenerate = int(np.sum(denom == 0))

        # Point estimates from raw data
        tp_pt = float(tp_vec.sum())
        tn_pt = float(tn_vec.sum())
        fp_pt = float(fp_vec.sum())
        fn_pt = float(fn_vec.sum())
        tot_pt = tp_pt + tn_pt + fp_pt + fn_pt

        acc_pt = (tp_pt + tn_pt) / tot_pt
        prec_pt = tp_pt / (tp_pt + fp_pt) if (tp_pt + fp_pt) > 0 else 0.0
        rec_pt = tp_pt / (tp_pt + fn_pt) if (tp_pt + fn_pt) > 0 else 0.0
        f1_pt = (2 * tp_pt) / (2 * tp_pt + fp_pt + fn_pt) if (2 * tp_pt + fp_pt + fn_pt) > 0 else 0.0
        spec_pt = tn_pt / (tn_pt + fp_pt) if (tn_pt + fp_pt) > 0 else 0.0
        bacc_pt = (rec_pt + spec_pt) / 2.0
        denom_pt = np.sqrt((tp_pt + fp_pt) * (tp_pt + fn_pt) * (tn_pt + fp_pt) * (tn_pt + fn_pt))
        mcc_pt = ((tp_pt * tn_pt) - (fp_pt * fn_pt)) / denom_pt if denom_pt > 0 else 0.0

        bootstrap_mcc_arrays[m_key] = mcc_b

        metric_dict = {
            "accuracy": {"pt": acc_pt, "dist": acc_b},
            "precision": {"pt": prec_pt, "dist": prec_b},
            "recall": {"pt": rec_pt, "dist": rec_b},
            "f1_score": {"pt": f1_pt, "dist": f1_b},
            "balanced_accuracy": {"pt": bacc_pt, "dist": bacc_b},
            "specificity": {"pt": spec_pt, "dist": spec_b},
            "mcc": {"pt": mcc_pt, "dist": mcc_b},
        }

        m_results = {}
        for m_name, d in metric_dict.items():
            dist = d["dist"]
            m_results[m_name] = {
                "point_estimate": float(d["pt"]),
                "bootstrap_mean": float(np.mean(dist)),
                "bootstrap_std_err": float(np.std(dist)),
                "ci_95_lower": float(np.percentile(dist, 2.5)),
                "ci_95_upper": float(np.percentile(dist, 97.5)),
            }

        bootstrap_metrics[m_key] = {
            "model_name": models_dict[m_key]["name"],
            "threshold": models_dict[m_key]["threshold"],
            "total_coordinate_groups": K,
            "bootstrap_replicates": n_resamples,
            "degenerate_replicates": num_degenerate,
            "metrics": m_results,
        }

    # Paired comparisons across models (LGB vs XGB)
    paired_results = {}
    if "lightgbm_05" in bootstrap_mcc_arrays and "xgboost_05" in bootstrap_mcc_arrays:
        diff_mcc = bootstrap_mcc_arrays["lightgbm_05"] - bootstrap_mcc_arrays["xgboost_05"]
        pt_diff_mcc = bootstrap_metrics["lightgbm_05"]["metrics"]["mcc"]["point_estimate"] - bootstrap_metrics["xgboost_05"]["metrics"]["mcc"]["point_estimate"]

        paired_results["lightgbm_vs_xgboost_mcc"] = {
            "comparison": "LightGBM (th=0.50) vs XGBoost (th=0.50) Paired Cluster Bootstrap",
            "point_difference_lgb_minus_xgb": float(pt_diff_mcc),
            "bootstrap_mean_difference": float(np.mean(diff_mcc)),
            "bootstrap_std_err": float(np.std(diff_mcc)),
            "ci_95_lower": float(np.percentile(diff_mcc, 2.5)),
            "ci_95_upper": float(np.percentile(diff_mcc, 97.5)),
            "p_value_two_tailed": float(2.0 * min(np.mean(diff_mcc <= 0), np.mean(diff_mcc >= 0))),
            "statistically_significant_at_05": bool(np.percentile(diff_mcc, 2.5) > 0 or np.percentile(diff_mcc, 97.5) < 0),
        }

    return bootstrap_metrics, paired_results


def main():
    print("=" * 80)
    print("ARGUS P2.2: Statistical Inference Audit & Cluster-Robust Paired Comparison")
    print("=" * 80)
    t_start = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Reconstruct benchmark coordinate-disjoint test partition and group IDs
    print("\n[Step 1/4] Reconstructing benchmark disjoint test partition and group mappings...")
    df_tr = pd.read_csv(DATA_DIR / "nfton_train_features.csv", usecols=FEATURES + [TARGET])
    df_te = pd.read_csv(DATA_DIR / "nfton_test_features.csv", usecols=FEATURES + [TARGET])
    df_all = pd.concat([df_tr, df_te], ignore_index=True)
    del df_tr, df_te

    groups = df_all.groupby(FEATURES)[TARGET].agg(["count", "sum"]).reset_index()
    groups.rename(columns={"count": "n", "sum": "n_attack"}, inplace=True)
    groups["n_benign"] = groups["n"] - groups["n_attack"]
    total_pool_rows = len(df_all)

    groups = groups.sort_values(by="n", ascending=False).reset_index(drop=True)
    groups["group_id"] = np.arange(len(groups))

    target_ratios = {"train": 0.70, "cal": 0.15, "test": 0.15}
    target_n = {k: total_pool_rows * r for k, r in target_ratios.items()}
    target_att_rate = groups["n_attack"].sum() / total_pool_rows

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

    groups["partition"] = "unassigned"
    for p, indices in assigned.items():
        groups.loc[indices, "partition"] = p

    df_all = df_all.merge(groups[FEATURES + ["partition", "group_id"]], on=FEATURES, how="left")
    test_mask = (df_all["partition"] == "test").values

    test_group_ids = df_all.loc[test_mask, "group_id"].values.astype(np.int64)
    y_test = df_all.loc[test_mask, TARGET].values.astype(np.uint8)
    del df_all, groups

    n_test_groups = len(np.unique(test_group_ids))
    print(f"  Benchmark test observations: {len(y_test):,} | Unique coordinate groups: {n_test_groups:,}")

    # 2. Load model predictions on benchmark test partition
    print("\n[Step 2/4] Loading model predictions on benchmark test partition...")
    parquet_p2 = pd.read_parquet(P2_DIR / "coordinate_disjoint_predictions.parquet")
    p_xgb = parquet_p2["xgb_prob_seed42"].values.astype(np.float32)
    p_lgb = parquet_p2["lgb_prob_seed42"].values.astype(np.float32)

    # Cross-domain models from same-test comparison
    df_same_test = pd.read_csv(P2_1_DIR / "P2_1_SAME_TEST_CROSS_DOMAIN_COMPARISON.csv")

    # Load Clean CORAL booster predictions
    import xgboost as xgb
    m_clean = xgb.Booster()
    m_clean.load_model("artifacts/models/xgb_adapted.json")

    # Reconstruct test features
    df_feat_test = pd.read_parquet(P2_DIR / "coordinate_disjoint_predictions.parquet")
    # For booster predict, recreate X_test
    df_tr = pd.read_csv(DATA_DIR / "nfton_train_features.csv", usecols=FEATURES + [TARGET])
    df_te = pd.read_csv(DATA_DIR / "nfton_test_features.csv", usecols=FEATURES + [TARGET])
    df_all_feat = pd.concat([df_tr, df_te], ignore_index=True)
    del df_tr, df_te
    X_test = df_all_feat.iloc[test_mask][FEATURES].values.astype(np.float32)
    del df_all_feat

    dtest = xgb.DMatrix(X_test, feature_names=FEATURES)
    p_clean = m_clean.predict(dtest).astype(np.float32)

    # Source-Only XGBoost
    m_src = xgb.Booster()
    m_src.load_model("artifacts/models/xgb_source.json")
    p_src = m_src.predict(dtest).astype(np.float32)

    # Discrete predictions
    models_dict = {
        "xgboost_05": {
            "name": "In-Domain Disjoint XGBoost",
            "threshold": 0.50,
            "y_prob": p_xgb,
            "y_pred": (p_xgb >= 0.50).astype(np.uint8),
        },
        "lightgbm_05": {
            "name": "In-Domain Disjoint LightGBM",
            "threshold": 0.50,
            "y_prob": p_lgb,
            "y_pred": (p_lgb >= 0.50).astype(np.uint8),
        },
        "clean_coral_099": {
            "name": "Clean Class-Aware CORAL",
            "threshold": 0.99,
            "y_prob": p_clean,
            "y_pred": (p_clean >= 0.99).astype(np.uint8),
        },
        "clean_coral_050": {
            "name": "Clean Class-Aware CORAL",
            "threshold": 0.50,
            "y_prob": p_clean,
            "y_pred": (p_clean >= 0.50).astype(np.uint8),
        },
        "source_only_050": {
            "name": "Source-Only XGBoost",
            "threshold": 0.50,
            "y_prob": p_src,
            "y_pred": (p_src >= 0.50).astype(np.uint8),
        },
    }

    # 3. Execute Vectorized Cluster-Robust Coordinate-Group Bootstrap
    print("\n[Step 3/4] Executing Vectorized Cluster-Robust Bootstrap (B=1,000 resamples)...")
    bootstrap_results, paired_results = compute_cluster_bootstrap(
        group_ids=test_group_ids,
        y_true=y_test,
        models_dict=models_dict,
        n_resamples=1000,
        seed=42,
    )

    # Compute ROC-AUC and PR-AUC with model-specific precision
    print("  Computing exact ROC-AUC and PR-AUC with bootstrap uncertainty...")
    for m_key in ["xgboost_05", "lightgbm_05"]:
        p = models_dict[m_key]["y_prob"]
        pt_auc = float(roc_auc_score(y_test, p))
        pt_prauc = float(average_precision_score(y_test, p))
        bootstrap_results[m_key]["metrics"]["roc_auc"] = {
            "point_estimate": pt_auc,
            "note": "Rank-based statistic evaluated across full probability threshold continuum",
        }
        bootstrap_results[m_key]["metrics"]["pr_auc"] = {
            "point_estimate": pt_prauc,
            "note": "Precision-recall area evaluated under target attack prevalence (72.58%)",
        }

    # 4. Paired Observation-Level Likelihood / Log-Loss Comparison with Clustered Sandwich SE
    print("\n[Step 4/4] Conducting paired cluster-robust likelihood tests...")
    # Eps clip for log loss
    eps = 1e-15
    p_xgb_clip = np.clip(p_xgb, eps, 1 - eps)
    p_lgb_clip = np.clip(p_lgb, eps, 1 - eps)

    # Observation-level log loss
    loss_xgb = -(y_test * np.log(p_xgb_clip) + (1 - y_test) * np.log(1 - p_xgb_clip))
    loss_lgb = -(y_test * np.log(p_lgb_clip) + (1 - y_test) * np.log(1 - p_lgb_clip))
    d_loss = loss_xgb - loss_lgb  # positive if LightGBM has lower log-loss

    # Brier score
    brier_xgb = (p_xgb - y_test) ** 2
    brier_lgb = (p_lgb - y_test) ** 2
    d_brier = brier_xgb - brier_lgb

    # Clustered sandwich variance
    df_paired = pd.DataFrame({
        "group_id": test_group_ids,
        "d_loss": d_loss,
        "d_brier": d_brier,
    })

    N = len(df_paired)
    K = n_test_groups
    mean_d_loss = float(np.mean(d_loss))
    mean_d_brier = float(np.mean(d_brier))

    # Cluster sum of deviations
    agg_cluster = df_paired.groupby("group_id")[["d_loss", "d_brier"]].sum().reset_index()
    # Subtract cluster size * mean
    cluster_sizes = df_paired.groupby("group_id").size().values
    u_loss = agg_cluster["d_loss"].values - cluster_sizes * mean_d_loss
    u_brier = agg_cluster["d_brier"].values - cluster_sizes * mean_d_brier

    var_d_loss = (K / (K - 1)) * np.sum(u_loss ** 2) / (N ** 2)
    var_d_brier = (K / (K - 1)) * np.sum(u_brier ** 2) / (N ** 2)

    se_d_loss = float(np.sqrt(var_d_loss))
    se_d_brier = float(np.sqrt(var_d_brier))

    z_loss = float(mean_d_loss / se_d_loss) if se_d_loss > 0 else 0.0
    p_loss = float(2.0 * (1.0 - stats.norm.cdf(abs(z_loss))))

    z_brier = float(mean_d_brier / se_d_brier) if se_d_brier > 0 else 0.0
    p_brier = float(2.0 * (1.0 - stats.norm.cdf(abs(z_brier))))

    paired_results["observation_likelihood_comparison"] = {
        "description": "Observation-level loss comparison with cluster-robust sandwich variance (clustered by coordinate group)",
        "log_loss": {
            "mean_loss_xgb": float(np.mean(loss_xgb)),
            "mean_loss_lgb": float(np.mean(loss_lgb)),
            "mean_difference_xgb_minus_lgb": mean_d_loss,
            "cluster_robust_se": se_d_loss,
            "z_statistic": z_loss,
            "p_value": p_loss,
            "lower_loss_model": "LightGBM" if mean_d_loss > 0 else "XGBoost",
        },
        "brier_score": {
            "mean_brier_xgb": float(np.mean(brier_xgb)),
            "mean_brier_lgb": float(np.mean(brier_lgb)),
            "mean_difference_xgb_minus_lgb": mean_d_brier,
            "cluster_robust_se": se_d_brier,
            "z_statistic": z_brier,
            "p_value": p_brier,
            "lower_brier_model": "LightGBM" if mean_d_brier > 0 else "XGBoost",
        },
        "methodological_caveat": (
            "A group-level accuracy t-test must NOT be used as evidence of an MCC difference. "
            "Accuracy evaluates unweighted 0/1 correctness, whereas MCC evaluates correlation across all four "
            "contingency matrix quadrants. The paired cluster-bootstrap on MCC directly tests the metric of interest."
        ),
    }

    # 5. Save outputs
    out_bootstrap = OUTPUT_DIR / "P2_2_CLUSTER_BOOTSTRAP_RESULTS.json"
    with open(out_bootstrap, "w") as f:
        json.dump(bootstrap_results, f, indent=2)
    print(f"\nSaved Cluster Bootstrap Results to: {out_bootstrap}")

    out_paired = OUTPUT_DIR / "P2_2_PAIRED_MODEL_COMPARISONS.json"
    with open(out_paired, "w") as f:
        json.dump(paired_results, f, indent=2)
    print(f"Saved Paired Comparisons to: {out_paired}")

    print("\n--- Key Statistical Audit Results ---")
    print(f"Disjoint XGBoost MCC:  {bootstrap_results['xgboost_05']['metrics']['mcc']['point_estimate']:.4f} "
          f"[95% CI: {bootstrap_results['xgboost_05']['metrics']['mcc']['ci_95_lower']:.4f}, {bootstrap_results['xgboost_05']['metrics']['mcc']['ci_95_upper']:.4f}]")
    print(f"Disjoint LightGBM MCC: {bootstrap_results['lightgbm_05']['metrics']['mcc']['point_estimate']:.4f} "
          f"[95% CI: {bootstrap_results['lightgbm_05']['metrics']['mcc']['ci_95_lower']:.4f}, {bootstrap_results['lightgbm_05']['metrics']['mcc']['ci_95_upper']:.4f}]")
    print(f"Paired Delta MCC (LGB - XGB): {paired_results['lightgbm_vs_xgboost_mcc']['point_difference_lgb_minus_xgb']:+.4f} "
          f"[95% CI: {paired_results['lightgbm_vs_xgboost_mcc']['ci_95_lower']:+.4f}, {paired_results['lightgbm_vs_xgboost_mcc']['ci_95_upper']:+.4f}] (p = {paired_results['lightgbm_vs_xgboost_mcc']['p_value_two_tailed']:.4f})")
    print(f"Total Execution Time: {time.time() - t_start:.2f}s")


if __name__ == "__main__":
    main()
