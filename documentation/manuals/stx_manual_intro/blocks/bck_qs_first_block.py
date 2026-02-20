"""Quick Start — First Block & Run."""

import textwrap
from streamtex import *
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details


class BlockStyles:
    """Quick Start first block styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle


bs = BlockStyles


def build():
    """Quick Start Step 3: Write your first block and run the project."""
    st_space("v", 1)
    st_write(bs.heading, "Quick Start — First Block & Run",
             tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Create a block file ---
    st_write(bs.sub, "Step 1: Create a block file", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        Create a new file in blocks/ with the bck_ prefix.
        Every block needs a BlockStyles class, a bs alias,
        and a build() function.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # blocks/bck_hello.py
        from streamtex import *
        import streamtex as stx
        from streamtex.enums import Tags as t

        _sts = stx.StxStyles


        class BlockStyles:
            title = _sts.huge + _sts.text.colors.reset
            body = _sts.large

        bs = BlockStyles


        def build():
            st_write(bs.title, "Hello StreamTeX!", tag=t.h1, toc_lvl="1")
            st_space("v", 1)
            st_write(bs.body, "This is my first block.")
    """))
    st_space("v", 2)

    # --- Register in book.py ---
    st_write(bs.sub, "Step 2: Register in book.py", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        Add your new block to the module list in book.py.
        The block auto-discovery in blocks/__init__.py
        makes it available as blocks.bck_hello.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # book.py — add your block to st_book
        st_book([
            blocks.bck_welcome,
            blocks.bck_hello,      # <-- your new block
        ], toc_config=toc, paginate=True)
    """))
    st_space("v", 2)

    # --- Run the project ---
    st_write(bs.sub, "Step 3: Run the project", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        Launch your project with Streamlit.
        The browser opens automatically.
        Edit any block and the page hot-reloads.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        uv run streamlit run projects/my_project/book.py
    """), language="bash", line_numbers=False)
    st_space("v", 2)

    # --- Next steps ---
    st_write(bs.sub, "Step 4: Next steps", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        You now have a working StreamTeX project.
        Explore these topics to go further.
    """))
    st_space("v", 1)

    with st_list(list_type="ul"):
        st_write(s.large, "Add styles with the Style() constructor and + operator")
        st_write(s.large, "Use st_grid() for multi-column layouts")
        st_write(s.large, "Add images with st_image() and base64 encoding")
        st_write(s.large, "Use show_code() and show_explanation() helpers in blocks")
        st_write(s.large, "Enable dark mode with custom themes")
        st_write(s.large, "Deploy with Docker or Hugging Face Spaces")
    st_space("v", 2)

    show_details(textwrap.dedent("""\
        Hot-reload is your best friend during development.
        Save a file and Streamlit refreshes automatically.
        Use uv run pytest tests/ -v after library changes.
    """))
    st_space("v", 1)
