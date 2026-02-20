"""Zoom controls and responsive design demonstration."""

import streamlit as st
from streamtex import *
from streamtex.styles import Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s


class BlockStyles:
    """Styles for zoom and responsive demo."""

    heading = s.project.titles.section_title + s.center_txt
    section = s.project.titles.section_subtitle
    info_box = Style("background:rgba(100,150,200,0.1);padding:16px;border-radius:8px;", "info_box")
    code_block = s.project.containers.code_box


bs = BlockStyles


def build():
    """Demonstrate zoom controls and responsive design."""

    st_write(bs.heading, "Zoom Controls & Responsive Design", tag=t.h1, toc_lvl="1")
    st_space("v", 2)

    # Section 1: Zoom Controls
    st_write(bs.section, "Sidebar Zoom Control", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.large,
            (
                s.text.weights.bold_weight,
                "Automatic Feature: ",
            ),
            "StreamTeX automatically adds a zoom control button in the sidebar. "
            "This uses CSS zoom property (Baseline 2024) for pixel-perfect scaling.",
        )
    st_space("v", 2)

    st_write(
        s.medium,
        "👉 Look at your ",
        (s.text.weights.bold_weight, "Sidebar (top right)"),
        " to find the Zoom slider. "
        "Use it to scale the entire page content up/down without reflow.",
    )
    st_space("v", 2)

    # Section 2: How Zoom Works
    st_write(bs.section, "How Zoom Works", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (
                s.text.weights.bold_weight,
                "CSS zoom property: ",
            ),
            "Scales the entire element and descendants without changing layout flow. "
            "Perfect for presentations or accessibility.",
        )
    st_space("v", 1)

    with st_block(s.project.containers.code_box):
        st_code("python", """\
# Zoom is automatically injected by st_book()
# No need to manually add it to your blocks

# Users control it via sidebar slider
# Default range: 80% - 120%
""")
    st_space("v", 2)

    # Section 3: Responsive Design Pattern
    st_write(bs.section, "Responsive Design Patterns", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.medium, "Use these patterns for responsive layouts:")
    st_space("v", 1)

    with st_list(list_type="ul"):
        st_write(s.medium, "CSS Grid with 'repeat(auto-fit, ...)' for flexible columns")
        st_write(s.medium, "Relative sizing: '1fr 2fr' instead of fixed pixels")
        st_write(s.medium, "Percentages for widths and paddings")
        st_write(s.medium, "Mobile-first: start small, scale up with zoom")

    st_space("v", 2)

    # Section 4: Demo Responsive Grid
    st_write(bs.section, "Responsive Grid Demo", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.medium, "This 3-column grid adapts to page width. Try zooming:")
    st_space("v", 2)

    # Create responsive grid (auto-fill)
    responsive_gap = Style("gap:16px;", "responsive_gap")
    with st_grid(
        cols="repeat(auto-fit, minmax(150px, 1fr))",
        grid_style=responsive_gap,
    ):
        for i in range(1, 7):
            with st_block(Style("background:rgba(100,150,200,0.15);padding:12px;border-radius:6px;text-align:center;", f"card_{i}")):
                st_write(s.Large + s.text.weights.bold_weight, str(i))
                st_write(s.medium, f"Card {i}")

    st_space("v", 2)

    # Section 5: Best Practices
    st_write(bs.section, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    with st_list(list_type="ol"):
        st_write(
            s.medium,
            "Never fix font sizes in pixels — use relative sizes (12pt, 14pt, etc.)",
        )
        st_write(
            s.medium,
            "Use grid with 'auto-fit' or 'auto-fill' for adaptive columns",
        )
        st_write(
            s.medium,
            "Test at zoom levels: 80%, 100%, 120% to ensure readability",
        )
        st_write(
            s.medium,
            "Zoom is transparent to users — content stays crisp and proportional",
        )

    st_space("v", 3)
