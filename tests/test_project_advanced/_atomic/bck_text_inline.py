import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_code_inline, show_explanation, show_details
import textwrap


class BlockStyles:
    """Inline text styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    link_style = s.project.colors.primary_blue + s.text.decors.underline_text + s.large
    wrong_label = s.project.colors.warning_red + s.bold + s.large
    correct_label = s.project.colors.success_green + s.bold + s.large
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Inline Text & Tuples",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # WRONG vs CORRECT
        st_write(bs.sub, "Multiple calls STACK vertically", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Multiple st_write() calls stack vertically.
            Use tuples for inline flow.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.bad_callout):
            st_write(bs.wrong_label, "WRONG - stacks vertically:")
            st_space("v", 1)
            st_write(s.large,
                     "Each st_write() generates a separate HTML block.")
            st_br()
            st_write(s.large,
                     "The two texts appear on different lines,")
            st_br()
            st_write(s.large, "not side by side.")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                st_write(s.text.colors.red, "Red ")
                st_write(s.text.colors.blue, "Blue")
            """))
            st_space("v", 1)
            st_write(s.text.colors.red + s.large, "Red ")
            st_write(s.text.colors.blue + s.large, "Blue")
        st_space("v", 2)

        with st_block(s.project.containers.good_callout):
            st_write(bs.correct_label, "CORRECT - flows inline:")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                st_write(s.large,
                         (s.text.colors.red, "Red "),
                         (s.text.colors.blue, "Blue"))
            """))
            st_space("v", 1)
            st_write(s.large,
                     (s.text.colors.red, "Red "),
                     (s.text.colors.blue, "Blue"))
        st_space("v", 2)

        # Tuple syntax
        st_write(bs.sub,
                 "Tuple syntax: (style, text) and (style, text, link)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Tuples let you mix styles and links inline
            within a single st_write() call.
        """))
        st_space("v", 1)

        theURL = "https://github.com"
        show_code(textwrap.dedent("""\
            theURL = "https://github.com"
            st_write(s.large,
                     "Visit the ",
                     (s.project.colors.primary_blue + s.bold, "StreamTeX"),
                     " project on ",
                     (bs.link_style, "GitHub", theURL))
        """))
        st_space("v", 1)

        st_write(s.large,
                 "Visit the ",
                 (s.project.colors.primary_blue + s.bold, "StreamTeX"),
                 " project on ",
                 (bs.link_style, "GitHub", theURL))
        st_space("v", 2)

        # Links
        st_write(bs.sub, "Links with st_write", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Wrap entire text in a link with the link= parameter.
        """))
        st_space("v", 1)

        theURL = "https://docs.streamlit.io"
        show_code(textwrap.dedent("""\
            theURL = "https://docs.streamlit.io"
            st_write(s.large, "Click here for Streamlit docs", link=theURL)
        """))
        st_space("v", 1)

        st_write(s.large, "Click here for Streamlit docs", link=theURL)
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_write(bs.link_style,
                     "Styled link (no default decoration)",
                     link=theURL, no_link_decor=True)
        """))
        st_space("v", 1)

        st_write(bs.link_style,
                 "Styled link (no default decoration)",
                 link=theURL, no_link_decor=True)
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Default: link="" (no link), no_link_decor=False, hover=True.
            Links default to 12pt font size.
            When surrounding text is larger,
            include font size in the link style to match.
        """))
