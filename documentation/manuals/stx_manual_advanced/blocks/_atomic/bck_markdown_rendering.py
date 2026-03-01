import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Markdown rendering demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


# ---------------------------------------------------------------------------
# Sample Markdown content for the interactive demo
# ---------------------------------------------------------------------------

MARKDOWN_EXAMPLES = {
    "Basic formatting": """\
# Welcome to StreamTeX

This is **bold text** and *italic text*. You can also use ~~strikethrough~~.

- First item
- Second item
  - Nested item
- Third item

> This is a blockquote with **rich** formatting.
""",
    "Tables": """\
## Feature Comparison

| Feature | st_write() | st_markdown() |
|---------|-----------|--------------|
| Styled text | Native StreamTeX | Markdown syntax |
| Tables | st_grid() | Pipe syntax |
| Math | No | $...$ and $$...$$ |
| File loading | No | file= parameter |
""",
    "Math in Markdown": """\
## Mathematics

Inline math: the formula $E = mc^2$ changed physics forever.

Display math:

$$\\int_0^\\infty e^{-x^2}\\,dx = \\frac{\\sqrt{\\pi}}{2}$$

The quadratic formula: $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$
""",
    "Code blocks": """\
## Code Examples

Inline code: use `st_markdown()` for Markdown content.

```python
import streamtex as stx

# Render Markdown with optional styling
stx.st_markdown("# Hello **World**", style=my_style)

# Load from file
stx.st_markdown(file="docs/readme.md")
```
""",
}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Markdown Rendering", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            **st_markdown()** renders interpreted Markdown content using
            Streamlit's native engine. Use it when you have existing Markdown
            content (README files, documentation, notes) that you want to
            display with full formatting support — headings, bold, italic,
            lists, links, tables, code blocks, and even LaTeX math.

            Unlike **st_write()** which applies StreamTeX styles to plain text,
            st_markdown() interprets Markdown syntax and renders it as
            formatted HTML. Both can be used together in the same block.
        """))
        st_space("v", 2)

        # --- Section 1: Basic Formatting ---
        st_write(bs.sub, "Basic Formatting", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Standard Markdown syntax is fully supported: headings (#),
            bold (**), italic (*), strikethrough (~~), lists (- or 1.),
            links, blockquotes (>), and horizontal rules (---).
        """))
        st_space("v", 1)

        show_code(file="examples/markdown/markdown_basic_formatting.py")
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_markdown(MARKDOWN_EXAMPLES["Basic formatting"])
        st_space("v", 2)

        # --- Section 2: Tables and Code Blocks ---
        st_write(bs.sub, "Tables and Code Blocks", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Markdown pipe tables and fenced code blocks with syntax
            highlighting are supported natively. Tables use the standard
            pipe syntax (| col1 | col2 |), and code blocks use triple
            backticks with an optional language identifier.
        """))
        st_space("v", 1)

        show_code(file="examples/markdown/markdown_tables_code.py")
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_markdown(MARKDOWN_EXAMPLES["Tables"])
        st_space("v", 2)

        # --- Section 3: LaTeX Math in Markdown ---
        st_write(bs.sub, "LaTeX Math in Markdown", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Streamlit's Markdown engine natively supports LaTeX math:
            use **$...$** for inline formulas and **$$...$$** for display
            equations. This means you can mix text and math in a single
            Markdown string without switching to st_latex().
        """))
        st_space("v", 1)

        show_code(file="examples/markdown/markdown_latex_math.py")
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_markdown(MARKDOWN_EXAMPLES["Math in Markdown"])
        st_space("v", 2)

        # --- Section 4: Styled Markdown ---
        st_write(bs.sub, "Styled Markdown", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The **style=** parameter wraps the rendered Markdown inside a
            StreamTeX st_block() container. This lets you apply CSS styling
            (background, padding, borders) around the Markdown content
            while keeping the Markdown interpretation intact.
        """))
        st_space("v", 1)

        show_code(file="examples/markdown/markdown_styled.py")
        st_space("v", 2)

        # --- Section 5: Loading from Files ---
        st_write(bs.sub, "Loading from Files", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use **file=** to load Markdown from an external .md file. The
            path is resolved via resolve_static(), so relative paths search
            the configured static source directories. This is ideal for
            reusing existing documentation (README, changelogs, API docs).
        """))
        st_space("v", 1)

        show_code(file="examples/markdown/markdown_file_loading.py")
        st_space("v", 2)

        # --- Section 6: Interactive Selection ---
        st_write(bs.sub, "Interactive Selection", toc_lvl="+1")
        st_space("v", 1)

        show_code(file="examples/markdown/markdown_interactive_selection.py")
        st_space("v", 1)

        choice = st.selectbox(
            "Choose a Markdown example",
            [*MARKDOWN_EXAMPLES],
            key="bck_markdown_select",
        )
        with st_block(s.project.containers.result_box):
            stx.st_markdown(MARKDOWN_EXAMPLES[choice])
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            **st_markdown()** uses Streamlit's native st.markdown() engine.

            **Parameters:**
            - content — Markdown source string (mutually exclusive with file)
            - style — Optional StreamTeX Style wrapping the rendered content
            - file — Path to a .md file (resolved via resolve_static())
            - encoding — File encoding (default: "utf-8")

            **Supported syntax:** headings, bold, italic, strikethrough, lists,
            blockquotes, links, tables (pipe syntax), fenced code blocks with
            syntax highlighting, inline math ($...$), display math ($$...$$).

            **HTML export:** Uses python-markdown with tables and fenced_code
            extensions. Install the markdown package for export support.

            **st_markdown() vs st_write():**
            - st_markdown() interprets Markdown syntax → formatted HTML
            - st_write() applies StreamTeX styles to plain text → styled spans
            - Use st_markdown() for existing Markdown content
            - Use st_write() for StreamTeX-styled inline text with composition
        """))
