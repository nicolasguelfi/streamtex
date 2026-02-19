import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_tip
import textwrap


class BlockStyles:
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    st_write(bs.heading, "Images", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Basic image ---
    st_write(bs.sub, "Basic Image", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        st_image(uri="https://placehold.co/600x200/4A90D9/white?text=StreamTeX",
                 width="600px", height="200px",
                 alt="Placeholder image")
    """))
    st_space("v", 1)

    st_image(uri="https://placehold.co/600x200/4A90D9/white?text=StreamTeX",
             width="600px", height="200px",
             alt="Placeholder image")
    st_space("v", 2)

    # --- Clickable image ---
    st_write(bs.sub, "Clickable Image with Hover", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        st_image(uri="https://placehold.co/400x150/2EC4B6/white?text=Click+me",
                 width="400px", height="150px",
                 alt="Clickable image",
                 link="https://github.com/",
                 hover=True)
    """))
    st_space("v", 1)

    st_image(uri="https://placehold.co/400x150/2EC4B6/white?text=Click+me",
             width="400px", height="150px",
             alt="Clickable image",
             link="https://github.com/",
             hover=True)
    st_space("v", 2)

    # --- Images in a grid ---
    st_write(bs.sub, "Images in a Grid", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        with st_grid(cols=3, cell_styles=s.center_txt) as g:
            with g.cell():
                st_image(uri="https://placehold.co/200/E74C3C/white?text=1",
                         width="200px", height="200px")
            with g.cell():
                st_image(uri="https://placehold.co/200/F39C12/white?text=2",
                         width="200px", height="200px")
            with g.cell():
                st_image(uri="https://placehold.co/200/27AE60/white?text=3",
                         width="200px", height="200px")
    """))
    st_space("v", 1)

    with st_grid(cols=3, cell_styles=s.center_txt) as g:
        with g.cell():
            st_image(uri="https://placehold.co/200/E74C3C/white?text=1",
                     width="200px", height="200px")
        with g.cell():
            st_image(uri="https://placehold.co/200/F39C12/white?text=2",
                     width="200px", height="200px")
        with g.cell():
            st_image(uri="https://placehold.co/200/27AE60/white?text=3",
                     width="200px", height="200px")
    st_space("v", 2)

    show_tip(
        "For local images, place files in static/images/ and reference them "
        "as static/images/filename.png. Ensure enableStaticServing = true in "
        ".streamlit/config.toml."
    )
