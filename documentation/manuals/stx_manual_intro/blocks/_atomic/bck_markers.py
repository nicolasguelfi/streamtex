import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Marker demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Marker Navigation",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            Markers let you place navigation waypoints anywhere in content.
            Use ArrowRight/ArrowLeft to jump between them.
        """))
        st_space("v", 2)

        # --- Manual marker (visible) ---
        st_marker("Visible Marker Demo", visible=True)

        st_write(bs.sub, "Manual markers", toc_lvl="+1")
        st_space("v", 1)

        show_code(file="examples/nav/marker_manual.py")
        st_space("v", 2)

        # --- Invisible marker ---
        st_marker("Hidden Waypoint")

        st_write(bs.sub, "Auto-markers from TOC", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            With auto_marker_on_toc, TOC headings become markers automatically.
            Use marker=False on st_write to exclude a specific heading.
        """))
        st_space("v", 1)

        show_code(file="examples/nav/marker_auto_toc.py")
        st_space("v", 2)

        # --- Another manual marker ---
        st_marker("End of Marker Demo", visible=True)

        show_details(textwrap.dedent("""\
            The nav widget shows your position and total marker count.
            Keyboard navigation skips focused inputs for form safety.
        """))
