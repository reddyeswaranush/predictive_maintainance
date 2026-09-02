"""Reusable UI components.

Every page is assembled from these primitives, which is what keeps the pages
looking like one product. Views should not write raw HTML of their own.
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any, Literal

import pandas as pd
import streamlit as st

from frontend import api, state
from frontend.transforms import ALERT_STATES, HEALTHY_STATES

PRODUCT_NAME = "FactoryOps"
PRODUCT_SUBTITLE = "Predictive Maintenance"
APP_VERSION = "1.0.0"

Tone = Literal["good", "warn", "bad", "info", "mute"]
Emphasis = Literal["default", "success", "warning", "critical"]


def esc(value: Any) -> str:
    """Escape any value before it reaches an HTML string."""
    return escape(str(value if value is not None and str(value) != "nan" else "—"))


# Backwards-compatible private alias used inside this module.
_esc = esc


def _html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------


def brand_block(stacked: bool = False) -> str:
    """Brand lockup markup, shared by the header and the auth screen."""
    wrapper_class = "fo-brand" + (" fo-brand-stacked" if stacked else "")
    return (
        f'<div class="{wrapper_class}">'
        f'<div class="fo-brand-mark">FO</div>'
        f"<div><div class=\"fo-brand-name\">{PRODUCT_NAME}</div>"
        f'<div class="fo-brand-sub">{PRODUCT_SUBTITLE}</div></div>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------


def badge(label: str, tone: Tone = "mute") -> str:
    """Return badge markup. Use inside another component's HTML."""
    return f'<span class="fo-badge {tone}"><span class="fo-dot"></span>{_esc(label)}</span>'


def tone_for_state(value: Any) -> Tone:
    """Map a domain status string onto a badge tone."""
    text = str(value).strip().lower()
    if text in {"critical", "high"}:
        return "bad"
    if text in {"warning", "medium", "low stock", "scheduled", "idle"}:
        return "warn"
    if text in HEALTHY_STATES:
        return "good"
    if text in ALERT_STATES:
        return "bad"
    return "mute"


def state_badge(value: Any) -> str:
    return badge(str(value).title(), tone_for_state(value))


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------


def render_header(health: dict[str, Any]) -> None:
    """Top navigation bar. No sidebar anywhere in the product."""
    user = state.current_user()
    nav_items = state.NAV_ITEMS
    active = state.active_route()

    with st.container(key="app_header"):
        brand_col, nav_col, account_col = st.columns([2.3, 6.2, 2.3], vertical_alignment="center")

        with brand_col:
            _html(brand_block())

        with nav_col:
            nav_columns = st.columns(len(nav_items), gap="small")
            for column, (route, label) in zip(nav_columns, nav_items):
                with column:
                    st.button(
                        label,
                        key=f"nav_{route}",
                        type="primary" if route == active else "secondary",
                        width="stretch",
                        on_click=state.go_to,
                        args=(route,),
                    )

        with account_col:
            initials = "".join(part[0] for part in str(user.get("name", "U")).split()[:2]).upper()
            with st.popover(f"{initials}  ·  {user.get('name', 'Account')}", width="stretch"):
                _html(
                    f'<div class="fo-metric-label">Signed in as</div>'
                    f'<div style="font-weight:650;margin:.2rem 0 .1rem">{_esc(user.get("name", "User"))}</div>'
                    f'<div style="font-size:.8rem;color:var(--muted);margin-bottom:.6rem">'
                    f'{_esc(user.get("role", "User"))} · {_esc(user.get("username", ""))}</div>'
                    f'<div style="margin-bottom:.7rem">{service_badge(health)}</div>'
                )
                if st.button("Refresh data", key="account_refresh", width="stretch"):
                    api.clear_cache()
                    st.rerun()
                if st.button("Sign out", key="account_signout", type="primary", width="stretch"):
                    state.sign_out()
                    st.rerun()


def service_badge(health: dict[str, Any]) -> str:
    return badge("Service online", "good") if health else badge("Service offline", "bad")


# ---------------------------------------------------------------------------
# Page scaffolding
# ---------------------------------------------------------------------------


def page_head(title: str, meta: list[str] | None = None) -> None:
    """Page title plus optional status badges. Deliberately no marketing copy."""
    meta_markup = "".join(meta or [])
    _html(
        f'<div class="fo-page-head fo-animate">'
        f'<h1 class="fo-page-title">{_esc(title)}</h1>'
        f'<div class="fo-page-meta">{meta_markup}</div>'
        f"</div>"
    )


