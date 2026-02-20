"""Export-aware widgets demonstration (Phase 1 feature)."""

import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s
import pandas as pd
import numpy as np


class BlockStyles:
    """Styles for export-aware widgets."""

    heading = s.project.titles.section_title + s.center_txt
    section = s.project.titles.section_subtitle
    warning_box = Style("background:rgba(255,100,100,0.1);padding:16px;border-radius:8px;", "warning_box")
    good_box = Style("background:rgba(100,200,100,0.1);padding:16px;border-radius:8px;", "good_box")


bs = BlockStyles


def build():
    """Demonstrate export-aware widgets for HTML export."""

    st_write(bs.heading, "Export-Aware Widgets", tag=t.h1, toc_lvl="1")
    st_space("v", 2)

    # Section 1: The Problem
    st_write(bs.section, "The Problem: st.* Widgets Disappear in Export", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.warning_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "⚠️ Native Streamlit widgets are invisible in HTML export"),
        )
    st_space("v", 1)

    st_write(
        s.medium,
        "When you enable HTML export (st_book(..., export=True)), native st.* widgets "
        "(st.dataframe, st.line_chart, st.table, etc.) become invisible because they use "
        "Streamlit's React pipeline which doesn't export to static HTML.",
    )
    st_space("v", 2)

    # Section 2: The Solution
    st_write(bs.section, "The Solution: Use sx.st_* Wrappers", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.good_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "✓ Use sx.st_* functions instead"),
        )
    st_space("v", 1)

    st_write(
        s.medium,
        "StreamTeX provides export-aware wrappers (sx.st_dataframe, sx.st_line_chart, etc.) "
        "that render BOTH in the live app AND in exported HTML with static fallbacks.",
    )
    st_space("v", 2)

    # Section 3: Available Export-Aware Widgets
    st_write(bs.section, "Available Export-Aware Widgets", toc_lvl="+1")
    st_space("v", 1)

    with st_list(list_type="ul"):
        st_write(s.medium, "sx.st_dataframe() — tables")
        st_write(s.medium, "sx.st_line_chart() — line charts")
        st_write(s.medium, "sx.st_bar_chart() — bar charts")
        st_write(s.medium, "sx.st_area_chart() — area charts")
        st_write(s.medium, "sx.st_scatter_chart() — scatter plots")
        st_write(s.medium, "sx.st_table() — simple tables")
        st_write(s.medium, "sx.st_metric() — metrics")
        st_write(s.medium, "sx.st_json() — JSON display")
        st_write(s.medium, "sx.st_graphviz() — graph diagrams")
        st_write(s.medium, "sx.st_audio() — audio playback")
        st_write(s.medium, "sx.st_video() — video playback")

    st_space("v", 2)

    # Section 4: Live Demo
    st_write(bs.section, "Live Demo: Dataframe", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.medium, "This table will appear in both the live app AND the exported HTML:")
    st_space("v", 1)

    # Create sample data
    df = pd.DataFrame(
        {
            "Name": ["Alice", "Bob", "Charlie", "Diana"],
            "Score": [95, 87, 92, 88],
            "Status": ["Pass", "Pass", "Pass", "Pass"],
        }
    )

    # Use export-aware dataframe (visible in both live app and export)
    sx.st_dataframe(df, use_container_width=True)

    st_space("v", 2)

    # Section 5: Live Demo - Line Chart
    st_write(bs.section, "Live Demo: Line Chart", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.medium, "This chart will appear in both the live app AND the exported HTML:")
    st_space("v", 1)

    # Create sample time series
    chart_data = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=12),
            "Sales": [100, 120, 135, 130, 150, 160, 155, 170, 180, 190, 195, 200],
            "Growth": [0, 20, 15, -5, 20, 10, -5, 15, 10, 10, 5, 5],
        }
    )

    # Use export-aware line chart
    sx.st_line_chart(
        chart_data.set_index("Date")[["Sales", "Growth"]],
    )

    st_space("v", 2)

    # Section 6: Code Examples
    st_write(bs.section, "Code Examples", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.medium + s.text.weights.bold_weight, "WRONG — Won't appear in export:")
    st_space("v", 1)

    with st_block(s.project.containers.code_box):
        st_code("python", """\
# ❌ BAD - disappears in export
import streamlit as st

st.dataframe(df)  # Invisible in HTML export
st.line_chart(data)  # Invisible in HTML export
""")

    st_space("v", 2)

    st_write(s.medium + s.text.weights.bold_weight, "CORRECT — Visible in both:")
    st_space("v", 1)

    with st_block(s.project.containers.code_box):
        st_code("python", """\
# ✓ GOOD - visible in live app AND export
import streamtex as sx

sx.st_dataframe(df)      # Static HTML fallback in export
sx.st_line_chart(data)   # SVG chart in export
""")

    st_space("v", 2)

    # Section 7: Best Practices
    st_write(bs.section, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    with st_list(list_type="ol"):
        st_write(
            s.medium,
            "Always use sx.st_* for widgets when export is enabled",
        )
        st_write(
            s.medium,
            "Use st.* ONLY for interactive elements (buttons, inputs) that won't export",
        )
        st_write(
            s.medium,
            "For custom widgets without sx.st_* wrapper, use sx.st_export() context",
        )
        st_write(
            s.medium,
            "Test HTML export to ensure all data is visible",
        )

    st_space("v", 3)
