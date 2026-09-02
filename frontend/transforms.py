"""Data shaping helpers.

The thresholds and the machine/telemetry/prediction merge below are carried
over unchanged from the original implementation so derived values (condition,
health, risk) stay identical.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

# Original thresholds - do not change without a matching backend change.
TEMPERATURE_CRITICAL = 100.0
TEMPERATURE_WARNING = 80.0
RISK_CRITICAL = 0.60
RISK_WARNING = 0.30

HEALTHY_STATES = {"running", "active", "normal", "healthy", "completed", "closed", "resolved", "available"}
ALERT_STATES = {"critical", "maintenance", "inactive", "open", "in progress", "out of stock", "stopped"}


def number_column(frame: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    """Coerce a column to float, tolerating missing columns and bad values."""
    if column not in frame:
        return pd.Series(default, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce").fillna(default)


def temperature_state(value: float) -> str:
    if value >= TEMPERATURE_CRITICAL:
        return "critical"
    if value >= TEMPERATURE_WARNING:
        return "warning"
    return "normal"


def risk_state(value: float) -> str:
    if value >= RISK_CRITICAL:
        return "critical"
    if value >= RISK_WARNING:
        return "warning"
    return "normal"


def format_table(frame: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Project a frame onto the requested columns, skipping absent ones."""
    present = [column for column in columns if column in frame]
    return frame[present] if present else frame


def latest_telemetry(telemetry: pd.DataFrame) -> pd.DataFrame:
    """Most recent reading per machine, using insertion order as the clock."""
    if telemetry.empty or "machine_id" not in telemetry:
        return telemetry.copy()
    ordered = telemetry.sort_values("id") if "id" in telemetry else telemetry
    return ordered.drop_duplicates("machine_id", keep="last")


def build_machine_view(
    machines: pd.DataFrame,
    telemetry: pd.DataFrame,
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    """Join machines with their latest telemetry and prediction rows."""
    machine_view = machines.copy()
    if machine_view.empty:
        return machine_view

    latest = latest_telemetry(telemetry)
    telemetry_columns = [
        column
        for column in ["machine_id", "temperature", "vibration", "power", "rpm", "health_score", "failure_probability"]
        if column in latest
    ]
    if telemetry_columns:
        machine_view = machine_view.merge(
            latest[telemetry_columns], on="machine_id", how="left", suffixes=("", "_telemetry")
        )

    if not predictions.empty and "machine_id" in predictions:
        latest_predictions = (
            predictions.sort_values("id").drop_duplicates("machine_id", keep="last")
            if "id" in predictions
            else predictions
        )
        prediction_columns = [
            column
            for column in ["machine_id", "failure_probability", "health_score", "predicted_days"]
            if column in latest_predictions
        ]
        machine_view = machine_view.merge(
            latest_predictions[prediction_columns],
            on="machine_id",
            how="left",
            suffixes=("_telemetry", "_prediction"),
        )

    machine_view["temperature"] = number_column(machine_view, "temperature")

    risk_columns = [column for column in machine_view if column.startswith("failure_probability")]
    machine_view["failure_probability_display"] = (
        machine_view[risk_columns].bfill(axis=1).iloc[:, 0].fillna(0.0) if risk_columns else 0.0
    )
    health_columns = [column for column in machine_view if column.startswith("health_score")]
    machine_view["health_score_display"] = (
        machine_view[health_columns].bfill(axis=1).iloc[:, 0].fillna(0.0) if health_columns else 0.0
    )

    machine_view["condition"] = machine_view.apply(_row_condition, axis=1)
    return machine_view


def _row_condition(row: pd.Series) -> str:
    risk = risk_state(float(row["failure_probability_display"]))
    temperature = temperature_state(float(row["temperature"]))
    if "critical" in (risk, temperature):
        return "critical"
    if "warning" in (risk, temperature):
        return "warning"
    return "normal"


def apply_filters(
    machine_view: pd.DataFrame,
    locations: list[str],
    statuses: list[str],
    query: str,
) -> pd.DataFrame:
    filtered = machine_view.copy()
    if locations and "location" in filtered:
        filtered = filtered[filtered["location"].isin(locations)]
    if statuses and "status" in filtered:
        filtered = filtered[filtered["status"].isin(statuses)]
    if query:
        searchable = [column for column in ["machine_name", "department", "location"] if column in filtered]
        if searchable:
            mask = (
                filtered[searchable]
                .fillna("")
                .astype(str)
                .apply(lambda column: column.str.contains(query, case=False, na=False))
                .any(axis=1)
            )
            filtered = filtered[mask]
    return filtered


def machine_label(machine_id: int, machines: pd.DataFrame) -> str:
    """Readable label for a machine id, used by every selectbox."""
    if "machine_id" not in machines or machines.empty:
        return f"Machine #{machine_id}"
    matching = machines[machines["machine_id"].eq(machine_id)]
    if matching.empty:
        return f"Machine #{machine_id}"
    return f"{matching.iloc[0]['machine_name']} (#{machine_id})"


def count_status(frame: pd.DataFrame, values: Iterable[str], column: str = "status") -> int:
    """Count rows whose status matches any of `values`, case-insensitively."""
    if frame.empty or column not in frame:
        return 0
    wanted = {value.lower() for value in values}
    return int(frame[column].astype(str).str.lower().isin(wanted).sum())
