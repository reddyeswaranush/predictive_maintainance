"""Design system for the FactoryOps console.

Every colour, radius, font and motion value used anywhere in the frontend is
defined here once. Views never hard-code a hex value; they import from this
module so the product keeps one consistent visual language.
"""

from __future__ import annotations

from string import Template
from typing import Any

import streamlit as st

# --------------------------------------------------------------------------
# Tokens
# --------------------------------------------------------------------------

LIGHT_COLORS: dict[str, str] = {
    "canvas": "#F3EFED",
    "surface": "#FFFDFC",
    "surface_raised": "#F6F1EF",
    "surface_hover": "#EEE6E3",
    "field": "#FFFDFC",
    "field_border": "rgba(var(--slate-rgb), 0.16)",
    "field_text": "#3F2526",

    "border": "rgba(var(--slate-rgb), 0.16)",
    "border_strong": "rgba(var(--slate-rgb), 0.32)",

    "text": "#3F2526",
    "text_muted": "#6D5958",
    "text_faint": "#958483",

    "accent": "#6C403E",
    "accent_soft": "#7E4D4A",
    "accent_deep": "#55302F",

    "success": "#35A96B",
    "warning": "#E3A329",
    "danger": "#C94D4D",
}

DARK_COLORS: dict[str, str] = {
    "canvas": "#1B1412",
    "surface": "#251B18",
    "surface_raised": "#30221E",
    "surface_hover": "#3A2924",
    "field": "#5C5958",
    "field_border": "#927466",
    "field_text": "#F3DDD0",

    "border": "rgba(var(--slate-rgb), 0.22)",
    "border_strong": "rgba(var(--slate-rgb), 0.42)",

    "text": "#F7EEE7",
    "text_muted": "#D0BDB1",
    "text_faint": "#A89082",

    "accent": "#B9795D",
    "accent_soft": "#D6A184",
    "accent_deep": "#794936",

    "success": "#70B083",
    "warning": "#D8A05D",
    "danger": "#D4776F",
}

THEME_PALETTES: dict[str, dict[str, str]] = {
    "light": LIGHT_COLORS,
    "dark": DARK_COLORS,
}

COLORS: dict[str, str] = LIGHT_COLORS.copy()
FONT_HEADING = "'Plus Jakarta Sans', 'Segoe UI', sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', sans-serif"


def _theme_name() -> str:
    try:
        from frontend import state

        return state.current_theme()
    except Exception:
        return "light"


def set_theme(theme_name: str | None = None) -> None:
    palette = THEME_PALETTES.get(theme_name or _theme_name(), LIGHT_COLORS)
    COLORS.clear()
    COLORS.update(palette)

    global CONDITION_COLORS, CATEGORICAL_SEQUENCE, CONTINUOUS_SCALE, RGB_TOKENS
    CONDITION_COLORS = {
        "normal": COLORS["success"],
        "warning": COLORS["warning"],
        "critical": COLORS["danger"],
    }
    CATEGORICAL_SEQUENCE = [
        COLORS["accent"],
        COLORS["accent_soft"],
        COLORS["success"],
        COLORS["warning"],
        COLORS["danger"],
        COLORS["accent_deep"],
    ]
    CONTINUOUS_SCALE = ["#1B3355", COLORS["accent_deep"], COLORS["accent"], COLORS["accent_soft"]]
    RGB_TOKENS = {
        "accent_rgb": _rgb(COLORS["accent"]),
        "accent_deep_rgb": _rgb(COLORS["accent_deep"]),
        "success_rgb": _rgb(COLORS["success"]),
        "warning_rgb": _rgb(COLORS["warning"]),
        "danger_rgb": _rgb(COLORS["danger"]),
        "surface_rgb": _rgb(COLORS["surface_raised"]),
        "canvas_rgb": _rgb(COLORS["canvas"]),
        "slate_rgb": "201, 189, 194" if theme_name == "light" or theme_name is None else "190, 165, 151",
    }


