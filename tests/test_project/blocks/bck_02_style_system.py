import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Style system demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "The Style System",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Style constructor
        st_write(bs.sub, "Creating styles with Style()", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Create custom CSS styles with the Style() constructor.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            my_style = Style("color: coral; font-weight: bold;", "my_coral")
            st_write(my_style + s.large, "Text styled with a custom Style instance")
        """))
        st_space("v", 1)

        my_style = ns("color: coral; font-weight: bold;", "my_coral")
        st_write(my_style + s.large,
                 "Text styled with a custom Style instance")
        st_space("v", 2)

        # Style composition (+)
        st_write(bs.sub, "Composing styles with +", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Combine multiple styles into one with the + operator.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            combined = s.bold + s.Large + s.text.colors.dodger_blue
            st_write(combined, "Bold + Large + DodgerBlue")
        """))
        st_space("v", 1)

        combined = s.bold + s.Large + s.text.colors.dodger_blue
        st_write(combined, "Bold + Large + DodgerBlue")
        st_space("v", 2)

        # Style removal (-)
        st_write(bs.sub, "Removing styles with -", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Remove CSS properties from a composed style with the - operator.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            no_bold = combined - s.bold
            st_write(no_bold, "Large + DodgerBlue (bold removed)")
        """))
        st_space("v", 1)

        no_bold = combined - s.bold
        st_write(no_bold, "Large + DodgerBlue (bold removed)")
        st_space("v", 2)

        # Style.create()
        st_write(bs.sub, "Style.create() for themed styles", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Style.create() assigns a single style_id,
            making the composed style themeable.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            Style.create(s.bold + s.huge + color, "my_title")
        """))
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Why Style.create()?
            The theme dict can override a style by its style_id.
            Without Style.create(), composed styles have multiple ids
            and cannot be themed as a unit.
        """))
        st_space("v", 2)

        # ns() shorthand
        st_write(bs.sub, "ns() shorthand for Style()", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Import Style as ns for quick one-off CSS declarations.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            from streamtex.styles import Style as ns
            ns("padding: 10pt 36pt;")  # quick inline CSS
        """))
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Use ns() for quick one-off CSS.
            For reusable styles, define them in BlockStyles
            or custom/styles.py instead.
        """))
        st_space("v", 2)

        # repr vs theme
        st_write(bs.sub, "Theme resolution: repr() lookup", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            When a Style is rendered, repr() checks the theme dict first.
        """))
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            How theming works:
            Python calls repr(style).
            This checks theme[style_id] first.
            If found, it returns the override CSS.
            Otherwise, it returns the original CSS.
            Give meaningful style_ids to any style you want to be themeable.
        """))
