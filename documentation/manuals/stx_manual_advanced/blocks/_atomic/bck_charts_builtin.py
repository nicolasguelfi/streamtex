import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import random


class BlockStyles:
    """Built-in charts demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding)
bs = BlockStyles


def _make_line_data(n=20):
    """Generate synthetic line chart data as a dict."""
    random.seed(42)
    series_a = [random.gauss(50, 10) for _ in range(n)]
    series_b = [random.gauss(60, 15) for _ in range(n)]
    return {"Series A": series_a, "Series B": series_b}


def _make_bar_data():
    """Generate categorical bar chart data."""
    return {"Category": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
            "Value": [23, 45, 12, 67, 34]}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Built-in Charts", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            Streamlit bundles Vega-Lite for charts. Charts are st.* widgets.
            Wrap them in st_block() for styling. Use st_grid() for side-by-side layout.
        """))
        st_space("v", 2)

        # --- Section 1: Line chart ---
        st_write(bs.sub, "Line Chart", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            data = {"Series A": [...], "Series B": [...]}
            with st_block(s.project.containers.result_box):
                st.line_chart(data)
        """))
        st_space("v", 1)

        with st_block(s.project.containers.result_box):
            stx.st_line_chart(_make_line_data())
        st_space("v", 2)

        # --- Section 2: Bar chart ---
        st_write(bs.sub, "Bar Chart", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            data = {"Category": [...], "Value": [...]}
            st.bar_chart(data, x="Category", y="Value")
        """))
        st_space("v", 1)

        bar_data = _make_bar_data()
        with st_block(s.project.containers.result_box):
            stx.st_bar_chart(bar_data, x="Category", y="Value")
        st_space("v", 2)

        # --- Section 3: Area chart with slider ---
        st_write(bs.sub, "Interactive Area Chart", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            n_points = st.slider("Number of points", 5, 100, 30)
            st.area_chart(_make_line_data(n_points))
        """))
        st_space("v", 1)

        n_points = st.slider("Number of data points", 5, 100, 30,
                             key="bck27_area_slider")
        with st_block(s.project.containers.result_box):
            stx.st_area_chart(_make_line_data(n_points))
        st_space("v", 2)

        # --- Section 4: Scatter chart ---
        st_write(bs.sub, "Scatter Chart", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            random.seed(0)
            scatter_data = {"x": [...], "y": [...], "size": [...]}
            st.scatter_chart(scatter_data, x="x", y="y", size="size")
        """))
        st_space("v", 1)

        random.seed(0)
        scatter_data = {
            "x": [random.gauss(0, 1) for _ in range(50)],
            "y": [random.gauss(0, 1) for _ in range(50)],
            "size": [random.uniform(10, 60) for _ in range(50)],
        }
        with st_block(s.project.containers.result_box):
            stx.st_scatter_chart(scatter_data, x="x", y="y", size="size")
        st_space("v", 2)

        # --- Section 5: Metrics + chart in grid ---
        st_write(bs.sub, "Metrics & Chart in Grid", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_grid(cols="1fr 2fr", cell_styles=bs.cell) as g:
                with g.cell():
                    st.metric("Users", "1,234", "+12%")
                    st.metric("Revenue", "$5.6K", "+8%")
                with g.cell():
                    st.line_chart(data)
        """))
        st_space("v", 1)

        with st_grid(cols="1fr 2fr", cell_styles=bs.cell) as g:
            with g.cell():
                stx.st_metric("Users", "1,234", "+12%")
                stx.st_metric("Revenue", "$5.6K", "+8%")
                stx.st_metric("Uptime", "99.9%", "+0.1%")
            with g.cell():
                stx.st_line_chart(_make_line_data())
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Charts are st.* widgets — correct per the sx/st split.
            Wrap charts in st_block() for borders and backgrounds.
            Use st_grid() to place charts alongside metrics or text.
            Data can be dicts, lists, or pandas DataFrames.
        """))