def _rgb(hex_colour: str) -> str:
    """'#4C9AFF' -> '76, 154, 255'.

    CSS cannot apply an alpha channel to a hex custom property, so every
    translucent tint (hover fills, focus rings, glows) is built with
    `rgba(var(--accent-rgb), .12)`. These derived tokens are what make that
    work, which is why changing a single hex in COLORS recolours the whole
    product - tints included.
    """
    value = hex_colour.lstrip("#")
    return ", ".join(str(int(value[i:i + 2], 16)) for i in (0, 2, 4))


# Derived automatically - never edit these by hand.
CONDITION_COLORS: dict[str, str] = {
    "normal": COLORS["success"],
    "warning": COLORS["warning"],
    "critical": COLORS["danger"],
}
CATEGORICAL_SEQUENCE: list[str] = [
    COLORS["accent"],
    COLORS["accent_soft"],
    COLORS["success"],
    COLORS["warning"],
    COLORS["danger"],
    COLORS["accent_deep"],
]
CONTINUOUS_SCALE: list[str] = ["#1B3355", COLORS["accent_deep"], COLORS["accent"], COLORS["accent_soft"]]
RGB_TOKENS: dict[str, str] = {
    "accent_rgb": _rgb(COLORS["accent"]),
    "accent_deep_rgb": _rgb(COLORS["accent_deep"]),
    "success_rgb": _rgb(COLORS["success"]),
    "warning_rgb": _rgb(COLORS["warning"]),
    "danger_rgb": _rgb(COLORS["danger"]),
    "surface_rgb": _rgb(COLORS["surface_raised"]),
    "canvas_rgb": _rgb(COLORS["canvas"]),
    "slate_rgb": "201, 189, 194",  # neutral blue-grey used for borders/dividers
}


def chart_layout(height: int = 380) -> dict[str, Any]:
    """Shared Plotly layout so every chart in the product matches."""
    slate_grid = f"rgba({RGB_TOKENS['slate_rgb']}, 0.10)"
    slate_zeroline = f"rgba({RGB_TOKENS['slate_rgb']}, 0.16)"
    slate_line = f"rgba({RGB_TOKENS['slate_rgb']}, 0.18)"
    slate_border_strong = f"rgba({RGB_TOKENS['slate_rgb']}, 0.32)"

    axis = {
        "gridcolor": slate_grid,
        "zerolinecolor": slate_zeroline,
        "linecolor": slate_line,
        "tickfont": {"color": COLORS["text_muted"], "size": 11},
        "title": {"font": {"color": COLORS["text_muted"], "size": 12}},
    }
    return {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": COLORS["text"], "family": "Inter, sans-serif", "size": 12},
        "margin": {"l": 8, "r": 12, "t": 24, "b": 12},
        "hoverlabel": {
            "bgcolor": COLORS["surface_raised"],
            "bordercolor": slate_border_strong,
            "font": {"color": COLORS["text"], "family": "Inter, sans-serif"},
        },
        "legend": {"orientation": "h", "y": 1.14, "x": 0, "font": {"color": COLORS["text_muted"]}},
        "xaxis": dict(axis),
        "yaxis": dict(axis),
    }


# --------------------------------------------------------------------------
# Stylesheet
# --------------------------------------------------------------------------

_STYLESHEET = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root {
    --canvas: ${canvas};
    --surface: ${surface};
    --surface-raised: ${surface_raised};
    --surface-hover: ${surface_hover};
    --field: ${field};
    --field-border: ${field_border};
    --field-text: ${field_text};
    --border: ${border};
    --border-strong: ${border_strong};
    --text: ${text};
    --muted: ${text_muted};
    --faint: ${text_faint};
    --accent: ${accent};
    --accent-soft: ${accent_soft};
    --accent-deep: ${accent_deep};
    --success: ${success};
    --warning: ${warning};
    --danger: ${danger};

    /* rgb triplets, for translucent tints - derived from the hexes above */
    --accent-rgb: ${accent_rgb};
    --accent-deep-rgb: ${accent_deep_rgb};
    --success-rgb: ${success_rgb};
    --warning-rgb: ${warning_rgb};
    --danger-rgb: ${danger_rgb};
    --surface-rgb: ${surface_rgb};
    --canvas-rgb: ${canvas_rgb};
    --slate-rgb: ${slate_rgb};

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --shadow-card: 0 1px 2px rgba(0,0,0,.30), 0 12px 32px -18px rgba(0,0,0,.75);
    --shadow-lift: 0 2px 4px rgba(0,0,0,.30), 0 20px 44px -20px rgba(6,20,42,.95);
    --ease: cubic-bezier(.22,.61,.36,1);
    --speed: 180ms;
}

