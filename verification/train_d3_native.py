#!/usr/bin/env python3
"""
ARGUS Phase 5: Native SCADA-Domain Feature Recovery Experiment
================================================================
Trains a SCADA-domain-only LightGBM classifier (model_d3_native) using ALL available
CIC flow features from the IEC 60870-5-104 dataset, NOT the 4-feature cross-domain
harmonized representation.

This script:
1. Loads all raw CIC flow CSVs from data/IEC104/extracted_csvs/
2. Engineers features from the 84-column CIC flow representation
3. Splits into the same calibration/test partition sizes used for E5
4. Trains LightGBM with same hyperparameters as model_d2_coral for fair comparison
5. Computes ROC-AUC, threshold sweep, confusion matrix, and distinct feature tuples
6. Saves model to phase3_results/models/model_d3_native.txt
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
import json
import warnings
from pathlib import Path
from sklearn.metrics import (
    roc_auc_score, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score, matthews_corrcoef
)
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
PROJECT_ROOT = _curr
RAW_DATA_DIR = PROJECT_ROOT / "data/IEC104/extracted_csvs"
MODELS_DIR = PROJECT_ROOT / "phase3_results/models"
RESULTS_DIR = PROJECT_ROOT / "verification"

# Same LightGBM hyperparameters as model_d2_coral for fair comparison
LGB_PARAMS = {
    "objective": "binary",
    "metric": "binary_logloss",
    "boosting_type": "gbdt",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "max_depth": 6,
    "min_child_samples": 20,
    "verbose": -1,
    "seed": 42,
    "n_jobs": -1,
    "is_unbalance": True,
}
NUM_BOOST_ROUND = 200

# The 4 harmonized features used in model_d2_coral (for comparison)
HARMONIZED_FEATURES = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']


def load_all_cic_flows() -> pd.DataFrame:
    """Load all CIC Flow CSVs from extracted_csvs, label them using CICFlowMeter's
    per-flow 'Label' column: 'NORMAL' = benign (0), anything else = attack (1)."""
    print("[1] Loading all IEC 60870-5-104 CIC Flow CSVs...")
    attack_dirs = [d for d in sorted(RAW_DATA_DIR.iterdir()) if d.is_dir()]
    
    all_dfs = []
    for attack_dir in attack_dirs:
        dir_name = attack_dir.name
        # Use *_Flow.csv files (CICFlowMeter output), skip iec104_only variants
        flow_files = sorted(attack_dir.glob("*_Flow.csv"))
        flow_files = [f for f in flow_files if "iec104_only" not in f.name]
        
        for flow_file in flow_files:
            try:
                df = pd.read_csv(flow_file, low_memory=False)
                df["attack_category"] = dir_name
                all_dfs.append(df)
            except Exception as e:
                print(f"  [!] Skipping {flow_file.name}: {e}")
    
    df_all = pd.concat(all_dfs, ignore_index=True)
    
    # Use CICFlowMeter's per-flow Label column for ground truth
    # Each pcap contains both NORMAL and attack flows; Label distinguishes them
    df_all["label"] = df_all["Label"].apply(
        lambda x: 0 if str(x).strip().upper() == "NORMAL" else 1
    )
    
    print(f"  Total rows loaded: {len(df_all):,}")
    print(f"  Label distribution: {df_all['label'].value_counts().to_dict()}")
    print(f"  Attack categories: {df_all['attack_category'].nunique()}")
    print(f"  CICFlowMeter Label values: {df_all['Label'].value_counts().to_dict()}")
    return df_all


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer features from CIC flow data, including the excluded domain-specific
    features (pkt_min_to_max, pkt_range_ratio, log_flow_activity) and all other
    usable numeric flow statistics.
    """
    print("[2] Engineering features from raw CIC flow data...")
    
    # Start with existing CIC numeric columns
    exclude_cols = {"Flow ID", "Src IP", "Dst IP", "Timestamp", "Label",
                    "label", "attack_category", "Src Port", "Dst Port", "Protocol"}
    
    numeric_cols = []
    for col in df.columns:
        if col not in exclude_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                if df[col].notna().sum() > 0:
                    numeric_cols.append(col)
            except:
                pass
    
    # Engineer the harmonized features for comparison
    if "Pkt Len Mean" in df.columns and "Pkt Len Max" in df.columns:
        df["pkt_mean_to_max"] = np.where(
            df["Pkt Len Max"] == 0, 0, df["Pkt Len Mean"] / df["Pkt Len Max"]
        )
    
    if "Pkt Len Mean" in df.columns:
        df["log_pkt_mean"] = np.log1p(df["Pkt Len Mean"].clip(lower=0))
    
    if "Pkt Len Max" in df.columns:
        df["log_pkt_max"] = np.log1p(df["Pkt Len Max"].clip(lower=0))
    
    # TCP flag density (multiplicity)
    flag_cols = [c for c in df.columns if "Flag" in c and c not in exclude_cols]
    if flag_cols:
        df["tcp_flag_density"] = df[flag_cols].sum(axis=1)
    
    # === DOMAIN-SPECIFIC FEATURES EXCLUDED FROM HARMONIZED SET ===
    
    # pkt_min_to_max: ratio of min to max packet length
    if "Pkt Len Min" in df.columns and "Pkt Len Max" in df.columns:
        df["pkt_min_to_max"] = np.where(
            df["Pkt Len Max"] == 0, 0, df["Pkt Len Min"] / df["Pkt Len Max"]
        )
    
    # pkt_range_ratio: (max - min) / mean, measures spread relative to center
    if "Pkt Len Min" in df.columns and "Pkt Len Max" in df.columns and "Pkt Len Mean" in df.columns:
        pkt_range = df["Pkt Len Max"] - df["Pkt Len Min"]
        df["pkt_range_ratio"] = np.where(
            df["Pkt Len Mean"] == 0, 0, pkt_range / df["Pkt Len Mean"]
        )
    
    # log_flow_activity: log of flow packets/s (measures activity intensity)
    if "Flow Pkts/s" in df.columns:
        df["log_flow_activity"] = np.log1p(df["Flow Pkts/s"].clip(lower=0))
    
    # log_flow_bytes: log of flow bytes/s
    if "Flow Byts/s" in df.columns:
        df["log_flow_bytes"] = np.log1p(df["Flow Byts/s"].clip(lower=0))
    
    # Fwd/Bwd packet ratio
    if "Tot Fwd Pkts" in df.columns and "Tot Bwd Pkts" in df.columns:
        total_pkts = df["Tot Fwd Pkts"] + df["Tot Bwd Pkts"]
        df["fwd_pkt_ratio"] = np.where(total_pkts == 0, 0, df["Tot Fwd Pkts"] / total_pkts)
    
    # Flow duration log
    if "Flow Duration" in df.columns:
        df["log_flow_duration"] = np.log1p(df["Flow Duration"].clip(lower=0))
    
    # IAT coefficient of variation
    if "Flow IAT Mean" in df.columns and "Flow IAT Std" in df.columns:
        df["iat_cv"] = np.where(
            df["Flow IAT Mean"] == 0, 0, df["Flow IAT Std"] / (df["Flow IAT Mean"] + 1e-10)
        )
    
    # Collect ALL usable feature columns
    final_exclude = {"Flow ID", "Src IP", "Dst IP", "Timestamp", "Label",
                     "label", "attack_category", "Src Port", "Dst Port", "Protocol"}
    feature_cols = [c for c in df.columns if c not in final_exclude and df[c].dtype in [np.float64, np.int64, np.float32, np.int32]]
    
    # Drop columns with all NaN or all constant
    valid_cols = []
    for c in feature_cols:
        if df[c].notna().sum() > 100 and df[c].nunique() > 1:
            valid_cols.append(c)
    
    print(f"  Total engineered feature columns: {len(valid_cols)}")
    print(f"  Includes domain-specific: pkt_min_to_max, pkt_range_ratio, log_flow_activity, log_flow_bytes, fwd_pkt_ratio, log_flow_duration, iat_cv")
    
    return df, valid_cols


