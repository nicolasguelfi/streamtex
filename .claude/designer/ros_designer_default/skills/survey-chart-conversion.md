# Survey Chart Conversion Schema — `ros_designer_default`

> Converts Stack Overflow Developer Survey screenshots into **code-generated** StreamTeX blocks.
> The screenshot is the **source** — the output is pure Python code. No static image dependency.

## Source Material

Screenshots from the Stack Overflow Developer Survey site, all following this layout:
- **Left panel**: Title, description paragraph, survey question
- **Right panel**: Horizontal bar chart with category tabs, response count

## Goal

Extract **all data** from the screenshot and generate a self-contained Python block that:
1. Stores chart data as a `SURVEY_DATA` list of `{"label": ..., "value": ...}` dicts
2. Renders the bar chart via `_render_bars()` using `st_html()` (CSS grid + dynamic height)
3. Displays metadata (title, keywords, source, question) via `st_write()`

**Zero image dependency** — the screenshot is only used as a reference during conversion.

## Target Layout — Single Column, 5 Rows

```
┌─────────────────────────────────────────────────┐
│  1. TITLE          (Large + bold, toc_lvl="1")  │
│     KEY STATS      (Large + accent + bold)      │
│     SOURCE         (large + muted + italic)     │
│                         [card container]         │
│                                                 │
│  2. QUESTION       (Large + highlight/amber)    │
│                  [callout_highlight container]    │
│                                                 │
│  3. BAR CHART      (_render_bars() 48px font)   │
│                  [st_html, dynamic height]│
│                                                 │
│  4. RESPONSES      (large + muted)              │
│     Responses: N (X%)       [card container]     │
└─────────────────────────────────────────────────┘
```

