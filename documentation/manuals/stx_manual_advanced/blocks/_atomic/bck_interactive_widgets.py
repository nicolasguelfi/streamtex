import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Interactive widgets demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Interactive Widgets", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            Widgets are st.* (interactivity). Their return values drive
            what stx.* renders. Styles can be built dynamically at runtime.
        """))
        st_space("v", 2)

        # --- Section 1: Buttons & toggles ---
        st_write(bs.sub, "Buttons & Toggles", toc_lvl="+1")
        st_space("v", 1)

        show_code("""\
if st.button("Say hello", key="bck25_hello"):
    with st_block(s.project.containers.result_box):
        st_write(s.large + s.bold + s.project.colors.success_green,
                 "Hello from StreamTeX!")
show = st.toggle("Show styled block", key="bck25_toggle")
if show:
    with st_block(s.project.containers.tip_callout):
        st_write(s.large, "This block appears when toggled on.")""")
        st_space("v", 1)

        if st.button("Say hello", key="bck25_hello"):
            with st_block(s.project.containers.result_box):
                st_write(s.large + s.bold + s.project.colors.success_green,
                         "Hello from StreamTeX!")
        show = st.toggle("Show styled block", key="bck25_toggle")
        if show:
            with st_block(s.project.containers.tip_callout):
                st_write(s.large, "This block appears when toggled on.")
        st_space("v", 2)

        # --- Section 2: Radio & selectbox ---
        st_write(bs.sub, "Radio & Selectbox", toc_lvl="+1")
        st_space("v", 1)

        show_code(file="examples/widget/radio_selectbox.py")
        st_space("v", 1)

        choice = st.radio("Pick a callout style",
                          ["Good", "Bad", "Tip", "Note"],
                          key="bck25_radio", horizontal=True)
        callout_map = {
            "Good": s.project.containers.good_callout,
            "Bad": s.project.containers.bad_callout,
            "Tip": s.project.containers.tip_callout,
            "Note": s.project.containers.note_callout,
        }
        with st_block(callout_map[choice]):
            st_write(s.large, f"This is a {choice} callout.")
        st_space("v", 2)

        # --- Section 3: Slider-driven styles ---
        st_write(bs.sub, "Slider-Driven Styles", toc_lvl="+1")
        st_space("v", 1)

        show_code("""\
size = st.slider("Font size (px)", 12, 96, 32, key="bck25_slider")
dynamic_style = ns(f"font-size: {size}px;")
with st_block(s.project.containers.result_box):
    st_write(dynamic_style + s.bold, "Dynamic size text")""")
        st_space("v", 1)

        size = st.slider("Font size (px)", 12, 96, 32, key="bck25_slider")
        dynamic_style = ns(f"font-size: {size}px;")
        with st_block(s.project.containers.result_box):
            st_write(dynamic_style + s.bold, "Dynamic size text")
        st_space("v", 2)

        # --- Section 4: Text input live ---
        st_write(bs.sub, "Text Input Live Preview", toc_lvl="+1")
        st_space("v", 1)

        show_code(file="examples/widget/text_input_preview.py")
        st_space("v", 1)

        user_text = st.text_input("Type something", key="bck25_text",
                                  value="Hello StreamTeX")
        if user_text:
            with st_block(s.project.containers.result_box):
                st_write(s.large + s.italic, user_text)
                st_br()
                st_write(s.large + s.bold + s.project.colors.primary_blue,
                         user_text)
                st_br()
                st_write(s.large + s.text.decors.underline_text
                         + s.project.colors.accent_teal, user_text)
        st_space("v", 2)

        # --- Section 5: Color picker ---
        st_write(bs.sub, "Color Picker", toc_lvl="+1")
        st_space("v", 1)

        show_code("""\
picked = st.color_picker("Pick a text color", "#E74C3C",
                         key="bck25_color")
color_style = ns(f"color: {picked};")
with st_block(s.project.containers.result_box):
    st_write(color_style + s.Large + s.bold, "Colored text!")""")
        st_space("v", 1)

        picked = st.color_picker("Pick a text color", "#E74C3C",
                                 key="bck25_color")
        color_style = ns(f"color: {picked};")
        with st_block(s.project.containers.result_box):
            st_write(color_style + s.Large + s.bold, "Colored text!")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Widgets return values that drive what stx.* displays.

            Style() objects can be constructed dynamically at runtime
            using f-strings: ns(f"font-size: {val}px;").

            Always use st.* for interactivity, stx.* for content.
        """))
