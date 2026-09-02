"""Step 2 of the workflow: Welcome.

A short confirmation screen after sign-in. It shows who is signed in, the state
of the service and the size of the fleet, then hands off to the dashboard.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from frontend import components as ui
from frontend import state
from frontend.transforms import count_status


def render(collections: dict[str, pd.DataFrame], health: dict[str, Any]) -> None:
    user = state.current_user()
    name = user.get("name", "there")

    left, middle, right = st.columns([1, 2.4, 1])
    with middle:
        st.markdown(
            f'<div class="fo-welcome fo-animate">'
            f'<div class="fo-welcome-eyebrow">{ui.PRODUCT_NAME}</div>'
            f'<h1 class="fo-welcome-title">Welcome back, {ui.esc(name)}</h1>'
            f'<div class="fo-welcome-sub">Signed in as {ui.esc(user.get("role", "User"))}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.write("")

        machines = collections.get("machines", pd.DataFrame())
        incidents = collections.get("incidents", pd.DataFrame())
        maintenance = collections.get("maintenance", pd.DataFrame())

        ui.metric_row(
            [
                {
                    "label": "Registered assets",
                    "value": str(len(machines)),
                    "detail": "Machines on record",
                },
                {
                    "label": "Open incidents",
                    "value": str(count_status(incidents, ["open", "in progress"])),
                    "detail": "Awaiting resolution",
                },
                {
                    "label": "Service",
                    "value": "Online" if health else "Offline",
                    "detail": "Backend connection",
                    "emphasis": "success" if health else "critical",
                },
            ]
        )

        st.write("")
        _, action, _ = st.columns([1, 1.35, 1])
        with action:
            st.button(
                "Continue to dashboard",
                type="primary",
                width="stretch",
                on_click=state.enter_app,
            )

        if not health:
            st.warning("The backend is unreachable. Start it with: uvicorn backend.api.main:app --reload")
