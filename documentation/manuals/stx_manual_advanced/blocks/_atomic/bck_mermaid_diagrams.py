import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Mermaid diagrams demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
bs = BlockStyles


# ---------------------------------------------------------------------------
# Inline diagram definitions
# ---------------------------------------------------------------------------

SIMPLE_FLOWCHART = """\
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> E[Read logs]
    E --> F[Fix code]
    F --> B
    C --> G[Deploy]\
"""

SEQUENCE = """\
sequenceDiagram
    participant U as User
    participant B as Browser
    participant S as Streamlit
    participant SX as StreamTeX

    U->>B: Open app
    B->>S: HTTP request
    S->>SX: st_book(blocks)
    SX->>SX: Load TOC + Markers
    SX->>S: Render HTML
    S->>B: Response
    B->>U: Display page
    U->>B: Navigate (PageDown)
    B->>S: Rerun
    S->>SX: Render next block
    SX->>S: HTML fragment
    S->>B: Updated page\
"""

CLASS_DIAGRAM = """\
classDiagram
    class Style {
        +str css
        +str name
        +__add__(other) Style
        +__sub__(other) Style
        +create(base, name) Style
    }
    class StreamTeX_Styles {
        +Text text
        +Container container
    }
    class BlockStyles {
        +Style heading
        +Style sub
    }
    class BlockHelper {
        +show_code(code)
        +show_explanation(text)
        +show_details(text)
    }

    StreamTeX_Styles --> Style : composes
    BlockStyles --> Style : uses
    BlockHelper --> Style : renders with\
"""

DIAGRAMS = {
    "Flowchart": SIMPLE_FLOWCHART,
    "Sequence Diagram": SEQUENCE,
    "Class Diagram": CLASS_DIAGRAM,
}


def _load_static_diagram(filename: str) -> str:
    """Load a .mmd file from the static/diagrams/ folder."""
    path = sx.resolve_static(f"diagrams/{filename}")
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Mermaid Diagrams", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            sx.st_mermaid() renders Mermaid diagrams: flowcharts, sequence
            diagrams, class diagrams, and more. Live rendering uses the
            streamlit-mermaid component. HTML export generates SVG via mermaid-py.
        """))
        st_space("v", 2)

        # --- Section 1: Simple flowchart (inline) ---
        st_write(bs.sub, "Flowchart", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            sx.st_mermaid('''
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
            sx.st_mermaid(SIMPLE_FLOWCHART)
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
            sx.st_mermaid('''
                sequenceDiagram
                    participant U as User
                    participant S as Server
                    U->>S: Request
                    S->>U: Response
            ''')
        """))
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            sx.st_mermaid(SEQUENCE)
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
            sx.st_mermaid(CLASS_DIAGRAM)
        st_space("v", 2)

        # --- Section 4: Loading from static file ---
        st_write(bs.sub, "Loading from Static Files", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Load a .mmd file from static/diagrams/
            path = sx.resolve_static("diagrams/flowchart.mmd")
            with open(path) as f:
                code = f.read()
            sx.st_mermaid(code)
        """))
        st_space("v", 1)

        static_code = _load_static_diagram("flowchart.mmd")
        with st_block(s.project.containers.result_box):
            sx.st_mermaid(static_code)
        st_space("v", 2)

        # --- Section 5: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            diagrams = {"Flowchart": code1, "Sequence": code2, ...}
            choice = st.selectbox("Choose a diagram", list(diagrams.keys()))
            sx.st_mermaid(diagrams[choice])
        """))
        st_space("v", 1)

        choice = st.selectbox("Choose a Mermaid diagram",
                              [*DIAGRAMS],
                              key="bck_mermaid_select")
        with st_block(s.project.containers.result_box):
            sx.st_mermaid(DIAGRAMS[choice])
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Mermaid supports: flowcharts, sequence, class, state, ER, Gantt, pie, and more.
            sx.st_mermaid() uses streamlit-mermaid for live rendering.
            HTML export generates SVG via mermaid-py (mermaid.ink service).
            Static .mmd files can be loaded with sx.resolve_static().
        """))
