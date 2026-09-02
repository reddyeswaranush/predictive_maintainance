# Customisation Guide

Where to change things. Every line number refers to the files as shipped — if
you edit a file, later numbers in that same file shift, so re-check before a
second edit to the same file.

**The one rule:** colours are defined in exactly one place (`theme.py` lines
20–34). Everything else — cards, charts, badges, borders, buttons, tables —
reads from there. Change a hex there and the whole product follows. Never write
a hex code inside a `views/` file.

---

## Quick lookup

| I want to change… | File | Line |
|---|---|---|
| Any colour in the app | `frontend/theme.py` | 20–34 |
| Streamlit's own widget colours | `.streamlit/config.toml` | 2–7 |
| Fonts | `frontend/theme.py` | 37–38 (+ 118) |
| Corner roundness | `frontend/theme.py` | 147–149 |
| Hover/animation speed | `frontend/theme.py` | 152–153 |
| Page width | `frontend/theme.py` | 166 |
| Product name / logo initials | `frontend/components.py` | 19–21, 50 |
| Footer links | `frontend/components.py` | 168 |
| Navigation menu items | `frontend/state.py` | 19–26 |
| Demo usernames + passwords | `frontend/state.py` | 41–57 |
| Risk / temperature thresholds | `frontend/transforms.py` | 15–18 |
| Backend URL | `frontend/api.py` | 17 |
| Data refresh rate | `frontend/api.py` | 37, 49 |
| Browser tab title | `frontend/app.py` | 24–25 |
| Page headings | `frontend/app.py` | 68–101 |

---

## 1. `frontend/theme.py` — all styling

The most important file. Two parts: **tokens** (top, plain Python) and the
**stylesheet** (a long CSS string that reads those tokens).

### Colours — lines 20–34

```python
COLORS: dict[str, str] = {
    "canvas":         "#08111F",   # 20 - page background (darkest)
    "surface":        "#0E1B2E",   # 21 - card background
    "surface_raised": "#132540",   # 22 - header, popover
    "surface_hover":  "#172C4A",   # 23 - hover fill
    "border":         "rgba(120, 165, 225, 0.16)",  # 24 - normal card border
    "border_strong":  "rgba(120, 165, 225, 0.32)",  # 25 - hovered border
    "text":           "#E4ECF7",   # 26 - headings, values
    "text_muted":     "#8CA3C4",   # 27 - body text, labels
    "text_faint":     "#5F779B",   # 28 - captions, footer
    "accent":         "#4C9AFF",   # 29 - PRIMARY BLUE (buttons, active nav)
    "accent_soft":    "#7FC1FF",   # 30 - lighter blue (hover, links)
    "accent_deep":    "#1E5FBF",   # 31 - darker blue (gradients)
    "success":        "#3DD68C",   # 32 - green: normal, online, completed
    "warning":        "#F5B544",   # 33 - amber: warning, idle, scheduled
    "danger":         "#F0655F",   # 34 - red: critical, offline, open
}
```

**Worked example — switch from blue to teal.** Change three lines:

```python
"accent":      "#2DD4BF",   # line 29
"accent_soft": "#5EEAD4",   # line 30
"accent_deep": "#0F766E",   # line 31
```

Then update `.streamlit/config.toml` line 3 to `primaryColor = "#2DD4BF"` so
native widgets match. That's it. Buttons, active nav, focus rings, hover fills, button glows, chart
palette, links and badges all shift together — verified by rebuilding the
stylesheet and confirming zero occurrences of the old blue remain, in either hex
or rgb form.

**Worked example — switch to a light theme.** Swap the dark values for light
ones and raise the text contrast:

```python
"canvas":         "#F6F8FC",   # 20
"surface":        "#FFFFFF",   # 21
"surface_raised": "#FFFFFF",   # 22
"surface_hover":  "#EEF3FA",   # 23
"border":         "rgba(20, 50, 95, 0.12)",   # 24
"border_strong":  "rgba(20, 50, 95, 0.26)",   # 25
"text":           "#0E1B2E",   # 26
"text_muted":     "#44566F",   # 27
"text_faint":     "#71829A",   # 28
```

Then in `.streamlit/config.toml`: `base = "light"` (line 2),
`backgroundColor = "#F6F8FC"` (4), `secondaryBackgroundColor = "#FFFFFF"` (5),
`textColor = "#0E1B2E"` (6).

One extra step for a light theme: `theme.py` lines 159–160 draw two faint blue
glows over the background. Lower the alpha values (`.13` and `.11`) to about
`.05` or they'll look muddy on a pale canvas.

### Chart colours — lines 41–57

Derived from `COLORS`, so they follow automatically. Only touch these if you
want charts to differ from the rest of the UI.

- **41–45** `CONDITION_COLORS` — the green/amber/red used for normal / warning /
  critical in the risk bars, scatter plot and status badges.
