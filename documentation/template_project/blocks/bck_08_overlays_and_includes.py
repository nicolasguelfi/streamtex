import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_tip
import blocks
import textwrap


class BlockStyles:
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    overlay_text = s.Large + s.bold + s.text.colors.white
bs = BlockStyles


def build():
    st_write(bs.heading, "Overlays & Includes", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- st_include ---
    st_write(bs.sub, "st_include — Reuse Blocks", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # Include another block's content here:
        st_include(block_file_module=blocks.sub_block)
    """))
    st_space("v", 1)

    with st_block(s.project.containers.callout):
        st_include(block_file_module=blocks.sub_block)
    st_space("v", 2)

    # --- st_overlay ---
    st_write(bs.sub, "st_overlay — Absolute Positioning", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        with st_overlay() as o:
            st_image(uri="https://placehold.co/800x300/4A90D9/4A90D9",
                     width="800px", height="300px")
            with o.layer(top=120, left=250):
                st_write(bs.overlay_text, "Overlay Text")
    """))
    st_space("v", 1)

    with st_overlay() as o:
        st_image(uri="https://placehold.co/800x300/4A90D9/4A90D9",
                 width="800px", height="300px")
        with o.layer(top=120, left=250):
            st_write(bs.overlay_text, "Overlay Text")
    st_space("v", 2)

    show_tip(
        "st_include() lets you compose pages from reusable sub-blocks. "
        "st_overlay() places layers at absolute pixel positions over a base element."
    )
