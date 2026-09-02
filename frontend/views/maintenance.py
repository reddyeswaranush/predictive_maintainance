"""Maintenance page: work planning and spare-parts readiness."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend import components as ui
from frontend import theme
from frontend.transforms import count_status, format_table, number_column


def render(maintenance: pd.DataFrame, inventory: pd.DataFrame, machines: pd.DataFrame) -> None:
    reference = (
        machines[["machine_id", "machine_name"]]
        if not machines.empty and "machine_id" in machines
        else pd.DataFrame(columns=["machine_id", "machine_name"])
    )

    work_tab, parts_tab = st.tabs(["Work orders", "Spare parts"])
    with work_tab:
        _render_work_orders(maintenance, reference)
    with parts_tab:
        _render_inventory(inventory)


def _render_work_orders(maintenance: pd.DataFrame, reference: pd.DataFrame) -> None:
    if maintenance.empty:
        ui.empty_state("No maintenance jobs recorded yet.")
        return

    view = maintenance.merge(reference, on="machine_id", how="left")
    total_cost = number_column(view, "cost").sum()
    active = count_status(view, ["scheduled", "in progress"])
    completed = count_status(view, ["completed"])

    ui.metric_row(
        [
            {"label": "Total jobs", "value": str(len(view)), "detail": "All recorded work orders"},
            {"label": "Active", "value": str(active), "detail": "Scheduled or in progress",
             "emphasis": "warning" if active else "default"},
            {"label": "Completed", "value": str(completed), "detail": "Closed out", "emphasis": "success"},
            {"label": "Recorded cost", "value": f"{total_cost:,.0f}", "detail": "Across all jobs"},
        ]
    )

    chart_col, table_col = st.columns([1, 1.35], gap="large")
    with chart_col:
        ui.section("Jobs by status")
        counts = (
            view.get("status", pd.Series(dtype=str))
            .fillna("Unspecified")
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Jobs")
        )
        figure = px.bar(
            counts, x="Status", y="Jobs", text="Jobs",
            color="Status", color_discrete_sequence=theme.CATEGORICAL_SEQUENCE,
        )
        layout = theme.chart_layout(height=320)
        figure.update_layout(**layout, showlegend=False)
        figure.update_traces(textposition="outside", textfont={"color": theme.COLORS["text_muted"]}, width=0.55)
        st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})

    with table_col:
        ui.section("Work orders")
        table = view.rename(
            columns={
                "machine_name": "Machine",
                "maintenance_type": "Type",
                "technician": "Technician",
                "cost": "Cost",
                "remarks": "Remarks",
                "status": "Status",
            }
        )
        if "id" in table:
            table = table.sort_values("id", ascending=False)
        table = ui.titleize(table, ["Status", "Type"])
        table = ui.clean_text(table, ["Machine", "Technician", "Remarks"])
        ui.data_table(
            format_table(table, ["Machine", "Type", "Technician", "Cost", "Status", "Remarks"]),
            column_config={"Cost": ui.currency_column()},
            height=320,
        )


def _render_inventory(inventory: pd.DataFrame) -> None:
    if inventory.empty:
        ui.empty_state("No inventory records yet.")
        return

    view = inventory.copy()
    view["quantity"] = number_column(view, "quantity")
    low_stock = view[view.get("status", pd.Series(dtype=str)).astype(str).str.lower().str.contains("low|out", na=False)]

    ui.metric_row(
        [
            {"label": "Line items", "value": str(len(view)), "detail": "Distinct parts tracked"},
            {"label": "Units on hand", "value": f"{view['quantity'].sum():,.0f}", "detail": "Total quantity"},
            {"label": "Needs reorder", "value": str(len(low_stock)), "detail": "Low or out of stock",
             "emphasis": "critical" if len(low_stock) else "success"},
        ]
    )

    view = view.rename(
        columns={"item_name": "Item", "quantity": "Quantity", "supplier": "Supplier", "status": "Status"}
    )

    chart_col, table_col = st.columns([1, 1.35], gap="large")
    with chart_col:
        ui.section("Lowest stock levels")
        figure = px.bar(
            view.sort_values("Quantity").head(10),
            x="Quantity", y="Item", orientation="h",
            color="Status", color_discrete_sequence=theme.CATEGORICAL_SEQUENCE,
        )
        layout = theme.chart_layout(height=360)
        layout["yaxis"].update({"categoryorder": "total ascending", "title": None})
        figure.update_layout(**layout)
        st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})

    with table_col:
        ui.section("Parts register")
        ui.data_table(
            format_table(ui.titleize(view.sort_values("Quantity"), ["Status"]),
                         ["Item", "Quantity", "Supplier", "Status"]),
            height=360,
        )
