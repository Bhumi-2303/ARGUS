#!/usr/bin/env python3
"""
ARGUS P1-1: NF-ToN-IoT-v2 In-Domain Supervised Baseline Training Script.

Trains two in-domain supervised models:
1. XGBoost (Model A)
2. LightGBM (Model B)

Using the designated NF-ToN-IoT-v2 adaptation/training split (8,406,962 rows).
Preserves the 4-feature harmonized schema matching Clean Class-Aware CORAL.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
import xgboost as xgb
import lightgbm as lgb

FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
TARGET = "label"


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 digest of a file in chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536 * 16):
            h.update(chunk)
    return h.hexdigest()


def get_memory_usage_mb() -> float:
    """Return current process RSS memory in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train in-domain supervised XGBoost and LightGBM baselines on NF-ToN-IoT-v2."
    )
    parser.add_argument(
        "--train-data",
        type=Path,
        default=Path("data/raw/legacy_package/argus_coral_data/nfton_train_adaptation.csv"),
        help="Path to NF-ToN training/adaptation dataset CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/experiments/p1_1_nfton_in_domain"),
        help="Directory to save trained model artifacts and training metadata.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic random seed for training reproducibility.",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=100,
        help="Number of boosting rounds (default: 100 matching ARGUS standard).",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.1,
        help="Learning rate for both gradient boosting models.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=8,
        help="Maximum tree depth (default: 8).",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=-1,
        help="Number of CPU threads (-1 for all available).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("================================================================================")
    print("ARGUS P1-1: NF-ToN-IoT-v2 In-Domain Supervised Baseline Training")
    print("================================================================================")
    print(f"Training Data Path : {args.train_data}")
    print(f"Output Directory   : {args.output_dir}")
    print(f"Random Seed        : {args.seed}")
    print(f"Features           : {FEATURES}")
    print(f"Target             : {TARGET}")
    print(f"Estimators         : {args.n_estimators}")
    print(f"Learning Rate      : {args.learning_rate}")
    print(f"Max Depth          : {args.max_depth}")

    if not args.train_data.exists():
        print(f"ERROR: Training data file not found: {args.train_data}", file=sys.stderr)
        sys.exit(1)

    # 1. Dataset Verification & Ingestion
    print("\n[Step 1/3] Computing checksum and loading training dataset...")
    t_start_load = time.time()
    train_sha256 = compute_file_sha256(args.train_data)
    mem_before_load = get_memory_usage_mb()

    # Load with optimized float32 / uint8 types to conserve memory
    df_train = pd.read_csv(
        args.train_data,
        dtype={
            "pkt_mean_to_max": "float32",
            "tcp_flag_density": "float32",
            "log_pkt_mean": "float32",
            "log_pkt_max": "float32",
            "label": "uint8",
        },
    )
    load_duration = time.time() - t_start_load
    mem_after_load = get_memory_usage_mb()

    total_samples = len(df_train)
    benign_samples = int((df_train[TARGET] == 0).sum())
    attack_samples = int((df_train[TARGET] == 1).sum())
    attack_ratio = attack_samples / total_samples

    print(f"  Loaded {total_samples:,} rows in {load_duration:.2f}s")
    print(f"  Memory delta: {mem_after_load - mem_before_load:.2f} MB (Current RSS: {mem_after_load:.2f} MB)")
    print(f"  SHA-256: {train_sha256}")
    print(f"  Class Distribution: Benign (0)={benign_samples:,} ({100*(1-attack_ratio):.2f}%), "
          f"Attack (1)={attack_samples:,} ({100*attack_ratio:.2f}%)")

    # Verify no NaN or Inf
    for col in FEATURES:
        assert not df_train[col].isna().any(), f"NaN detected in feature {col}"
        assert not np.isinf(df_train[col]).any(), f"Inf detected in feature {col}"

    X_train = df_train[FEATURES].values
    y_train = df_train[TARGET].values

    # 2. Train Model A: XGBoost
    print("\n[Step 2/3] Training Model A (XGBoost)...")
    xgb_params = {
        "n_estimators": args.n_estimators,
        "learning_rate": args.learning_rate,
        "max_depth": args.max_depth,
        "tree_method": "hist",
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "random_state": args.seed,
        "n_jobs": args.n_jobs,
    }
    print(f"  Hyperparameters: {xgb_params}")
    t_start_xgb = time.time()
    mem_before_xgb = get_memory_usage_mb()

    xgb_model = xgb.XGBClassifier(**xgb_params)
    xgb_model.fit(X_train, y_train)

    xgb_duration = time.time() - t_start_xgb
    mem_after_xgb = get_memory_usage_mb()
    xgb_path = args.output_dir / "xgboost_nfton_in_domain.json"
    xgb_model.save_model(str(xgb_path))
    xgb_sha256 = compute_file_sha256(xgb_path)

    print(f"  XGBoost training completed in {xgb_duration:.2f}s")
    print(f"  Memory delta: {mem_after_xgb - mem_before_xgb:.2f} MB")
    print(f"  Saved artifact: {xgb_path} ({xgb_path.stat().st_size / 1024:.1f} KB, SHA256: {xgb_sha256[:16]}...)")

    # 3. Train Model B: LightGBM
    print("\n[Step 3/3] Training Model B (LightGBM)...")
    lgb_params = {
        "n_estimators": args.n_estimators,
        "learning_rate": args.learning_rate,
        "max_depth": args.max_depth,
        "num_leaves": 63,
        "objective": "binary",
        "metric": "binary_logloss",
        "random_state": args.seed,
        "verbose": -1,
        "n_jobs": args.n_jobs,
    }
    print(f"  Hyperparameters: {lgb_params}")
    t_start_lgb = time.time()
    mem_before_lgb = get_memory_usage_mb()

    lgb_model = lgb.LGBMClassifier(**lgb_params)
    lgb_model.fit(X_train, y_train)

    lgb_duration = time.time() - t_start_lgb
    mem_after_lgb = get_memory_usage_mb()
    lgb_path = args.output_dir / "lightgbm_nfton_in_domain.txt"
    lgb_model.booster_.save_model(str(lgb_path))
    lgb_sha256 = compute_file_sha256(lgb_path)

    print(f"  LightGBM training completed in {lgb_duration:.2f}s")
    print(f"  Memory delta: {mem_after_lgb - mem_before_lgb:.2f} MB")
    print(f"  Saved artifact: {lgb_path} ({lgb_path.stat().st_size / 1024:.1f} KB, SHA256: {lgb_sha256[:16]}...)")

    # Save training metadata
    training_metadata = {
        "experiment": "ARGUS P1-1 NF-ToN-IoT-v2 In-Domain Supervised Baseline Training",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset": {
            "path": str(args.train_data),
            "sha256": train_sha256,
            "total_samples": total_samples,
            "benign_samples": benign_samples,
            "attack_samples": attack_samples,
            "attack_prevalence": attack_ratio,
            "features": FEATURES,
            "target": TARGET,
            "load_duration_seconds": load_duration,
        },
        "models": {
            "xgboost": {
                "class": "xgboost.XGBClassifier",
                "version": xgb.__version__,
                "artifact_path": str(xgb_path),
                "sha256": xgb_sha256,
                "hyperparameters": xgb_params,
                "training_duration_seconds": xgb_duration,
                "memory_delta_mb": mem_after_xgb - mem_before_xgb,
            },
            "lightgbm": {
                "class": "lightgbm.LGBMClassifier",
                "version": lgb.__version__,
                "artifact_path": str(lgb_path),
                "sha256": lgb_sha256,
                "hyperparameters": lgb_params,
                "training_duration_seconds": lgb_duration,
                "memory_delta_mb": mem_after_lgb - mem_before_lgb,
            },
        },
        "hardware": {
            "cpu_count": psutil.cpu_count(logical=True),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "total_ram_gb": psutil.virtual_memory().total / (1024**3),
        },
    }

    meta_path = args.output_dir / "training_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(training_metadata, f, indent=2)
    print(f"\nTraining metadata saved to {meta_path}")
    print("================================================================================")
    print("TRAINING SUCCESSFUL")
    print("================================================================================")


if __name__ == "__main__":
    main()
