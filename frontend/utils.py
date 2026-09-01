from typing import Any, Iterable

import pandas as pd
import streamlit as st


def number_column(frame: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    if column not in frame:
        return pd.Series(default, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce").fillna(default)


def temperature_state(value: float) -> str:
    if value >= 100:
        return "critical"
    if value >= 80:
        return "warning"
    return "normal"


def risk_state(value: float) -> str:
    if value >= 0.60:
        return "critical"
    if value >= 0.30:
        return "warning"
    return "normal"


def state_badge(state: str) -> str:
    state = str(state).lower()
    css = (
        "pill-good"
        if state in {"running", "active", "normal", "healthy", "completed", "closed", "resolved"}
        else "pill-bad"
        if state in {"critical", "maintenance", "inactive", "open", "in progress"}
        else "pill-warn"
    )
    return f'<span class="pill {css}">{state.title()}</span>'


def format_table(frame: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    present = [column for column in columns if column in frame]
    return frame[present] if present else frame


def latest_telemetry(telemetry: pd.DataFrame) -> pd.DataFrame:
    if telemetry.empty or "machine_id" not in telemetry:
        return telemetry.copy()
    ordered = telemetry.sort_values("id") if "id" in telemetry else telemetry
    return ordered.drop_duplicates("machine_id", keep="last")


def build_machine_view(machines: pd.DataFrame, telemetry: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
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
        machine_view = machine_view.merge(latest[telemetry_columns], on="machine_id", how="left", suffixes=("", "_telemetry"))
    if not predictions.empty and "machine_id" in predictions:
        latest_predictions = predictions.sort_values("id").drop_duplicates("machine_id", keep="last") if "id" in predictions else predictions
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
    machine_view["condition"] = machine_view.apply(
        lambda row: "critical"
        if risk_state(float(row["failure_probability_display"])) == "critical"
        or temperature_state(float(row["temperature"])) == "critical"
        else "warning"
        if risk_state(float(row["failure_probability_display"])) == "warning"
        or temperature_state(float(row["temperature"])) == "warning"
        else "normal",
        axis=1,
    )
    return machine_view


def chart_layout(height: int = 400) -> dict[str, Any]:
    return {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#2e241b", "family": "Manrope"},
        "margin": {"l": 10, "r": 10, "t": 35, "b": 18},
        "legend": {"orientation": "h", "y": 1.12},
    }


def render_metric_card(label: str, value: str, detail: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-detail">{detail}</div></div>',
        unsafe_allow_html=True,
    )


def machine_name_for(machine_id: int, machines: pd.DataFrame) -> str:
    matching = machines[machines["machine_id"].eq(machine_id)] if "machine_id" in machines else pd.DataFrame()
    return str(matching.iloc[0]["machine_name"]) if not matching.empty else "Unknown Machine"
