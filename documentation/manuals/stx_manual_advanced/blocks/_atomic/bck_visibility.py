import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Visibility demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    demo_box = (s.container.borders.solid_border
                + s.container.paddings.small_padding
                + s.center_txt + s.large)
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.center_txt
            + s.container.layouts.vertical_center_layout)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Visibility", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Overview table
        st_write(bs.sub, "Three visibility modes", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control element visibility with three modes:
            hidden, visible, invisible.
        """))
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=bs.cell) as g:
            # header
            with g.cell(): st_write(s.bold + s.large, "Mode")
            with g.cell(): st_write(s.bold + s.large, "CSS")
            with g.cell(): st_write(s.bold + s.large, "Behavior")
            # row 1
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large, "hidden")
            with g.cell():
                st_write(s.large, "display: none")
            with g.cell():
                st_write(s.large, "Removed from layout (no space)")
            # row 2
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large, "visible")
            with g.cell():
                st_write(s.large, "visibility: visible")
            with g.cell():
                st_write(s.large, "Normal rendering")
            # row 3
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large, "invisible")
            with g.cell():
                st_write(s.large, "visibility: hidden")
            with g.cell():
                st_write(s.large, "Space preserved, content invisible")
        st_space("v", 2)

        # Live demo
        st_write(bs.sub, "Live demonstration", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Three boxes below —
            the middle one changes visibility mode.
        """))
        st_space("v", 1)

        show_code(file="examples/visibility/visibility_modes.py")
        st_space("v", 1)

        # Visible
        st_write(s.bold + s.large + s.project.colors.success_green,
                 "s.visibility.visible:")
        st_space("v", 1)
        with st_span():
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_blue_bg):
                st_write("Box A")
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_green_bg
                          + s.visibility.visible):
                st_write("Box B (visible)")
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_coral_bg):
                st_write("Box C")
        st_space("v", 2)

        # Invisible (space preserved)
        st_write(s.bold + s.large + s.project.colors.highlight_amber,
                 "s.visibility.invisible:")
        st_space("v", 1)
        with st_span():
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_blue_bg):
                st_write("Box A")
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_green_bg
                          + s.visibility.invisible):
                st_write("Box B (invisible)")
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_coral_bg):
                st_write("Box C")
        st_space("v", 2)

        # Hidden (removed from layout)
        st_write(s.bold + s.large + s.project.colors.warning_red,
                 "s.visibility.hidden:")
        st_space("v", 1)
        with st_span():
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_blue_bg):
                st_write("Box A")
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_green_bg
                          + s.visibility.hidden):
                st_write("Box B (hidden)")
            with st_block(bs.demo_box
                          + s.container.bg_colors.light_coral_bg):
                st_write("Box C")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Use hidden to completely remove an element.

            Use invisible to preserve layout spacing
            while hiding content.
        """))
