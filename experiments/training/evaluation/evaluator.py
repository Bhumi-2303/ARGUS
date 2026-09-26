import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger

class Evaluator:
    """Evaluates ML model performance using standard metrics."""
    
    def __init__(self, config: ConfigurationManager):
        self.config = config
        self.logger = get_logger(__name__)

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray, y_proba: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Calculates configured metrics."""
        self.logger.info("evaluating_model")
        metrics_config = self.config.get("evaluation.metrics", ["accuracy", "f1_score"])
        results = {}
        
        if "accuracy" in metrics_config:
            results["accuracy"] = float(accuracy_score(y_true, y_pred))
            
        if "precision" in metrics_config:
            # Using macro for multi-class support by default
            results["precision"] = float(precision_score(y_true, y_pred, average='macro', zero_division=0))
            
        if "recall" in metrics_config:
            results["recall"] = float(recall_score(y_true, y_pred, average='macro', zero_division=0))
            
        if "f1_score" in metrics_config:
            results["f1_score"] = float(f1_score(y_true, y_pred, average='macro', zero_division=0))
            
        if "auc_roc" in metrics_config and y_proba is not None:
            try:
                # Handle multi-class with ovr if needed
                if len(np.unique(y_true)) > 2:
                    results["auc_roc"] = float(roc_auc_score(y_true, y_proba, multi_class='ovr'))
                else:
                    results["auc_roc"] = float(roc_auc_score(y_true, y_proba[:, 1] if len(y_proba.shape) > 1 else y_proba))
            except Exception as e:
                self.logger.warning("auc_roc_failed", error=str(e))
                
        if "confusion_matrix" in metrics_config:
            cm = confusion_matrix(y_true, y_pred)
            results["confusion_matrix"] = cm.tolist()
            
        self.logger.debug("evaluation_complete", results=results)
        return results

    def cross_validate(self, model: Any, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> Dict[str, Any]:
        """Performs cross-validation."""
        self.logger.info("running_cross_validation", cv=cv)
        # Note: Actual CV implementation would use sklearn.model_selection.cross_validate
        # This is the framework scaffolding
        return {"mean_f1": 0.0, "std_f1": 0.0}

    def per_class_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, class_names: Optional[list] = None) -> Dict[str, Any]:
        """Calculates metrics for each class."""
        self.logger.info("calculating_per_class_metrics")
        report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
        return report

    def generate_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Generates a raw numpy confusion matrix."""
        return confusion_matrix(y_true, y_pred)

    def summary(self, metrics: Dict[str, Any]) -> str:
        """Returns a human-readable summary of the metrics."""
        lines = ["Model Evaluation Summary:", "-" * 25]
        for k, v in metrics.items():
            if k != "confusion_matrix":
                lines.append(f"{k}: {v:.4f}")
        return "\n".join(lines)
