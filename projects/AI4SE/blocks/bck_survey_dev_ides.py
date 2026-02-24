"""Survey: Dev IDEs — Stack Overflow Developer Survey 2025."""

import streamlit as st
from streamtex import *
from streamtex.enums import Tags as t
from custom.styles import Styles as s


# ========================================================================
# DATA — Edit these values to update the chart
# ========================================================================

SURVEY_TITLE = "Dev IDEs"

SURVEY_KEYWORDS = [
    "VS Code dominates at 76.2%",
    "AI IDEs can't topple top spots",
    "Claude Code enters at 10%",
]

SURVEY_SOURCE = "Stack Overflow Developer Survey 2025 — All Respondents"

SURVEY_QUESTION = (
    "Which development environments and AI-enabled code editing tools did you "
    "use regularly over the past year, and which do you want to work with over "
    "the next year?"
)

SURVEY_DATA = [
    {"label": "Visual Studio Code", "value": 76.2},
    {"label": "Visual Studio", "value": 29.7},
    {"label": "IntelliJ IDEA", "value": 28.4},
    {"label": "Notepad++", "value": 26.9},
    {"label": "Vim", "value": 24.0},
    {"label": "Cursor", "value": 19.3},
    {"label": "Android Studio", "value": 14.8},
    {"label": "PyCharm", "value": 14.2},
    {"label": "Neovim", "value": 13.6},
    {"label": "Jupyter Notebook/JupyterLab", "value": 12.0},
    {"label": "Nano", "value": 11.3},
    {"label": "Xcode", "value": 10.6},
    {"label": "Sublime Text", "value": 10.5},
    {"label": "Claude Code", "value": 10.0},
    {"label": "WebStorm", "value": 8.3},
    {"label": "Rider", "value": 7.8},
    {"label": "Zed", "value": 7.5},
    {"label": "Eclipse", "value": 6.7},
    {"label": "PhpStorm", "value": 6.4},
    {"label": "VSCodium", "value": 6.5},
    {"label": "Windsurf", "value": 5.0},
    {"label": "RustRover", "value": 3.3},
    {"label": "Lovable.dev", "value": 2.4},
    {"label": "Bolt", "value": 2.3},
    {"label": "Cline and/or Roo", "value": 2.2},
    {"label": "Aider", "value": 2.0},
    {"label": "Trae", "value": 0.8},
]

RESPONSE_COUNT = "—"
RESPONSE_PERCENT = "—"


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

    # Bar chart CSS (st_html — uses hex constants)
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
    # --- Header: title, keywords, source ---
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

    # --- Bar chart (components_html with dynamic height) ---
    _render_bars()
