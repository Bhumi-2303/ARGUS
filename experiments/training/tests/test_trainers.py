import pytest
from training.trainers.base_trainer import BaseTrainer
from training.trainers.random_forest_trainer import RandomForestTrainer
from training.trainers.xgboost_trainer import XGBoostTrainer
from training.trainers.lightgbm_trainer import LightGBMTrainer
from training.trainers.catboost_trainer import CatBoostTrainer
from training.trainers.neural_network_trainer import NeuralNetworkTrainer
from training.utils.config_manager import ConfigurationManager

def test_base_trainer_is_abstract():
    cm = ConfigurationManager()
    with pytest.raises(TypeError):
        BaseTrainer(cm)

def test_random_forest_instantiates():
    cm = ConfigurationManager.from_args("random_forest")
    trainer = RandomForestTrainer(cm)
    assert trainer.get_model_name() == "random_forest"
    
def test_xgboost_instantiates():
    cm = ConfigurationManager.from_args("xgboost")
    trainer = XGBoostTrainer(cm)
    assert trainer.get_model_name() == "xgboost"

def test_lightgbm_instantiates():
    cm = ConfigurationManager.from_args("lightgbm")
    trainer = LightGBMTrainer(cm)
    assert trainer.get_model_name() == "lightgbm"

def test_catboost_instantiates():
    cm = ConfigurationManager.from_args("catboost")
    trainer = CatBoostTrainer(cm)
    assert trainer.get_model_name() == "catboost"

def test_neural_network_instantiates():
    cm = ConfigurationManager.from_args("neural_network")
    trainer = NeuralNetworkTrainer(cm)
    assert trainer.get_model_name() == "neural_network"
