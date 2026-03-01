import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Text basics styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    tip = s.project.titles.tip_label
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Text Basics", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Plain text
        st_write(bs.sub, "Plain text with st_write", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The simplest way to render text.
            Pass a string to st_write().
        """))
        st_space("v", 1)

        show_code('st_write("Hello, StreamTeX!")')
        st_space("v", 1)

        st_write(s.large, "Hello, StreamTeX!")
        st_space("v", 2)

        # Styled text
        st_write(bs.sub, "Styled text", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Pass a Style as the first argument to control appearance.
        """))
        st_space("v", 1)

        show_code('st_write(s.bold + s.Large, "Bold Large Text")')
        st_space("v", 1)

        st_write(s.bold + s.Large, "Bold Large Text")
        st_space("v", 2)

        # Tags parameter
        st_write(bs.sub, "The tag parameter", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Tags define HTML meaning (h1, div, span).

            Styles define appearance (size, color, weight).
        """))
        st_space("v", 1)

        show_code("""\
st_write(s.huge, "Section", tag=t.h1)   # semantic heading
st_write(s.huge, "Section", tag=t.div)   # styled div""")
        st_space("v", 1)

        st_write(s.huge, "Section Heading", tag=t.h1)
        st_space("v", 1)
        st_write(s.huge, "Section Heading", tag=t.div)
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Default: tag=Tags.span (inline element).

            Tags are semantic, styles are visual.

            Use tag=t.h1 for accessibility and SEO.

            Use tag=t.div for block-level visual styling without semantic meaning.
        """))
        st_space("v", 2)

        # toc_lvl and label
        st_write(bs.sub, "Table of Contents registration", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The toc_lvl parameter registers text in the sidebar Table of Contents.
        """))
        st_space("v", 1)

        show_code("""\
st_write(s.Large, "My Title", toc_lvl="1")        # absolute level
st_write(s.large, "Sub", toc_lvl="+1")            # relative level
st_write(s.large, "Custom Label", toc_lvl="2", label="Short")""")
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Default: toc_lvl=None (not registered in TOC).

            Use absolute levels ("1", "2") or relative ("+1", "-1").
            Absolute levels set the hierarchy directly.
            Relative levels adjust from the current depth.

            Default: label="" (auto-generated from text, max 73 chars).
        """))
