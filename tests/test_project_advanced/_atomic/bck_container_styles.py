import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Container styles catalog."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    demo_box = s.container.borders.solid_border + s.container.paddings.small_padding
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Container Styles Catalog",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Background colors
        st_write(bs.sub,
                 "Background Colors (s.container.bg_colors.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            All named CSS background colors available as predefined styles.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_block(s.container.bg_colors.light_coral_bg
                          + s.container.paddings.small_padding):
                st_write("light_coral_bg")
        """))
        st_space("v", 1)

        with st_grid(cols=4,
                     cell_styles=(s.container.paddings.medium_padding
                                  + s.center_txt + s.large)) as g:
            with g.cell():
                with st_block(s.container.bg_colors.light_coral_bg
                              + s.container.paddings.small_padding):
                    st_write("light_coral_bg")
            with g.cell():
                with st_block(s.container.bg_colors.light_blue_bg
                              + s.container.paddings.small_padding):
                    st_write("light_blue_bg")
            with g.cell():
                with st_block(s.container.bg_colors.light_green_bg
                              + s.container.paddings.small_padding):
                    st_write("light_green_bg")
            with g.cell():
                with st_block(s.container.bg_colors.light_golden_rod_yellow_bg
                              + s.container.paddings.small_padding):
                    st_write("light_golden_rod_yellow_bg")
        st_space("v", 2)

        # Paddings
        st_write(bs.sub, "Paddings (s.container.paddings.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Predefined paddings from tiny (3pt) to Giant (96pt),
            plus a factory method.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            s.container.paddings.medium_padding   # 12pt
            Paddings.size("10px", "20px")         # factory
        """))
        st_space("v", 1)

        with st_grid(cols=3,
                     cell_styles=(s.container.borders.solid_border
                                  + s.center_txt)) as g:
            with g.cell():
                with st_block(s.container.paddings.tiny_padding
                              + s.container.bg_colors.dark_sea_green_bg):
                    st_write("tiny (3pt)")
            with g.cell():
                with st_block(s.container.paddings.medium_padding
                              + s.container.bg_colors.dark_sea_green_bg):
                    st_write("medium (12pt)")
            with g.cell():
                with st_block(s.container.paddings.large_padding
                              + s.container.bg_colors.dark_sea_green_bg):
                    st_write("large (24pt)")
        st_space("v", 2)

        # Margins
        st_write(bs.sub, "Margins (s.container.margins.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control spacing outside elements.
            Same scale as paddings.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            s.container.margins.large_margin      # 24pt
            Margins.size("auto", "auto")          # factory
        """))
        st_space("v", 1)

        with st_block(s.container.borders.dashed_border):
            with st_block(s.container.margins.large_margin
                          + s.container.bg_colors.light_steel_blue_bg
                          + s.container.paddings.small_padding):
                st_write(s.large,
                         "This box has large (24pt) margin inside a dashed container")
        st_space("v", 2)

        # Borders
        st_write(bs.sub, "Borders (s.container.borders.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Border styles, widths, and colors for containers.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_block(s.container.borders.solid_border
                          + s.container.paddings.small_padding):
                st_write("solid")
            with st_block(s.container.borders.dashed_border
                          + s.container.paddings.small_padding):
                st_write("dashed")
        """))
        st_space("v", 1)

        with st_grid(cols=3,
                     cell_styles=(s.container.paddings.medium_padding
                                  + s.center_txt + s.large)) as g:
            with g.cell():
                with st_block(s.container.borders.solid_border
                              + s.container.paddings.small_padding):
                    st_write("solid")
            with g.cell():
                with st_block(s.container.borders.dashed_border
                              + s.container.paddings.small_padding):
                    st_write("dashed")
            with g.cell():
                with st_block(s.container.borders.dotted_border
                              + s.container.paddings.small_padding):
                    st_write("dotted")
            with g.cell():
                with st_block(s.container.borders.double_border
                              + s.container.borders.thick_border
                              + s.container.paddings.small_padding):
                    st_write("double + thick")
            with g.cell():
                with st_block(s.container.borders.ridge_border
                              + s.container.borders.thick_border
                              + s.container.paddings.small_padding):
                    st_write("ridge + thick")
            with g.cell():
                with st_block(s.container.borders.groove_border
                              + s.container.borders.thick_border
                              + s.container.paddings.small_padding):
                    st_write("groove + thick")
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Border factories available.
            Borders.size("2px") for custom width.
            Borders.color(s.text.colors.red) for custom color.
        """))
        st_space("v", 2)

        # Flex
        st_write(bs.sub, "Flex (s.container.flex.*)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Flexbox utilities for advanced layouts.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            s.container.flex.row_flex
            s.container.flex.col_flex
            s.container.flex.center_justify
            s.container.flex.center_align_items
        """), line_numbers=False)
        st_space("v", 2)

        # Layouts
        st_write(bs.sub, "Layouts (s.container.layouts.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Pre-composed layout patterns for common use cases.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            s.container.layouts.center    # width:fit + margin:auto
            s.container.layouts.span      # flex row + width:fit
        """), line_numbers=False)
        st_space("v", 1)

        with st_block(s.container.borders.dashed_border):
            with st_block(s.container.layouts.center
                          + s.container.bg_colors.light_salmon_bg
                          + s.container.paddings.small_padding):
                st_write(s.large, "Centered block (layouts.center)")
        st_space("v", 2)

        # Container Sizes
        st_write(bs.sub, "Container Sizes (s.container.sizes.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control container dimensions: width and height utilities.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            s.container.sizes.width_full   # 100%
            s.container.sizes.width_half   # 50%
            s.container.sizes.width_fit    # fit-content
            s.container.sizes.height_auto  # auto
        """), line_numbers=False)
