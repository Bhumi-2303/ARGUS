#!/usr/bin/env python3
"""
ARGUS Neural Robustness — Regularization & Robustness Ablation Suite (A0-A3)
Evaluates:
  A0: Baseline FTT-SMALL (Preserved)
  A1: FTT-SMALL + Label Smoothing (0.05)
  A2: FTT-SMALL + Feature Masking (10% noise during training)
  A3: FTT-SMALL + Label Smoothing (0.05) + Feature Masking (10%)
Generates all metrics, confusion matrices, raw curve CSVs, 300 DPI figures,
comparison tables, effect size tables, and artifact manifest.
"""

import os
import sys
import json
import time
import gc
import hashlib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_ablation"
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
ABL = NR / "ablation"
CORAL_DIR = BASE / "ARGUS_Cross_Domain_Results/argus_coral_data"

sys.path.append(str(EE / "scripts"))
from validate_metrics import compute_all_metrics

sys.path.append(str(NR / "scripts"))
from ft_transformer import FTTransformer

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

def compute_sha256(filepath):
    """Compute SHA256 checksum of a file."""
    if not os.path.exists(filepath):
        return "N/A"
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()

def run_ablation():
    print("=" * 80)
    print("ARGUS NEURAL ROBUSTNESS — REGULARIZATION & ROBUSTNESS ABLATION SUITE (A0-A3)")
    print("=" * 80)

    t_start = time.time()
    feat_cols = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
    seed = 42
    batch_size = 16384

    # 1. Load Frozen Datasets
    print(f"\n[1/6] Loading Frozen Dataset Partitions...")
    df_d1_train = pd.read_csv(CORAL_DIR / "ciciot_train_features.csv")
    X_d1_train = df_d1_train[feat_cols].values
    y_d1_train = df_d1_train["label"].values.astype(np.float32)

    df_d3_calib = pd.read_csv(CORAL_DIR / "iec104_train_calibration.csv")
    X_d3_calib = df_d3_calib[feat_cols].values
    y_d3_calib = df_d3_calib["label"].values.astype(np.float32)

    df_d3_test = pd.read_csv(CORAL_DIR / "iec104_test_features.csv")
    X_d3_test = df_d3_test[feat_cols].values
    y_d3_test = df_d3_test["label"].values.astype(np.float32)

    # Subsampling
    _, X_tr_sub, _, y_tr_sub = train_test_split(
        X_d1_train, y_d1_train, test_size=500000, random_state=seed, stratify=y_d1_train
    )
    _, X_val_sub, _, y_val_sub = train_test_split(
        X_d3_calib, y_d3_calib, test_size=50000, random_state=seed, stratify=y_d3_calib
    )

    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_tr_sub)
    X_val_scaled = scaler.transform(X_val_sub)
    X_val_full_scaled = scaler.transform(X_d3_calib)
    X_te_scaled = scaler.transform(X_d3_test)

    # 2. A0 Baseline Artifact Loading (Preserved)
    print(f"\n[2/6] Loading A0 Baseline Preserved Artifacts...")
    df_a0_preds = pd.read_csv(NR / "predictions/NR01/D1_D3_seed42_predictions.csv")
    y_a0_true = df_a0_preds["y_true"].values
    y_a0_prob = df_a0_preds["y_prob"].values
    
    df_a0_m = pd.read_csv(NR / "metrics/NR01_FTTransformer_ARGUS4.csv")
    a0_raw_m = df_a0_m[(df_a0_m["experiment_id"] == "D1_D3_FTT_ARGUS4_RAW") & (df_a0_m["seed"] == seed)].iloc[0]
    a0_cal_m = df_a0_m[(df_a0_m["experiment_id"] == "D1_D3_FTT_ARGUS4_CALIB") & (df_a0_m["seed"] == seed)].iloc[0]
    a0_hist = pd.read_csv(NR / "training_logs/training_history_FTT_ARGUS4_D1_D3_seed42.csv")

    a0_best_epoch = 1
    a0_train_loss = float(a0_hist.iloc[0]["train_loss"])
    a0_val_loss = float(a0_hist.iloc[0]["val_loss"])

    a0_results = {
        "condition": "A0_BASELINE",
        "parameters": 17473,
        "seed": seed,
        "label_smoothing": 0.00,
        "feature_masking": 0.00,
        "train_loss": a0_train_loss,
        "val_loss": a0_val_loss,
        "gen_gap": a0_val_loss - a0_train_loss,
        "best_epoch": a0_best_epoch,
        "roc_auc": float(a0_raw_m["roc_auc"]),
        "pr_auc": float(a0_raw_m["pr_auc"]),
        "raw_m": compute_all_metrics(y_a0_true, y_a0_prob, threshold=0.50),
        "cal_m": compute_all_metrics(y_a0_true, y_a0_prob, threshold=float(a0_cal_m["threshold"])),
        "calib_threshold": float(a0_cal_m["threshold"]),
        "y_prob": y_a0_prob,
        "y_true": y_a0_true,
        "history": a0_hist
    }

    # 3. Define Training Runner for Interventions (A1, A2, A3)
    conditions = [
        ("A1_LABEL_SMOOTHING", ABL / "configs/A1_label_smoothing.json", 0.05, 0.00),
        ("A2_FEATURE_MASKING", ABL / "configs/A2_feature_masking.json", 0.00, 0.10),
        ("A3_COMBINED", ABL / "configs/A3_combined.json", 0.05, 0.10)
    ]

    all_results = {"A0_BASELINE": a0_results}

    for cond_id, cfg_path, label_sm, feat_mask in conditions:
        print(f"\n[3/6] Running Condition {cond_id} (LS={label_sm}, FM={feat_mask})...")
        with open(cfg_path, "r") as f:
            cfg = json.load(f)

        torch.manual_seed(seed)
        np.random.seed(seed)

        model = FTTransformer(
            n_features=len(feat_cols),
            d_token=32,
            n_blocks=2,
            n_heads=4,
            d_ff=64,
            dropout=0.10
        ).to(DEVICE)

        tr_ds = TensorDataset(torch.tensor(X_tr_scaled, dtype=torch.float32), torch.tensor(y_tr_sub, dtype=torch.float32))
        val_ds = TensorDataset(torch.tensor(X_val_scaled, dtype=torch.float32), torch.tensor(y_val_sub, dtype=torch.float32))

        tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0001)

        best_val_loss = float("inf")
        best_epoch = 0
        patience_counter = 0

        ckpt_dir = ABL / f"checkpoints/{cond_id}_seed{seed}"
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        best_ckpt_path = ckpt_dir / "best_model.pt"

        history = []
        max_epochs = 10
        patience = 2

        for epoch in range(1, max_epochs + 1):
            model.train()
            tr_loss_sum = 0.0
            tr_count = 0

            for bx, by in tr_loader:
                bx, by = bx.to(DEVICE), by.to(DEVICE)
                
                # Apply dynamic feature masking if feature_mask > 0
                if feat_mask > 0.0:
                    mask = (torch.rand_like(bx) > feat_mask).float()
                    bx = bx * mask

                # Apply target label smoothing if label_sm > 0
                if label_sm > 0.0:
                    by_target = by * (1.0 - label_sm) + 0.5 * label_sm
                else:
                    by_target = by

                optimizer.zero_grad()
                logits = model(bx)
                loss = criterion(logits, by_target)
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

            print(f"  Epoch {epoch:02d}/10 | Train Loss: {tr_loss:.5f} | Val Loss: {val_loss:.5f} | Val AUC: {val_auc:.5f}")

            history.append({
                "epoch": epoch,
                "train_loss": float(tr_loss),
                "val_loss": float(val_loss),
                "val_auc": float(val_auc)
            })

            checkpoint_dict = {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": val_loss,
                "config": cfg,
                "seed": seed
            }

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

        df_hist = pd.DataFrame(history)
        df_hist.to_csv(ABL / f"training_logs/{cond_id}_history.csv", index=False)
        df_hist.to_csv(ABL / f"figures/{cond_id}_loss.csv", index=False)

        # Threshold Calibration on D3 Calibration Split
        ckpt_saved = torch.load(best_ckpt_path, map_location=DEVICE)
        model.load_state_dict(ckpt_saved["model_state_dict"])
        model.eval()

        val_full_ds = TensorDataset(torch.tensor(X_val_full_scaled, dtype=torch.float32))
        val_full_loader = DataLoader(val_full_ds, batch_size=batch_size, shuffle=False)

        val_probs = []
        with torch.no_grad():
            for (bx,) in val_full_loader:
                bx = bx.to(DEVICE)
                probs = torch.sigmoid(model(bx)).cpu().numpy()
                val_probs.extend(probs)
        val_probs = np.array(val_probs)

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
                "condition": cond_id,
                "threshold": float(th),
                "f1": float(f1_c),
                "precision": float(tp / (tp + fp)) if (tp + fp) > 0 else 0,
                "recall": float(tp / (tp + fn)) if (tp + fn) > 0 else 0,
                "fpr": float(fp / (fp + tn)),
                "fnr": float(fn / (fn + tp)),
                "mcc": float(matthews_corrcoef(y_d3_calib, p_val))
            })
            if f1_c > best_f1_val:
                best_f1_val = f1_c
                best_th = float(th)

        pd.DataFrame(operating_curve_data).to_csv(ABL / f"figures/{cond_id}_thresholds.csv", index=False)

        # Test Set Inference
        te_ds = TensorDataset(torch.tensor(X_te_scaled, dtype=torch.float32))
        te_loader = DataLoader(te_ds, batch_size=batch_size, shuffle=False)

        test_probs = []
        with torch.no_grad():
            for (bx,) in te_loader:
                bx = bx.to(DEVICE)
                probs = torch.sigmoid(model(bx)).cpu().numpy()
                test_probs.extend(probs)
        test_probs = np.array(test_probs)

        # Save Predictions
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
        df_preds.to_csv(ABL / f"predictions/{cond_id}_predictions.csv", index=False)

        # Compute Metrics
        raw_m = compute_all_metrics(y_d3_test, test_probs, threshold=0.50)
        cal_m = compute_all_metrics(y_d3_test, test_probs, threshold=best_th)

        raw_m.update({"condition": cond_id, "threshold": 0.50, "is_calibrated": False})
        cal_m.update({"condition": cond_id, "threshold": float(best_th), "is_calibrated": True})
        pd.DataFrame([raw_m, cal_m]).to_csv(ABL / f"metrics/{cond_id}_seed42.csv", index=False)

        best_tr_loss = float(df_hist.iloc[best_epoch - 1]["train_loss"])
        best_v_loss = float(df_hist.iloc[best_epoch - 1]["val_loss"])

        all_results[cond_id] = {
            "condition": cond_id,
            "parameters": 17473,
            "seed": seed,
            "label_smoothing": label_sm,
            "feature_masking": feat_mask,
            "train_loss": best_tr_loss,
            "val_loss": best_v_loss,
            "gen_gap": best_v_loss - best_tr_loss,
            "best_epoch": best_epoch,
            "roc_auc": float(raw_m["roc_auc"]),
            "pr_auc": float(raw_m["pr_auc"]),
            "raw_m": raw_m,
            "cal_m": cal_m,
            "calib_threshold": best_th,
            "y_prob": test_probs,
            "y_true": y_d3_test,
            "history": df_hist
        }

        # Memory Cleanup
        del model, optimizer, tr_loader, val_loader, tr_ds, val_ds
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    # 4. Generate Publication Figures & Curves (300 DPI)
    print(f"\n[4/6] Generating Publication Figures & Curves...")
    
    # 4.1 Save Individual Figures for A1, A2, A3
    for cond_id in ["A1_LABEL_SMOOTHING", "A2_FEATURE_MASKING", "A3_COMBINED"]:
        res = all_results[cond_id]
        y_t, y_p = res["y_true"], res["y_prob"]
        
        # ROC
        fpr_c, tpr_c, th_c = roc_curve(y_t, y_p)
        pd.DataFrame({"condition": cond_id, "threshold": np.append(th_c[:-1], th_c[-1]), "fpr": fpr_c, "tpr": tpr_c}).to_csv(
            ABL / f"figures/{cond_id}_ROC.csv", index=False
        )
        plt.figure(figsize=(6, 5), dpi=300)
        plt.plot(fpr_c, tpr_c, color="#1f77b4", lw=2, label=f"{cond_id} (AUC={res['roc_auc']:.4f})")
        plt.plot([0, 1], [0, 1], "--", color="#7f7f7f", lw=1.5)
        plt.xlabel("FPR", fontweight="bold")
        plt.ylabel("TPR", fontweight="bold")
        plt.title(f"ROC Curve — {cond_id}", fontweight="bold")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(ABL / f"figures/{cond_id}_ROC.png", dpi=300)
        plt.close()

        # PR
        prec_c, rec_c, pr_th_c = precision_recall_curve(y_t, y_p)
        pd.DataFrame({"condition": cond_id, "threshold": pr_th_c, "recall": rec_c[:-1], "precision": prec_c[:-1]}).to_csv(
            ABL / f"figures/{cond_id}_PR.csv", index=False
        )
        plt.figure(figsize=(6, 5), dpi=300)
        plt.plot(rec_c, prec_c, color="#2ca02c", lw=2, label=f"{cond_id} (AUC={res['pr_auc']:.4f})")
        plt.axhline(y=np.mean(y_t), linestyle="--", color="#7f7f7f")
        plt.xlabel("Recall", fontweight="bold")
        plt.ylabel("Precision", fontweight="bold")
        plt.title(f"PR Curve — {cond_id}", fontweight="bold")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(ABL / f"figures/{cond_id}_PR.png", dpi=300)
        plt.close()

        # Confusion Matrix
        cm_def = confusion_matrix(y_t, (y_p >= 0.50).astype(int))
        cm_cal = confusion_matrix(y_t, (y_p >= res["calib_threshold"]).astype(int))
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
        sns.heatmap(cm_def, annot=True, fmt="d", cmap="YlGnBu", cbar=False, ax=axes[0])
        axes[0].set_title(f"Default ($\Theta=0.50$)\nF1={res['raw_m']['f1']:.4f}", fontweight="bold")
        sns.heatmap(cm_cal, annot=True, fmt="d", cmap="PuBuGn", cbar=False, ax=axes[1])
        axes[1].set_title(f"Calibrated ($\Theta={res['calib_threshold']:.2f}$)\nF1={res['cal_m']['f1']:.4f}", fontweight="bold")
        fig.suptitle(f"Confusion Matrix — {cond_id}", fontweight="bold")
        plt.tight_layout()
        plt.savefig(ABL / f"figures/{cond_id}_confusion_matrix.png", dpi=300)
        plt.close()

    # 4.2 Combined 4-Way Overlay Figures (A0, A1, A2, A3)
    colors = {"A0_BASELINE": "#1f77b4", "A1_LABEL_SMOOTHING": "#ff7f0e", "A2_FEATURE_MASKING": "#2ca02c", "A3_COMBINED": "#d62728"}

    # ROC Combined
    plt.figure(figsize=(7.5, 6), dpi=300)
    for c_id, res in all_results.items():
        fpr_k, tpr_k, _ = roc_curve(res["y_true"], res["y_prob"])
        plt.plot(fpr_k, tpr_k, color=colors[c_id], lw=2.2, label=f"{c_id} (AUC={res['roc_auc']:.4f})")
    plt.plot([0, 1], [0, 1], "--", color="#7f7f7f", label="Random Guess (AUC=0.5000)")
    plt.xlabel("False Positive Rate (FPR)", fontsize=11, fontweight="bold")
    plt.ylabel("True Positive Rate (TPR)", fontsize=11, fontweight="bold")
    plt.title("ARGUS Robustness Ablation: ROC Curves (A0 vs A1 vs A2 vs A3)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=10)
    plt.tight_layout()
    plt.savefig(ABL / "figures/REGULARIZATION_ABLATION_ROC.png", dpi=300)
    plt.close()

    # PR Combined
    plt.figure(figsize=(7.5, 6), dpi=300)
    for c_id, res in all_results.items():
        prec_k, rec_k, _ = precision_recall_curve(res["y_true"], res["y_prob"])
        plt.plot(rec_k, prec_k, color=colors[c_id], lw=2.2, label=f"{c_id} (AUC={res['pr_auc']:.4f})")
    plt.axhline(y=np.mean(y_d3_test), linestyle="--", color="#7f7f7f", label=f"Prior ($\pi$={np.mean(y_d3_test):.4f})")
    plt.xlabel("Recall", fontsize=11, fontweight="bold")
    plt.ylabel("Precision", fontsize=11, fontweight="bold")
    plt.title("ARGUS Robustness Ablation: Precision-Recall Curves (A0-A3)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=10)
    plt.tight_layout()
    plt.savefig(ABL / "figures/REGULARIZATION_ABLATION_PR.png", dpi=300)
    plt.close()

    # Loss Combined
    plt.figure(figsize=(7.5, 6), dpi=300)
    for c_id, res in all_results.items():
        h = res["history"]
        plt.plot(h["epoch"], h["train_loss"], "--", color=colors[c_id], lw=1.8, label=f"{c_id} Train")
        plt.plot(h["epoch"], h["val_loss"], "-", color=colors[c_id], marker="o", lw=2, label=f"{c_id} Val")
    plt.xlabel("Epoch", fontsize=11, fontweight="bold")
    plt.ylabel("BCE Loss", fontsize=11, fontweight="bold")
    plt.title("ARGUS Robustness Ablation: Training vs Target Validation Loss", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(ABL / "figures/REGULARIZATION_ABLATION_LOSS.png", dpi=300)
    plt.close()

    # Summary 4-Way Bar Chart Comparison (Summary)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), dpi=300)
    cond_labels = ["A0\n(Base)", "A1\n(Smooth)", "A2\n(Mask)", "A3\n(Both)"]
    c_keys = ["A0_BASELINE", "A1_LABEL_SMOOTHING", "A2_FEATURE_MASKING", "A3_COMBINED"]
    bar_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    # ROC-AUC
    rocs = [all_results[k]["roc_auc"] for k in c_keys]
    axes[0, 0].bar(cond_labels, rocs, color=bar_colors)
    axes[0, 0].set_title("ROC-AUC", fontweight="bold")
    axes[0, 0].set_ylim(0.4, 0.7)
    for i, v in enumerate(rocs):
        axes[0, 0].text(i, v + 0.005, f"{v:.4f}", ha="center", fontweight="bold")

    # PR-AUC
    prs = [all_results[k]["pr_auc"] for k in c_keys]
    axes[0, 1].bar(cond_labels, prs, color=bar_colors)
    axes[0, 1].set_title("PR-AUC", fontweight="bold")
    axes[0, 1].set_ylim(0.1, 0.45)
    for i, v in enumerate(prs):
        axes[0, 1].text(i, v + 0.005, f"{v:.4f}", ha="center", fontweight="bold")

    # MCC Calibrated
    mccs = [all_results[k]["cal_m"]["mcc"] for k in c_keys]
    axes[1, 0].bar(cond_labels, mccs, color=bar_colors)
    axes[1, 0].set_title("MCC (Calibrated)", fontweight="bold")
    axes[1, 0].set_ylim(0.0, 0.15)
    for i, v in enumerate(mccs):
        axes[1, 0].text(i, v + 0.003, f"{v:.4f}", ha="center", fontweight="bold")

    # FPR Calibrated
    fprs = [all_results[k]["cal_m"]["fpr"] * 100 for k in c_keys]
    axes[1, 1].bar(cond_labels, fprs, color=bar_colors)
    axes[1, 1].set_title("False Positive Rate % (Calibrated)", fontweight="bold")
    axes[1, 1].set_ylim(0, 105)
    for i, v in enumerate(fprs):
        axes[1, 1].text(i, v + 1.5, f"{v:.2f}%", ha="center", fontweight="bold")

    fig.suptitle("ARGUS Robustness Ablation Suite (A0-A3) Primary Metrics", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(ABL / "figures/REGULARIZATION_ABLATION_SUMMARY.png", dpi=300)
    plt.close()

    # 5. Build Comparison & Effect-Size Tables
    print(f"\n[5/6] Generating Comparison & Effect-Size Tables...")
    
    comp_rows = []
    for k in c_keys:
        res = all_results[k]
        raw_m = res["raw_m"]
        cal_m = res["cal_m"]
        comp_rows.append({
            "Condition": k,
            "Parameters": res["parameters"],
            "Seed": res["seed"],
            "Label_Smoothing": res["label_smoothing"],
            "Feature_Masking": res["feature_masking"],
            "ROC_AUC": res["roc_auc"],
            "PR_AUC": res["pr_auc"],
            "Accuracy_Default": raw_m["accuracy"],
            "Precision_Default": raw_m["precision"],
            "Recall_Default": raw_m["recall"],
            "F1_Default": raw_m["f1"],
            "MCC_Default": raw_m["mcc"],
            "FPR_Default": raw_m["fpr"],
            "FNR_Default": raw_m["fnr"],
            "Calibrated_Threshold": res["calib_threshold"],
            "Accuracy_Calibrated": cal_m["accuracy"],
            "Precision_Calibrated": cal_m["precision"],
            "Recall_Calibrated": cal_m["recall"],
            "F1_Calibrated": cal_m["f1"],
            "MCC_Calibrated": cal_m["mcc"],
            "FPR_Calibrated": cal_m["fpr"],
            "FNR_Calibrated": cal_m["fnr"],
            "Best_Epoch": res["best_epoch"],
            "Train_Loss": res["train_loss"],
            "Validation_Loss": res["val_loss"],
            "Generalization_Gap": res["gen_gap"]
        })

    df_comp = pd.DataFrame(comp_rows)
    tables_dir = NR / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    df_comp.to_csv(tables_dir / "REGULARIZATION_ABLATION_COMPARISON.csv", index=False)
    df_comp.to_csv(ABL / "metrics/REGULARIZATION_ABLATION_COMPARISON.csv", index=False)

    # Effect Size Table relative to A0
    a0_res = all_results["A0_BASELINE"]
    effect_rows = []

    for k in ["A1_LABEL_SMOOTHING", "A2_FEATURE_MASKING", "A3_COMBINED"]:
        res = all_results[k]
        
        d_roc = res["roc_auc"] - a0_res["roc_auc"]
        d_pr = res["pr_auc"] - a0_res["pr_auc"]
        d_f1 = res["raw_m"]["f1"] - a0_res["raw_m"]["f1"]
        d_mcc = res["cal_m"]["mcc"] - a0_res["cal_m"]["mcc"]
        d_fpr = res["cal_m"]["fpr"] - a0_res["cal_m"]["fpr"]
        d_fnr = res["cal_m"]["fnr"] - a0_res["cal_m"]["fnr"]
        d_acc = res["cal_m"]["accuracy"] - a0_res["cal_m"]["accuracy"]

        rel_roc = (d_roc / a0_res["roc_auc"]) * 100
        rel_pr = (d_pr / a0_res["pr_auc"]) * 100

        effect_rows.append({
            "Intervention": k,
            "Delta_ROC_AUC": d_roc,
            "Rel_Change_ROC_AUC_Pct": rel_roc,
            "Delta_PR_AUC": d_pr,
            "Rel_Change_PR_AUC_Pct": rel_pr,
            "Delta_F1_Default": d_f1,
            "Delta_MCC_Calibrated": d_mcc,
            "Delta_FPR_Calibrated": d_fpr,
            "Delta_FNR_Calibrated": d_fnr,
            "Delta_Accuracy_Calibrated": d_acc
        })

    df_effects = pd.DataFrame(effect_rows)
    df_effects.to_csv(tables_dir / "REGULARIZATION_EFFECTS.csv", index=False)
    df_effects.to_csv(ABL / "metrics/REGULARIZATION_EFFECTS.csv", index=False)

    # 6. Generate SHA256 Artifact Manifest
    print(f"\n[6/6] Building SHA256 Artifact Manifest...")
    manifest_rows = []
    
    expected_files = [
        ("A1 Configuration", ABL / "configs/A1_label_smoothing.json", "A1", "Config"),
        ("A2 Configuration", ABL / "configs/A2_feature_masking.json", "A2", "Config"),
        ("A3 Configuration", ABL / "configs/A3_combined.json", "A3", "Config"),
        ("A1 Checkpoint", ABL / "checkpoints/A1_LABEL_SMOOTHING_seed42/best_model.pt", "A1", "Model Checkpoint"),
        ("A2 Checkpoint", ABL / "checkpoints/A2_FEATURE_MASKING_seed42/best_model.pt", "A2", "Model Checkpoint"),
        ("A3 Checkpoint", ABL / "checkpoints/A3_COMBINED_seed42/best_model.pt", "A3", "Model Checkpoint"),
        ("A1 Predictions", ABL / "predictions/A1_LABEL_SMOOTHING_predictions.csv", "A1", "Predictions CSV"),
        ("A2 Predictions", ABL / "predictions/A2_FEATURE_MASKING_predictions.csv", "A2", "Predictions CSV"),
        ("A3 Predictions", ABL / "predictions/A3_COMBINED_predictions.csv", "A3", "Predictions CSV"),
        ("A1 Metrics", ABL / "metrics/A1_LABEL_SMOOTHING_seed42.csv", "A1", "Metrics CSV"),
        ("A2 Metrics", ABL / "metrics/A2_FEATURE_MASKING_seed42.csv", "A2", "Metrics CSV"),
        ("A3 Metrics", ABL / "metrics/A3_COMBINED_seed42.csv", "A3", "Metrics CSV"),
        ("Ablation Comparison Table", tables_dir / "REGULARIZATION_ABLATION_COMPARISON.csv", "A0-A3", "Table CSV"),
        ("Effect Size Table", tables_dir / "REGULARIZATION_EFFECTS.csv", "A0-A3", "Table CSV"),
        ("Combined ROC Figure", ABL / "figures/REGULARIZATION_ABLATION_ROC.png", "A0-A3", "Figure PNG"),
        ("Combined PR Figure", ABL / "figures/REGULARIZATION_ABLATION_PR.png", "A0-A3", "Figure PNG"),
        ("Combined Loss Figure", ABL / "figures/REGULARIZATION_ABLATION_LOSS.png", "A0-A3", "Figure PNG"),
        ("Combined Summary Figure", ABL / "figures/REGULARIZATION_ABLATION_SUMMARY.png", "A0-A3", "Figure PNG")
    ]

    for desc, path, cond, ftype in expected_files:
        status = "EXISTS" if os.path.exists(path) else "MISSING"
        sha = compute_sha256(path)
        manifest_rows.append({
            "Artifact": desc,
            "Path": str(path.relative_to(BASE)),
            "Condition": cond,
            "Type": ftype,
            "Description": desc,
            "Seed": 42,
            "Test_Set_Used": "D3 Frozen Test Set (N=714,453)",
            "Status": status,
            "SHA256": sha
        })

    df_manifest = pd.DataFrame(manifest_rows)
    df_manifest.to_csv(ABL / "REGULARIZATION_ARTIFACT_MANIFEST.csv", index=False)
    df_manifest.to_csv(tables_dir / "REGULARIZATION_ARTIFACT_MANIFEST.csv", index=False)

    elapsed = time.time() - t_start
    print(f"\n[+] Regularization Ablation Suite (A0-A3) finished successfully in {elapsed:.2f} seconds.")
    return all_results

if __name__ == "__main__":
    run_ablation()