/* ---------------- base canvas ---------------- */
.stApp {
    background:
        radial-gradient(1100px 620px at 78% -12%, rgba(var(--accent-rgb),.13), transparent 62%),
        radial-gradient(900px 560px at 6% 4%, rgba(var(--accent-deep-rgb),.11), transparent 58%),
        var(--canvas);
    color: var(--text);
    font-family: ${font_body};
}
.block-container {
    max-width: 1360px;
    padding: 1.1rem 2.25rem 2rem;
}
h1, h2, h3, h4, h5 {
    font-family: ${font_heading} !important;
    color: var(--field-text) !important;
    letter-spacing: -0.02em;
}
p, li, span, label { font-family: ${font_body}; }
a { color: var(--accent); text-decoration: none; transition: color var(--speed) var(--ease); }
a:hover { color: var(--accent-soft); }

/* Sidebar is intentionally removed - all navigation lives in the header. */
[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'], [data-testid='collapsedControl'] {
    display: none !important;
}
[data-testid='stHeader'] { background: transparent; height: 0; }
#MainMenu, footer[class*='st'] { visibility: hidden; }

/* ---------------- motion ---------------- */
@keyframes fo-rise {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: none; }
}
.fo-animate { animation: fo-rise 380ms var(--ease) both; }

/* ---------------- header ---------------- */
.st-key-app_header {
    background: linear-gradient(180deg, rgba(var(--surface-rgb),.92), rgba(var(--surface-rgb),.86));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: .55rem 1.1rem;
    margin-bottom: 1.35rem;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(12px);
}
.fo-brand { display: flex; align-items: center; gap: .65rem; }
.fo-brand-stacked { flex-direction: column; gap: .1rem; text-align: center; justify-content: center; }
.fo-brand-mark {
    width: 34px; height: 34px; flex: none;
    border-radius: 10px;
    background: linear-gradient(145deg, var(--accent), var(--accent-deep));
    display: flex; align-items: center; justify-content: center;
    font-family: ${font_heading}; font-weight: 800; font-size: .95rem; color: #04101F;
    box-shadow: 0 6px 18px -8px rgba(var(--accent-rgb),.9);
}
.fo-brand-name {
    font-family: ${font_heading}; font-weight: 700; font-size: 1.02rem;
    color: var(--text); line-height: 1.15; letter-spacing: -0.015em;
}
.fo-brand-sub {
    font-size: .66rem; font-weight: 600; letter-spacing: .13em;
    text-transform: uppercase; color: var(--faint);
}

