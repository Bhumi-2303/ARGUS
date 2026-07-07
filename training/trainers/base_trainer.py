from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import gc
import os

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger
from training.data.csv_loader import CSVLoader
from training.data.dataset_inspector import DatasetInspector
from training.preprocessing.preprocessor import Preprocessor
from training.feature_engineering.feature_engineer import FeatureEngineer
from training.feature_selection.feature_selector import FeatureSelector
from training.evaluation.evaluator import Evaluator
from training.reports.report_generator import ReportGenerator
from training.exports.model_exporter import ModelExporter

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

    def load_dataset(self) -> None:
        """Loads data using CSVLoader."""
        self._logger.info("loading_dataset")
        dataset_path = self._config.get("dataset.raw_path")
        loader = CSVLoader(self._config)
        self._raw_df = loader.load(dataset_path)

    def preprocess(self) -> None:
        """Preprocesses data and sets data split attributes."""
        self._logger.info("preprocessing_data")
        target_col = self._config.get("dataset.target_column", "Label")
        
        # 1. Dataset Inspection & EDA
        inspector = DatasetInspector()
        profile_report = inspector.generate_profile_report(self._raw_df, target_col)
        reports_dir = self._config.get("reporting.output_dir", "training/reports/")
        os.makedirs(reports_dir, exist_ok=True)
        import json
        with open(os.path.join(reports_dir, "metadata.json"), "w") as f:
            json.dump(profile_report, f, indent=4)
        
        # 2. Preprocessing & Split
        preprocessor = Preprocessor(self._config)
        splits = preprocessor.run_pipeline(self._raw_df, target_col)
        
        # Free memory of raw_df immediately
        del self._raw_df
        gc.collect()
        
        # 3. Feature Engineering
        engineer = FeatureEngineer(self._config)
        splits["X_train"] = engineer.run_pipeline(splits["X_train"], target_col)
        # Apply same transformations to val/test
        splits["X_val"] = engineer.run_pipeline(splits["X_val"], target_col)
        splits["X_test"] = engineer.run_pipeline(splits["X_test"], target_col)
        
        # 4. Feature Selection
        selector = FeatureSelector(self._config)
        # We don't have estimator yet, fallback to all or basic correlation
        selected_features = selector.run_selection(splits["X_train"], splits["y_train"], estimator=None)
        self.feature_names = selected_features
        
        for k in ["X_train", "X_val", "X_test"]:
            splits[k] = splits[k][selected_features]
            
        self.X_train = splits["X_train"]
        self.X_val = splits["X_val"]
        self.X_test = splits["X_test"]
        self.y_train = splits["y_train"]
        self.y_val = splits["y_val"]
        self.y_test = splits["y_test"]

    @abstractmethod
    def train(self) -> None:
        """Trains the model on the prepared data."""
        pass

    def evaluate(self) -> Dict[str, Any]:
        """Evaluates the model and returns metrics."""
        self._logger.info("evaluating_model")
        evaluator = Evaluator(self._config)
        y_pred = self._model.predict(self.X_test)
        y_proba = None
        if hasattr(self._model, "predict_proba"):
            y_proba = self._model.predict_proba(self.X_test)
            
        metrics = evaluator.evaluate(self.y_test, y_pred, y_proba)
        
        # Generate reports and graphs
        reporter = ReportGenerator(self._config)
        reporter.generate_all(metrics, self.get_model_name())
        
        return metrics

    def export(self, output_path: str) -> str:
        """Exports the trained model to disk."""
        self._logger.info("exporting_model", path=output_path)
        exporter = ModelExporter(self._config)
        formats = self._config.get("export.formats", ["joblib"])
        results = exporter.export(
            model=self._model,
            model_name=self.get_model_name(),
            formats=formats,
            params=self.get_params(),
            metrics=self.metrics,
            feature_names=self.feature_names
        )
        return list(results.values())[0] if results else output_path

    def shutdown(self) -> None:
        """Cleans up resources and memory."""
        self._logger.info("shutting_down_trainer")
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        gc.collect()
        
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
