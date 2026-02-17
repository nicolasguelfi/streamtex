import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Spacing demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    marker = (s.container.bg_colors.coral_bg
              + s.container.paddings.small_padding
              + s.center_txt)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Spacing: st_space & st_br",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Vertical space
        st_write(bs.sub,
                 "Vertical space: st_space(\"v\", size)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Insert vertical gaps between elements
            with st_space("v", size).
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_space("v", 2)       # 2em vertical gap
            st_space("v", "50px")  # 50px vertical gap
        """))
        st_space("v", 1)

        with st_block(bs.marker):
            st_write(s.large, "Block A")
        st_space("v", 2)
        with st_block(bs.marker):
            st_write(s.large, "Block B (2em below A)")
        st_space("v", 1)

        with st_block(bs.marker):
            st_write(s.large, "Block C")
        st_space("v", "50px")
        with st_block(bs.marker):
            st_write(s.large, "Block D (50px below C)")
        st_space("v", 2)

        # Horizontal space
        st_write(bs.sub,
                 "Horizontal space: st_space(\"h\", size)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Insert horizontal gaps inside st_span containers.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_span():
                st_write(s.large, "Left")
                st_space("h", 3)
                st_write(s.large, "Right (3em gap)")
        """))
        st_space("v", 1)

        with st_span():
            with st_block(bs.marker):
                st_write(s.large, "Left")
            st_space("h", 3)
            with st_block(bs.marker):
                st_write(s.large, "Right (3em gap)")
        st_space("v", 2)

        # st_br
        st_write(bs.sub, "Line break: st_br()", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Insert a minimal vertical break (0 height space) with st_br().
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.large, "Line above")
            st_br()
            st_write(s.large, "Line below (minimal break)")
        """))
        st_space("v", 1)

        st_write(s.large, "Line above")
        st_br()
        st_write(s.large, "Line below (minimal break)")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Default: st_space(direction="v", size="1em").
            Size accepts int/float (em units) or string ("50px").
            Use st_space between blocks for layout.
            Use st_br for minimal breaks within content (calls st_space("v", 0)).
        """))
