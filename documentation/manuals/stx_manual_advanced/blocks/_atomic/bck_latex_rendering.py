import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """LaTeX rendering demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


# ---------------------------------------------------------------------------
# Sample LaTeX fragments for the interactive demo
# ---------------------------------------------------------------------------

MATH_EXAMPLES = {
    "Simple equation": r"E = mc^2",
    "Integral": r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}",
    "Matrix": r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}",
    "Sum series": r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}",
}

DOC_EXAMPLES = {
    "Simple text": r"""
\section{Introduction}
This is a simple LaTeX fragment rendered by \textbf{LaTeX.js}.
It supports \emph{emphasis}, \texttt{monospace}, and basic formatting.
""",
    "Lists and structure": r"""
\section{Structured Content}

LaTeX excels at structured documents. Here is a bullet list:

\begin{itemize}
  \item First item with \textbf{bold text}
  \item Second item with \emph{italic text}
  \item Third item with inline math: $a^2 + b^2 = c^2$
\end{itemize}

And a numbered list:

\begin{enumerate}
  \item Step one: define the problem
  \item Step two: solve it
  \item Step three: verify the solution
\end{enumerate}
""",
    "Math and theorems": r"""
\section{Mathematical Content}

\subsection{Equations}

The Cauchy-Schwarz inequality states:

$$\left(\sum_{k=1}^{n} a_k b_k\right)^2 \leq
  \left(\sum_{k=1}^{n} a_k^2\right)
  \left(\sum_{k=1}^{n} b_k^2\right)$$

\subsection{Theorem Environment}

\begin{quote}
\textbf{Theorem} (Fundamental Theorem of Calculus).
Let $f$ be a continuous function on $[a,b]$. Then:
$$\int_a^b f(x)\,dx = F(b) - F(a)$$
where $F$ is any antiderivative of $f$.
\end{quote}

\subsection{Constants}

Some fundamental constants:

\begin{itemize}
  \item Pi: $\pi \approx 3.14159$
  \item Euler's number: $e \approx 2.71828$
  \item Golden ratio: $\varphi \approx 1.61803$
\end{itemize}
""",
    "Full document": r"""
\documentclass{article}
\begin{document}

\section{Full Document}

This source contains \texttt{\textbackslash documentclass} and
\texttt{\textbackslash begin\{document\}}.  Fragments without these
wrappers are auto-wrapped in a minimal \texttt{article} document.
Full documents like this one are passed to LaTeX.js as-is.

