#!/usr/bin/env python3
"""
ARGUS Neural Robustness — CAPACITY-01 Experiment Runner
Evaluates FTT-LARGE (Substantially Higher Capacity FT-Transformer) on D1 -> D3 ARGUS-4.
Strictly controlled comparison against baseline FTT-SMALL (Seed 42).
"""

import os
import sys
import json
import time
import gc
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path

# Configure Matplotlib for headless 300 DPI rendering
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_capacity"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_curve,
    precision_recall_curve,
    auc,
    roc_auc_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    accuracy_score,
    precision_score,
    recall_score,
    log_loss,
    brier_score_loss
)

import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
BASE = _curr
EE = BASE / "experiment_execution"
NR = EE / "neural_robustness"
CAP = NR / "capacity_test"
CORAL_DIR = BASE / "ARGUS_Cross_Domain_Results/argus_coral_data"

sys.path.append(str(EE / "scripts"))
from validate_metrics import compute_all_metrics

sys.path.append(str(NR / "scripts"))
from ft_transformer import FTTransformer

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

def run_capacity01():
    print("=" * 80)
    print("ARGUS NEURAL CAPACITY STRESS TEST — EXPERIMENT CAPACITY-01 (FTT-LARGE)")
    print("=" * 80)

    t_start = time.time()
    
    # 1. Load Configuration
    with open(CAP / "configs/CAPACITY01_config.json", "r") as f:
        config = json.load(f)
        
    hp = config["hyperparameters"]
    tr = config["training"]
    seed = config["experiment"]["seed"]

    # 2. Instantiate FTT-LARGE Model & Calculate Parameters
    n_features = len(config["experiment"]["features"])
    model = FTTransformer(
        n_features=n_features,
        d_token=hp["d_token"],
        n_blocks=hp["n_blocks"],
        n_heads=hp["n_heads"],
        d_ff=hp["d_ff"],
        dropout=hp["dropout"]
    ).to(DEVICE)
    
    large_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    small_params = 17473
    param_ratio = large_params / small_params
    
    print(f"\n[1/7] Architecture Configuration:")
    print(f"  - Baseline FTT-SMALL Parameters: {small_params:,}")
    print(f"  - Target FTT-LARGE Parameters  : {large_params:,}")
    print(f"  - Capacity Increase Factor     : {param_ratio:.2f}x")
    print(f"  - Target Compute Device        : {DEVICE}")

    # 3. Load Frozen Dataset Partitions
    print(f"\n[2/7] Loading Frozen Dataset Partitions...")
    feat_cols = config["experiment"]["features"]
    
    # Source D1 Train Data (N = 5,491,971)
    df_d1_train = pd.read_csv(CORAL_DIR / "ciciot_train_features.csv")
    X_d1_train = df_d1_train[feat_cols].values
    y_d1_train = df_d1_train["label"].values.astype(np.float32)

    # Target D3 Calibration Partition (Validation split, N = 571,563)
    df_d3_calib = pd.read_csv(CORAL_DIR / "iec104_train_calibration.csv")
    X_d3_calib = df_d3_calib[feat_cols].values
    y_d3_calib = df_d3_calib["label"].values.astype(np.float32)

    # Target D3 Test Partition (Frozen Test split, N = 714,453)
    df_d3_test = pd.read_csv(CORAL_DIR / "iec104_test_features.csv")
    X_d3_test = df_d3_test[feat_cols].values
    y_d3_test = df_d3_test["label"].values.astype(np.float32)

    print(f"  - D1 Train Shape : {X_d1_train.shape}")
    print(f"  - D3 Calib Shape : {X_d3_calib.shape}")
    print(f"  - D3 Test Shape  : {X_d3_test.shape} (Attack Prior pi = {np.mean(y_d3_test):.4f})")

    # 4. Data Subsampling & Preprocessing
    max_train_samples = tr["max_train_samples"]
    if len(X_d1_train) > max_train_samples:
        _, X_tr_sub, _, y_tr_sub = train_test_split(
            X_d1_train, y_d1_train, test_size=max_train_samples, random_state=seed, stratify=y_d1_train
        )
    else:
        X_tr_sub, y_tr_sub = X_d1_train, y_d1_train

    if len(X_d3_calib) > 50000:
        _, X_val_sub, _, y_val_sub = train_test_split(
            X_d3_calib, y_d3_calib, test_size=50000, random_state=seed, stratify=y_d3_calib
        )
    else:
        X_val_sub, y_val_sub = X_d3_calib, y_d3_calib

    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_tr_sub)
    X_val_scaled = scaler.transform(X_val_sub)

    batch_size = tr["batch_size"]
    tr_ds = TensorDataset(torch.tensor(X_tr_scaled, dtype=torch.float32), torch.tensor(y_tr_sub, dtype=torch.float32))
    val_ds = TensorDataset(torch.tensor(X_val_scaled, dtype=torch.float32), torch.tensor(y_val_sub, dtype=torch.float32))

    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    # 5. Training Loop with Checkpointing & Early Stopping
    print(f"\n[3/7] Training FTT-LARGE (Seed={seed})...")
    torch.manual_seed(seed)
    np.random.seed(seed)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=tr["learning_rate"], weight_decay=tr["weight_decay"])

    best_val_loss = float("inf")
    best_epoch = 0
    patience_counter = 0

    ckpt_dir = CAP / f"checkpoints/CAPACITY01_seed{seed}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt_path = ckpt_dir / "best_model.pt"
    latest_ckpt_path = ckpt_dir / "latest_model.pt"

    history = []
    max_epochs = tr["max_epochs"]
    patience = tr["patience"]

    for epoch in range(1, max_epochs + 1):
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

        print(f"  Epoch {epoch:02d}/{max_epochs:02d} | Train Loss: {tr_loss:.5f} | Val Loss: {val_loss:.5f} | Val AUC: {val_auc:.5f}")

        hist_entry = {
            "epoch": epoch,
            "train_loss": float(tr_loss),
            "val_loss": float(val_loss),
            "val_auc": float(val_auc),
            "lr": tr["learning_rate"]
        }
        history.append(hist_entry)

        # Save latest checkpoint
        checkpoint_dict = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "val_loss": val_loss,
            "val_auc": val_auc,
            "config": config,
            "seed": seed
        }
        torch.save(checkpoint_dict, latest_ckpt_path)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch
            patience_counter = 0
            torch.save(checkpoint_dict, best_ckpt_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"    Early stopping triggered at epoch {epoch} (Best Epoch: {best_epoch}, Best Val Loss: {best_val_loss:.5f})")
                break

    # Save training history
    df_hist = pd.DataFrame(history)
    df_hist.to_csv(CAP / f"training_logs/CAPACITY01_seed{seed}_history.csv", index=False)
    df_hist.to_csv(CAP / "figures/CAPACITY01_training_history.csv", index=False)

    # 6. Load Best Checkpoint & Perform Batched Inference
    print(f"\n[4/7] Performing Batched Test Inference on D3 Test Set (N={len(X_d3_test):,})...")
    ckpt_saved = torch.load(best_ckpt_path, map_location=DEVICE)
    model.load_state_dict(ckpt_saved["model_state_dict"])
    model.eval()

    # Full Validation Inference for Threshold Calibration
    X_val_full_scaled = scaler.transform(X_d3_calib)
    val_full_ds = TensorDataset(torch.tensor(X_val_full_scaled, dtype=torch.float32))
    val_full_loader = DataLoader(val_full_ds, batch_size=batch_size, shuffle=False)

    val_probs = []
    with torch.no_grad():
        for (bx,) in val_full_loader:
            bx = bx.to(DEVICE)
            probs = torch.sigmoid(model(bx)).cpu().numpy()
            val_probs.extend(probs)
    val_probs = np.array(val_probs)

    # Find Calibrated Threshold on D3 Calibration Set (maximizing F1)
    best_th = 0.50
    best_f1_val = -1.0
    th_grid = np.linspace(0.01, 0.99, 99)
    operating_curve_data = []
    
    for th in th_grid:
        p_val = (val_probs >= th).astype(int)
        tp = np.sum((y_d3_calib == 1) & (p_val == 1))
        fp = np.sum((y_d3_calib == 0) & (p_val == 1))
        fn = np.sum((y_d3_calib == 1) & (p_val == 0))
        tn = np.sum((y_d3_calib == 0) & (p_val == 0))
        
        f1_c = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        operating_curve_data.append({
            "threshold": float(th),
            "val_f1": float(f1_c),
            "val_fpr": float(fp / (fp + tn)),
            "val_fnr": float(fn / (fn + tp))
        })
        if f1_c > best_f1_val:
            best_f1_val = f1_c
            best_th = float(th)

    pd.DataFrame(operating_curve_data).to_csv(CAP / "figures/CAPACITY01_operating_curve.csv", index=False)
    print(f"  - Target Calibration Partition Optimal Threshold: theta = {best_th:.4f} (Val F1 = {best_f1_val:.4f})")

    # Full Test Partition Inference
    X_te_scaled = scaler.transform(X_d3_test)
    te_ds = TensorDataset(torch.tensor(X_te_scaled, dtype=torch.float32))
    te_loader = DataLoader(te_ds, batch_size=batch_size, shuffle=False)

    test_probs = []
    with torch.no_grad():
        for (bx,) in te_loader:
            bx = bx.to(DEVICE)
            probs = torch.sigmoid(model(bx)).cpu().numpy()
            test_probs.extend(probs)
    test_probs = np.array(test_probs)

    # Save Test Predictions
    df_preds = pd.DataFrame({
        "sample_id": np.arange(len(y_d3_test)),
        "true_label": y_d3_test.astype(int),
        "predicted_probability": test_probs,
        "predicted_label_default": (test_probs >= 0.50).astype(int),
        "predicted_label_calibrated": (test_probs >= best_th).astype(int),
        "default_threshold": 0.50,
        "calibrated_threshold": best_th,
        "seed": seed
    })
    df_preds.to_csv(CAP / "predictions/CAPACITY01_seed42_predictions.csv", index=False)
    print(f"  -> Saved predictions/CAPACITY01_seed42_predictions.csv ({len(df_preds):,} rows)")

    # 7. Metrics & Confusion Matrix Serialization
    print(f"\n[5/7] Calculating Evaluation Metrics & Confusion Matrices...")
    
    # Default Threshold Metrics
    m_def = compute_all_metrics(y_d3_test, test_probs, threshold=0.50)
    m_def.update({
        "experiment_id": "CAPACITY01_RAW",
        "model_architecture": "FT-Transformer Large (FTT-LARGE)",
        "trainable_parameters": large_params,
        "seed": seed,
        "threshold": 0.50,
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss),
        "is_calibrated": False
    })
    
    # Calibrated Threshold Metrics
    m_cal = compute_all_metrics(y_d3_test, test_probs, threshold=best_th)
    m_cal.update({
        "experiment_id": "CAPACITY01_CALIB",
        "model_architecture": "FT-Transformer Large (FTT-LARGE)",
        "trainable_parameters": large_params,
        "seed": seed,
        "threshold": float(best_th),
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss),
        "is_calibrated": True
    })

    df_metrics = pd.DataFrame([m_def, m_cal])
    df_metrics.to_csv(CAP / "metrics/CAPACITY01_seed42.csv", index=False)

    # Save Confusion Matrices
    cm_def = confusion_matrix(y_d3_test, (test_probs >= 0.50).astype(int))
    cm_cal = confusion_matrix(y_d3_test, (test_probs >= best_th).astype(int))
    
    pd.DataFrame(cm_def, index=["True_0", "True_1"], columns=["Pred_0", "Pred_1"]).to_csv(
        CAP / "metrics/CAPACITY01_confusion_matrix_default.csv"
    )
    pd.DataFrame(cm_cal, index=["True_0", "True_1"], columns=["Pred_0", "Pred_1"]).to_csv(
        CAP / "metrics/CAPACITY01_confusion_matrix_calibrated.csv"
    )

    # 8. Primary Comparison Table: FTT-SMALL vs FTT-LARGE
    print(f"\n[6/7] Generating Primary Comparison Table (FTT-SMALL vs FTT-LARGE)...")
    
    # Load FTT-SMALL Seed 42 baseline metrics from N1
    df_n1_raw = pd.read_csv(NR / "metrics/NR01_FTTransformer_ARGUS4.csv")
    small_def = df_n1_raw[(df_n1_raw["experiment_id"] == "D1_D3_FTT_ARGUS4_RAW") & (df_n1_raw["seed"] == 42)].iloc[0]
    small_cal = df_n1_raw[(df_n1_raw["experiment_id"] == "D1_D3_FTT_ARGUS4_CALIB") & (df_n1_raw["seed"] == 42)].iloc[0]

    comp_rows = [
        {
            "Model": "FTT-SMALL (Baseline)",
            "Parameters": small_params,
            "Seed": 42,
            "ROC_AUC": float(small_def["roc_auc"]),
            "PR_AUC": float(small_def["pr_auc"]),
            "F1_Default": float(small_def["f1"]),
            "F1_Calibrated": float(small_cal["f1"]),
            "MCC_Default": float(small_def["mcc"]),
            "MCC_Calibrated": float(small_cal["mcc"]),
            "FPR_Default": float(small_def["fpr"]),
            "FPR_Calibrated": float(small_cal["fpr"]),
            "FNR_Default": float(small_def["fnr"]),
            "FNR_Calibrated": float(small_cal["fnr"]),
            "Accuracy_Calibrated": float(small_cal["accuracy"])
        },
        {
            "Model": "FTT-LARGE (Capacity Test)",
            "Parameters": large_params,
            "Seed": 42,
            "ROC_AUC": float(m_def["roc_auc"]),
            "PR_AUC": float(m_def["pr_auc"]),
            "F1_Default": float(m_def["f1"]),
            "F1_Calibrated": float(m_cal["f1"]),
            "MCC_Default": float(m_def["mcc"]),
            "MCC_Calibrated": float(m_cal["mcc"]),
            "FPR_Default": float(m_def["fpr"]),
            "FPR_Calibrated": float(m_cal["fpr"]),
            "FNR_Default": float(m_def["fnr"]),
            "FNR_Calibrated": float(m_cal["fnr"]),
            "Accuracy_Calibrated": float(m_cal["accuracy"])
        },
        {
            "Model": "Absolute Difference (LARGE - SMALL)",
            "Parameters": large_params - small_params,
            "Seed": 42,
            "ROC_AUC": float(m_def["roc_auc"] - small_def["roc_auc"]),
            "PR_AUC": float(m_def["pr_auc"] - small_def["pr_auc"]),
            "F1_Default": float(m_def["f1"] - small_def["f1"]),
            "F1_Calibrated": float(m_cal["f1"] - small_cal["f1"]),
            "MCC_Default": float(m_def["mcc"] - small_def["mcc"]),
            "MCC_Calibrated": float(m_cal["mcc"] - small_cal["mcc"]),
            "FPR_Default": float(m_def["fpr"] - small_def["fpr"]),
            "FPR_Calibrated": float(m_cal["fpr"] - small_cal["fpr"]),
            "FNR_Default": float(m_def["fnr"] - small_def["fnr"]),
            "FNR_Calibrated": float(m_cal["fnr"] - small_cal["fnr"]),
            "Accuracy_Calibrated": float(m_cal["accuracy"] - small_cal["accuracy"])
        },
        {
            "Model": "Relative Change ((LARGE - SMALL) / SMALL)",
            "Parameters": f"+{(param_ratio - 1)*100:.1f}%",
            "Seed": 42,
            "ROC_AUC": f"{(m_def['roc_auc'] - small_def['roc_auc'])/small_def['roc_auc']*100:+.2f}%",
            "PR_AUC": f"{(m_def['pr_auc'] - small_def['pr_auc'])/small_def['pr_auc']*100:+.2f}%",
            "F1_Default": f"{(m_def['f1'] - small_def['f1'])/small_def['f1']*100:+.2f}%",
            "F1_Calibrated": f"{(m_cal['f1'] - small_cal['f1'])/small_cal['f1']*100:+.2f}%",
            "MCC_Default": f"{(m_def['mcc'] - small_def['mcc']):+.4f}",
            "MCC_Calibrated": f"{(m_cal['mcc'] - small_cal['mcc'])/small_cal['mcc']*100:+.2f}%",
            "FPR_Default": f"{(m_def['fpr'] - small_def['fpr']):+.4f}",
            "FPR_Calibrated": f"{(m_cal['fpr'] - small_cal['fpr'])/small_cal['fpr']*100:+.2f}%",
            "FNR_Default": f"{(m_def['fnr'] - small_def['fnr']):+.4f}",
            "FNR_Calibrated": f"{(m_cal['fnr'] - small_cal['fnr']):+.4f}",
            "Accuracy_Calibrated": f"{(m_cal['accuracy'] - small_cal['accuracy'])/small_cal['accuracy']*100:+.2f}%"
        }
    ]

    df_comp = pd.DataFrame(comp_rows)
    df_comp.to_csv(CAP / "metrics/CAPACITY01_SMALL_vs_LARGE.csv", index=False)

    # 9. Plot Publication-Ready Figures (300 DPI)
    print(f"\n[7/7] Generating 300 DPI Publication Figures...")
    
    # 9.1 ROC Curve for FTT-LARGE
    fpr_l, tpr_l, th_l = roc_curve(y_d3_test, test_probs)
    roc_auc_large = auc(fpr_l, tpr_l)
    pd.DataFrame({"fpr": fpr_l, "tpr": tpr_l, "threshold": np.append(th_l[:-1], th_l[-1])}).to_csv(
        CAP / "figures/CAPACITY01_ROC.csv", index=False
    )
    
    plt.figure(figsize=(7, 6), dpi=300)
    plt.plot(fpr_l, tpr_l, color="#9467bd", lw=2.5, label=f"FTT-LARGE (Seed 42, AUC = {roc_auc_large:.4f})")
    plt.plot([0, 1], [0, 1], color="#7f7f7f", linestyle="--", lw=1.5, label="Random Guess (AUC = 0.5000)")
    plt.xlabel("False Positive Rate (FPR)", fontsize=12, fontweight="bold")
    plt.ylabel("True Positive Rate / Recall (TPR)", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01: ROC Curve — FTT-LARGE ARGUS-4 (D1 → D3)\nModel Capacity: 200,705 Parameters (N=714,453)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=11)
    plt.tight_layout()
    plt.savefig(CAP / "figures/CAPACITY01_ROC.png", dpi=300)
    plt.close()

    # 9.2 PR Curve for FTT-LARGE
    prec_l, rec_l, pr_th_l = precision_recall_curve(y_d3_test, test_probs)
    pr_auc_large = auc(rec_l, prec_l)
    pd.DataFrame({"precision": prec_l[:-1], "recall": rec_l[:-1], "threshold": pr_th_l}).to_csv(
        CAP / "figures/CAPACITY01_PR.csv", index=False
    )
    
    no_skill = np.mean(y_d3_test)
    plt.figure(figsize=(7, 6), dpi=300)
    plt.plot(rec_l, prec_l, color="#8c564b", lw=2.5, label=f"FTT-LARGE (Seed 42, AUC = {pr_auc_large:.4f})")
    plt.axhline(y=no_skill, color="#7f7f7f", linestyle="--", lw=1.5, label=f"Target Attack Prior ($\pi$ = {no_skill:.4f})")
    plt.xlabel("Recall", fontsize=12, fontweight="bold")
    plt.ylabel("Precision", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01: Precision-Recall Curve — FTT-LARGE (D1 → D3)\nModel Capacity: 200,705 Parameters (N=714,453)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=11)
    plt.tight_layout()
    plt.savefig(CAP / "figures/CAPACITY01_PR.png", dpi=300)
    plt.close()

    # 9.3 Confusion Matrix Figure
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    sns.heatmap(cm_def, annot=True, fmt="d", cmap="Purples", cbar=False, ax=axes[0],
                xticklabels=["Normal (0)", "Attack (1)"], yticklabels=["Normal (0)", "Attack (1)"])
    axes[0].set_title(f"Default Threshold ($\Theta = 0.50$)\nFPR={m_def['fpr']*100:.2f}%, FNR={m_def['fnr']*100:.2f}%, F1={m_def['f1']:.4f}", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Predicted Class", fontsize=11)
    axes[0].set_ylabel("True Class", fontsize=11)

    sns.heatmap(cm_cal, annot=True, fmt="d", cmap="Oranges", cbar=False, ax=axes[1],
                xticklabels=["Normal (0)", "Attack (1)"], yticklabels=["Normal (0)", "Attack (1)"])
    axes[1].set_title(f"Calibrated Threshold ($\Theta = {best_th:.2f}$)\nFPR={m_cal['fpr']*100:.2f}%, FNR={m_cal['fnr']*100:.2f}%, F1={m_cal['f1']:.4f}", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Predicted Class", fontsize=11)
    axes[1].set_ylabel("True Class", fontsize=11)

    fig.suptitle("CAPACITY-01: Confusion Matrices — FTT-LARGE ARGUS-4 (D1 → D3 Seed 42)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CAP / "figures/CAPACITY01_confusion_matrix.png", dpi=300)
    plt.close()

    # 9.4 Training Curve
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(df_hist["epoch"], df_hist["train_loss"], linestyle="--", color="#9467bd", marker="s", lw=2, label="FTT-LARGE Train Loss")
    plt.plot(df_hist["epoch"], df_hist["val_loss"], linestyle="-", color="#d62728", marker="o", lw=2, label="FTT-LARGE Val Loss")
    plt.xlabel("Epoch", fontsize=12, fontweight="bold")
    plt.ylabel("BCE Loss", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01: Training & Validation Loss — FTT-LARGE (200,705 Params)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=11)
    plt.tight_layout()
    plt.savefig(CAP / "figures/CAPACITY01_training_curve.png", dpi=300)
    plt.close()

    # 9.5 Operating Curve (Validation F1 vs Threshold)
    df_op = pd.DataFrame(operating_curve_data)
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(df_op["threshold"], df_op["val_f1"], color="#2ca02c", lw=2.5, label="Validation F1")
    plt.axvline(x=best_th, color="#d62728", linestyle="--", lw=1.5, label=f"Optimal Calibration ($\Theta$ = {best_th:.2f})")
    plt.xlabel("Decision Threshold ($\Theta$)", fontsize=12, fontweight="bold")
    plt.ylabel("Target Validation F1", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01: Operating Threshold Calibration Curve", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=11)
    plt.tight_layout()
    plt.savefig(CAP / "figures/CAPACITY01_operating_curve.png", dpi=300)
    plt.close()

    # 9.6 PRIMARY COMPARISON FIGURE: FTT-SMALL vs FTT-LARGE
    print("  -> Generating Primary Comparison Figure: CAPACITY01_SMALL_vs_LARGE.png...")
    # Load FTT-SMALL Seed 42 test predictions from N1
    pred_small_file = NR / "predictions/NR01/D1_D3_seed42_predictions.csv"
    df_small_p = pd.read_csv(pred_small_file)
    y_small_true = df_small_p["y_true"].values
    y_small_prob = df_small_p["y_prob"].values
    
    fpr_s, tpr_s, _ = roc_curve(y_small_true, y_small_prob)
    roc_auc_small = auc(fpr_s, tpr_s)
    
    prec_s, rec_s, _ = precision_recall_curve(y_small_true, y_small_prob)
    pr_auc_small = auc(rec_s, prec_s)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    # ROC Overlay
    axes[0].plot(fpr_s, tpr_s, color="#1f77b4", lw=2.5, label=f"FTT-SMALL (17,473 params, AUC = {roc_auc_small:.4f})")
    axes[0].plot(fpr_l, tpr_l, color="#9467bd", lw=2.5, label=f"FTT-LARGE (200,705 params, AUC = {roc_auc_large:.4f})")
    axes[0].plot([0, 1], [0, 1], color="#7f7f7f", linestyle="--", lw=1.5, label="Random Guess (AUC = 0.5000)")
    axes[0].set_xlabel("False Positive Rate (FPR)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("True Positive Rate / Recall (TPR)", fontsize=11, fontweight="bold")
    axes[0].set_title("A. ROC Curve Comparison (D1 → D3 Seed 42)", fontsize=12, fontweight="bold")
    axes[0].grid(True, linestyle=":", alpha=0.6)
    axes[0].legend(loc="lower right", fontsize=10)

    # PR Overlay
    axes[1].plot(rec_s, prec_s, color="#1f77b4", lw=2.5, label=f"FTT-SMALL (17,473 params, AUC = {pr_auc_small:.4f})")
    axes[1].plot(rec_l, prec_l, color="#9467bd", lw=2.5, label=f"FTT-LARGE (200,705 params, AUC = {pr_auc_large:.4f})")
    axes[1].axhline(y=no_skill, color="#7f7f7f", linestyle="--", lw=1.5, label=f"Target Prior ($\pi$ = {no_skill:.4f})")
    axes[1].set_xlabel("Recall", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Precision", fontsize=11, fontweight="bold")
    axes[1].set_title("B. Precision-Recall Curve Comparison (D1 → D3 Seed 42)", fontsize=12, fontweight="bold")
    axes[1].grid(True, linestyle=":", alpha=0.6)
    axes[1].legend(loc="upper right", fontsize=10)

    fig.suptitle("ARGUS Neural Capacity Stress Test: FTT-SMALL (17.5k Params) vs FTT-LARGE (200.7k Params)\nControlled Comparison on D1 → D3 ARGUS-4 Task (11.5x Capacity Increase)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CAP / "figures/CAPACITY01_SMALL_vs_LARGE.png", dpi=300)
    plt.close()

    elapsed = time.time() - t_start
    print(f"\n[+] CAPACITY-01 completed successfully in {elapsed:.2f} seconds.")
    return {
        "large_params": large_params,
        "small_params": small_params,
        "param_ratio": param_ratio,
        "m_def": m_def,
        "m_cal": m_cal,
        "small_def": small_def,
        "small_cal": small_cal,
        "elapsed": elapsed
    }

if __name__ == "__main__":
    res = run_capacity01()