def section(title: str, note: str = "") -> None:
    note_markup = f'<span class="fo-section-note">{_esc(note)}</span>' if note else ""
    _html(f'<div class="fo-section"><span class="fo-section-title">{_esc(title)}</span>{note_markup}</div>')


def empty_state(message: str) -> None:
    _html(f'<div class="fo-empty">{_esc(message)}</div>')


def render_footer(health: dict[str, Any]) -> None:
    year = datetime.now().year
    _html(
        f'<div class="fo-footer">'
        f"<div>© {year} {PRODUCT_NAME} · Predictive Maintenance Platform</div>"
        f'<div class="fo-footer-links">'
        f"<span>Documentation</span><span>API Reference</span><span>Support</span><span>Privacy</span>"
        f"</div>"
        f'<div class="fo-footer-right"><span>v{APP_VERSION}</span>{service_badge(health)}</div>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------


def metric_card(
    label: str,
    value: str,
    detail: str = "",
    unit: str = "",
    emphasis: Emphasis = "default",
) -> None:
    unit_markup = f'<span class="fo-unit">{_esc(unit)}</span>' if unit else ""
    detail_markup = f'<div class="fo-metric-detail">{_esc(detail)}</div>' if detail else ""
    emphasis_class = "" if emphasis == "default" else f" is-{emphasis}"
    _html(
        f'<div class="fo-card fo-metric fo-animate{emphasis_class}">'
        f'<div class="fo-metric-label">{_esc(label)}</div>'
        f'<div class="fo-metric-value">{_esc(value)}{unit_markup}</div>'
        f"{detail_markup}</div>"
    )


def metric_row(metrics: list[dict[str, Any]]) -> None:
    """Render a row of metric cards with even spacing."""
    columns = st.columns(len(metrics), gap="medium")
    for column, metric in zip(columns, metrics):
        with column:
            metric_card(**metric)


def asset_card(
    title: str,
    subtitle: str,
    stats: list[tuple[str, str]],
    condition: str = "normal",
    badges: list[str] | None = None,
) -> None:
    """Compact record card used for assets and incidents."""
    stat_markup = "".join(
        f'<div><div class="fo-stat-label">{_esc(label)}</div>'
        f'<div class="fo-stat-value">{_esc(value)}</div></div>'
        for label, value in stats
    )
    badge_markup = (
        f'<div style="display:flex;gap:.35rem;flex-wrap:wrap">{"".join(badges)}</div>' if badges else ""
    )
    _html(
        f'<div class="fo-card fo-asset fo-animate {_esc(condition)}">'
        f'<div><div class="fo-asset-title">{_esc(title)}</div>'
        f'<div class="fo-asset-sub">{_esc(subtitle)}</div></div>'
        f"{badge_markup}"
        f'<div class="fo-asset-stats">{stat_markup}</div>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


def titleize(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Present status-like columns in Title Case and blank out missing values."""
    out = frame.copy()
    for column in columns:
        if column in out:
            out[column] = (
                out[column].astype(str).str.strip().str.title().replace({"Nan": "—", "None": "—", "": "—"})
            )
    return out


def clean_text(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Replace nulls in free-text columns with an em dash."""
    out = frame.copy()
    for column in columns:
        if column in out:
            out[column] = out[column].astype(str).replace({"nan": "—", "None": "—", "": "—"})
    return out


def data_table(
    frame: pd.DataFrame,
    column_config: dict[str, Any] | None = None,
    height: int | None = None,
    empty_message: str = "No records to display.",
) -> None:
    """Standard table presentation used across the product.

    `height` acts as a maximum: a short table shrinks to its content instead of
    padding the remaining space with blank rows.
    """
    if frame is None or frame.empty:
        empty_state(empty_message)
        return

    options: dict[str, Any] = {}
    if height is not None and len(frame) > _rows_that_fit(height):
        options["height"] = height

    st.dataframe(
        frame,
        column_config=column_config or {},
        width="stretch",
        hide_index=True,
        **options,
    )


# Streamlit renders roughly 35px per row plus a 38px header.
_ROW_PX = 35
_HEADER_PX = 38


def _rows_that_fit(height: int) -> int:
    return max(1, (height - _HEADER_PX) // _ROW_PX)


def percent_column(label: str, help_text: str = "") -> Any:
    return st.column_config.ProgressColumn(
        label, help=help_text or None, format="%.0f%%", min_value=0, max_value=100
    )


def temperature_column(label: str = "Temperature") -> Any:
    return st.column_config.NumberColumn(label, format="%.1f °C")


def currency_column(label: str = "Cost") -> Any:
    return st.column_config.NumberColumn(label, format="%.0f")
