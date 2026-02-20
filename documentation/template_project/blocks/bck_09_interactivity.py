import streamlit as st
from streamtex import *
import streamtex as stx
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
    st_write(bs.heading, "Interactivity", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    show_tip(
        "Widgets are st.* (interactivity). Their return values drive "
        "what stx.* renders. Styles can be built dynamically at runtime."
    )
    st_space("v", 2)

    # --- Button & Toggle ---
    st_write(bs.sub, "Button & Toggle", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        if st.button("Say hello"):
            st_write(s.large + s.bold, "Hello from StreamTeX!")

        show = st.toggle("Show styled block")
        if show:
            with st_block(s.project.containers.callout):
                st_write(s.large, "This block appears when toggled on.")
    """))
    st_space("v", 1)

    if st.button("Say hello", key="tpl_hello"):
        with st_block(s.project.containers.callout):
            st_write(s.large + s.bold + s.project.colors.accent,
                     "Hello from StreamTeX!")

    show = st.toggle("Show styled block", key="tpl_toggle")
    if show:
        with st_block(s.project.containers.callout):
            st_write(s.large, "This block appears when toggled on.")
    st_space("v", 2)

    # --- Slider-driven style ---
    st_write(bs.sub, "Slider-Driven Style", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        size = st.slider("Font size (px)", 12, 96, 32)
        dynamic_style = ns(f"font-size: {size}px;")
        st_write(dynamic_style + s.bold, "Dynamic size text")
    """))
    st_space("v", 1)

    size = st.slider("Font size (px)", 12, 96, 32, key="tpl_slider")
    dynamic_style = ns(f"font-size: {size}px;")
    with st_block(s.project.containers.callout):
        st_write(dynamic_style + s.bold, "Dynamic size text")
    st_space("v", 2)

    # --- Color picker ---
    st_write(bs.sub, "Color Picker", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        picked = st.color_picker("Pick a text color", "#E74C3C")
        color_style = ns(f"color: {picked};")
        st_write(color_style + s.Large + s.bold, "Colored text!")
    """))
    st_space("v", 1)

    picked = st.color_picker("Pick a text color", "#E74C3C", key="tpl_color")
    color_style = ns(f"color: {picked};")
    with st_block(s.project.containers.callout):
        st_write(color_style + s.Large + s.bold, "Colored text!")
    st_space("v", 2)

    show_tip(
        "Always use st.* for interactivity and stx.* for content rendering. "
        "Style() objects can be built dynamically with f-strings: "
        "ns(f\"font-size: {val}px;\")."
    )
