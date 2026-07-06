from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger

class BaseTrainer(ABC):
    """Abstract base class that all model trainers must implement."""
    
    def __init__(self, config: ConfigurationManager, logger=None):
        self._config = config
        self._logger = logger or get_logger(self.__class__.__name__)
        self._model = None
        self._is_trained = False
        self._metrics: Dict[str, Any] = {}
        
        # Data splits
        self.X_train: Optional[pd.DataFrame] = None
        self.X_val: Optional[pd.DataFrame] = None
        self.X_test: Optional[pd.DataFrame] = None
        self.y_train: Optional[pd.Series] = None
        self.y_val: Optional[pd.Series] = None
        self.y_test: Optional[pd.Series] = None

    @abstractmethod
    def initialize(self) -> None:
        """Loads config and sets up the model instance with parameters."""
        pass

    @abstractmethod
    def load_dataset(self) -> None:
        """Loads data using CSVLoader."""
        pass

    @abstractmethod
    def preprocess(self) -> None:
        """Preprocesses data using Preprocessor and sets data split attributes."""
        pass

    @abstractmethod
    def train(self) -> None:
        """Trains the model on the prepared data."""
        pass

    @abstractmethod
    def evaluate(self) -> Dict[str, Any]:
        """Evaluates the model and returns metrics."""
        pass

    @abstractmethod
    def export(self, output_path: str) -> str:
        """Exports the trained model to disk."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleans up resources and memory."""
        pass
        
    def run_pipeline(self) -> Dict[str, Any]:
        """Executes the complete training pipeline end-to-end."""
        self._logger.info("starting_training_pipeline", model=self.get_model_name())
        try:
            self.initialize()
            self.load_dataset()
            self.preprocess()
            self.train()
            self._metrics = self.evaluate()
            
            output_dir = self._config.get("export.output_dir", "training/exports/")
            import os
            os.makedirs(output_dir, exist_ok=True)
            self.export(f"{output_dir}/{self.get_model_name()}")
            
            return self._metrics
        except Exception as e:
            self._logger.error("training_pipeline_failed", error=str(e), exc_info=True)
            raise
        finally:
            self.shutdown()

    def get_model_name(self) -> str:
        """Returns the configured model name."""
        return self._config.get("model.name", "unknown_model")
        
    def get_params(self) -> Dict[str, Any]:
        """Returns the model parameters from config."""
        return self._config.get("parameters", {})
        
    @property
    def model(self) -> Any:
        return self._model
        
    @property
    def is_trained(self) -> bool:
        return self._is_trained
        
    @property
    def metrics(self) -> Dict[str, Any]:
        return self._metrics
