"""Feature engineering shared by training and inference."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


BASE_FEATURES = [
    "temperature",
    "pressure",
    "vibration",
    "voltage",
    "current",
    "power",
    "rpm",
    "humidity",
    "oil_level",
]


def build_features(data: pd.DataFrame) -> pd.DataFrame:
    """Build deterministic sensor features from raw telemetry.

    Target columns are intentionally not used here to prevent target leakage.
    """
    missing = [column for column in BASE_FEATURES if column not in data.columns]
    if missing:
        raise ValueError(f"Telemetry is missing required columns: {', '.join(missing)}")

    frame = data[BASE_FEATURES].copy()
    frame = frame.apply(pd.to_numeric, errors="coerce")
    if frame.isna().any().any():
        raise ValueError("Telemetry contains missing or non-numeric sensor values")

    frame["temperature_pressure_ratio"] = frame["temperature"] / frame["pressure"].clip(lower=0.001)
    frame["electrical_load"] = frame["voltage"] * frame["current"]
    frame["rpm_per_power"] = frame["rpm"] / frame["power"].clip(lower=0.001)
    frame["oil_depletion"] = 100.0 - frame["oil_level"]
    frame["thermal_vibration_index"] = frame["temperature"] * (1.0 + frame["vibration"])
    return frame


def feature_names() -> list[str]:
    return [
        *BASE_FEATURES,
        "temperature_pressure_ratio",
        "electrical_load",
        "rpm_per_power",
        "oil_depletion",
        "thermal_vibration_index",
    ]


METRO_ANALOG_FEATURES = [
    "TP2",
    "TP3",
    "H1",
    "DV_pressure",
    "Reservoirs",
    "Oil_temperature",
    "Motor_current",
]
METRO_DIGITAL_FEATURES = [
    "COMP",
    "DV_eletric",
    "Towers",
    "MPG",
    "LPS",
    "Pressure_switch",
    "Oil_level",
    "Caudal_impulses",
]
METRO_ROLLING_WINDOWS = (5, 30, 120)


def normalize_metro_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize known spelling/casing differences between dataset mirrors."""
    frame = data.rename(
        columns={
            "DV_electric": "DV_eletric",
            "Caudal_impulse": "Caudal_impulses",
            "Unnamed: 0": "source_row",
        }
    ).copy()
    required = {"timestamp", *METRO_ANALOG_FEATURES, *METRO_DIGITAL_FEATURES}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"MetroPT-3 data is missing columns: {', '.join(missing)}")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    if frame["timestamp"].isna().any():
        raise ValueError("MetroPT-3 contains invalid timestamps")
    for column in [*METRO_ANALOG_FEATURES, *METRO_DIGITAL_FEATURES]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame[[*METRO_ANALOG_FEATURES, *METRO_DIGITAL_FEATURES]].isna().any().any():
        raise ValueError("MetroPT-3 contains missing or non-numeric sensor values")
    return frame


def metro_feature_names() -> list[str]:
    names = [*METRO_ANALOG_FEATURES, *METRO_DIGITAL_FEATURES]
    for column in METRO_ANALOG_FEATURES:
        for window in METRO_ROLLING_WINDOWS:
            names.extend([f"{column}_mean_{window}m", f"{column}_std_{window}m"])
        names.append(f"{column}_diff")
    return names


def build_metro_features(data: pd.DataFrame) -> pd.DataFrame:
    """Create causal minute-level level, trend, and volatility features."""
    frame = normalize_metro_columns(data).sort_values("timestamp").copy()
    frame = frame.set_index("timestamp")
    result = frame[[*METRO_ANALOG_FEATURES, *METRO_DIGITAL_FEATURES]].copy()
    for column in METRO_ANALOG_FEATURES:
        for window in METRO_ROLLING_WINDOWS:
            rolling = frame[column].rolling(window, min_periods=1)
            result[f"{column}_mean_{window}m"] = rolling.mean()
            result[f"{column}_std_{window}m"] = rolling.std().fillna(0.0)
        result[f"{column}_diff"] = frame[column].diff().fillna(0.0)
    return result.reset_index()