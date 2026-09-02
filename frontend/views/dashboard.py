"""Step 3 of the workflow: Dashboard.

Reduced to the four numbers an operator acts on, the risk ranking and the open
work queue. The raw telemetry panels that previously lived here were removed;
signal history now sits inside the machine detail on the Fleet page.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from frontend import components as ui
from frontend import theme
from frontend.transforms import count_status, format_table, number_column


def render(
    machine_view: pd.DataFrame,
    incidents: pd.DataFrame,
    maintenance: pd.DataFrame,
) -> None:
    _render_metrics(machine_view, incidents, maintenance)

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        ui.section("Failure risk ranking", "Highest predicted risk first")
        _render_risk_chart(machine_view)
    with right:
        ui.section("Needs attention", "Assets outside normal thresholds")
        _render_attention_list(machine_view)

    ui.section("Open work queue", "Maintenance jobs that are not yet complete")
    _render_work_queue(maintenance, machine_view)


def _render_metrics(
    machine_view: pd.DataFrame,
    incidents: pd.DataFrame,
    maintenance: pd.DataFrame,
) -> None:
    total = len(machine_view)
    running = count_status(machine_view, ["running"])
    condition = machine_view.get("condition", pd.Series(dtype=str))
    critical = int(condition.eq("critical").sum())
    warning = int(condition.eq("warning").sum())

    average_health = number_column(machine_view, "health_score_display").replace(0, pd.NA).mean()
    average_health = 0.0 if pd.isna(average_health) else float(average_health)

    open_incidents = count_status(incidents, ["open", "in progress"])
    open_jobs = count_status(maintenance, ["scheduled", "in progress"])

    ui.metric_row(
        [
            {
                "label": "Fleet availability",
                "value": f"{running}/{total}",
                "detail": "Machines currently running",
            },
            {
                "label": "Average health",
                "value": f"{average_health:.0f}",
                "unit": "%",
                "detail": "Across reporting assets",
                "emphasis": "success" if average_health >= 70 else "warning",
            },
            {
                "label": "Critical assets",
                "value": str(critical),
                "detail": f"{warning} more on the watch list",
                "emphasis": "critical" if critical else "default",
            },
            {
                "label": "Open work",
                "value": str(open_incidents + open_jobs),
                "detail": f"{open_incidents} incidents · {open_jobs} jobs",
                "emphasis": "warning" if (open_incidents + open_jobs) else "default",
            },
        ]
    )


def _render_risk_chart(machine_view: pd.DataFrame) -> None:
    if machine_view.empty:
        ui.empty_state("No machines registered yet. Add assets from the Records page.")
        return

    data = machine_view.sort_values("failure_probability_display", ascending=False).head(8)
    colors = [theme.CONDITION_COLORS.get(condition, theme.COLORS["accent"]) for condition in data["condition"]]

    figure = go.Figure(
        go.Bar(
            x=data["failure_probability_display"],
            y=data["machine_name"],
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            width=0.62,
            text=[f"{value:.0%}" for value in data["failure_probability_display"]],
            textposition="outside",
            textfont={"color": theme.COLORS["text_muted"], "size": 11},
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Failure probability: %{x:.1%}<extra></extra>",
        )
    )
    layout = theme.chart_layout(height=max(300, 44 * len(data)))
    layout.update(
        showlegend=False,
        margin={"l": 6, "r": 46, "t": 8, "b": 28},
        bargap=0.34,
    )
    layout["yaxis"].update({"categoryorder": "total ascending", "automargin": True, "title": None})
    layout["xaxis"].update(
        {
            "tickformat": ".0%",
            "range": [0, max(0.1, float(data["failure_probability_display"].max()) + 0.18)],
            "title": None,
        }
    )
    figure.update_layout(**layout)
    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})


def _render_attention_list(machine_view: pd.DataFrame) -> None:
    if machine_view.empty:
        ui.empty_state("No assets to review.")
        return

    flagged = machine_view[machine_view["condition"].isin(["critical", "warning"])]
    flagged = flagged.sort_values("failure_probability_display", ascending=False).head(4)

    if flagged.empty:
        ui.empty_state("All assets are operating within normal thresholds.")
        return

    for _, machine in flagged.iterrows():
        condition = str(machine.get("condition", "normal"))
        ui.asset_card(
            title=machine.get("machine_name", "Unnamed machine"),
            subtitle=f"{machine.get('location', 'Unassigned')} · {machine.get('department', 'Unassigned')}",
            condition=condition,
            badges=[ui.state_badge(condition), ui.state_badge(machine.get("status", "unknown"))],
            stats=[
                ("Temp", f"{float(machine.get('temperature', 0)):.1f} °C"),
                ("Health", f"{float(machine.get('health_score_display', 0)):.0f}%"),
                ("Risk", f"{float(machine.get('failure_probability_display', 0)):.0%}"),
            ],
        )


def _render_work_queue(maintenance: pd.DataFrame, machine_view: pd.DataFrame) -> None:
    if maintenance.empty:
        ui.empty_state("No maintenance jobs recorded.")
        return

    queue = maintenance.copy()
    if not machine_view.empty and {"machine_id", "machine_name"}.issubset(machine_view.columns):
        queue = queue.merge(machine_view[["machine_id", "machine_name"]], on="machine_id", how="left")

    if "status" in queue:
        queue = queue[~queue["status"].astype(str).str.lower().isin(["completed", "closed"])]

    if queue.empty:
        ui.empty_state("Every maintenance job is complete.")
        return

    queue = queue.rename(
        columns={
            "machine_name": "Machine",
            "maintenance_type": "Type",
            "technician": "Technician",
            "status": "Status",
            "cost": "Cost",
        }
    )
    queue = ui.titleize(queue, ["Status", "Type"])
    queue = ui.clean_text(queue, ["Machine", "Technician"])
    ui.data_table(
        format_table(queue, ["Machine", "Type", "Technician", "Status", "Cost"]),
        column_config={"Cost": ui.currency_column()},
    )
