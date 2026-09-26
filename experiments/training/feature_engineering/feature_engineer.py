import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.feature_selection import mutual_info_classif

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger

class FeatureEngineer:
    """Handles creation of new features and basic statistical feature analysis."""

    def __init__(self, config: ConfigurationManager):
        self.config = config
        self.logger = get_logger(__name__)

    def compute_mutual_information(self, X: pd.DataFrame, y: pd.Series) -> pd.Series:
        """
        Computes mutual information between features and target.
        """
        self.logger.info("computing_mutual_information")
        # Ensure data is numeric
        X_num = X.select_dtypes(include=[np.number])
        if X_num.shape[1] == 0:
            self.logger.warning("no_numeric_features_for_mi")
            return pd.Series(dtype=float)
            
        mi_scores = mutual_info_classif(X_num, y, random_state=42)
        mi_series = pd.Series(mi_scores, index=X_num.columns).sort_values(ascending=False)
        return mi_series

    def compute_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes the Pearson correlation matrix for numeric features.
        """
        self.logger.info("computing_correlation_matrix")
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr(method='pearson')

    def remove_highly_correlated(self, df: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
        """
        Removes features that are highly correlated with each other.
        Keeps the first feature, drops subsequent correlated features.
        """
        self.logger.info("removing_highly_correlated_features", threshold=threshold)
        corr_matrix = self.compute_correlation_matrix(df).abs()
        
        # Upper triangle of correlation matrix
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Find features with correlation greater than threshold
        to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
        
        self.logger.debug("dropping_correlated_features", dropped_cols=to_drop)
        return df.drop(columns=to_drop)

    def create_interaction_features(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Creates multiplicative interaction features for the specified columns.
        """
        self.logger.info("creating_interaction_features", columns=columns)
        df_new = df.copy()
        
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                col1, col2 = columns[i], columns[j]
                if col1 in df_new.columns and col2 in df_new.columns:
                    new_col_name = f"{col1}_x_{col2}"
                    df_new[new_col_name] = df_new[col1] * df_new[col2]
                    
        return df_new

    def run_pipeline(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Executes the feature engineering pipeline based on config.
        """
        fe_config = self.config.get("feature_engineering", {})
        if not fe_config.get("enabled", False):
            self.logger.info("feature_engineering_disabled_skipping")
            return df
            
        self.logger.info("running_feature_engineering_pipeline")
        df_engineered = df.copy()
        
        # 1. Remove highly correlated
        threshold = fe_config.get("correlation_threshold", 0.95)
        if threshold and threshold < 1.0:
            df_engineered = self.remove_highly_correlated(df_engineered, threshold=threshold)
            
        # 2. Mutual Information (Mostly for reporting/logging, doesn't drop features here)
        if fe_config.get("mutual_information", True):
            if target_col in df_engineered.columns:
                X = df_engineered.drop(columns=[target_col])
                y = df_engineered[target_col]
                mi = self.compute_mutual_information(X, y)
                self.logger.debug("top_5_mi_features", features=mi.head(5).to_dict())
                
        # 3. Interactions
        if fe_config.get("create_interactions", False):
            # Example: Just take top 3 numeric cols to avoid explosion
            num_cols = df_engineered.select_dtypes(include=[np.number]).columns.tolist()
            num_cols = [c for c in num_cols if c != target_col][:3]
            df_engineered = self.create_interaction_features(df_engineered, num_cols)
            
        self.logger.info("feature_engineering_complete", 
                         original_cols=df.shape[1], 
                         new_cols=df_engineered.shape[1])
        return df_engineered
