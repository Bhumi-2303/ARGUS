"""ARGUS Correlation Alignment (CORAL) Domain Adaptation Implementation."""

from pathlib import Path
from typing import Optional, Union
import numpy as np


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

        denom_s = max(n_s - 1, 1)
        denom_t = max(n_t - 1, 1)

        C_s = (X_s_c.T @ X_s_c) / denom_s + self.reg * np.eye(d)
        C_t = (X_t_c.T @ X_t_c) / denom_t + self.reg * np.eye(d)

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

    def save(self, path: Union[str, Path]) -> Path:
        """Saves CORAL adapter parameters to .npz or .json without pickle."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            import json

            data = {
                "reg": float(self.reg),
                "A": self.A.tolist() if self.A is not None else None,
                "source_mean": self.source_mean.tolist() if self.source_mean is not None else None,
                "target_mean": self.target_mean.tolist() if self.target_mean is not None else None,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            np.savez(
                path,
                A=self.A if self.A is not None else np.empty((0, 0)),
                source_mean=self.source_mean if self.source_mean is not None else np.empty(0),
                target_mean=self.target_mean if self.target_mean is not None else np.empty(0),
                reg=np.array([self.reg], dtype=np.float64),
            )
        return path

    @classmethod
    def load(cls, path: Union[str, Path]) -> "CORALAdapter":
        """Loads CORAL adapter parameters from .npz or .json without pickle."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"CORAL parameter file not found: {path}")

        if path.suffix == ".json":
            import json

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            adapter = cls(reg=float(data.get("reg", 1e-5)))
            adapter.A = np.array(data["A"], dtype=np.float64) if data.get("A") is not None else None
            adapter.source_mean = (
                np.array(data["source_mean"], dtype=np.float64)
                if data.get("source_mean") is not None
                else None
            )
            adapter.target_mean = (
                np.array(data["target_mean"], dtype=np.float64)
                if data.get("target_mean") is not None
                else None
            )
            return adapter
        else:
            data = np.load(path, allow_pickle=False)
            reg = float(data["reg"][0]) if "reg" in data else 1e-5
            adapter = cls(reg=reg)
            adapter.A = data["A"] if "A" in data and data["A"].size > 0 else None
            adapter.source_mean = (
                data["source_mean"] if "source_mean" in data and data["source_mean"].size > 0 else None
            )
            adapter.target_mean = (
                data["target_mean"] if "target_mean" in data and data["target_mean"].size > 0 else None
            )
            return adapter
