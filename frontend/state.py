"""Session state, demo authentication and navigation routing.

Authentication behaviour is carried over unchanged from the original app; it is
only reorganised here and extended with the Login -> Welcome -> Dashboard flow.
"""

from __future__ import annotations

import os
from copy import deepcopy

import streamlit as st

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

# (route key, header label). Order defines header order.
NAV_ITEMS: list[tuple[str, str]] = [
    ("dashboard", "Dashboard"),
    ("fleet", "Fleet"),
    ("predictions", "Predictions"),
    ("maintenance", "Maintenance"),
    ("records", "Records"),
]

NAV_LABELS: dict[str, str] = dict(NAV_ITEMS)
DEFAULT_ROUTE = NAV_ITEMS[0][0]

# Screens that sit outside the header navigation.
SCREEN_LOGIN = "login"
SCREEN_WELCOME = "welcome"
SCREEN_APP = "app"

# ---------------------------------------------------------------------------
# Demo accounts
# ---------------------------------------------------------------------------

ROLES = ["Operator", "Maintenance", "System Administrator"]

DEFAULT_DEMO_USERS: dict[str, dict[str, str]] = {
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


def initialise_session() -> None:
    defaults = {
        "authenticated": False,
        "current_user": {},
        "demo_users": deepcopy(DEFAULT_DEMO_USERS),
        "screen": SCREEN_LOGIN,
        "route": DEFAULT_ROUTE,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def authenticate(username: str, password: str) -> bool:
    account = st.session_state.demo_users.get(username.strip().lower())
    if account and password == account["password"]:
        st.session_state.authenticated = True
        st.session_state.current_user = {
            "username": username.strip(),
            "name": account["name"],
            "role": account["role"],
        }
        st.session_state.screen = SCREEN_WELCOME
        st.session_state.route = DEFAULT_ROUTE
        return True
    return False


def create_account(name: str, username: str, password: str, role: str) -> tuple[bool, str]:
    clean_username = username.strip().lower()
    if not name.strip() or not clean_username or not password.strip():
        return False, "Name, username and password are required."
    if clean_username in st.session_state.demo_users:
        return False, "That username already exists."
    st.session_state.demo_users[clean_username] = {
        "password": password,
        "name": name.strip(),
        "role": role,
    }
    authenticate(clean_username, password)
    return True, "Account created."


def sign_out() -> None:
    st.session_state.authenticated = False
    st.session_state.current_user = {}
    st.session_state.screen = SCREEN_LOGIN
    st.session_state.route = DEFAULT_ROUTE


# ---------------------------------------------------------------------------
# Routing helpers
# ---------------------------------------------------------------------------


def current_user() -> dict[str, str]:
    return st.session_state.get("current_user", {})


def enter_app() -> None:
    """Advance from the welcome screen into the dashboard."""
    st.session_state.screen = SCREEN_APP


def go_to(route: str) -> None:
    st.session_state.route = route
    st.session_state.screen = SCREEN_APP


def active_route() -> str:
    return st.session_state.get("route", DEFAULT_ROUTE)
