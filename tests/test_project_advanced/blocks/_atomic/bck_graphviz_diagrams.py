import streamlit as st
from streamtex import *
import streamtex as sx
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

# Pre-defined DOT diagrams
SIMPLE_GRAPH = """
digraph {
    A -> B
    B -> C
    C -> D
    D -> A
    A -> C
}
"""

FLOWCHART = """
digraph {
    rankdir=TB
    node [shape=box, style="rounded,filled", fontname="Helvetica"]
    edge [fontname="Helvetica"]

    book [label="book.py", fillcolor="#4A90D9", fontcolor="white"]
    blocks [label="blocks/", fillcolor="#2EC4B6", fontcolor="white"]
    styles [label="custom/styles.py", fillcolor="#F39C12", fontcolor="white"]
    streamtex [label="streamtex/", fillcolor="#E74C3C", fontcolor="white"]

    book -> blocks [label="st_include"]
    book -> styles [label="imports"]
    blocks -> streamtex [label="sx.*"]
    blocks -> styles [label="s.*"]
    streamtex -> styles [label="inherits"]
}
"""

ARCHITECTURE = """
digraph {
    rankdir=LR
    node [shape=record, style=filled, fontname="Helvetica"]

    st_book [label="{st_book|entry point}", fillcolor="#4A90D9", fontcolor="white"]
    toc [label="{TOC|sidebar nav}", fillcolor="#2EC4B6", fontcolor="white"]
    marker [label="{Markers|page nav}", fillcolor="#2EC4B6", fontcolor="white"]
    block [label="{block.build()|content}", fillcolor="#F39C12", fontcolor="white"]
    style [label="{Style|css compose}", fillcolor="#E74C3C", fontcolor="white"]
    export [label="{Export|HTML output}", fillcolor="#27AE60", fontcolor="white"]

    st_book -> toc
    st_book -> marker
    st_book -> block
    block -> style
    st_book -> export
}
"""

DATA_FLOW = """
digraph {
    rankdir=TB
    node [shape=ellipse, style=filled, fontname="Helvetica"]

    user [label="User Input", fillcolor="#95A5A6", fontcolor="white"]
    widget [label="st.* Widget", fillcolor="#4A90D9", fontcolor="white"]
    state [label="Session State", fillcolor="#F39C12", fontcolor="white"]
    render [label="sx.* Render", fillcolor="#2EC4B6", fontcolor="white"]
    html [label="HTML Output", fillcolor="#E74C3C", fontcolor="white"]

    user -> widget [label="interacts"]
    widget -> state [label="updates"]
    state -> render [label="drives"]
    render -> html [label="produces"]
    html -> user [label="displays"]
}
"""

DIAGRAMS = {
    "Simple Graph": SIMPLE_GRAPH,
    "StreamTeX Flowchart": FLOWCHART,
    "Architecture": ARCHITECTURE,
    "Data Flow": DATA_FLOW,
}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Graphviz Diagrams", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            sx.st_graphviz() renders DOT language diagrams.
            DOT is concise for describing directed graphs.
            Charts are interactive (pan/zoom).
        """))
        st_space("v", 2)

        # --- Section 1: Simple graph ---
        st_write(bs.sub, "Simple Directed Graph", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            sx.st_graphviz('''
                digraph {
                    A -> B -> C -> D -> A
                    A -> C
                }
            ''')
        """))
        st_space("v", 1)

        sx.st_graphviz(SIMPLE_GRAPH)
        st_space("v", 2)

        # --- Section 2: Styled flowchart ---
        st_write(bs.sub, "Styled Flowchart", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            sx.st_graphviz('''
                digraph {
                    node [shape=box, style="rounded,filled"]
                    book [label="book.py", fillcolor="#4A90D9"]
                    blocks [label="blocks/", fillcolor="#2EC4B6"]
                    book -> blocks [label="st_include"]
                }
            ''')
        """))
        st_space("v", 1)

        sx.st_graphviz(FLOWCHART)
        st_space("v", 2)

        # --- Section 3: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            diagrams = {"Simple Graph": dot1, "Flowchart": dot2, ...}
            choice = st.selectbox("Choose a diagram", list(diagrams.keys()))
            sx.st_graphviz(diagrams[choice])
        """))
        st_space("v", 1)

        choice = st.selectbox("Choose a diagram",
                              [*DIAGRAMS],
                              key="bck31_diagram_select")
        with st_block(s.project.containers.result_box):
            sx.st_graphviz(DIAGRAMS[choice])
        st_space("v", 2)

        # --- Section 4: Self-referential architecture ---
        st_write(bs.sub, "Architecture Diagram", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            This diagram shows the internal architecture of StreamTeX itself:
            st_book orchestrates TOC, markers, blocks, and export.
        """))
        st_space("v", 1)

        sx.st_graphviz(ARCHITECTURE)
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            DOT language: concise graph description (nodes, edges, attributes).
            sx.st_graphviz() supports pan and zoom interaction.
            Combine with st.selectbox() to switch between diagrams.
            Requires: uv add graphviz (Python bindings).
        """))
