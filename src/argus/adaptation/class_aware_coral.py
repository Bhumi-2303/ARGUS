"""ARGUS Class-Aware CORAL Domain Adaptation Module."""

from pathlib import Path
from typing import Dict, Optional, Union
import numpy as np
from .coral import CORALAdapter


class ClassAwareCORALAdapter:
    """Class-conditional covariance alignment between source and target domains."""

    def __init__(self, reg: float = 1e-5):
        self.reg = reg
        self.adapters: Dict[int, CORALAdapter] = {}

    def fit(
        self, X_source: np.ndarray, y_source: np.ndarray, X_target: np.ndarray, y_target: np.ndarray
    ):
        """Fits separate CORAL adapters for each class y in {0, 1}."""
        classes = np.unique(y_source)
        for c in classes:
            idx_s = y_source == c
            idx_t = y_target == c
            if np.sum(idx_s) > 0 and np.sum(idx_t) > 0:
                adapter = CORALAdapter(reg=self.reg)
                adapter.fit(X_source[idx_s], X_target[idx_t])
                self.adapters[int(c)] = adapter
        return self

    def transform(self, X_source: np.ndarray, y_source: np.ndarray) -> np.ndarray:
        """Transforms source features conditionally by class."""
        X_aligned = np.zeros_like(X_source)
        for c, adapter in self.adapters.items():
            idx = y_source == c
            if np.sum(idx) > 0:
                X_aligned[idx] = adapter.transform(X_source[idx])
        return X_aligned

    def save(self, path: Union[str, Path]) -> Path:
        """Saves Class-Aware CORAL parameters to .json or .npz without pickle."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            import json

            payload = {
                "reg": float(self.reg),
                "classes": [int(c) for c in self.adapters.keys()],
                "adapters": {
                    str(c): {
                        "reg": float(ad.reg),
                        "A": ad.A.tolist() if ad.A is not None else None,
                        "source_mean": (
                            ad.source_mean.tolist() if ad.source_mean is not None else None
                        ),
                        "target_mean": (
                            ad.target_mean.tolist() if ad.target_mean is not None else None
                        ),
                    }
                    for c, ad in self.adapters.items()
                },
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        else:
            save_dict = {
                "reg": np.array([self.reg], dtype=np.float64),
                "classes": np.array(list(self.adapters.keys()), dtype=np.int64),
            }
            for c, ad in self.adapters.items():
                save_dict[f"adapter_{c}_A"] = ad.A if ad.A is not None else np.empty((0, 0))
                save_dict[f"adapter_{c}_source_mean"] = (
                    ad.source_mean if ad.source_mean is not None else np.empty(0)
                )
                save_dict[f"adapter_{c}_target_mean"] = (
                    ad.target_mean if ad.target_mean is not None else np.empty(0)
                )
            np.savez(path, **save_dict)
        return path

    @classmethod
    def load(cls, path: Union[str, Path]) -> "ClassAwareCORALAdapter":
        """Loads Class-Aware CORAL parameters from .json or .npz without pickle."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Class-Aware CORAL parameter file not found: {path}")

        if path.suffix == ".json":
            import json

            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            instance = cls(reg=float(payload.get("reg", 1e-5)))
            for c_str, ad_data in payload.get("adapters", {}).items():
                c = int(c_str)
                ad = CORALAdapter(reg=float(ad_data.get("reg", instance.reg)))
                ad.A = np.array(ad_data["A"], dtype=np.float64) if ad_data.get("A") is not None else None
                ad.source_mean = (
                    np.array(ad_data["source_mean"], dtype=np.float64)
                    if ad_data.get("source_mean") is not None
                    else None
                )
                ad.target_mean = (
                    np.array(ad_data["target_mean"], dtype=np.float64)
                    if ad_data.get("target_mean") is not None
                    else None
                )
                instance.adapters[c] = ad
            return instance
        else:
            data = np.load(path, allow_pickle=False)
            reg = float(data["reg"][0]) if "reg" in data else 1e-5
            instance = cls(reg=reg)
            classes = data["classes"]
            for c in classes:
                c = int(c)
                ad = CORALAdapter(reg=reg)
                key_a = f"adapter_{c}_A"
                key_sm = f"adapter_{c}_source_mean"
                key_tm = f"adapter_{c}_target_mean"
                ad.A = data[key_a] if key_a in data and data[key_a].size > 0 else None
                ad.source_mean = data[key_sm] if key_sm in data and data[key_sm].size > 0 else None
                ad.target_mean = data[key_tm] if key_tm in data and data[key_tm].size > 0 else None
                instance.adapters[c] = ad
            return instance
