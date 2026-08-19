#!/usr/bin/env python3
"""
ARGUS Domain Adaptation Experiment Pipeline.

Runs 4 experiments to evaluate cross-dataset generalization:
  Exp 1: Baseline (no adaptation) — zero-padded raw features, XGBoost/LightGBM
  Exp 2: Aligned Baseline — UFS-mapped features, XGBoost/LightGBM
  Exp 3: DANN — UFS-mapped features, Domain-Adversarial Neural Network
  Exp 4: Comparison — all metrics side by side

Usage:
  python training/scripts/domain_adaptation_experiment.py \\
    --source nftoniotv2 --target ciciot2023 --trials 50

  python training/scripts/domain_adaptation_experiment.py \\
    --source nftoniotv2 --target ciciot2023 --dry-run
"""
import os
import sys
import gc
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Experiment Helpers ──────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="ARGUS Domain Adaptation Experiment Pipeline"
    )
    parser.add_argument(
        "--source", type=str, required=True,
        help="Source dataset name (e.g., nftoniotv2)"
    )
    parser.add_argument(
        "--target", type=str, required=True,
        help="Target dataset name (e.g., ciciot2023)"
    )
    parser.add_argument(
        "--trials", type=int, default=50,
        help="Number of Optuna trials for baseline tuning"
    )
    parser.add_argument(
        "--dann-epochs", type=int, default=100,
        help="DANN training epochs"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate pipeline without training"
    )
    parser.add_argument(
        "--skip-baseline", action="store_true",
        help="Skip Exp 1 (baseline) if already run"
    )
    parser.add_argument(
        "--skip-aligned", action="store_true",
        help="Skip Exp 2 (aligned baseline) if already run"
    )
    parser.add_argument(
        "--skip-dann", action="store_true",
        help="Skip Exp 3 (DANN) if already run"
    )
    return parser.parse_args()


