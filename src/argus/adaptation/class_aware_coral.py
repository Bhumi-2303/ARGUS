"""ARGUS Class-Aware CORAL Domain Adaptation Module."""

import numpy as np
from .coral import CORALAdapter


class ClassAwareCORALAdapter:
    """Class-conditional covariance alignment between source and target domains."""
    
    def __init__(self, reg: float = 1e-5):
        self.reg = reg
        self.adapters = {}

    def fit(self, X_source: np.ndarray, y_source: np.ndarray, X_target: np.ndarray, y_target: np.ndarray):
        """Fits separate CORAL adapters for each class y in {0, 1}."""
        classes = np.unique(y_source)
        for c in classes:
            idx_s = (y_source == c)
            idx_t = (y_target == c)
            if np.sum(idx_s) > 0 and np.sum(idx_t) > 0:
                adapter = CORALAdapter(reg=self.reg)
                adapter.fit(X_source[idx_s], X_target[idx_t])
                self.adapters[c] = adapter
        return self

    def transform(self, X_source: np.ndarray, y_source: np.ndarray) -> np.ndarray:
        """Transforms source features conditionally by class."""
        X_aligned = np.zeros_like(X_source)
        for c, adapter in self.adapters.items():
            idx = (y_source == c)
            if np.sum(idx) > 0:
                X_aligned[idx] = adapter.transform(X_source[idx])
        return X_aligned
