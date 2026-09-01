"""Command Center - Fleet condition dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from frontend.utils import number_column, risk_state, state_badge, temperature_state, render_metric_card


def render_command_center(
    filtered_machines: pd.DataFrame, telemetry: pd.DataFrame, incidents: pd.DataFrame, maintenance: pd.DataFrame
) -> None:
    """Render Command Center page."""
    if filtered_machines.empty:
        st.info("No machines found matching your filters.")
        return

    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        render_metric_card("Total Machines", str(len(filtered_machines)), "Active fleet")
    with col2:
        critical = filtered_machines[filtered_machines["condition"] == "critical"]
        render_metric_card("Machines At Risk", str(len(critical)), "Requiring attention")
    with col3:
        incident_count = len(incidents) if not incidents.empty else 0
        render_metric_card("Open Incidents", str(incident_count), "Reported issues")
    with col4:
        maintenance_count = len(maintenance) if not maintenance.empty else 0
        render_metric_card("Maintenance Tasks", str(maintenance_count), "Pending work")

    st.markdown("---")
    st.markdown("#### Fleet Status Overview")

    if not filtered_machines.empty:
        for _, machine in filtered_machines.iterrows():
            condition = str(machine.get("condition", "normal")).lower()
            name = str(machine.get("machine_name", "Unknown"))
            dept = str(machine.get("department", "—"))
            loc = str(machine.get("location", "—"))
            temp = number_column(pd.DataFrame([machine]), "temperature").iloc[0]
            health = number_column(pd.DataFrame([machine]), "health_score_display").iloc[0]
            risk = number_column(pd.DataFrame([machine]), "failure_probability_display").iloc[0]

            st.markdown(
                f"""
                <div class="machine-card {condition}">
                    <div class="machine-card-title">{name}</div>
                    <div class="machine-card-subtitle">{dept} • {loc}</div>
                    <div class="machine-card-metrics">
                        Temp: {temp:.1f}°C | Health: {health:.1%} | Risk: {risk:.1%}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