- **48–55** `CATEGORICAL_SEQUENCE` — the ordered palette for bar charts with no
  semantic meaning (jobs-by-status, stock levels). Reorder or extend freely.

### Fonts — lines 37–38

```python
FONT_HEADING = "'Plus Jakarta Sans', 'Segoe UI', sans-serif"   # 37
FONT_BODY    = "'Inter', 'Segoe UI', sans-serif"               # 38
```

Both are loaded from Google Fonts on **line 118**. If you name a different font
you must also change that import line, or the browser falls back to Segoe UI.
For example, to use Poppins for headings, line 118 becomes:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap');
```

…and line 37 becomes `"'Poppins', 'Segoe UI', sans-serif"`.

### Shape, motion, spacing — lines 147–166

| Line | Token | Effect |
|---|---|---|
| 147 | `--radius-sm: 8px` | buttons, inputs, tabs |
| 148 | `--radius-md: 12px` | tables, expanders, alerts |
| 149 | `--radius-lg: 16px` | cards, header, login panel |
| 150 | `--shadow-card` | resting card shadow |
| 152 | `--ease` | easing curve for every transition |
| 153 | `--speed: 180ms` | **hover speed — raise to 300ms for slower, 0ms to disable** |
| 166 | `max-width: 1360px` | content width; raise for wider monitors |

Set line 153 to `0ms` and every hover becomes instant. To remove the fade-in on
page load instead, delete the `.fo-animate` rule at **line 190**.

### Text sizes

- **273** `.fo-page-title` — page headings ("Dashboard", "Fleet")
- **308** `.fo-metric-value` — the big numbers on KPI cards
- **390** `.fo-welcome-title` — "Welcome back, …"

### Derived RGB tokens — do not edit

Just below `CONTINUOUS_SCALE` you'll find `_rgb()` and a `RGB_TOKENS` dict.
These exist because CSS **cannot** apply transparency to a hex variable — you
can't write `rgba(var(--accent), .1)` when `--accent` is `#4C9AFF`. So every
translucent tint in the app (hover fills, focus rings, button glows, badge
backgrounds) is built from a matching `--accent-rgb: 76, 154, 255` token, which
is computed automatically from your hex.

The practical upshot: **change the hex on line 29 and the tints follow too.**
You never edit `RGB_TOKENS` yourself.

### Safety note

The stylesheet uses `$name` placeholders (e.g. `${accent}`), **not** `%`. This
matters: an earlier version used `%`-formatting and crashed because CSS is full
of `%` characters. If you add a new token, write `${my_token}` and add the key
to the `COLORS` dict — nothing else needed.

---

## 2. `.streamlit/config.toml` — native widget theme

Streamlit renders tables, dropdowns and date pickers itself; CSS can't reach
inside them. This file colours those. **Keep it in sync with `theme.py`:**

| Line | Key | Should match |
|---|---|---|
| 2 | `base` | `"dark"` or `"light"` |
| 3 | `primaryColor` | `COLORS["accent"]` |
| 4 | `backgroundColor` | `COLORS["canvas"]` |
| 5 | `secondaryBackgroundColor` | roughly `COLORS["surface"]` |
| 6 | `textColor` | `COLORS["text"]` |

Streamlit only reads this **at startup** — restart the server after editing.

---

## 3. `frontend/components.py` — shared UI pieces

### Branding — lines 19–21

```python
PRODUCT_NAME     = "FactoryOps"             # 19 - header + footer
PRODUCT_SUBTITLE = "Predictive Maintenance" # 20 - small caps under the name
APP_VERSION      = "1.0.0"                  # 21 - footer right
```

The square logo initials are on **line 50** (`>FO<`). Two characters fit; more
will overflow the 34px box.

### Footer links — line 168

```python
f"<span>Documentation</span><span>API Reference</span><span>Support</span><span>Privacy</span>"
```

To make them real links, swap a `<span>` for `<a href="…" target="_blank">`.
The hover colour is already styled in the `.fo-footer-links span:hover` rule.

### Other useful spots

- **62** `badge()` — the badge component; tones are `good` / `warn` / `bad` /
  `info` / `mute`
- **67** `tone_for_state()` — maps a status word to a colour. Add new statuses
  here, e.g. put `"paused"` in the warn branch
- **90** `render_header()` — header layout. Line 92's `[2.3, 6.2, 2.3]` sets the
  brand / nav / account column split
- **180** `metric_card()` — KPI card
- **286–287** `_ROW_PX = 35`, `_HEADER_PX = 38` — used to decide whether a table
  needs a scrollbar. Leave alone unless Streamlit changes its row height

---

## 4. `frontend/state.py` — navigation and login

### Navigation menu — lines 19–26

