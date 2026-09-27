#!/usr/bin/env python3
"""
ARGUS Domain Adaptation DA-01 — Phase DA-01D & DA-01E:
FT-Transformer Training on CORAL-Aligned Features & Frozen Test Evaluation.
Trains across 5 random seeds [42, 123, 456, 789, 1011], performs calibration on D3 calib,
and evaluates blind inference on frozen D3 test partition (N = 714,453).
"""

import os
import sys
import gc
import json
import time
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_recall_curve,
    roc_curve, auc, confusion_matrix, accuracy_score, precision_score,
    recall_score, f1_score, matthews_corrcoef, log_loss, brier_score_loss
)

os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib_cache'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path("/Volumes/BLACK-BOX/ARGUS")
EE = BASE / "experiment_execution"
NR = EE / "neural_robustness"
DA = NR / "domain_adaptation"
CORAL_DATA_DIR = BASE / "ARGUS_Cross_Domain_Results/argus_coral_data"

sys.path.append(str(NR / "scripts"))
from ft_transformer import FTTransformer

FEATURE_COLS = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
SEEDS = [42, 123, 456, 789, 1011]
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

# FT-Transformer hyperparameters (identical to baseline B0)
HP = {
    "d_token": 32,
    "n_blocks": 2,
    "n_heads": 4,
    "d_ff": 64,
    "dropout": 0.10
}
BATCH_SIZE = 16384
MAX_EPOCHS = 10
PATIENCE = 2
LR = 0.001
WEIGHT_DECAY = 0.0001
MAX_TRAIN_SAMPLES = 500000

def compute_all_metrics_audited(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict:
    """Computes all audited metrics with step-function AP as primary PR ranking."""
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    y_prob_clipped = np.clip(y_prob, 1e-15, 1.0 - 1e-15)
    y_pred = (y_prob >= threshold).astype(int)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average='macro', zero_division=0))
    mcc = float(matthews_corrcoef(y_true, y_pred))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = float('nan')

    try:
        ap = float(average_precision_score(y_true, y_prob))
    except Exception:
        ap = float('nan')

    try:
        p_curve, r_curve, _ = precision_recall_curve(y_true, y_prob)
        pr_auc_trapz = float(auc(r_curve, p_curve))
    except Exception:
        pr_auc_trapz = float('nan')

    try:
        ll = float(log_loss(y_true, y_prob_clipped))
    except Exception:
        ll = float('nan')

    try:
        brier = float(brier_score_loss(y_true, y_prob_clipped))
    except Exception:
        brier = float('nan')

    return {
        'threshold': float(threshold),
        'tn': int(tn),
        'fp': int(fp),
        'fn': int(fn),
        'tp': int(tp),
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'macro_f1': f1_macro,
        'fpr': fpr,
        'fnr': fnr,
        'mcc': mcc,
        'roc_auc': roc_auc,
        'average_precision': ap,
        'pr_auc_trapezoidal': pr_auc_trapz,
        'log_loss': ll,
        'brier_score': brier
    }

