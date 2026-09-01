"""Telemetry Lab - Signal analysis and inspection."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from frontend.utils import number_column, latest_telemetry, format_table


def render_telemetry_lab(telemetry: pd.DataFrame, machines: pd.DataFrame) -> None:
    """Render Telemetry Lab page."""
    if telemetry.empty:
        st.info("No telemetry data available.")
        return

    st.markdown("#### Signal History")

    latest = latest_telemetry(telemetry)

    columns_to_display = [
        "machine_id",
        "temperature",
        "vibration",
        "power",
        "rpm",
        "health_score",
        "timestamp",
    ]

    display_frame = format_table(latest[columns_to_display].copy(), columns_to_display)

    display_frame = display_frame.rename(
        columns={
            "machine_id": "Machine ID",
            "temperature": "Temperature (°C)",
            "vibration": "Vibration",
            "power": "Power (W)",
            "rpm": "RPM",
            "health_score": "Health Score",
            "timestamp": "Recorded At",
        }
    )

    st.dataframe(display_frame, use_container_width=True, hide_index=True)

    with st.expander("Signal Comparison"):
        st.info("Select machines to compare their signal patterns over time.")
        left, right = st.columns(2, gap="small")
        with left:
            st.write("Machine 1 selection would appear here")
        with right:
            st.write("Machine 2 selection would appear here")

    with st.expander("Export Telemetry"):
        st.write("Export options for telemetry data analysis")
