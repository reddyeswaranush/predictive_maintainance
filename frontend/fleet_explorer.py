"""Fleet Explorer - Asset search and management."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from frontend.utils import number_column, state_badge, format_table


def render_fleet_explorer(filtered_machines: pd.DataFrame) -> None:
    """Render Fleet Explorer page."""
    if filtered_machines.empty:
        st.info("No machines found matching your filters.")
        return

    st.markdown("#### Asset Registry")

    columns_to_display = [
        "machine_name",
        "machine_id",
        "department",
        "location",
        "status",
        "temperature",
        "health_score_display",
        "condition",
    ]

    display_frame = format_table(filtered_machines[columns_to_display].copy(), columns_to_display)

    display_frame = display_frame.rename(
        columns={
            "machine_name": "Machine Name",
            "machine_id": "ID",
            "department": "Department",
            "location": "Location",
            "status": "Status",
            "temperature": "Temperature (°C)",
            "health_score_display": "Health",
            "condition": "Condition",
        }
    )

    st.dataframe(display_frame, use_container_width=True, hide_index=True)

    with st.expander("Update Machine Status"):
        st.info("Machine status updates would be performed through the backend API in a production environment.")
