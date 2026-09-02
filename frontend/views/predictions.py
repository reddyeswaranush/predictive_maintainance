"""Predictions page: model output prioritisation and the incident board."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend import components as ui
from frontend import theme
from frontend.transforms import format_table, number_column, risk_state

INCIDENT_STAGES = ["Open", "In Progress", "Resolved", "Closed"]


def render(predictions: pd.DataFrame, incidents: pd.DataFrame, machines: pd.DataFrame) -> None:
    reference = (
        machines[["machine_id", "machine_name", "location"]]
        if not machines.empty and "machine_id" in machines
        else pd.DataFrame(columns=["machine_id", "machine_name", "location"])
    )

    prediction_tab, incident_tab = st.tabs(["Failure predictions", "Incident board"])
    with prediction_tab:
        _render_predictions(predictions, reference)
    with incident_tab:
        _render_incidents(incidents, reference)


def _render_predictions(predictions: pd.DataFrame, reference: pd.DataFrame) -> None:
    if predictions.empty:
        ui.empty_state("No predictions recorded yet.")
        return

    view = predictions.merge(reference, on="machine_id", how="left").copy()
    view["failure_probability"] = number_column(view, "failure_probability")
    view["health_score"] = number_column(view, "health_score")
    view["priority"] = view["failure_probability"].map(risk_state)

    chart_col, table_col = st.columns([1.1, 1], gap="large")
    with chart_col:
        ui.section("Health against risk", "Each point is one machine")
        figure = px.scatter(
            view,
            x="health_score",
            y="failure_probability",
            size="failure_probability",
            color="priority",
            hover_name="machine_name",
            hover_data=["predicted_days", "location"],
            color_discrete_map=theme.CONDITION_COLORS,
            labels={"health_score": "Health score", "failure_probability": "Failure probability"},
        )
        layout = theme.chart_layout(height=390)
        layout["yaxis"].update({"tickformat": ".0%"})
        figure.update_layout(**layout)
        figure.update_traces(marker={"line": {"width": 0}}, opacity=0.88)
        st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})

    with table_col:
        ui.section("Priority queue", "Act on these first")
        urgent = view.sort_values(["failure_probability", "predicted_days"], ascending=[False, True]).head(8).copy()
        urgent["failure_probability"] = urgent["failure_probability"] * 100
        urgent = urgent.rename(
            columns={
                "machine_name": "Machine",
                "location": "Location",
                "failure_probability": "Risk",
                "health_score": "Health",
                "predicted_days": "Days",
                "priority": "Priority",
            }
        )
        # Priority is intentionally omitted: the Risk bar already encodes it and
        # a sixth column clips at this width.
        urgent = ui.clean_text(urgent, ["Location"])
        ui.data_table(
            format_table(urgent, ["Machine", "Location", "Risk", "Health", "Days"]),
            column_config={
                "Risk": ui.percent_column("Risk"),
                "Health": ui.percent_column("Health"),
                "Days": st.column_config.NumberColumn("Days", help="Predicted days to failure"),
            },
        )

    st.download_button(
        "Export CSV",
        view.to_csv(index=False).encode("utf-8"),
        "prediction_priorities.csv",
        "text/csv",
    )


def _render_incidents(incidents: pd.DataFrame, reference: pd.DataFrame) -> None:
    if incidents.empty:
        ui.empty_state("No incidents recorded yet.")
        return

    view = incidents.merge(reference, on="machine_id", how="left")
    columns = st.columns(len(INCIDENT_STAGES), gap="medium")

    for column, stage in zip(columns, INCIDENT_STAGES):
        with column:
            stage_rows = view[view.get("status", pd.Series(dtype=str)).astype(str).str.lower().eq(stage.lower())]
            ui.section(stage, f"{len(stage_rows)}")
            if stage_rows.empty:
                ui.empty_state("None")
                continue
            for _, incident in stage_rows.iterrows():
                priority = str(incident.get("priority", "low")).lower()
                condition = (
                    "critical" if priority == "critical" else "warning" if priority in {"high", "medium"} else "normal"
                )
                machine_name = incident.get("machine_name") or f"Machine #{incident.get('machine_id')}"
                ui.asset_card(
                    title=str(machine_name),
                    subtitle=str(incident.get("description", "No description")),
                    condition=condition,
                    badges=[ui.state_badge(incident.get("priority", "Low"))],
                    stats=[("Owner", incident.get("assigned_to", "Unassigned"))],
                )