/* Header nav buttons */
.st-key-app_header .stButton > button {
    background: transparent;
    border: 1px solid transparent;
    color: var(--muted);
    font-weight: 600;
    font-size: .855rem;
    border-radius: var(--radius-sm);
    min-height: 2.3rem;
    padding: 0 .55rem;
    transition: color var(--speed) var(--ease), background var(--speed) var(--ease),
                border-color var(--speed) var(--ease), transform var(--speed) var(--ease);
    box-shadow: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
.st-key-app_header .stButton > button:hover {
    color: var(--text);
    background: rgba(var(--accent-rgb),.10);
    border-color: rgba(var(--accent-rgb),.22);
    transform: translateY(-1px);
}
.st-key-app_header .stButton > button[kind='primary'],
.st-key-app_header .stButton > button[data-testid='stBaseButton-primary'] {
    background: rgba(var(--accent-rgb),.15);
    border-color: rgba(var(--accent-rgb),.42);
    color: #DCEBFF;
    box-shadow: inset 0 -2px 0 var(--accent);
}

/* Account popover trigger */
.st-key-app_header [data-testid='stPopover'] button {
    background: rgba(var(--slate-rgb),.07);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 999px;
    font-weight: 600;
    font-size: .82rem;
    min-height: 2.3rem;
    transition: all var(--speed) var(--ease);
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
.st-key-app_header [data-testid='stPopover'] button:hover {
    background: rgba(var(--accent-rgb),.14);
    border-color: var(--border-strong);
}

#theme_toggle {
    height: 2.35rem;
    min-height: 2.35rem;
    align-self: center;
}

/* ---------------- page heading ---------------- */
.fo-page-head {
    display: flex; align-items: flex-end; justify-content: space-between;
    gap: 1rem; flex-wrap: wrap;
    margin: .15rem 0 1.15rem;
    padding-bottom: .85rem;
    border-bottom: 1px solid var(--border);
}
.fo-page-title, .stMarkdown h1.fo-page-title {
    font-family: ${font_heading} !important; font-weight: 700 !important;
    font-size: 1.6rem !important; line-height: 1.25 !important;
    letter-spacing: -0.025em; color: var(--text); margin: 0 !important; padding: 0 !important;
}
.fo-page-meta { display: flex; gap: .45rem; align-items: center; flex-wrap: wrap; }

/* ---------------- cards ---------------- */
.fo-card {
    background: linear-gradient(180deg, rgba(var(--surface-rgb),.62), rgba(var(--surface-rgb),.62));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.05rem 1.15rem;
    box-shadow: var(--shadow-card);
    transition: transform var(--speed) var(--ease), border-color var(--speed) var(--ease),
                box-shadow var(--speed) var(--ease), background var(--speed) var(--ease);
}
.fo-card:hover {
    transform: translateY(-3px);
    border-color: var(--border-strong);
    box-shadow: var(--shadow-lift);
}

/* Metric card */
.fo-metric { min-height: 118px; display: flex; flex-direction: column; gap: .3rem; position: relative; overflow: hidden; }
.fo-metric::after {
    content: ''; position: absolute; inset: auto 0 0 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
    opacity: 0; transition: opacity var(--speed) var(--ease);
}
.fo-metric:hover::after { opacity: 1; }
.fo-metric-label {
    font-size: .68rem; font-weight: 700; letter-spacing: .11em;
    text-transform: uppercase; color: var(--faint);
}
.fo-metric-value {
    font-family: ${font_heading}; font-size: 1.85rem; font-weight: 700;
    line-height: 1.1; color: var(--text); letter-spacing: -0.03em;
}
.fo-metric-value .fo-unit { font-size: 1rem; font-weight: 600; color: var(--muted); margin-left: .12rem; }
.fo-metric-detail { font-size: .775rem; color: var(--muted); line-height: 1.45; }
.fo-metric.is-critical .fo-metric-value { color: var(--danger); }
.fo-metric.is-warning  .fo-metric-value { color: var(--warning); }
.fo-metric.is-success  .fo-metric-value { color: var(--success); }

/* Asset / record card */
.fo-asset {
    display: flex; flex-direction: column; gap: .5rem;
    border-left: 3px solid var(--accent);
    margin-bottom: .7rem;
}
.fo-asset.normal   { border-left-color: var(--success); }
.fo-asset.warning  { border-left-color: var(--warning); }
.fo-asset.critical { border-left-color: var(--danger); }
.fo-asset-title { font-weight: 650; font-size: .93rem; color: var(--text); }
.fo-asset-sub { font-size: .78rem; color: var(--faint); }
.fo-asset-stats { display: flex; gap: 1.15rem; flex-wrap: wrap; margin-top: .1rem; }
.fo-stat-label { font-size: .64rem; letter-spacing: .09em; text-transform: uppercase; color: var(--faint); font-weight: 700; }
.fo-stat-value { font-size: .9rem; font-weight: 650; color: var(--text); font-variant-numeric: tabular-nums; }

/* ---------------- badges ---------------- */
.fo-badge {
    display: inline-flex; align-items: center; gap: .34rem;
    padding: .2rem .6rem; border-radius: 999px;
    font-size: .7rem; font-weight: 650; letter-spacing: .01em;
    border: 1px solid transparent; white-space: nowrap;
    transition: background var(--speed) var(--ease), border-color var(--speed) var(--ease);
}
.fo-badge .fo-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex: none; }
.fo-badge.good { color: var(--success); background: rgba(var(--success-rgb),.11); border-color: rgba(var(--success-rgb),.26); }
.fo-badge.warn { color: var(--warning); background: rgba(var(--warning-rgb),.11); border-color: rgba(var(--warning-rgb),.26); }
.fo-badge.bad  { color: var(--danger);  background: rgba(var(--danger-rgb),.11);  border-color: rgba(var(--danger-rgb),.26); }
.fo-badge.info { color: var(--accent-soft); background: rgba(var(--accent-rgb),.11); border-color: rgba(var(--accent-rgb),.26); }
.fo-badge.mute { color: var(--muted); background: rgba(var(--slate-rgb),.07); border-color: var(--border); }

