"""FactoryOps AI Streamlit operations console.

Run alongside the FastAPI service:
    uvicorn backend.api.main:app --reload
    streamlit run frontend/app.py
"""

from __future__ import annotations

import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)


st.set_page_config(
    page_title="FactoryOps AI | Operations Console",
    layout="wide",
    initial_sidebar_state="collapsed",
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
DEFAULT_DEMO_USERS = {
    os.getenv("FACTORYOPS_ADMIN_USER", "admin").strip().lower(): {
        "password": os.getenv("FACTORYOPS_ADMIN_PASSWORD", "FactoryOps@123"),
        "name": "Operations Lead",
        "role": "System Administrator",
    },
    "operator": {
        "password": "Operator@123",
        "name": "Operations User",
        "role": "Operator",
    },
    "maintenance": {
        "password": "Maintenance@123",
        "name": "Maintenance User",
        "role": "Maintenance",
    },
}

DEMO_USER_CREDENTIALS = "admin / operator / maintenance"
PAGES = [
    "Command Center",
    "Fleet Explorer",
    "Telemetry Lab",
    "Predictions & Incidents",
    "Maintenance & Inventory",
    "Data Management",
]
def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap');
        :root {
            --page: #f6f1e8;
            --surface: #fffaf2;
            --surface-2: #efe5d7;
            --surface-3: #e5d6c3;
            --border: #d8c6af;
            --text: #2e241b;
            --muted: #756454;
            --accent: #22133A;
            --accent-2: #4b2a69;
            --accent-3: #5e3a7b;
            --success: #6c8751;
            --warning: #5e3a7b;
            --danger: #b84d49;
        }
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(94, 58, 123, 0.14), transparent 22%),
                radial-gradient(circle at bottom left, rgba(75, 42, 105, 0.1), transparent 28%),
                var(--page);
            color: var(--text);
            font-family: 'Manrope', sans-serif;
        }
        .block-container {
            max-width: 1420px;
            padding: 1.5rem 2rem 3.5rem;
        }
        [data-testid='stSidebar'],
        [data-testid='collapsedControl'] {
            display: none;
        }
        [data-testid='stHeader'] {
            background: rgba(246, 241, 232, 0.82);
            backdrop-filter: blur(10px);
        }
        h1, h2, h3, h4 {
            font-family: 'Outfit', sans-serif;
            color: var(--text);
            letter-spacing: -0.02em;
        }
        .hero,
        .topbar,
        .filter-shell,
        .login-panel,
        .auth-note {
            background: rgba(255, 250, 242, 0.9);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 18px 45px rgba(71, 54, 37, 0.08);
        }
        .hero {
            padding: 1.5rem 1.6rem;
            margin-bottom: 1.5rem;
        }
        .eyebrow {
            color: var(--accent);
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .subtle,
        .subtle p,
        .stCaption {
            color: var(--text) !important;
            opacity: 0.75;
        }
        .login-intro h1 {
            font-size: 3.2rem !important;
            line-height: 1.08;
            letter-spacing: -0.04em;
        }
        .pill {
            display: inline-block;
            padding: 0.26rem 0.68rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            margin-right: 0.35rem;
            border: 1px solid transparent;
        }
        .pill-good {
            color: #456233;
            background: rgba(126, 143, 90, 0.12);
            border-color: rgba(126, 143, 90, 0.3);
        }
        .pill-warn {
            color: #4b2a69;
            background: rgba(94, 58, 123, 0.14);
            border-color: rgba(94, 58, 123, 0.3);
        }
        .pill-bad {
            color: #923c38;
            background: rgba(184, 77, 73, 0.13);
            border-color: rgba(184, 77, 73, 0.28);
        }
        .metric-card,
        .machine-card,
        .section-card,
        div[data-testid='stMetric'] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
        }
        .metric-card {
            padding: 1.2rem 1.3rem;
            min-height: 124px;
        }
        .metric-label,
        div[data-testid='stMetricLabel'] p {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.68rem;
            font-weight: 800;
        }
        .metric-value,
        div[data-testid='stMetricValue'] {
            color: var(--text);
            font-family: 'Outfit', sans-serif;
            font-size: 1.82rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }
        .metric-detail {
            color: var(--muted);
            font-size: 0.79rem;
            line-height: 1.5;
        }
        .machine-card {
            padding: 1.2rem 1.2rem;
            min-height: auto;
            border-left: 4px solid var(--accent-2);
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }
        .machine-card-title {
            font-weight: 700;
            font-size: 0.95rem;
            color: var(--text);
        }
        .machine-card-subtitle {
            font-size: 0.82rem;
            color: var(--muted);
        }
        .machine-card-metrics {
            font-size: 0.8rem;
            color: var(--text);
            line-height: 1.6;
        }
        .machine-card.warning {
            border-left-color: var(--warning);
        }
        .machine-card.critical {
            border-left-color: var(--danger);
        }
        .topbar {
            padding: 1.1rem 1.3rem;
            margin: 0.3rem 0 1.3rem;
            background: rgba(255, 250, 242, 0.72);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: 0 10px 24px rgba(71, 54, 37, 0.04);
        }
        .brand-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: flex-end;
            margin-bottom: 0.9rem;
        }
        .brand-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.85rem;
            font-weight: 700;
        }
        .user-chip {
            text-align: right;
            font-size: 0.9rem;
        }
        .user-chip .role {
            display: block;
            margin-top: 0.2rem;
            color: var(--accent);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
        }
        .filter-shell {
            padding: 1.2rem 1.3rem 0.4rem;
            margin-bottom: 1.5rem;
        }
        .login-wrap {
            max-width: 720px;
            margin: 10vh auto 0;
        }
        .login-intro {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .login-intro h1 {
            font-size: 2.9rem !important;
            margin-bottom: 0.35rem !important;
        }
        .login-panel {
            padding: 1.8rem;
        }
        .auth-note {
            margin-top: 1.3rem;
            padding: 1rem 1.2rem;
        }
        .auth-note p {
            margin: 0;
            color: var(--muted);
            font-size: 0.86rem;
        }
        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {
            border-radius: 12px;
            border: 1px solid #000000;
            background: var(--accent);
            color: #fffaf5;
            font-weight: 700;
            min-height: 2.7rem;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {
            background: #342052;
            border-color: #000000;
            color: #fffaf5;
        }
        .stSelectbox,
        .stSelectbox > div,
        div[data-baseweb='select'] > div:first-child,
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {
            background: #ffffff !important;
            border-color: var(--border) !important;
            color: var(--text) !important;
            border-radius: 12px !important;
        }
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        .stSelectbox input::placeholder {
            color: #7c6c5f !important;
            opacity: 1 !important;
        }
        .stSelectbox,
        .stSelectbox > div {
            width: 100% !important;
        }
        .stSelectbox [data-baseweb='popover'] {
            z-index: 9999;
        }
        .stTextInput label,
        .stNumberInput label,
        .stTextArea label,
        .stSelectbox label,
        .stMultiSelect label {
            color: var(--text) !important;
            font-weight: 600 !important;
        }
        .stMultiSelect label p {
            color: var(--text) !important;
            font-weight: 600 !important;
        }
        div[data-baseweb='select'] span {
            color: var(--text) !important;
        }
        div[data-baseweb='popover'] [role='option'] {
            color: var(--text) !important;
            background: #ffffff !important;
        }
        div[data-baseweb='popover'] [role='option']:hover {
            background: #f0eaf6 !important;
        }
        .stTabs [data-baseweb='tab-list'] {
            gap: 0.45rem;
        }
        .stTabs [data-baseweb='tab'] {
            background: rgba(229, 214, 195, 0.35);
            border: 1px solid #000000;
            border-bottom: 0;
            border-radius: 10px 10px 0 0;
            color: var(--text) !important;
            padding: 0.55rem 0.9rem;
            font-weight: 600;
        }
        .stTabs [aria-selected='true'] {
            color: var(--text) !important;
            background: var(--surface) !important;
            border: 1px solid #000000 !important;
            border-bottom: none !important;
            font-weight: 700;
        }
        div[role="radiogroup"] {
            gap: 0.55rem;
        }
        div[role="radiogroup"] label {
            background: rgba(229, 214, 195, 0.35);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
        }
        div[role="radiogroup"] label p {
            color: var(--text) !important;
            font-weight: 600 !important;
        }
        div[role="radiogroup"] label:has(input:checked) {
            background: var(--accent);
            border-color: var(--accent);
        }
        div[role="radiogroup"] label:has(input:checked) p {
            color: #fffaf5 !important;
        }
        div[data-testid='stDataFrame'] {
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
        }
        .stAlert {
            border-radius: 14px;
        }
        .section-note {
            color: var(--muted);
            font-size: 0.84rem;
            margin: 0.2rem 0 1rem;
        }
        .filter-shell h4,
        .section-title {
            font-size: 2.1rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em;
            font-family: 'Outfit', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def api_url(resource: str = "") -> str:
    return f"{API_BASE_URL}/{resource.lstrip('/')}"


def initialise_session() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = {}
    if "demo_users" not in st.session_state:
        st.session_state.demo_users = deepcopy(DEFAULT_DEMO_USERS)
    if "active_page" not in st.session_state:
        st.session_state.active_page = PAGES[0]


def authenticate(username: str, password: str) -> bool:
    account = st.session_state.demo_users.get(username.strip().lower())
    if account and password == account["password"]:
        st.session_state.authenticated = True
        st.session_state.current_user = {
            "username": username.strip(),
            "name": account["name"],
            "role": account["role"],
        }
        return True
    return False


def create_account(name: str, username: str, password: str, role: str) -> tuple[bool, str]:
    clean_username = username.strip().lower()
    if not name.strip() or not clean_username or not password.strip():
        return False, "Name, username, and password are required."
    if clean_username in st.session_state.demo_users:
        return False, "That username already exists."
    st.session_state.demo_users[clean_username] = {
        "password": password,
        "name": name.strip(),
        "role": role,
    }
    authenticate(clean_username, password)
    return True, "Account created successfully."


def render_login_page() -> None:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="login-intro">
            <div class="eyebrow">FactoryOps Access</div>
            <h1>Operations clarity without the clutter.</h1>
            <p class="subtle">Monitor telemetry, predictions, incidents, maintenance, and inventory from one production-focused console.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, middle, right = st.columns([1, 1.25, 1], gap="large")
    with middle:
        sign_in_tab, sign_up_tab = st.tabs(["Sign In", "Sign Up"])
        with sign_in_tab:
            with st.form("factoryops_login", clear_on_submit=False):
                username = st.text_input("Username", autocomplete="username")
                password = st.text_input("Password", type="password", autocomplete="current-password")
                submitted = st.form_submit_button("Sign in", use_container_width=True)
            if submitted:
                if authenticate(username, password):
                    st.rerun()
                st.error("Incorrect username or password.")
        with sign_up_tab:
            with st.form("factoryops_signup", clear_on_submit=False):
                name = st.text_input("Full name")
                username = st.text_input("Choose a username")
                password = st.text_input("Create a password", type="password")
                role = st.selectbox("Role", ["Operator", "Maintenance", "System Administrator"])
                created = st.form_submit_button("Create account", use_container_width=True)
            if created:
                ok, message = create_account(name, username, password, role)
                if ok:
                    st.success(message)
                    st.rerun()
                st.error(message)
    st.markdown("</div>", unsafe_allow_html=True)


@st.cache_data(ttl=15, show_spinner=False)
def get_records(resource: str) -> list[dict[str, Any]]:
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
    css = (
        "pill-good"
        if state in {"running", "active", "normal", "healthy", "completed", "closed", "resolved"}
        else "pill-bad"
        if state in {"critical", "maintenance", "inactive", "open", "in progress"}
        else "pill-warn"
    )
    return f'<span class="pill {css}">{state.title()}</span>'


def format_table(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    present = [column for column in columns if column in frame]
    return frame[present] if present else frame


def latest_telemetry(telemetry: pd.DataFrame) -> pd.DataFrame:
    if telemetry.empty or "machine_id" not in telemetry:
        return telemetry.copy()
    ordered = telemetry.sort_values("id") if "id" in telemetry else telemetry
    return ordered.drop_duplicates("machine_id", keep="last")


def build_machine_view(machines: pd.DataFrame, telemetry: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    machine_view = machines.copy()
    if machine_view.empty:
        return machine_view
    latest = latest_telemetry(telemetry)
    telemetry_columns = [
        column
        for column in ["machine_id", "temperature", "vibration", "power", "rpm", "health_score", "failure_probability"]
        if column in latest
    ]
    if telemetry_columns:
        machine_view = machine_view.merge(latest[telemetry_columns], on="machine_id", how="left", suffixes=("", "_telemetry"))
    if not predictions.empty and "machine_id" in predictions:
        latest_predictions = predictions.sort_values("id").drop_duplicates("machine_id", keep="last") if "id" in predictions else predictions
        prediction_columns = [
            column
            for column in ["machine_id", "failure_probability", "health_score", "predicted_days"]
            if column in latest_predictions
        ]
        machine_view = machine_view.merge(
            latest_predictions[prediction_columns],
            on="machine_id",
            how="left",
            suffixes=("_telemetry", "_prediction"),
        )
    machine_view["temperature"] = number_column(machine_view, "temperature")
    risk_columns = [column for column in machine_view if column.startswith("failure_probability")]
    machine_view["failure_probability_display"] = (
        machine_view[risk_columns].bfill(axis=1).iloc[:, 0].fillna(0.0) if risk_columns else 0.0
    )
    health_columns = [column for column in machine_view if column.startswith("health_score")]
    machine_view["health_score_display"] = (
        machine_view[health_columns].bfill(axis=1).iloc[:, 0].fillna(0.0) if health_columns else 0.0
    )
    machine_view["condition"] = machine_view.apply(
        lambda row: "critical"
        if risk_state(float(row["failure_probability_display"])) == "critical"
        or temperature_state(float(row["temperature"])) == "critical"
        else "warning"
        if risk_state(float(row["failure_probability_display"])) == "warning"
        or temperature_state(float(row["temperature"])) == "warning"
        else "normal",
        axis=1,
    )
    return machine_view


def page_header(title: str, description: str, health: dict[str, Any]) -> None:
    state = "Online" if health else "API unavailable"
    badge = "pill-good" if health else "pill-bad"
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">FactoryOps Operations Console</div>
            <h1>{title}</h1>
            <div class="subtle">{description}</div>
            <div style="margin-top:0.95rem"><span class="pill {badge}">{state}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, detail: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-detail">{detail}</div></div>',
        unsafe_allow_html=True,
    )


def chart_layout(height: int = 400) -> dict[str, Any]:
    return {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#2e241b", "family": "Manrope"},
        "margin": {"l": 10, "r": 10, "t": 35, "b": 18},
        "legend": {"orientation": "h", "y": 1.12},
    }


def render_top_navigation() -> str:
    user = st.session_state.current_user
    left, right = st.columns([1.55, 0.8], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="brand-row">
                <div>
                    <div class="eyebrow">FactoryOps</div>
                    <div class="brand-title">Predictive Maintenance Console</div>
                </div>
                <div class="user-chip">
                    {user.get("name", "Signed-in user")}
                    <span class="role">{user.get("role", "User")}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        current = PAGES.index(st.session_state.active_page)
        page = st.radio(
            "Navigation",
            PAGES,
            index=current,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.active_page = page
    with right:
        st.write("")
        st.write("")
        action_left, action_right = st.columns(2, gap="small")
        with action_left:
            if st.button("Refresh data", use_container_width=True):
                get_records.clear()
                get_health.clear()
                st.rerun()
        with action_right:
            if st.button("Sign out", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.current_user = {}
                st.rerun()
    return st.session_state.active_page


def render_search_filter_section(machine_view: pd.DataFrame) -> tuple[list[str], list[str], str]:
    st.markdown('<div class="filter-shell">', unsafe_allow_html=True)
    st.markdown('<h4 class="section-title">Search And Filter</h4>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-note">Browse {len(machine_view)} registered assets from one combined search and filter bar.</div>',
        unsafe_allow_html=True,
    )
    left, middle, right = st.columns([1.6, 1, 1], gap="large")
    locations = sorted(machine_view["location"].dropna().astype(str).unique()) if "location" in machine_view else []
    statuses = sorted(machine_view["status"].dropna().astype(str).unique()) if "status" in machine_view else []
    with left:
        query = st.text_input("Search machines")
    with middle:
        selected_locations = st.multiselect("Locations", locations, placeholder=" ")
    with right:
        selected_statuses = st.multiselect("Machine status", statuses, placeholder=" ")
    st.markdown("</div>", unsafe_allow_html=True)
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
            mask = (
                filtered[searchable]
                .fillna("")
                .astype(str)
                .apply(lambda column: column.str.contains(query, case=False, na=False))
                .any(axis=1)
            )
            filtered = filtered[mask]
    return filtered


def render_command_center(
    machine_view: pd.DataFrame,
    telemetry: pd.DataFrame,
    incidents: pd.DataFrame,
    maintenance: pd.DataFrame,
) -> None:
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
        open_incidents = int(
            incidents.get("status", pd.Series(dtype=str)).astype(str).str.lower().isin(["open", "in progress"]).sum()
        )
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
                        f"""<div class="machine-card {condition}"><h4>{machine.get("machine_name", "Unnamed machine")}</h4>
                        <p>{machine.get("location", "Unassigned location")} · {machine.get("department", "Unassigned department")}</p>
                        {state_badge(condition)} {state_badge(machine.get("status", "unknown"))}
                        <div style="margin-top:.8rem" class="metric-label">Temperature / risk</div>
                        <b>{float(machine.get("temperature", 0)):.1f}°C</b> <span class="subtle">· {float(machine.get("failure_probability_display", 0)):.0%}</span></div>""",
                        unsafe_allow_html=True,
                    )
    with right:
        st.markdown("#### Risk radar")
        if machine_view.empty:
            st.info("Add machines and telemetry to populate the risk radar.")
        else:
            chart_data = machine_view.sort_values("failure_probability_display", ascending=False).head(10)
            condition_colours = {"normal": "#6c8751", "warning": "#5e3a7b", "critical": "#b84d49"}
            figure = go.Figure(
                go.Bar(
                    x=chart_data["failure_probability_display"],
                    y=chart_data["machine_name"],
                    orientation="h",
                    marker_color=[condition_colours.get(condition, "#22133A") for condition in chart_data["condition"]],
                    text=[
                        f"{probability:.0%} · {condition.title()}"
                        for probability, condition in zip(
                            chart_data["failure_probability_display"], chart_data["condition"]
                        )
                    ],
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
                xaxis={
                    "title": "Failure probability",
                    "tickformat": ".0%",
                    "range": [0, max(0.1, float(chart_data["failure_probability_display"].max()) + 0.15)],
                },
            )
            figure.update_layout(**radar_layout)
            st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    st.markdown("#### Decision queue")
    queue_left, queue_right = st.columns(2, gap="large")
    with queue_left:
        st.caption("Highest-risk machines")
        columns = [
            "machine_name",
            "location",
            "temperature",
            "health_score_display",
            "failure_probability_display",
            "condition",
        ]
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
            if not machine_view.empty and {"machine_id", "machine_name"}.issubset(machine_view.columns):
                workload = workload.merge(
                    machine_view[["machine_id", "machine_name"]],
                    on="machine_id",
                    how="left",
                )
            if "status" in workload:
                workload = workload[~workload["status"].astype(str).str.lower().isin(["completed", "closed"])]
            workload = workload.rename(
                columns={
                    "machine_name": "Machine",
                    "maintenance_type": "Task",
                    "technician": "Technician",
                    "status": "Status",
                    "cost": "Cost",
                }
            )
            st.dataframe(
                format_table(workload, ["Machine", "Task", "Technician", "Status", "Cost"]),
                use_container_width=True,
                hide_index=True,
            )

    if not telemetry.empty:
        st.markdown("#### Fleet signal snapshot")
        snapshot = latest_telemetry(telemetry)
        columns = [column for column in ["temperature", "vibration", "power", "rpm"] if column in snapshot]
        if columns:
            summary = snapshot[columns].mean(numeric_only=True).rename("Average").to_frame()
            st.dataframe(summary, use_container_width=True)


def render_fleet_explorer(machine_view: pd.DataFrame) -> None:
    if machine_view.empty:
        st.info("No machines match the active filters.")
        return
    summary, table = st.tabs(["Fleet map", "Machine register"])
    with summary:
        left, right = st.columns([1, 1.35], gap="large")
        with left:
            status_counts = (
                machine_view.get("status", pd.Series(dtype=str))
                .fillna("Unspecified")
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Machines")
            )
            figure = px.pie(
                status_counts,
                names="Status",
                values="Machines",
                hole=0.65,
                color="Status",
                color_discrete_sequence=["#6c8751", "#5e3a7b", "#b84d49", "#22133A", "#4b2a69"],
            )
            figure.update_layout(**chart_layout(370), showlegend=True)
            st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
        with right:
            location_counts = (
                machine_view.get("location", pd.Series(dtype=str))
                .fillna("Unassigned")
                .value_counts()
                .rename_axis("Location")
                .reset_index(name="Machines")
            )
            figure = px.bar(
                location_counts,
                x="Location",
                y="Machines",
                color="Machines",
                color_continuous_scale=["#e5d6c3", "#22133A"],
                text="Machines",
            )
            figure.update_layout(**chart_layout(370), coloraxis_showscale=False)
            st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
    with table:
        export = machine_view.copy()
        export["failure_probability_display"] = export["failure_probability_display"].map("{:.1%}".format)
        export["temperature"] = export["temperature"].map("{:.1f} C".format)
        export = export.rename(
            columns={
                "machine_name": "Machine",
                "department": "Department",
                "location": "Location",
                "status": "Status",
                "condition": "Condition",
                "temperature": "Temperature",
                "health_score_display": "Health Score",
                "failure_probability_display": "Failure Risk",
                "predicted_days": "Predicted Days",
            }
        )
        st.dataframe(
            format_table(
                export,
                [
                    "Machine",
                    "Department",
                    "Location",
                    "Status",
                    "Condition",
                    "Temperature",
                    "Health Score",
                    "Failure Risk",
                    "Predicted Days",
                ],
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download filtered fleet CSV",
            machine_view.to_csv(index=False).encode("utf-8"),
            "factoryops_fleet.csv",
            "text/csv",
        )

        with st.expander("Update a machine status"):
            options = machine_view["machine_id"].tolist()
            selected_id = st.selectbox(
                "Machine",
                options,
                format_func=lambda identifier: machine_view.loc[
                    machine_view["machine_id"].eq(identifier), "machine_name"
                ].iloc[0],
                key="machine_status_select",
            )
            selected = machine_view[machine_view["machine_id"].eq(selected_id)].iloc[0]
            status_options = ["Running", "Idle", "Maintenance", "Stopped"]
            st.caption(
                f"{selected.get('department', 'Unassigned department')} | {selected.get('location', 'Unassigned location')}"
            )
            with st.form("update_machine_status"):
                new_status = st.selectbox(
                    "Operating status",
                    status_options,
                    index=status_options.index(selected.get("status", "Running"))
                    if selected.get("status", "Running") in status_options
                    else 0,
                )
                if st.form_submit_button("Save status"):
                    payload = {key: selected.get(key) for key in ["machine_name", "department", "location"]}
                    payload["status"] = new_status
                    ok, message = send_record("PUT", "machines", payload, int(selected_id))
                    (st.success if ok else st.error)(message)


def render_telemetry_lab(telemetry: pd.DataFrame, machines: pd.DataFrame) -> None:
    if telemetry.empty:
        st.info("No telemetry exists yet. Use Data Management to record a reading.")
        return
    machine_names = (
        machines[["machine_id", "machine_name"]]
        if not machines.empty and {"machine_id", "machine_name"}.issubset(machines.columns)
        else pd.DataFrame(columns=["machine_id", "machine_name"])
    )
    data = telemetry.merge(machine_names, on="machine_id", how="left")
    data["machine_label"] = data["machine_name"].fillna("Unknown machine #" + data["machine_id"].astype(str))
    selected_machine = st.selectbox(
        "Inspect machine",
        sorted(data["machine_id"].dropna().unique()),
        format_func=lambda identifier: data.loc[data["machine_id"].eq(identifier), "machine_label"].iloc[0],
    )
    selected = (
        data[data["machine_id"].eq(selected_machine)].sort_values("id")
        if "id" in data
        else data[data["machine_id"].eq(selected_machine)]
    )
    latest = selected.iloc[-1]
    metrics = st.columns(5)
    for column, label, suffix in [
        ("temperature", "Temperature", "°C"),
        ("vibration", "Vibration", ""),
        ("rpm", "RPM", ""),
        ("power", "Power", ""),
        ("oil_level", "Oil level", "%"),
    ]:
        with metrics[["temperature", "vibration", "rpm", "power", "oil_level"].index(column)]:
            st.metric(label, f"{float(latest.get(column, 0)):.1f}{suffix}")

    signal_columns = [
        column
        for column in ["temperature", "pressure", "vibration", "voltage", "current", "power", "rpm", "humidity", "oil_level"]
        if column in selected
    ]
    chosen_signals = st.multiselect("Signals", signal_columns, default=signal_columns[:3])
    if chosen_signals:
        figure = go.Figure()
        x_values = selected["id"] if "id" in selected else selected.index
        for signal in chosen_signals:
            figure.add_trace(
                go.Scatter(
                    x=x_values,
                    y=number_column(selected, signal),
                    mode="lines+markers",
                    name=signal.replace("_", " ").title(),
                )
            )
        figure.update_layout(**chart_layout(430), xaxis_title="Reading sequence", yaxis_title="Recorded value")
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
        st.caption("The backend does not yet store timestamps, so readings are shown in capture order.")

    st.markdown("#### Recent raw readings")
    display_selected = selected.sort_values("id", ascending=False).copy() if "id" in selected else selected.copy()
    display_selected = display_selected.rename(
        columns={
            "machine_name": "Machine",
            "temperature": "Temperature",
            "pressure": "Pressure",
            "vibration": "Vibration",
            "voltage": "Voltage",
            "current": "Current",
            "power": "Power",
            "rpm": "RPM",
            "humidity": "Humidity",
            "oil_level": "Oil Level",
            "health_score": "Health Score",
            "failure_probability": "Failure Risk",
        }
    )
    st.dataframe(
        format_table(
            display_selected,
            [
                "Machine",
                *[signal.replace("_", " ").title() for signal in signal_columns],
                "Health Score",
                "Failure Risk",
            ],
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download inspected telemetry CSV",
        selected.to_csv(index=False).encode("utf-8"),
        "telemetry_export.csv",
        "text/csv",
    )


def render_prediction_incident_page(predictions: pd.DataFrame, incidents: pd.DataFrame, machines: pd.DataFrame) -> None:
    machine_names = (
        machines[["machine_id", "machine_name", "location"]]
        if not machines.empty
        else pd.DataFrame(columns=["machine_id", "machine_name", "location"])
    )
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
                figure = px.scatter(
                    view,
                    x="health_score",
                    y="failure_probability",
                    size="failure_probability",
                    color="priority",
                    hover_name="machine_name",
                    hover_data=["predicted_days", "location"],
                    color_discrete_map={"normal": "#6c8751", "warning": "#5e3a7b", "critical": "#b84d49"},
                    labels={"health_score": "Health score", "failure_probability": "Failure probability"},
                )
                figure.update_layout(**chart_layout(410), yaxis_tickformat=".0%")
                st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
            with right:
                st.markdown("#### Immediate attention")
                urgent = view.sort_values(["failure_probability", "predicted_days"], ascending=[False, True]).head(8).copy()
                urgent["failure_probability"] = urgent["failure_probability"].map("{:.1%}".format)
                urgent = urgent.rename(
                    columns={
                        "machine_name": "Machine",
                        "location": "Location",
                        "failure_probability": "Failure Risk",
                        "health_score": "Health Score",
                        "predicted_days": "Predicted Days",
                        "priority": "Priority",
                    }
                )
                st.dataframe(
                    format_table(
                        urgent,
                        ["Machine", "Location", "Failure Risk", "Health Score", "Predicted Days", "Priority"],
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            st.download_button(
                "Download prediction CSV",
                view.to_csv(index=False).encode("utf-8"),
                "prediction_priorities.csv",
                "text/csv",
            )
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
                        st.markdown(
                            f'<div class="machine-card {css}"><b>{machine_label}</b><p>{incident.get("description", "No description")}</p>{state_badge(incident.get("priority", "normal"))}<br><span class="subtle">Owner: {incident.get("assigned_to", "Unassigned")}</span></div>',
                            unsafe_allow_html=True,
                        )


def render_maintenance_inventory_page(maintenance: pd.DataFrame, inventory: pd.DataFrame, machines: pd.DataFrame) -> None:
    machine_names = (
        machines[["machine_id", "machine_name"]]
        if not machines.empty
        else pd.DataFrame(columns=["machine_id", "machine_name"])
    )
    tab_maintenance, tab_inventory = st.tabs(["Maintenance planning", "Spare-parts readiness"])
    with tab_maintenance:
        if maintenance.empty:
            st.info("No maintenance jobs available.")
        else:
            view = maintenance.merge(machine_names, on="machine_id", how="left")
            view = view.rename(
                columns={
                    "machine_name": "Machine",
                    "maintenance_type": "Task",
                    "technician": "Technician",
                    "cost": "Cost",
                    "remarks": "Remarks",
                    "status": "Status",
                }
            )
            left, right = st.columns([1.15, 1], gap="large")
            with left:
                status_counts = (
                    view.get("status", pd.Series(dtype=str))
                    .fillna("Unspecified")
                    .value_counts()
                    .rename_axis("Status")
                    .reset_index(name="Jobs")
                )
                figure = px.bar(
                    status_counts,
                    x="Status",
                    y="Jobs",
                    color="Status",
                    text="Jobs",
                    color_discrete_sequence=["#22133A", "#5e3a7b", "#6c8751", "#b84d49"],
                )
                figure.update_layout(**chart_layout(340), showlegend=False)
                st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
            with right:
                total_cost = number_column(view, "cost").sum()
                scheduled = int(
                    view.get("status", pd.Series(dtype=str)).astype(str).str.lower().isin(["scheduled", "in progress"]).sum()
                )
                st.metric("Recorded maintenance cost", f"{total_cost:,.0f}")
                st.metric("Active / scheduled jobs", scheduled)
            st.dataframe(
                format_table(
                    view.sort_values("id", ascending=False),
                    ["Machine", "Task", "Technician", "Cost", "Remarks", "Status"],
                ),
                use_container_width=True,
                hide_index=True,
            )
    with tab_inventory:
        if inventory.empty:
            st.info("No inventory records available.")
        else:
            view = inventory.copy()
            view["quantity"] = number_column(view, "quantity")
            view = view.rename(
                columns={
                    "item_name": "Item",
                    "quantity": "Quantity",
                    "supplier": "Supplier",
                    "status": "Status",
                }
            )
            left, right = st.columns([1.15, 1], gap="large")
            with left:
                figure = px.bar(
                    view.sort_values("Quantity").head(12),
                    x="Quantity",
                    y="Item",
                    orientation="h",
                    color="Status",
                    color_discrete_sequence=["#6c8751", "#5e3a7b", "#b84d49"],
                    labels={"Quantity": "Quantity", "Item": ""},
                )
                figure.update_layout(**chart_layout(400), yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
            with right:
                low = view[view.get("Status", pd.Series(dtype=str)).astype(str).str.lower().str.contains("low")]
                st.markdown("#### Reorder watch")
                st.dataframe(
                    format_table(low, ["Item", "Quantity", "Supplier", "Status"]),
                    use_container_width=True,
                    hide_index=True,
                )
            st.dataframe(
                format_table(view.sort_values("Quantity"), ["Item", "Quantity", "Supplier", "Status"]),
                use_container_width=True,
                hide_index=True,
            )


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
                    ok, message = send_record(
                        "POST",
                        "machines",
                        {
                            "machine_name": name.strip(),
                            "department": department or None,
                            "location": location or None,
                            "status": status,
                        },
                    )
                    (st.success if ok else st.error)(message)
    with tabs[1]:
        if not machine_options:
            st.warning("Create a machine before entering telemetry.")
        else:
            with st.form("create_telemetry", clear_on_submit=True):
                machine_id = st.selectbox(
                    "Machine *",
                    machine_options,
                    format_func=lambda value: machine_name_for(value, machines),
                    key="telemetry_machine",
                )
                fields = [
                    ("temperature", "Temperature"),
                    ("pressure", "Pressure"),
                    ("vibration", "Vibration"),
                    ("voltage", "Voltage"),
                    ("current", "Current"),
                    ("power", "Power"),
                    ("rpm", "RPM"),
                    ("humidity", "Humidity"),
                    ("oil_level", "Oil level"),
                    ("health_score", "Health score"),
                    ("failure_probability", "Failure probability (0-1)"),
                ]
                values: dict[str, float] = {}
                columns = st.columns(3)
                for index, (key, label) in enumerate(fields):
                    values[key] = columns[index % 3].number_input(
                        label,
                        min_value=0.0,
                        value=0.0,
                        key=f"telemetry_{key}",
                    )
                if st.form_submit_button("Record telemetry"):
                    ok, message = send_record("POST", "telemetry", {"machine_id": machine_id, **values})
                    (st.success if ok else st.error)(message)
    with tabs[2]:
        if machine_options:
            with st.form("create_maintenance", clear_on_submit=True):
                left, right = st.columns(2)
                machine_id = left.selectbox(
                    "Machine *",
                    machine_options,
                    format_func=lambda value: machine_name_for(value, machines),
                    key="maintenance_machine",
                )
                maintenance_type = right.selectbox(
                    "Type",
                    ["Inspection", "Preventive", "Corrective", "Predictive", "Emergency"],
                )
                technician = left.text_input("Technician *")
                cost = right.number_input("Cost *", min_value=0.0, value=0.0)
                remarks = left.text_input("Remarks *")
                status = right.selectbox("Status", ["Scheduled", "In Progress", "Completed"])
                if st.form_submit_button("Create maintenance job"):
                    if not technician.strip() or not remarks.strip():
                        st.error("Technician and remarks are required.")
                    else:
                        ok, message = send_record(
                            "POST",
                            "maintenance",
                            {
                                "machine_id": machine_id,
                                "maintenance_type": maintenance_type,
                                "technician": technician,
                                "cost": cost,
                                "remarks": remarks,
                                "status": status,
                            },
                        )
                        (st.success if ok else st.error)(message)
    with tabs[3]:
        if machine_options:
            with st.form("create_incident", clear_on_submit=True):
                left, right = st.columns(2)
                machine_id = left.selectbox(
                    "Machine *",
                    machine_options,
                    format_func=lambda value: machine_name_for(value, machines),
                    key="incident_machine",
                )
                priority = right.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                description = st.text_area("Description *")
                assigned_to = left.text_input("Assigned to *")
                status = right.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
                if st.form_submit_button("Log incident"):
                    if not description.strip() or not assigned_to.strip():
                        st.error("Description and assignee are required.")
                    else:
                        ok, message = send_record(
                            "POST",
                            "incidents",
                            {
                                "machine_id": machine_id,
                                "priority": priority,
                                "description": description,
                                "assigned_to": assigned_to,
                                "status": status,
                            },
                        )
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
                    ok, message = send_record(
                        "POST",
                        "inventory",
                        {"item_name": item_name, "quantity": quantity, "supplier": supplier, "status": status},
                    )
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
                    ok, feedback = send_record(
                        "POST",
                        "notifications",
                        {
                            "title": title,
                            "message": message,
                            "notification_type": notification_type,
                            "status": status,
                        },
                    )
                    (st.success if ok else st.error)(feedback)
        if not notifications.empty:
            st.caption("Latest notifications")
            display_notifications = notifications.sort_values("id", ascending=False).rename(
                columns={
                    "title": "Title",
                    "message": "Message",
                    "notification_type": "Type",
                    "status": "Status",
                }
            )
            st.dataframe(
                format_table(
                    display_notifications,
                    ["Title", "Message", "Type", "Status"],
                ),
                use_container_width=True,
                hide_index=True,
            )
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
                    ok, message = send_record(
                        "POST",
                        "sensors",
                        {"sensor_name": sensor_name, "location": location or None, "status": status},
                    )
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
    page = render_top_navigation()

    if not health:
        page_header("Connection required", "Start the FastAPI backend to unlock live fleet operations and data entry.", health)
        st.error("The API is unavailable. Run: `uvicorn backend.api.main:app --reload`")
        st.info("The UI remains empty by design when the backend is offline.")
        return

    collections = {resource: as_frame(get_records(resource)) for resource in RESOURCE_LABELS}
    machine_view = build_machine_view(collections["machines"], collections["telemetry"], collections["predictions"])
    locations, statuses, query = render_search_filter_section(machine_view)
    filtered_machines = apply_filters(machine_view, locations, statuses, query)

    copy = {
        "Command Center": ("Command Center", "Prioritize operational attention from fleet condition, health, risk, and work queues."),
        "Fleet Explorer": ("Fleet Explorer", "Search the registered assets and update operating state from one cleaner workspace."),
        "Telemetry Lab": ("Telemetry Lab", "Inspect recorded machine signals, compare conditions, and export the data you need."),
        "Predictions & Incidents": ("Predictions & Incidents", "Turn model outputs and reported issues into an action-oriented priority queue."),
        "Maintenance & Inventory": ("Maintenance & Inventory", "Plan work, monitor spend, and verify whether required parts are available."),
        "Data Management": ("Data Management", "Create the operational records that power the dashboard through the FastAPI service."),
    }
    page_header(*copy[page], health)

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
