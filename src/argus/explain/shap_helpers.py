"""ARGUS SHAP Explainability & Attribution Helpers."""

import numpy as np
import pandas as pd


def compute_shap_importance(model, X: pd.DataFrame) -> pd.DataFrame:
    """Computes mean absolute SHAP feature importance for tree models."""
    import shap
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X)
    
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]
        
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    df_imp = pd.DataFrame({
        "feature": X.columns,
        "mean_abs_shap": mean_abs_shap
    }).sort_values(by="mean_abs_shap", ascending=False)
    
    return df_imp
