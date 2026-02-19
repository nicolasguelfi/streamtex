import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Tabs, expanders & popovers demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.center_txt)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Tabs, Expanders & Popovers",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            Streamlit containers (tabs, expanders, popovers) are context
            managers — just like st_block(). StreamTeX content works
            normally inside them.
        """))
        st_space("v", 2)

        # --- Section 1: Tabs ---
        st_write(bs.sub, "st.tabs", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            tab1, tab2, tab3 = st.tabs(["Text", "Grid", "List"])
            with tab1:
                st_write(s.large, "Rich StreamTeX text inside a tab.")
            with tab2:
                with st_grid(cols=2, cell_styles=bs.cell) as g:
                    with g.cell(): st_write(s.large, "A1")
                    with g.cell(): st_write(s.large, "B1")
            with tab3:
                with st_list(list_type=lt.unordered, li_style=s.large) as l:
                    with l.item(): st_write("Item one")
        """))
        st_space("v", 1)

        tab1, tab2, tab3 = st.tabs(["Text", "Grid", "List"])
        with tab1:
            with st_block(s.project.containers.tip_callout):
                st_write(s.project.titles.tip_label, "Tip")
                st_space("v", 1)
                st_write(s.large, "Rich StreamTeX content inside a tab. "
                         "All sx.* functions work here.")
        with tab2:
            with st_grid(cols=2, cell_styles=bs.cell) as g:
                with g.cell():
                    st_write(s.large + s.bold, "Column A")
                with g.cell():
                    st_write(s.large + s.bold, "Column B")
                with g.cell():
                    st_write(s.large, "Data A1")
                with g.cell():
                    st_write(s.large, "Data B1")
        with tab3:
            with st_list(list_type=lt.unordered, li_style=s.large) as l:
                with l.item():
                    st_write("First item in a tab")
                with l.item():
                    st_write("Second item in a tab")
                with l.item():
                    st_write("Third item in a tab")
        st_space("v", 2)

        # --- Section 2: Expanders ---
        st_write(bs.sub, "st.expander", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st.expander("Click to expand"):
                with st_block(s.project.containers.result_box):
                    st_write(s.large, "Hidden content revealed!")
                    with st_list(li_style=s.large) as l:
                        with l.item(): st_write("Detail A")
                        with l.item(): st_write("Detail B")
        """))
        st_space("v", 1)

        with st.expander("Architecture Overview"):
            with st_block(s.project.containers.good_callout):
                st_write(s.project.titles.tip_label, "StreamTeX Architecture")
                st_space("v", 1)
                with st_list(list_type=lt.ordered, li_style=s.large) as l:
                    with l.item():
                        st_write("book.py orchestrates the app")
                    with l.item():
                        st_write("blocks/ contain the content modules")
                    with l.item():
                        st_write("custom/ holds project styles")

        with st.expander("Style Examples"):
            with st_block(s.project.containers.note_callout):
                st_write(s.project.titles.details_label, "Composition")
                st_space("v", 1)
                st_write(s.large,
                         "Styles compose with + operator: s.bold + s.Large")
                st_br()
                st_write(s.large,
                         "Remove with - operator: style - s.bold")
        st_space("v", 2)

        # --- Section 3: Popovers ---
        st_write(bs.sub, "st.popover", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st.popover("Show info card"):
                with st_block(s.project.containers.result_box):
                    st_write(s.large + s.bold, "Info Card")
                    st_write(s.large, "A mini styled card in a popover.")
        """))
        st_space("v", 1)

        with st.popover("Show info card"):
            with st_block(s.project.containers.result_box):
                st_write(s.large + s.bold + s.project.colors.primary_blue,
                         "StreamTeX Info")
                st_space("v", 1)
                st_write(s.large, "Version: 0.2.0")
                st_br()
                st_write(s.large, "Python >= 3.10")
                st_br()
                st_write(s.large, "Streamlit >= 1.54.0")
        st_space("v", 2)

        # --- Section 4: Nesting ---
        st_write(bs.sub, "Deep Nesting", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Streamlit containers can nest: tabs > expander > st_grid.
        """))
        st_space("v", 1)

        tab_a, tab_b = st.tabs(["Tab A", "Tab B"])
        with tab_a:
            with st.expander("Expand for grid"):
                with st_grid(cols=2, cell_styles=bs.cell) as g:
                    with g.cell():
                        st_write(s.large + s.bold + s.project.colors.accent_teal,
                                 "Nested A1")
                    with g.cell():
                        st_write(s.large + s.bold + s.project.colors.highlight_amber,
                                 "Nested B1")
                    with g.cell():
                        st_write(s.large, "Cell A2")
                    with g.cell():
                        st_write(s.large, "Cell B2")
        with tab_b:
            with st.expander("Expand for list"):
                with st_block(s.project.containers.tip_callout):
                    with st_list(list_type=lt.unordered,
                                 li_style=s.large) as l:
                        with l.item():
                            st_write("Deeply nested item 1")
                        with l.item():
                            st_write("Deeply nested item 2")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            st.tabs, st.expander, st.popover are context managers like st_block().
            All sx.* functions work inside Streamlit containers.
            Nesting is supported: tabs > expander > grid/list.
        """))