/* ---------------- section heading ---------------- */
.fo-section {
    display: flex; align-items: baseline; gap: .6rem;
    margin: 1.5rem 0 .8rem;
}
.fo-section-title {
    font-family: ${font_heading}; font-weight: 650;
    font-size: 1rem; color: var(--text); letter-spacing: -0.012em;
}
.fo-section-note { font-size: .78rem; color: var(--faint); }

/* ---------------- empty state ---------------- */
.fo-empty {
    border: 1px dashed var(--border-strong);
    border-radius: var(--radius-lg);
    padding: 2rem 1.25rem;
    text-align: center;
    color: var(--muted);
    background: rgba(var(--surface-rgb),.28);
    font-size: .87rem;
}

/* ---------------- auth ---------------- */
.fo-auth-shell { max-width: 400px; margin: 0 auto; }
.fo-auth-brand { text-align: center; margin: 7vh 0 1.6rem; }
.fo-auth-brand .fo-brand-mark { width: 48px; height: 48px; font-size: 1.3rem; margin: 0 auto .85rem; border-radius: 14px; }
.fo-auth-brand .fo-brand-name { font-size: 1.32rem; }
.fo-auth-brand .fo-brand-sub { margin-top: .28rem; }
.st-key-auth_card {
    background: linear-gradient(180deg, rgba(var(--surface-rgb),.78), rgba(var(--surface-rgb),.78));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.5rem .9rem;
    box-shadow: var(--shadow-lift);
}

/* ---------------- welcome ---------------- */
.fo-welcome { text-align: center; padding: 4vh 0 .4rem; }
.fo-welcome-eyebrow {
    font-size: .7rem; font-weight: 700; letter-spacing: .16em;
    text-transform: uppercase; color: var(--accent); margin-bottom: .7rem;
}
.fo-welcome-title, .stMarkdown h1.fo-welcome-title {
    font-family: ${font_heading} !important; font-weight: 700 !important;
    font-size: 2rem !important; line-height: 1.2 !important;
    letter-spacing: -0.035em; color: var(--text); margin: 0 0 .45rem !important; padding: 0 !important;
}
.fo-welcome-sub { color: var(--muted); font-size: .95rem; }

/* ---------------- footer ---------------- */
.fo-footer {
    margin-top: 2.75rem; padding: 1.15rem 0 .35rem;
    border-top: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem; flex-wrap: wrap;
    font-size: .78rem; color: var(--faint);
}
.fo-footer-links { display: flex; gap: 1.35rem; flex-wrap: wrap; }
.fo-footer-links span { transition: color var(--speed) var(--ease); cursor: default; }
.fo-footer-links span:hover { color: var(--accent-soft); }
.fo-footer-right { display: flex; align-items: center; gap: .8rem; }