def main():
    print("=" * 80)
    print("ARGUS NATIVE SCADA-DOMAIN FEATURE RECOVERY EXPERIMENT")
    print("Model: model_d3_native (LightGBM, all CIC features, D3-only)")
    print("=" * 80)
    
    # 1. Load data
    df_all = load_all_cic_flows()
    
    # 2. Engineer features
    df_all, feature_cols = engineer_features(df_all)
    
    # Replace inf/nan
    X_all = df_all[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0).values
    y_all = df_all["label"].values
    
    print(f"\n[3] Dataset shape: X={X_all.shape}, y={y_all.shape}")
    print(f"  Feature count: {X_all.shape[1]}")
    print(f"  Distinct feature tuples (native): {len(np.unique(X_all, axis=0)):,}")
    
    # Compare with 4-feature distinct tuples
    harmonized_idx = [feature_cols.index(c) for c in HARMONIZED_FEATURES if c in feature_cols]
    if harmonized_idx:
        X_harm = X_all[:, harmonized_idx]
        print(f"  Distinct feature tuples (4-harmonized): {len(np.unique(X_harm, axis=0)):,}")
    
    # 3. Split: same proportions as CORAL pipeline
    # CORAL: 2,857,812 train (80%) + 714,453 test (20%)
    # Train further split: 571,563 calib (20% of train) + 2,286,249 adapt (80% of train)
    X_train, X_test, y_train, y_test = train_test_split(
        X_all, y_all, test_size=0.20, random_state=42, stratify=y_all
    )
    X_calib, X_adapt, y_calib, y_adapt = train_test_split(
        X_train, y_train, test_size=0.80, random_state=42, stratify=y_train
    )
    
    print(f"\n[4] Data Splits:")
    print(f"  Train (adaptation): {X_adapt.shape[0]:,} ({y_adapt.mean()*100:.1f}% attack)")
    print(f"  Calibration: {X_calib.shape[0]:,} ({y_calib.mean()*100:.1f}% attack)")
    print(f"  Test (held-out): {X_test.shape[0]:,} ({y_test.mean()*100:.1f}% attack)")
    
    # 4. Train LightGBM
    print(f"\n[5] Training LightGBM (same hyperparameters as model_d2_coral)...")
    train_data = lgb.Dataset(X_adapt, label=y_adapt, feature_name=feature_cols)
    valid_data = lgb.Dataset(X_calib, label=y_calib, feature_name=feature_cols, reference=train_data)
    
    eval_results = {}
    model = lgb.train(
        LGB_PARAMS, train_data, num_boost_round=NUM_BOOST_ROUND,
        valid_sets=[train_data, valid_data],
        valid_names=["training", "validation"],
        callbacks=[
            lgb.record_evaluation(eval_results),
            lgb.log_evaluation(period=50)
        ]
    )
    
    # Save model
    model_path = MODELS_DIR / "model_d3_native.txt"
    model.save_model(str(model_path))
    print(f"  Model saved to: {model_path}")
    
    # 5. Predict on held-out test set
    y_prob_test = model.predict(X_test)
    y_prob_calib = model.predict(X_calib)
    
    # 6. ROC-AUC
    auc_test = roc_auc_score(y_test, y_prob_test)
    auc_calib = roc_auc_score(y_calib, y_prob_calib)
    print(f"\n[6] ROC-AUC Results:")
    print(f"  model_d3_native (Test):  {auc_test:.6f}")
    print(f"  model_d3_native (Calib): {auc_calib:.6f}")
    print(f"  model_d2_coral  (Test):  0.486020  (from probability_distribution_report.md)")
    print(f"  E5 Fused        (Test):  0.501695  (from probability_distribution_report.md)")
    
    # 7. Distinct probability values
    distinct_probs = len(np.unique(np.round(y_prob_test, 6)))
    print(f"\n[7] Probability Resolution:")
    print(f"  Distinct probabilities (model_d3_native): {distinct_probs}")
    print(f"  Distinct probabilities (model_d2_coral):  89")
    
    # 8. Threshold sweep on CALIBRATION set
    print(f"\n[8] Threshold Sweep on Calibration Set (N={len(y_calib):,})...")
    print(f"{'θ':<6} {'Recall':<10} {'FPR':<10} {'Prec':<10} {'F1':<10} {'MCC':<10}")
    print("-" * 56)
    
    best_f1 = -1
    best_f1_th = 0.50
    best_mcc = -999
    best_mcc_th = 0.50
    
    sweep_results = []
    for th_int in range(1, 100):
        th = th_int / 100.0
        y_pred = (y_prob_calib >= th).astype(int)
        tp = np.sum((y_calib == 1) & (y_pred == 1))
        fp = np.sum((y_calib == 0) & (y_pred == 1))
        tn = np.sum((y_calib == 0) & (y_pred == 0))
        fn = np.sum((y_calib == 1) & (y_pred == 0))
        
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr_val = fp / (fp + tn) if (fp + tn) > 0 else 0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2*tp / (2*tp + fp + fn) if (2*tp + fp + fn) > 0 else 0
        denom = np.sqrt(float(tp+fp) * float(tp+fn) * float(tn+fp) * float(tn+fn))
        mcc = (float(tp)*tn - float(fp)*fn) / denom if denom > 0 else 0
        
        sweep_results.append({
            "threshold": th, "recall": rec, "fpr": fpr_val,
            "precision": prec, "f1": f1, "mcc": mcc,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn
        })
        
        if f1 > best_f1:
            best_f1 = f1
            best_f1_th = th
        if mcc > best_mcc:
            best_mcc = mcc
            best_mcc_th = th
        
        if th_int % 5 == 0 or th_int <= 5:
            print(f"{th:<6.2f} {rec:<10.4f} {fpr_val:<10.4f} {prec:<10.4f} {f1:<10.4f} {mcc:<10.4f}")
    
    print("-" * 56)
    print(f"Best F1  = {best_f1:.4f} at θ = {best_f1_th:.2f}")
    print(f"Best MCC = {best_mcc:.4f} at θ = {best_mcc_th:.2f}")
    
    # 9. Evaluate at best threshold on TEST set
    optimal_th = best_mcc_th
    y_pred_test = (y_prob_test >= optimal_th).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred_test).ravel()
    
    print(f"\n[9] Final Metrics at Optimal Threshold θ* = {optimal_th:.2f} on HELD-OUT TEST SET:")
    print(f"  TN={tn:,}  FP={fp:,}  FN={fn:,}  TP={tp:,}")
    print(f"  Accuracy:  {accuracy_score(y_test, y_pred_test):.4f}")
    print(f"  Precision: {precision_score(y_test, y_pred_test):.4f}")
    print(f"  Recall:    {recall_score(y_test, y_pred_test):.4f}")
    print(f"  F1 Score:  {f1_score(y_test, y_pred_test):.4f}")
    print(f"  MCC:       {matthews_corrcoef(y_test, y_pred_test):.4f}")
    print(f"  ROC-AUC:   {auc_test:.4f}")
    
    # Also evaluate at θ=0.50 for direct comparison with model_d2_coral
    y_pred_50 = (y_prob_test >= 0.50).astype(int)
    tn50, fp50, fn50, tp50 = confusion_matrix(y_test, y_pred_50).ravel()
    print(f"\n[10] Metrics at θ=0.50 (for direct comparison with model_d2_coral):")
    print(f"  TN={tn50:,}  FP={fp50:,}  FN={fn50:,}  TP={tp50:,}")
    print(f"  Accuracy:  {accuracy_score(y_test, y_pred_50):.4f}")
    print(f"  Precision: {precision_score(y_test, y_pred_50):.4f}")
    print(f"  Recall:    {recall_score(y_test, y_pred_50):.4f}")
    print(f"  F1 Score:  {f1_score(y_test, y_pred_50):.4f}")
    print(f"  MCC:       {matthews_corrcoef(y_test, y_pred_50):.4f}")
    
    # 10. Feature importance (top 15)
    importance = model.feature_importance(importance_type='gain')
    feat_imp = sorted(zip(feature_cols, importance), key=lambda x: x[1], reverse=True)
    print(f"\n[11] Top 15 Features by Gain Importance:")
    for fname, fimp in feat_imp[:15]:
        print(f"  {fname:<30} {fimp:>12.2f}")
    
    # Save sweep results
    pd.DataFrame(sweep_results).to_csv(RESULTS_DIR / "d3_native_threshold_sweep.csv", index=False)
    
    # Save config
    config = {
        "model_name": "model_d3_native",
        "description": "SCADA-domain-only LightGBM trained on ALL CIC flow features from IEC 60870-5-104",
        "num_features": len(feature_cols),
        "feature_names": feature_cols,
        "lgb_params": LGB_PARAMS,
        "num_boost_round": NUM_BOOST_ROUND,
        "optimal_threshold": optimal_th,
        "roc_auc_test": auc_test,
        "best_f1": best_f1,
        "best_mcc": best_mcc,
        "distinct_prob_values": distinct_probs,
        "test_set_size": int(len(y_test)),
        "train_set_size": int(len(y_adapt)),
        "calib_set_size": int(len(y_calib)),
    }
    with open(RESULTS_DIR / "d3_native_config.json", "w") as f:
        json.dump(config, f, indent=2, default=str)
    
    print(f"\n[12] Artifacts saved to {RESULTS_DIR}/")
    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