```python
NAV_ITEMS: list[tuple[str, str]] = [
    ("dashboard",   "Dashboard"),
    ("fleet",       "Fleet"),
    ("predictions", "Predictions"),
    ("maintenance", "Maintenance"),
    ("records",     "Records"),
]
```

First item of each tuple is the internal route key, second is the visible label.

- **Rename a tab:** change only the second value. Nothing else breaks.
- **Reorder:** move whole lines. The first entry becomes the landing page.
- **Add a page:** add a tuple here, create `views/yourpage.py`, import it in
  `app.py` line 33, and add an `elif route == "yourkey":` branch around line 100.
- **Remove a page:** delete the tuple *and* its branch in `app.py`. Deleting only
  the tuple leaves unreachable code.

Five items fit comfortably; past seven the header gets cramped on a laptop.

### Demo accounts — lines 41–57

```python
"password": os.getenv("FACTORYOPS_ADMIN_PASSWORD", "FactoryOps@123"),  # 43
"name":     "Operations Lead",       # 44 - shown in "Welcome back, …"
"role":     "System Administrator",  # 45 - shown under the greeting
```

Add an account by copying the three-line block. **Line 39** `ROLES` controls the
dropdown on the sign-up tab.

⚠️ These are plaintext passwords held in memory, and new sign-ups vanish on
restart. Fine for a demo; don't present it as real authentication.

---

## 5. `frontend/transforms.py` — business rules

### Thresholds — lines 15–18

```python
TEMPERATURE_CRITICAL = 100.0   # 15 - °C at or above → critical
TEMPERATURE_WARNING  =  80.0   # 16 - °C at or above → warning
RISK_CRITICAL        =   0.60  # 17 - failure probability → critical
RISK_WARNING         =   0.30  # 18 - failure probability → warning
```

These decide the red/amber/green everywhere: card borders, badges, chart bars,
the "Critical assets" count. Changing line 17 to `0.50` immediately reclassifies
machines across the whole app.

Risk is a **fraction** (0.60 = 60%), not a percentage.

### Status word lists — lines 20–21

`HEALTHY_STATES` (green) and `ALERT_STATES` (red); anything unlisted renders
grey. Add your own vocabulary here.

---

## 6. `frontend/api.py` — backend connection

- **17** `API_BASE_URL` — defaults to `http://127.0.0.1:8000`. Override without
  editing code: `export FACTORYOPS_API_URL=http://your-server:8000`
- **18** `REQUEST_TIMEOUT_SECONDS = 4` — raise if your backend is slow
- **37** `ttl=15` — how long record data is cached, in seconds
- **49** `ttl=10` — how long the health check is cached

Lower the TTLs for fresher data at the cost of more API calls.

---

## 7. `frontend/app.py` — routing and page titles

- **24** `page_title` — browser tab text
- **25** `page_icon="◧"` — favicon; any emoji or character works
- **68–101** — one branch per page. The `ui.page_head(...)` call in each sets the
  visible heading and its status badges.

Example — rename the Dashboard heading, line 69–72:

```python
ui.page_head(
    "Operations Overview",                                    # ← heading text
    [ui.badge(f"{len(machine_view)} assets", "info"), ui.service_badge(health)],
)
```

---

## 8. `frontend/views/` — individual pages

Each file owns one page. Common tweaks:

| Change | File | Line |
|---|---|---|
| Bars shown on the risk chart (8) | `dashboard.py` | 90 |
| Attention cards shown (4) | `dashboard.py` | 131 |
| "Average health" green/amber cutoff (70) | `dashboard.py` | 67 |
| KPI card labels | `dashboard.py` | 58, 63, 70, 76 |
| Machine status dropdown options | `fleet.py` | 20 |
| Signals offered in Signal history | `fleet.py` | 19 |
| Priority queue length (8) | `predictions.py` | 62 |
| Incident board columns | `predictions.py` | 13 |
| Low-stock chart length (10) | `maintenance.py` | 116 |
| Telemetry form fields | `records.py` | 16 |
| Records tab names | `records.py` | 35 |

Note on `records.py` line 16 and `fleet.py` line 19: those field names map
directly to the backend's telemetry schema. Renaming a key breaks the POST;
renaming only the *label* (the second value in each tuple) is safe.

---

## After editing

Streamlit hot-reloads Python files — just save and the browser refreshes.

Two exceptions that need a **full server restart** (`Ctrl+C`, then
`streamlit run frontend/app.py`):

1. Any change to `.streamlit/config.toml`
2. Changes to `state.py` login accounts, if you're already signed in — sign out
   first, since your old session is cached

If a colour change seems to do nothing, it's almost always a hard-coded value in
a `views/` file rather than `theme.py`. Search for it:

```bash
grep -rn "#[0-9A-Fa-f]\{6\}" frontend/views/
```

That should return **nothing**. Any hit is a bug worth moving into `theme.py`.
