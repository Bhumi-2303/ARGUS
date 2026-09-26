"""
Domain Evaluation Module for ARGUS Domain Adaptation Experiments.

Evaluates whether learned feature representations are domain-invariant by
training a post-hoc domain classifier on extracted features. If the domain
classifier achieves AUC ≈ 0.5, the representations are domain-invariant.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    roc_auc_score, accuracy_score, f1_score,
    balanced_accuracy_score, precision_recall_curve, auc
)
from sklearn.model_selection import StratifiedKFold


def evaluate_domain_invariance(
    source_features: np.ndarray,
    target_features: np.ndarray,
    n_splits: int = 5,
    random_seed: int = 42,
) -> Dict[str, float]:
    """
    Evaluates domain invariance by training a classifier to distinguish
    source vs target feature representations.

    If the classifier achieves AUC ≈ 0.5, the features are domain-invariant
    (it can't tell which dataset a sample came from).

    Args:
        source_features: Feature representations from source domain. Shape (n_source, d).
        target_features: Feature representations from target domain. Shape (n_target, d).
        n_splits: Number of cross-validation folds.
        random_seed: Random seed for reproducibility.

    Returns:
        Dict with domain_auc, domain_accuracy, and per-fold scores.
    """
    print("[*] Evaluating domain invariance (post-hoc domain classifier)...")

    # Create domain labels: source=0, target=1
    X = np.vstack([source_features, target_features])
    y = np.concatenate([
        np.zeros(len(source_features)),
        np.ones(len(target_features))
    ])

    # Shuffle
    rng = np.random.RandomState(random_seed)
    shuffle_idx = rng.permutation(len(X))
    X = X[shuffle_idx]
    y = y[shuffle_idx]

    # Cross-validated domain classification
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_seed)
    fold_aucs = []
    fold_accs = []

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        clf = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation='relu',
            solver='adam',
            max_iter=100,
            early_stopping=True,
            n_iter_no_change=10,
            random_state=random_seed + fold_idx,
            verbose=False,
        )
        clf.fit(X_train, y_train)

        y_prob = clf.predict_proba(X_test)[:, 1]
        y_pred = clf.predict(X_test)

        fold_auc = roc_auc_score(y_test, y_prob)
        fold_acc = accuracy_score(y_test, y_pred)
        fold_aucs.append(fold_auc)
        fold_accs.append(fold_acc)

        print(f"    Fold {fold_idx + 1}/{n_splits}: Domain AUC={fold_auc:.4f}, Acc={fold_acc:.4f}")

    mean_auc = float(np.mean(fold_aucs))
    std_auc = float(np.std(fold_aucs))
    mean_acc = float(np.mean(fold_accs))

    # Interpret results
    if mean_auc < 0.55:
        verdict = "EXCELLENT - Features are domain-invariant (AUC ≈ 0.5)"
    elif mean_auc < 0.65:
        verdict = "GOOD - Moderate domain invariance achieved"
    elif mean_auc < 0.75:
        verdict = "PARTIAL - Some domain-specific information remains"
    else:
        verdict = "POOR - Features are still domain-specific (AUC > 0.75)"

    print(f"[*] Domain Classifier AUC: {mean_auc:.4f} ± {std_auc:.4f}")
    print(f"[*] Verdict: {verdict}")

    return {
        "domain_auc_mean": mean_auc,
        "domain_auc_std": std_auc,
        "domain_accuracy_mean": mean_acc,
        "fold_aucs": fold_aucs,
        "fold_accs": fold_accs,
        "verdict": verdict,
    }


def track_domain_auc_over_epochs(
    dann_trainer,
    source_X: np.ndarray,
    target_X: np.ndarray,
    epoch_indices: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Evaluates domain classifier AUC at multiple checkpoints during DANN training.
    This is called after training with saved checkpoints.

    Args:
        dann_trainer: A trained DANNTrainer instance with extract_features method.
        source_X: Source domain samples.
        target_X: Target domain samples.
        epoch_indices: Which epochs to evaluate (if checkpoints available).

    Returns:
        Dict with epoch-wise domain AUC values.
    """
    print("[*] Computing domain AUC on final model representations...")

    source_features = dann_trainer.extract_features(source_X)
    target_features = dann_trainer.extract_features(target_X)

    result = evaluate_domain_invariance(
        source_features, target_features,
        n_splits=3,  # Faster for per-epoch tracking
    )

    return result


def evaluate_task_performance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """
    Evaluates task (threat detection) performance with the full metric suite.

    Args:
        y_true: Ground truth binary labels.
        y_pred: Predicted binary labels.
        y_prob: Predicted probabilities for the positive class.

    Returns:
        Dict with F1, Balanced_Accuracy, ROC_AUC, PR_AUC, Kappa.
    """
    from sklearn.metrics import (
        cohen_kappa_score, matthews_corrcoef
    )

    metrics = {
        "F1": float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
        "Balanced_Accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "Accuracy": float(accuracy_score(y_true, y_pred)),
        "MCC": float(matthews_corrcoef(y_true, y_pred)),
        "Kappa": float(cohen_kappa_score(y_true, y_pred)),
    }

    if y_prob is not None:
        try:
            metrics["ROC_AUC"] = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            metrics["ROC_AUC"] = 0.0

        try:
            precision_vals, recall_vals, _ = precision_recall_curve(y_true, y_prob)
            metrics["PR_AUC"] = float(auc(recall_vals, precision_vals))
        except ValueError:
            metrics["PR_AUC"] = 0.0
    else:
        metrics["ROC_AUC"] = 0.0
        metrics["PR_AUC"] = 0.0

    return metrics


def compute_generalization_drop(
    intra_metrics: Dict[str, float],
    cross_metrics: Dict[str, float],
) -> Dict[str, float]:
    """
    Computes the generalization drop between intra-dataset and cross-dataset performance.

    A lower drop indicates better domain generalization.

    Args:
        intra_metrics: Metrics when training and testing on the same dataset.
        cross_metrics: Metrics when training on source and testing on target.

    Returns:
        Dict with absolute and relative drops for each metric.
    """
    drop = {}
    for key in ["F1", "Balanced_Accuracy", "ROC_AUC", "PR_AUC", "Kappa"]:
        intra_val = intra_metrics.get(key, 0.0)
        cross_val = cross_metrics.get(key, 0.0)
        abs_drop = intra_val - cross_val
        rel_drop = abs_drop / intra_val if intra_val > 0 else 0.0
        drop[f"{key}_absolute_drop"] = float(abs_drop)
        drop[f"{key}_relative_drop_pct"] = float(rel_drop * 100)

    return drop
