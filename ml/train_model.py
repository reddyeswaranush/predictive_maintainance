"""Train and persist the predictive-maintenance models.

Run from the project root:
    python -m ml.train_model
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import pandas as pd
from xgboost import XGBRegressor

from ml.features import build_features, feature_names


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
    values = features.to_numpy()
    probability_model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        n_jobs=1,
    ).fit(values, data["failure_probability"].to_numpy(dtype=float))
    health_model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        n_jobs=1,
    ).fit(values, data["health_score"].to_numpy(dtype=float))
    artifact_path = Path(artifact_path)
    probability_model_path = artifact_path.with_name(f"{artifact_path.stem}_probability.json")
    health_model_path = artifact_path.with_name(f"{artifact_path.stem}_health.json")
    probability_model_path.parent.mkdir(parents=True, exist_ok=True)
    probability_model.save_model(probability_model_path)
    health_model.save_model(health_model_path)
    artifact = {
        "version": 2,
        "model_type": "xgboost.XGBRegressor",
        "feature_names": feature_names(),
        "training_rows": len(data),
        "targets": {
            "failure_probability": "telemetry.failure_probability",
            "health_score": "telemetry.health_score",
            "predicted_days": "derived from predicted failure probability; no RUL label exists",
        },
        "probability_model": probability_model_path.name,
        "health_model": health_model_path.name,
    }
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