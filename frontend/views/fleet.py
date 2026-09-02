"""Fleet page: asset registry, filtering and per-machine detail.

The former standalone "Telemetry Lab" page was folded in here as an on-demand
signal history inside the machine detail, so the reading history is still
available without a permanent dashboard of raw sensor panels.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from frontend import api
from frontend import components as ui
from frontend import theme
from frontend.transforms import apply_filters, format_table, number_column

SIGNALS = ["temperature", "pressure", "vibration", "voltage", "current", "power", "rpm", "humidity", "oil_level"]
STATUS_OPTIONS = ["Running", "Idle", "Maintenance", "Stopped"]


def render_filters(machine_view: pd.DataFrame) -> pd.DataFrame:
    """Filter bar. Scoped to this page rather than shown on every screen."""
    locations = sorted(machine_view["location"].dropna().astype(str).unique()) if "location" in machine_view else []
    statuses = sorted(machine_view["status"].dropna().astype(str).unique()) if "status" in machine_view else []

    search_col, location_col, status_col = st.columns([2, 1, 1], gap="medium")
    with search_col:
        query = st.text_input("Search", placeholder="Machine, department or location", label_visibility="collapsed")
    with location_col:
        selected_locations = st.multiselect("Location", locations, placeholder="All locations", label_visibility="collapsed")
    with status_col:
        selected_statuses = st.multiselect("Status", statuses, placeholder="All statuses", label_visibility="collapsed")

    return apply_filters(machine_view, selected_locations, selected_statuses, query)


def render(filtered: pd.DataFrame, telemetry: pd.DataFrame) -> None:
    if filtered.empty:
        ui.empty_state("No machines match the current filters.")
        return

    ui.section("Asset registry", f"{len(filtered)} machine(s) shown")
    _render_registry(filtered)
    ui.section("Machine detail", "Inspect and update a single asset")
    _render_detail(filtered, telemetry)


def _render_registry(filtered: pd.DataFrame) -> None:
    table = filtered.copy()
    table["failure_probability_display"] = number_column(table, "failure_probability_display") * 100
    table = table.rename(
        columns={
            "machine_name": "Machine",
            "department": "Department",
            "location": "Location",
            "status": "Status",
            "condition": "Condition",
            "temperature": "Temperature",
            "health_score_display": "Health",
            "failure_probability_display": "Risk",
        }
    )
    table = ui.titleize(table, ["Status", "Condition"])
    table = ui.clean_text(table, ["Department", "Location"])
    ui.data_table(
        format_table(table, ["Machine", "Department", "Location", "Status", "Condition", "Temperature", "Health", "Risk"]),
        column_config={
            "Temperature": ui.temperature_column(),
            "Health": ui.percent_column("Health", "Latest reported health score"),
            "Risk": ui.percent_column("Risk", "Predicted failure probability"),
        },
    )
    st.download_button(
        "Export CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        "factoryops_fleet.csv",
        "text/csv",
    )


def _render_detail(filtered: pd.DataFrame, telemetry: pd.DataFrame) -> None:
    options = filtered["machine_id"].tolist()
    selected_id = st.selectbox(
        "Machine",
        options,
        format_func=lambda identifier: str(
            filtered.loc[filtered["machine_id"].eq(identifier), "machine_name"].iloc[0]
        ),
        key="fleet_detail_machine",
        label_visibility="collapsed",
    )
    machine = filtered[filtered["machine_id"].eq(selected_id)].iloc[0]

    summary_col, action_col = st.columns([1.6, 1], gap="large")
    with summary_col:
        ui.asset_card(
            title=machine.get("machine_name", "Unnamed machine"),
            subtitle=f"{machine.get('department', 'Unassigned')} · {machine.get('location', 'Unassigned')}",
            condition=str(machine.get("condition", "normal")),
            badges=[ui.state_badge(machine.get("condition", "normal")), ui.state_badge(machine.get("status", "unknown"))],
            stats=[
                ("Temperature", f"{float(machine.get('temperature', 0)):.1f} °C"),
                ("Health", f"{float(machine.get('health_score_display', 0)):.0f}%"),
                ("Failure risk", f"{float(machine.get('failure_probability_display', 0)):.0%}"),
            ],
        )
    with action_col:
        _render_status_form(machine, selected_id)

    _render_signal_history(telemetry, selected_id)


def _render_status_form(machine: pd.Series, machine_id: int) -> None:
    current_status = machine.get("status", "Running")
    index = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0

    with st.form("update_machine_status", border=False):
        new_status = st.selectbox("Operating status", STATUS_OPTIONS, index=index)
        if st.form_submit_button("Update status", type="primary", width="stretch"):
            payload = {key: machine.get(key) for key in ["machine_name", "department", "location"]}
            payload["status"] = new_status
            ok, message = api.send_record("PUT", "machines", payload, int(machine_id))
            (st.success if ok else st.error)(message)


def _render_signal_history(telemetry: pd.DataFrame, machine_id: int) -> None:
    with st.expander("Signal history"):
        if telemetry.empty or "machine_id" not in telemetry:
            ui.empty_state("No telemetry recorded for this machine.")
            return

        readings = telemetry[telemetry["machine_id"].eq(machine_id)]
        if readings.empty:
            ui.empty_state("No telemetry recorded for this machine.")
            return

        readings = readings.sort_values("id") if "id" in readings else readings
        available = [signal for signal in SIGNALS if signal in readings]
        chosen = st.multiselect(
            "Signals",
            available,
            default=available[:3],
            format_func=lambda name: name.replace("_", " ").title(),
        )
        if not chosen:
            return

        figure = go.Figure()
        x_values = readings["id"] if "id" in readings else readings.index
        for position, signal in enumerate(chosen):
            figure.add_trace(
                go.Scatter(
                    x=x_values,
                    y=number_column(readings, signal),
                    mode="lines+markers",
                    name=signal.replace("_", " ").title(),
                    line={"width": 2, "color": theme.CATEGORICAL_SEQUENCE[position % len(theme.CATEGORICAL_SEQUENCE)]},
                    marker={"size": 5},
                )
            )
        layout = theme.chart_layout(height=330)
        layout["xaxis"].update({"title": "Reading sequence"})
        layout["yaxis"].update({"title": "Value"})
        figure.update_layout(**layout)
        st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
        st.caption("Readings are ordered by capture sequence; the backend does not store timestamps.")
