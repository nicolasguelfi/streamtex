import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Text styles catalog."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    label = s.bold + s.large
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.center_txt
            + s.container.layouts.vertical_center_layout)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Text Styles Catalog",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Colors
        st_write(bs.sub, "Text Colors (s.text.colors.*)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            StreamTeX includes all named CSS colors as predefined styles.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.text.colors.red + s.large, "red")
            st_write(s.text.colors.dodger_blue + s.large, "dodger_blue")
        """))
        st_space("v", 1)

        with st_grid(cols=4, cell_styles=bs.cell) as g:
            with g.cell(): st_write(s.text.colors.red + s.large, "red")
            with g.cell(): st_write(s.text.colors.blue + s.large, "blue")
            with g.cell(): st_write(s.text.colors.green + s.large, "green")
            with g.cell(): st_write(s.text.colors.orange + s.large, "orange")
            with g.cell(): st_write(s.text.colors.coral + s.large, "coral")
            with g.cell(): st_write(s.text.colors.dodger_blue + s.large, "dodger_blue")
            with g.cell(): st_write(s.text.colors.crimson + s.large, "crimson")
            with g.cell(): st_write(s.text.colors.teal + s.large, "teal")
            with g.cell(): st_write(s.text.colors.gold + s.large, "gold")
            with g.cell(): st_write(s.text.colors.lime + s.large, "lime")
            with g.cell(): st_write(s.text.colors.violet + s.large, "violet")
            with g.cell(): st_write(s.text.colors.salmon + s.large, "salmon")
        st_space("v", 2)

        # Sizes
        st_write(bs.sub, "Text Sizes (s.GIANT to s.tiny)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Predefined sizes from GIANT (196pt) to tiny (4pt),
            plus a factory method.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.huge, "huge (80pt)")
            st_write(s.Large, "Large (48pt)")
            st_write(s.large, "large (32pt)")
            st_write(s.small, "small (8pt)")
        """))
        st_space("v", 1)

        st_write(s.huge, "huge (80pt)")
        st_write(s.LARGE, "LARGE (64pt)")
        st_write(s.Large, "Large (48pt)")
        st_write(s.large, "large (32pt)")
        st_write(s.big, "big (24pt)")
        st_write(s.medium, "medium (16pt)")
        st_write(s.little, "little (12pt)")
        st_write(s.small, "small (8pt)")
        st_write(s.tiny, "tiny (4pt)")
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            custom_size = s.text.sizes.size(42)
            st_write(custom_size, "Custom 42pt text")
        """))
        st_space("v", 1)

        custom_size = s.text.sizes.size(42)
        st_write(custom_size, "Custom 42pt text")
        st_space("v", 2)

        # Fonts
        st_write(bs.sub, "Fonts (s.text.fonts.*)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Common font families available as predefined styles.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.text.fonts.font_arial + s.large, "Arial")
            st_write(s.text.fonts.font_courier_new + s.large,
                     "Courier New")
        """))
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=bs.cell) as g:
            with g.cell(): st_write(s.text.fonts.font_arial + s.large, "Arial")
            with g.cell(): st_write(s.text.fonts.font_georgia + s.large, "Georgia")
            with g.cell(): st_write(s.text.fonts.font_courier_new + s.large, "Courier New")
            with g.cell(): st_write(s.text.fonts.font_times_new_roman + s.large, "Times New Roman")
            with g.cell(): st_write(s.text.fonts.font_verdana + s.large, "Verdana")
            with g.cell(): st_write(s.text.fonts.font_monospace + s.large, "monospace")
        st_space("v", 2)

        # Weights
        st_write(bs.sub, "Weights (s.text.weights.*)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control font weight: bold, light, or normal.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.text.weights.bold_weight + s.large,
                     "bold_weight")
            st_write(s.text.weights.light_weight + s.large,
                     "light_weight")
        """))
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=bs.cell) as g:
            with g.cell(): st_write(s.text.weights.bold_weight + s.large, "bold_weight")
            with g.cell(): st_write(s.text.weights.light_weight + s.large, "light_weight")
            with g.cell(): st_write(s.text.weights.normal_weight + s.large, "normal_weight")
        st_space("v", 2)

        # Decorations
        st_write(bs.sub, "Decorations (s.text.decors.*)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Text decorations: italic, underline, strikethrough, and none.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.text.decors.italic_text + s.large,
                     "italic")
            st_write(s.text.decors.underline_text + s.large,
                     "underline")
        """))
        st_space("v", 1)

        with st_grid(cols=4, cell_styles=bs.cell) as g:
            with g.cell(): st_write(s.text.decors.italic_text + s.large, "italic")
            with g.cell(): st_write(s.text.decors.underline_text + s.large, "underline")
            with g.cell(): st_write(s.text.decors.strike_text + s.large, "strikethrough")
            with g.cell(): st_write(s.text.decors.decor_none_text + s.large, "none")
        st_space("v", 2)

        # Alignments
        st_write(bs.sub, "Alignments (s.text.alignments.*)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control text alignment within containers.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_block(bs.cell + s.container.sizes.width_full):
                st_write(s.text.alignments.left_align + s.large,
                         "left_align", tag=t.div)
            with st_block(bs.cell + s.container.sizes.width_full):
                st_write(s.text.alignments.center_align + s.large,
                         "center_align", tag=t.div)
        """))
        st_space("v", 1)

        cell_wide = bs.cell + s.container.sizes.width_full
        with st_block(cell_wide):
            st_write(s.text.alignments.left_align + s.large,
                     "left_align", tag=t.div)
        st_space("v", 1)
        with st_block(cell_wide):
            st_write(s.text.alignments.center_align + s.large,
                     "center_align", tag=t.div)
        st_space("v", 1)
        with st_block(cell_wide):
            st_write(s.text.alignments.right_align + s.large,
                     "right_align", tag=t.div)
        st_space("v", 1)
        with st_block(cell_wide):
            st_write(s.text.alignments.justify_align + s.large,
                     "justify_align spreads text evenly across the full width",
                     tag=t.div)
        st_space("v", 2)

        # Wrap
        st_write(bs.sub, "Text Wrap (s.text.wrap.*)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control text wrapping behavior: wrap or nowrap.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.text.wrap.nowrap + s.large, "This text will not break...")
        """))
        st_space("v", 1)

        with st_block(bs.cell + ns("max-width: 300px;")):
            st_write(s.text.wrap.nowrap + s.large,
                     "This text has nowrap and will not break even if it overflows")
