#!/usr/bin/env python3
"""
ARGUS Final Probability Output Audit Script.
Analyzes probability integrity, pipeline stages, quantization, unique values,
high-resolution threshold sweep (0.4900 to 0.5100), and tests for pre-thresholding/bugs.
"""

import os, sys, json, time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
PROJECT_ROOT = _curr
CORAL_DATA_DIR = PROJECT_ROOT / "ARGUS_Cross_Domain_Results/argus_coral_data"
P3_RESULTS = PROJECT_ROOT / "phase3_results"
P4_RESULTS = PROJECT_ROOT / "phase4_results"
AUDIT_DIR = P4_RESULTS / "probability_audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']

def prior_correction(y_prob: np.ndarray, p_s_attack: float, p_t_attack: float) -> np.ndarray:
    p_s_benign = 1.0 - p_s_attack
    p_t_benign = 1.0 - p_t_attack
    y_prob_clipped = np.clip(y_prob, 1e-15, 1 - 1e-15)
    attack_unnorm = y_prob_clipped * (p_t_attack / p_s_attack)
    benign_unnorm = (1.0 - y_prob_clipped) * (p_t_benign / p_s_benign)
    total = attack_unnorm + benign_unnorm
    return attack_unnorm / total

def get_stats(arr: np.ndarray) -> dict:
    quantiles = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 0.999]
    q_vals = np.quantile(arr, quantiles)
    q_dict = {f"Q{int(q*100) if q*100==int(q*100) else q*100}": float(v) for q, v in zip(quantiles, q_vals)}
    
    n_total = len(arr)
    n_unique = len(np.unique(arr))
    p_zero = float(np.count_nonzero(arr == 0.0) / n_total * 100)
    p_one = float(np.count_nonzero(arr == 1.0) / n_total * 100)
    p_half = float(np.count_nonzero(arr == 0.5) / n_total * 100)
    p_below = float(np.count_nonzero(arr < 0.5) / n_total * 100)
    p_equal = float(np.count_nonzero(arr == 0.5) / n_total * 100)
    p_above = float(np.count_nonzero(arr > 0.5) / n_total * 100)
    
    return {
        "min": float(arr.min()),
        "max": float(arr.max()),
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "std": float(arr.std()),
        "n_unique": n_unique,
        "pct_exact_0": p_zero,
        "pct_exact_1": p_one,
        "pct_exact_0.5": p_half,
        "pct_below_0.5": p_below,
        "pct_equal_0.5": p_equal,
        "pct_above_0.5": p_above,
        **q_dict
    }

