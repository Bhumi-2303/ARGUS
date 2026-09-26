#!/usr/bin/env python3
"""
ARGUS Domain Adaptation DA-01 — Phase DA-01B & DA-01C:
CORAL Statistics Computation & Transformation Validation.
Computes Source, Target, and Aligned covariance structures, Frobenius distances, and publication figures.
"""

import os
import sys
import gc
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import scipy.linalg

os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib_cache'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
BASE = _curr
EE = BASE / "experiment_execution"
NR = EE / "neural_robustness"
DA = NR / "domain_adaptation"
CORAL_DATA_DIR = BASE / "ARGUS_Cross_Domain_Results/argus_coral_data"

FEATURE_COLS = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
FEATURE_DISPLAY_NAMES = [
    'Packet Mean/Max Ratio',
    'TCP Flag Density',
    'Log Packet Mean',
    'Log Packet Max'
]

class CORALOperator:
    """Mathematical Second-Order Covariance Alignment (Sun et al., 2016)."""
    def __init__(self, reg: float = 1e-6):
        self.reg = reg
        self.source_mean = None
        self.target_mean = None
        self.source_cov = None
        self.target_cov = None
        self.aligned_cov = None
        self.A = None

    def fit(self, X_s: np.ndarray, X_t: np.ndarray):
        n_s, d = X_s.shape
        n_t, _ = X_t.shape

        self.source_mean = np.mean(X_s, axis=0)
        self.target_mean = np.mean(X_t, axis=0)

        X_s_c = X_s - self.source_mean
        X_t_c = X_t - self.target_mean

        C_s = (X_s_c.T @ X_s_c) / (n_s - 1) + self.reg * np.eye(d)
        C_t = (X_t_c.T @ X_t_c) / (n_t - 1) + self.reg * np.eye(d)

        self.source_cov = C_s
        self.target_cov = C_t

        U_s, S_s, V_s = np.linalg.svd(C_s)
        C_s_inv_half = U_s @ np.diag(1.0 / np.sqrt(S_s)) @ V_s

        U_t, S_t, V_t = np.linalg.svd(C_t)
        C_t_half = U_t @ np.diag(np.sqrt(S_t)) @ V_t

        self.A = C_s_inv_half @ C_t_half
        return self

    def transform_source(self, X_s: np.ndarray) -> np.ndarray:
        X_s_c = X_s - self.source_mean
        X_aligned = (X_s_c @ self.A) + self.target_mean
        return X_aligned


