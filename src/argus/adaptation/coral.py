"""ARGUS Correlation Alignment (CORAL) Domain Adaptation Implementation."""

import numpy as np
import pandas as pd


class CORALAdapter:
    """Computes second-order covariance alignment between source and target domains."""
    
    def __init__(self, reg: float = 1e-5):
        self.reg = reg
        self.A = None
        self.source_mean = None
        self.target_mean = None

    def fit(self, X_source: np.ndarray, X_target: np.ndarray):
        """Fits covariance alignment matrix A = C_s^(-1/2) * C_t^(1/2)."""
        n_s, d = X_source.shape
        n_t, _ = X_target.shape
        
        self.source_mean = np.mean(X_source, axis=0)
        self.target_mean = np.mean(X_target, axis=0)
        
        X_s_c = X_source - self.source_mean
        X_t_c = X_target - self.target_mean
        
        C_s = (X_s_c.T @ X_s_c) / (n_s - 1) + self.reg * np.eye(d)
        C_t = (X_t_c.T @ X_t_c) / (n_t - 1) + self.reg * np.eye(d)
        
        # Matrix square root via SVD
        U_s, S_s, V_s = np.linalg.svd(C_s)
        C_s_inv_sqrt = U_s @ np.diag(1.0 / np.sqrt(S_s)) @ V_s
        
        U_t, S_t, V_t = np.linalg.svd(C_t)
        C_t_sqrt = U_t @ np.diag(np.sqrt(S_t)) @ V_t
        
        self.A = C_s_inv_sqrt @ C_t_sqrt
        return self

    def transform(self, X_source: np.ndarray) -> np.ndarray:
        """Transforms source features into aligned target space."""
        X_s_c = X_source - self.source_mean
        return (X_s_c @ self.A) + self.target_mean
