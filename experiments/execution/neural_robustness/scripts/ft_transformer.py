#!/usr/bin/env python3
"""
FT-Transformer (Feature Tokenizer Transformer) Implementation for Tabular Data
Reference: Gorishniy et al., "Revisiting Deep Learning Models for Tabular Data", NeurIPS 2021
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class NumericalFeatureTokenizer(nn.Module):
    """
    Transforms D scalar numerical features into a sequence of D embedding vectors of dimension d_token.
    For feature i, compute: T_i(x_i) = x_i * w_i + b_i
    """
    def __init__(self, n_features: int, d_token: int):
        super().__init__()
        self.n_features = n_features
        self.d_token = d_token
        # Weights: (n_features, d_token), Biases: (n_features, d_token)
        self.weight = nn.Parameter(torch.Tensor(n_features, d_token))
        self.bias = nn.Parameter(torch.Tensor(n_features, d_token))
        self.cls_token = nn.Parameter(torch.Tensor(1, 1, d_token))
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        nn.init.zeros_(self.bias)
        nn.init.normal_(self.cls_token, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch_size, n_features)
        # x.unsqueeze(-1): (batch_size, n_features, 1)
        # self.weight.unsqueeze(0): (1, n_features, d_token)
        # Multiplication -> (batch_size, n_features, d_token)
        x_emb = x.unsqueeze(-1) * self.weight.unsqueeze(0) + self.bias.unsqueeze(0)
        
        # Prepend [CLS] token
        cls_tokens = self.cls_token.expand(x.size(0), -1, -1)  # (batch_size, 1, d_token)
        tokens = torch.cat([cls_tokens, x_emb], dim=1)         # (batch_size, n_features + 1, d_token)
        return tokens


class TransformerBlock(nn.Module):
    """Pre-LN Transformer Block with Multi-Head Self-Attention and Feed-Forward Network."""
    def __init__(self, d_token: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_token)
        self.attn = nn.MultiheadAttention(embed_dim=d_token, num_heads=n_heads, dropout=dropout, batch_first=True)
        self.norm2 = nn.LayerNorm(d_token)
        self.ffn = nn.Sequential(
            nn.Linear(d_token, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_token),
            nn.Dropout(dropout)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-LN Self-Attention
        x_norm = self.norm1(x)
        attn_out, _ = self.attn(x_norm, x_norm, x_norm)
        x = x + attn_out
        
        # Pre-LN FFN
        x = x + self.ffn(self.norm2(x))
        return x


class FTTransformer(nn.Module):
    """Full FT-Transformer Architecture for Tabular Classification."""
    def __init__(self, n_features: int, d_token: int = 64, n_blocks: int = 3, n_heads: int = 4, d_ff: int = 128, dropout: float = 0.1):
        super().__init__()
        self.tokenizer = NumericalFeatureTokenizer(n_features, d_token)
        self.blocks = nn.ModuleList([
            TransformerBlock(d_token, n_heads, d_ff, dropout)
            for _ in range(n_blocks)
        ])
        self.head_norm = nn.LayerNorm(d_token)
        self.head = nn.Linear(d_token, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Tokenize features + CLS token
        x = self.tokenizer(x)  # (batch_size, n_features + 1, d_token)
        
        # Pass through Transformer blocks
        for block in self.blocks:
            x = block(x)
            
        # Extract [CLS] token representation (index 0)
        cls_rep = x[:, 0, :]    # (batch_size, d_token)
        cls_rep = self.head_norm(cls_rep)
        logits = self.head(cls_rep).squeeze(-1)  # (batch_size,)
        return logits
