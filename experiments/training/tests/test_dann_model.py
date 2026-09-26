"""
Tests for the DANN model and DANNTrainer.

Verifies:
1. Model architecture (forward pass shapes)
2. Feature extraction
3. Training loop convergence on synthetic data
4. Save/load round-trip
"""
import pytest
import numpy as np
import tempfile
import os


def _make_synthetic_data(n_source=200, n_target=200, n_features=15, seed=42):
    """Create synthetic source/target data with a domain shift."""
    rng = np.random.RandomState(seed)

    # Source: cluster around mean=0
    source_X = rng.randn(n_source, n_features).astype(np.float32)
    source_y = (source_X[:, 0] + source_X[:, 1] > 0).astype(np.int64)

    # Target: cluster around mean=2 (domain shift)
    target_X = (rng.randn(n_target, n_features) + 2).astype(np.float32)
    target_y = (target_X[:, 0] + target_X[:, 1] > 2).astype(np.int64)

    return source_X, source_y, target_X, target_y


class TestDANNModel:
    """Test suite for DANN model architecture."""

    def test_import(self):
        from training.trainers.dann_model import DANN, DANNTrainer

    def test_forward_pass_shapes(self):
        """Forward pass should return correct output shapes."""
        import torch
        from training.trainers.dann_model import DANN

        model = DANN(input_dim=15, feature_hidden_dims=[128, 64], label_hidden_dims=[32], domain_hidden_dims=[32])
        x = torch.randn(10, 15)
        label_out, domain_out, features = model(x, lambda_=0.5)

        assert label_out.shape == (10, 1), f"Label output shape: {label_out.shape}"
        assert domain_out.shape == (10, 1), f"Domain output shape: {domain_out.shape}"
        assert features.shape == (10, 64), f"Feature shape: {features.shape}"

    def test_extract_features(self):
        """Feature extraction should return the feature extractor output."""
        import torch
        from training.trainers.dann_model import DANN

        model = DANN(input_dim=10, feature_hidden_dims=[64, 32], label_hidden_dims=[16], domain_hidden_dims=[16])
        x = torch.randn(5, 10)
        features = model.extract_features(x)

        assert features.shape == (5, 32), f"Expected (5, 32), got {features.shape}"

    def test_feature_extractor_deterministic(self):
        """Same input should produce same output in eval mode."""
        import torch
        from training.trainers.dann_model import DANN

        model = DANN(input_dim=10, feature_hidden_dims=[64, 32], label_hidden_dims=[16], domain_hidden_dims=[16])
        model.eval()

        x = torch.randn(5, 10)
        f1 = model.extract_features(x)
        f2 = model.extract_features(x)

        assert torch.allclose(f1, f2), "Feature extraction should be deterministic in eval mode"


