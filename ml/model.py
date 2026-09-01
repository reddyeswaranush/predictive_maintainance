"""Regression model for telemetry-based maintenance risk."""

from __future__ import annotations

import numpy as np


class RidgeRegressor:
    """A deterministic ridge regressor implemented with NumPy.

    Using a small in-repo implementation keeps the production path lightweight
    and avoids requiring a compiled ML framework just to run inference.
    """

    def __init__(self, alpha: float = 1.0):
        self.alpha = float(alpha)
        self.weights_: np.ndarray | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "RidgeRegressor":
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        design = np.column_stack([np.ones(len(x)), x])
        penalty = np.eye(design.shape[1])
        penalty[0, 0] = 0.0
        self.weights_ = np.linalg.solve(
            design.T @ design + self.alpha * penalty,
            design.T @ y,
        )
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.weights_ is None:
            raise RuntimeError("Model must be fitted before predict")
        design = np.column_stack([np.ones(len(x)), np.asarray(x, dtype=float)])
        return design @ self.weights_

    def to_dict(self) -> dict:
        if self.weights_ is None:
            raise RuntimeError("Model has not been fitted")
        return {"alpha": self.alpha, "weights": self.weights_.tolist()}

    @classmethod
    def from_dict(cls, payload: dict) -> "RidgeRegressor":
        model = cls(payload["alpha"])
        model.weights_ = np.asarray(payload["weights"], dtype=float)
        return model