"""Survey: AI tools in the development process — horizontal bar chart.

Reproduces the Stack Overflow Developer Survey 2024 chart (All Respondents).
Edit DATA section below to update values.
"""

import streamlit as st
from streamtex import *
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s


# ========================================================================
# DATA — Edit these values to update the chart
# ========================================================================

SURVEY_TITLE = "AI tools in the development process"

SURVEY_KEYWORDS = [
    "84% use or plan AI tools",
    "51% daily usage among pros",
    "+8% vs 2023",
]

SURVEY_SOURCE = "Stack Overflow Developer Survey 2024 — All Respondents"

SURVEY_DATA = [
    {"label": "Yes, I use AI tools daily", "value": 47.1},
    {"label": "Yes, I use AI tools weekly", "value": 17.7},
    {"label": "Yes, I use AI tools monthly or infrequently", "value": 13.7},
    {"label": "No, but I plan to soon", "value": 5.3},
    {"label": "No, and I don't plan to", "value": 16.2},
]

RESPONSE_COUNT = "33,662"
RESPONSE_PERCENT = "68.7%"


# ========================================================================
# STYLES
# ========================================================================

# Hex constants from project palette — for st_html() CSS (not themed)
_PRIMARY = "#7AB8F5"
_MUTED = "#94A3B8"
_BAR_COLOR = "#6C9AEF"


class BlockStyles:
    """Local styles for the survey chart block."""

    # --- Text styles (composed from project palette) ---
    title = s.Large + s.bold
    body = s.Large
    body_accent = s.Large + s.project.colors.accent + s.bold
    source = s.large + s.project.colors.muted + s.italic
    caption = s.large + s.project.colors.muted
    caption_bold = s.large + s.project.colors.muted + s.bold

    # --- Containers (reuse project styles) ---
    card = s.project.containers.card
    grid_gap = s.project.containers.gap_24

    # --- Bar chart CSS (st_html — uses hex constants above) ---
    bar_label_css = f"color:{_MUTED};font-size:48px;white-space:nowrap;"
    bar_bg_css = f"background:{_BAR_COLOR};border-radius:8px;height:48px;"
    bar_value_css = f"font-size:48px;font-weight:600;white-space:nowrap;"

bs = BlockStyles


# ========================================================================
# RENDERING HELPERS
# ========================================================================

def _render_bars():
    """Render the horizontal bar chart."""
    max_val = max(item["value"] for item in SURVEY_DATA)
    rows = ""
    for item in SURVEY_DATA:
        pct = item["value"] / max_val * 100
        rows += (
            f'<div style="{bs.bar_label_css}">{item["label"]}</div>'
            f'<div><div style="{bs.bar_bg_css}width:{pct}%;"></div></div>'
            f'<div style="{bs.bar_value_css}">{item["value"]}%</div>'
        )
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
    """Render the AI tools survey chart — single-column presentation layout."""
    # --- Header: title, keywords, source ---
    with st_block(bs.card):
        st_write(bs.title, SURVEY_TITLE, tag=t.div, toc_lvl="1")
        st_space(size=2)
        for kw in SURVEY_KEYWORDS:
            st_write(bs.body_accent, kw)
        st_space(size=2)
        st_write(bs.source, SURVEY_SOURCE)

    st_space(size=2)

    # --- Bar chart (full width) ---
    _render_bars()

    st_space(size=2)

    # --- Footer: responses ---
    with st_block(bs.card):
        st_write(
            bs.caption,
            (bs.caption, "Responses: "),
            (bs.caption_bold, f"{RESPONSE_COUNT} ({RESPONSE_PERCENT})"),
        )
