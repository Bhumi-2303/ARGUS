from typing import Dict, Any
import matplotlib.pyplot as plt
import numpy as np
import os
try:
    import shap
except ImportError:
    shap = None
from lightgbm import LGBMClassifier, plot_importance

from training.trainers.base_trainer import BaseTrainer

class LightGBMTrainer(BaseTrainer):
    """Trainer for LightGBM models."""
    
    def initialize(self) -> None:
        self._logger.info("initializing_lightgbm")
        try:
            params = self.get_params()
            self._model = LGBMClassifier(**params)
        except ImportError:
            self._logger.error("lightgbm_not_installed")
            raise
        
    def train(self) -> None:
        self._logger.info("training_model")
        if self.X_train is not None and self.y_train is not None:
            eval_set = [(self.X_val, self.y_val)] if self.X_val is not None else None
            try:
                from lightgbm import early_stopping
                callbacks = [early_stopping(stopping_rounds=10, verbose=False)]
            except ImportError:
                callbacks = None
            
            self._model.fit(
                self.X_train, self.y_train,
                eval_set=eval_set,
                callbacks=callbacks
            )
            self._is_trained = True
            
    def evaluate(self) -> Dict[str, Any]:
        metrics = super().evaluate()
        self._logger.info("generating_tree_specific_graphs")
        
        graphs_dir = self._config.get("reporting.graphs_dir", "training/graphs/")
        os.makedirs(graphs_dir, exist_ok=True)
        
        # 1. Feature Importance
        plt.figure(figsize=(10, 6))
        plot_importance(self._model, max_num_features=20)
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, "lgb_feature_importance.png"))
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
            plt.savefig(os.path.join(graphs_dir, "lgb_shap_summary.png"))
            plt.close()
            
            # SHAP Bar Plot
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X_sample, feature_names=self.feature_names, plot_type="bar", show=False)
            plt.savefig(os.path.join(graphs_dir, "lgb_shap_bar.png"))
            plt.close()
            
        return metrics
