import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Export HTML demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Export HTML", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # --- 1. Download HTML button ---
        st_write(bs.sub, "The Download HTML button", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_book() enables HTML export by default.
            A "Download HTML" button appears in the sidebar.
            The exported file is a self-contained HTML document.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Export is enabled by default in st_book()
            st_book([
                blocks.bck_00_welcome,
                blocks.bck_01_architecture,
                # ...
            ], export_title="My Course")

            # The sidebar shows a "Download HTML" button automatically.
        """))
        st_space("v", 2)

        # --- 2. How it works ---
        st_write(bs.sub, "How it works: dual rendering", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Every stx.* content call goes through st_html(),
            which sends HTML to both Streamlit and an export buffer.
            Context managers (st_block, st_grid, st_list) push/pop
            wrapper tags so the exported HTML keeps the nesting structure.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Dual rendering pipeline (simplified)
            #
            #   stx.st_write(...)
            #        |
            #   st_html(html)
            #        |
            #   +----+----+
            #   |         |
            # st.html() buffer.append()
            #              |
            #       generate_full_html()
            #              |
            #     self-contained .html file
        """), language="text")
        st_space("v", 2)

        # --- 3. Customization ---
        st_write(bs.sub, "Customization", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control the export with the export_title parameter
            and the ExportConfig dataclass.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            from streamtex.export import ExportConfig

            # ExportConfig fields:
            #   enabled: bool       = False   (st_book sets this to True)
            #   page_title: str     = "StreamTeX Export"
            #   page_width: str     = "100%"
            #   page_padding: str   = "36pt"

            # The simplest way: just set export_title in st_book()
            st_book([...], export_title="My Document Title")
        """))
        st_space("v", 2)

        # --- 4. Disable export ---
        st_write(bs.sub, "Disabling export", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Pass export=False to st_book() to hide the
            Download button and skip buffer accumulation.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_book([
                blocks.bck_00_welcome,
                # ...
            ], export=False)  # No download button
        """))
        st_space("v", 2)

        # --- 5. Details ---
        show_details(textwrap.dedent("""\
            The exported file embeds all CSS and base64 images.
            Interactive features (markers, zoom) are not included.
            The HTML is fully self-contained: no external dependencies.
        """))
