from typing import Dict, Any
import matplotlib.pyplot as plt
import numpy as np
import os
try:
    import shap
except ImportError:
    shap = None
from xgboost import XGBClassifier, plot_importance

from training.trainers.base_trainer import BaseTrainer

class XGBoostTrainer(BaseTrainer):
    """Trainer for XGBoost models."""
    
    def initialize(self) -> None:
        self._logger.info("initializing_xgboost")
        try:
            params = self.get_params()
            # Handle potential param inconsistencies if any, but trust config
            self._model = XGBClassifier(**params)
        except ImportError:
            self._logger.error("xgboost_not_installed")
            raise
        
    def train(self) -> None:
        self._logger.info("training_model")
        if self.X_train is not None and self.y_train is not None:
            eval_set = [(self.X_val, self.y_val)] if self.X_val is not None else None
            # Extract verbosity
            verbose = self._config.get("parameters.verbosity", False)
            self._model.fit(
                self.X_train, self.y_train,
                eval_set=eval_set,
                verbose=verbose
            )
            self._is_trained = True
            
    def evaluate(self) -> Dict[str, Any]:
        metrics = super().evaluate()
        self._logger.info("generating_tree_specific_graphs")
        
        graphs_dir = self._config.get("reporting.graphs_dir", "training/graphs/")
        os.makedirs(graphs_dir, exist_ok=True)
        
        # 1. Feature Importance
        plt.figure(figsize=(10, 6))
        # plot_importance creates its own axes if ax is not provided, but it's cleaner to manage the figure
        plot_importance(self._model, max_num_features=20)
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, "xgb_feature_importance.png"))
        plt.close()
        
        # 2. SHAP
        if shap is not None:
            self._logger.info("generating_shap_plots")
            X_sample = self.X_train.sample(min(1000, len(self.X_train)), random_state=42)
            explainer = shap.TreeExplainer(self._model)
            shap_values = explainer.shap_values(X_sample)
            
            # SHAP Summary Plot
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X_sample, feature_names=self.feature_names, show=False)
            plt.savefig(os.path.join(graphs_dir, "xgb_shap_summary.png"))
            plt.close()
            
            # SHAP Bar Plot
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X_sample, feature_names=self.feature_names, plot_type="bar", show=False)
            plt.savefig(os.path.join(graphs_dir, "xgb_shap_bar.png"))
            plt.close()
            
        return metrics