\end{document}
""",
}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "LaTeX Rendering", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            If you have existing LaTeX content — articles, course notes,
            formulas — StreamTeX lets you display it directly without
            conversion. Two complementary functions cover all use cases:

            - **st_latex()** — isolated math formulas (KaTeX via Streamlit, fast)
            - **st_latex_doc()** — structured documents and fragments
              (LaTeX.js programmatic API, CDN, zero system dependency)

            Everything runs client-side in the browser. No LaTeX installation required.
        """))
        st_space("v", 2)

        # === When to Use What ===
        st_write(bs.sub, "When to Use What", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            - **st_latex()** — math formulas only (KaTeX via Streamlit native, fastest)
            - **st_latex_doc()** — documents with sections, lists, tables, math
              (LaTeX.js CDN, renders in an isolated iframe)
            - **st_tikz()** — TikZ diagrams (separate LaTeX pipeline, see Diagrams section)
            - **st_markdown()** — when source content is in Markdown, not LaTeX
        """))
        st_space("v", 2)

        # === SIMPLE: Math formulas ===
        st_write(bs.sub, "Simple: Math Formulas", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_latex() wraps Streamlit's native st.latex() renderer.
            Use it for inline or display math. Supports any LaTeX math
            notation: fractions, integrals, matrices, sums, etc.
        """))
        st_space("v", 1)

        show_code("""\
# Simple equation
stx.st_latex(r"E = mc^2")

# Integral
stx.st_latex(r"\\int_0^\\infty e^{-x^2}\\,dx = \\frac{\\sqrt{\\pi}}{2}")

# Sum series
stx.st_latex(r"\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}")""")
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_latex(r"E = mc^2")
            st_space("v", 1)
            stx.st_latex(
                r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}"
            )
            st_space("v", 1)
            stx.st_latex(
                r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}"
            )
        st_space("v", 2)

        # Interactive math selection
        st_write(bs.sub, "Interactive Math Selection", toc_lvl="+1")
        st_space("v", 1)

        choice_math = st.selectbox(
            "Choose a math formula",
            [*MATH_EXAMPLES],
            key="bck_latex_math_select",
        )
        with st_block(s.project.containers.result_box):
            stx.st_latex(MATH_EXAMPLES[choice_math])
        st_space("v", 2)

        # === Document fragments ===
        st_write(bs.sub, "Document Fragments (st_latex_doc)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_latex_doc() renders LaTeX fragments and full documents using
            the LaTeX.js programmatic API (parse + HtmlGenerator) loaded
            from CDN. It runs entirely client-side with zero system
            dependency. Supports sections, lists, math, bold, italic,
            footnotes, quotes, and more.

            - Fragments (no \\\\documentclass) are auto-wrapped in a minimal article
            - Full documents (with \\\\documentclass) are passed to LaTeX.js as-is
        """))
        st_space("v", 1)

        show_code('''\
stx.st_latex_doc(r"""
\\section{Introduction}
This is a simple LaTeX fragment rendered by \\textbf{LaTeX.js}.
It supports \\emph{emphasis}, \\texttt{monospace}, and basic formatting.
""", height=150)''')
        st_space("v", 1)

        # Single interactive selector — renders ONE iframe at a time (perf)
        doc_heights = {
            "Simple text": 150,
            "Lists and structure": 400,
            "Math and theorems": 600,
            "Full document": 200,
        }
        choice_doc = st.selectbox(
            "Choose a LaTeX document example",
            [*DOC_EXAMPLES],
            key="bck_latex_doc_select",
        )
        with st_block(s.project.containers.result_box):
            stx.st_latex_doc(
                DOC_EXAMPLES[choice_doc],
                height=doc_heights.get(choice_doc, 400),
                light_bg=True,
            )
        st_space("v", 2)

        # === Coexistence with StreamTeX ===
        st_write(bs.sub, "Coexistence with StreamTeX", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_latex() and st_latex_doc() coexist naturally with other
            StreamTeX components in the same block. Each st_latex_doc()
            call renders in its own iframe, providing full CSS/JS isolation.
        """))
        st_space("v", 1)

        show_code("""\
# Mix StreamTeX text, math, and document rendering
st_write(s.Large, "Introduction to Linear Algebra")
stx.st_latex(r"\\mathbf{A}\\vec{x} = \\vec{b}")
stx.st_latex_doc(r'''
    \\section{Matrix Operations}
    Solving $\\mathbf{A}\\vec{x} = \\vec{b}$ requires...
''', height=200)""")
        st_space("v", 2)

        # === Utilities ===
        st_write(bs.sub, "Parsing Utilities", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            StreamTeX exports three parsing utilities for extracting
            LaTeX structures from source files. These are pure regex
            functions useful for migration and conversion tools.
        """))
        st_space("v", 1)

        show_code("""\
from streamtex import extract_tikz, extract_math, extract_frames

# Extract all TikZ diagrams
tikz_blocks = extract_tikz(latex_source)

# Extract all math formulas ($, $$, \\[, \\()
math_exprs = extract_math(latex_source)

# Extract all Beamer frames
frames = extract_frames(beamer_source)""")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            **st_latex()** uses Streamlit's native KaTeX renderer. Fast, lightweight, math only.

            **st_latex_doc()** uses the LaTeX.js programmatic API (parse + HtmlGenerator),
            loaded from CDN, running entirely client-side.
            Supports: text, sections, lists, math, bold/italic, footnotes, quotes, refs.
            Does NOT support: TikZ (use st_tikz()), tabular, custom packages, \\def macros.

            **Document handling:**
            - Fragments (no \\\\documentclass) are auto-wrapped in a minimal article document
            - Full documents (with \\\\documentclass) are passed to LaTeX.js as-is

            **Coexistence**: Each st_latex_doc() renders in its own iframe (CSS/JS isolation).
            Mix freely with st_write(), st_tikz(), st_mermaid() in the same block.

            **light_bg**: Forces white background (default True). Set False for transparent.
            **hyphenate**: Enables LaTeX.js hyphenation (default True).
            **file=**: Loads .tex files via resolve_static() (same as st_mermaid, st_tikz).
        """))
