import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """DataFrames & tables demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
    header_cell = (s.bold + s.large
                   + s.project.colors.primary_blue
                   + s.container.paddings.small_padding
                   + s.container.borders.solid_border)
    data_cell = (s.large
                 + s.container.paddings.small_padding
                 + s.container.borders.solid_border)
bs = BlockStyles

# Sample data shared across sections
SAMPLE_DATA = {
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Role": ["Engineer", "Designer", "Manager", "Analyst"],
    "Score": [92, 87, 95, 88],
}

SAMPLE_JSON = {
    "project": "StreamTeX",
    "version": "0.2.0",
    "features": ["styles", "grids", "lists", "export"],
}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "DataFrames & Structured Data",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            st.dataframe() = interactive table (sort, filter).

            st_grid() = static table with full visual control.

            Choose based on your needs.
        """))
        st_space("v", 2)

        # --- Section 1: st.dataframe ---
        st_write(bs.sub, "st.dataframe (interactive)", toc_lvl="+1")
        st_space("v", 1)

        show_code("""\
data = {
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Role": ["Engineer", "Designer", "Manager", "Analyst"],
    "Score": [92, 87, 95, 88],
}
stx.st_dataframe(data, use_container_width=True)""")
        st_space("v", 1)

        stx.st_dataframe(SAMPLE_DATA, use_container_width=True)
        st_space("v", 2)

        # --- Section 2: st.table ---
        st_write(bs.sub, "st.table (static)", toc_lvl="+1")
        st_space("v", 1)

        show_code("""\
data = {
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Role": ["Engineer", "Designer", "Manager", "Analyst"],
    "Score": [92, 87, 95, 88],
}
stx.st_table(data)""")
        st_space("v", 1)

        stx.st_table(SAMPLE_DATA)
        st_space("v", 2)

        # --- Section 3: st.json ---
        st_write(bs.sub, "st.json (JSON viewer)", toc_lvl="+1")
        st_space("v", 1)

        show_code("""\
data = {
    "project": "StreamTeX",
    "version": "0.2.0",
    "features": ["styles", "grids", "lists", "export"],
}
stx.st_json(data)""")
        st_space("v", 1)

        stx.st_json(SAMPLE_JSON)
        st_space("v", 2)

        # --- Section 4: StreamTeX styled grid ---
        st_write(bs.sub, "StreamTeX Styled Grid", toc_lvl="+1")
        st_space("v", 1)

        show_code("""\
header_style = sg.create("A1:C1", bs.header_cell)
data_style = sg.create("A2:C5", bs.data_cell)
with st_grid(cols=3, cell_styles=header_style + data_style) as g:
    for col in ["Name", "Role", "Score"]:
        with g.cell(): st_write(col)
    for i in range(len(data["Name"])):
        for col in ["Name", "Role", "Score"]:
            with g.cell(): st_write(str(data[col][i]))""")
        st_space("v", 1)

        header_style = sg.create("A1:C1", bs.header_cell)
        data_style = sg.create("A2:C5", bs.data_cell)
        with st_grid(cols=3, cell_styles=header_style + data_style) as g:
            for col in ["Name", "Role", "Score"]:
                with g.cell():
                    st_write(col)
            for i in range(len(SAMPLE_DATA["Name"])):
                for col in ["Name", "Role", "Score"]:
                    with g.cell():
                        st_write(str(SAMPLE_DATA[col][i]))
        st_space("v", 2)

        # --- Section 5: Side-by-side comparison ---
        st_write(bs.sub, "Side-by-Side Comparison", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st.dataframe (left) vs st_grid (right) — same data, different rendering.
        """))
        st_space("v", 1)

        cmp_cell = (s.container.borders.solid_border
                    + s.container.paddings.small_padding)
        with st_grid(cols=2, cell_styles=cmp_cell) as g:
            with g.cell():
                st_write(s.large + s.bold + s.project.colors.primary_blue,
                         "st.dataframe")
                stx.st_dataframe(SAMPLE_DATA, use_container_width=True)
            with g.cell():
                st_write(s.large + s.bold + s.project.colors.accent_teal,
                         "st_grid")
                with st_grid(cols=3,
                             cell_styles=header_style + data_style) as g2:
                    for col in ["Name", "Role", "Score"]:
                        with g2.cell():
                            st_write(col)
                    for i in range(len(SAMPLE_DATA["Name"])):
                        for col in ["Name", "Role", "Score"]:
                            with g2.cell():
                                st_write(str(SAMPLE_DATA[col][i]))
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            st.dataframe() supports interactive sorting and filtering.

            st_grid() provides full visual control (colors, borders, fonts).

            Use st.dataframe for exploration, st_grid for presentation.
        """))
