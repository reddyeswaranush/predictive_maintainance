"""FactoryOps operations console.

Run alongside the FastAPI service:
    uvicorn backend.api.main:app --reload
    streamlit run frontend/app.py

This module is only a router. Presentation lives in `frontend/views`, shared UI
in `frontend/components.py`, styling in `frontend/theme.py` and backend access
in `frontend/api.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

st.set_page_config(
    page_title="FactoryOps | Predictive Maintenance",
    page_icon="◧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from frontend import api  # noqa: E402
from frontend import components as ui  # noqa: E402
from frontend import state, theme  # noqa: E402
from frontend.transforms import build_machine_view  # noqa: E402
from frontend.views import dashboard, fleet, login, maintenance, predictions, records, welcome  # noqa: E402


def main() -> None:
    theme.apply_theme()
    state.initialise_session()

    if not st.session_state.authenticated:
        login.render()
        return

    health = api.get_health()
    collections = api.load_collections()

    if st.session_state.screen == state.SCREEN_WELCOME:
        welcome.render(collections, health)
        return

    ui.render_header(health)
    _render_route(collections, health)
    ui.render_footer(health)


def _render_route(collections, health) -> None:
    route = state.active_route()
    machine_view = build_machine_view(
        collections["machines"], collections["telemetry"], collections["predictions"]
    )

    if not health:
        ui.page_head("Service unavailable", [ui.service_badge(health)])
        st.error("The backend is not responding. Start it with: uvicorn backend.api.main:app --reload")
        return

    if route == "dashboard":
        ui.page_head(
            "Dashboard",
            [ui.badge(f"{len(machine_view)} assets", "info"), ui.service_badge(health)],
        )
        dashboard.render(machine_view, collections["incidents"], collections["maintenance"])

    elif route == "fleet":
        ui.page_head("Fleet", [ui.badge(f"{len(machine_view)} assets", "info")])
        filtered = fleet.render_filters(machine_view)
        fleet.render(filtered, collections["telemetry"])

    elif route == "predictions":
        ui.page_head(
            "Predictions",
            [
                ui.badge(f"{len(collections['predictions'])} predictions", "info"),
                ui.badge(f"{len(collections['incidents'])} incidents", "mute"),
            ],
        )
        predictions.render(collections["predictions"], collections["incidents"], collections["machines"])

    elif route == "maintenance":
        ui.page_head(
            "Maintenance",
            [
                ui.badge(f"{len(collections['maintenance'])} jobs", "info"),
                ui.badge(f"{len(collections['inventory'])} parts", "mute"),
            ],
        )
        maintenance.render(collections["maintenance"], collections["inventory"], collections["machines"])

    else:
        ui.page_head("Records", [ui.service_badge(health)])
        records.render(collections)


if __name__ == "__main__":
    main()
