import streamlit as st
import os
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Architecture demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Project Architecture",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Folder tree
        st_write(bs.sub, "Project folder structure", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            A StreamTeX project follows
            this standard folder layout.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            project/
            +-- book.py              # Entry point
            +-- setup.py             # Adds streamtex to sys.path
            +-- custom/
            |   +-- styles.py        # Project-specific styles
            |   +-- themes.py        # Theme overrides
            +-- blocks/
                +-- __init__.py      # Auto-discovers bck_*.py files
                +-- bck_00_welcome.py
                +-- bck_01_architecture.py
                +-- ...
        """), language="text", line_numbers=False)
        st_space("v", 2)

        # st_book
        st_write(bs.sub, "st_book: the orchestrator", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_book() takes a list of block modules
            and renders them sequentially.
        """))
        st_space("v", 1)

        # Read actual book.py
        try:
            book_path = os.path.join(
                os.path.dirname(__file__), "..", "book.py")
            with open(book_path) as f:
                book_source = f.read()
            show_code(book_source)
        except Exception:
            show_code(textwrap.dedent("""\
                st_book([blocks.bck_01, blocks.bck_02, ...],
                        toc_config=toc)
            """))
        st_space("v", 2)

        # st_include
        st_write(bs.sub, "st_include: embedding sub-blocks", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_include() calls a block module's build() function
            to embed it inline.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            from blocks import bck_welcome
            st_include(bck_welcome)
        """))
        st_space("v", 1)

        # Live sub-include
        with st_block(s.container.borders.dashed_border
                      + s.container.paddings.medium_padding):
            st_write(s.project.colors.accent_teal + s.bold + s.large,
                     "Sub-block included via st_include:")
            st_space("v", 1)
        #             from blocks import bck_welcome
        #             st_include(bck_welcome)
        st_space("v", 2)

        # Block file structure
        st_write(bs.sub, "Block file structure", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Every block file must have BlockStyles,
            bs alias, and build() function.
        """))
        st_space("v", 1)

        with st_grid(cols=2, cell_styles=bs.cell) as g:
            # header
            with g.cell(): st_write(s.bold + s.large, "Element")
            with g.cell(): st_write(s.bold + s.large, "Purpose")
            # row 1
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "class BlockStyles:")
            with g.cell():
                st_write(s.large,
                         "Local style compositions for this block")
            # row 2
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "bs = BlockStyles")
            with g.cell():
                st_write(s.large, "Short alias for cleaner code")
            # row 3
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "def build():")
            with g.cell():
                st_write(s.large,
                         "Required entry point that renders block content")
        st_space("v", 2)

        # blocks/__init__.py
        st_write(bs.sub,
                 "Dynamic imports: blocks/__init__.py",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Auto-discovers all bck_*.py files
            so adding a block is just creating a file.
        """))
        st_space("v", 1)

        # Read actual __init__.py
        try:
            init_path = os.path.join(
                os.path.dirname(__file__), "__init__.py")
            with open(init_path) as f:
                init_source = f.read()
            show_code(init_source)
        except Exception:
            show_code(textwrap.dedent("""\
                # blocks/__init__.py uses glob + importlib
                # to auto-discover all bck_*.py files
            """))
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            One concept per block.
            Use st_include for composition
            when blocks share sub-components.
        """))
