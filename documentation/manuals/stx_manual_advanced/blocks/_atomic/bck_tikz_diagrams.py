import os
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
    "Function Plot": _load("simple_shapes.tex"),
    "Neural Network": _load("neural_network.tex"),
    "Finite Automaton": _load("finite_automaton.tex"),
}

# Only the automaton needs an extra TikZ library
PREAMBLES = {"Finite Automaton": r"\usetikzlibrary{automata,positioning}"}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "TikZ Diagrams", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            stx.st_tikz() renders TikZ diagrams via a local LaTeX pipeline:
            pdflatex + dvisvgm. LaTeX is an optional system dependency.
            If absent, a warning is shown with the raw source as fallback.
        """))
        st_space("v", 2)

        # --- Section 1: Function plot ---
        st_write(bs.sub, "Function Plot", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent(r"""
            stx.st_tikz(r'''
                \begin{tikzpicture}
                    \draw[->] (-0.5,0) -- (5,0) node[right] {$x$};
                    \draw[->] (0,-0.5) -- (0,4) node[above] {$y$};
                    \draw[blue, thick, domain=0:4.5, samples=100]
                        plot (\x, {0.15*\x*\x});
                \end{tikzpicture}
            ''')
        """).strip())
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_tikz(DIAGRAMS["Function Plot"], height=800)
        st_space("v", 2)

        # --- Section 2: Neural network ---
        st_write(bs.sub, "Neural Network", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            TikZ excels at complex technical diagrams. This neural network
            uses foreach loops to connect layers automatically.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent(r"""
            stx.st_tikz(r'''
                \begin{tikzpicture}[
                    neuron/.style={circle, draw, minimum size=0.8cm},
                    input/.style={neuron, fill=blue!20},
                ]
                    \node[input] (i1) at (0,2) {$x_1$};
                    \foreach \i in {1,2,3}
                        \foreach \h in {1,2,3}
                            \draw[->] (i\i) -- (h\h);
                \end{tikzpicture}
            ''')
        """).strip())
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_tikz(DIAGRAMS["Neural Network"], height=800)
        st_space("v", 2)

        # --- Section 3: Finite automaton (with preamble) ---
        st_write(bs.sub, "Finite Automaton (with preamble)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The preamble parameter adds LaTeX packages. Here we use
            the automata and positioning TikZ libraries.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent(r"""
            stx.st_tikz(
                r'''\begin{tikzpicture}[..., state/.style={...}]
                    \node[state, initial] (q0) {$q_0$};
                    \path (q0) edge [bend left] node [above] {a} (q1);
                \end{tikzpicture}''',
                preamble=r"\usetikzlibrary{automata,positioning}"
            )
        """).strip())
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_tikz(DIAGRAMS["Finite Automaton"], height=800,
                        preamble=PREAMBLES["Finite Automaton"])
        st_space("v", 2)

        # --- Section 4: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            diagrams = {"Plot": code1, "Network": code2, ...}
            choice = st.selectbox("Choose a diagram", list(diagrams.keys()))
            stx.st_tikz(diagrams[choice], preamble=preambles.get(choice, ""))
        """))
        st_space("v", 1)

        choice = st.selectbox("Choose a TikZ diagram",
                              [*DIAGRAMS],
                              key="bck_tikz_select")
        with st_block(s.project.containers.result_box):
            stx.st_tikz(DIAGRAMS[choice], height=800, preamble=PREAMBLES.get(choice, ""))
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            TikZ requires pdflatex + dvisvgm installed on the system.
            If LaTeX is absent, a warning and the raw source are displayed.
            Results are cached (st.cache_data) to avoid recompilation.
            Use the preamble parameter for extra packages (pgfplots, automata, etc.).
            Static .tex files can be loaded from the static/diagrams/ folder.
        """))
