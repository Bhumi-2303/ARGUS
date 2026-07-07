from typing import Dict, Any

from training.trainers.base_trainer import BaseTrainer

class NeuralNetworkTrainer(BaseTrainer):
    """Trainer for sklearn MLPClassifier Neural Network models."""
    
    def initialize(self) -> None:
        self._logger.info("initializing_neural_network")
        try:
            from sklearn.neural_network import MLPClassifier
            
            params = self.get_params()
            self._model = MLPClassifier(**params)
        except ImportError:
            self._logger.error("sklearn_not_installed")
            raise
        
    def train(self) -> None:
        self._logger.info("training_model")
        if self.X_train is not None and self.y_train is not None:
            self._model.fit(self.X_train, self.y_train)
            self._is_trained = True
            
    def evaluate(self) -> Dict[str, Any]:
        metrics = super().evaluate()
        self._logger.info("generating_learning_curves")
        
        if hasattr(self._model, 'loss_curve_'):
            import matplotlib.pyplot as plt
            import os
            
            graphs_dir = self._config.get("reporting.graphs_dir", "training/graphs/")
            os.makedirs(graphs_dir, exist_ok=True)
            
            # Loss curve
            plt.figure(figsize=(10, 6))
            plt.plot(self._model.loss_curve_, label='Train Loss')
            plt.title('Neural Network Loss Curve')
            plt.xlabel('Epochs')
            plt.ylabel('Loss')
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(graphs_dir, "nn_loss_curve.png"))
            plt.close()
            
            # Validation curve if available
            if hasattr(self._model, 'validation_scores_') and self._model.validation_scores_ is not None:
                plt.figure(figsize=(10, 6))
                plt.plot(self._model.validation_scores_, label='Validation Score')
                plt.title('Neural Network Validation Score Curve')
                plt.xlabel('Epochs')
                plt.ylabel('Score (Accuracy)')
                plt.legend()
                plt.tight_layout()
                plt.savefig(os.path.join(graphs_dir, "nn_val_score_curve.png"))
                plt.close()
                
        return metrics
