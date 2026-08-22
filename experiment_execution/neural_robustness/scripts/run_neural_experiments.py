#!/usr/bin/env python3
"""
ARGUS Neural Network Robustness Experiments (NR-01 & NR-02)
Executes FT-Transformer model family across ARGUS-4 and Native SCADA representations
across 5 random seeds [42, 123, 456, 789, 1011].
Optimized PyTorch MPS execution with fast validation evaluation.
"""

import os
import sys
import json
import time
import gc
import yaml
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_curve, roc_curve, auc, confusion_matrix

BASE = Path("/Users/tirthkosambia/Documents/ARGUS")
EE = BASE / "experiment_execution"
NR = EE / "neural_robustness"
CORAL_DIR = BASE / "ARGUS_Cross_Domain_Results/argus_coral_data"
RAW_DATA_DIR = BASE / "data/IEC104/extracted_csvs"

sys.path.append(str(EE / "scripts"))
from validate_metrics import compute_all_metrics

sys.path.append(str(NR / "scripts"))
from ft_transformer import FTTransformer

SEEDS = [42, 123, 456, 789, 1011]
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

# Load FT-Transformer YAML config
with open(NR / "configs/ft_transformer_config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

HP = CONFIG["hyperparameters"]
TR = CONFIG["training"]

MAX_EPOCHS = TR["max_epochs"]
PATIENCE = TR["patience"]
LR = TR["learning_rate"]
WEIGHT_DECAY = TR["weight_decay"]


def train_ft_transformer_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: np.ndarray,
    seed: int,
    exp_tag: str,
    batch_size: int = 16384,
    max_train_samples: int = 500000
):
    """
    Trains FT-Transformer with StandardScaler, AdamW optimizer, BCE loss,
    and Early Stopping based on validation loss. Saves best checkpoint.
    Fast validation evaluation (50k samples) during training, full test evaluation at end.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    gc.collect()

    # Subsample training data if larger than max_train_samples (stratified)
    if len(X_train) > max_train_samples:
        _, X_tr_sub, _, y_tr_sub = train_test_split(
            X_train, y_train, test_size=max_train_samples, random_state=seed, stratify=y_train
        )
    else:
        X_tr_sub, y_tr_sub = X_train, y_train

    # Fast validation subset (50k samples) for epoch loss & early stopping
    if len(X_val) > 50000:
        _, X_val_sub, _, y_val_sub = train_test_split(
            X_val, y_val, test_size=50000, random_state=seed, stratify=y_val
        )
    else:
        X_val_sub, y_val_sub = X_val, y_val

    # Scaling
    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_tr_sub)
    X_val_scaled = scaler.transform(X_val_sub)

    # Tensor datasets & dataloaders
    tr_ds = TensorDataset(torch.tensor(X_tr_scaled, dtype=torch.float32), torch.tensor(y_tr_sub, dtype=torch.float32))
    val_ds = TensorDataset(torch.tensor(X_val_scaled, dtype=torch.float32), torch.tensor(y_val_sub, dtype=torch.float32))

    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    n_features = X_train.shape[1]
    model = FTTransformer(
        n_features=n_features,
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

    ckpt_dir = NR / f"checkpoints/{exp_tag}_seed{seed}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt_path = ckpt_dir / "best_model.pt"

    history = []

    for epoch in range(1, MAX_EPOCHS + 1):
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

        # Validation
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
        val_auc = float(auc(*roc_curve(val_targets, val_preds)[:2]))

        history.append({
            "epoch": epoch,
            "train_loss": float(tr_loss),
            "val_loss": float(val_loss),
            "val_auc": float(val_auc),
            "lr": LR
        })

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
    pd.DataFrame(history).to_csv(NR / f"logs/training_history_{exp_tag}_seed{seed}.csv", index=False)

    # Load best checkpoint for full validation & test evaluation
    model.load_state_dict(torch.load(best_ckpt_path, map_location=DEVICE))
    model.eval()

    # Predict on Full Validation (for threshold selection)
    X_val_full_scaled = scaler.transform(X_val)
    val_full_ds = TensorDataset(torch.tensor(X_val_full_scaled, dtype=torch.float32))
    val_full_loader = DataLoader(val_full_ds, batch_size=batch_size, shuffle=False)

    val_probs = []
    with torch.no_grad():
        for (bx,) in val_full_loader:
            bx = bx.to(DEVICE)
            logits = model(bx)
            probs = torch.sigmoid(logits).cpu().numpy()
            val_probs.extend(probs)
    val_probs = np.array(val_probs)

    # Predict on Full Test
    X_te_scaled = scaler.transform(X_test)
    te_ds = TensorDataset(torch.tensor(X_te_scaled, dtype=torch.float32))
    te_loader = DataLoader(te_ds, batch_size=batch_size, shuffle=False)

    test_probs = []
    with torch.no_grad():
        for (bx,) in te_loader:
            bx = bx.to(DEVICE)
            logits = model(bx)
            probs = torch.sigmoid(logits).cpu().numpy()
            test_probs.extend(probs)
    test_probs = np.array(test_probs)

    return val_probs, test_probs, best_epoch, best_val_loss


def run_nr01_experiments():
    print("\n=========================================================================")
    print("RUNNING EXPERIMENT NR-01: FT-TRANSFORMER + ARGUS-4 TRANSFER (D1->D3, D2->D3)")
    print("=========================================================================")

    nr01_csv = NR / "metrics/NR01_FTTransformer_ARGUS4.csv"
    if nr01_csv.exists() and len(pd.read_csv(nr01_csv)) >= 20:
        print("  [NR-01] Results already computed! Loading from metrics/NR01_FTTransformer_ARGUS4.csv...")
        return

    # Load Target D3 Test Data (N = 714,453)
    df_d3_test = pd.read_csv(CORAL_DIR / "iec104_test_features.csv")
    X_d3_test = df_d3_test[["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]].values
    y_d3_test = df_d3_test["label"].values

    # Load Target D3 Calibration Data for validation (N = 571,563)
    df_d3_calib = pd.read_csv(CORAL_DIR / "iec104_train_calibration.csv")
    X_d3_calib = df_d3_calib[["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]].values
    y_d3_calib = df_d3_calib["label"].values

    # Load D1 Train Data (N = 5,491,971)
    df_d1_train = pd.read_csv(CORAL_DIR / "ciciot_train_features.csv")
    X_d1_train = df_d1_train[["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]].values
    y_d1_train = df_d1_train["label"].values

    # Load D2 Train Data (N = 10,508,704)
    df_d2_train = pd.read_csv(CORAL_DIR / "nfton_train_features.csv")
    X_d2_train = df_d2_train[["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]].values
    y_d2_train = df_d2_train["label"].values

    raw_results = []
    (NR / "predictions/NR01").mkdir(parents=True, exist_ok=True)

    # 1. D1 -> D3 Transfer
    for seed in SEEDS:
        print(f"\n  [NR-01] D1 -> D3 FT-Transformer + ARGUS-4 (seed={seed})...")
        v_prob, t_prob, b_ep, b_loss = train_ft_transformer_model(
            X_d1_train, y_d1_train, X_d3_calib, y_d3_calib, X_d3_test, seed, f"FTT_ARGUS4_D1_D3", batch_size=16384, max_train_samples=500000
        )

        if seed == 42:
            pd.DataFrame({"y_true": y_d3_test, "y_prob": t_prob}).to_csv(
                NR / "predictions/NR01/D1_D3_seed42_predictions.csv", index=False
            )

        # Default threshold 0.50
        m_def = compute_all_metrics(y_d3_test, t_prob, threshold=0.50)
        m_def.update({
            "experiment_id": "D1_D3_FTT_ARGUS4_RAW",
            "source_domain": "D1",
            "target_domain": "D3",
            "feature_set": "ARGUS-4",
            "model": "FT-Transformer D1 Source Baseline",
            "seed": seed,
            "best_epoch": b_ep,
            "best_val_loss": float(b_loss),
            "is_calibrated": False
        })
        raw_results.append(m_def)

        # Calibrated threshold on validation
        best_th = 0.50
        best_f1 = -1.0
        for th in np.linspace(0.1, 0.9, 81):
            p_val = (v_prob >= th).astype(int)
            tp = np.sum((y_d3_calib == 1) & (p_val == 1))
            fp = np.sum((y_d3_calib == 0) & (p_val == 1))
            fn = np.sum((y_d3_calib == 1) & (p_val == 0))
            f1_c = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
            if f1_c > best_f1:
                best_f1 = f1_c
                best_th = float(th)

        m_cal = compute_all_metrics(y_d3_test, t_prob, threshold=best_th)
        m_cal.update({
            "experiment_id": "D1_D3_FTT_ARGUS4_CALIB",
            "source_domain": "D1",
            "target_domain": "D3",
            "feature_set": "ARGUS-4",
            "model": f"FT-Transformer D1 Source Calibrated (θ={best_th:.2f})",
            "seed": seed,
            "best_epoch": b_ep,
            "best_val_loss": float(b_loss),
            "is_calibrated": True
        })
        raw_results.append(m_cal)

    # 2. D2 -> D3 Transfer
    for seed in SEEDS:
        print(f"\n  [NR-01] D2 -> D3 FT-Transformer + ARGUS-4 (seed={seed})...")
        v_prob, t_prob, b_ep, b_loss = train_ft_transformer_model(
            X_d2_train, y_d2_train, X_d3_calib, y_d3_calib, X_d3_test, seed, f"FTT_ARGUS4_D2_D3", batch_size=16384, max_train_samples=500000
        )

        if seed == 42:
            pd.DataFrame({"y_true": y_d3_test, "y_prob": t_prob}).to_csv(
                NR / "predictions/NR01/D2_D3_seed42_predictions.csv", index=False
            )

        m_def = compute_all_metrics(y_d3_test, t_prob, threshold=0.50)
        m_def.update({
            "experiment_id": "D2_D3_FTT_ARGUS4_RAW",
            "source_domain": "D2",
            "target_domain": "D3",
            "feature_set": "ARGUS-4",
            "model": "FT-Transformer D2 Source Baseline",
            "seed": seed,
            "best_epoch": b_ep,
            "best_val_loss": float(b_loss),
            "is_calibrated": False
        })
        raw_results.append(m_def)

        best_th = 0.50
        best_f1 = -1.0
        for th in np.linspace(0.01, 0.9, 90):
            p_val = (v_prob >= th).astype(int)
            tp = np.sum((y_d3_calib == 1) & (p_val == 1))
            fp = np.sum((y_d3_calib == 0) & (p_val == 1))
            fn = np.sum((y_d3_calib == 1) & (p_val == 0))
            f1_c = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
            if f1_c > best_f1:
                best_f1 = f1_c
                best_th = float(th)

        m_cal = compute_all_metrics(y_d3_test, t_prob, threshold=best_th)
        m_cal.update({
            "experiment_id": "D2_D3_FTT_ARGUS4_CALIB",
            "source_domain": "D2",
            "target_domain": "D3",
            "feature_set": "ARGUS-4",
            "model": f"FT-Transformer D2 Source Calibrated (θ={best_th:.2f})",
            "seed": seed,
            "best_epoch": b_ep,
            "best_val_loss": float(b_loss),
            "is_calibrated": True
        })
        raw_results.append(m_cal)

    df_raw = pd.DataFrame(raw_results)
    df_raw.to_csv(NR / "metrics/NR01_FTTransformer_ARGUS4.csv", index=False)

    # Multi-seed Summary
    metrics_to_agg = ["accuracy", "precision", "recall", "f1", "macro_f1", "fpr", "fnr", "mcc", "roc_auc", "pr_auc"]
    summary_rows = []
    for (exp_id, src, tgt, feat, model_name, is_cal), group in df_raw.groupby(["experiment_id", "source_domain", "target_domain", "feature_set", "model", "is_calibrated"]):
        row = {
            "experiment_id": exp_id,
            "source_domain": src,
            "target_domain": tgt,
            "feature_set": feat,
            "model": model_name,
            "is_calibrated": is_cal,
            "num_seeds": len(group),
            "threshold_mean": float(group["threshold"].mean())
        }
        for m in metrics_to_agg:
            row[f"{m}_mean"] = float(group[m].mean())
            row[f"{m}_std"] = float(group[m].std())
            row[f"{m}_formatted"] = f"{group[m].mean():.4f} ± {group[m].std():.4f}"
        summary_rows.append(row)

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(NR / "metrics/NR01_FTTransformer_ARGUS4_summary.csv", index=False)
    print("\n[OK] Experiment NR-01 completed successfully.")


def run_nr02_experiments():
    print("\n=========================================================================")
    print("RUNNING EXPERIMENT NR-02: FT-TRANSFORMER + NATIVE SCADA (Native-73)")
    print("=========================================================================")

    # Load Native-73 dataset using exact EXP-04 pipeline
    sys.path.append(str(EE / "scripts"))
    from run_exp04 import load_and_engineer_d3
    df_all, feature_cols = load_and_engineer_d3()

    X = df_all[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0).values
    y = df_all["label"].values

    from sklearn.model_selection import train_test_split
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=714453, random_state=42, stratify=y
    )
    X_train, X_calib, y_train, y_calib = train_test_split(
        X_train_full, y_train_full, test_size=571563, random_state=42, stratify=y_train_full
    )

    print(f"  Native Data: Train: {len(X_train):,} | Calib: {len(X_calib):,} | Test: {len(X_test):,}")

    raw_results = []
    (NR / "predictions/NR02").mkdir(parents=True, exist_ok=True)

    for seed in SEEDS:
        print(f"\n  [NR-02] Target In-Domain FT-Transformer + Native SCADA (seed={seed})...")
        v_prob, t_prob, b_ep, b_loss = train_ft_transformer_model(
            X_train, y_train, X_calib, y_calib, X_test, seed, f"FTT_Native", batch_size=4096, max_train_samples=100000
        )

        if seed == 42:
            pd.DataFrame({"y_true": y_test, "y_prob": t_prob}).to_csv(
                NR / "predictions/NR02/D3_native_seed42_predictions.csv", index=False
            )

        # Default threshold 0.50
        m_def = compute_all_metrics(y_test, t_prob, threshold=0.50)
        m_def.update({
            "experiment_id": "D3_NATIVE_FTT_TH05",
            "source_domain": "D3",
            "target_domain": "D3",
            "feature_set": "Native-73",
            "model": "Native SCADA FT-Transformer (73 Feat, θ=0.50)",
            "seed": seed,
            "best_epoch": b_ep,
            "best_val_loss": float(b_loss),
            "is_calibrated": False
        })
        raw_results.append(m_def)

        # Calibrated threshold on validation (MCC optimization)
        best_th_mcc = 0.50
        best_mcc = -1.0
        from sklearn.metrics import matthews_corrcoef
        for th in np.linspace(0.1, 0.9, 81):
            pred_c = (v_prob >= th).astype(int)
            m = matthews_corrcoef(y_calib, pred_c)
            if m > best_mcc:
                best_mcc = m
                best_th_mcc = float(th)

        m_cal = compute_all_metrics(y_test, t_prob, threshold=best_th_mcc)
        m_cal.update({
            "experiment_id": "D3_NATIVE_FTT_CALIB",
            "source_domain": "D3",
            "target_domain": "D3",
            "feature_set": "Native-73",
            "model": f"Native SCADA FT-Transformer (73 Feat, Calib θ={best_th_mcc:.2f})",
            "seed": seed,
            "best_epoch": b_ep,
            "best_val_loss": float(b_loss),
            "is_calibrated": True
        })
        raw_results.append(m_cal)

        # Low FPR Operating Point (θ = 0.78)
        m_low_fpr = compute_all_metrics(y_test, t_prob, threshold=0.78)
        m_low_fpr.update({
            "experiment_id": "D3_NATIVE_FTT_LOW_FPR",
            "source_domain": "D3",
            "target_domain": "D3",
            "feature_set": "Native-73",
            "model": "Native SCADA FT-Transformer (73 Feat, Operational θ=0.78)",
            "seed": seed,
            "best_epoch": b_ep,
            "best_val_loss": float(b_loss),
            "is_calibrated": True
        })
        raw_results.append(m_low_fpr)

    df_raw = pd.DataFrame(raw_results)
    df_raw.to_csv(NR / "metrics/NR02_FTTransformer_Native.csv", index=False)

    metrics_to_agg = ["accuracy", "precision", "recall", "f1", "macro_f1", "fpr", "fnr", "mcc", "roc_auc", "pr_auc"]
    summary_rows = []
    for (exp_id, src, tgt, feat, model_name, is_cal), group in df_raw.groupby(["experiment_id", "source_domain", "target_domain", "feature_set", "model", "is_calibrated"]):
        row = {
            "experiment_id": exp_id,
            "source_domain": src,
            "target_domain": tgt,
            "feature_set": feat,
            "model": model_name,
            "is_calibrated": is_cal,
            "num_seeds": len(group),
            "threshold_mean": float(group["threshold"].mean())
        }
        for m in metrics_to_agg:
            row[f"{m}_mean"] = float(group[m].mean())
            row[f"{m}_std"] = float(group[m].std())
            row[f"{m}_formatted"] = f"{group[m].mean():.4f} ± {group[m].std():.4f}"
        summary_rows.append(row)

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(NR / "metrics/NR02_FTTransformer_Native_summary.csv", index=False)
    print("\n[OK] Experiment NR-02 completed successfully.")


if __name__ == "__main__":
    t0 = time.time()
    run_nr01_experiments()
    run_nr02_experiments()
    print(f"\n[+] All Neural Robustness Experiments finished in {time.time() - t0:.1f} seconds.")
