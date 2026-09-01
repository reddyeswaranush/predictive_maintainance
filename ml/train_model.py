"""Train and persist the predictive-maintenance models.

Run from the project root:
    python -m ml.train_model
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from ml.features import build_features, feature_names
from ml.model import RidgeRegressor
from ml.scaler import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = ROOT / "factoryops.db"
DEFAULT_ARTIFACT = Path(__file__).resolve().parent / "model.json"


def load_training_data(database_path: str | Path = DEFAULT_DATABASE) -> pd.DataFrame:
    with sqlite3.connect(database_path) as connection:
        data = pd.read_sql_query(
            "SELECT * FROM telemetry "
            "WHERE failure_probability IS NOT NULL AND health_score IS NOT NULL",
            connection,
        )
    if len(data) < 5:
        raise ValueError("At least five labelled telemetry rows are required for training")
    return data


def train(database_path: str | Path = DEFAULT_DATABASE, artifact_path: str | Path = DEFAULT_ARTIFACT) -> dict:
    data = load_training_data(database_path)
    features = build_features(data)
    scaler = StandardScaler().fit(features.to_numpy())
    scaled = scaler.transform(features.to_numpy())

    probability_model = RidgeRegressor(alpha=1.0).fit(
        scaled, data["failure_probability"].to_numpy(dtype=float)
    )
    health_model = RidgeRegressor(alpha=1.0).fit(
        scaled, data["health_score"].to_numpy(dtype=float)
    )
    artifact = {
        "version": 1,
        "feature_names": feature_names(),
        "training_rows": len(data),
        "targets": {
            "failure_probability": "telemetry.failure_probability",
            "health_score": "telemetry.health_score",
            "predicted_days": "derived from predicted failure probability; no RUL label exists",
        },
        "scaler": scaler.to_dict(),
        "probability_model": probability_model.to_dict(),
        "health_model": health_model.to_dict(),
    }
    artifact_path = Path(artifact_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Train FactoryOps maintenance-risk models")
    parser.add_argument("--database", default=str(DEFAULT_DATABASE))
    parser.add_argument("--artifact", default=str(DEFAULT_ARTIFACT))
    args = parser.parse_args()
    artifact = train(args.database, args.artifact)
    print(f"Trained on {artifact['training_rows']} telemetry rows")
    print(f"Saved model artifact to {args.artifact}")


if __name__ == "__main__":
    main()