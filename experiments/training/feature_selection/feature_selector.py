import pandas as pd
import numpy as np
from typing import List, Optional
from sklearn.feature_selection import RFE, mutual_info_classif

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger

class FeatureSelector:
    """Handles feature selection to reduce dimensionality."""

    def __init__(self, config: ConfigurationManager):
        self.config = config
        self.logger = get_logger(__name__)

    def select_rfe(self, X: pd.DataFrame, y: pd.Series, estimator: Any, n_features: Optional[int] = None) -> List[str]:
        """
        Recursive Feature Elimination.
        """
        self.logger.info("running_rfe", n_features=n_features)
        selector = RFE(estimator, n_features_to_select=n_features, step=1)
        selector = selector.fit(X, y)
        selected_features = X.columns[selector.support_].tolist()
        return selected_features

    def select_shap(self, X: pd.DataFrame, y: pd.Series, model: Any, n_samples: int = 1000) -> List[str]:
        """
        Select features based on SHAP values.
        """
        self.logger.info("running_shap_selection")
        try:
            import shap
        except ImportError:
            self.logger.warning("shap_not_installed_falling_back_to_all_features")
            return X.columns.tolist()
            
        # Downsample for speed
        if len(X) > n_samples:
            X_sample = X.sample(n_samples, random_state=42)
        else:
            X_sample = X
            
        explainer = shap.Explainer(model, X_sample)
        shap_values = explainer(X_sample)
        
        # Calculate mean absolute shap values per feature
        vals = np.abs(shap_values.values).mean(0)
        feature_importance = pd.DataFrame(list(zip(X.columns, vals)), columns=['col_name', 'feature_importance_vals'])
        feature_importance.sort_values(by=['feature_importance_vals'], ascending=False, inplace=True)
        
        # Select features with > 0 importance
        selected = feature_importance[feature_importance['feature_importance_vals'] > 0]['col_name'].tolist()
        return selected

    def select_by_correlation(self, X: pd.DataFrame, y: pd.Series, threshold: float = 0.1) -> List[str]:
        """
        Select features that have at least `threshold` absolute correlation with the target.
        """
        self.logger.info("running_correlation_selection", threshold=threshold)
        # Assuming y is numeric for this to work well
        df = X.copy()
        target_name = y.name if y.name else 'target'
        df[target_name] = y
        
        corr = df.corr()[target_name].drop(target_name).abs()
        selected = corr[corr >= threshold].index.tolist()
        return selected

    def select_by_mutual_info(self, X: pd.DataFrame, y: pd.Series, n_features: int) -> List[str]:
        """
        Select top N features using mutual information.
        """
        self.logger.info("running_mutual_info_selection", n_features=n_features)
        mi_scores = mutual_info_classif(X, y, random_state=42)
        mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
        selected = mi_series.head(n_features).index.tolist()
        return selected

    def run_selection(self, X: pd.DataFrame, y: pd.Series, estimator: Optional[Any] = None) -> List[str]:
        """
        Executes selection based on config.
        """
        fs_config = self.config.get("feature_selection", {})
        if not fs_config.get("enabled", False):
            self.logger.info("feature_selection_disabled")
            return X.columns.tolist()
            
        method = fs_config.get("method", "rfe")
        n_features = fs_config.get("n_features", None)
        
        self.logger.info("running_feature_selection", method=method)
        
        try:
            if method == "rfe" and estimator:
                return self.select_rfe(X, y, estimator, n_features)
            elif method == "shap" and estimator:
                return self.select_shap(X, y, estimator, fs_config.get("shap_samples", 1000))
            elif method == "correlation":
                return self.select_by_correlation(X, y)
            elif method == "mutual_info" and n_features:
                return self.select_by_mutual_info(X, y, n_features)
            else:
                self.logger.warning("unsupported_or_invalid_selection_method_using_all", method=method)
                return X.columns.tolist()
        except Exception as e:
            self.logger.error("feature_selection_failed", error=str(e))
            return X.columns.tolist()
