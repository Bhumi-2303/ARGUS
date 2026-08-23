#!/usr/bin/env python3
"""
ARGUS Neural Robustness — CAPACITY-01R Regularization Stress Test Script
Trains FTT-LARGE-REG (Dropout = 0.30, Weight Decay = 0.01) on D1 -> D3 ARGUS-4.
Generates metrics, confusion matrices, ROC/PR figures, loss comparison overlays,
overfitting analysis, and diagnostic interpretation report.
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
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_reg"
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

BASE = Path("/Users/tirthkosambia/Documents/ARGUS")
EE = BASE / "experiment_execution"
NR = EE / "neural_robustness"
CAP = NR / "capacity_test"
REG = CAP / "regularization"
CORAL_DIR = BASE / "ARGUS_Cross_Domain_Results/argus_coral_data"

sys.path.append(str(EE / "scripts"))
from validate_metrics import compute_all_metrics

sys.path.append(str(NR / "scripts"))
from ft_transformer import FTTransformer

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

def run_regularization():
    print("=" * 80)
    print("ARGUS NEURAL CAPACITY STRESS TEST — EXPERIMENT CAPACITY-01R (FTT-LARGE-REG)")
    print("=" * 80)

    t_start = time.time()
    
    # 1. Load Configuration
    with open(REG / "configs/FTT_LARGE_REG_seed42.json", "r") as f:
        config = json.load(f)
        
    hp = config["hyperparameters"]
    tr = config["training"]
    seed = config["experiment"]["seed"]

    # 2. Instantiate FTT-LARGE-REG Model & Calculate Parameters
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
    
    print(f"\n[1/8] Model Specification:")
    print(f"  - Model Architecture: FTT-LARGE-REG")
    print(f"  - Parameters        : {large_params:,}")
    print(f"  - Dropout           : {hp['dropout']}")
    print(f"  - Weight Decay      : {tr['weight_decay']}")
    print(f"  - Compute Device    : {DEVICE}")

    # 3. Load Frozen Dataset Partitions
    print(f"\n[2/8] Loading Frozen Dataset Partitions...")
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
    print(f"\n[3/8] Training FTT-LARGE-REG (Seed={seed})...")
    torch.manual_seed(seed)
    np.random.seed(seed)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=tr["learning_rate"], weight_decay=tr["weight_decay"])

    best_val_loss = float("inf")
    best_epoch = 0
    patience_counter = 0

    ckpt_dir = REG / f"checkpoints/FTT_LARGE_REG_seed{seed}"
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
    df_hist.to_csv(REG / f"training_logs/FTT_LARGE_REG_seed{seed}_history.csv", index=False)
    df_hist.to_csv(REG / "figures/FTT_LARGE_REG_training_history.csv", index=False)

    # 6. Load Best Checkpoint & Perform Batched Inference
    print(f"\n[4/8] Performing Batched Test Inference on D3 Test Set (N={len(X_d3_test):,})...")
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

    # Threshold Calibration on Validation Split
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

    pd.DataFrame(operating_curve_data).to_csv(REG / "figures/FTT_LARGE_REG_operating_curve.csv", index=False)
    pd.DataFrame(operating_curve_data).to_csv(REG / "figures/FTT_LARGE_REG_calibration.csv", index=False)

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
        "default_prediction": (test_probs >= 0.50).astype(int),
        "calibrated_prediction": (test_probs >= best_th).astype(int),
        "default_threshold": 0.50,
        "calibrated_threshold": best_th,
        "seed": seed
    })
    df_preds.to_csv(REG / "predictions/FTT_LARGE_REG_seed42_predictions.csv", index=False)
    print(f"  -> Saved predictions/FTT_LARGE_REG_seed42_predictions.csv ({len(df_preds):,} rows)")

    # 7. Metrics & Confusion Matrix Serialization
    print(f"\n[5/8] Calculating Evaluation Metrics...")
    
    # Default Threshold Metrics
    m_def = compute_all_metrics(y_d3_test, test_probs, threshold=0.50)
    m_def.update({
        "experiment_id": "FTT_LARGE_REG_RAW",
        "model_architecture": "FT-Transformer Large Regularized (FTT-LARGE-REG)",
        "trainable_parameters": large_params,
        "dropout": hp["dropout"],
        "weight_decay": tr["weight_decay"],
        "seed": seed,
        "threshold": 0.50,
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss),
        "is_calibrated": False
    })
    
    # Calibrated Threshold Metrics
    m_cal = compute_all_metrics(y_d3_test, test_probs, threshold=best_th)
    m_cal.update({
        "experiment_id": "FTT_LARGE_REG_CALIB",
        "model_architecture": "FT-Transformer Large Regularized (FTT-LARGE-REG)",
        "trainable_parameters": large_params,
        "dropout": hp["dropout"],
        "weight_decay": tr["weight_decay"],
        "seed": seed,
        "threshold": float(best_th),
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss),
        "is_calibrated": True
    })

    df_metrics = pd.DataFrame([m_def, m_cal])
    df_metrics.to_csv(REG / "metrics/FTT_LARGE_REG_seed42.csv", index=False)

    # 8. Primary Comparison Tables & Overfitting Analysis
    print(f"\n[6/8] Generating Primary Comparison Tables & Overfitting Analysis...")
    
    # Load FTT-SMALL Seed 42 baseline metrics from N1
    df_n1_raw = pd.read_csv(NR / "metrics/NR01_FTTransformer_ARGUS4.csv")
    small_def = df_n1_raw[(df_n1_raw["experiment_id"] == "D1_D3_FTT_ARGUS4_RAW") & (df_n1_raw["seed"] == 42)].iloc[0]
    small_cal = df_n1_raw[(df_n1_raw["experiment_id"] == "D1_D3_FTT_ARGUS4_CALIB") & (df_n1_raw["seed"] == 42)].iloc[0]
    small_hist = pd.read_csv(NR / "training_logs/training_history_FTT_ARGUS4_D1_D3_seed42.csv")

    # Load FTT-LARGE Seed 42 capacity test metrics
    df_cap_metrics = pd.read_csv(CAP / "metrics/CAPACITY01_seed42.csv")
    large_def = df_cap_metrics[df_cap_metrics["experiment_id"] == "CAPACITY01_RAW"].iloc[0]
    large_cal = df_cap_metrics[df_cap_metrics["experiment_id"] == "CAPACITY01_CALIB"].iloc[0]
    large_hist = pd.read_csv(CAP / "training_logs/CAPACITY01_seed42_history.csv")

    # FTT-SMALL loss history info
    small_best_ep = 1
    small_train_loss = float(small_hist.iloc[0]["train_loss"])
    small_val_loss = float(small_hist.iloc[0]["val_loss"])

    # FTT-LARGE loss history info
    large_best_ep = int(large_def["best_epoch"])
    large_train_loss = float(large_hist.iloc[large_best_ep - 1]["train_loss"])
    large_val_loss = float(large_hist.iloc[large_best_ep - 1]["val_loss"])

    # FTT-LARGE-REG loss history info
    reg_best_ep = int(best_epoch)
    reg_train_loss = float(df_hist.iloc[reg_best_ep - 1]["train_loss"])
    reg_val_loss = float(df_hist.iloc[reg_best_ep - 1]["val_loss"])

    # CAPACITY_REGULARIZATION_COMPARISON.csv
    comp_matrix_rows = [
        {
            "Model": "FTT-SMALL",
            "Parameters": 17473,
            "Dropout": 0.10,
            "Weight_Decay": 0.0001,
            "Best_Epoch": small_best_ep,
            "Train_Loss": small_train_loss,
            "Validation_Loss": small_val_loss,
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
            "Model": "FTT-LARGE",
            "Parameters": large_params,
            "Dropout": 0.10,
            "Weight_Decay": 0.0001,
            "Best_Epoch": large_best_ep,
            "Train_Loss": large_train_loss,
            "Validation_Loss": large_val_loss,
            "ROC_AUC": float(large_def["roc_auc"]),
            "PR_AUC": float(large_def["pr_auc"]),
            "F1_Default": float(large_def["f1"]),
            "F1_Calibrated": float(large_cal["f1"]),
            "MCC_Default": float(large_def["mcc"]),
            "MCC_Calibrated": float(large_cal["mcc"]),
            "FPR_Default": float(large_def["fpr"]),
            "FPR_Calibrated": float(large_cal["fpr"]),
            "FNR_Default": float(large_def["fnr"]),
            "FNR_Calibrated": float(large_cal["fnr"]),
            "Accuracy_Calibrated": float(large_cal["accuracy"])
        },
        {
            "Model": "FTT-LARGE-REG",
            "Parameters": large_params,
            "Dropout": hp["dropout"],
            "Weight_Decay": tr["weight_decay"],
            "Best_Epoch": reg_best_ep,
            "Train_Loss": reg_train_loss,
            "Validation_Loss": reg_val_loss,
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
        }
    ]
    pd.DataFrame(comp_matrix_rows).to_csv(REG / "metrics/CAPACITY_REGULARIZATION_COMPARISON.csv", index=False)

    # CAPACITY_OVERFITTING_ANALYSIS.csv
    gap_small = small_val_loss - small_train_loss
    gap_large = large_val_loss - large_train_loss
    gap_reg = reg_val_loss - reg_train_loss
    
    overfitting_rows = [
        {
            "Model": "FTT-SMALL",
            "Train_Loss": small_train_loss,
            "Val_Loss": small_val_loss,
            "Generalization_Gap": gap_small,
            "Val_Train_Loss_Ratio": small_val_loss / small_train_loss,
            "Target_ROC_AUC": float(small_def["roc_auc"])
        },
        {
            "Model": "FTT-LARGE",
            "Train_Loss": large_train_loss,
            "Val_Loss": large_val_loss,
            "Generalization_Gap": gap_large,
            "Val_Train_Loss_Ratio": large_val_loss / large_train_loss,
            "Target_ROC_AUC": float(large_def["roc_auc"])
        },
        {
            "Model": "FTT-LARGE-REG",
            "Train_Loss": reg_train_loss,
            "Val_Loss": reg_val_loss,
            "Generalization_Gap": gap_reg,
            "Val_Train_Loss_Ratio": reg_val_loss / reg_train_loss,
            "Target_ROC_AUC": float(m_def["roc_auc"])
        }
    ]
    pd.DataFrame(overfitting_rows).to_csv(REG / "metrics/CAPACITY_OVERFITTING_ANALYSIS.csv", index=False)

    # 9. Standalone & Comparison Figures (300 DPI)
    print(f"\n[7/8] Generating 300 DPI Publication Figures...")
    
    # 9.1 FTT-LARGE-REG ROC
    fpr_r, tpr_r, th_r = roc_curve(y_d3_test, test_probs)
    roc_auc_reg = auc(fpr_r, tpr_r)
    pd.DataFrame({"fpr": fpr_r, "tpr": tpr_r, "threshold": np.append(th_r[:-1], th_r[-1])}).to_csv(
        REG / "figures/FTT_LARGE_REG_ROC.csv", index=False
    )
    
    plt.figure(figsize=(7, 6), dpi=300)
    plt.plot(fpr_r, tpr_r, color="#17becf", lw=2.5, label=f"FTT-LARGE-REG (Seed 42, AUC = {roc_auc_reg:.4f})")
    plt.plot([0, 1], [0, 1], color="#7f7f7f", linestyle="--", lw=1.5, label="Random Guess (AUC = 0.5000)")
    plt.xlabel("False Positive Rate (FPR)", fontsize=12, fontweight="bold")
    plt.ylabel("True Positive Rate / Recall (TPR)", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01R: ROC Curve — FTT-LARGE-REG ARGUS-4 (D1 → D3)\nDropout=0.30, WeightDecay=0.01 (N=714,453)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=11)
    plt.tight_layout()
    plt.savefig(REG / "figures/FTT_LARGE_REG_ROC.png", dpi=300)
    plt.close()

    # 9.2 FTT-LARGE-REG PR
    prec_r, rec_r, pr_th_r = precision_recall_curve(y_d3_test, test_probs)
    pr_auc_reg = auc(rec_r, prec_r)
    pd.DataFrame({"precision": prec_r[:-1], "recall": rec_r[:-1], "threshold": pr_th_r}).to_csv(
        REG / "figures/FTT_LARGE_REG_PR.csv", index=False
    )
    
    no_skill = np.mean(y_d3_test)
    plt.figure(figsize=(7, 6), dpi=300)
    plt.plot(rec_r, prec_r, color="#bcbd22", lw=2.5, label=f"FTT-LARGE-REG (Seed 42, AUC = {pr_auc_reg:.4f})")
    plt.axhline(y=no_skill, color="#7f7f7f", linestyle="--", lw=1.5, label=f"Target Attack Prior ($\pi$ = {no_skill:.4f})")
    plt.xlabel("Recall", fontsize=12, fontweight="bold")
    plt.ylabel("Precision", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01R: Precision-Recall Curve — FTT-LARGE-REG (D1 → D3)\nDropout=0.30, WeightDecay=0.01 (N=714,453)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=11)
    plt.tight_layout()
    plt.savefig(REG / "figures/FTT_LARGE_REG_PR.png", dpi=300)
    plt.close()

    # 9.3 Confusion Matrix
    cm_def_r = confusion_matrix(y_d3_test, (test_probs >= 0.50).astype(int))
    cm_cal_r = confusion_matrix(y_d3_test, (test_probs >= best_th).astype(int))
    
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    sns.heatmap(cm_def_r, annot=True, fmt="d", cmap="YlGnBu", cbar=False, ax=axes[0],
                xticklabels=["Normal (0)", "Attack (1)"], yticklabels=["Normal (0)", "Attack (1)"])
    axes[0].set_title(f"Default Threshold ($\Theta = 0.50$)\nFPR={m_def['fpr']*100:.2f}%, FNR={m_def['fnr']*100:.2f}%, F1={m_def['f1']:.4f}", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Predicted Class", fontsize=11)
    axes[0].set_ylabel("True Class", fontsize=11)

    sns.heatmap(cm_cal_r, annot=True, fmt="d", cmap="PuBuGn", cbar=False, ax=axes[1],
                xticklabels=["Normal (0)", "Attack (1)"], yticklabels=["Normal (0)", "Attack (1)"])
    axes[1].set_title(f"Calibrated Threshold ($\Theta = {best_th:.2f}$)\nFPR={m_cal['fpr']*100:.2f}%, FNR={m_cal['fnr']*100:.2f}%, F1={m_cal['f1']:.4f}", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Predicted Class", fontsize=11)
    axes[1].set_ylabel("True Class", fontsize=11)

    fig.suptitle("CAPACITY-01R: Confusion Matrices — FTT-LARGE-REG (D1 → D3 Seed 42)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(REG / "figures/FTT_LARGE_REG_confusion_matrix.png", dpi=300)
    plt.close()

    # 9.4 Training Curve
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(df_hist["epoch"], df_hist["train_loss"], linestyle="--", color="#17becf", marker="s", lw=2, label="FTT-LARGE-REG Train Loss")
    plt.plot(df_hist["epoch"], df_hist["val_loss"], linestyle="-", color="#d62728", marker="o", lw=2, label="FTT-LARGE-REG Val Loss")
    plt.xlabel("Epoch", fontsize=12, fontweight="bold")
    plt.ylabel("BCE Loss", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01R: Loss History — FTT-LARGE-REG (Dropout=0.30, Decay=0.01)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=11)
    plt.tight_layout()
    plt.savefig(REG / "figures/FTT_LARGE_REG_training_curve.png", dpi=300)
    plt.close()

    # 9.5 Operating Curve
    df_op = pd.DataFrame(operating_curve_data)
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(df_op["threshold"], df_op["val_f1"], color="#2ca02c", lw=2.5, label="Validation F1")
    plt.axvline(x=best_th, color="#d62728", linestyle="--", lw=1.5, label=f"Optimal Calibration ($\Theta$ = {best_th:.2f})")
    plt.xlabel("Decision Threshold ($\Theta$)", fontsize=12, fontweight="bold")
    plt.ylabel("Target Validation F1", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01R: Operating Threshold Calibration Curve", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=11)
    plt.tight_layout()
    plt.savefig(REG / "figures/FTT_LARGE_REG_calibration_curve.png", dpi=300)
    plt.savefig(REG / "figures/FTT_LARGE_REG_operating_curve.png", dpi=300)
    plt.close()

    # 9.6 THREE-WAY COMPARISON FIGURES (FTT-SMALL vs FTT-LARGE vs FTT-LARGE-REG)
    # Load FTT-SMALL Seed 42 predictions
    df_small_p = pd.read_csv(NR / "predictions/NR01/D1_D3_seed42_predictions.csv")
    fpr_s, tpr_s, _ = roc_curve(df_small_p["y_true"], df_small_p["y_prob"])
    roc_auc_s = auc(fpr_s, tpr_s)
    prec_s, rec_s, _ = precision_recall_curve(df_small_p["y_true"], df_small_p["y_prob"])
    pr_auc_s = auc(rec_s, prec_s)

    # Load FTT-LARGE Seed 42 predictions
    df_large_p = pd.read_csv(CAP / "predictions/CAPACITY01_seed42_predictions.csv")
    fpr_l, tpr_l, _ = roc_curve(df_large_p["true_label"], df_large_p["predicted_probability"])
    roc_auc_l = auc(fpr_l, tpr_l)
    prec_l, rec_l, _ = precision_recall_curve(df_large_p["true_label"], df_large_p["predicted_probability"])
    pr_auc_l = auc(rec_l, prec_l)

    # 9.6.1 ROC Comparison Figure
    plt.figure(figsize=(8, 6), dpi=300)
    plt.plot(fpr_s, tpr_s, color="#1f77b4", lw=2.5, label=f"FTT-SMALL (17.5k params, AUC = {roc_auc_s:.4f})")
    plt.plot(fpr_l, tpr_l, color="#9467bd", lw=2.5, label=f"FTT-LARGE (200.7k params, AUC = {roc_auc_l:.4f})")
    plt.plot(fpr_r, tpr_r, color="#17becf", lw=2.5, label=f"FTT-LARGE-REG (200.7k params + Reg, AUC = {roc_auc_reg:.4f})")
    plt.plot([0, 1], [0, 1], color="#7f7f7f", linestyle="--", lw=1.5, label="Random Guess (AUC = 0.5000)")
    plt.xlabel("False Positive Rate (FPR)", fontsize=12, fontweight="bold")
    plt.ylabel("True Positive Rate / Recall (TPR)", fontsize=12, fontweight="bold")
    plt.title("ARGUS Capacity & Regularization Stress Test: ROC Curve Comparison\nControlled D1 → D3 ARGUS-4 Task (Seed 42)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=10)
    plt.tight_layout()
    plt.savefig(REG / "figures/CAPACITY_REGULARIZATION_ROC_COMPARISON.png", dpi=300)
    plt.close()

    # 9.6.2 PR Comparison Figure
    plt.figure(figsize=(8, 6), dpi=300)
    plt.plot(rec_s, prec_s, color="#1f77b4", lw=2.5, label=f"FTT-SMALL (17.5k params, AUC = {pr_auc_s:.4f})")
    plt.plot(rec_l, prec_l, color="#9467bd", lw=2.5, label=f"FTT-LARGE (200.7k params, AUC = {pr_auc_l:.4f})")
    plt.plot(rec_r, prec_r, color="#17becf", lw=2.5, label=f"FTT-LARGE-REG (200.7k params + Reg, AUC = {pr_auc_reg:.4f})")
    plt.axhline(y=no_skill, color="#7f7f7f", linestyle="--", lw=1.5, label=f"Target Attack Prior ($\pi$ = {no_skill:.4f})")
    plt.xlabel("Recall", fontsize=12, fontweight="bold")
    plt.ylabel("Precision", fontsize=12, fontweight="bold")
    plt.title("ARGUS Capacity & Regularization Stress Test: PR Curve Comparison\nControlled D1 → D3 ARGUS-4 Task (Seed 42)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=10)
    plt.tight_layout()
    plt.savefig(REG / "figures/CAPACITY_REGULARIZATION_PR_COMPARISON.png", dpi=300)
    plt.close()

    # 9.6.3 Loss Comparison Figure
    plt.figure(figsize=(8, 6), dpi=300)
    plt.plot(small_hist["epoch"], small_hist["train_loss"], linestyle="--", color="#1f77b4", lw=2, label="FTT-SMALL Train Loss")
    plt.plot(small_hist["epoch"], small_hist["val_loss"], linestyle="-", color="#1f77b4", marker="o", lw=2, label="FTT-SMALL Val Loss")
    plt.plot(large_hist["epoch"], large_hist["train_loss"], linestyle="--", color="#9467bd", lw=2, label="FTT-LARGE Train Loss")
    plt.plot(large_hist["epoch"], large_hist["val_loss"], linestyle="-", color="#9467bd", marker="s", lw=2, label="FTT-LARGE Val Loss")
    plt.plot(df_hist["epoch"], df_hist["train_loss"], linestyle="--", color="#17becf", lw=2, label="FTT-LARGE-REG Train Loss")
    plt.plot(df_hist["epoch"], df_hist["val_loss"], linestyle="-", color="#17becf", marker="^", lw=2, label="FTT-LARGE-REG Val Loss")
    plt.xlabel("Epoch", fontsize=12, fontweight="bold")
    plt.ylabel("BCE Loss", fontsize=12, fontweight="bold")
    plt.title("CAPACITY-01R: Train vs Target-Validation Loss Gap Comparison", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=9, ncol=2)
    plt.tight_layout()
    plt.savefig(REG / "figures/CAPACITY_REGULARIZATION_LOSS_COMPARISON.png", dpi=300)
    plt.close()

    elapsed = time.time() - t_start
    print(f"\n[+] CAPACITY-01R finished in {elapsed:.2f} seconds.")
    return {
        "reg_params": large_params,
        "small_def": small_def,
        "small_cal": small_cal,
        "large_def": large_def,
        "large_cal": large_cal,
        "m_def": m_def,
        "m_cal": m_cal,
        "gap_small": gap_small,
        "gap_large": gap_large,
        "gap_reg": gap_reg,
        "elapsed": elapsed
    }

if __name__ == "__main__":
    res = run_regularization()