def train_and_eval_seed(
    X_train_aligned: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    seed: int
):
    print(f"\n=========================================================================")
    print(f"TRAINING DA-01: FTT-SMALL + CORAL (Seed {seed}) on Device: {DEVICE}")
    print(f"=========================================================================")

    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    gc.collect()

    # Subsample training data if larger than max_train_samples (stratified)
    if len(X_train_aligned) > MAX_TRAIN_SAMPLES:
        _, X_tr_sub, _, y_tr_sub = train_test_split(
            X_train_aligned, y_train, test_size=MAX_TRAIN_SAMPLES, random_state=seed, stratify=y_train
        )
    else:
        X_tr_sub, y_tr_sub = X_train_aligned, y_train

    # Fast validation subset (50k samples) for epoch loss & early stopping
    if len(X_val) > 50000:
        _, X_val_sub, _, y_val_sub = train_test_split(
            X_val, y_val, test_size=50000, random_state=seed, stratify=y_val
        )
    else:
        X_val_sub, y_val_sub = X_val, y_val

    # Standard scaling fitted on aligned training subset
    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_tr_sub)
    X_val_scaled = scaler.transform(X_val_sub)

    # Tensor datasets & dataloaders
    tr_ds = TensorDataset(torch.tensor(X_tr_scaled, dtype=torch.float32), torch.tensor(y_tr_sub, dtype=torch.float32))
    val_ds = TensorDataset(torch.tensor(X_val_scaled, dtype=torch.float32), torch.tensor(y_val_sub, dtype=torch.float32))

    tr_loader = DataLoader(tr_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    model = FTTransformer(
        n_features=4,
        d_token=HP["d_token"],
        n_blocks=HP["n_blocks"],
        n_heads=HP["n_heads"],
        d_ff=HP["d_ff"],
        dropout=HP["dropout"]
    ).to(DEVICE)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    best_val_loss = float("inf")
    best_epoch = 0
    patience_counter = 0

    ckpt_dir = DA / f"checkpoints/DA01_FTT_CORAL_seed{seed}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt_path = ckpt_dir / "best_model.pt"

    history = []

    for epoch in range(1, MAX_EPOCHS + 1):
        t_ep_start = time.time()
        model.train()
        tr_loss_sum = 0.0
        tr_count = 0

        for bx, by in tr_loader:
            bx, by = bx.to(DEVICE), by.to(DEVICE)
            optimizer.zero_grad()
            logits = model(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()
            tr_loss_sum += loss.item() * len(by)
            tr_count += len(by)

        tr_loss = tr_loss_sum / tr_count

        # Validation on D3 target calibration split
        model.eval()
        val_loss_sum = 0.0
        val_count = 0
        val_preds = []
        val_targets = []

        with torch.no_grad():
            for bx, by in val_loader:
                bx, by = bx.to(DEVICE), by.to(DEVICE)
                logits = model(bx)
                loss = criterion(logits, by)
                val_loss_sum += loss.item() * len(by)
                val_count += len(by)
                probs = torch.sigmoid(logits).cpu().numpy()
                val_preds.extend(probs)
                val_targets.extend(by.cpu().numpy())

        val_loss = val_loss_sum / val_count
        val_auc = float(roc_auc_score(val_targets, val_preds))
        ep_duration = time.time() - t_ep_start

        history.append({
            "epoch": epoch,
            "train_loss": float(tr_loss),
            "val_loss": float(val_loss),
            "val_auc": float(val_auc),
            "lr": LR,
            "duration_s": float(ep_duration)
        })

        print(f"  Epoch {epoch:2d}/{MAX_EPOCHS:2d} | Train Loss: {tr_loss:.4f} | Val Loss: {val_loss:.4f} | Val ROC-AUC: {val_auc:.4f} ({ep_duration:.1f}s)")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), best_ckpt_path)
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"    Early stopping triggered at epoch {epoch} (Best epoch: {best_epoch}, Best Val Loss: {best_val_loss:.5f})")
                break

    # Save training history
    (DA / "logs").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(history).to_csv(DA / f"logs/DA01_training_history_seed{seed}.csv", index=False)

    # Load best checkpoint for full calibration and test evaluation
    model.load_state_dict(torch.load(best_ckpt_path, map_location=DEVICE))
    model.eval()

    # Predict on Full Target Calibration (N = 571,563) for threshold selection
    print("  [+] Evaluating Full D3 Calibration Split for Threshold Selection...")
    X_val_full_scaled = scaler.transform(X_val)
    val_full_ds = TensorDataset(torch.tensor(X_val_full_scaled, dtype=torch.float32))
    val_full_loader = DataLoader(val_full_ds, batch_size=BATCH_SIZE, shuffle=False)

    val_probs = []
    with torch.no_grad():
        for (bx,) in val_full_loader:
            bx = bx.to(DEVICE)
            logits = model(bx)
            probs = torch.sigmoid(logits).cpu().numpy()
            val_probs.extend(probs)
    val_probs = np.array(val_probs)

    # Optimize threshold on D3 calibration set (F1 optimization)
    best_th = 0.50
    best_f1_cal = -1.0
    for th in np.linspace(0.01, 0.99, 99):
        p_val = (val_probs >= th).astype(int)
        tp = np.sum((y_val == 1) & (p_val == 1))
        fp = np.sum((y_val == 0) & (p_val == 1))
        fn = np.sum((y_val == 1) & (p_val == 0))
        f1_c = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        if f1_c > best_f1_cal:
            best_f1_cal = f1_c
            best_th = float(th)

    print(f"  [+] Calibrated Threshold on D3: θ* = {best_th:.2f} (Calibration F1 = {best_f1_cal:.4f})")

    # Predict on Frozen Full Test Set (N = 714,453)
    print("  [+] Running Blind Inference on Frozen D3 Test Partition (N = 714,453)...")
    X_te_scaled = scaler.transform(X_test)
    te_ds = TensorDataset(torch.tensor(X_te_scaled, dtype=torch.float32))
    te_loader = DataLoader(te_ds, batch_size=BATCH_SIZE, shuffle=False)

    test_probs = []
    with torch.no_grad():
        for (bx,) in te_loader:
            bx = bx.to(DEVICE)
            logits = model(bx)
            probs = torch.sigmoid(logits).cpu().numpy()
            test_probs.extend(probs)
    test_probs = np.array(test_probs)

    assert len(test_probs) == 714453, f"Test prediction count mismatch: {len(test_probs)}"

    # Save Predictions
    (DA / "predictions").mkdir(parents=True, exist_ok=True)
    pred_df = pd.DataFrame({
        "sample_index": np.arange(len(test_probs)),
        "y_true": y_test,
        "probability": test_probs,
        "prediction_default": (test_probs >= 0.50).astype(int),
        "prediction_calibrated": (test_probs >= best_th).astype(int)
    })
    pred_df.to_csv(DA / f"predictions/DA01_seed{seed}.csv", index=False)
    print(f"  [+] Saved predictions/DA01_seed{seed}.csv ({len(pred_df):,} rows)")

    # Compute metrics at default (0.50) and calibrated thresholds
    m_def = compute_all_metrics_audited(y_test, test_probs, threshold=0.50)
    m_def.update({
        "experiment_id": "DA01_FTT_CORAL_RAW",
        "variant": "B1_CORAL",
        "source_domain": "D1",
        "target_domain": "D3",
        "feature_set": "ARGUS-4",
        "model": "FTT-SMALL + CORAL (θ=0.50)",
        "seed": seed,
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss),
        "is_calibrated": False
    })

    m_cal = compute_all_metrics_audited(y_test, test_probs, threshold=best_th)
    m_cal.update({
        "experiment_id": "DA01_FTT_CORAL_CALIB",
        "variant": "B1_CORAL",
        "source_domain": "D1",
        "target_domain": "D3",
        "feature_set": "ARGUS-4",
        "model": f"FTT-SMALL + CORAL (Calibrated θ={best_th:.2f})",
        "seed": seed,
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss),
        "is_calibrated": True
    })

    print(f"  [+] Test Results (Seed {seed}):")
    print(f"      ROC-AUC:           {m_cal['roc_auc']:.4f}")
    print(f"      Average Precision: {m_cal['average_precision']:.4f}")
    print(f"      F1 (Calibrated):   {m_cal['f1']:.4f}")
    print(f"      MCC (Calibrated):  {m_cal['mcc']:.4f}")
    print(f"      FPR (Calibrated):  {m_cal['fpr']*100:.2f}%")

    return m_def, m_cal, history, test_probs, best_th


