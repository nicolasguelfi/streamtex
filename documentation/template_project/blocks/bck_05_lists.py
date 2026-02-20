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
    item_accent = s.project.colors.accent + s.bold
bs = BlockStyles


def build():
    st_write(bs.heading, "Lists", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # --- Unordered ---
    st_write(bs.sub, "Unordered List", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        with st_list(list_type=lt.unordered, li_style=s.large) as l:
            with l.item(): st_write("First item")
            with l.item(): st_write("Second item")
            with l.item(): st_write("Third item")
    """))
    st_space("v", 1)

    with st_list(list_type=lt.unordered, li_style=s.large) as l:
        with l.item(): st_write("First item")
        with l.item(): st_write("Second item")
        with l.item(): st_write("Third item")
    st_space("v", 2)

    # --- Ordered ---
    st_write(bs.sub, "Ordered List", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        with st_list(list_type=lt.ordered, li_style=s.large) as l:
            with l.item(): st_write("Step one")
            with l.item(): st_write("Step two")
            with l.item(): st_write("Step three")
    """))
    st_space("v", 1)

    with st_list(list_type=lt.ordered, li_style=s.large) as l:
        with l.item(): st_write("Step one")
        with l.item(): st_write("Step two")
        with l.item(): st_write("Step three")
    st_space("v", 2)

    # --- Nested with custom styles ---
    st_write(bs.sub, "Nested List with Styles", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        with st_list(list_type=lt.unordered, li_style=bs.item_accent) as l:
            with l.item(): st_write("Parent A")
            with l.item():
                st_write("Parent B")
                with st_list(li_style=s.large) as l2:
                    with l2.item(): st_write("Child B.1")
                    with l2.item(): st_write("Child B.2")
            with l.item(): st_write("Parent C")
    """))
    st_space("v", 1)

    with st_list(list_type=lt.unordered, li_style=bs.item_accent) as l:
        with l.item(): st_write("Parent A")
        with l.item():
            st_write("Parent B")
            with st_list(li_style=s.large) as l2:
                with l2.item(): st_write("Child B.1")
                with l2.item(): st_write("Child B.2")
        with l.item(): st_write("Parent C")
    st_space("v", 2)

    show_tip(
        "Nest st_list() context managers for multi-level lists. "
        "l_style controls the container, li_style controls each item."
    )
