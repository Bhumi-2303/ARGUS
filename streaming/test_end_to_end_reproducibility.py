#!/usr/bin/env python3
"""
End-to-End Streaming Pipeline Reproducibility Verification Script.
Replays a labeled SCADA test slice (N = 1000 samples) through the detector API,
builds the confusion matrix from scratch based on live returned predictions,
and diffs against original verified Phase 3 research artifacts.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, recall_score, precision_score
from fastapi.testclient import TestClient
from api.main import app as detector_app

PROJECT_ROOT = Path(__file__).resolve().parent.parent
P3_PREDS_PATH = PROJECT_ROOT / "phase3_results/experiments/D2_D3_CORAL/predictions.csv"
TEST_FEATS_PATH = PROJECT_ROOT / "ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv"

def run_reproducibility_test(num_samples: int = 1000):
    print("=" * 85)
    print(f"[*] RUNNING END-TO-END STREAMING REPRODUCIBILITY TEST (N = {num_samples} samples)")
    print("=" * 85)

    if not P3_PREDS_PATH.exists() or not TEST_FEATS_PATH.exists():
        raise FileNotFoundError(f"Required test artifacts not found at {P3_PREDS_PATH} or {TEST_FEATS_PATH}")

    # 1. Load labeled test slice
    df_preds = pd.read_csv(P3_PREDS_PATH).iloc[:num_samples]
    df_feats = pd.read_csv(TEST_FEATS_PATH).iloc[:num_samples]

    y_true = df_preds["y_true"].values
    y_prob_orig = df_preds["y_prob"].values
    y_pred_orig = (y_prob_orig >= 0.50).astype(int)

    tn_orig, fp_orig, fn_orig, tp_orig = confusion_matrix(y_true, y_pred_orig).ravel()

    # 2. Replay test slice through Detector API
    feature_cols = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
    records = df_feats[feature_cols].to_dict(orient="records")

    live_preds = []
    live_probs = []

    with TestClient(detector_app) as client:
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            resp = client.post("/predict", json=batch)
            assert resp.status_code == 200, f"Predict failed with HTTP {resp.status_code}"
            res_data = resp.json()["predictions"]
            for item in res_data:
                live_preds.append(item["prediction"])
                live_probs.append(item["probability"])

    live_preds = np.array(live_preds)
    live_probs = np.array(live_probs)

    tn_live, fp_live, fn_live, tp_live = confusion_matrix(y_true, live_preds).ravel()

    # 3. Diff Confusion Matrix and Metrics
    acc_orig = accuracy_score(y_true, y_pred_orig)
    acc_live = accuracy_score(y_true, live_preds)
    rec_orig = recall_score(y_true, y_pred_orig)
    rec_live = recall_score(y_true, live_preds)
    prec_orig = precision_score(y_true, y_pred_orig)
    prec_live = precision_score(y_true, live_preds)
    f1_orig = f1_score(y_true, y_pred_orig)
    f1_live = f1_score(y_true, live_preds)

    print(f"{'Metric / Matrix Cell':<32} | {'Original Verified':<20} | {'Live Reproduced':<20} | {'Diff':<10}")
    print("-" * 85)
    print(f"{'True Negatives (TN)':<32} | {tn_orig:<20} | {tn_live:<20} | {tn_live - tn_orig:<10}")
    print(f"{'False Positives (FP)':<32} | {fp_orig:<20} | {fp_live:<20} | {fp_live - fp_orig:<10}")
    print(f"{'False Negatives (FN)':<32} | {fn_orig:<20} | {fn_live:<20} | {fn_live - fn_orig:<10}")
    print(f"{'True Positives (TP)':<32} | {tp_orig:<20} | {tp_live:<20} | {tp_live - tp_orig:<10}")
    print("-" * 85)
    print(f"{'Accuracy':<32} | {acc_orig:<20.4f} | {acc_live:<20.4f} | {acc_live - acc_orig:<10.4f}")
    print(f"{'Attack Recall (TPR)':<32} | {rec_orig:<20.4f} | {rec_live:<20.4f} | {rec_live - rec_orig:<10.4f}")
    print(f"{'Precision':<32} | {prec_orig:<20.4f} | {prec_live:<20.4f} | {prec_live - prec_orig:<10.4f}")
    print(f"{'F1 Score':<32} | {f1_orig:<20.4f} | {f1_live:<20.4f} | {f1_live - f1_orig:<10.4f}")
    print("=" * 85)

    divergences = int(np.sum(y_pred_orig != live_preds))
    print(f"Divergent Prediction Count across {num_samples} records: {divergences}")

    assert divergences == 0, f"Reproducibility failure: {divergences} predictions diverged!"
    print("\n[✓] VERDICT: EXACT MATCH! The live pipeline perfectly reproduces reported research metrics.")

if __name__ == "__main__":
    run_reproducibility_test(num_samples=1000)
