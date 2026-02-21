import os
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
    "Flowchart": _load("flowchart.mmd"),
    "Sequence Diagram": _load("sequence.mmd"),
    "Class Diagram": _load("class_diagram.mmd"),
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

        show_code(textwrap.dedent("""\
            stx.st_mermaid('''
                graph TD
                    A[Start] --> B{Is it working?}
                    B -->|Yes| C[Great!]
                    B -->|No| D[Debug]
                    D --> F[Fix code]
                    F --> B
            ''')
        """))
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_mermaid(DIAGRAMS["Flowchart"], key="mermaid_flowchart")
        st_space("v", 2)

        # --- Section 2: Sequence diagram ---
        st_write(bs.sub, "Sequence Diagram", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Sequence diagrams show interactions between components over time.
            Ideal for documenting request/response flows.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            stx.st_mermaid('''
                sequenceDiagram
                    participant U as User
                    participant S as Server
                    U->>S: Request
                    S->>U: Response
            ''')
        """))
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_mermaid(DIAGRAMS["Sequence Diagram"], key="mermaid_sequence")
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
            stx.st_mermaid(DIAGRAMS["Class Diagram"], key="mermaid_class")
        st_space("v", 2)

        # --- Section 4: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            diagrams = {"Flowchart": code1, "Sequence": code2, ...}
            choice = st.selectbox("Choose a diagram", list(diagrams.keys()))
            stx.st_mermaid(diagrams[choice], key="my_mermaid")
        """))
        st_space("v", 1)

        choice = st.selectbox("Choose a Mermaid diagram",
                              [*DIAGRAMS],
                              key="bck_mermaid_select")
        with st_block(s.project.containers.result_box):
            stx.st_mermaid(DIAGRAMS[choice], key="mermaid_interactive")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Mermaid supports: flowcharts, sequence, class, state, ER, Gantt, pie, and more.
            stx.st_mermaid() uses streamlit-mermaid for live rendering.
            HTML export generates SVG via mermaid-py (mermaid.ink service).
            Static .mmd files can be loaded from the static/diagrams/ folder.
        """))
