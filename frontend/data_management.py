"""Data Management - Operational records and system configuration."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def render_data_management(machines: pd.DataFrame, notifications: pd.DataFrame) -> None:
    """Render Data Management page."""
    machines_tab, notif_tab = st.tabs(["Machines", "Notifications"])

    with machines_tab:
        st.markdown("#### Machine Registry")

        if machines.empty:
            st.info("No machines in the registry.")
        else:
            columns_to_display = ["machine_name", "machine_id", "department", "location", "status"]
            
            present_columns = [col for col in columns_to_display if col in machines.columns]
            display_frame = machines[present_columns].copy() if present_columns else machines.copy()

            display_frame = display_frame.rename(
                columns={
                    "machine_name": "Machine Name",
                    "machine_id": "ID",
                    "department": "Department",
                    "location": "Location",
                    "status": "Status",
                }
            )

            st.dataframe(display_frame, use_container_width=True, hide_index=True)

        with st.expander("Add New Machine"):
            st.info("Machine creation would be performed through the backend API.")

    with notif_tab:
        st.markdown("#### System Notifications")

        if notifications.empty:
            st.info("No notifications.")
        else:
            columns_to_display = ["message", "timestamp", "type"]
            
            present_columns = [col for col in columns_to_display if col in notifications.columns]
            display_frame = notifications[present_columns].copy() if present_columns else notifications.copy()

            display_frame = display_frame.rename(
                columns={
                    "message": "Message",
                    "timestamp": "Time",
                    "type": "Type",
                }
            )

            st.dataframe(display_frame, use_container_width=True, hide_index=True)
