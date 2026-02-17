import streamlit as st
import os
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Custom styles demo."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    cell = (s.container.borders.solid_border
            + s.container.paddings.small_padding
            + s.container.layouts.vertical_center_layout)
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Custom Styles Pattern",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # The inheritance chain
        st_write(bs.sub, "Style class inheritance chain", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Custom styles are organized in layers,
            each building on the previous.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            ColorsCustom
              -> BackgroundsCustom
                -> TextStylesCustom
                  -> Custom
                    -> Styles(StreamTeX_Styles)
        """), line_numbers=False)
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Each layer builds on the previous.
            ColorsCustom defines raw colors.
            TextStylesCustom composes colors with sizes and weights.
            Custom aggregates all categories.
            Styles inherits StreamTeX_Styles.
        """))
        st_space("v", 2)

        # Actual styles.py source
        st_write(bs.sub, "custom/styles.py source", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The actual custom styles
            defined in this project.
        """))
        st_space("v", 1)

        try:
            styles_path = os.path.join(
                os.path.dirname(__file__), "..", "custom", "styles.py")
            with open(styles_path) as f:
                styles_source = f.read()
            show_code(styles_source)
        except Exception:
            show_code("# Could not read custom/styles.py")
        st_space("v", 2)

        # Colors
        st_write(bs.sub, "Project colors (s.project.colors.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            All project-specific text colors
            in one place.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.project.colors.primary_blue + s.large,
                     "primary_blue")
            st_write(s.project.colors.accent_teal + s.large,
                     "accent_teal")
        """))
        st_space("v", 1)

        with st_grid(cols=3, cell_styles=bs.cell) as g:
            with g.cell():
                st_write(s.project.colors.primary_blue + s.large,
                         "primary_blue")
            with g.cell():
                st_write(s.project.colors.accent_teal + s.large,
                         "accent_teal")
            with g.cell():
                st_write(s.project.colors.warning_red + s.large,
                         "warning_red")
            with g.cell():
                st_write(s.project.colors.success_green + s.large,
                         "success_green")
            with g.cell():
                st_write(s.project.colors.neutral_gray + s.large,
                         "neutral_gray")
            with g.cell():
                st_write(s.project.colors.highlight_amber + s.large,
                         "highlight_amber")
        st_space("v", 2)

        # Title styles
        st_write(bs.sub, "Title compositions (s.project.titles.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Pre-composed title styles
            combining color, weight, and size.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(s.project.titles.course_title, "My Title")
            st_write(s.project.titles.section_title, "Section")
            st_write(s.project.titles.section_subtitle, "Sub")
        """))
        st_space("v", 1)

        st_write(s.project.titles.course_title, "course_title (Giant)")
        st_space("v", 1)
        st_write(s.project.titles.section_title, "section_title (huge)")
        st_space("v", 1)
        st_write(s.project.titles.section_subtitle,
                 "section_subtitle (Large)")
        st_space("v", 1)
        st_write(s.project.titles.tip_label, "tip_label (large)")
        st_space("v", 1)
        st_write(s.project.titles.warning_label, "warning_label (large)")
        st_space("v", 2)

        # Callout containers
        st_write(bs.sub,
                 "Callout containers (s.project.containers.*)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Styled containers for different message types:
            success, error, tip, note.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_block(s.project.containers.good_callout):
                st_write(s.project.colors.success_green
                         + s.bold + s.large,
                         "good_callout")
                st_write(s.large,
                         "Use for correct examples.")
        """))
        st_space("v", 1)

        with st_block(s.project.containers.good_callout):
            st_write(s.project.colors.success_green + s.bold + s.large,
                     "good_callout")
            st_write(s.large,
                     "Use for correct examples and positive feedback.")
        st_space("v", 1)

        with st_block(s.project.containers.bad_callout):
            st_write(s.project.colors.warning_red + s.bold + s.large,
                     "bad_callout")
            st_write(s.large,
                     "Use for wrong examples and common mistakes.")
        st_space("v", 1)

        with st_block(s.project.containers.tip_callout):
            st_write(s.project.colors.primary_blue + s.bold + s.large,
                     "tip_callout")
            st_write(s.large, "Use for tips and best practices.")
        st_space("v", 1)

        with st_block(s.project.containers.note_callout):
            st_write(s.project.colors.highlight_amber + s.bold + s.large,
                     "note_callout")
            st_write(s.large,
                     "Use for notes and important information.")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Use generic English names.
            Define colors and compositions
            once in custom/styles.py,
            then reuse everywhere via s.project.*.
        """))