/* ---------------- widgets ---------------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: .86rem;
    min-height: 2.5rem;
    border: 1px solid var(--border-strong);
    background: rgba(var(--slate-rgb),.08);
    color: var(--text);
    transition: all var(--speed) var(--ease);
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    background: rgba(var(--accent-rgb),.16);
    border-color: var(--accent);
    color: #fff;
    transform: translateY(-1px);
    box-shadow: 0 8px 20px -12px rgba(var(--accent-rgb),.9);
}
.stButton > button:active, .stFormSubmitButton > button:active { transform: translateY(0); }
.stButton > button[kind='primary'], .stFormSubmitButton > button[kind='primary'],
.stButton > button[data-testid='stBaseButton-primary'],
.stFormSubmitButton > button[data-testid='stBaseButton-primaryFormSubmit'] {
    background: linear-gradient(180deg, var(--accent), var(--accent-deep));
    border-color: transparent;
    color: #041020;
    font-weight: 700;
}
.stButton > button[kind='primary']:hover, .stFormSubmitButton > button[kind='primary']:hover,
.stButton > button[data-testid='stBaseButton-primary']:hover,
.stFormSubmitButton > button[data-testid='stBaseButton-primaryFormSubmit']:hover {
    filter: brightness(1.08);
    color: #041020;
    box-shadow: 0 10px 26px -12px rgba(var(--accent-rgb),1);
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
div[data-baseweb='select'] > div:first-child {
    background: var(--field) !important;
    border: 1px solid var(--field-border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    transition: border-color var(--speed) var(--ease), box-shadow var(--speed) var(--ease);
}
.stTextInput input:hover, .stNumberInput input:hover, .stTextArea textarea:hover,
div[data-baseweb='select'] > div:first-child:hover { border-color: var(--accent) !important; }
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(var(--accent-rgb),.16) !important;
}
div[data-baseweb='select'] > div:first-child {
    min-height: 2.5rem !important;
    background: var(--field) !important;
    color: var(--text) !important;
    border-color: var(--field-border) !important;
}
div[data-baseweb='select'] > div:first-child > div {
    background: transparent !important;
    color: var(--field-text) !important;
}
div[data-baseweb='select'] > div:first-child span {
    color: var(--field-text) !important;
    opacity: 1 !important;
}
div[data-baseweb='select'] > div:first-child svg {
    color: var(--field-text) !important;
    fill: var(--field-text) !important;
}
div[data-testid='stSelectbox'] div[data-baseweb='select'] > div:first-child,
div[data-testid='stMultiSelect'] div[data-baseweb='select'] > div:first-child,
div[data-testid='stSelectbox'] div[data-baseweb='select'] > div:first-child > div,
div[data-testid='stMultiSelect'] div[data-baseweb='select'] > div:first-child > div {
    background: var(--field) !important;
    border-color: var(--field-border) !important;
}
div[data-testid='stSelectbox'] div[data-baseweb='select'],
div[data-testid='stMultiSelect'] div[data-baseweb='select'],
div[data-testid='stSelectbox'] div[data-baseweb='select'] > div,
div[data-testid='stMultiSelect'] div[data-baseweb='select'] > div {
    background: var(--field) !important;
    border-color: var(--field-border) !important;
    border-radius: var(--radius-sm) !important;
}
div[data-testid='stSelectbox'] div[data-baseweb='select'] > div > div,
div[data-testid='stMultiSelect'] div[data-baseweb='select'] > div > div {
    background: transparent !important;
}
div[data-testid='stSelectbox'] div[data-baseweb='select'] > div:first-child:hover,
div[data-testid='stMultiSelect'] div[data-baseweb='select'] > div:first-child:hover {
    border-color: var(--accent) !important;
}
div[data-baseweb='select'] input {
    color: var(--field-text) !important;
    caret-color: var(--accent) !important;
}
.stTextInput label, .stNumberInput label, .stTextArea label,
.stSelectbox label, .stMultiSelect label, .stRadio label {
    color: var(--muted) !important;
    font-size: .8rem !important;
    font-weight: 600 !important;
}
input::placeholder, textarea::placeholder {
    color: var(--field-text) !important;
    opacity: .86 !important;
}

/* Tabs */
.stTabs [data-baseweb='tab-list'] {
    gap: .25rem;
    border-bottom: 1px solid var(--border);
    background: transparent;
}
.stTabs [data-baseweb='tab'] {
    background: transparent;
    border: none;
    color: var(--muted);
    font-weight: 600;
    font-size: .85rem;
    padding: .55rem .9rem;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    transition: color var(--speed) var(--ease), background var(--speed) var(--ease);
}
.stTabs [data-baseweb='tab']:hover { color: var(--text); background: rgba(var(--accent-rgb),.07); }
.stTabs [aria-selected='true'] { color: var(--accent-soft) !important; }
.stTabs [data-baseweb='tab-highlight'] { background: var(--accent) !important; }
.stTabs [data-baseweb='tab-border'] { background: transparent; }

