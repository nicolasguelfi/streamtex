import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_code_inline, show_explanation, show_details
import textwrap


class BlockStyles:
    """Best practices summary styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    wrong_label = s.project.colors.warning_red + s.bold + s.large
    correct_label = s.project.colors.success_green + s.bold + s.large
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Best Practices Summary",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Rule 1: sx for content, st for interactivity
        st_write(bs.sub,
                 "sx for content, st for interactivity",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use StreamTeX (sx.*) for all content rendering.
            Reserve st.* for interactive widgets.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.bad_callout):
            st_write(bs.wrong_label, "WRONG:")
            st_space("v", 1)
            st_write(s.large, "Bypasses StreamTeX styling system.")
            st_br()
            st_write(s.large, "No theme support, no style composition.")
            st_br()
            st_write(s.large, "Raw HTML is fragile and hard to maintain.")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                st.markdown(
                    "<h1 style='color:red'>Title</h1>",
                    unsafe_allow_html=True)
            """))
        st_space("v", 1)

        with st_block(s.project.containers.good_callout):
            st_write(bs.correct_label, "CORRECT:")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                st_write(s.text.colors.red + s.huge,
                         "Title", tag=t.h1)
            """))
        st_space("v", 2)

        # Rule 2: Inline text
        st_write(bs.sub,
                 "One st_write with tuples for inline",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use tuples for inline mixed-style text
            in a single st_write() call.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.bad_callout):
            st_write(bs.wrong_label, "WRONG — stacks vertically:")
            st_space("v", 1)
            st_write(s.large,
                     "Each st_write() creates a separate HTML block.")
            st_br()
            st_write(s.large,
                     "'Hello' and 'World' appear on different lines")
            st_br()
            st_write(s.large, "instead of flowing inline.")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                st_write(s.red, "Hello ")
                st_write(s.blue, "World")
            """))
        st_space("v", 1)

        with st_block(s.project.containers.good_callout):
            st_write(bs.correct_label, "CORRECT — flows inline:")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                st_write(s.large,
                         (s.red, "Hello "),
                         (s.blue, "World"))
            """))
        st_space("v", 2)

        # Rule 3: No hardcoded colors
        st_write(bs.sub, "No hardcoded black or white", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Avoid hardcoded black/white —
            let Streamlit handle light/dark theming.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.bad_callout):
            st_write(bs.wrong_label, "WRONG:")
            st_space("v", 1)
            st_write(s.large,
                     "Hardcoded black text becomes invisible")
            st_br()
            st_write(s.large, "on dark backgrounds.")
            st_br()
            st_write(s.large,
                     "Streamlit handles theming automatically")
            st_br()
            st_write(s.large, "when you omit these.")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                Style("color: black;")             # breaks in dark mode
                Style("background-color: white;")  # breaks in dark mode
            """))
        st_space("v", 1)

        with st_block(s.project.containers.good_callout):
            st_write(bs.correct_label, "CORRECT:")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                # Omit color — let Streamlit handle Light/Dark mode
                # Or use theme overrides for dark adaptation
            """))
        st_space("v", 2)

        # Rule 4: No raw HTML/CSS
        st_write(bs.sub, "No raw HTML or CSS in code", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use StreamTeX style composition
            instead of raw HTML/CSS strings.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.bad_callout):
            st_write(bs.wrong_label, "WRONG:")
            st_space("v", 1)
            st_write(s.large,
                     "Raw HTML bypasses the Style system entirely.")
            st_br()
            st_write(s.large, "No theme overrides, no composability,")
            st_br()
            st_write(s.large, "no reuse across blocks.")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                st.html("<div style='padding:10px'>Content</div>")
            """))
        st_space("v", 1)

        with st_block(s.project.containers.good_callout):
            st_write(bs.correct_label, "CORRECT:")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                with st_block(s.container.paddings.medium_padding):
                    st_write("Content")
            """))
        st_space("v", 2)

        # Rule 5: Style reuse
        st_write(bs.sub, "Define once, reuse everywhere", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Define styles once in custom/styles.py
            and reuse via s.project.*.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.bad_callout):
            st_write(bs.wrong_label, "WRONG — duplicate definitions:")
            st_space("v", 1)
            st_write(s.large,
                     "Duplicating style definitions across files")
            st_br()
            st_write(s.large,
                     "means every change must be applied")
            st_br()
            st_write(s.large,
                     "in multiple places. Risk of inconsistency.")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                # In block A:
                title = s.bold + s.huge + s.text.colors.blue
                # In block B (same style redefined):
                title = s.bold + s.huge + s.text.colors.blue
            """))
        st_space("v", 1)

        with st_block(s.project.containers.good_callout):
            st_write(bs.correct_label,
                     "CORRECT — define in custom/styles.py:")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                # custom/styles.py:
                course_title = Style.create(
                    blue + bold + huge, "course_title")
                # Any block:
                st_write(s.project.titles.course_title, "My Title")
            """))
        st_space("v", 2)

        # Rule 6: Block structure
        st_write(bs.sub,
                 "Every block needs BlockStyles + build()",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Follow the standard block pattern
            for consistency.
        """))
        st_space("v", 1)

        with st_block(s.project.containers.good_callout):
            st_write(bs.correct_label, "Standard block pattern:")
            st_space("v", 1)
            show_code_inline(textwrap.dedent("""\
                class BlockStyles:
                    heading = s.project.titles.section_title + s.center_txt
                bs = BlockStyles

                def build():
                    st_write(bs.heading, "Title", toc_lvl="1")
            """))
        st_space("v", 2)

        # Rule 7: link font size
        st_write(bs.sub, "Include font size in link styles", toc_lvl="+1")
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Links default to 12pt font size.
            When surrounding text is larger,
            include the font size in the link tuple style to match.
        """))
        st_space("v", 2)

        # Closing
        with st_block(s.center_txt):
            st_write(s.project.titles.section_subtitle,
                     "End of StreamTeX Training Course")
            st_space("v", 1)
            st_write(s.large, "You now know every major feature.")
            st_br()
            st_write(s.large, "Build something great!")
