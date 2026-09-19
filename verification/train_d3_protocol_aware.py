#!/usr/bin/env python3
"""
ARGUS Phase 5: Protocol-Aware IEC 60870-5-104 Feature Recovery Experiment
===========================================================================
Tests whether protocol-semantic ASDU/APDU fields (ASDU type IDs, COTs, IOA structure,
I/S/U frame ratios, command-vs-monitoring ratios, APDU length statistics) recover
detection power on the SCADA/IEC 60870-5-104 target domain (D3).

Evaluates:
1. Protocol-Aware Features Only (ASDU/APDU fields + engineered ratios)
2. Full Combined Set (Protocol-Aware + Transport/Flow statistics)
"""

import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score,
    matthews_corrcoef, precision_score, recall_score, roc_auc_score
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


def load_and_engineer_layer_data() -> pd.DataFrame:
    """Load all 118 custom layer CSV files containing pre-parsed IEC 60870-5-104
    ASDU and APDU protocol fields."""
    print("[1] Loading all IEC 60870-5-104 Protocol Layer CSVs...")
    layer_files = list(RAW_DATA_DIR.rglob("*iec104_network_flow_leayer.csv"))
    print(f"  Found {len(layer_files)} layer flow CSV files.")

    dfs = []
    for f in layer_files:
        try:
            df = pd.read_csv(f, low_memory=False)
            dfs.append(df)
        except Exception as e:
            print(f"  [!] Error reading {f.name}: {e}")

    df_all = pd.concat(dfs, ignore_index=True)
    df_all["label"] = df_all["Label"].apply(
        lambda x: 0 if str(x).strip().upper() == "NORMAL" else 1
    )

    print(f"  Total protocol layer flows loaded: {len(df_all):,}")
    print(f"  Label distribution: {df_all['label'].value_counts().to_dict()}")

    print("\n[2] Engineering protocol-aware ASDU/APDU ratio features...")
    # Safe division helper
    def safe_div(a, b):
        return np.where(b == 0, 0, a / (b + 1e-10))

    # Command frames vs Monitoring frames
    cmd_cols = [
        "type_id_process_information_in_control_direction",
        "type_id_system_information_in_control_direction",
        "type_id_parameter_in_control_direction",
        "type_id_file_transfer",
    ]
    mon_cols = [
        "type_id_process_information_in_monitor_direction",
        "type_id_system_information_in_monitor_direction",
    ]

    cmd_sum = sum(df_all[c] for c in cmd_cols if c in df_all.columns)
    mon_sum = sum(df_all[c] for c in mon_cols if c in df_all.columns)

    df_all["cmd_frame_count"] = cmd_sum
    df_all["mon_frame_count"] = mon_sum
    df_all["cmd_to_mon_ratio"] = safe_div(cmd_sum, mon_sum)

    # I, S, U message ratios relative to total IEC104 packets
    i_pkts = df_all.get("flow total IEC104_I_Message_SingleIOA packets", 0) + df_all.get("flow total IEC104_I_Message_SeqIOA packets", 0)
    s_pkts = df_all.get("flow total IEC104_S_Message packets", 0)
    u_pkts = df_all.get("flow total IEC104_U_Message packets", 0)
    tot_iec_pkts = i_pkts + s_pkts + u_pkts

    df_all["i_msg_ratio"] = safe_div(i_pkts, tot_iec_pkts)
    df_all["s_msg_ratio"] = safe_div(s_pkts, tot_iec_pkts)
    df_all["u_msg_ratio"] = safe_div(u_pkts, tot_iec_pkts)

    # IOA structure: Single IOA vs Sequential IOA ratio
    seq_ioa = df_all.get("flow total IEC104_I_Message_SeqIOA packets", 0)
    single_ioa = df_all.get("flow total IEC104_I_Message_SingleIOA packets", 0)
    df_all["seq_to_single_ioa_ratio"] = safe_div(seq_ioa, single_ioa)

    return df_all


def get_feature_subsets(df: pd.DataFrame):
    """Identify Protocol-Aware feature subset and Full Combined feature subset."""
    exclude = {
        "flow id", "protocol", "src ip", "dst ip", "src port", "dst port",
        "flow start timestamp", "Label", "label", "source_file"
    }

    # Protocol-aware feature names/patterns
    protocol_keywords = [
        "cot=", "type_id_", "IEC104", "APDU", "apdu", "cmd_", "mon_",
        "ratio", "seq_to_single"
    ]

    all_num_cols = [
        c for c in df.columns
        if c not in exclude and df[c].dtype in [np.float64, np.int64, np.float32, np.int32]
    ]

    # Filter out all-NaN or zero-variance
    valid_cols = [c for c in all_num_cols if df[c].notna().sum() > 50 and df[c].nunique() > 1]

    protocol_cols = [
        c for c in valid_cols
        if any(kw in c for kw in protocol_keywords)
    ]

    print(f"\n[3] Feature Subsets Identified:")
    print(f"  Protocol-Aware ASDU/APDU features count: {len(protocol_cols)}")
    print(f"  Full Combined features count:           {len(valid_cols)}")

    return protocol_cols, valid_cols


