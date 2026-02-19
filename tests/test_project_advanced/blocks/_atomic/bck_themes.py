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
    """Theme demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Themes", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # How themes work
        st_write(bs.sub, "How themes work", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            A theme is a Python dictionary
            mapping style_ids to replacement CSS strings.
        """))
        st_space("v", 1)

        # Read actual themes.py
        try:
            themes_path = os.path.join(
                os.path.dirname(__file__), "..", "custom", "themes.py")
            with open(themes_path) as f:
                themes_source = f.read()
            show_code(themes_source)
        except Exception:
            show_code(textwrap.dedent("""\
                # custom/themes.py
                dark = {
                    "primary_blue": "color: #7AB8F5;",
                    "section_title": "color: #7AB8F5; font-weight: bold;",
                    "good_example_bg": "background-color: rgba(...);",
                }
            """))
        st_space("v", 2)

        # Activating a theme
        st_write(bs.sub, "Activating a theme in book.py", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Set the theme dict in book.py
            before rendering blocks.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            import streamtex.styles as sts
            from custom.themes import dark
            sts.theme = dark
        """))
        st_space("v", 2)

        # Override table
        st_write(bs.sub,
                 "This project's theme overrides",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The dark theme remaps specific style_ids
            for better contrast on dark backgrounds.
        """))
        st_space("v", 1)

        with st_grid(cols="1fr 1fr 1fr", cell_styles=bs.cell) as g:
            # header
            with g.cell(): st_write(s.bold + s.large, "style_id")
            with g.cell(): st_write(s.bold + s.large, "Original")
            with g.cell(): st_write(s.bold + s.large, "Dark Override")
            # row 1
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "primary_blue")
            with g.cell(): st_write(s.large, "#4A90D9")
            with g.cell(): st_write(s.large, "#7AB8F5 (lighter)")
            # row 2
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "section_title")
            with g.cell():
                st_write(s.large, "Full style (blue 80pt bold)")
            with g.cell():
                st_write(s.large, "Lighter blue for dark bg")
            # row 3
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "good_example_bg")
            with g.cell(): st_write(s.large, "15% opacity green")
            with g.cell():
                st_write(s.large, "25% opacity (brighter on dark)")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Override only what needs dark adaptation.
            Most styles work well in both modes
            if you avoid hardcoded black/white.
        """))
