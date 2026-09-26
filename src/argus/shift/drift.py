"""ARGUS Data Shift & Drift Analysis Module."""

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


def compute_ks_test(source_data: np.ndarray, target_data: np.ndarray) -> pd.DataFrame:
    """Computes Kolmogorov-Smirnov test statistic across features."""
    n_feats = source_data.shape[1]
    records = []
    for i in range(n_feats):
        stat, pval = ks_2samp(source_data[:, i], target_data[:, i])
        records.append({
            "feature_index": i,
            "ks_statistic": stat,
            "p_value": pval,
            "significant_shift": pval < 0.05
        })
    return pd.DataFrame(records)


def compute_psi(source_col: np.ndarray, target_col: np.ndarray, num_bins: int = 10) -> float:
    """Computes Population Stability Index (PSI) for a single feature."""
    bins = np.linspace(min(source_col.min(), target_col.min()), max(source_col.max(), target_col.max()), num_bins + 1)
    s_counts, _ = np.histogram(source_col, bins=bins)
    t_counts, _ = np.histogram(target_col, bins=bins)
    
    s_pct = np.where(s_counts == 0, 1e-4, s_counts) / len(source_col)
    t_pct = np.where(t_counts == 0, 1e-4, t_counts) / len(target_col)
    
    psi = np.sum((t_pct - s_pct) * np.log(t_pct / s_pct))
    return float(psi)
