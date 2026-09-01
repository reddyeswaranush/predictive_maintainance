"""Maintenance & Inventory - Work planning and parts tracking."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from frontend.utils import format_table


def render_maintenance_inventory_page(maintenance: pd.DataFrame, inventory: pd.DataFrame, machines: pd.DataFrame) -> None:
    """Render Maintenance & Inventory page."""
    maint_tab, inv_tab = st.tabs(["Maintenance", "Inventory"])

    with maint_tab:
        if maintenance.empty:
            st.info("No maintenance tasks scheduled.")
        else:
            st.markdown("#### Work Queue")

            columns_to_display = ["machine_id", "task_type", "status", "scheduled_date"]

            display_frame = format_table(maintenance[columns_to_display].copy(), columns_to_display)
            display_frame = display_frame.rename(
                columns={
                    "machine_id": "Machine ID",
                    "task_type": "Task Type",
                    "status": "Status",
                    "scheduled_date": "Scheduled",
                }
            )

            st.dataframe(display_frame, use_container_width=True, hide_index=True)

    with inv_tab:
        if inventory.empty:
            st.info("No inventory items available.")
        else:
            st.markdown("#### Parts & Supplies")

            columns_to_display = ["part_name", "quantity", "location", "reorder_level"]

            display_frame = format_table(inventory[columns_to_display].copy(), columns_to_display)
            display_frame = display_frame.rename(
                columns={
                    "part_name": "Part Name",
                    "quantity": "Quantity",
                    "location": "Location",
                    "reorder_level": "Reorder Level",
                }
            )

            st.dataframe(display_frame, use_container_width=True, hide_index=True)
