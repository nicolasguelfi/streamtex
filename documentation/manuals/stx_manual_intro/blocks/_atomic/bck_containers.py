import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Container demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    demo_border = s.container.borders.solid_border + s.container.paddings.small_padding
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Containers: st_block & st_span",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # st_block
        st_write(bs.sub, "st_block: vertical container", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_block wraps content in a styled container.
            Children stack vertically.
        """))
        st_space("v", 1)

        show_code(file="examples/container/block_basic.py")
        st_space("v", 1)

        with st_block(s.container.bg_colors.dark_slate_gray_bg
                      + s.container.paddings.medium_padding
                      + s.center_txt):
            st_write(s.text.colors.white + s.Large, "Inside st_block")
            st_write(s.text.colors.light_gray + s.large,
                     "Children stack vertically")
            st_write(s.text.colors.light_gray + s.large,
                     "Each st_write is a new line")
        st_space("v", 2)

        # st_span
        st_write(bs.sub, "st_span: horizontal container", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_span lays children side by side on the same line.
        """))
        st_space("v", 1)

        show_code(file="examples/container/span_basic.py")
        st_space("v", 1)

        with st_span(s.container.bg_colors.dark_slate_blue_bg
                     + s.container.paddings.medium_padding):
            st_write(s.text.colors.white + s.large, "Left ")
            st_write(s.text.colors.light_green + s.large, "Center ")
            st_write(s.text.colors.light_coral + s.large, "Right")
        st_space("v", 2)

        # Nesting
        st_write(bs.sub, "Nesting containers", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Containers can be nested freely:
            block inside block, span inside block, etc.
        """))
        st_space("v", 1)

        show_code(file="examples/container/nesting.py")
        st_space("v", 1)

        with st_block(bs.demo_border):
            st_write(s.bold + s.large, "Outer st_block")
            st_space("v", 1)
            with st_block(s.container.bg_colors.light_blue_bg
                          + s.container.paddings.small_padding):
                st_write(s.large,
                         "Inner st_block with light blue background")
                with st_span():
                    st_write(s.large + s.bold, "Span child A  ")
                    st_write(s.large + s.text.colors.coral, "Span child B")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Use st_block for sections and logical grouping.
            Use st_span when you need side-by-side elements within a block.
        """))
        st_space("v", 2)

        # st_br
        st_write(bs.sub, "st_br: line breaks", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_br() adds vertical spacing between elements.
            Useful for breaking up visual density without large gaps.
            More subtle than st_space() which can be configured more explicitly.
        """))
        st_space("v", 1)

        show_code(file="examples/container/line_break.py")
        st_space("v", 1)

        st_write(s.large, "First line of text")
        st_br()
        st_write(s.large, "Second line of text")
        st_br()
        st_write(s.large, "Third line of text")
        st_space("v", 2)

        # Difference: st_br vs st_space
        st_write(bs.sub, "st_br vs st_space: when to use each", toc_lvl="+1")
        st_space("v", 1)

        st_write(s.large, """
**st_br()** — Implicit spacing
- Simple line break
- Fixed height (consistent)
- No parameters
- Use: Quick spacing between related elements

**st_space(direction, amount)** — Explicit sizing
- Configurable height/width
- Control exact spacing
- Takes "v" or "h" + amount
- Use: Precise layout control, responsive spacing
        """)
        st_space("v", 1)

        show_code(file="examples/container/br_vs_space.py")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            st_br is simpler for casual spacing.
            st_space is better when you need control.
            Combine them: st_br between sentences, st_space between sections.
        """))
