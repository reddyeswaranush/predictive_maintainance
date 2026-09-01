"""Predictions & Incidents - Model outputs and issue queue."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from frontend.utils import number_column, state_badge, format_table, machine_name_for


def render_prediction_incident_page(predictions: pd.DataFrame, incidents: pd.DataFrame, machines: pd.DataFrame) -> None:
    """Render Predictions & Incidents page."""
    pred_tab, incident_tab = st.tabs(["Predictions", "Incidents"])

    with pred_tab:
        if predictions.empty:
            st.info("No predictions available.")
        else:
            st.markdown("#### Failure Predictions")

            columns_to_display = ["machine_id", "failure_probability", "health_score", "predicted_days"]

            display_frame = format_table(predictions[columns_to_display].copy(), columns_to_display)
            display_frame = display_frame.rename(
                columns={
                    "machine_id": "Machine ID",
                    "failure_probability": "Failure Risk",
                    "health_score": "Health Score",
                    "predicted_days": "Days Until Issue",
                }
            )

            st.dataframe(display_frame, use_container_width=True, hide_index=True)

    with incident_tab:
        if incidents.empty:
            st.info("No incidents reported.")
        else:
            st.markdown("#### Reported Issues")

            columns_to_display = ["machine_id", "status", "severity", "reported_at"]

            display_frame = format_table(incidents[columns_to_display].copy(), columns_to_display)
            display_frame = display_frame.rename(
                columns={
                    "machine_id": "Machine ID",
                    "status": "Status",
                    "severity": "Severity",
                    "reported_at": "Reported",
                }
            )

            st.dataframe(display_frame, use_container_width=True, hide_index=True)