def run_experiment(df: pd.DataFrame, feature_cols: list, model_name: str, desc: str):
    print(f"\n{'='*70}")
    print(f"RUNNING EXPERIMENT: {model_name} ({desc})")
    print(f"Feature count: {len(feature_cols)}")
    print(f"{'='*70}")

    X = df[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0).values
    y = df["label"].values

    distinct_tuples = len(np.unique(X, axis=0))
    print(f"Distinct feature tuples: {distinct_tuples:,} / {len(X):,}")

    # Stratified split: 80% train (with 20% calib sub-split), 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    X_calib, X_adapt, y_calib, y_adapt = train_test_split(
        X_train, y_train, test_size=0.80, random_state=42, stratify=y_train
    )

    # Train LightGBM
    train_data = lgb.Dataset(X_adapt, label=y_adapt, feature_name=feature_cols)
    valid_data = lgb.Dataset(X_calib, label=y_calib, feature_name=feature_cols, reference=train_data)

    model = lgb.train(
        LGB_PARAMS, train_data, num_boost_round=NUM_BOOST_ROUND,
        valid_sets=[train_data, valid_data],
        valid_names=["training", "validation"],
        callbacks=[lgb.log_evaluation(period=0)]
    )

    model_path = MODELS_DIR / f"{model_name}.txt"
    model.save_model(str(model_path))

    # Evaluate
    y_prob_test = model.predict(X_test)
    y_prob_calib = model.predict(X_calib)

    auc_test = roc_auc_score(y_test, y_prob_test)
    auc_calib = roc_auc_score(y_calib, y_prob_calib)
    distinct_probs = len(np.unique(np.round(y_prob_test, 6)))

    print(f"\nROC-AUC (Test):  {auc_test:.6f}")
    print(f"ROC-AUC (Calib): {auc_calib:.6f}")
    print(f"Distinct test probabilities: {distinct_probs}")

    # Threshold sweep on calibration set
    best_f1 = -1
    best_f1_th = 0.50
    best_mcc = -999
    best_mcc_th = 0.50

    for th_int in range(1, 100):
        th = th_int / 100.0
        y_pred = (y_prob_calib >= th).astype(int)
        tp = np.sum((y_calib == 1) & (y_pred == 1))
        fp = np.sum((y_calib == 0) & (y_pred == 1))
        tn = np.sum((y_calib == 0) & (y_pred == 0))
        fn = np.sum((y_calib == 1) & (y_pred == 0))

        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        denom = np.sqrt(float(tp + fp) * float(tp + fn) * float(tn + fp) * float(tn + fn))
        mcc = (float(tp) * tn - float(fp) * fn) / denom if denom > 0 else 0

        if f1 > best_f1:
            best_f1 = f1
            best_f1_th = th
        if mcc > best_mcc:
            best_mcc = mcc
            best_mcc_th = th

    # Evaluate at optimal MCC threshold and at default 0.50
    def eval_at_th(th):
        y_pred = (y_prob_test >= th).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        return {
            "threshold": th, "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "f1": float(f1_score(y_test, y_pred)),
            "mcc": float(matthews_corrcoef(y_test, y_pred)),
            "fpr": float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        }

    metrics_opt = eval_at_th(best_mcc_th)
    metrics_50 = eval_at_th(0.50)

    print(f"\nMetrics at Optimal Threshold θ* = {best_mcc_th:.2f}:")
    print(f"  TN={metrics_opt['tn']} FP={metrics_opt['fp']} FN={metrics_opt['fn']} TP={metrics_opt['tp']}")
    print(f"  Precision: {metrics_opt['precision']:.4f}  Recall: {metrics_opt['recall']:.4f}  F1: {metrics_opt['f1']:.4f}  MCC: {metrics_opt['mcc']:.4f}")

    print(f"\nMetrics at θ = 0.50:")
    print(f"  TN={metrics_50['tn']} FP={metrics_50['fp']} FN={metrics_50['fn']} TP={metrics_50['tp']}")
    print(f"  Precision: {metrics_50['precision']:.4f}  Recall: {metrics_50['recall']:.4f}  F1: {metrics_50['f1']:.4f}  MCC: {metrics_50['mcc']:.4f}")

    # Top feature importances
    imp = model.feature_importance(importance_type="gain")
    top_features = sorted(zip(feature_cols, imp), key=lambda x: x[1], reverse=True)[:15]

    print(f"\nTop 10 Feature Drivers:")
    for fname, fimp in top_features[:10]:
        print(f"  {fname:<45} {fimp:>12.2f}")

    return {
        "model_name": model_name,
        "description": desc,
        "num_features": len(feature_cols),
        "distinct_tuples": distinct_tuples,
        "auc_test": float(auc_test),
        "auc_calib": float(auc_calib),
        "distinct_probs": distinct_probs,
        "best_mcc_th": best_mcc_th,
        "metrics_optimal": metrics_opt,
        "metrics_50": metrics_50,
        "top_features": [(f, float(v)) for f, v in top_features]
    }


def main():
    print("=" * 80)
    print("ARGUS PROTOCOL-AWARE IEC 60870-5-104 EXPERIMENT")
    print("=" * 80)

    df_layer = load_and_engineer_layer_data()
    protocol_cols, combined_cols = get_feature_subsets(df_layer)

    res_protocol = run_experiment(
        df_layer, protocol_cols, "model_d3_protocol_aware",
        "Protocol-Aware ASDU/APDU Features Only"
    )

    res_combined = run_experiment(
        df_layer, combined_cols, "model_d3_protocol_combined",
        "Protocol-Aware ASDU/APDU + Transport/Flow Features Combined"
    )

    # Save summary results JSON
    summary = {
        "dataset_size": len(df_layer),
        "label_counts": df_layer["label"].value_counts().to_dict(),
        "protocol_aware_results": res_protocol,
        "combined_results": res_combined
    }
    with open(RESULTS_DIR / "protocol_aware_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n[+] Experiment complete. Summary saved to verification/protocol_aware_summary.json")


if __name__ == "__main__":
    main()
