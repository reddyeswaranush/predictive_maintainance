"""HTTP access layer for the FastAPI backend.

Endpoints, payload shapes and status handling are unchanged from the original
implementation - this module only isolates them so views never call `requests`
directly.
"""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.getenv("FACTORYOPS_API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = 4

# Resource -> human label. Drives both fetching and UI copy.
RESOURCES: dict[str, str] = {
    "machines": "Machines",
    "sensors": "Sensors",
    "telemetry": "Telemetry",
    "predictions": "Predictions",
    "maintenance": "Maintenance",
    "incidents": "Incidents",
    "inventory": "Inventory",
    "notifications": "Notifications",
}


def api_url(resource: str = "") -> str:
    return f"{API_BASE_URL}/{resource.lstrip('/')}"


@st.cache_data(ttl=15, show_spinner=False)
def get_records(resource: str) -> list[dict[str, Any]]:
    """GET /{resource}/ -> list of records. Returns [] when unreachable."""
    try:
        response = requests.get(api_url(f"{resource}/"), timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []
    except (requests.RequestException, ValueError):
        return []


@st.cache_data(ttl=10, show_spinner=False)
def get_health() -> dict[str, Any]:
    """GET /health -> service status. Returns {} when unreachable."""
    try:
        response = requests.get(api_url("health"), timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}
    except (requests.RequestException, ValueError):
        return {}


def send_record(
    method: str,
    resource: str,
    payload: dict[str, Any],
    record_id: int | None = None,
) -> tuple[bool, str]:
    """POST/PUT/DELETE against a resource. Returns (ok, message)."""
    suffix = f"/{record_id}" if record_id is not None else "/"
    try:
        response = requests.request(
            method,
            api_url(f"{resource}{suffix}"),
            json=payload if method != "DELETE" else None,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.ok:
            clear_cache()
            return True, "Saved successfully."
        detail = response.json().get("detail", response.text)
        return False, f"API returned {response.status_code}: {detail}"
    except (requests.RequestException, ValueError) as error:
        return False, f"Could not contact the API: {error}"


def clear_cache() -> None:
    """Drop cached reads so the next render reflects fresh data."""
    get_records.clear()
    get_health.clear()


def as_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(records) if records else pd.DataFrame()


def load_collections() -> dict[str, pd.DataFrame]:
    """Fetch every resource once per rerun and return it as DataFrames."""
    return {resource: as_frame(get_records(resource)) for resource in RESOURCES}