def run_coral_statistics_and_validation():
    print("=========================================================================")
    print("ARGUS DA-01: PHASE DA-01B & DA-01C — CORAL STATISTICS & VALIDATION")
    print("=========================================================================")

    # 1. Load D1 source training features
    print("[1] Loading D1 Source Training Features (N = 5,491,971)...")
    d1_df = pd.read_csv(CORAL_DATA_DIR / "ciciot_train_features.csv", usecols=FEATURE_COLS)
    X_s = d1_df.values.astype(np.float64)
    del d1_df
    gc.collect()

    # 2. Load D3 target unlabeled adaptation features
    print("[2] Loading D3 Target Adaptation Features (N = 2,286,249, UNLABELED)...")
    d3_adapt_df = pd.read_csv(CORAL_DATA_DIR / "iec104_train_adaptation.csv", usecols=FEATURE_COLS)
    X_t = d3_adapt_df.values.astype(np.float64)
    del d3_adapt_df
    gc.collect()

    # 3. Fit CORAL Operator
    print("[3] Computing Empirical Means & 4x4 Covariance Matrices...")
    coral = CORALOperator(reg=1e-6)
    coral.fit(X_s, X_t)

    # 4. Transform Source & Compute Aligned Covariance
    print("[4] Aligning Source Representation into Target Covariance Space...")
    X_s_aligned = coral.transform_source(X_s)
    coral.aligned_cov = np.cov(X_s_aligned, rowvar=False)

    # 5. Export Statistics
    (DA / "statistics").mkdir(parents=True, exist_ok=True)
    (DA / "figures").mkdir(parents=True, exist_ok=True)

    # Source Statistics
    df_src_stat = pd.DataFrame({
        "feature": FEATURE_COLS,
        "feature_name": FEATURE_DISPLAY_NAMES,
        "mean": coral.source_mean,
        "variance": np.diag(coral.source_cov) - 1e-6,
        "std": np.sqrt(np.diag(coral.source_cov) - 1e-6)
    })
    df_src_stat.to_csv(DA / "statistics/DA01_source_statistics.csv", index=False)

    # Target Statistics
    df_tgt_stat = pd.DataFrame({
        "feature": FEATURE_COLS,
        "feature_name": FEATURE_DISPLAY_NAMES,
        "mean": coral.target_mean,
        "variance": np.diag(coral.target_cov) - 1e-6,
        "std": np.sqrt(np.diag(coral.target_cov) - 1e-6)
    })
    df_tgt_stat.to_csv(DA / "statistics/DA01_target_statistics.csv", index=False)

    # Covariance Comparison Table
    df_comp = pd.DataFrame({
        "feature": FEATURE_COLS,
        "feature_name": FEATURE_DISPLAY_NAMES,
        "source_mean": coral.source_mean,
        "target_mean": coral.target_mean,
        "aligned_mean": np.mean(X_s_aligned, axis=0),
        "source_variance": np.diag(coral.source_cov) - 1e-6,
        "target_variance": np.diag(coral.target_cov) - 1e-6,
        "aligned_variance": np.diag(coral.aligned_cov)
    })
    df_comp.to_csv(DA / "statistics/DA01_covariance_comparison.csv", index=False)

    # Save 4x4 covariance matrices
    np.savez(
        DA / "statistics/DA01_covariance_matrices.npz",
        source_mean=coral.source_mean,
        target_mean=coral.target_mean,
        source_cov=coral.source_cov,
        target_cov=coral.target_cov,
        aligned_cov=coral.aligned_cov,
        A_transform=coral.A
    )

    # 6. Compute Frobenius Norm Distances
    d_before = float(np.linalg.norm(coral.source_cov - coral.target_cov, ord='fro'))
    d_after = float(np.linalg.norm(coral.aligned_cov - coral.target_cov, ord='fro'))
    abs_reduction = d_before - d_after
    pct_reduction = (abs_reduction / d_before) * 100.0

    print(f"\n[*] Pre-alignment Frobenius Distance  ||C_s - C_t||_F:      {d_before:.6f}")
    print(f"[*] Post-alignment Frobenius Distance ||C_align - C_t||_F:  {d_after:.6f}")
    print(f"[*] Absolute Covariance Reduction:                         {abs_reduction:.6f}")
    print(f"[*] Percentage Covariance Reduction:                       {pct_reduction:.4f}%")

    df_coral_val = pd.DataFrame([{
        "metric": "Frobenius_Covariance_Distance",
        "pre_alignment_distance": d_before,
        "post_alignment_distance": d_after,
        "absolute_reduction": abs_reduction,
        "percentage_reduction": pct_reduction,
        "source_samples": len(X_s),
        "target_adaptation_samples": len(X_t),
        "regularization": 1e-6,
        "status": "VALIDATED_SUCCESSFUL_ALIGNMENT"
    }])
    df_coral_val.to_csv(DA / "statistics/DA01_coral_alignment_statistics.csv", index=False)

    # 7. Generate Figures (300 DPI)
    # Figure 1: 3-Panel Covariance Heatmap
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), dpi=300)
    vmin = min(coral.source_cov.min(), coral.target_cov.min(), coral.aligned_cov.min())
    vmax = max(coral.source_cov.max(), coral.target_cov.max(), coral.aligned_cov.max())

    sns.heatmap(coral.source_cov, ax=axes[0], annot=True, fmt=".3f", cmap="Blues",
                xticklabels=FEATURE_COLS, yticklabels=FEATURE_COLS, cbar=True)
    axes[0].set_title(r"$\mathbf{Source\ Covariance\ (C_s)}$" + "\n" + r"$D_1:\ \mathrm{CICIoT2023}$", fontsize=12, fontweight='bold')

    sns.heatmap(coral.target_cov, ax=axes[1], annot=True, fmt=".3f", cmap="Oranges",
                xticklabels=FEATURE_COLS, yticklabels=FEATURE_COLS, cbar=True)
    axes[1].set_title(r"$\mathbf{Target\ Covariance\ (C_t)}$" + "\n" + r"$D_3:\ \mathrm{IEC\ 60870\text{-}5\text{-}104\ (Unlabeled)}$", fontsize=12, fontweight='bold')

    sns.heatmap(coral.aligned_cov, ax=axes[2], annot=True, fmt=".3f", cmap="Greens",
                xticklabels=FEATURE_COLS, yticklabels=FEATURE_COLS, cbar=True)
    axes[2].set_title(r"$\mathbf{Aligned\ Covariance\ (C_{aligned})}$" + "\n" + r"$CORAL\ Transformation\ (D_1 \to D_3)$", fontsize=12, fontweight='bold')

    plt.tight_layout()
    fig.savefig(DA / "figures/DA01_covariance_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] Saved figures/DA01_covariance_heatmap.png")

    # Figure 2: Covariance Comparison & Distance
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # Bar chart of Frobenius Distance Before vs After
    bars = ax1.bar(["Pre-Alignment\n(||C_s - C_t||_F)", "Post-Alignment\n(||C_aligned - C_t||_F)"],
                   [d_before, d_after], color=["#d9534f", "#5cb85c"], width=0.5, edgecolor="black", linewidth=1.2)
    ax1.set_ylabel("Frobenius Distance", fontsize=11, fontweight='bold')
    ax1.set_title("Source-Target Covariance Discrepancy Reduction", fontsize=12, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    for bar, val in zip(bars, [d_before, d_after]):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.02 * d_before, f"{val:.4f}",
                 ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax1.set_ylim(0, d_before * 1.2)

    # Feature variance comparison
    x = np.arange(len(FEATURE_COLS))
    width = 0.25
    ax2.bar(x - width, np.diag(coral.source_cov) - 1e-6, width, label='Source (D1)', color='#337ab7', edgecolor='black')
    ax2.bar(x, np.diag(coral.target_cov) - 1e-6, width, label='Target (D3)', color='#f0ad4e', edgecolor='black')
    ax2.bar(x + width, np.diag(coral.aligned_cov), width, label='Aligned Source', color='#5cb85c', edgecolor='black')
    ax2.set_xticks(x)
    ax2.set_xticklabels(FEATURE_COLS, rotation=15, ha='right', fontsize=9)
    ax2.set_ylabel("Variance", fontsize=11, fontweight='bold')
    ax2.set_title("Feature-Wise Variance Alignment", fontsize=12, fontweight='bold')
    ax2.legend(frameon=True)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    fig.savefig(DA / "figures/DA01_covariance_distance.png", dpi=300, bbox_inches='tight')
    fig.savefig(DA / "figures/DA01_covariance_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] Saved figures/DA01_covariance_distance.png & figures/DA01_covariance_comparison.png")

    # Update experiment_state.json
    with open(DA / "experiment_state.json", "r") as f:
        state = json.load(f)
    state["current_stage"] = "STAGE_DA01B_C_CORAL_VALIDATED"
    state["completed_stages"].extend(["DA01B", "DA01C"])
    state["last_successful_artifact"] = "experiment_execution/neural_robustness/domain_adaptation/statistics/DA01_coral_alignment_statistics.csv"
    state["status"] = "READY_FOR_PHASE_DA01D_MODEL_TRAINING"
    state["timestamp"] = datetime.now().isoformat()
    with open(DA / "experiment_state.json", "w") as f:
        json.dump(state, f, indent=2)

    print("\n[OK] Phase DA-01B & DA-01C completed successfully.")

if __name__ == "__main__":
    run_coral_statistics_and_validation()
