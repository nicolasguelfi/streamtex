import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """TikZ diagrams demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
bs = BlockStyles


# ---------------------------------------------------------------------------
# Inline TikZ definitions
# ---------------------------------------------------------------------------

SIMPLE_SHAPES = r"""
\begin{tikzpicture}
    % Axes
    \draw[->] (-0.5,0) -- (5,0) node[right] {$x$};
    \draw[->] (0,-0.5) -- (0,4) node[above] {$y$};

    % Curve
    \draw[blue, thick, domain=0:4.5, samples=100]
        plot (\x, {0.15*\x*\x}) node[right] {$f(x) = 0.15x^2$};

    % Filled area
    \fill[blue!15, domain=1:3, samples=50]
        (1,0) -- plot (\x, {0.15*\x*\x}) -- (3,0) -- cycle;

    % Bounds
    \draw[dashed] (1,0) -- (1,0.15) node[below left] {$a$};
    \draw[dashed] (3,0) -- (3,1.35) node[below right] {$b$};

    % Label
    \node at (2,0.4) {$\int_a^b f$};
\end{tikzpicture}
"""

NEURAL_NETWORK = r"""
\begin{tikzpicture}[
    node distance=1.5cm,
    neuron/.style={circle, draw, minimum size=0.8cm, thick},
    input/.style={neuron, fill=blue!20},
    hidden/.style={neuron, fill=orange!20},
    output/.style={neuron, fill=green!20},
]
    % Input layer
    \node[input] (i1) at (0,2) {$x_1$};
    \node[input] (i2) at (0,0) {$x_2$};
    \node[input] (i3) at (0,-2) {$x_3$};

    % Hidden layer
    \node[hidden] (h1) at (3,1.5) {$h_1$};
    \node[hidden] (h2) at (3,0) {$h_2$};
    \node[hidden] (h3) at (3,-1.5) {$h_3$};

    % Output layer
    \node[output] (o1) at (6,0.75) {$y_1$};
    \node[output] (o2) at (6,-0.75) {$y_2$};

    % Connections input -> hidden
    \foreach \i in {1,2,3}
        \foreach \h in {1,2,3}
            \draw[->] (i\i) -- (h\h);

    % Connections hidden -> output
    \foreach \h in {1,2,3}
        \foreach \o in {1,2}
            \draw[->] (h\h) -- (o\o);

    % Labels
    \node[above=0.3cm] at (0,2.5) {\small Input};
    \node[above=0.3cm] at (3,2) {\small Hidden};
    \node[above=0.3cm] at (6,1.3) {\small Output};
\end{tikzpicture}
"""

FINITE_AUTOMATON = r"""
\begin{tikzpicture}[
    ->, >=stealth, shorten >=1pt,
    node distance=3cm,
    state/.style={circle, draw, minimum size=1cm, thick},
    accepting/.style={state, double},
]
    \node[state, initial] (q0) {$q_0$};
    \node[state] (q1) [right of=q0] {$q_1$};
    \node[accepting] (q2) [right of=q1] {$q_2$};

    \path (q0) edge [bend left] node [above] {a} (q1)
          (q0) edge [loop above] node {b} ()
          (q1) edge [bend left] node [above] {a} (q2)
          (q1) edge [bend left] node [below] {b} (q0)
          (q2) edge [loop above] node {a,b} ();
\end{tikzpicture}
"""

DIAGRAMS = {
    "Function Plot": SIMPLE_SHAPES,
    "Neural Network": NEURAL_NETWORK,
    "Finite Automaton": FINITE_AUTOMATON,
}

# Preamble needed for automata (automata library)
PREAMBLES = {
    "Function Plot": "",
    "Neural Network": "",
    "Finite Automaton": r"\usetikzlibrary{automata,positioning}",
}


def _load_static_diagram(filename: str) -> str:
    """Load a .tex file from the static/diagrams/ folder."""
    path = sx.resolve_static(f"diagrams/{filename}")
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "TikZ Diagrams", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            sx.st_tikz() renders TikZ diagrams via a local LaTeX pipeline:
            pdflatex + dvisvgm. LaTeX is an optional system dependency.
            If absent, a warning is shown with the raw source as fallback.
        """))
        st_space("v", 2)

        # --- Section 1: Simple plot ---
        st_write(bs.sub, "Function Plot", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent(r"""
            sx.st_tikz(r'''
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
            sx.st_tikz(SIMPLE_SHAPES)
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
            sx.st_tikz(r'''
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
            sx.st_tikz(NEURAL_NETWORK)
        st_space("v", 2)

        # --- Section 3: Finite automaton with preamble ---
        st_write(bs.sub, "Finite Automaton (with preamble)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The preamble parameter adds LaTeX packages. Here we use
            the automata and positioning TikZ libraries.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent(r"""
            sx.st_tikz(
                r'''\begin{tikzpicture}[..., state/.style={...}]
                    \node[state, initial] (q0) {$q_0$};
                    \path (q0) edge [bend left] node [above] {a} (q1);
                \end{tikzpicture}''',
                preamble=r"\usetikzlibrary{automata,positioning}"
            )
        """).strip())
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            sx.st_tikz(FINITE_AUTOMATON,
                        preamble=r"\usetikzlibrary{automata,positioning}")
        st_space("v", 2)

        # --- Section 4: Loading from static file ---
        st_write(bs.sub, "Loading from Static Files", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Load a .tex file from static/diagrams/
            path = sx.resolve_static("diagrams/neural_network.tex")
            with open(path) as f:
                code = f.read()
            sx.st_tikz(code)
        """))
        st_space("v", 1)

        static_code = _load_static_diagram("neural_network.tex")
        with st_block(s.project.containers.result_box):
            sx.st_tikz(static_code)
        st_space("v", 2)

        # --- Section 5: Interactive selection ---
        st_write(bs.sub, "Interactive Diagram Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            diagrams = {"Plot": code1, "Network": code2, ...}
            choice = st.selectbox("Choose a diagram", list(diagrams.keys()))
            sx.st_tikz(diagrams[choice], preamble=preambles[choice])
        """))
        st_space("v", 1)

        choice = st.selectbox("Choose a TikZ diagram",
                              [*DIAGRAMS],
                              key="bck_tikz_select")
        with st_block(s.project.containers.result_box):
            sx.st_tikz(DIAGRAMS[choice], preamble=PREAMBLES[choice])
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            TikZ requires pdflatex + dvisvgm installed on the system.
            If LaTeX is absent, a warning and the raw source are displayed.
            Results are cached (st.cache_data) to avoid recompilation.
            Use the preamble parameter for extra packages (pgfplots, automata, etc.).
            Static .tex files can be loaded with sx.resolve_static().
        """))