**Key design decisions:**
- Question is shown **BEFORE** the chart in a `callout_highlight` box (amber border + bg)
- Question text uses `highlight` color (#FFB547 warm amber) at `Large` size
- Bar chart labels/values use **48px** font (doubled from 24px for projection readability)
- Bar height is **48px** with **8px** border-radius

Header and footer are in `st_block(bs.card)` cards. The bar chart uses `st_html()`
(from `streamtex`) with dynamic `height` based on bar count. No grid, no columns.

## Data Extraction Rules

From the screenshot, extract:

| Field | Source | Example |
|---|---|---|
| `SURVEY_TITLE` | Bold title in left panel | `"Dev IDEs"` |
| `SURVEY_KEYWORDS` | Distill description into 2–3 keyword phrases (5–7 words each) | `["VS Code dominates at 76.2%", "AI IDEs can't topple top spots"]` |
| `SURVEY_SOURCE` | Fixed format + active tab name | `"Stack Overflow Developer Survey 2025 — All Respondents"` |
| `SURVEY_QUESTION` | Question text in the gray box (left panel bottom) | `"Which development environments and AI-enabled code editing tools..."` |
| `SURVEY_DATA` | **Every bar** from the chart: label + percentage value | `[{"label": "VS Code", "value": 76.2}, {"label": "Visual Studio", "value": 29.7}, ...]` |
| `RESPONSE_COUNT` | Bottom-right of chart | `"26,004"` |
| `RESPONSE_PERCENT` | Bottom-right of chart | `"53%"` |

### Chart Data Extraction — Critical Rules

- Extract **ALL bars** from the chart, top to bottom, in the exact order shown
- Read the **percentage value** for each bar (the number shown to the right of the bar)
- Read the **label** for each bar (the text shown to the left of the bar)
- Use the exact label text as shown (do not abbreviate or paraphrase)
- Values are percentages (floats), e.g. `76.2`, `29.7`, `10.0`

### Keyword Extraction Guidelines

- Extract **numbers and trends** first (percentages, rankings, year-over-year changes)
- Max **3 keywords** per chart
- Each keyword: **5–7 words max**
- Format: `"<number/stat> <what it means>"`

### Tab Selection

- Use the **active tab** shown in the screenshot (usually highlighted)
- Include the tab name in `SURVEY_SOURCE`

## Block Naming Convention

- File: `bck_survey_<topic_slug>.py`
- Example: `bck_survey_dev_ides.py`, `bck_survey_ai_sentiment.py`

## Template Code

```python
"""Survey: <TITLE> — Stack Overflow Developer Survey 2025."""

import streamlit as st
from streamtex import *
from streamtex.enums import Tags as t
from custom.styles import Styles as s


# ========================================================================
# DATA — Edit these values to update the chart
# ========================================================================

SURVEY_TITLE = "<title>"

SURVEY_KEYWORDS = [
    "<stat 1>",
    "<stat 2>",
    "<stat 3>",
]

SURVEY_SOURCE = "Stack Overflow Developer Survey 2025 — <tab>"

SURVEY_QUESTION = "<question text>"

SURVEY_DATA = [
    {"label": "<label 1>", "value": <value 1>},
    {"label": "<label 2>", "value": <value 2>},
    # ... one entry per bar, top to bottom
]

RESPONSE_COUNT = "<N>"
RESPONSE_PERCENT = "<X%>"


# ========================================================================
# STYLES
# ========================================================================

# Hex constants from project palette — for st_html() CSS
_MUTED = "#94A3B8"
_BAR_COLOR = "#6C9AEF"


class BlockStyles:
    """Local styles for the survey chart block."""
    title = s.Large + s.bold
    body_accent = s.Large + s.project.colors.accent + s.bold
    source = s.large + s.project.colors.muted + s.italic
    caption = s.large + s.project.colors.muted
    caption_bold = s.large + s.project.colors.muted + s.bold
    card = s.project.containers.card

    # Question box (highlight/amber callout)
    question_box = s.project.containers.callout_highlight
    question_text = s.Large + s.project.colors.highlight

    # Bar chart CSS (st_html — 48px for projection readability)
    bar_label_css = f"color:{_MUTED};font-size:48px;white-space:nowrap;"
    bar_bg_css = f"background:{_BAR_COLOR};border-radius:8px;height:48px;"
    bar_value_css = f"font-size:48px;font-weight:600;white-space:nowrap;"

bs = BlockStyles


# ========================================================================
# RENDERING HELPERS
# ========================================================================

def _render_bars():
    """Render horizontal bar chart from SURVEY_DATA."""
    max_val = max(item["value"] for item in SURVEY_DATA)
    rows = ""
    for item in SURVEY_DATA:
        pct = item["value"] / max_val * 100
        rows += (
            f'<div style="{bs.bar_label_css}">{item["label"]}</div>'
            f'<div><div style="{bs.bar_bg_css}width:{pct}%;"></div></div>'
            f'<div style="{bs.bar_value_css}">{item["value"]}%</div>'
        )
    # Height: each row ~ 72px (48px bar/font + gaps), calculate dynamically
    chart_height = len(SURVEY_DATA) * 72 + 20
    st_html(
        f'<div style="display:grid;grid-template-columns:auto 1fr auto;'
        f'gap:10px 16px;align-items:center;">{rows}</div>',
        height=chart_height,
    )


# ========================================================================
# BUILD
# ========================================================================

def build():
    """Render survey chart — single-column presentation layout."""
    # --- Header: title, keywords, source (inside card) ---
    with st_block(bs.card):
        st_write(bs.title, SURVEY_TITLE, tag=t.div, toc_lvl="1")
        st_space(size=2)
        for kw in SURVEY_KEYWORDS:
            st_write(bs.body_accent, kw)
        st_space(size=2)
        st_write(bs.source, SURVEY_SOURCE)

    st_space(size=2)

    # --- Question (highlight callout — before chart) ---
    with st_block(bs.question_box):
        st_write(bs.question_text, SURVEY_QUESTION)

    st_space(size=2)

    # --- Bar chart (st_html with dynamic height) ---
    _render_bars()

    st_space(size=2)

    # --- Footer: responses (inside card) ---
    with st_block(bs.card):
        st_write(
            bs.caption,
            (bs.caption, "Responses: "),
            (bs.caption_bold, f"{RESPONSE_COUNT} ({RESPONSE_PERCENT})"),
        )
```

## Checklist Before Generating

1. Read the screenshot carefully — zoom in on each bar to read label + value
2. Identify the **active tab** (highlighted text in tab bar)
3. Extract **ALL bars** with exact labels and percentage values
4. Extract title, question, response count exactly as shown
5. Distill description into 2–3 keyword stats
6. Choose a clean slug for the block file
7. Generate the block from the template above
8. Register the block in `book.py`
