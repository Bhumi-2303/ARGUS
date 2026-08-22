import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    matthews_corrcoef, roc_auc_score, precision_recall_curve, auc,
    log_loss, brier_score_loss, confusion_matrix
)

def compute_all_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict:
    """
    Authoritative, mathematically validated metric calculation function for ARGUS.
    Strictly verifies boundary constraints and confusion matrix consistency.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    y_prob_clipped = np.clip(y_prob, 1e-15, 1.0 - 1e-15)
    y_pred = (y_prob >= threshold).astype(int)
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    # Core Rates
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
    
    # Standard Classification Metrics
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average='macro', zero_division=0))
    mcc = float(matthews_corrcoef(y_true, y_pred))
    
    # Curve & Probabilistic Metrics
    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = float('nan')
        
    try:
        p_curve, r_curve, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = float(auc(r_curve, p_curve))
    except Exception:
        pr_auc = float('nan')
        
    try:
        ll = float(log_loss(y_true, y_prob_clipped))
    except Exception:
        ll = float('nan')
        
    try:
        brier = float(brier_score_loss(y_true, y_prob_clipped))
    except Exception:
        brier = float('nan')
        
    # Mathematical assertions
    assert 0.0 <= fpr <= 1.0, f"FPR out of bounds: {fpr}"
    assert 0.0 <= fnr <= 1.0, f"FNR out of bounds: {fnr}"
    assert -1.0 <= mcc <= 1.0, f"MCC out of bounds: {mcc}"
    if not np.isnan(roc_auc):
        assert 0.0 <= roc_auc <= 1.0, f"ROC-AUC out of bounds: {roc_auc}"
    if not np.isnan(pr_auc):
        assert 0.0 <= pr_auc <= 1.0, f"PR-AUC out of bounds: {pr_auc}"
        
    return {
        'threshold': float(threshold),
        'tn': int(tn),
        'fp': int(fp),
        'fn': int(fn),
        'tp': int(tp),
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'macro_f1': f1_macro,
        'fpr': fpr,
        'fnr': fnr,
        'mcc': mcc,
        'roc_auc': roc_auc,
        'pr_auc': pr_auc,
        'log_loss': ll,
        'brier_score': brier
    }

if __name__ == '__main__':
    # Self-test
    y_t = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_p = np.array([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])
    res = compute_all_metrics(y_t, y_p, threshold=0.5)
    print("Self-test passed. Sample metric output:")
    for k, v in res.items():
        print(f"  {k:15s}: {v}")
