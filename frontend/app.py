"""FactoryOps AI Streamlit operations console.

Run alongside the FastAPI service:
    uvicorn backend.api.main:app --reload
    streamlit run app.py
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


st.set_page_config(
    page_title="FactoryOps AI | Operations Console",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv("FACTORYOPS_API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = 4
RESOURCE_LABELS = {
    "machines": "Machines",
    "sensors": "Sensors",
    "telemetry": "Telemetry",
    "predictions": "Predictions",
    "maintenance": "Maintenance",
    "incidents": "Incidents",
    "inventory": "Inventory",
    "notifications": "Notifications",
}

# Demo accounts keep the presentation self-contained. Override the administrator
# account in the environment for shared demonstrations.
DEMO_USERS = {
    os.getenv("FACTORYOPS_ADMIN_USER", "admin").strip().lower(): {
        "password": os.getenv("FACTORYOPS_ADMIN_PASSWORD", "FactoryOps@123"),
        "name": "System Administrator",
        "role": "Administrator",
    },
    "operator": {"password": "Operator@123", "name": "Operations User", "role": "Operator"},
    "maintenance": {"password": "Maintenance@123", "name": "Maintenance User", "role": "Maintenance"},
}


def inject_styles() -> None:
    """Apply a consistent, responsive operations-console visual system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root {
            --page: #080d16; --surface: #101927; --surface-2: #172235;
            --border: #273650; --text: #f3f7ff; --muted: #9aaac4;
            --blue: #70a7ff; --cyan: #5bd6d1; --green: #65cf98;
            --amber: #ffc46b; --red: #ff747d; --purple: #bca5ff;
        }
        .stApp { background: var(--page); color: var(--text); font-family: 'DM Sans', sans-serif; }
        .block-container { max-width: 1550px; padding: 1.35rem 2rem 2.5rem; }
        [data-testid='stHeader'] { background: transparent; }
        [data-testid='stToolbar'] { visibility: hidden; }
        [data-testid='stSidebar'] { background: #0b1320; border-right: 1px solid var(--border); }
        [data-testid='stSidebar'] * { color: var(--text); }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.025em; }
        h1 { font-size: 2rem !important; margin-bottom: .15rem !important; }
        h2 { font-size: 1.3rem !important; margin-top: .4rem !important; }
        .hero { padding: 1.35rem 1.5rem; border: 1px solid var(--border); border-radius: 16px;
                background: radial-gradient(circle at 88% 15%, rgba(112,167,255,.18), transparent 28%), linear-gradient(120deg, #121e30, #0e1725); }
        .eyebrow { color: var(--cyan); font-size: .72rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; }
        .subtle { color: var(--muted); font-size: .9rem; }
        .pill { display: inline-block; padding: .24rem .62rem; border-radius: 999px; font-size: .73rem; font-weight: 700; margin-right: .3rem; }
        .pill-good { color: #86e8b0; background: rgba(101,207,152,.12); border: 1px solid rgba(101,207,152,.32); }
        .pill-warn { color: #ffd48c; background: rgba(255,196,107,.12); border: 1px solid rgba(255,196,107,.32); }
        .pill-bad { color: #ff9ba1; background: rgba(255,116,125,.12); border: 1px solid rgba(255,116,125,.32); }
        .metric-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: .95rem 1.05rem; min-height: 112px; }
        .metric-label { color: var(--muted); text-transform: uppercase; letter-spacing: .08em; font-size: .67rem; font-weight: 700; }
        .metric-value { color: var(--text); font-family: 'Space Grotesk', sans-serif; font-size: 1.75rem; font-weight: 700; margin: .2rem 0; }
        .metric-detail { color: var(--muted); font-size: .78rem; }
        .section-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1rem 1.1rem; }
        .machine-card { background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--blue); border-radius: 10px; padding: .9rem 1rem; min-height: 166px; }
        .machine-card.warning { border-left-color: var(--amber); }
        .machine-card.critical { border-left-color: var(--red); }
        .machine-card h4 { margin: 0; font-family: 'Space Grotesk', sans-serif; }
        .machine-card p { color: var(--muted); font-size: .78rem; margin: .25rem 0 .75rem; }
        .stButton > button, .stDownloadButton > button { border-radius: 8px; border-color: #3b4e70; background: #1b2a43; color: var(--text); font-weight: 600; }
        .stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--blue); color: white; }
        div[data-testid='stMetric'] { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: .65rem .85rem; }
        div[data-testid='stMetricLabel'] { color: var(--muted); }
        div[data-testid='stMetricValue'] { color: var(--text); }
        div[data-baseweb='select'] > div, .stTextInput input, .stNumberInput input { background: #111d2e !important; border-color: #324462 !important; }
        .stTabs [data-baseweb='tab-list'] { gap: .5rem; }
        .stTabs [data-baseweb='tab'] { border-radius: 8px 8px 0 0; color: var(--muted); }
        .stTabs [aria-selected='true'] { color: var(--blue) !important; }
        .login-shell { max-width: 1080px; margin: 7vh auto 0; }
        .login-copy { padding: 2rem 2.2rem 1.5rem 0; }
        .login-copy h1 { font-size: 2.7rem !important; line-height: 1.04; }
        .login-card { background: linear-gradient(145deg, #15233a, #0e1725); border: 1px solid #344867;
                      border-radius: 18px; padding: 1.5rem; box-shadow: 0 22px 60px rgba(0,0,0,.3); }
        .login-mark { width: 42px; height: 42px; border-radius: 11px; display: inline-grid; place-items: center;
                      background: rgba(112,167,255,.16); border: 1px solid rgba(112,167,255,.45); color: var(--blue); font-size: 1.3rem; }
        .user-panel { background: #121f32; border: 1px solid var(--border); border-radius: 10px; padding: .7rem .75rem; margin-bottom: .7rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def api_url(resource: str = "") -> str:
    return f"{API_BASE_URL}/{resource.lstrip('/')}"


def initialise_session() -> None:
    """Create session keys without persisting a password in browser state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = {}


def render_login_page() -> None:
    """Show the presentation login gate before operational data is visible."""
    st.markdown('<div class="login-shell">', unsafe_allow_html=True)
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown(
            '''<div class="login-copy"><div class="eyebrow">Secure operations access</div>
            <h1>Make every maintenance decision count.</h1>
            <p class="subtle">FactoryOps AI unifies live telemetry, risk signals, incidents, maintenance work and inventory readiness in one operations console.</p>
            <div style="margin-top:1.35rem"><span class="pill pill-good">Live monitoring</span><span class="pill pill-warn">Risk prioritization</span><span class="pill pill-good">Maintenance planning</span></div></div>''',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="login-card"><div class="login-mark">⚙</div><h2 style="margin-top:.85rem">Sign in to FactoryOps</h2><p class="subtle">Use your assigned operations account to continue.</p></div>', unsafe_allow_html=True)
        with st.form("factoryops_login", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username", autocomplete="username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", autocomplete="current-password")
            submitted = st.form_submit_button("Sign in", use_container_width=True)
        if submitted:
            account = DEMO_USERS.get(username.strip().lower())
            if account and password == account["password"]:
                st.session_state.authenticated = True
                st.session_state.current_user = {"username": username.strip(), "name": account["name"], "role": account["role"]}
                st.rerun()
            else:
                st.error("Incorrect username or password.")
        with st.expander("Demo access details"):
            st.code("admin / FactoryOps@123", language=None)
            st.caption("Other demo roles: operator / Operator@123, maintenance / Maintenance@123")
    st.markdown("</div>", unsafe_allow_html=True)


@st.cache_data(ttl=15, show_spinner=False)
def get_records(resource: str) -> list[dict[str, Any]]:
    """Fetch a collection endpoint without breaking the UI during an outage."""
    try:
        response = requests.get(api_url(f"{resource}/"), timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []
    except (requests.RequestException, ValueError):
        return []


@st.cache_data(ttl=10, show_spinner=False)
def get_health() -> dict[str, Any]:
    try:
        response = requests.get(api_url("health"), timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}
    except (requests.RequestException, ValueError):
        return {}


def send_record(method: str, resource: str, payload: dict[str, Any], record_id: int | None = None) -> tuple[bool, str]:
    """Perform a state-changing API request and invalidate stale dashboard data."""
    suffix = f"/{record_id}" if record_id is not None else "/"
    try:
        response = requests.request(
            method,
            api_url(f"{resource}{suffix}"),
            json=payload if method != "DELETE" else None,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.ok:
            get_records.clear()
            get_health.clear()
            return True, "Saved successfully."
        detail = response.json().get("detail", response.text)
        return False, f"API returned {response.status_code}: {detail}"
    except (requests.RequestException, ValueError) as error:
        return False, f"Could not contact the API: {error}"


def as_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(records) if records else pd.DataFrame()


def number_column(frame: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    if column not in frame:
        return pd.Series(default, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce").fillna(default)


def temperature_state(value: float) -> str:
    if value >= 100:
        return "critical"
    if value >= 80:
        return "warning"
    return "normal"


def risk_state(value: float) -> str:
    if value >= 0.60:
        return "critical"
    if value >= 0.30:
        return "warning"
    return "normal"


def state_badge(state: str) -> str:
    state = str(state).lower()
    css = "pill-good" if state in {"running", "active", "normal", "healthy", "completed", "closed", "resolved"} else "pill-bad" if state in {"critical", "maintenance", "inactive", "open", "in progress"} else "pill-warn"
    return f'<span class="pill {css}">{state.title()}</span>'


def format_table(frame: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    present = [column for column in columns if column in frame]
    return frame[present] if present else frame


def latest_telemetry(telemetry: pd.DataFrame) -> pd.DataFrame:
    """Use the greatest record ID as the newest reading until timestamps are added."""
    if telemetry.empty or "machine_id" not in telemetry:
        return telemetry.copy()
    ordered = telemetry.sort_values("id") if "id" in telemetry else telemetry
    return ordered.drop_duplicates("machine_id", keep="last")


def build_machine_view(machines: pd.DataFrame, telemetry: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    machine_view = machines.copy()
    if machine_view.empty:
        return machine_view
    latest = latest_telemetry(telemetry)
    telemetry_columns = [column for column in ["machine_id", "temperature", "vibration", "power", "rpm", "health_score", "failure_probability"] if column in latest]
    if telemetry_columns:
        machine_view = machine_view.merge(latest[telemetry_columns], on="machine_id", how="left", suffixes=("", "_telemetry"))
    if not predictions.empty and "machine_id" in predictions:
        latest_predictions = predictions.sort_values("id").drop_duplicates("machine_id", keep="last") if "id" in predictions else predictions
        prediction_columns = [column for column in ["machine_id", "failure_probability", "health_score", "predicted_days"] if column in latest_predictions]
        machine_view = machine_view.merge(latest_predictions[prediction_columns], on="machine_id", how="left", suffixes=("_telemetry", "_prediction"))
    machine_view["temperature"] = number_column(machine_view, "temperature")
    risk_columns = [column for column in machine_view if column.startswith("failure_probability")]
    if risk_columns:
        machine_view["failure_probability_display"] = machine_view[risk_columns].bfill(axis=1).iloc[:, 0].fillna(0.0)
    else:
        machine_view["failure_probability_display"] = 0.0
    health_columns = [column for column in machine_view if column.startswith("health_score")]
    if health_columns:
        machine_view["health_score_display"] = machine_view[health_columns].bfill(axis=1).iloc[:, 0].fillna(0.0)
    else:
        machine_view["health_score_display"] = 0.0
    machine_view["condition"] = machine_view.apply(
        lambda row: "critical" if risk_state(float(row["failure_probability_display"])) == "critical" or temperature_state(float(row["temperature"])) == "critical" else "warning" if risk_state(float(row["failure_probability_display"])) == "warning" or temperature_state(float(row["temperature"])) == "warning" else "normal",
        axis=1,
    )
    return machine_view


def filters_sidebar(machine_view: pd.DataFrame) -> tuple[list[str], list[str], str]:
    st.sidebar.markdown("### Fleet filters")
    locations = sorted(machine_view["location"].dropna().astype(str).unique()) if "location" in machine_view else []
    statuses = sorted(machine_view["status"].dropna().astype(str).unique()) if "status" in machine_view else []
    selected_locations = st.sidebar.multiselect("Locations", locations, placeholder="All locations")
    selected_statuses = st.sidebar.multiselect("Machine status", statuses, placeholder="All statuses")
    query = st.sidebar.text_input("Search machines", placeholder="Name, department, location…")
    return selected_locations, selected_statuses, query


def apply_filters(machine_view: pd.DataFrame, locations: list[str], statuses: list[str], query: str) -> pd.DataFrame:
    filtered = machine_view.copy()
    if locations and "location" in filtered:
        filtered = filtered[filtered["location"].isin(locations)]
    if statuses and "status" in filtered:
        filtered = filtered[filtered["status"].isin(statuses)]
    if query:
        searchable = [column for column in ["machine_name", "department", "location"] if column in filtered]
        if searchable:
            mask = filtered[searchable].fillna("").astype(str).apply(lambda column: column.str.contains(query, case=False, na=False)).any(axis=1)
            filtered = filtered[mask]
    return filtered


def page_header(title: str, description: str, health: dict[str, Any]) -> None:
    state = "Online" if health else "API unavailable"
    badge = "pill-good" if health else "pill-bad"
    st.markdown(
        f'''<div class="hero"><div class="eyebrow">FactoryOps AI · Operations Console</div>
        <h1>{title}</h1><div class="subtle">{description}</div>
        <div style="margin-top:.85rem"><span class="pill {badge}">{state}</span>
        <span class="subtle">API: {API_BASE_URL}</span></div></div>''',
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, detail: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-detail">{detail}</div></div>',
        unsafe_allow_html=True,
    )


def render_command_center(machine_view: pd.DataFrame, telemetry: pd.DataFrame, incidents: pd.DataFrame, maintenance: pd.DataFrame) -> None:
    st.markdown("#### Real-time operational picture")
    total = len(machine_view)
    running = int(machine_view.get("status", pd.Series(dtype=str)).astype(str).str.lower().eq("running").sum())
    critical = int(machine_view.get("condition", pd.Series(dtype=str)).eq("critical").sum())
    warning = int(machine_view.get("condition", pd.Series(dtype=str)).eq("warning").sum())
    average_health = number_column(machine_view, "health_score_display").replace(0, pd.NA).mean()
    average_health = 0 if pd.isna(average_health) else average_health

    metrics = st.columns(5)
    with metrics[0]:
        render_metric_card("Fleet availability", f"{running}/{total}", "Machines currently marked running")
    with metrics[1]:
        render_metric_card("Average health", f"{average_health:.0f}%", "Latest reported health score")
    with metrics[2]:
        render_metric_card("Critical attention", str(critical), "High-risk or overheating assets")
    with metrics[3]:
        render_metric_card("Watch list", str(warning), "Assets outside normal thresholds")
    with metrics[4]:
        open_incidents = int(incidents.get("status", pd.Series(dtype=str)).astype(str).str.lower().isin(["open", "in progress"]).sum())
        render_metric_card("Open incidents", str(open_incidents), "Open and in-progress incident records")

    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown("#### Condition by machine")
        display = machine_view.sort_values(["condition", "failure_probability_display"], ascending=[True, False]).head(12)
        for start in range(0, len(display), 3):
            columns = st.columns(3)
            for column, (_, machine) in zip(columns, display.iloc[start:start + 3].iterrows()):
                with column:
                    condition = str(machine.get("condition", "normal"))
                    st.markdown(
                        f'''<div class="machine-card {condition}"><h4>{machine.get("machine_name", "Unnamed machine")}</h4>
                        <p>{machine.get("location", "Unassigned location")} · {machine.get("department", "Unassigned department")}</p>
                        {state_badge(condition)} {state_badge(machine.get("status", "unknown"))}
                        <div style="margin-top:.8rem" class="metric-label">Temperature / risk</div>
                        <b>{float(machine.get("temperature", 0)):.1f}°C</b> <span class="subtle">· {float(machine.get("failure_probability_display", 0)):.0%}</span></div>''',
                        unsafe_allow_html=True,
                    )
    with right:
        st.markdown("#### Risk radar")
        if machine_view.empty:
            st.info("Add machines and telemetry to populate the risk radar.")
        else:
            chart_data = machine_view.sort_values("failure_probability_display", ascending=False).head(10)
            condition_colours = {"normal": "#65cf98", "warning": "#ffc46b", "critical": "#ff747d"}
            figure = go.Figure(
                go.Bar(
                    x=chart_data["failure_probability_display"],
                    y=chart_data["machine_name"],
                    orientation="h",
                    marker_color=[condition_colours.get(condition, "#70a7ff") for condition in chart_data["condition"]],
                    text=[f"{probability:.0%} · {condition.title()}" for probability, condition in zip(chart_data["failure_probability_display"], chart_data["condition"])],
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>Failure probability: %{x:.1%}<extra></extra>",
                )
            )
            radar_layout = chart_layout(height=max(390, 44 * len(chart_data)))
            radar_layout.update(
                showlegend=False,
                margin={"l": 150, "r": 95, "t": 16, "b": 45},
                yaxis={"categoryorder": "total ascending", "title": None, "automargin": True},
                xaxis={"title": "Failure probability", "tickformat": ".0%", "range": [0, max(0.1, float(chart_data["failure_probability_display"].max()) + 0.15)]},
            )
            figure.update_layout(**radar_layout)
            st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    st.markdown("#### Decision queue")
    queue_left, queue_right = st.columns(2, gap="large")
    with queue_left:
        st.caption("Highest-risk machines")
        columns = ["machine_name", "location", "temperature", "health_score_display", "failure_probability_display", "condition"]
        risk_table = format_table(machine_view.sort_values("failure_probability_display", ascending=False).head(8), columns).copy()
        if "failure_probability_display" in risk_table:
            risk_table["failure_probability_display"] = risk_table["failure_probability_display"].map("{:.1%}".format)
        if "temperature" in risk_table:
            risk_table["temperature"] = risk_table["temperature"].map("{:.1f} °C".format)
        st.dataframe(risk_table, use_container_width=True, hide_index=True)
    with queue_right:
        st.caption("Maintenance workload")
        if maintenance.empty:
            st.info("No maintenance records available.")
        else:
            workload = maintenance.copy()
            if "status" in workload:
                workload = workload[~workload["status"].astype(str).str.lower().isin(["completed", "closed"])]
            st.dataframe(format_table(workload, ["id", "machine_id", "maintenance_type", "technician", "status", "cost"]), use_container_width=True, hide_index=True)

    if not telemetry.empty:
        st.markdown("#### Fleet signal snapshot")
        snapshot = latest_telemetry(telemetry)
        columns = [column for column in ["temperature", "vibration", "power", "rpm"] if column in snapshot]
        if columns:
            summary = snapshot[columns].mean(numeric_only=True).rename("Average").to_frame()
            st.dataframe(summary, use_container_width=True)


def chart_layout(height: int = 400) -> dict[str, Any]:
    return {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#dce7f9", "family": "DM Sans"},
        "margin": {"l": 10, "r": 10, "t": 35, "b": 10},
        "legend": {"orientation": "h", "y": 1.12},
    }


def render_fleet_explorer(machine_view: pd.DataFrame) -> None:
    if machine_view.empty:
        st.info("No machines match the active filters.")
        return
    summary, table = st.tabs(["Fleet map", "Machine register"])
    with summary:
        left, right = st.columns([1, 1.35], gap="large")
        with left:
            status_counts = machine_view.get("status", pd.Series(dtype=str)).fillna("Unspecified").value_counts().rename_axis("Status").reset_index(name="Machines")
            figure = px.pie(status_counts, names="Status", values="Machines", hole=0.65, color="Status", color_discrete_sequence=["#65cf98", "#ffc46b", "#ff747d", "#70a7ff", "#bca5ff"])
            figure.update_layout(**chart_layout(370), showlegend=True)
            st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
        with right:
            location_counts = machine_view.get("location", pd.Series(dtype=str)).fillna("Unassigned").value_counts().rename_axis("Location").reset_index(name="Machines")
            figure = px.bar(location_counts, x="Location", y="Machines", color="Machines", color_continuous_scale=["#203a63", "#70a7ff"], text="Machines")
            figure.update_layout(**chart_layout(370), coloraxis_showscale=False)
            st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
    with table:
        export = machine_view.copy()
        export["failure_probability_display"] = export["failure_probability_display"].map("{:.1%}".format)
        export["temperature"] = export["temperature"].map("{:.1f}".format)
        st.dataframe(format_table(export, ["machine_id", "machine_name", "department", "location", "status", "condition", "temperature", "health_score_display", "failure_probability_display", "predicted_days"]), use_container_width=True, hide_index=True)
        st.download_button("Download filtered fleet CSV", machine_view.to_csv(index=False).encode("utf-8"), "factoryops_fleet.csv", "text/csv")

        with st.expander("Update a machine status"):
            options = machine_view["machine_id"].tolist()
            selected_id = st.selectbox("Machine", options, format_func=lambda identifier: f"#{identifier} · {machine_view.loc[machine_view['machine_id'].eq(identifier), 'machine_name'].iloc[0]}", key="machine_status_select")
            selected = machine_view[machine_view["machine_id"].eq(selected_id)].iloc[0]
            with st.form("update_machine_status"):
                new_status = st.selectbox("Operating status", ["Running", "Idle", "Maintenance", "Stopped"], index=["Running", "Idle", "Maintenance", "Stopped"].index(selected.get("status", "Running")) if selected.get("status", "Running") in ["Running", "Idle", "Maintenance", "Stopped"] else 0)
                if st.form_submit_button("Save status"):
                    payload = {key: selected.get(key) for key in ["machine_name", "department", "location"]}
                    payload["status"] = new_status
                    ok, message = send_record("PUT", "machines", payload, int(selected_id))
                    (st.success if ok else st.error)(message)


def render_telemetry_lab(telemetry: pd.DataFrame, machines: pd.DataFrame) -> None:
    if telemetry.empty:
        st.info("No telemetry exists yet. Use Data Management to record a reading.")
        return
    machine_names = machines[["machine_id", "machine_name"]] if not machines.empty and {"machine_id", "machine_name"}.issubset(machines.columns) else pd.DataFrame(columns=["machine_id", "machine_name"])
    data = telemetry.merge(machine_names, on="machine_id", how="left")
    data["machine_label"] = data["machine_name"].fillna("Unknown machine #" + data["machine_id"].astype(str))
    selected_machine = st.selectbox("Inspect machine", sorted(data["machine_id"].dropna().unique()), format_func=lambda identifier: data.loc[data["machine_id"].eq(identifier), "machine_label"].iloc[0])
    selected = data[data["machine_id"].eq(selected_machine)].sort_values("id") if "id" in data else data[data["machine_id"].eq(selected_machine)]
    latest = selected.iloc[-1]
    metrics = st.columns(5)
    for column, label, suffix in [("temperature", "Temperature", "°C"), ("vibration", "Vibration", ""), ("rpm", "RPM", ""), ("power", "Power", ""), ("oil_level", "Oil level", "%")]:
        with metrics[["temperature", "vibration", "rpm", "power", "oil_level"].index(column)]:
            st.metric(label, f"{float(latest.get(column, 0)):.1f}{suffix}")

    signal_columns = [column for column in ["temperature", "pressure", "vibration", "voltage", "current", "power", "rpm", "humidity", "oil_level"] if column in selected]
    chosen_signals = st.multiselect("Signals", signal_columns, default=signal_columns[:3])
    if chosen_signals:
        figure = go.Figure()
        x_values = selected["id"] if "id" in selected else selected.index
        for signal in chosen_signals:
            figure.add_trace(go.Scatter(x=x_values, y=number_column(selected, signal), mode="lines+markers", name=signal.replace("_", " ").title()))
        figure.update_layout(**chart_layout(430), xaxis_title="Telemetry record ID", yaxis_title="Recorded value")
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
        st.caption("The backend does not yet store timestamps; record ID is used as the sequence indicator.")

    st.markdown("#### Recent raw readings")
    st.dataframe(format_table(selected.sort_values("id", ascending=False), ["id", "machine_id", *signal_columns, "health_score", "failure_probability"]), use_container_width=True, hide_index=True)
    st.download_button("Download inspected telemetry CSV", selected.to_csv(index=False).encode("utf-8"), "telemetry_export.csv", "text/csv")


def render_prediction_incident_page(predictions: pd.DataFrame, incidents: pd.DataFrame, machines: pd.DataFrame) -> None:
    machine_names = machines[["machine_id", "machine_name", "location"]] if not machines.empty else pd.DataFrame(columns=["machine_id", "machine_name", "location"])
    tab_predictions, tab_incidents = st.tabs(["Failure prediction prioritization", "Incident command board"])
    with tab_predictions:
        if predictions.empty:
            st.info("No predictions have been recorded.")
        else:
            view = predictions.merge(machine_names, on="machine_id", how="left").copy()
            view["failure_probability"] = number_column(view, "failure_probability")
            view["health_score"] = number_column(view, "health_score")
            view["priority"] = view["failure_probability"].map(risk_state)
            left, right = st.columns([1.15, 1], gap="large")
            with left:
                figure = px.scatter(view, x="health_score", y="failure_probability", size="failure_probability", color="priority", hover_name="machine_name", hover_data=["predicted_days", "location"], color_discrete_map={"normal": "#65cf98", "warning": "#ffc46b", "critical": "#ff747d"}, labels={"health_score": "Health score", "failure_probability": "Failure probability"})
                figure.update_layout(**chart_layout(410), yaxis_tickformat=".0%")
                st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
            with right:
                st.markdown("#### Immediate attention")
                urgent = view.sort_values(["failure_probability", "predicted_days"], ascending=[False, True]).head(8).copy()
                urgent["failure_probability"] = urgent["failure_probability"].map("{:.1%}".format)
                st.dataframe(format_table(urgent, ["machine_name", "location", "failure_probability", "health_score", "predicted_days", "priority"]), use_container_width=True, hide_index=True)
            st.download_button("Download prediction CSV", view.to_csv(index=False).encode("utf-8"), "prediction_priorities.csv", "text/csv")
    with tab_incidents:
        if incidents.empty:
            st.info("No incidents have been recorded.")
        else:
            view = incidents.merge(machine_names, on="machine_id", how="left")
            status_order = ["Open", "In Progress", "Resolved", "Closed"]
            columns = st.columns(4)
            for column, status in zip(columns, status_order):
                with column:
                    st.markdown(f"##### {status}")
                    cards = view[view.get("status", pd.Series(dtype=str)).astype(str).str.lower().eq(status.lower())]
                    if cards.empty:
                        st.caption("No records")
                    for _, incident in cards.iterrows():
                        priority = str(incident.get("priority", "normal")).lower()
                        css = "critical" if priority == "critical" else "warning" if priority in {"high", "medium"} else "normal"
                        machine_label = incident.get("machine_name") or f"Machine #{incident.get('machine_id')}"
                        st.markdown(f'<div class="machine-card {css}"><b>{machine_label}</b><p>{incident.get("description", "No description")}</p>{state_badge(incident.get("priority", "normal"))}<br><span class="subtle">Owner: {incident.get("assigned_to", "Unassigned")}</span></div>', unsafe_allow_html=True)


def render_maintenance_inventory_page(maintenance: pd.DataFrame, inventory: pd.DataFrame, machines: pd.DataFrame) -> None:
    machine_names = machines[["machine_id", "machine_name"]] if not machines.empty else pd.DataFrame(columns=["machine_id", "machine_name"])
    tab_maintenance, tab_inventory = st.tabs(["Maintenance planning", "Spare-parts readiness"])
    with tab_maintenance:
        if maintenance.empty:
            st.info("No maintenance jobs available.")
        else:
            view = maintenance.merge(machine_names, on="machine_id", how="left")
            left, right = st.columns([1.15, 1], gap="large")
            with left:
                status_counts = view.get("status", pd.Series(dtype=str)).fillna("Unspecified").value_counts().rename_axis("Status").reset_index(name="Jobs")
                figure = px.bar(status_counts, x="Status", y="Jobs", color="Status", text="Jobs", color_discrete_sequence=["#70a7ff", "#ffc46b", "#65cf98", "#ff747d"])
                figure.update_layout(**chart_layout(340), showlegend=False)
                st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
            with right:
                total_cost = number_column(view, "cost").sum()
                scheduled = int(view.get("status", pd.Series(dtype=str)).astype(str).str.lower().isin(["scheduled", "in progress"]).sum())
                st.metric("Recorded maintenance cost", f"{total_cost:,.0f}")
                st.metric("Active / scheduled jobs", scheduled)
            st.dataframe(format_table(view.sort_values("id", ascending=False), ["id", "machine_name", "maintenance_type", "technician", "cost", "remarks", "status"]), use_container_width=True, hide_index=True)
    with tab_inventory:
        if inventory.empty:
            st.info("No inventory records available.")
        else:
            view = inventory.copy()
            view["quantity"] = number_column(view, "quantity")
            left, right = st.columns([1.15, 1], gap="large")
            with left:
                figure = px.bar(view.sort_values("quantity").head(12), x="quantity", y="item_name", orientation="h", color="status", color_discrete_sequence=["#65cf98", "#ffc46b", "#ff747d"], labels={"quantity": "Quantity", "item_name": ""})
                figure.update_layout(**chart_layout(400), yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
            with right:
                low = view[view.get("status", pd.Series(dtype=str)).astype(str).str.lower().str.contains("low")]
                st.markdown("#### Reorder watch")
                st.dataframe(format_table(low, ["item_name", "quantity", "supplier", "status"]), use_container_width=True, hide_index=True)
            st.dataframe(format_table(view.sort_values("quantity"), ["id", "item_name", "quantity", "supplier", "status"]), use_container_width=True, hide_index=True)


def render_data_management(machines: pd.DataFrame, notifications: pd.DataFrame) -> None:
    st.caption("Submit records directly through the FastAPI API. Required fields match the current backend schemas.")
    machine_options = machines["machine_id"].tolist() if "machine_id" in machines else []
    tabs = st.tabs(["Machine", "Telemetry", "Maintenance", "Incident", "Inventory", "Notification", "Sensor"])
    with tabs[0]:
        with st.form("create_machine", clear_on_submit=True):
            left, right = st.columns(2)
            name = left.text_input("Machine name *")
            department = right.text_input("Department")
            location = left.text_input("Location")
            status = right.selectbox("Status", ["Running", "Idle", "Maintenance", "Stopped"])
            if st.form_submit_button("Add machine"):
                if not name.strip():
                    st.error("Machine name is required.")
                else:
                    ok, message = send_record("POST", "machines", {"machine_name": name.strip(), "department": department or None, "location": location or None, "status": status})
                    (st.success if ok else st.error)(message)
    with tabs[1]:
        if not machine_options:
            st.warning("Create a machine before entering telemetry.")
        else:
            with st.form("create_telemetry", clear_on_submit=True):
                machine_id = st.selectbox("Machine *", machine_options, format_func=lambda value: machine_name_for(value, machines), key="telemetry_machine")
                fields = [("temperature", "Temperature"), ("pressure", "Pressure"), ("vibration", "Vibration"), ("voltage", "Voltage"), ("current", "Current"), ("power", "Power"), ("rpm", "RPM"), ("humidity", "Humidity"), ("oil_level", "Oil level"), ("health_score", "Health score"), ("failure_probability", "Failure probability (0–1)")]
                values: dict[str, float] = {}
                columns = st.columns(3)
                for index, (key, label) in enumerate(fields):
                    values[key] = columns[index % 3].number_input(label, min_value=0.0, value=0.0, key=f"telemetry_{key}")
                if st.form_submit_button("Record telemetry"):
                    ok, message = send_record("POST", "telemetry", {"machine_id": machine_id, **values})
                    (st.success if ok else st.error)(message)
    with tabs[2]:
        if machine_options:
            with st.form("create_maintenance", clear_on_submit=True):
                left, right = st.columns(2)
                machine_id = left.selectbox("Machine *", machine_options, format_func=lambda value: machine_name_for(value, machines), key="maintenance_machine")
                maintenance_type = right.selectbox("Type", ["Inspection", "Preventive", "Corrective", "Predictive", "Emergency"])
                technician = left.text_input("Technician *")
                cost = right.number_input("Cost *", min_value=0.0, value=0.0)
                remarks = left.text_input("Remarks *")
                status = right.selectbox("Status", ["Scheduled", "In Progress", "Completed"])
                if st.form_submit_button("Create maintenance job"):
                    if not technician.strip() or not remarks.strip():
                        st.error("Technician and remarks are required.")
                    else:
                        ok, message = send_record("POST", "maintenance", {"machine_id": machine_id, "maintenance_type": maintenance_type, "technician": technician, "cost": cost, "remarks": remarks, "status": status})
                        (st.success if ok else st.error)(message)
    with tabs[3]:
        if machine_options:
            with st.form("create_incident", clear_on_submit=True):
                left, right = st.columns(2)
                machine_id = left.selectbox("Machine *", machine_options, format_func=lambda value: machine_name_for(value, machines), key="incident_machine")
                priority = right.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                description = st.text_area("Description *")
                assigned_to = left.text_input("Assigned to *")
                status = right.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
                if st.form_submit_button("Log incident"):
                    if not description.strip() or not assigned_to.strip():
                        st.error("Description and assignee are required.")
                    else:
                        ok, message = send_record("POST", "incidents", {"machine_id": machine_id, "priority": priority, "description": description, "assigned_to": assigned_to, "status": status})
                        (st.success if ok else st.error)(message)
    with tabs[4]:
        with st.form("create_inventory", clear_on_submit=True):
            left, right = st.columns(2)
            item_name = left.text_input("Item name *")
            quantity = right.number_input("Quantity *", min_value=0, value=0, step=1)
            supplier = left.text_input("Supplier *")
            status = right.selectbox("Stock status", ["Available", "Low Stock", "Out of Stock"])
            if st.form_submit_button("Add inventory item"):
                if not item_name.strip() or not supplier.strip():
                    st.error("Item name and supplier are required.")
                else:
                    ok, message = send_record("POST", "inventory", {"item_name": item_name, "quantity": quantity, "supplier": supplier, "status": status})
                    (st.success if ok else st.error)(message)
    with tabs[5]:
        with st.form("create_notification", clear_on_submit=True):
            title = st.text_input("Title *")
            message = st.text_area("Message *")
            left, right = st.columns(2)
            notification_type = left.selectbox("Type", ["Info", "Alert", "Warning", "Critical"])
            status = right.selectbox("Status", ["Unread", "Read"])
            if st.form_submit_button("Create notification"):
                if not title.strip() or not message.strip():
                    st.error("Title and message are required.")
                else:
                    ok, feedback = send_record("POST", "notifications", {"title": title, "message": message, "notification_type": notification_type, "status": status})
                    (st.success if ok else st.error)(feedback)
        if not notifications.empty:
            st.caption("Latest notifications")
            st.dataframe(format_table(notifications.sort_values("id", ascending=False), ["id", "title", "message", "notification_type", "status"]), use_container_width=True, hide_index=True)
    with tabs[6]:
        with st.form("create_sensor", clear_on_submit=True):
            left, right = st.columns(2)
            sensor_name = left.text_input("Sensor name *")
            location = right.text_input("Location")
            status = left.selectbox("Sensor status", ["Active", "Inactive", "Maintenance"])
            if st.form_submit_button("Add sensor"):
                if not sensor_name.strip():
                    st.error("Sensor name is required.")
                else:
                    ok, message = send_record("POST", "sensors", {"sensor_name": sensor_name, "location": location or None, "status": status})
                    (st.success if ok else st.error)(message)


def machine_name_for(machine_id: int, machines: pd.DataFrame) -> str:
    matching = machines[machines["machine_id"].eq(machine_id)] if "machine_id" in machines else pd.DataFrame()
    return f"#{machine_id} · {matching.iloc[0]['machine_name']}" if not matching.empty else f"Machine #{machine_id}"


def main() -> None:
    inject_styles()
    initialise_session()
    if not st.session_state.authenticated:
        render_login_page()
        return

    health = get_health()

    with st.sidebar:
        st.markdown("## ⚙️ FactoryOps AI")
        st.caption("Predictive maintenance control center")
        user = st.session_state.current_user
        st.markdown(f'<div class="user-panel"><b>{user.get("name", "Signed-in user")}</b><br><span class="subtle">{user.get("role", "User")}</span></div>', unsafe_allow_html=True)
        if st.button("Sign out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = {}
            st.rerun()
        if st.button("↻ Refresh live data", use_container_width=True):
            get_records.clear()
            get_health.clear()
            st.rerun()
        page = st.radio("Navigate", ["Command Center", "Fleet Explorer", "Telemetry Lab", "Predictions & Incidents", "Maintenance & Inventory", "Data Management"], label_visibility="collapsed")
        st.divider()
        st.caption("Connected endpoint")
        st.code(API_BASE_URL, language=None)

    if not health:
        page_header("Connection required", "Start the FastAPI backend to unlock live fleet operations and data entry.", health)
        st.error("The API is unavailable. Run: `uvicorn backend.api.main:app --reload`")
        st.info("The UI is intentionally safe in offline mode: it does not fabricate operational data.")
        return

    collections = {resource: as_frame(get_records(resource)) for resource in RESOURCE_LABELS}
    machine_view = build_machine_view(collections["machines"], collections["telemetry"], collections["predictions"])
    locations, statuses, query = filters_sidebar(machine_view)
    filtered_machines = apply_filters(machine_view, locations, statuses, query)

    copy = {
        "Command Center": ("Command Center", "Prioritize operational attention from fleet condition, health, risk and work queues."),
        "Fleet Explorer": ("Fleet Explorer", "Search and filter every registered asset, then update its operating state."),
        "Telemetry Lab": ("Telemetry Lab", "Inspect recorded machine signals, compare conditions and export data for analysis."),
        "Predictions & Incidents": ("Predictions & Incidents", "Turn model outputs and reported issues into an action-oriented priority queue."),
        "Maintenance & Inventory": ("Maintenance & Inventory", "Plan work, monitor spend and see whether required parts are available."),
        "Data Management": ("Data Management", "Create the operational records that power the dashboard through the FastAPI service."),
    }
    page_header(*copy[page], health)
    st.write("")

    if page == "Command Center":
        render_command_center(filtered_machines, collections["telemetry"], collections["incidents"], collections["maintenance"])
    elif page == "Fleet Explorer":
        render_fleet_explorer(filtered_machines)
    elif page == "Telemetry Lab":
        render_telemetry_lab(collections["telemetry"], collections["machines"])
    elif page == "Predictions & Incidents":
        render_prediction_incident_page(collections["predictions"], collections["incidents"], collections["machines"])
    elif page == "Maintenance & Inventory":
        render_maintenance_inventory_page(collections["maintenance"], collections["inventory"], collections["machines"])
    else:
        render_data_management(collections["machines"], collections["notifications"])


if __name__ == "__main__":
    main()
