"""What is StreamTeX? — Visual showcase of the library.

A rich, demo-driven introduction that serves as the library's
storefront: every feature is shown live with syntax-highlighted
code alongside the rendered result.
"""

import textwrap

from streamtex import *
import streamtex as stx
from streamtex.styles import Style, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_code_inline


class BlockStyles:
    """Showcase page styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    feature_title = s.project.titles.feature_title

    # Elevator pitch banner
    pitch = Style(
        "background: linear-gradient(135deg, rgba(79,172,254,0.08) 0%, "
        "rgba(0,242,254,0.08) 100%); border-radius: 8px; padding: 24px;",
        "showcase_pitch"
    )

    # Before / after comparison
    before_box = Style(
        "background: rgba(231, 76, 60, 0.06); "
        "border-left: 3px solid #E74C3C; "
        "padding: 16px 20px; border-radius: 0 6px 6px 0;",
        "showcase_before"
    )
    after_box = Style(
        "background: rgba(39, 174, 96, 0.06); "
        "border-left: 3px solid #27AE60; "
        "padding: 16px 20px; border-radius: 0 6px 6px 0;",
        "showcase_after"
    )
    label_before = s.project.colors.warning_red + s.bold + s.large
    label_after = s.project.colors.success_green + s.bold + s.large

    # Live result area
    result = Style(
        "background: rgba(46, 196, 182, 0.06); "
        "border: 1px dashed #2EC4B6; "
        "padding: 12px 16px; border-radius: 6px;",
        "showcase_result"
    )
    result_label = s.project.colors.accent_teal + s.bold + s.medium

    # Grid demo cell
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.center_txt
            + s.container.layouts.vertical_center_layout)

    # Capability card
    card = Style(
        "background: rgba(79, 172, 254, 0.06); "
        "border-left: 3px solid #4facfe; "
        "padding: 16px 20px; border-radius: 0 6px 6px 0;",
        "showcase_card"
    )

    # Gradient demo
    gradient_demo = Style(
        "background: linear-gradient(135deg, #667eea, #764ba2); "
        "border-radius: 8px; padding: 20px;",
        "showcase_gradient"
    )


bs = BlockStyles


def build():
    """Render the library showcase page."""
    st_space("v", 1)
    st_write(bs.heading, "What is StreamTeX?",
             tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # ── Elevator pitch ─────────────────────────────────────────────
    with st_block(bs.pitch):
        st_write(
            s.Large + s.bold + s.center_txt,
            "Write content in Python. Get professional documents.",
            tag=t.div,
        )
        st_space("v", 1)
        st_write(
            s.large + s.center_txt + s.project.colors.neutral_gray,
            "StreamTeX is a library built on Streamlit that replaces "
            "raw HTML/CSS with composable Style objects and high-level "
            "components — so you write clean Python and get themed, "
            "exportable documents.",
            tag=t.div,
        )
    st_space("v", 2)

    # ── Before / After ─────────────────────────────────────────────
    st_write(bs.sub, "The problem it solves", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.before_box):
        st_write(bs.label_before, "Raw Streamlit")
        st_space("v", 0.5)
        show_code(textwrap.dedent("""\
            st.markdown(
                '<div style="color:navy; font-size:1.2em; font-weight:bold;">'
                'Hello World</div>',
                unsafe_allow_html=True
            )
        """), line_numbers=False)

    st_space("v", 1)

    with st_block(bs.after_box):
        st_write(bs.label_after, "With StreamTeX")
        st_space("v", 0.5)
        show_code(textwrap.dedent("""\
            title = Style("color:navy; font-size:1.2em; font-weight:bold;", "title")
            st_write(title, "Hello World")
        """), line_numbers=False)

    st_space("v", 2)

    # ── Live feature showcase ──────────────────────────────────────
    st_write(bs.sub, "Live feature showcase", toc_lvl="+1")
    st_space("v", 1)

    # --- 1. Composable Styles ---
    _section("Composable Styles")
    show_code_inline(
        'title = s.bold + s.Large + s.text.colors.coral',
        line_numbers=False,
    )
    st_space("v", 0.5)
    with st_block(bs.result):
        st_write(bs.result_label, "Result:")
        st_write(
            s.bold + s.Large + s.text.colors.coral,
            "This text is bold, large, and coral",
        )
    st_space("v", 2)

    # --- 2. Inline Mixed Styles ---
    _section("Inline Mixed Styles")
    show_code_inline(
        'st_write(s.Large, (s.text.colors.dodger_blue, "Blue "), '
        '(s.bold, "Bold "), (s.text.colors.coral, "Coral"))',
        line_numbers=False,
    )
    st_space("v", 0.5)
    with st_block(bs.result):
        st_write(bs.result_label, "Result:")
        st_write(
            s.Large,
            (s.text.colors.dodger_blue, "Blue "),
            (s.bold, "Bold "),
            (s.text.colors.coral, "Coral"),
        )
    st_space("v", 2)

    # --- 3. Named Colors ---
    _section("150+ Named Colors")
    show_code_inline(
        'st_write(s.text.colors.coral + s.large, "coral")',
        line_numbers=False,
    )
    st_space("v", 0.5)
    with st_block(bs.result):
        st_write(bs.result_label, "Result:")
        st_space("v", 0.5)
        with st_grid(cols=4, cell_styles=bs.cell) as g:
            with g.cell():
                st_write(s.text.colors.coral + s.large, "coral")
            with g.cell():
                st_write(s.text.colors.dodger_blue + s.large, "dodger_blue")
            with g.cell():
                st_write(s.text.colors.gold + s.large, "gold")
            with g.cell():
                st_write(s.text.colors.teal + s.large, "teal")
            with g.cell():
                st_write(s.text.colors.crimson + s.large, "crimson")
            with g.cell():
                st_write(s.text.colors.lime + s.large, "lime")
            with g.cell():
                st_write(s.text.colors.violet + s.large, "violet")
            with g.cell():
                st_write(s.text.colors.salmon + s.large, "salmon")
    st_space("v", 2)

    # --- 4. CSS Grid ---
    _section("CSS Grid Layouts")
    show_code(textwrap.dedent("""\
        with st_grid(cols=3, cell_styles=cell) as g:
            with g.cell(): st_write(s.large, "Column A")
            with g.cell(): st_write(s.large, "Column B")
            with g.cell(): st_write(s.large, "Column C")
    """), line_numbers=False)
    st_space("v", 0.5)
    with st_block(bs.result):
        st_write(bs.result_label, "Result:")
        st_space("v", 0.5)
        with st_grid(cols=3, cell_styles=bs.cell) as g:
            with g.cell():
                st_write(s.text.colors.dodger_blue + s.large, "Column A")
            with g.cell():
                st_write(s.text.colors.coral + s.large, "Column B")
            with g.cell():
                st_write(s.text.colors.teal + s.large, "Column C")
    st_space("v", 2)

    # --- 5. Styled Containers ---
    _section("Styled Containers")
    show_code(textwrap.dedent("""\
        gradient = Style(
            "background: linear-gradient(135deg, #667eea, #764ba2);"
            "border-radius: 8px; padding: 20px;", "gradient")
        with st_block(gradient):
            st_write(white + s.Large, "Gradient container")
    """), line_numbers=False)
    st_space("v", 0.5)
    with st_block(bs.result):
        st_write(bs.result_label, "Result:")
        st_space("v", 0.5)
        with st_block(bs.gradient_demo):
            st_write(
                s.text.colors.white + s.Large + s.center_txt,
                "Gradient container",
                tag=t.div,
            )
    st_space("v", 2)

    # --- 6. Lists ---
    _section("Styled Lists")
    show_code(textwrap.dedent("""\
        with st_list(list_type=lt.unordered,
                     l_style=s.container.lists.g_docs,
                     li_style=s.large) as l:
            with l.item(): st_write("Styled bullet points")
            with l.item(): st_write("Custom symbols per level")
    """), line_numbers=False)
    st_space("v", 0.5)
    with st_block(bs.result):
        st_write(bs.result_label, "Result:")
        st_space("v", 0.5)
        with st_list(
            list_type=lt.unordered,
            l_style=s.container.lists.g_docs,
            li_style=s.large,
            align="center",
        ) as l:
            with l.item():
                st_write("Styled bullet points")
            with l.item():
                st_write("Custom symbols per level")
            with l.item():
                st_write("Nesting supported")
                with st_list(
                    list_type=lt.unordered,
                    l_style=s.container.lists.g_docs,
                    li_style=s.large,
                ) as l2:
                    with l2.item():
                        st_write("Sub-item with auto indentation")
    st_space("v", 2)

    # --- 7. Syntax-highlighted Code ---
    _section("Syntax-Highlighted Code")
    show_code_inline(
        'st_code(style, code="def hello(): ...", language="python")',
        line_numbers=False,
    )
    st_space("v", 0.5)
    with st_block(bs.result):
        st_write(bs.result_label, "Result:")
        st_space("v", 0.5)
        st_code(
            s.project.containers.code_box,
            code=(
                'def greet(name: str) -> str:\n'
                '    """Return a greeting."""\n'
                '    return f"Hello, {name}!"'
            ),
            language="python",
        )
    st_space("v", 2)

    # ── And much more… ─────────────────────────────────────────────
    st_write(bs.sub, "And much more...", toc_lvl="+1")
    st_space("v", 1)

    with st_grid(
        cols="repeat(auto-fit, minmax(280px, 1fr))",
        grid_style=stx.StxStyles.container.grid.gap_24,
    ):
        _card(
            "Book Navigation",
            "st_book()",
            "Paginated or continuous documents with table of contents, "
            "slide-like markers, PageUp/PageDown, and configurable banners.",
        )
        _card(
            "HTML Export",
            "st_export()",
            "Generate self-contained HTML files. Dual rendering pipeline: "
            "live Streamlit app and static HTML from the same source code.",
        )
        _card(
            "Diagrams",
            "st_mermaid() / st_plantuml() / st_tikz()",
            "Render Mermaid, PlantUML, and TikZ diagrams with "
            "pan/zoom support, directly from Python.",
        )
        _card(
            "Deploy Anywhere",
            "render.sh / preflight.sh",
            "Docker, Streamlit Cloud, Render.com, Hugging Face Spaces, "
            "GCP — with preflight checks and deployment scripts.",
        )

    st_space("v", 2)

    # ── Course outline ─────────────────────────────────────────────
    st_write(bs.sub, "What you will learn", toc_lvl="+1")
    st_space("v", 1)

    with st_list(list_type=lt.ordered, li_style=s.large, align="center") as l:
        with l.item():
            st_write("Install StreamTeX and create your first project")
        with l.item():
            st_write("Write text with styles and compose them")
        with l.item():
            st_write("Build layouts with CSS Grid and lists")
        with l.item():
            st_write("Add images, code blocks, and diagrams")
        with l.item():
            st_write("Organize pages with book navigation and TOC")
        with l.item():
            st_write("Export to HTML and deploy")

    st_space("v", 1)


# ── Helpers ────────────────────────────────────────────────────────

def _section(title: str):
    """Feature showcase section title."""
    st_write(bs.feature_title, title)
    st_space("v", 0.5)


def _card(title: str, api: str, description: str):
    """Capability card with API keyword highlighted as code."""
    with st_block(bs.card):
        st_write(bs.feature_title, title)
        st_space("v", 0.3)
        st_code(None, code=api, language="python")
        st_space("v", 0.5)
        st_write(s.large, description)
