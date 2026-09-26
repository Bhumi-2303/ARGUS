#!/usr/bin/env python3
"""
CLI entry point for the ARGUS ML Training Framework.
"""
import argparse
import sys
from pathlib import Path

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import setup_logging, get_logger

AVAILABLE_MODELS = [
    "random_forest",
    "xgboost",
    "lightgbm",
    "catboost",
    "neural_network"
]

def main():
    parser = argparse.ArgumentParser(description="ARGUS ML Training Framework")
    parser.add_argument("--model", type=str, choices=AVAILABLE_MODELS, help="Model to train")
    parser.add_argument("--all", action="store_true", help="Train all available models")
    parser.add_argument("--dry-run", action="store_true", help="Validate framework without training")
    parser.add_argument("--config", type=str, help="Path to override config file")
    parser.add_argument("--seed", type=int, help="Override random seed")
    
    args = parser.parse_args()
    
    if not args.model and not args.all:
        parser.error("Must specify either --model or --all")
        
    # Setup base config just for logging setup initially
    base_config = ConfigurationManager()
    setup_logging(base_config.config)
    logger = get_logger("argus_train_cli")
    
    if args.dry_run:
        logger.info("starting_dry_run_validation")
        models_to_test = AVAILABLE_MODELS if args.all else [args.model]
        
        # 1. Validate Configs
        for model in models_to_test:
            try:
                cm = ConfigurationManager.from_args(model_name=model)
                logger.info("config_validation_passed", model=model)
            except Exception as e:
                logger.error("config_validation_failed", model=model, error=str(e))
                sys.exit(1)
                
        # 2. Validate Directories
        required_dirs = [
            "training/configs", "training/data", "training/preprocessing",
            "training/feature_engineering", "training/feature_selection",
            "training/trainers", "training/evaluation", "training/tuning",
            "training/reports", "training/exports", "training/graphs",
            "training/logs", "training/utils"
        ]
        for d in required_dirs:
            if not Path(d).exists():
                logger.error("directory_missing", directory=d)
                sys.exit(1)
        logger.info("directory_validation_passed")
        
        # 3. Validate Dataset Path (Config check)
        dataset_path = base_config.get("dataset.raw_path")
        if not Path(dataset_path).exists():
            logger.warning("dataset_path_missing_in_dry_run", path=dataset_path)
            # We don't exit here because the dataset might be mounted later, but we warn
            
        logger.info("dry_run_successful_framework_is_ready")
        sys.exit(0)
        
    else:
        logger.info("starting_training_execution")
        models_to_train = AVAILABLE_MODELS if args.all else [args.model]
        
        trainer_classes = {
            "random_forest": "RandomForestTrainer",
            "xgboost": "XGBoostTrainer",
            "lightgbm": "LightGBMTrainer",
            "catboost": "CatBoostTrainer",
            "neural_network": "NeuralNetworkTrainer"
        }
        
        import importlib
        import gc
        
        for model_name in models_to_train:
            logger.info(f"training_{model_name}")
            config = ConfigurationManager.from_args(model_name=model_name)
            
            # Dynamic import
            module_name = f"training.trainers.{model_name}_trainer"
            class_name = trainer_classes[model_name]
            module = importlib.import_module(module_name)
            trainer_class = getattr(module, class_name)
            
            # Run pipeline
            trainer = trainer_class(config)
            try:
                metrics = trainer.run_pipeline()
                logger.info(f"finished_training_{model_name}", metrics=metrics)
            except Exception as e:
                logger.error(f"failed_training_{model_name}", error=str(e))
            
            # Memory optimization: release memory after each model
            del trainer
            gc.collect()
            
        sys.exit(0)

if __name__ == "__main__":
    main()
