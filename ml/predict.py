"""Inference API for telemetry-based maintenance predictions."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from ml.features import build_features, build_metro_features
from ml.model import RidgeRegressor
from ml.scaler import StandardScaler


ARTIFACT_PATH = Path(__file__).resolve().parent / "model.json"
METRO_ARTIFACT_PATH = Path(__file__).resolve().parent / "metropt_model.joblib"


def _load_models(artifact_path: str | Path = ARTIFACT_PATH):
    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {path}. Run `python -m ml.train_model` first."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return (
        StandardScaler.from_dict(payload["scaler"]),
        RidgeRegressor.from_dict(payload["probability_model"]),
        RidgeRegressor.from_dict(payload["health_model"]),
    )


def predict_telemetry(
    telemetry: pd.DataFrame | dict,
    artifact_path: str | Path = ARTIFACT_PATH,
) -> dict[str, float | int]:
    frame = telemetry if isinstance(telemetry, pd.DataFrame) else pd.DataFrame([telemetry])
    scaler, probability_model, health_model = _load_models(artifact_path)
    values = scaler.transform(build_features(frame).to_numpy())
    probability = float(max(0.0, min(1.0, probability_model.predict(values)[0])))
    health = float(max(0.0, min(100.0, health_model.predict(values)[0])))
    predicted_days = max(1, min(365, round(90.0 * (1.0 - probability) + 1.0)))
    return {
        "failure_probability": round(probability, 4),
        "health_score": round(health, 2),
        "predicted_days": predicted_days,
    }


def predict_metro_telemetry(
    telemetry: pd.DataFrame | dict,
    artifact_path: str | Path = METRO_ARTIFACT_PATH,
) -> dict[str, float | int]:
    """Score one MetroPT-3 reading using the trained failure classifier."""
    frame = telemetry if isinstance(telemetry, pd.DataFrame) else pd.DataFrame([telemetry])
    payload = joblib.load(artifact_path)
    feature_columns = payload["feature_columns"]
    features = build_metro_features(frame)
    probability = float(payload["model"].predict_proba(features[feature_columns])[:, 1][0])
    probability = max(0.0, min(1.0, probability))
    health = 100.0 * (1.0 - probability)
    predicted_days = max(1, min(7, round(1.0 + 6.0 * (1.0 - probability))))
    return {
        "failure_probability": round(probability, 4),
        "health_score": round(health, 2),
        "predicted_days": predicted_days,
    }