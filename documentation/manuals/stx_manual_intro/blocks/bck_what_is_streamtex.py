"""What is StreamTeX? — Library overview and capabilities.

Gives the reader an intuitive understanding of what StreamTeX does,
why it exists, and what they will learn in this course — before
diving into installation.
"""

import textwrap

from streamtex import *
import streamtex as stx
from streamtex.styles import Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation


class BlockStyles:
    """Styles for the overview page."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    feature_title = s.project.titles.feature_title
    feature_box = Style(
        "background: rgba(46, 196, 182, 0.06); "
        "border-left: 3px solid #2EC4B6; "
        "padding: 16px 20px; border-radius: 0 6px 6px 0;",
        "overview_feature_box"
    )
    comparison_raw = Style(
        "background: rgba(231, 76, 60, 0.06); "
        "border-left: 3px solid #E74C3C; "
        "padding: 16px 20px; border-radius: 0 6px 6px 0;",
        "overview_comparison_raw"
    )
    comparison_stx = Style(
        "background: rgba(39, 174, 96, 0.06); "
        "border-left: 3px solid #27AE60; "
        "padding: 16px 20px; border-radius: 0 6px 6px 0;",
        "overview_comparison_stx"
    )
    label_raw = s.project.colors.warning_red + s.text.weights.bold_weight + s.large
    label_stx = s.project.colors.success_green + s.text.weights.bold_weight + s.large


bs = BlockStyles


def build():
    """Render the library overview page."""
    st_space("v", 1)
    st_write(bs.heading, "What is StreamTeX?",
             tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Elevator pitch ---
    show_explanation(textwrap.dedent("""\
        StreamTeX is a Python library built on top of Streamlit.
        It replaces raw HTML/CSS with composable Style objects
        and high-level components — so you write clean Python code
        and get professional, themed, exportable documents.
    """))
    st_space("v", 2)

    # --- The problem it solves ---
    st_write(bs.sub, "The problem", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        Streamlit is great for interactive dashboards, but rendering
        rich documents (courses, presentations, reports) quickly leads to
        verbose HTML strings, duplicated CSS, and no theme support.
    """))
    st_space("v", 1)

    with st_block(bs.comparison_raw):
        st_write(bs.label_raw, "Raw Streamlit")
        st_space("v", 0.5)
        show_code(textwrap.dedent("""\
            st.markdown(
                '<div style="color:navy;font-size:1.2em;font-weight:bold;">'
                'Hello World</div>',
                unsafe_allow_html=True
            )
        """), line_numbers=False)

    st_space("v", 1)

    with st_block(bs.comparison_stx):
        st_write(bs.label_stx, "With StreamTeX")
        st_space("v", 0.5)
        show_code(textwrap.dedent("""\
            style = Style("color:navy; font-size:1.2em; font-weight:bold;", "my_style")
            sx.st_write(style, "Hello World")
        """), line_numbers=False)

    st_space("v", 2)

    # --- Key capabilities ---
    st_write(bs.sub, "Key capabilities", toc_lvl="+1")
    st_space("v", 1)

    _feature(
        "Composable Styles",
        "Create styles from CSS, combine them with +, "
        "remove properties with -. One style, reused everywhere. "
        "Dark mode works automatically — no hardcoded colors needed.",
    )
    _feature(
        "Rich Content Components",
        "st_write for text (with inline mixed styles via tuples), "
        "st_grid for CSS Grid layouts, st_list for bullet/numbered lists, "
        "st_block and st_span for containers, st_image, st_code, st_mermaid, "
        "st_plantuml, st_tikz for diagrams.",
    )
    _feature(
        "Book Navigation",
        "st_book organizes blocks into a paginated or continuous document. "
        "Table of contents with auto-numbering, slide-like markers with "
        "PageUp/PageDown, configurable navigation banners, zoom control.",
    )
    _feature(
        "Block Architecture",
        "Each page is a Python module with a build() function. "
        "Blocks are lazy-loaded (fast startup even with hundreds of pages). "
        "Shared blocks can be reused across projects.",
    )
    _feature(
        "HTML Export",
        "Generate self-contained HTML files from your documents. "
        "Dual rendering pipeline: live Streamlit app and static HTML "
        "from the same source code.",
    )
    _feature(
        "Deploy Anywhere",
        "Docker, Streamlit Cloud, Render.com, Hugging Face Spaces, "
        "GCP — with preflight checks and deployment scripts included.",
    )

    st_space("v", 2)

    # --- What you will learn ---
    st_write(bs.sub, "What you will learn", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        This introduction course walks you through the basics step by step:
    """))
    st_space("v", 0.5)
    with st_list(list_type="ol"):
        st_write(s.large, "Install StreamTeX and create your first project")
        st_write(s.large, "Write text with styles and compose them")
        st_write(s.large, "Build layouts with CSS Grid and lists")
        st_write(s.large, "Add images, code blocks, and diagrams")
        st_write(s.large, "Organize pages with book navigation and TOC")
        st_write(s.large, "Export to HTML and deploy")

    st_space("v", 1)


def _feature(title: str, description: str):
    """Render a single feature box."""
    with st_block(bs.feature_box):
        st_write(bs.feature_title, title)
        st_space("v", 0.5)
        st_write(s.large, description)
    st_space("v", 1)
