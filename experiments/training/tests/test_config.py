import pytest
from pathlib import Path
from training.utils.config_manager import ConfigurationManager

def test_default_config_loads():
    cm = ConfigurationManager()
    assert cm.config is not None
    assert cm.get("project.name") == "ARGUS"
    
def test_model_config_loads_and_merges():
    cm = ConfigurationManager.from_args("random_forest")
    assert cm.get("model.name") == "random_forest"
    assert cm.get("parameters.n_estimators") == 200
    assert cm.get("project.name") == "ARGUS" # Ensure merge happened
    
def test_all_model_configs_load():
    models = ["random_forest", "xgboost", "lightgbm", "catboost", "neural_network"]
    for model in models:
        cm = ConfigurationManager.from_args(model)
        assert cm.get("model.name") == model
        
def test_invalid_config_raises_error():
    with pytest.raises(FileNotFoundError):
        ConfigurationManager.from_args("invalid_model_name")
        
def test_override_works():
    cm = ConfigurationManager()
    cm.override({"hardware": {"max_memory_gb": 16}})
    assert cm.get("hardware.max_memory_gb") == 16
