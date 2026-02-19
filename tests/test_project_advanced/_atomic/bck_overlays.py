import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Overlay demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    overlay_text = s.text.colors.white + s.bold + s.Large
    overlay_bg = ns("background-color: rgba(0, 0, 0, 0.5); padding: 8pt;")
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Overlays", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Basic overlay
        st_write(bs.sub,
                 "st_overlay with positioned layers",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Place content on top of a base element
            with absolute positioning.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_overlay(s.container.sizes.width_full) as o:
                with st_block(s.container.bg_colors.dark_slate_blue_bg
                              + ns("height: 200px; width: 100%;")):
                    st_write(s.text.colors.white + s.large,
                             "Base content area")
                with o.layer(top=20, left=20):
                    with st_block(bs.overlay_bg):
                        st_write(bs.overlay_text, "Top-Left")
                with o.layer(bottom=20, right=20):
                    with st_block(bs.overlay_bg):
                        st_write(bs.overlay_text, "Bottom-Right")
        """))
        st_space("v", 1)

        with st_overlay(s.container.sizes.width_full) as o:
            with st_block(s.container.bg_colors.dark_slate_blue_bg
                          + ns("height: 200px; width: 100%;")):
                st_write(s.text.colors.white + s.large,
                         "Base content area (dark background)")
            with o.layer(top=20, left=20):
                with st_block(bs.overlay_bg):
                    st_write(bs.overlay_text, "Top-Left")
            with o.layer(bottom=20, right=20):
                with st_block(bs.overlay_bg):
                    st_write(bs.overlay_text, "Bottom-Right")
        st_space("v", 2)

        # Positioning parameters
        st_write(bs.sub,
                 "Layer positioning: top, left, right, bottom",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Each o.layer() accepts top, left, right, bottom
            positioning parameters.
        """))
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Integer values are treated as pixels.
            String values are used as-is (e.g., "50%").
            The base content determines the overlay container size.
        """))
