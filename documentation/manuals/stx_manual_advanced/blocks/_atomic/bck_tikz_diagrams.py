import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """TikZ diagrams demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    file_label = s.medium + s.italic + s.project.colors.neutral_gray
bs = BlockStyles


DIAGRAMS = {
    "Function Plot": "diagrams/simple_shapes.tex",
    "Neural Network": "diagrams/neural_network.tex",
    "Finite Automaton": "diagrams/finite_automaton.tex",
}

# Only the automaton needs an extra TikZ library
PREAMBLES = {"Finite Automaton": r"\usetikzlibrary{automata,positioning}"}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "TikZ Diagrams", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            stx.st_tikz() renders TikZ diagrams via a local LaTeX pipeline:
            pdflatex + dvisvgm.

            LaTeX is an optional system dependency.
            If absent, a warning is shown with the raw source as fallback.
        """))
        st_space("v", 2)

        # --- Section 1: Function plot ---
        st_write(bs.sub, "Function Plot", toc_lvl="+1")
        st_space("v", 1)

        show_code('stx.st_tikz(file="diagrams/simple_shapes.tex", height=800)')
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_tikz(file=DIAGRAMS["Function Plot"], height=800)
        st_space("v", 1)
        st_write(bs.file_label, f"Source: {DIAGRAMS['Function Plot']}")
        show_code(file=DIAGRAMS["Function Plot"], language="latex")
        st_space("v", 2)

        # --- Section 2: Neural network ---
        st_write(bs.sub, "Neural Network", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            TikZ excels at complex technical diagrams. This neural network
            uses foreach loops to connect layers automatically.
        """))
        st_space("v", 1)

        show_code('stx.st_tikz(file="diagrams/neural_network.tex", height=800)')
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_tikz(file=DIAGRAMS["Neural Network"], height=800)
        st_space("v", 1)
        st_write(bs.file_label, f"Source: {DIAGRAMS['Neural Network']}")
        show_code(file=DIAGRAMS["Neural Network"], language="latex")
        st_space("v", 2)

        # --- Section 3: Finite automaton (with preamble) ---
        st_write(bs.sub, "Finite Automaton (with preamble)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The preamble parameter adds LaTeX packages. Here we use
            the automata and positioning TikZ libraries.
        """))
        st_space("v", 1)

        show_code("""\
stx.st_tikz(
    file="diagrams/finite_automaton.tex",
    height=800,
    preamble=r"\\usetikzlibrary{automata,positioning}",
)""")
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_tikz(file=DIAGRAMS["Finite Automaton"], height=800,
                        preamble=PREAMBLES["Finite Automaton"])
        st_space("v", 1)
        st_write(bs.file_label, f"Source: {DIAGRAMS['Finite Automaton']}")
        show_code(file=DIAGRAMS["Finite Automaton"], language="latex")
        st_space("v", 2)

        # --- Section 4: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code("""\
DIAGRAMS = {
    "Function Plot": "diagrams/simple_shapes.tex",
    "Neural Network": "diagrams/neural_network.tex",
    "Finite Automaton": "diagrams/finite_automaton.tex",
}
PREAMBLES = {"Finite Automaton": r"\\usetikzlibrary{automata,positioning}"}

choice = st.selectbox("Choose a TikZ diagram", [*DIAGRAMS])
stx.st_tikz(file=DIAGRAMS[choice], height=800, preamble=PREAMBLES.get(choice, ""))""")
        st_space("v", 1)

        choice = st.selectbox("Choose a TikZ diagram",
                              [*DIAGRAMS],
                              key="bck_tikz_select")
        with st_block(s.project.containers.result_box):
            stx.st_tikz(file=DIAGRAMS[choice], height=800, preamble=PREAMBLES.get(choice, ""))
        st_space("v", 1)
        st_write(bs.file_label, f"Source: {DIAGRAMS[choice]}")
        show_code(file=DIAGRAMS[choice], language="latex")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            TikZ requires pdflatex + dvisvgm installed on the system.

            If LaTeX is absent, a warning and the raw source are displayed.

            Results are cached (st.cache_data) to avoid recompilation.

            Use the preamble parameter for extra packages (pgfplots, automata, etc.).

            Static .tex files can be loaded from the static/diagrams/ folder.
        """))
