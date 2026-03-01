"""Quick Start — Create a Project."""

import textwrap
from streamtex import *
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details


class BlockStyles:
    """Quick Start new project styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle


bs = BlockStyles


def build():
    """Quick Start Step 2: Create a new project from the template."""
    st_space("v", 1)
    st_write(bs.heading, "Quick Start — Create a Project",
             tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Copy the template ---
    st_write(bs.sub, "Step 1: Copy the template", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        StreamTeX provides a ready-to-use template.
        Copy it to the projects/ folder and rename it.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        cp -r documentation/template_project/ projects/my_project/
    """), language="bash", line_numbers=False)
    st_space("v", 2)

    # --- Project structure ---
    st_write(bs.sub, "Step 2: Project structure", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        The template gives you a standard folder layout.

        Each folder has a specific role.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        projects/my_project/
        +-- book.py              # Entry point (orchestrates blocks)
        +-- setup.py             # Adds streamtex to sys.path
        +-- custom/
        |   +-- styles.py        # Project-specific style definitions
        |   +-- themes.py        # Theme overrides (dark/light)
        +-- blocks/
        |   +-- __init__.py      # Block auto-discovery (ProjectBlockRegistry)
        |   +-- helpers.py       # Project-specific helper config
        |   +-- bck_welcome.py   # Your first block
        +-- static/              # Images, fonts, assets
        +-- .streamlit/
            +-- config.toml      # Static serving configuration
    """), language="text", line_numbers=False)
    st_space("v", 2)

    # --- Configure styles ---
    st_write(bs.sub, "Step 3: Configure styles", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        Edit custom/styles.py to define your project colors,
        font sizes, and layout styles. Use Style composition
        with the + operator to combine styles.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # custom/styles.py
        from streamtex.styles import Style
        import streamtex as stx

        _sts = stx.StxStyles

        class ProjectStyles:
            class titles:
                main = Style(
                    "color: #4A90D9; font-weight: bold; font-size: 80pt;",
                    "main_title"
                )

        class Styles(_sts.__class__):
            project = ProjectStyles
    """))
    st_space("v", 2)

    # --- Configure book.py ---
    st_write(bs.sub, "Step 4: Configure book.py", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        book.py is the entry point. It imports blocks,
        configures navigation, and calls st_book()
        to render everything.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # book.py
        import streamlit as st
        import setup
        from streamtex import st_book, TOCConfig, BannerConfig
        import blocks

        st.set_page_config(page_title="My Project", layout="wide")

        toc = TOCConfig(numerate_titles=False, toc_position=0, sidebar_max_level=2)

        st_book([
            blocks.bck_welcome,
        ], toc_config=toc, paginate=True,
           banner=BannerConfig.full())
    """))
    st_space("v", 2)

    # --- Static serving ---
    st_write(bs.sub, "Step 5: Enable static serving", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        Streamlit needs static serving enabled
        for images and assets.

        Create or edit
        .streamlit/config.toml in your project.
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # .streamlit/config.toml
        [server]
        enableStaticServing = true
    """), language="toml", line_numbers=False)
    st_space("v", 2)

    show_details(textwrap.dedent("""\
        Mandatory files: book.py, setup.py, custom/styles.py, blocks/__init__.py.

        The setup.py adds the streamtex library to sys.path
        so imports work correctly from any location.
    """))
    st_space("v", 1)
