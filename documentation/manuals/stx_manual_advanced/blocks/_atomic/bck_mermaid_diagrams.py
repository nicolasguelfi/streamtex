import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Mermaid diagrams demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    file_label = s.medium + s.italic + s.project.colors.neutral_gray
bs = BlockStyles


DIAGRAMS = {
    "Flowchart": "diagrams/flowchart.mmd",
    "Sequence Diagram": "diagrams/sequence.mmd",
    "Class Diagram": "diagrams/class_diagram.mmd",
}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Mermaid Diagrams", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            stx.st_mermaid() renders Mermaid diagrams: flowcharts, sequence
            diagrams, class diagrams, and more. Live rendering uses the
            streamlit-mermaid component. HTML export generates SVG via mermaid-py.
        """))
        st_space("v", 2)

        # --- Section 1: Flowchart ---
        st_write(bs.sub, "Flowchart", toc_lvl="+1")
        st_space("v", 1)

        show_code(file="examples/diagram/mermaid_flowchart.py")
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_mermaid(file=DIAGRAMS["Flowchart"], height=1000, key="mermaid_flowchart")
        st_space("v", 1)
        st_write(bs.file_label, f"Source: {DIAGRAMS['Flowchart']}")
        show_code(file=DIAGRAMS["Flowchart"], language="text")
        st_space("v", 2)

        # --- Section 2: Sequence diagram ---
        st_write(bs.sub, "Sequence Diagram", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Sequence diagrams show interactions between components over time.
            Ideal for documenting request/response flows.
        """))
        st_space("v", 1)

        show_code(file="examples/diagram/mermaid_sequence.py")
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_mermaid(file=DIAGRAMS["Sequence Diagram"], height=1000, key="mermaid_sequence")
        st_space("v", 1)
        st_write(bs.file_label, f"Source: {DIAGRAMS['Sequence Diagram']}")
        show_code(file=DIAGRAMS["Sequence Diagram"], language="text")
        st_space("v", 2)

        # --- Section 3: Class diagram ---
        st_write(bs.sub, "Class Diagram", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Class diagrams visualize the StreamTeX style system:
            Style composition, inheritance, and block helpers.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_mermaid(file=DIAGRAMS["Class Diagram"], height=1000, key="mermaid_class")
        st_space("v", 1)
        st_write(bs.file_label, f"Source: {DIAGRAMS['Class Diagram']}")
        show_code(file=DIAGRAMS["Class Diagram"], language="text")
        st_space("v", 2)

        # --- Section 4: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(file="examples/diagram/mermaid_interactive.py")
        st_space("v", 1)

        choice = st.selectbox("Choose a Mermaid diagram",
                              [*DIAGRAMS],
                              key="bck_mermaid_select")
        with st_block(s.project.containers.result_box):
            stx.st_mermaid(file=DIAGRAMS[choice], height=1000, key="mermaid_interactive")
        st_space("v", 1)
        st_write(bs.file_label, f"Source: {DIAGRAMS[choice]}")
        show_code(file=DIAGRAMS[choice], language="text")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Mermaid supports: flowcharts, sequence, class, state, ER, Gantt, pie, and more.
            stx.st_mermaid() uses streamlit-mermaid for live rendering.
            HTML export generates SVG via mermaid-py (mermaid.ink service).
            Static .mmd files can be loaded from the static/diagrams/ folder.
        """))