def run_all_seeds():
    print("=========================================================================")
    print("ARGUS DA-01: EXECUTING MULTI-SEED EXPERIMENT (SEEDS: 42, 123, 456, 789, 1011)")
    print("=========================================================================")

    # 1. Load Datasets
    print("[1] Loading Datasets...")
    # D1 Source
    d1_df = pd.read_csv(CORAL_DATA_DIR / "ciciot_train_features.csv")
    X_s = d1_df[FEATURE_COLS].values.astype(np.float64)
    y_s = d1_df["label"].values.astype(int)
    del d1_df
    gc.collect()

    # D3 Unlabeled Adaptation
    d3_adapt_df = pd.read_csv(CORAL_DATA_DIR / "iec104_train_adaptation.csv", usecols=FEATURE_COLS)
    X_t_adapt = d3_adapt_df.values.astype(np.float64)
    del d3_adapt_df
    gc.collect()

    # D3 Target Calibration (with labels for validation/calibration)
    d3_calib_df = pd.read_csv(CORAL_DATA_DIR / "iec104_train_calibration.csv")
    X_val = d3_calib_df[FEATURE_COLS].values.astype(np.float32)
    y_val = d3_calib_df["label"].values.astype(int)
    del d3_calib_df
    gc.collect()

    # D3 Frozen Test Partition
    d3_test_df = pd.read_csv(CORAL_DATA_DIR / "iec104_test_features.csv")
    X_test = d3_test_df[FEATURE_COLS].values.astype(np.float32)
    y_test = d3_test_df["label"].values.astype(int)
    del d3_test_df
    gc.collect()

    # 2. Fit CORAL Alignment Operator
    print("[2] Fitting Second-Order Covariance Alignment Operator...")
    from stage_b_c_coral import CORALOperator
    coral = CORALOperator(reg=1e-6)
    coral.fit(X_s, X_t_adapt)
    X_s_aligned = coral.transform_source(X_s).astype(np.float32)
    del X_s, X_t_adapt
    gc.collect()

    raw_results = []
    all_seed_probs = {}
    all_calib_thresholds = {}

    for seed in SEEDS:
        m_def, m_cal, hist, t_probs, best_th = train_and_eval_seed(
            X_s_aligned, y_s, X_val, y_val, X_test, y_test, seed
        )
        raw_results.append(m_def)
        raw_results.append(m_cal)
        all_seed_probs[seed] = t_probs
        all_calib_thresholds[seed] = best_th

        # Update experiment state after each seed
        with open(DA / "experiment_state.json", "r") as f:
            state = json.load(f)
        state["current_seed"] = seed
        if seed not in state["completed_seeds"]:
            state["completed_seeds"].append(seed)
        state["checkpoint_path"] = f"experiment_execution/neural_robustness/domain_adaptation/checkpoints/DA01_FTT_CORAL_seed{seed}/best_model.pt"
        state["last_successful_artifact"] = f"experiment_execution/neural_robustness/domain_adaptation/predictions/DA01_seed{seed}.csv"
        state["status"] = f"COMPLETED_SEED_{seed}"
        state["timestamp"] = datetime.now().isoformat()
        with open(DA / "experiment_state.json", "w") as f:
            json.dump(state, f, indent=2)

    # Save raw results table
    (DA / "tables").mkdir(parents=True, exist_ok=True)
    df_raw = pd.DataFrame(raw_results)
    df_raw.to_csv(DA / "tables/DA01_raw_seed_metrics.csv", index=False)

    print("\n[OK] All 5 seeds trained and evaluated successfully.")

if __name__ == "__main__":
    t0 = time.time()
    run_all_seeds()
    print(f"\n[+] Multi-seed execution finished in {time.time() - t0:.1f} seconds.")
