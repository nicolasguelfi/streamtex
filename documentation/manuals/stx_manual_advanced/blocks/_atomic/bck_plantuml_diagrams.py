import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """PlantUML diagrams demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


DIAGRAMS = {
    "Class Diagram": "diagrams/class_diagram.puml",
    "Sequence Diagram": "diagrams/sequence_diagram.puml",
    "Use Case Diagram": "diagrams/usecase_diagram.puml",
}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "PlantUML Diagrams", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            stx.st_plantuml() renders PlantUML diagrams: class diagrams,
            sequence diagrams, use case diagrams, and more. Rendering uses a
            PlantUML server (public by default, configurable). No local
            installation required — only stdlib Python (zlib + urllib).
        """))
        st_space("v", 2)

        # --- Section 1: Class Diagram ---
        st_write(bs.sub, "Class Diagram", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            stx.st_plantuml('''
            @startuml
            class Style {
              +css: str
              +__add__(other): Style
            }
            @enduml
            ''')
        """))
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_plantuml(file=DIAGRAMS["Class Diagram"], height=1000, key="plantuml_class")
        st_space("v", 2)

        # --- Section 2: Sequence Diagram ---
        st_write(bs.sub, "Sequence Diagram", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Sequence diagrams show interactions between components over time.
            Ideal for documenting request/response flows and API calls.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            stx.st_plantuml('''
            @startuml
            actor User
            participant "st_book()" as Book
            User -> Book: run app
            Book --> User: display page
            @enduml
            ''')
        """))
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_plantuml(file=DIAGRAMS["Sequence Diagram"], height=1000, key="plantuml_sequence")
        st_space("v", 2)

        # --- Section 3: Use Case Diagram ---
        st_write(bs.sub, "Use Case Diagram", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use case diagrams visualize system functionality from the
            user's perspective: actors, use cases, and relationships.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_plantuml(file=DIAGRAMS["Use Case Diagram"], height=1000, key="plantuml_usecase")
        st_space("v", 2)

        # --- Section 4: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            diagrams = {"Class": code1, "Sequence": code2, ...}
            choice = st.selectbox("Choose a diagram", list(diagrams.keys()))
            stx.st_plantuml(diagrams[choice], key="my_plantuml")
        """))
        st_space("v", 1)

        choice = st.selectbox("Choose a PlantUML diagram",
                              [*DIAGRAMS],
                              key="bck_plantuml_select")
        with st_block(s.project.containers.result_box):
            stx.st_plantuml(file=DIAGRAMS[choice], height=1000, key="plantuml_interactive")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            PlantUML supports: class, sequence, use case, activity, state,
            component, deployment, object, and many more diagram types.
            stx.st_plantuml() uses a PlantUML HTTP server for rendering.
            The server is configurable (default: public plantuml.com).
            Static .puml files can be loaded from the static/diagrams/ folder.
        """))
