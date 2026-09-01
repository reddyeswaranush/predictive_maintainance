"""Chunked MetroPT-3 training and evaluation pipeline.

Run from the project root:
    .venv\\Scripts\\python.exe -m ml.metropt_pipeline train
    .venv\\Scripts\\python.exe -m ml.metropt_pipeline evaluate
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, classification_report, roc_auc_score

from ml.features import (
    METRO_ANALOG_FEATURES,
    METRO_DIGITAL_FEATURES,
    build_metro_features,
    metro_feature_names,
    normalize_metro_columns,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "metropt3" / "MetroPT3(AirCompressor).csv"
DEFAULT_ARTIFACT = ROOT / "ml" / "metropt_model.joblib"
LEAD_TIME = pd.Timedelta(hours=24)
CHUNK_SIZE = 250_000

FAILURE_EVENTS = [
    ("2020-04-18 00:00:00", "2020-04-18 23:59:00"),
    ("2020-05-29 23:30:00", "2020-05-30 06:00:00"),
    ("2020-06-05 10:00:00", "2020-06-07 14:30:00"),
    ("2020-07-15 14:30:00", "2020-07-15 19:00:00"),
]


def failure_events() -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    return [(pd.Timestamp(start), pd.Timestamp(end)) for start, end in FAILURE_EVENTS]


def load_minute_data(path: str | Path = DEFAULT_CSV) -> pd.DataFrame:
    """Read the 1-second CSV in chunks and reduce it to one row per minute."""
    usecols = [
        "timestamp",
        *METRO_ANALOG_FEATURES,
        *METRO_DIGITAL_FEATURES,
        "DV_eletric",
        "DV_electric",
        "Caudal_impulses",
        "Caudal_impulse",
    ]
    parts: list[pd.DataFrame] = []
    for chunk in pd.read_csv(path, usecols=lambda column: column in usecols, chunksize=CHUNK_SIZE):
        frame = normalize_metro_columns(chunk)
        frame["minute"] = frame["timestamp"].dt.floor("min")
        grouped = frame.groupby("minute", sort=True)[
            [*METRO_ANALOG_FEATURES, *METRO_DIGITAL_FEATURES]
        ].mean()
        parts.append(grouped)
    if not parts:
        raise ValueError("MetroPT-3 CSV did not contain any rows")
    minute_data = pd.concat(parts).groupby(level=0).mean().sort_index()
    minute_data.index.name = "timestamp"
    return minute_data.reset_index()


def add_labels(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    frame["label"] = 0
    frame["event_id"] = -1
    for event_id, (start, end) in enumerate(failure_events()):
        imminent = (frame["timestamp"] >= start - LEAD_TIME) & (frame["timestamp"] <= start)
        during = (frame["timestamp"] > start) & (frame["timestamp"] <= end)
        frame.loc[imminent, ["label", "event_id"]] = [1, event_id]
        frame = frame.loc[~during]
    return frame.reset_index(drop=True)


def prepare_dataset(csv_path: str | Path = DEFAULT_CSV) -> pd.DataFrame:
    minute_data = load_minute_data(csv_path)
    labelled = add_labels(minute_data)
    features = build_metro_features(labelled)
    labels = labelled[["timestamp", "label", "event_id"]]
    return features.merge(labels, on="timestamp", how="inner")


def _classifier() -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )


def train(
    csv_path: str | Path = DEFAULT_CSV,
    artifact_path: str | Path = DEFAULT_ARTIFACT,
) -> dict:
    data = prepare_dataset(csv_path)
    feature_columns = metro_feature_names()
    model = _classifier().fit(data[feature_columns], data["label"])
    payload = {
        "version": 1,
        "dataset": "MetroPT-3 Air Compressor",
        "csv_path": str(csv_path),
        "feature_columns": feature_columns,
        "lead_time_hours": 24,
        "training_rows": int(len(data)),
        "positive_rows": int(data["label"].sum()),
        "failure_events": [
            {"start": start.isoformat(), "end": end.isoformat()}
            for start, end in failure_events()
        ],
        "model": model,
    }
    artifact_path = Path(artifact_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, artifact_path)
    return {key: value for key, value in payload.items() if key != "model"}


def evaluate(
    csv_path: str | Path = DEFAULT_CSV,
    artifact_path: str | Path = DEFAULT_ARTIFACT,
) -> dict:
    data = prepare_dataset(csv_path)
    payload = joblib.load(artifact_path)
    feature_columns = payload["feature_columns"]
    results = []
    for event_id in range(len(failure_events())):
        test = data[data["event_id"].eq(event_id)]
        normal = data[data["label"].eq(0)]
        if test.empty:
            continue
        train_data = data[data["event_id"].ne(event_id)]
        model = _classifier().fit(train_data[feature_columns], train_data["label"])
        normal_sample = normal.sample(min(5000, len(normal)), random_state=42)
        evaluation = pd.concat([test, normal_sample], ignore_index=True)
        probabilities = model.predict_proba(evaluation[feature_columns])[:, 1]
        results.append(
            {
                "event": event_id,
                "rows": len(evaluation),
                "roc_auc": float(roc_auc_score(evaluation["label"], probabilities)),
                "pr_auc": float(average_precision_score(evaluation["label"], probabilities)),
            }
        )
    return {
        "rows": len(data),
        "positive_rows": int(data["label"].sum()),
        "events": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="MetroPT-3 predictive-maintenance pipeline")
    parser.add_argument("command", choices=["train", "evaluate"])
    parser.add_argument("--csv", default=str(DEFAULT_CSV))
    parser.add_argument("--artifact", default=str(DEFAULT_ARTIFACT))
    args = parser.parse_args()
    result = train(args.csv, args.artifact) if args.command == "train" else evaluate(args.csv, args.artifact)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
