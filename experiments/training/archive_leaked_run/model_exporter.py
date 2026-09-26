import os
import json
from pathlib import Path
from typing import Dict, Any, List

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger

class ModelExporter:
    """Exports trained models to various formats."""
    
    def __init__(self, config: ConfigurationManager):
        self.config = config
        self.logger = get_logger(__name__)
        self.output_dir = Path(self.config.get("export.output_dir", "training/exports/"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_joblib(self, model: Any, output_path: str) -> str:
        self.logger.info("exporting_model_joblib", path=output_path)
        try:
            import joblib
            joblib.dump(model, output_path)
            return output_path
        except ImportError:
            self.logger.error("joblib_not_installed")
            raise

    def export_json(self, metadata: Dict[str, Any], output_path: str) -> str:
        self.logger.info("exporting_model_json", path=output_path)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        return output_path

    def export_h5(self, model: Any, output_path: str) -> str:
        self.logger.info("exporting_model_h5", path=output_path)
        try:
            model.save(output_path, save_format="h5")
            return output_path
        except Exception as e:
            self.logger.error("h5_export_failed", error=str(e))
            raise

    def export_keras(self, model: Any, output_path: str) -> str:
        self.logger.info("exporting_model_keras", path=output_path)
        try:
            model.save(output_path, save_format="tf")
            return output_path
        except Exception as e:
            self.logger.error("keras_export_failed", error=str(e))
            raise

    def export_onnx(self, model: Any, output_path: str) -> str:
        self.logger.info("exporting_model_onnx", path=output_path)
        try:
            import skl2onnx
            # Actual ONNX conversion logic would go here depending on model type
            self.logger.warning("onnx_export_not_fully_implemented_in_framework_skeleton")
            return output_path
        except ImportError:
            self.logger.warning("skl2onnx_not_installed_skipping")
            return ""

    def save_metadata(self, model_name: str, params: Dict[str, Any], 
                      metrics: Dict[str, Any], feature_names: List[str], 
                      output_path: str) -> str:
        self.logger.info("saving_model_metadata")
        meta = {
            "model_name": model_name,
            "parameters": params,
            "metrics": metrics,
            "features": feature_names
        }
        return self.export_json(meta, output_path)

    def export(self, model: Any, model_name: str, formats: List[str], 
               params: Dict[str, Any], metrics: Dict[str, Any], 
               feature_names: List[str]) -> Dict[str, str]:
        """Orchestrates model export to all configured formats."""
        self.logger.info("exporting_model", formats=formats)
        results = {}
        base_path = str(self.output_dir / model_name)
        
        if "joblib" in formats:
            results["joblib"] = self.export_joblib(model, f"{base_path}.joblib")
            
        if "h5" in formats:
            results["h5"] = self.export_h5(model, f"{base_path}.h5")
            
        if "keras" in formats:
            results["keras"] = self.export_keras(model, f"{base_path}")
            
        if "onnx" in formats:
            results["onnx"] = self.export_onnx(model, f"{base_path}.onnx")
            
        if self.config.get("export.save_metadata", True):
            results["metadata"] = self.save_metadata(
                model_name, params, metrics, feature_names, f"{base_path}_metadata.json"
            )
            
        return results
