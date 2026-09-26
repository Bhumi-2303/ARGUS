"""
Gradient Reversal Layer (GRL) implementation.

Based on Ganin et al., 2016 ("Domain-Adversarial Training of Neural Networks").
"""

import math
from typing import Any, Tuple

import torch
import torch.nn as nn
from torch.autograd import Function

__all__ = ['GradientReversalFunction', 'GradientReversalLayer', 'lambda_scheduler']

class GradientReversalFunction(Function):
    """
    Custom autograd function for Gradient Reversal Layer.
    Forward pass: identity (passes inputs unchanged).
    Backward pass: reverses gradients by multiplying with a negative coefficient (-lambda).
    """
    
    @staticmethod
    def forward(ctx: Any, x: torch.Tensor, lambda_: float) -> torch.Tensor:
        ctx.lambda_ = lambda_
        return x.view_as(x)

    @staticmethod
    def backward(ctx: Any, grad_output: torch.Tensor) -> Tuple[torch.Tensor, None]:
        # Gradient is multiplied by -lambda_
        grad_input = grad_output.clone()
        return grad_input * -ctx.lambda_, None


class GradientReversalLayer(nn.Module):
    """
    Module wrapper for GradientReversalFunction.
    """
    
    def __init__(self, lambda_: float = 1.0):
        super().__init__()
        self.lambda_ = lambda_

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return GradientReversalFunction.apply(x, self.lambda_)


def lambda_scheduler(p: float) -> float:
    """
    Implements the lambda scheduling from Ganin et al., 2016.
    lambda = 2 / (1 + exp(-10 * p)) - 1
    
    Args:
        p: float in [0, 1] representing the progress of training 
           (e.g., current_step / total_steps).
           
    Returns:
        float: the calculated lambda value.
    """
    return 2.0 / (1.0 + math.exp(-10.0 * p)) - 1.0
