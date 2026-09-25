import pytest
from pathlib import Path

def test_required_directories_exist():
    base = Path("training")
    required_dirs = [
        "configs", "data", "preprocessing", "feature_engineering", 
        "feature_selection", "trainers", "evaluation", "tuning",
        "reports", "exports", "graphs", "logs", "utils", "notebooks", "tests"
    ]
    for d in required_dirs:
        assert (base / d).exists() and (base / d).is_dir(), f"Directory {d} is missing"

def test_required_configs_exist():
    base = Path("training/configs")
    configs = ["default.yaml", "random_forest.yaml", "xgboost.yaml", 
               "lightgbm.yaml", "catboost.yaml", "neural_network.yaml"]
    for c in configs:
        assert (base / c).exists() and (base / c).is_file(), f"Config {c} is missing"
