import pytest
import numpy as np
from argus.monitoring.drift import analyze_batch_drift, DriftConfig

def test_analyze_batch_drift_normal():
    np.random.seed(42)
    reference = np.random.randn(100, 5)
    current = reference
    
    preds = np.zeros(100)
    confs = np.random.uniform(0.8, 1.0, 100)
    
    report = analyze_batch_drift(
        current_features=current,
        current_predictions=preds,
        current_confidences=confs,
        reference_features=reference,
        source_domain="D1",
        target_domain="D1"
    )
    
    assert report.warning_state == "NORMAL"
    assert report.feature_drift_score < 0.2
    assert report.source_domain == "D1"

def test_analyze_batch_drift_warning():
    np.random.seed(42)
    reference = np.random.randn(100, 5)
    # Introduce shift
    current = np.random.randn(50, 5) + 0.3 
    
    preds = np.zeros(100)
    confs = np.random.uniform(0.5, 0.7, 50)
    
    config = DriftConfig(feature_drift_threshold_warning=0.2)
    report = analyze_batch_drift(
        current_features=current,
        current_predictions=preds,
        current_confidences=confs,
        reference_features=reference,
        source_domain="D1",
        target_domain="D2",
        config=config
    )
    
    assert report.warning_state in ["WARNING", "CRITICAL"]
    assert report.feature_drift_score > 0.2
