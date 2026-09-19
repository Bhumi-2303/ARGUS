#!/usr/bin/env python3
"""
ARGUS Project DA-02: Steps 5-10 — Controlled DANN Lambda Sweep Pilot (Seed 42).
Trains DANN models across lambda in [0.00, 0.10, 0.25, 0.50, 1.00] on Seed 42.
Monitors source classification loss, domain loss, domain accuracy, and target validation ROC-AUC / AP.
Performs model selection strictly on Target Validation Split (D3 calibration data).
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
    recall_score, f1_score, matthews_corrcoef, log_loss
)

BASE = Path(__file__).resolve().parent.parent.parent.parent
EE = BASE / "experiment_execution"
NR = EE / "neural_robustness"
DA01 = NR / "domain_adaptation"
DA02 = DA01 / "DA02_DANN"
CORAL_DATA_DIR = BASE / "ARGUS_Cross_Domain_Results/argus_coral_data"

sys.path.append(str(DA02 / "scripts"))
from dann_model import DANNNetwork

FEATURE_COLS = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
LAMBDA_LIST = [0.00, 0.10, 0.25, 0.50, 1.00]
BATCH_SIZE = 128
MAX_EPOCHS = 10
PATIENCE = 3
LR = 0.001
WEIGHT_DECAY = 0.0001
MAX_SAMPLES = 200000
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

def train_dann_lambda(
    X_s: np.ndarray,
    y_s: np.ndarray,
    X_t_adapt: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    lambda_val: float,
    seed: int = 42
):
    print(f"\n=========================================================================")
    print(f"RUNNING DA-02 PILOT: DANN (Seed {seed}, Lambda = {lambda_val:.2f}) on {DEVICE}")
    print(f"=========================================================================")

    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    gc.collect()

    # Subsample source and target adaptation data
    if len(X_s) > MAX_SAMPLES:
        _, X_s_sub, _, y_s_sub = train_test_split(
            X_s, y_s, test_size=MAX_SAMPLES, random_state=seed, stratify=y_s
        )
    else:
        X_s_sub, y_s_sub = X_s, y_s

    if len(X_t_adapt) > MAX_SAMPLES:
        rng = np.random.RandomState(seed)
        idx_t = rng.choice(len(X_t_adapt), MAX_SAMPLES, replace=False)
        X_t_sub = X_t_adapt[idx_t]
    else:
        X_t_sub = X_t_adapt

    # Scaling fit on source training data
    scaler = StandardScaler()
    X_s_scaled = scaler.fit_transform(X_s_sub).astype(np.float32)
    X_t_scaled = scaler.transform(X_t_sub).astype(np.float32)
    X_val_scaled = scaler.transform(X_val).astype(np.float32)

    # Tensor datasets & loaders
    s_dataset = TensorDataset(torch.tensor(X_s_scaled), torch.tensor(y_s_sub, dtype=torch.float32))
    t_dataset = TensorDataset(torch.tensor(X_t_scaled))
    val_dataset = TensorDataset(torch.tensor(X_val_scaled), torch.tensor(y_val, dtype=torch.float32))

    s_loader = DataLoader(s_dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
    t_loader = DataLoader(t_dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=4096, shuffle=False)

    model = DANNNetwork(input_dim=4, hidden_dim=64, latent_dim=32, dropout=0.10).to(DEVICE)

    criterion_class = nn.BCEWithLogitsLoss()
    criterion_domain = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    best_val_roc = -1.0
    best_val_loss = float("inf")
    best_epoch = 0
    patience_counter = 0

    ckpt_dir = DA02 / f"checkpoints/DA02_DANN_seed{seed}_lambda_{lambda_val:.2f}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt_path = ckpt_dir / "best_model.pt"
    final_ckpt_path = ckpt_dir / "final_model.pt"

    history = []
    n_batches = min(len(s_loader), len(t_loader))

    total_training_start = time.time()

    for epoch in range(1, MAX_EPOCHS + 1):
        epoch_start = time.time()
        model.train()

        loss_class_sum = 0.0
        loss_dom_sum = 0.0
        loss_total_sum = 0.0
        src_correct = 0
        dom_correct = 0
        total_samples = 0

        t_iter = iter(t_loader)

        for step, (bx_s, by_s) in enumerate(s_loader):
            if step >= n_batches:
                break
            try:
                (bx_t,) = next(t_iter)
            except StopIteration:
                t_iter = iter(t_loader)
                (bx_t,) = next(t_iter)

            bx_s, by_s = bx_s.to(DEVICE), by_s.to(DEVICE)
            bx_t = bx_t.to(DEVICE)

            # Standard DANN progressive alpha schedule (Ganin et al. 2016)
            p = float(step + (epoch - 1) * n_batches) / (MAX_EPOCHS * n_batches)
            alpha = float(2.0 / (1.0 + np.exp(-10 * p)) - 1.0)

            # Domain labels: Source D1 = 0, Target D3 = 1
            b_dom_s = torch.zeros(len(bx_s), device=DEVICE)
            b_dom_t = torch.ones(len(bx_t), device=DEVICE)

            # Forward passes
            out_class_s, out_dom_s, _ = model(bx_s, alpha=alpha)
            _, out_dom_t, _ = model(bx_t, alpha=alpha)

            err_class = criterion_class(out_class_s, by_s)
            err_dom_s = criterion_domain(out_dom_s, b_dom_s)
            err_dom_t = criterion_domain(out_dom_t, b_dom_t)
            err_domain = 0.5 * (err_dom_s + err_dom_t)

            err_total = err_class + lambda_val * err_domain

            optimizer.zero_grad()
            err_total.backward()
            optimizer.step()

            # Tracking batch metrics
            loss_class_sum += err_class.item() * len(by_s)
            loss_dom_sum += err_domain.item() * (len(bx_s) + len(bx_t))
            loss_total_sum += err_total.item() * len(by_s)

            pred_class_s = (torch.sigmoid(out_class_s) >= 0.5).float()
            src_correct += (pred_class_s == by_s).sum().item()

            pred_dom_s = (torch.sigmoid(out_dom_s) >= 0.5).float()
            pred_dom_t = (torch.sigmoid(out_dom_t) >= 0.5).float()
            dom_correct += (pred_dom_s == b_dom_s).sum().item() + (pred_dom_t == b_dom_t).sum().item()

            total_samples += len(by_s)

        train_class_loss = loss_class_sum / total_samples
        train_domain_loss = loss_dom_sum / (2 * total_samples)
        train_total_loss = loss_total_sum / total_samples
        src_accuracy = src_correct / total_samples
        dom_accuracy = dom_correct / (2 * total_samples)

        # Validation on D3 Target Calibration Split (Unseen during task training)
        model.eval()
        val_preds = []
        val_targets = []
        val_loss_sum = 0.0
        val_count = 0

        with torch.no_grad():
            for bx_v, by_v in val_loader:
                bx_v, by_v = bx_v.to(DEVICE), by_v.to(DEVICE)
                logits_v, _, _ = model(bx_v, alpha=0.0)
                loss_v = criterion_class(logits_v, by_v)
                val_loss_sum += loss_v.item() * len(by_v)
                val_count += len(by_v)
                probs = torch.sigmoid(logits_v).cpu().numpy()
                val_preds.extend(probs)
                val_targets.extend(by_v.cpu().numpy())

        val_class_loss = val_loss_sum / val_count
        val_preds = np.array(val_preds)
        val_targets = np.array(val_targets)

        val_roc = float(roc_auc_score(val_targets, val_preds))
        val_ap = float(average_precision_score(val_targets, val_preds))

        # Calibrate threshold on validation set
        best_th = 0.50
        best_f1 = -1.0
        for th in np.linspace(0.1, 0.9, 81):
            pred_v = (val_preds >= th).astype(int)
            tp = np.sum((val_targets == 1) & (pred_v == 1))
            fp = np.sum((val_targets == 0) & (pred_v == 1))
            fn = np.sum((val_targets == 1) & (pred_v == 0))
            f1_c = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
            if f1_c > best_f1:
                best_f1 = f1_c
                best_th = float(th)

        epoch_duration = time.time() - epoch_start

        epoch_record = {
            "epoch": epoch,
            "lambda": float(lambda_val),
            "train_classification_loss": float(train_class_loss),
            "domain_loss": float(train_domain_loss),
            "total_loss": float(train_total_loss),
            "source_accuracy": float(src_accuracy),
            "domain_accuracy": float(dom_accuracy),
            "target_validation_loss": float(val_class_loss),
            "target_validation_ROC_AUC": float(val_roc),
            "target_validation_AP": float(val_ap),
            "target_validation_F1": float(best_f1),
            "target_validation_best_threshold": float(best_th),
            "learning_rate": LR,
            "runtime_seconds": float(epoch_duration)
        }
        history.append(epoch_record)

        print(f"  Epoch {epoch:2d}/{MAX_EPOCHS:2d} | Tr Loss: {train_class_loss:.4f} | Dom Loss: {train_domain_loss:.4f} | Dom Acc: {dom_accuracy*100:.1f}% | Val ROC: {val_roc:.4f} | Val AP: {val_ap:.4f} | Val F1: {best_f1:.4f} ({epoch_duration:.1f}s)")

        # Early stopping and best model tracking based on Target Validation AP / ROC-AUC
        if val_roc > best_val_roc:
            best_val_roc = val_roc
            best_val_loss = val_class_loss
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), best_ckpt_path)
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"    Early stopping triggered at epoch {epoch} (Best epoch: {best_epoch}, Best Val ROC: {best_val_roc:.4f})")
                break

    # Save final model
    torch.save(model.state_dict(), final_ckpt_path)

    total_duration = time.time() - total_training_start

    # Save config
    config = {
        "model": "DANNNetwork",
        "lambda": lambda_val,
        "seed": seed,
        "parameters": model.count_parameters(),
        "batch_size": BATCH_SIZE,
        "epochs_trained": len(history),
        "best_epoch": best_epoch,
        "best_val_roc_auc": best_val_roc,
        "best_val_loss": best_val_loss,
        "total_runtime_seconds": total_duration,
        "scaler_fitted_on": "D1 Source Subset"
    }
    with open(ckpt_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)

    # Save training history for this lambda
    (DA02 / "logs").mkdir(parents=True, exist_ok=True)
    df_h = pd.DataFrame(history)
    df_h.to_csv(DA02 / f"logs/training_history_lambda_{lambda_val:.2f}.csv", index=False)

    return config, df_h, best_val_roc, best_val_loss, best_epoch


def run_lambda_sweep_pilot():
    print("=========================================================================")
    print("ARGUS DA-02: CONTROLLED DANN LAMBDA SWEEP PILOT (SEED 42)")
    print("=========================================================================")

    # 1. Load Datasets
    print("\n[1] Loading Source and Target Datasets...")
    d1_df = pd.read_csv(CORAL_DATA_DIR / "ciciot_train_features.csv")
    X_s = d1_df[FEATURE_COLS].values
    y_s = d1_df["label"].values.astype(int)
    del d1_df
    gc.collect()

    d3_adapt_df = pd.read_csv(CORAL_DATA_DIR / "iec104_train_adaptation.csv", usecols=FEATURE_COLS)
    X_t_adapt = d3_adapt_df.values
    del d3_adapt_df
    gc.collect()

    d3_calib_df = pd.read_csv(CORAL_DATA_DIR / "iec104_train_calibration.csv")
    X_val = d3_calib_df[FEATURE_COLS].values
    y_val = d3_calib_df["label"].values.astype(int)
    del d3_calib_df
    gc.collect()

    print(f"  Source D1 Samples:      {len(X_s):,}")
    print(f"  Target D3 Adapt Samples: {len(X_t_adapt):,} (Unlabeled)")
    print(f"  Target D3 Calib Samples: {len(X_val):,}")

    all_configs = []
    all_histories = []
    comparison_records = []

    for l_val in LAMBDA_LIST:
        cfg, df_h, b_roc, b_loss, b_ep = train_dann_lambda(
            X_s, y_s, X_t_adapt, X_val, y_val, l_val, seed=42
        )
        all_configs.append(cfg)
        all_histories.append(df_h)

        best_row = df_h[df_h["epoch"] == b_ep].iloc[0]
        comparison_records.append({
            "lambda": l_val,
            "best_epoch": int(b_ep),
            "target_validation_ROC_AUC": float(best_row["target_validation_ROC_AUC"]),
            "target_validation_AP": float(best_row["target_validation_AP"]),
            "target_validation_F1": float(best_row["target_validation_F1"]),
            "target_validation_loss": float(best_row["target_validation_loss"]),
            "final_domain_accuracy": float(df_h.iloc[-1]["domain_accuracy"]),
            "final_domain_loss": float(df_h.iloc[-1]["domain_loss"]),
            "train_classification_loss": float(best_row["train_classification_loss"]),
            "total_runtime_seconds": float(cfg["total_runtime_seconds"])
        })

    # Save Combined Training History
    (DA02 / "reports").mkdir(parents=True, exist_ok=True)
    df_all_hist = pd.concat(all_histories, ignore_index=True)
    df_all_hist.to_csv(DA02 / "reports/DA02_training_history.csv", index=False)
    print("\n[+] Saved reports/DA02_training_history.csv")

    # Save Lambda Comparison Table
    (DA02 / "tables").mkdir(parents=True, exist_ok=True)
    df_comp = pd.DataFrame(comparison_records)
    df_comp.to_csv(DA02 / "tables/DA02_lambda_validation_comparison.csv", index=False)
    print("[+] Saved tables/DA02_lambda_validation_comparison.csv")

    # Determine Best Lambda based exclusively on Target Validation Ranking Performance
    best_row = df_comp.sort_values(by="target_validation_ROC_AUC", ascending=False).iloc[0]
    best_lambda = float(best_row["lambda"])

    print("\n=========================================================================")
    print("PILOT LAMBDA SWEEP RESULTS (TARGET VALIDATION SPLIT ONLY)")
    print("=========================================================================")
    for _, r in df_comp.iterrows():
        print(f"  Lambda = {r['lambda']:4.2f} | Val ROC-AUC: {r['target_validation_ROC_AUC']:.4f} | Val AP: {r['target_validation_AP']:.4f} | Val F1: {r['target_validation_F1']:.4f} | Dom Acc: {r['final_domain_accuracy']*100:.1f}%")

    print(f"\n[SELECTED BEST LAMBDA]: lambda* = {best_lambda:.2f} (Target Val ROC-AUC: {best_row['target_validation_ROC_AUC']:.4f}, AP: {best_row['target_validation_AP']:.4f})")

    # Update manifest & state
    with open(DA02 / "DA02_manifest.json", "r") as f:
        manifest = json.load(f)
    manifest["selected_best_lambda"] = best_lambda
    manifest["status"] = "LAMBDA_SWEEP_COMPLETE_READY_FOR_FINAL_EVALUATION"
    with open(DA02 / "DA02_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    with open(DA02 / "experiment_state.json", "r") as f:
        state = json.load(f)
    state["current_stage"] = "STAGE_DA02_LAMBDA_SWEEP_COMPLETE"
    state["completed_lambdas"] = LAMBDA_LIST
    state["best_lambda"] = best_lambda
    state["checkpoint_path"] = f"experiment_execution/neural_robustness/domain_adaptation/DA02_DANN/checkpoints/DA02_DANN_seed42_lambda_{best_lambda:.2f}/best_model.pt"
    state["last_successful_artifact"] = "experiment_execution/neural_robustness/domain_adaptation/DA02_DANN/tables/DA02_lambda_validation_comparison.csv"
    state["status"] = "READY_FOR_FINAL_TEST_EVALUATION"
    state["timestamp"] = datetime.now().isoformat()
    with open(DA02 / "experiment_state.json", "w") as f:
        json.dump(state, f, indent=2)

    print("\n[OK] Lambda Sweep Pilot Complete.")

if __name__ == "__main__":
    t0 = time.time()
    run_lambda_sweep_pilot()
    print(f"\n[+] Lambda sweep finished in {time.time() - t0:.1f} seconds.")
