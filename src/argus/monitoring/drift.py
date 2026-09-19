import numpy as np
from typing import Dict, List, Any
from pydantic import BaseModel

class DriftConfig(BaseModel):
    feature_drift_threshold_warning: float = 0.2
    feature_drift_threshold_critical: float = 0.4
    confidence_drift_threshold: float = 0.15
    class_prior_threshold: float = 0.1

class DriftReport(BaseModel):
    source_domain: str
    target_domain: str
    feature_drift_score: float
    prediction_distribution: Dict[str, float]
    confidence_distribution: Dict[str, float]
    class_distribution: Dict[str, float]
    warning_state: str  # NORMAL, WARNING, CRITICAL
    reference_distribution: Dict[str, Any]
    current_distribution: Dict[str, Any]

def compute_jensen_shannon_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Compute JS divergence between two discrete probability distributions."""
    # Add epsilon to avoid division by zero / log(0)
    p = np.asarray(p, dtype=float) + 1e-10
    q = np.asarray(q, dtype=float) + 1e-10
    p /= p.sum()
    q /= q.sum()
    m = 0.5 * (p + q)
    # KL divergence P || M
    kl_pm = np.sum(p * np.log(p / m))
    # KL divergence Q || M
    kl_qm = np.sum(q * np.log(q / m))
    return 0.5 * (kl_pm + kl_qm)

def analyze_batch_drift(
    current_features: np.ndarray,
    current_predictions: np.ndarray,
    current_confidences: np.ndarray,
    reference_features: np.ndarray,
    source_domain: str,
    target_domain: str,
    config: DriftConfig = DriftConfig()
) -> DriftReport:
    """
    Lightweight batch analysis for drift monitoring.
    Does not require streaming infrastructure.
    """
    # 1. Feature Drift (simplified using mean shift divergence for lightweight monitoring)
    # In a full setup, this would be KS test or Wasserstein distance.
    ref_mean = np.mean(reference_features, axis=0)
    ref_std = np.std(reference_features, axis=0) + 1e-8
    cur_mean = np.mean(current_features, axis=0)
    
    # Calculate Z-score of mean shift as a basic drift score
    shift = np.abs(cur_mean - ref_mean) / ref_std
    feature_drift_score = float(np.max(shift))
    
    # 2. Prediction & Class Distribution
    total_samples = len(current_predictions)
    anomalies = np.sum(current_predictions > 0)
    class_dist = {
        "benign": float((total_samples - anomalies) / total_samples),
        "anomaly": float(anomalies / total_samples)
    }
    
    # 3. Confidence Distribution (histogram)
    hist, bin_edges = np.histogram(current_confidences, bins=[0.0, 0.5, 0.8, 0.95, 1.0])
    conf_dist = {
        f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}": float(count/total_samples) 
        for i, count in enumerate(hist)
    }
    
    # Determine warning state
    state = "NORMAL"
    if feature_drift_score > config.feature_drift_threshold_critical:
        state = "CRITICAL"
    elif feature_drift_score > config.feature_drift_threshold_warning:
        state = "WARNING"
        
    return DriftReport(
        source_domain=source_domain,
        target_domain=target_domain,
        feature_drift_score=feature_drift_score,
        prediction_distribution=class_dist,
        confidence_distribution=conf_dist,
        class_distribution=class_dist,
        warning_state=state,
        reference_distribution={"mean": ref_mean.tolist(), "std": ref_std.tolist()},
        current_distribution={"mean": cur_mean.tolist()}
    )
