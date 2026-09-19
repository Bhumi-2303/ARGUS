#!/usr/bin/env python3
"""
DANN (Domain-Adversarial Neural Network) Implementation for Tabular Telemetry
Reference: Ganin et al., "Domain-Adversarial Training of Neural Networks", JMLR 2016.
Architecture:
Input (4) -> Feature Encoder (32) -> Attack Classifier (1) & GRL (alpha) -> Domain Classifier (1)
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class GradReverse(torch.autograd.Function):
    """
    Gradient Reversal Layer (GRL):
    Forward pass: Identity mapping f(x) = x
    Backward pass: Gradient scaling and sign reversal: grad_out = -alpha * grad_in
    """
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = alpha
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.alpha, None

class DANNNetwork(nn.Module):
    """
    Lightweight Domain-Adversarial Neural Network for ARGUS-4 Cross-Domain Transfer.
    """
    def __init__(self, input_dim: int = 4, hidden_dim: int = 64, latent_dim: int = 32, dropout: float = 0.1):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.dropout = dropout

        # 1. Feature Encoder
        self.feature_encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, latent_dim),
            nn.BatchNorm1d(latent_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )

        # 2. Attack (Task) Classifier: Normal (0) vs Attack (1)
        self.attack_classifier = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 1)
        )

        # 3. Domain Classifier: Source D1 (0) vs Target D3 (1)
        self.domain_classifier = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 1)
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor, alpha: float = 1.0):
        # Extract domain-shared feature representation
        features = self.feature_encoder(x)
        
        # Predict attack label
        attack_logits = self.attack_classifier(features).squeeze(-1)
        
        # Apply gradient reversal layer before domain classifier
        reversed_features = GradReverse.apply(features, alpha)
        domain_logits = self.domain_classifier(reversed_features).squeeze(-1)
        
        return attack_logits, domain_logits, features

    def count_parameters(self) -> dict:
        total = sum(p.numel() for p in self.parameters() if p.requires_grad)
        enc = sum(p.numel() for p in self.feature_encoder.parameters() if p.requires_grad)
        att = sum(p.numel() for p in self.attack_classifier.parameters() if p.requires_grad)
        dom = sum(p.numel() for p in self.domain_classifier.parameters() if p.requires_grad)
        return {
            "total_parameters": total,
            "feature_encoder_parameters": enc,
            "attack_classifier_parameters": att,
            "domain_classifier_parameters": dom
        }

if __name__ == "__main__":
    model = DANNNetwork()
    p_info = model.count_parameters()
    print("DANN Network Initialized:")
    for k, v in p_info.items():
        print(f"  {k}: {v:,}")
    
    # Sanity forward pass
    dummy_x = torch.randn(8, 4)
    att_logits, dom_logits, feats = model(dummy_x, alpha=0.5)
    print(f"Sanity Check -> att_logits: {att_logits.shape}, dom_logits: {dom_logits.shape}, feats: {feats.shape}")
