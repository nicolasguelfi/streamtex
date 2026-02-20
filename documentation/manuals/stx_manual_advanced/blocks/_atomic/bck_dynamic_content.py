import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Dynamic & conditional content demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.center_txt
            + s.container.layouts.vertical_center_layout)
bs = BlockStyles

# Predefined style presets
STYLE_PRESETS = {
    "Bold Blue": s.bold + s.Large + s.project.colors.primary_blue,
    "Italic Teal": s.italic + s.Large + s.project.colors.accent_teal,
    "Warning Red": s.bold + s.Large + s.project.colors.warning_red,
    "Success Green": s.bold + s.Large + s.project.colors.success_green,
    "Amber Highlight": s.bold + s.Large + s.project.colors.highlight_amber,
}


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Dynamic & Conditional Content",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            Content changes dynamically based on user interaction.
            Python if/else controls what renders. Styles can be selected at runtime.
        """))
        st_space("v", 2)

        # --- Section 1: Style switcher ---
        st_write(bs.sub, "Style Switcher", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            presets = {"Bold Blue": s.bold + s.Large + s.project.colors.primary_blue, ...}
            choice = st.selectbox("Choose a style", list(presets.keys()))
            st_write(presets[choice], "Sample text with the selected style")
        """))
        st_space("v", 1)

        choice = st.selectbox("Choose a style preset",
                              [*STYLE_PRESETS],
                              key="bck30_style_select")
        with st_block(s.project.containers.result_box):
            st_write(STYLE_PRESETS[choice],
                     "Sample text with the selected style")
        st_space("v", 2)

        # --- Section 2: Conditional rendering ---
        st_write(bs.sub, "Conditional Rendering", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            show_a = st.checkbox("Show block A")
            show_b = st.checkbox("Show block B")
            if show_a:
                with st_block(s.project.containers.good_callout):
                    st_write(s.large, "Block A is visible (Python if)")
            if show_b:
                with st_block(s.project.containers.tip_callout):
                    st_write(s.large, "Block B is visible (Python if)")
        """))
        st_space("v", 1)

        col1, col2 = st.columns(2)
        show_a = col1.checkbox("Show block A", value=True,
                               key="bck30_show_a")
        show_b = col2.checkbox("Show block B", key="bck30_show_b")

        if show_a:
            with st_block(s.project.containers.good_callout):
                st_write(s.project.titles.tip_label,
                         "Block A")
                st_space("v", 1)
                st_write(s.large,
                         "Visible via Python conditional (if show_a).")
        if show_b:
            with st_block(s.project.containers.tip_callout):
                st_write(s.project.titles.tip_label,
                         "Block B")
                st_space("v", 1)
                st_write(s.large,
                         "Visible via Python conditional (if show_b).")
        if not show_a and not show_b:
            with st_block(s.project.containers.note_callout):
                st_write(s.large, "No blocks selected. Check a box above.")
        st_space("v", 2)

        # --- Section 3: Dynamic grid builder ---
        st_write(bs.sub, "Dynamic Grid Builder", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            cols = st.slider("Columns", 1, 5, 3)
            rows = st.slider("Rows", 1, 4, 2)
            with st_grid(cols=cols, cell_styles=bs.cell) as g:
                for i in range(cols * rows):
                    with g.cell():
                        st_write(s.large, f"Cell {i+1}")
        """))
        st_space("v", 1)

        c1, c2 = st.columns(2)
        grid_cols = c1.slider("Columns", 1, 5, 3, key="bck30_cols")
        grid_rows = c2.slider("Rows", 1, 4, 2, key="bck30_rows")

        with st_grid(cols=grid_cols, cell_styles=bs.cell) as g:
            for i in range(grid_cols * grid_rows):
                with g.cell():
                    st_write(s.large, f"Cell {i + 1}")
        st_space("v", 2)

        # --- Section 4: Progressive disclosure (wizard) ---
        st_write(bs.sub, "Progressive Disclosure (Wizard)", toc_lvl="+1")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            if "step" not in st.session_state:
                st.session_state.step = 1
            step = st.session_state.step
            # Show content for current step
            if step >= 1:
                with st_block(...): st_write("Step 1: ...")
            if step >= 2:
                with st_block(...): st_write("Step 2: ...")
            if st.button("Next") and step < 3:
                st.session_state.step += 1
        """))
        st_space("v", 1)

        if "bck30_step" not in st.session_state:
            st.session_state.bck30_step = 1
        step = st.session_state.bck30_step

        steps_data = [
            ("Step 1: Choose your project name",
             s.project.containers.tip_callout),
            ("Step 2: Configure your styles",
             s.project.containers.note_callout),
            ("Step 3: Build your blocks",
             s.project.containers.good_callout),
        ]

        for i, (label, callout) in enumerate(steps_data):
            if step > i:
                with st_block(callout):
                    st_write(s.large + s.bold, label)

        col_prev, col_next, col_reset = st.columns(3)
        if col_prev.button("Previous", key="bck30_prev",
                           disabled=(step <= 1)):
            st.session_state.bck30_step -= 1
            st.rerun()
        if col_next.button("Next", key="bck30_next",
                           disabled=(step >= 3)):
            st.session_state.bck30_step += 1
            st.rerun()
        if col_reset.button("Reset", key="bck30_reset"):
            st.session_state.bck30_step = 1
            st.rerun()
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Python if/else controls what gets rendered (true show/hide).
            Styles can be selected dynamically from a dict of presets.
            st_grid() can be rebuilt with slider-driven dimensions.
            The wizard pattern uses session_state to track progress.
        """))
