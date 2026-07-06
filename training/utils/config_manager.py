import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigurationManager:
    """Manages YAML configurations for the ARGUS ML framework."""
    
    def __init__(self, default_config_path: str = "training/configs/default.yaml"):
        """Initializes the configuration manager."""
        self.default_config_path = Path(default_config_path)
        self.config: Dict[str, Any] = self._load_yaml(self.default_config_path)
        
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Loads a YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
            
    def load_model_config(self, model_name: str) -> None:
        """Loads a model-specific config and merges it with the default."""
        model_config_path = self.default_config_path.parent / f"{model_name}.yaml"
        model_config = self._load_yaml(model_config_path)
        self.config = self._deep_merge(self.config, model_config)
        
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merges two dictionaries."""
        for k, v in update.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                base[k] = self._deep_merge(base[k], v)
            else:
                base[k] = v
        return base
        
    def override(self, overrides: Dict[str, Any]) -> None:
        """Overrides configuration values."""
        self.config = self._deep_merge(self.config, overrides)
        
    def get(self, key: str, default: Any = None) -> Any:
        """Gets a configuration value using dot notation (e.g., 'dataset.raw_path')."""
        keys = key.split(".")
        val = self.config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    @staticmethod
    def from_args(model_name: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> "ConfigurationManager":
        """Factory method to create a ConfigurationManager from arguments."""
        cm = ConfigurationManager()
        if model_name:
            cm.load_model_config(model_name)
        if overrides:
            cm.override(overrides)
        return cm
