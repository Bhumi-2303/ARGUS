"""
Tests for the Gradient Reversal Layer (GRL).

Verifies that:
1. Forward pass is identity
2. Backward pass reverses and scales gradients
3. Lambda scheduler follows Ganin schedule
"""
import pytest
import numpy as np


class TestGradientReversal:
    """Test suite for Gradient Reversal Layer."""

    def test_import(self):
        from training.trainers.gradient_reversal import (
            GradientReversalFunction, GradientReversalLayer, lambda_scheduler
        )

    def test_forward_is_identity(self):
        """Forward pass should not modify the input."""
        import torch
        from training.trainers.gradient_reversal import GradientReversalLayer

        grl = GradientReversalLayer(lambda_=1.0)
        x = torch.randn(5, 3, requires_grad=True)
        y = grl(x)

        assert torch.allclose(x, y), "Forward pass should be identity"

    def test_backward_reverses_gradient(self):
        """Backward pass should negate gradients when lambda=1.0."""
        import torch
        from training.trainers.gradient_reversal import GradientReversalFunction

        x = torch.randn(5, 3, requires_grad=True)
        lambda_ = 1.0

        # Apply GRL
        y = GradientReversalFunction.apply(x, lambda_)
        loss = y.sum()
        loss.backward()

        # Gradient of sum w.r.t. x should be all 1s normally.
        # With GRL at lambda=1.0, it should be all -1s.
        expected = -torch.ones_like(x)
        assert torch.allclose(x.grad, expected), (
            f"Expected gradient {expected}, got {x.grad}"
        )

    def test_backward_scales_gradient(self):
        """Backward pass should scale by -lambda."""
        import torch
        from training.trainers.gradient_reversal import GradientReversalFunction

        x = torch.randn(5, 3, requires_grad=True)
        lambda_ = 0.5

        y = GradientReversalFunction.apply(x, lambda_)
        loss = y.sum()
        loss.backward()

        expected = -0.5 * torch.ones_like(x)
        assert torch.allclose(x.grad, expected, atol=1e-6), (
            f"Expected gradient {expected}, got {x.grad}"
        )

    def test_backward_zero_lambda(self):
        """With lambda=0, gradients should be zero (no reversal effect)."""
        import torch
        from training.trainers.gradient_reversal import GradientReversalFunction

        x = torch.randn(5, 3, requires_grad=True)
        lambda_ = 0.0

        y = GradientReversalFunction.apply(x, lambda_)
        loss = y.sum()
        loss.backward()

        expected = torch.zeros_like(x)
        assert torch.allclose(x.grad, expected, atol=1e-6)

    def test_lambda_scheduler_boundaries(self):
        """Lambda scheduler should go from 0 to ~1 over p=[0,1]."""
        from training.trainers.gradient_reversal import lambda_scheduler

        # At p=0, lambda should be near 0
        assert lambda_scheduler(0.0) < 0.05, f"lambda(0) should be near 0, got {lambda_scheduler(0.0)}"

        # At p=1, lambda should be near 1
        assert lambda_scheduler(1.0) > 0.95, f"lambda(1) should be near 1, got {lambda_scheduler(1.0)}"

        # At p=0.5, lambda is ~0.986 with gamma=10 scaling
        mid = lambda_scheduler(0.5)
        assert 0.9 < mid < 1.0, f"lambda(0.5) should be near 0.986, got {mid}"

    def test_lambda_scheduler_monotonic(self):
        """Lambda scheduler should be monotonically increasing."""
        from training.trainers.gradient_reversal import lambda_scheduler

        values = [lambda_scheduler(p / 100) for p in range(101)]
        for i in range(1, len(values)):
            assert values[i] >= values[i - 1] - 1e-10, (
                f"Lambda not monotonic at p={i/100}: {values[i]} < {values[i-1]}"
            )

    def test_grl_layer_module(self):
        """GradientReversalLayer should work as an nn.Module."""
        import torch
        from training.trainers.gradient_reversal import GradientReversalLayer

        grl = GradientReversalLayer(lambda_=0.8)

        # Should be usable in nn.Sequential
        model = torch.nn.Sequential(
            torch.nn.Linear(10, 5),
            grl,
            torch.nn.Linear(5, 1),
        )

        x = torch.randn(3, 10)
        y = model(x)
        assert y.shape == (3, 1)

        # Backprop should work
        loss = y.sum()
        loss.backward()
