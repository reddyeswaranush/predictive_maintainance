"""Small, dependency-light standard scaler used by the model."""

from __future__ import annotations

import numpy as np


class StandardScaler:
    def __init__(self, mean: np.ndarray | None = None, scale: np.ndarray | None = None):
        self.mean_ = mean
        self.scale_ = scale

    def fit(self, values: np.ndarray) -> "StandardScaler":
        values = np.asarray(values, dtype=float)
        self.mean_ = values.mean(axis=0)
        self.scale_ = values.std(axis=0)
        self.scale_[self.scale_ < 1e-12] = 1.0
        return self

    def transform(self, values: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.scale_ is None:
            raise RuntimeError("Scaler must be fitted before transform")
        return (np.asarray(values, dtype=float) - self.mean_) / self.scale_

    def to_dict(self) -> dict:
        if self.mean_ is None or self.scale_ is None:
            raise RuntimeError("Scaler has not been fitted")
        return {"mean": self.mean_.tolist(), "scale": self.scale_.tolist()}

    @classmethod
    def from_dict(cls, payload: dict) -> "StandardScaler":
        return cls(np.asarray(payload["mean"], dtype=float), np.asarray(payload["scale"], dtype=float))