def main():
    print("=" * 80)
    print("ARGUS FINAL PROBABILITY OUTPUT AUDIT")
    print("=" * 80)
    
    # Load labels
    d3_test = pd.read_csv(CORAL_DATA_DIR / "iec104_test_features.csv")
    y_test = d3_test['label'].values
    d3_calib = pd.read_csv(CORAL_DATA_DIR / "iec104_train_calibration.csv")
    y_calib = d3_calib['label'].values
    d3_adapt = pd.read_csv(CORAL_DATA_DIR / "iec104_train_adaptation.csv")
    y_adapt = d3_adapt['label'].values
    P_T_ATTACK = float(np.mean(np.concatenate([y_calib, y_adapt])))
    P_S1_ATTACK = 0.976421
    P_S2_ATTACK = 0.725844

    # Load Phase 3 predictions
    df_d1_coral_test = pd.read_csv(P3_RESULTS / "experiments/D1_D3_CORAL/predictions.csv")["y_prob"].values
    df_d2_coral_test = pd.read_csv(P3_RESULTS / "experiments/D2_D3_CORAL/predictions.csv")["y_prob"].values

    import lightgbm as lgb
    X_calib = d3_calib[FEATURE_COLS].values
    model_d1_coral = lgb.Booster(model_file=str(P3_RESULTS / "models/model_d1_coral.txt"))
    model_d2_coral = lgb.Booster(model_file=str(P3_RESULTS / "models/model_d2_coral.txt"))
    df_d1_coral_calib = model_d1_coral.predict(X_calib)
    df_d2_coral_calib = model_d2_coral.predict(X_calib)

    # 1. Pipeline Stages Audit
    print("\n1. Stage-by-Stage Probability Diagnostic Stats:")
    stages_calib = {
        "D1_raw": df_d1_coral_calib,
        "D2_raw": df_d2_coral_calib,
        "D1_prior_corr": prior_correction(df_d1_coral_calib, P_S1_ATTACK, P_T_ATTACK),
        "D2_prior_corr": prior_correction(df_d2_coral_calib, P_S2_ATTACK, P_T_ATTACK),
    }

    # Check fusion configuration
    with open(P4_RESULTS / "experiments/E5_fusion_CORAL_prior/config.json", "r") as f:
        cfg = json.load(f)
    w1, w2 = cfg["w1"], cfg["w2"]
    print(f"   Config loaded fusion weights: w1={w1}, w2={w2}")
    
    stages_calib["Full_ARGUS_fused"] = w1 * stages_calib["D1_prior_corr"] + w2 * stages_calib["D2_prior_corr"]

    stats_list = []
    for s_name, arr in stages_calib.items():
        st = get_stats(arr)
        st["Stage"] = s_name
        st["Partition"] = "Calibration"
        stats_list.append(st)
        print(f"\n   [{s_name}] Calibration:")
        print(f"      Range: [{st['min']:.6f}, {st['max']:.6f}] | Mean: {st['mean']:.6f} | Median: {st['median']:.6f} | Std: {st['std']:.6f}")
        print(f"      Unique count: {st['n_unique']} / {len(arr)}")
        print(f"      Below 0.5: {st['pct_below_0.5']:.2f}% | Equal 0.5: {st['pct_equal_0.5']:.2f}% | Above 0.5: {st['pct_above_0.5']:.2f}%")

    # Test set stats
    stages_test = {
        "D1_raw": df_d1_coral_test,
        "D2_raw": df_d2_coral_test,
        "D1_prior_corr": prior_correction(df_d1_coral_test, P_S1_ATTACK, P_T_ATTACK),
        "D2_prior_corr": prior_correction(df_d2_coral_test, P_S2_ATTACK, P_T_ATTACK),
    }
    stages_test["Full_ARGUS_fused"] = w1 * stages_test["D1_prior_corr"] + w2 * stages_test["D2_prior_corr"]
    
    for s_name, arr in stages_test.items():
        st = get_stats(arr)
        st["Stage"] = s_name
        st["Partition"] = "Test"
        stats_list.append(st)

    df_stats = pd.DataFrame(stats_list)
    df_stats.to_csv(AUDIT_DIR / "stage_probability_stats.csv", index=False)

    # 2. High-Resolution Threshold Sweep (0.4900 to 0.5100, step 0.0001)
    print("\n2. High-Resolution Threshold Sweep on Calibration Set (0.4900 .. 0.5100, step 0.0001)...")
    p_calib = stages_calib["Full_ARGUS_fused"]
    fine_thresholds = np.round(np.arange(0.4900, 0.5101, 0.0001), 4)
    
    high_res_rows = []
    y_calib_bool = y_calib.astype(bool)
    
    for th in fine_thresholds:
        y_pred = (p_calib >= th)
        tp = int(np.count_nonzero(y_calib_bool & y_pred))
        fp = int(np.count_nonzero((~y_calib_bool) & y_pred))
        tn = int(np.count_nonzero((~y_calib_bool) & (~y_pred)))
        fn = int(np.count_nonzero(y_calib_bool & (~y_pred)))
        
        n_pos = tp + fn
        n_neg = tn + fp
        total = n_pos + n_neg
        
        acc = (tp + tn) / total
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / n_pos if n_pos > 0 else 0.0
        f1 = (2.0 * tp) / (2.0 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
        spec = tn / n_neg if n_neg > 0 else 0.0
        fpr = fp / n_neg if n_neg > 0 else 0.0
        fnr = fn / n_pos if n_pos > 0 else 0.0
        bal_acc = 0.5 * (rec + spec)
        
        denom = np.sqrt(float(tp + fp) * float(tp + fn) * float(tn + fp) * float(tn + fn))
        mcc = (float(tp) * tn - float(fp) * fn) / denom if denom > 0 else 0.0
        
        high_res_rows.append({
            "Threshold": th,
            "TP": tp, "TN": tn, "FP": fp, "FN": fn,
            "Accuracy": acc, "Precision": prec, "Recall": rec,
            "F1": f1, "MCC": mcc, "Balanced_Accuracy": bal_acc,
            "Specificity": spec, "FPR": fpr, "FNR": fnr
        })

    df_high_res = pd.DataFrame(high_res_rows)
    df_high_res.to_csv(AUDIT_DIR / "high_res_threshold_sweep.csv", index=False)
    
    print("\n   Sample points around 0.5000 in Calibration High-Res Sweep:")
    print(df_high_res[(df_high_res["Threshold"] >= 0.4990) & (df_high_res["Threshold"] <= 0.5010)][["Threshold", "F1", "MCC", "Recall", "FPR", "FNR"]])

    # 3. Unique-Value & Neighborhood Investigation
    print("\n3. Unique-Value Neighborhood Investigation around 0.50:")
    p_sorted = np.sort(p_calib)
    below_050 = p_sorted[p_sorted < 0.50]
    equal_050 = p_sorted[p_sorted == 0.50]
    above_050 = p_sorted[p_sorted > 0.50]
    
    p_max_below = float(below_050.max()) if len(below_050) > 0 else None
    p_min_above = float(above_050.min()) if len(above_050) > 0 else None
    n_exact_050 = len(equal_050)
    
    print(f"   Max value < 0.50:  {p_max_below}")
    print(f"   Count exact == 0.50: {n_exact_050}")
    print(f"   Min value > 0.50:  {p_min_above}")
    print(f"   Count < 0.50:      {len(below_050)} ({len(below_050)/len(p_calib)*100:.2f}%)")
    print(f"   Count > 0.50:      {len(above_050)} ({len(above_050)/len(p_calib)*100:.2f}%)")

    # Distinct values between 0.49 and 0.51
    between_49_51 = p_sorted[(p_sorted >= 0.49) & (p_sorted <= 0.51)]
    unique_between_49_51 = np.unique(between_49_51)
    print(f"   Number of unique probability values between 0.49 and 0.51: {len(unique_between_49_51)}")
    print(f"   Unique values in [0.49, 0.51]: {unique_between_49_51}")

    # 4. Generate Audit Plots (Plot A through Plot F)
    print("\n4. Generating Audit Plots (Plots A - F)...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Plot A: Histogram on Calibration
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(p_calib, bins=100, color='#3498db', edgecolor='black', alpha=0.7)
    ax.set_title("Plot A: Full ARGUS Probability Histogram (D3 Calibration)")
    ax.set_xlabel("Probability p(Attack|x)")
    ax.set_ylabel("Sample Count")
    plt.tight_layout()
    plt.savefig(AUDIT_DIR / "plot_a_hist_calib.png")
    plt.close()

    # Plot B: Histogram on Test
    p_test = stages_test["Full_ARGUS_fused"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(p_test, bins=100, color='#2ecc71', edgecolor='black', alpha=0.7)
    ax.set_title("Plot B: Full ARGUS Probability Histogram (D3 Test)")
    ax.set_xlabel("Probability p(Attack|x)")
    ax.set_ylabel("Sample Count")
    plt.tight_layout()
    plt.savefig(AUDIT_DIR / "plot_b_hist_test.png")
    plt.close()

    # Plot C: Zoomed Histogram [0.49, 0.51]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(between_49_51, bins=50, color='#e74c3c', edgecolor='black', alpha=0.7)
    ax.set_title("Plot C: Zoomed Probability Histogram (0.49 <= p <= 0.51)")
    ax.set_xlabel("Probability p(Attack|x)")
    ax.set_ylabel("Sample Count")
    plt.tight_layout()
    plt.savefig(AUDIT_DIR / "plot_c_zoomed_hist.png")
    plt.close()

    # Plot D: Empirical CDF
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sorted_p = np.sort(p_calib)
    cdf = np.arange(1, len(sorted_p) + 1) / len(sorted_p)
    ax.plot(sorted_p, cdf, color='#9b59b6', linewidth=2)
    ax.set_title("Plot D: Empirical CDF of Full ARGUS Probabilities")
    ax.set_xlabel("Probability p(Attack|x)")
    ax.set_ylabel("Cumulative Probability")
    plt.tight_layout()
    plt.savefig(AUDIT_DIR / "plot_d_ecdf.png")
    plt.close()

    # Plot E: MCC vs Threshold (0.49 -> 0.51)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df_high_res["Threshold"], df_high_res["MCC"], '-o', color='#34495e', markersize=3)
    ax.set_title("Plot E: High-Resolution MCC vs Threshold (0.4900 -> 0.5100)")
    ax.set_xlabel("Threshold θ")
    ax.set_ylabel("MCC")
    plt.tight_layout()
    plt.savefig(AUDIT_DIR / "plot_e_mcc_high_res.png")
    plt.close()

    # Plot F: Recall vs Threshold (0.49 -> 0.51)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df_high_res["Threshold"], df_high_res["Recall"], '-o', color='#c0392b', markersize=3)
    ax.set_title("Plot F: High-Resolution Recall vs Threshold (0.4900 -> 0.5100)")
    ax.set_xlabel("Threshold θ")
    ax.set_ylabel("Recall")
    plt.tight_layout()
    plt.savefig(AUDIT_DIR / "plot_f_recall_high_res.png")
    plt.close()

    print("   Saved Plots A through F to phase4_results/probability_audit/")

if __name__ == "__main__":
    main()