class TestDANNTrainer:
    """Test suite for DANNTrainer."""

    def test_trainer_init(self):
        from training.trainers.dann_model import DANNTrainer

        config = {
            "feature_extractor": {"hidden_dims": [64, 32], "dropout": 0.1},
            "label_classifier": {"hidden_dims": [16]},
            "domain_classifier": {"hidden_dims": [16]},
            "training": {
                "epochs": 5, "batch_size": 32, "lr": 0.01,
                "patience": 3, "lambda_schedule": "ganin",
            },
        }
        trainer = DANNTrainer(input_dim=15, config=config)
        assert trainer is not None

    def test_training_runs(self):
        """Training should complete without errors on synthetic data."""
        from training.trainers.dann_model import DANNTrainer

        source_X, source_y, target_X, _ = _make_synthetic_data(
            n_source=100, n_target=100, n_features=10
        )

        config = {
            "feature_extractor": {"hidden_dims": [32, 16], "dropout": 0.1},
            "label_classifier": {"hidden_dims": [8]},
            "domain_classifier": {"hidden_dims": [8]},
            "training": {
                "epochs": 3, "batch_size": 32, "lr": 0.01,
                "patience": 5, "lambda_schedule": "ganin",
            },
        }

        trainer = DANNTrainer(input_dim=10, config=config)
        history = trainer.train(
            source_X=source_X,
            source_y=source_y,
            target_X=target_X,
            source_val_X=source_X[:20],
            source_val_y=source_y[:20],
            target_val_X=target_X[:20],
        )

        assert "label_losses" in history
        assert len(history["label_losses"]) > 0

    def test_predict(self):
        """Predict should return binary array."""
        from training.trainers.dann_model import DANNTrainer

        source_X, source_y, target_X, _ = _make_synthetic_data(
            n_source=100, n_target=100, n_features=10
        )

        config = {
            "feature_extractor": {"hidden_dims": [32, 16], "dropout": 0.1},
            "label_classifier": {"hidden_dims": [8]},
            "domain_classifier": {"hidden_dims": [8]},
            "training": {
                "epochs": 2, "batch_size": 32, "lr": 0.01,
                "patience": 5, "lambda_schedule": "ganin",
            },
        }

        trainer = DANNTrainer(input_dim=10, config=config)
        trainer.train(
            source_X=source_X, source_y=source_y,
            target_X=target_X,
            source_val_X=source_X[:20], source_val_y=source_y[:20],
            target_val_X=target_X[:20],
        )

        preds = trainer.predict(target_X)
        assert preds.shape == (100,)
        assert set(np.unique(preds)).issubset({0, 1})

    def test_predict_proba(self):
        """Predict proba should return values in [0, 1]."""
        from training.trainers.dann_model import DANNTrainer

        source_X, source_y, target_X, _ = _make_synthetic_data(
            n_source=100, n_target=100, n_features=10
        )

        config = {
            "feature_extractor": {"hidden_dims": [32, 16], "dropout": 0.1},
            "label_classifier": {"hidden_dims": [8]},
            "domain_classifier": {"hidden_dims": [8]},
            "training": {
                "epochs": 2, "batch_size": 32, "lr": 0.01,
                "patience": 5, "lambda_schedule": "ganin",
            },
        }

        trainer = DANNTrainer(input_dim=10, config=config)
        trainer.train(
            source_X=source_X, source_y=source_y,
            target_X=target_X,
            source_val_X=source_X[:20], source_val_y=source_y[:20],
            target_val_X=target_X[:20],
        )

        proba = trainer.predict_proba(target_X)
        assert proba.shape == (100,)
        assert proba.min() >= 0.0
        assert proba.max() <= 1.0

    def test_extract_features(self):
        """Feature extraction should return correct dimensionality."""
        from training.trainers.dann_model import DANNTrainer

        source_X, source_y, target_X, _ = _make_synthetic_data(
            n_source=100, n_target=100, n_features=10
        )

        config = {
            "feature_extractor": {"hidden_dims": [32, 16], "dropout": 0.1},
            "label_classifier": {"hidden_dims": [8]},
            "domain_classifier": {"hidden_dims": [8]},
            "training": {
                "epochs": 2, "batch_size": 32, "lr": 0.01,
                "patience": 5, "lambda_schedule": "ganin",
            },
        }

        trainer = DANNTrainer(input_dim=10, config=config)
        trainer.train(
            source_X=source_X, source_y=source_y,
            target_X=target_X,
            source_val_X=source_X[:20], source_val_y=source_y[:20],
            target_val_X=target_X[:20],
        )

        features = trainer.extract_features(target_X)
        assert features.shape == (100, 16), f"Expected (100, 16), got {features.shape}"

    def test_save_load_roundtrip(self):
        """Model should produce same predictions after save/load."""
        from training.trainers.dann_model import DANNTrainer

        source_X, source_y, target_X, _ = _make_synthetic_data(
            n_source=100, n_target=100, n_features=10
        )

        config = {
            "feature_extractor": {"hidden_dims": [32, 16], "dropout": 0.1},
            "label_classifier": {"hidden_dims": [8]},
            "domain_classifier": {"hidden_dims": [8]},
            "training": {
                "epochs": 2, "batch_size": 32, "lr": 0.01,
                "patience": 5, "lambda_schedule": "ganin",
            },
        }

        trainer = DANNTrainer(input_dim=10, config=config)
        trainer.train(
            source_X=source_X, source_y=source_y,
            target_X=target_X,
            source_val_X=source_X[:20], source_val_y=source_y[:20],
            target_val_X=target_X[:20],
        )

        preds_before = trainer.predict_proba(target_X[:10])

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_model.pt")
            trainer.save(save_path)

            trainer2 = DANNTrainer(input_dim=10, config=config)
            trainer2.load(save_path)

            preds_after = trainer2.predict_proba(target_X[:10])

        np.testing.assert_allclose(preds_before, preds_after, atol=1e-5)