/* Tables */
div[data-testid='stDataFrame'], div[data-testid='stDataFrameResizable'] {
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: border-color var(--speed) var(--ease);
    background: rgba(var(--surface-rgb), .24);
}
div[data-testid='stDataFrame']:hover { border-color: var(--border-strong); }
div[data-testid='stDataFrame'] thead tr th,
div[data-testid='stDataFrameResizable'] thead tr th {
    background: rgba(var(--accent-rgb), .12) !important;
    color: var(--text) !important;
    border-bottom: 1px solid var(--border) !important;
    font-weight: 700 !important;
}
div[data-testid='stDataFrame'] tbody tr td,
div[data-testid='stDataFrameResizable'] tbody tr td {
    background: rgba(var(--surface-rgb), .08) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}
div[data-testid='stDataFrame'] tbody tr:hover td,
div[data-testid='stDataFrameResizable'] tbody tr:hover td {
    background: rgba(var(--accent-rgb), .06) !important;
}

/* Expander */
details, div[data-testid='stExpander'] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: rgba(var(--surface-rgb),.4);
    transition: border-color var(--speed) var(--ease), background var(--speed) var(--ease);
}
div[data-testid='stExpander']:hover { border-color: var(--border-strong) !important; background: rgba(var(--surface-rgb),.62); }
div[data-testid='stExpander'] summary { font-weight: 600; font-size: .86rem; color: var(--text); }

/* Alerts */
div[data-testid='stAlert'] { border-radius: var(--radius-md); border: 1px solid var(--border); font-size: .85rem; }

/* Metric widget fallback */
div[data-testid='stMetric'] {
    background: rgba(var(--surface-rgb),.5);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: .85rem 1rem;
    transition: border-color var(--speed) var(--ease), transform var(--speed) var(--ease);
}
div[data-testid='stMetric']:hover { border-color: var(--border-strong); transform: translateY(-2px); }
div[data-testid='stMetricLabel'] p {
    color: var(--faint) !important; font-size: .68rem !important;
    text-transform: uppercase; letter-spacing: .1em; font-weight: 700 !important;
}
div[data-testid='stMetricValue'] { font-family: ${font_heading}; color: var(--text); }

/* Popover surface */
div[data-baseweb='popover'] [role='option'] { transition: background var(--speed) var(--ease); }
div[data-baseweb='popover'] [role='option']:hover { background: rgba(var(--accent-rgb),.14) !important; }

/* Select and multiselect menus render in a portal outside the page block. */
div[data-baseweb='popover']:has([role='listbox']),
div[data-baseweb='popover']:has([data-baseweb='menu']),
div[data-baseweb='popover'] [role='listbox'],
div[data-baseweb='popover'] [data-baseweb='menu'],
div[data-baseweb='menu'],
ul[role='listbox'] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-card) !important;
}
div[data-baseweb='popover'] [role='listbox'] *,
div[data-baseweb='popover'] [data-baseweb='menu'] *,
div[data-baseweb='menu'] *,
ul[role='listbox'] * {
    color: var(--text) !important;
}
div[data-baseweb='popover'] [role='option'],
div[data-baseweb='menu'] [role='option'],
ul[role='listbox'] [role='option'] {
    background: var(--surface) !important;
    color: var(--text) !important;
}
div[data-baseweb='popover'] [role='option']:hover,
div[data-baseweb='menu'] [role='option']:hover,
ul[role='listbox'] [role='option']:hover {
    background: var(--surface-hover) !important;
}

