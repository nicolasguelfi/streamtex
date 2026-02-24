import os
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Graphviz diagrams demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
bs = BlockStyles


# ---------------------------------------------------------------------------
# Load all diagrams from static files (single source of truth)
# ---------------------------------------------------------------------------

# _atomic/ → blocks/ → project root (where static/ lives)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_STATIC_DIR = os.path.join(_PROJECT_ROOT, "static")


def _load(filename: str) -> str:
    path = os.path.join(_STATIC_DIR, "diagrams", filename)
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


DIAGRAMS = {
    "Simple Graph": _load("simple_graph.dot"),
    "StreamTeX Flowchart": _load("flowchart.dot"),
    "Architecture": _load("architecture.dot"),
    "Data Flow": _load("data_flow.dot"),
}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Graphviz Diagrams", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            stx.st_graphviz() renders DOT language diagrams.
            DOT is concise for describing directed graphs.
            Charts are interactive (pan/zoom).
        """))
        st_space("v", 2)

        # --- Section 1: Simple graph ---
        st_write(bs.sub, "Simple Directed Graph", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            stx.st_graphviz('''
                digraph {
                    A -> B -> C -> D -> A
                    A -> C
                }
            ''')
        """))
        st_space("v", 1)

        stx.st_graphviz(DIAGRAMS["Simple Graph"])
        st_space("v", 2)

        # --- Section 2: Styled flowchart ---
        st_write(bs.sub, "Styled Flowchart", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            stx.st_graphviz('''
                digraph {
                    node [shape=box, style="rounded,filled"]
                    book [label="book.py", fillcolor="#4A90D9"]
                    blocks [label="blocks/", fillcolor="#2EC4B6"]
                    book -> blocks [label="st_include"]
                }
            ''')
        """))
        st_space("v", 1)

        stx.st_graphviz(DIAGRAMS["StreamTeX Flowchart"], height=600)
        st_space("v", 2)

        # --- Section 3: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            diagrams = {"Simple Graph": dot1, "Flowchart": dot2, ...}
            choice = st.selectbox("Choose a diagram", list(diagrams.keys()))
            stx.st_graphviz(diagrams[choice])
        """))
        st_space("v", 1)

        choice = st.selectbox("Choose a diagram",
                              [*DIAGRAMS],
                              key="bck31_diagram_select")
        with st_block(s.project.containers.result_box):
            stx.st_graphviz(DIAGRAMS[choice])
        st_space("v", 2)

        # --- Section 4: Self-referential architecture ---
        st_write(bs.sub, "Architecture Diagram", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            This diagram shows the internal architecture of StreamTeX itself:
            st_book orchestrates TOC, markers, blocks, and export.
        """))
        st_space("v", 1)

        stx.st_graphviz(DIAGRAMS["Architecture"])
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            DOT language: concise graph description (nodes, edges, attributes).
            stx.st_graphviz() supports pan and zoom interaction.
            Combine with st.selectbox() to switch between diagrams.
            Requires: uv add graphviz (Python bindings).
            Static .dot files can be loaded from the static/diagrams/ folder.
        """))
