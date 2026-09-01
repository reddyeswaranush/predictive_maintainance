"""Evaluate the saved models against labelled telemetry."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from ml.predict import _load_models
from ml.train_model import DEFAULT_ARTIFACT, load_training_data
from ml.features import build_features


def evaluate(database_path: str | Path, artifact_path: str | Path = DEFAULT_ARTIFACT) -> dict[str, float | int]:
    data = load_training_data(database_path)
    scaler, probability_model, health_model = _load_models(artifact_path)
    values = scaler.transform(build_features(data).to_numpy())
    probability_error = probability_model.predict(values) - data["failure_probability"].to_numpy()
    health_error = health_model.predict(values) - data["health_score"].to_numpy()
    return {
        "rows": len(data),
        "failure_probability_mae": float(np.abs(probability_error).mean()),
        "health_score_mae": float(np.abs(health_error).mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate FactoryOps maintenance-risk models")
    parser.add_argument("--database", default="factoryops.db")
    parser.add_argument("--artifact", default=str(DEFAULT_ARTIFACT))
    args = parser.parse_args()
    print(evaluate(args.database, args.artifact))


if __name__ == "__main__":
    main()