/* Popover panel */
div[data-baseweb='popover'],
div[data-baseweb='popover'] > div,
div[data-baseweb='popover'] > div > div,
div[data-baseweb='popover'] [role='dialog'],
div[data-testid='stPopoverBody'] {
    background: linear-gradient(180deg, rgba(var(--surface-rgb),.96), rgba(var(--surface-rgb),.98)) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-card) !important;
}
div[data-baseweb='popover'] *,
div[data-testid='stPopoverBody'] * {
    color: var(--text);
}
div[data-baseweb='popover'] button,
div[data-baseweb='popover'] .stButton > button,
div[data-testid='stPopoverBody'] button,
div[data-testid='stPopoverBody'] .stButton > button {
    background: transparent !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}
div[data-baseweb='popover'] .stButton > button[kind='primary'],
div[data-testid='stPopoverBody'] .stButton > button[kind='primary'] {
    background: linear-gradient(180deg, var(--accent), var(--accent-deep)) !important;
    color: #041020 !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Final BaseWeb filter override. Streamlit renders these controls with
   inline/generated styles that otherwise override the shared field tokens. */
div[data-testid='stSelectbox'] [data-baseweb='select'],
div[data-testid='stMultiSelect'] [data-baseweb='select'],
div[data-testid='stSelectbox'] [data-baseweb='select'] > div,
div[data-testid='stMultiSelect'] [data-baseweb='select'] > div,
div[data-testid='stSelectbox'] [data-baseweb='select'] > div:first-child,
div[data-testid='stMultiSelect'] [data-baseweb='select'] > div:first-child {
    background: var(--field) !important;
    border-color: var(--field-border) !important;
    box-shadow: inset 0 0 0 1px var(--field-border) !important;
}
div[data-testid='stSelectbox'] [data-baseweb='select'] span,
div[data-testid='stMultiSelect'] [data-baseweb='select'] span,
div[data-testid='stSelectbox'] [data-baseweb='select'] input,
div[data-testid='stMultiSelect'] [data-baseweb='select'] input,
div[data-testid='stSelectbox'] [data-baseweb='select'] svg,
div[data-testid='stMultiSelect'] [data-baseweb='select'] svg {
    color: var(--field-text) !important;
    fill: var(--field-text) !important;
    -webkit-text-fill-color: var(--field-text) !important;
}
div[data-testid='stSelectbox'] [data-baseweb='select'] > div > div *,
div[data-testid='stMultiSelect'] [data-baseweb='select'] > div > div *,
div[data-testid='stSelectbox'] [data-baseweb='select'] [data-baseweb='select-value'],
div[data-testid='stMultiSelect'] [data-baseweb='select'] [data-baseweb='select-value'] {
    color: var(--field-text) !important;
    -webkit-text-fill-color: var(--field-text) !important;
    opacity: 1 !important;
}
div[data-testid='stSelectbox'] [data-baseweb='select'] > div:first-child,
div[data-testid='stMultiSelect'] [data-baseweb='select'] > div:first-child {
    border: 1px solid var(--field-border) !important;
    outline: 0 !important;
}
div[data-testid='stSelectbox'] [data-baseweb='select']:hover,
div[data-testid='stMultiSelect'] [data-baseweb='select']:hover,
div[data-testid='stSelectbox'] [data-baseweb='select']:focus-within,
div[data-testid='stMultiSelect'] [data-baseweb='select']:focus-within {
    border-color: var(--accent) !important;
    box-shadow: inset 0 0 0 1px var(--accent), 0 0 0 3px rgba(var(--accent-rgb), .12) !important;
}
</style>
"""


def build_stylesheet() -> str:
    """Resolve design tokens into the final CSS. `$name` placeholders only -
    CSS percentages and `%` values pass through untouched."""
    set_theme(_theme_name())
    return Template(_STYLESHEET).substitute(
        **COLORS,
        **RGB_TOKENS,
        font_heading=FONT_HEADING,
        font_body=FONT_BODY,
    )


def apply_theme() -> None:
    """Inject the stylesheet. Call once per rerun, before anything renders."""
    set_theme(_theme_name())
    st.markdown(build_stylesheet(), unsafe_allow_html=True)