def load_config() -> dict:
    """Load domain adaptation config."""
    config_path = Path("training/configs/domain_adaptation.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    else:
        print("[!] Warning: domain_adaptation.yaml not found, using defaults.")
        return {
            "dann": {
                "feature_extractor": {"hidden_dims": [128, 64], "dropout": 0.3},
                "label_classifier": {"hidden_dims": [32]},
                "domain_classifier": {"hidden_dims": [32]},
                "training": {
                    "epochs": 100, "batch_size": 256, "lr": 0.001,
                    "weight_decay": 0.0001, "lambda_schedule": "ganin",
                    "patience": 15, "min_delta": 0.001,
                },
            },
            "experiments": {
                "max_rows_per_dataset": 500000,
                "baseline_models": ["xgboost", "lightgbm"],
                "random_seed": 42,
            },
        }


def setup_directories(source: str, target: str) -> Dict[str, Path]:
    """Create output directories for the experiment."""
    exp_dir = Path(f"training/exports/domain_adaptation/{source}_to_{target}")
    dirs = {
        "root": exp_dir,
        "exp1_baseline": exp_dir / "exp1_baseline",
        "exp2_aligned": exp_dir / "exp2_aligned",
        "exp3_dann": exp_dir / "exp3_dann",
        "exp4_comparison": exp_dir / "exp4_comparison",
        "figures": exp_dir / "figures",
        "models": exp_dir / "models",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def load_processed_data(dataset: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load preprocessed train/val/test splits."""
    data_dir = Path(f"training/data/processed/{dataset}")
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Processed data for '{dataset}' not found at {data_dir}. "
            f"Run preprocessing first."
        )

    train_df = pd.read_parquet(data_dir / "training.parquet")
    val_df = pd.read_parquet(data_dir / "validation.parquet")
    test_df = pd.read_parquet(data_dir / "testing.parquet")

    print(f"[*] Loaded {dataset}: train={train_df.shape}, val={val_df.shape}, test={test_df.shape}")
    return train_df, val_df, test_df


def split_xy(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Split DataFrame into features and target."""
    target_col = "Label"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found. Columns: {list(df.columns)}")
    df = df.reset_index(drop=True)
    y = df[target_col].astype(int)
    X = df.drop(columns=[target_col])
    return X, y


def zero_pad_align(source_X: pd.DataFrame, target_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Align target features to source features using zero-padding.
    This is the naive baseline approach.
    """
    target_df = target_df.reset_index(drop=True)
    source_features = list(source_X.columns)
    target_y = target_df["Label"].astype(int) if "Label" in target_df.columns else pd.Series(np.zeros(len(target_df)))
    
    target_X_dict = {}
    for col in source_features:
        if col in target_df.columns:
            target_X_dict[col] = target_df[col].values
        else:
            target_X_dict[col] = np.zeros(len(target_df), dtype=np.float32)

    target_X = pd.DataFrame(target_X_dict)
    return target_X, target_y


# ── Experiment 1: Baseline (No Adaptation) ─────────────────────────────────


def run_experiment_1(
    source_train: pd.DataFrame,
    source_val: pd.DataFrame,
    target_test: pd.DataFrame,
    trials: int,
    dirs: Dict[str, Path],
    config: dict,
) -> Dict[str, Dict[str, float]]:
    """
    Experiment 1: Baseline with zero-padded features.
    Train XGBoost/LightGBM on source, evaluate on zero-padded target.
    """
    print("\n" + "=" * 60)
    print("  EXPERIMENT 1: Baseline (Zero-Padded, No Adaptation)")
    print("=" * 60)

    from training.evaluation.domain_eval import evaluate_task_performance

    source_X_train, source_y_train = split_xy(source_train)
    source_X_val, source_y_val = split_xy(source_val)
    target_X_test, target_y_test = zero_pad_align(source_X_train, target_test)

    results = {}
    models_to_run = config.get("experiments", {}).get("baseline_models", ["xgboost", "lightgbm"])

    for model_name in models_to_run:
        print(f"\n[*] --- Exp 1: {model_name} (zero-padded) ---")

        model = _get_baseline_model(model_name, config)

        start = time.time()
        model.fit(source_X_train, source_y_train)
        train_time = time.time() - start

        y_pred = model.predict(target_X_test)
        if hasattr(model, "predict_proba"):
            raw_prob = model.predict_proba(target_X_test)
            y_prob = raw_prob[:, 1] if raw_prob.ndim > 1 and raw_prob.shape[1] > 1 else raw_prob.ravel()
        else:
            y_prob = None
        infer_time = time.time() - start

        metrics = evaluate_task_performance(
            target_y_test.values, y_pred, y_prob
        )
        metrics["Training_Time_s"] = train_time
        metrics["Inference_Time_s"] = infer_time

        results[model_name] = metrics
        print(f"    F1={metrics['F1']:.4f}  ROC_AUC={metrics['ROC_AUC']:.4f}  "
              f"Balanced_Acc={metrics['Balanced_Accuracy']:.4f}")

    # Save results
    with open(dirs["exp1_baseline"] / "metrics.json", "w") as f:
        json.dump(results, f, indent=4)

    print(f"\n[*] Exp 1 results saved to {dirs['exp1_baseline']}")
    return results


# ── Experiment 2: Aligned Baseline ──────────────────────────────────────────


def run_experiment_2(
    source_raw_train: pd.DataFrame,
    source_raw_val: pd.DataFrame,
    target_raw_test: pd.DataFrame,
    source_name: str,
    target_name: str,
    trials: int,
    dirs: Dict[str, Path],
    config: dict,
) -> Dict[str, Dict[str, float]]:
    """
    Experiment 2: Aligned baseline using Unified Feature Schema.
    Train XGBoost/LightGBM on UFS-aligned source, evaluate on UFS-aligned target.
    """
    print("\n" + "=" * 60)
    print("  EXPERIMENT 2: Aligned Baseline (Unified Feature Schema)")
    print("=" * 60)

    from training.feature_engineering.feature_aligner import FeatureAligner
    from training.evaluation.domain_eval import evaluate_task_performance, evaluate_domain_invariance

    aligner = FeatureAligner()

    # Align datasets
    print(f"[*] Aligning {source_name} to UFS...")
    source_train_aligned = aligner.align_dataset(source_raw_train.copy(), source_name)
    source_val_aligned = aligner.align_dataset(source_raw_val.copy(), source_name)

    print(f"[*] Aligning {target_name} to UFS...")
    target_test_aligned = aligner.align_dataset(target_raw_test.copy(), target_name)

    # Split X/y
    source_X_train, source_y_train = split_xy(source_train_aligned)
    source_X_val, source_y_val = split_xy(source_val_aligned)
    target_X_test, target_y_test = split_xy(target_test_aligned)

    # Scale aligned features (fit on source train only)
    scaler = StandardScaler()
    feature_cols = list(source_X_train.columns)
    source_X_train[feature_cols] = scaler.fit_transform(source_X_train[feature_cols])
    source_X_val[feature_cols] = scaler.transform(source_X_val[feature_cols])
    target_X_test[feature_cols] = scaler.transform(target_X_test[feature_cols])

    results = {}
    models_to_run = config.get("experiments", {}).get("baseline_models", ["xgboost", "lightgbm"])

    for model_name in models_to_run:
        print(f"\n[*] --- Exp 2: {model_name} (aligned) ---")

        model = _get_baseline_model(model_name, config)

        start = time.time()
        model.fit(source_X_train, source_y_train)
        train_time = time.time() - start

        start = time.time()
        y_pred = model.predict(target_X_test)
        if hasattr(model, "predict_proba"):
            raw_prob = model.predict_proba(target_X_test)
            y_prob = raw_prob[:, 1] if raw_prob.ndim > 1 and raw_prob.shape[1] > 1 else raw_prob.ravel()
        else:
            y_prob = None
        infer_time = time.time() - start

        metrics = evaluate_task_performance(
            target_y_test.values, y_pred, y_prob
        )
        metrics["Training_Time_s"] = train_time
        metrics["Inference_Time_s"] = infer_time

        results[model_name] = metrics
        print(f"    F1={metrics['F1']:.4f}  ROC_AUC={metrics['ROC_AUC']:.4f}  "
              f"Balanced_Acc={metrics['Balanced_Accuracy']:.4f}")

    # Domain invariance check on raw aligned features
    print("\n[*] Domain invariance check on raw aligned features...")
    domain_result = evaluate_domain_invariance(
        source_X_train.values, target_X_test.values,
        n_splits=3,
    )
    results["_domain_invariance"] = domain_result

    # Save
    with open(dirs["exp2_aligned"] / "metrics.json", "w") as f:
        json.dump(results, f, indent=4, default=_json_serializer)

    print(f"\n[*] Exp 2 results saved to {dirs['exp2_aligned']}")
    return results


# ── Experiment 3: DANN ───────────────────────────────────────────────────────


def run_experiment_3(
    source_raw_train: pd.DataFrame,
    source_raw_val: pd.DataFrame,
    target_raw_train: pd.DataFrame,
    target_raw_test: pd.DataFrame,
    source_name: str,
    target_name: str,
    dirs: Dict[str, Path],
    config: dict,
) -> Dict[str, Dict[str, Any]]:
    """
    Experiment 3: Domain-Adversarial Neural Network.
    Train DANN on UFS-aligned source (labeled) + target (unlabeled for task).
    """
    print("\n" + "=" * 60)
    print("  EXPERIMENT 3: Domain-Adversarial Neural Network (DANN)")
    print("=" * 60)

    from training.feature_engineering.feature_aligner import FeatureAligner
    from training.trainers.dann_model import DANNTrainer
    from training.evaluation.domain_eval import (
        evaluate_task_performance, evaluate_domain_invariance
    )

    aligner = FeatureAligner()

    # Align all datasets
    print(f"[*] Aligning datasets to UFS...")
    source_train_aligned = aligner.align_dataset(source_raw_train.copy(), source_name)
    source_val_aligned = aligner.align_dataset(source_raw_val.copy(), source_name)
    target_train_aligned = aligner.align_dataset(target_raw_train.copy(), target_name)
    target_test_aligned = aligner.align_dataset(target_raw_test.copy(), target_name)

    # Split X/y
    source_X_train, source_y_train = split_xy(source_train_aligned)
    source_X_val, source_y_val = split_xy(source_val_aligned)
    target_X_train, _ = split_xy(target_train_aligned)
    target_X_test, target_y_test = split_xy(target_test_aligned)

    # Scale (fit on source train)
    scaler = StandardScaler()
    feature_cols = list(source_X_train.columns)
    source_X_train_scaled = pd.DataFrame(
        scaler.fit_transform(source_X_train[feature_cols]),
        columns=feature_cols, index=source_X_train.index
    )
    source_X_val_scaled = pd.DataFrame(
        scaler.transform(source_X_val[feature_cols]),
        columns=feature_cols, index=source_X_val.index
    )
    target_X_train_scaled = pd.DataFrame(
        scaler.transform(target_X_train[feature_cols]),
        columns=feature_cols, index=target_X_train.index
    )
    target_X_test_scaled = pd.DataFrame(
        scaler.transform(target_X_test[feature_cols]),
        columns=feature_cols, index=target_X_test.index
    )

    # Configure DANN
    dann_config = config.get("dann", {})
    dann_config.setdefault("training", {})
    dann_config["training"].setdefault("epochs", 100)

    trainer = DANNTrainer(
        input_dim=len(feature_cols),
        config=dann_config,
    )

    # Subsample training sets for fast CPU training if large
    max_dann_samples = config.get("experiments", {}).get("max_dann_samples", 50000)
    seed = config.get("experiments", {}).get("random_seed", 42)
    rng = np.random.RandomState(seed)

    s_train_x = source_X_train_scaled.values
    s_train_y = source_y_train.values
    t_train_x = target_X_train_scaled.values

    if len(s_train_x) > max_dann_samples:
        s_idx = rng.choice(len(s_train_x), max_dann_samples, replace=False)
        s_train_x = s_train_x[s_idx]
        s_train_y = s_train_y[s_idx]

    if len(t_train_x) > max_dann_samples:
        t_idx = rng.choice(len(t_train_x), max_dann_samples, replace=False)
        t_train_x = t_train_x[t_idx]

    print(f"[*] DANN Training Samples: source={len(s_train_x)}, target={len(t_train_x)}")

    # Train DANN
    print("[*] Training DANN...")
    history = trainer.train(
        source_X=s_train_x,
        source_y=s_train_y,
        target_X=t_train_x,
        source_val_X=source_X_val_scaled.values[:10000],
        source_val_y=source_y_val.values[:10000],
        target_val_X=target_X_test_scaled.values[:10000],
    )

    # Save model
    trainer.save(str(dirs["models"] / "dann_model.pt"))

    # Evaluate on target test set
    print("[*] Evaluating DANN on target test set...")
    y_pred = trainer.predict(target_X_test_scaled.values)
    y_prob = trainer.predict_proba(target_X_test_scaled.values)

    task_metrics = evaluate_task_performance(
        target_y_test.values, y_pred, y_prob
    )
    print(f"    F1={task_metrics['F1']:.4f}  ROC_AUC={task_metrics['ROC_AUC']:.4f}  "
          f"Balanced_Acc={task_metrics['Balanced_Accuracy']:.4f}")

    # Domain invariance evaluation
    print("[*] Evaluating domain invariance on DANN representations...")
    source_features = trainer.extract_features(source_X_train_scaled.values[:5000])
    target_features = trainer.extract_features(target_X_test_scaled.values[:5000])

    domain_result = evaluate_domain_invariance(
        source_features, target_features,
        n_splits=3,
    )

    results = {
        "DANN": {
            **task_metrics,
            "domain_auc": domain_result["domain_auc_mean"],
            "domain_auc_std": domain_result["domain_auc_std"],
            "domain_verdict": domain_result["verdict"],
        },
        "_training_history": {
            "final_label_loss": history.get("label_losses", [0])[-1] if history.get("label_losses") else 0,
            "final_domain_loss": history.get("domain_losses", [0])[-1] if history.get("domain_losses") else 0,
            "epochs_trained": len(history.get("label_losses", [])),
        },
        "_domain_invariance": domain_result,
    }

    # Save training history for plotting
    if history:
        history_serializable = {}
        for k, v in history.items():
            if isinstance(v, list):
                history_serializable[k] = [float(x) if isinstance(x, (np.floating, float)) else x for x in v]
            else:
                history_serializable[k] = v
        with open(dirs["exp3_dann"] / "training_history.json", "w") as f:
            json.dump(history_serializable, f, indent=4, default=_json_serializer)

    # Save metrics
    with open(dirs["exp3_dann"] / "metrics.json", "w") as f:
        json.dump(results, f, indent=4, default=_json_serializer)

    # Save extracted features for t-SNE visualization
    np.save(dirs["exp3_dann"] / "source_features.npy", source_features)
    np.save(dirs["exp3_dann"] / "target_features.npy", target_features)

    print(f"\n[*] Exp 3 results saved to {dirs['exp3_dann']}")
    return results


# ── Experiment 4: Comparison ─────────────────────────────────────────────────


def run_experiment_4(
    exp1_results: Optional[Dict],
    exp2_results: Optional[Dict],
    exp3_results: Optional[Dict],
    source_name: str,
    target_name: str,
    dirs: Dict[str, Path],
) -> pd.DataFrame:
    """
    Experiment 4: Compare all approaches side by side.
    """
    print("\n" + "=" * 60)
    print("  EXPERIMENT 4: Comparative Analysis")
    print("=" * 60)

    from training.evaluation.domain_eval import compute_generalization_drop

    rows = []

    # Exp 1 results
    if exp1_results:
        for model_name, metrics in exp1_results.items():
            if model_name.startswith("_"):
                continue
            rows.append({
                "Experiment": "Exp1_Baseline",
                "Model": model_name,
                "Approach": "Zero-Padded (No Adaptation)",
                **{k: v for k, v in metrics.items() if isinstance(v, (int, float))},
            })

    # Exp 2 results
    if exp2_results:
        for model_name, metrics in exp2_results.items():
            if model_name.startswith("_"):
                continue
            rows.append({
                "Experiment": "Exp2_Aligned",
                "Model": model_name,
                "Approach": "UFS-Aligned Features",
                **{k: v for k, v in metrics.items() if isinstance(v, (int, float))},
            })

    # Exp 3 results
    if exp3_results:
        for model_name, metrics in exp3_results.items():
            if model_name.startswith("_"):
                continue
            rows.append({
                "Experiment": "Exp3_DANN",
                "Model": model_name,
                "Approach": "Domain-Adversarial NN",
                **{k: v for k, v in metrics.items() if isinstance(v, (int, float))},
            })

    if not rows:
        print("[!] No experiment results to compare.")
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Print leaderboard
    display_cols = [c for c in ["Experiment", "Model", "F1", "ROC_AUC", "Balanced_Accuracy",
                                 "PR_AUC", "Kappa", "domain_auc"] if c in df.columns]
    print("\n[*] Leaderboard:")
    print(df[display_cols].to_string(index=False))

    # Best model
    if "F1" in df.columns:
        best_idx = df["F1"].idxmax()
        best = df.loc[best_idx]
        print(f"\n[*] Best overall: {best['Model']} ({best['Approach']}) with F1={best['F1']:.4f}")

    # Save
    df.to_csv(dirs["exp4_comparison"] / "comparison_table.csv", index=False)
    try:
        df.to_markdown(dirs["exp4_comparison"] / "comparison_table.md")
    except Exception:
        pass

    with open(dirs["exp4_comparison"] / "comparison.json", "w") as f:
        json.dump(rows, f, indent=4, default=_json_serializer)

    print(f"\n[*] Exp 4 results saved to {dirs['exp4_comparison']}")
    return df


# ── Utility Functions ────────────────────────────────────────────────────────


def _get_baseline_model(model_name: str, config: dict):
    """Instantiate a baseline tree model."""
    seed = config.get("experiments", {}).get("random_seed", 42)

    if model_name == "xgboost":
        import xgboost as xgb
        return xgb.XGBClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            n_jobs=-1, random_state=seed, use_label_encoder=False,
            eval_metric='logloss', verbosity=0,
        )
    elif model_name == "lightgbm":
        import lightgbm as lgb
        return lgb.LGBMClassifier(
            n_estimators=200, max_depth=-1, learning_rate=0.05,
            num_leaves=63, n_jobs=-1, random_state=seed, verbose=-1,
        )
    elif model_name == "random_forest":
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier(
            n_estimators=200, max_depth=20, n_jobs=-1, random_state=seed,
        )
    elif model_name == "catboost":
        from catboost import CatBoostClassifier
        return CatBoostClassifier(
            iterations=200, depth=8, learning_rate=0.05,
            random_seed=seed, verbose=0,
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")


def _json_serializer(obj):
    """JSON serializer for numpy types."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


def load_raw_data(dataset: str) -> pd.DataFrame:
    """Load raw data for a dataset (for UFS alignment before preprocessing)."""
    # Try processed data first (already split and cleaned)
    processed_dir = Path(f"training/data/processed/{dataset}")
    if processed_dir.exists():
        train_df = pd.read_parquet(processed_dir / "training.parquet")
        val_df = pd.read_parquet(processed_dir / "validation.parquet")
        test_df = pd.read_parquet(processed_dir / "testing.parquet")
        return train_df, val_df, test_df

    raise FileNotFoundError(
        f"No processed data for '{dataset}'. Run preprocessing first:\n"
        f"  python training/scripts/phase2_execute.py --dataset {dataset}\n"
        f"  or: python training/scripts/preprocess_ciciot.py"
    )


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    args = parse_args()
    source = args.source
    target = args.target

    print(f"\n{'=' * 60}")
    print(f"  ARGUS Domain Adaptation Experiment Pipeline")
    print(f"  Source: {source}  →  Target: {target}")
    print(f"  Time: {datetime.now().isoformat()}")
    print(f"{'=' * 60}")

    config = load_config()
    dirs = setup_directories(source, target)

    if args.dry_run:
        print("\n[*] DRY RUN — Validating pipeline components...")

        # Check data availability
        for ds in [source, target]:
            processed_dir = Path(f"training/data/processed/{ds}")
            if processed_dir.exists():
                print(f"  ✓ Processed data for {ds} found")
            else:
                print(f"  ✗ Processed data for {ds} NOT found")

        # Check imports
        try:
            from training.feature_engineering.feature_aligner import FeatureAligner
            print("  ✓ FeatureAligner importable")
        except ImportError as e:
            print(f"  ✗ FeatureAligner import failed: {e}")

        try:
            from training.trainers.dann_model import DANNTrainer
            print("  ✓ DANNTrainer importable")
        except ImportError as e:
            print(f"  ✗ DANNTrainer import failed: {e}")

        try:
            from training.evaluation.domain_eval import evaluate_domain_invariance
            print("  ✓ domain_eval importable")
        except ImportError as e:
            print(f"  ✗ domain_eval import failed: {e}")

        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"  ✓ PyTorch available (device: {device})")
        except ImportError:
            print("  ✗ PyTorch NOT installed — DANN will fail")

        print("\n[*] Dry run complete.")
        return

    # ── Load Data ────────────────────────────────────────────────────────

    print("\n[*] Loading processed datasets...")
    source_train, source_val, source_test = load_raw_data(source)
    target_train, target_val, target_test = load_raw_data(target)

    # ── Experiment 1: Baseline ───────────────────────────────────────────

    exp1_results = None
    if not args.skip_baseline:
        try:
            exp1_results = run_experiment_1(
                source_train, source_val, target_test,
                args.trials, dirs, config,
            )
        except Exception as e:
            print(f"[!] Experiment 1 failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Try loading previous results
        exp1_path = dirs["exp1_baseline"] / "metrics.json"
        if exp1_path.exists():
            with open(exp1_path) as f:
                exp1_results = json.load(f)
            print("[*] Loaded previous Exp 1 results.")

    gc.collect()

    # ── Experiment 2: Aligned Baseline ───────────────────────────────────

    exp2_results = None
    if not args.skip_aligned:
        try:
            exp2_results = run_experiment_2(
                source_train, source_val, target_test,
                source, target,
                args.trials, dirs, config,
            )
        except Exception as e:
            print(f"[!] Experiment 2 failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        exp2_path = dirs["exp2_aligned"] / "metrics.json"
        if exp2_path.exists():
            with open(exp2_path) as f:
                exp2_results = json.load(f)
            print("[*] Loaded previous Exp 2 results.")

    gc.collect()

    # ── Experiment 3: DANN ───────────────────────────────────────────────

    exp3_results = None
    if not args.skip_dann:
        try:
            exp3_results = run_experiment_3(
                source_train, source_val,
                target_train, target_test,
                source, target,
                dirs, config,
            )
        except Exception as e:
            print(f"[!] Experiment 3 failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        exp3_path = dirs["exp3_dann"] / "metrics.json"
        if exp3_path.exists():
            with open(exp3_path) as f:
                exp3_results = json.load(f)
            print("[*] Loaded previous Exp 3 results.")

    gc.collect()

    # ── Experiment 4: Comparison ─────────────────────────────────────────

    comparison_df = run_experiment_4(
        exp1_results, exp2_results, exp3_results,
        source, target, dirs,
    )

    # ── Generate Report ──────────────────────────────────────────────────

    print("\n[*] Generating domain adaptation report...")
    try:
        from training.scripts.domain_adaptation_report import generate_report
        generate_report(
            exp1_results, exp2_results, exp3_results,
            comparison_df, source, target, dirs,
        )
    except Exception as e:
        print(f"[!] Report generation failed: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'=' * 60}")
    print(f"  ARGUS Domain Adaptation Experiment Complete")
    print(f"  Results: {dirs['root']}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
