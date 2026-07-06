import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import uuid

from training.utils.logger import get_logger

class ExperimentTracker:
    """Tracks machine learning experiments, logging parameters, metrics, and artifacts."""
    
    def __init__(self, log_dir: str = "training/logs/experiments/"):
        """Initializes the experiment tracker."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
        self.current_experiment: Optional[Dict[str, Any]] = None
        
    def start_experiment(self, model_name: str) -> str:
        """Starts a new experiment and returns its ID."""
        experiment_id = str(uuid.uuid4())
        self.current_experiment = {
            "experiment_id": experiment_id,
            "model_name": model_name,
            "start_time": datetime.utcnow().isoformat(),
            "status": "running",
            "parameters": {},
            "metrics": {},
            "artifacts": []
        }
        self.logger.info("experiment_started", experiment_id=experiment_id, model_name=model_name)
        return experiment_id
        
    def log_params(self, params: Dict[str, Any]) -> None:
        """Logs hyperparameters for the current experiment."""
        if not self.current_experiment:
            raise RuntimeError("No active experiment. Call start_experiment() first.")
        self.current_experiment["parameters"].update(params)
        
    def log_metrics(self, metrics: Dict[str, float]) -> None:
        """Logs evaluation metrics for the current experiment."""
        if not self.current_experiment:
            raise RuntimeError("No active experiment. Call start_experiment() first.")
        self.current_experiment["metrics"].update(metrics)
        
    def log_artifact(self, artifact_path: str) -> None:
        """Logs a file artifact (e.g., model file, graph) path."""
        if not self.current_experiment:
            raise RuntimeError("No active experiment. Call start_experiment() first.")
        self.current_experiment["artifacts"].append(artifact_path)
        
    def end_experiment(self, status: str = "completed") -> None:
        """Ends the current experiment and saves the log to disk."""
        if not self.current_experiment:
            return
            
        self.current_experiment["end_time"] = datetime.utcnow().isoformat()
        self.current_experiment["status"] = status
        
        # Calculate duration
        start = datetime.fromisoformat(self.current_experiment["start_time"])
        end = datetime.fromisoformat(self.current_experiment["end_time"])
        self.current_experiment["duration_seconds"] = (end - start).total_seconds()
        
        # Save to JSON
        experiment_id = self.current_experiment["experiment_id"]
        log_file = self.log_dir / f"{experiment_id}.json"
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.current_experiment, f, indent=4)
            
        self.logger.info("experiment_ended", experiment_id=experiment_id, status=status, log_file=str(log_file))
        self.current_experiment = None
