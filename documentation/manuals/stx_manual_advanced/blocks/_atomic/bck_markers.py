"""Marker Navigation — Introduction & basic usage.

Covers: manual markers (visible/invisible), auto-markers from TOC,
and the marker= parameter on st_write.
"""

from streamtex import st_write, st_block, st_space, st_marker, st_include
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Marker intro styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    feature = s.project.titles.feature_title


bs = BlockStyles


def build():
    st_write(bs.heading, "Marker Navigation", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Introduction
    # ------------------------------------------------------------------
    show_explanation(textwrap.dedent("""\
        Markers are navigation waypoints placed in your content.
        They power the floating navigation widget (prev/next buttons,
        popup list) and keyboard shortcuts (PageDown/PageUp by default).
        Markers work in both continuous and paginated book modes.
    """))
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Manual markers — st_marker()
    # ------------------------------------------------------------------
    st_write(bs.sub, "Manual Markers — st_marker()", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        Use st_marker() to place a waypoint at any position in your content.
        By default markers are invisible (height 0, used only for navigation).
        Set visible=True to show a dashed border with the marker label.
    """))
    st_space("v", 1)

    show_code(file="examples/nav/marker_manual.py")
    st_space("v", 1)

    # Live demo
    st_write(bs.feature, "Live demo:")
    st_marker("Visible Marker Demo", visible=True)
    st_space("v", 1)
    st_marker("Hidden Waypoint")
    st_write(s.large,
             "(An invisible marker was placed just above this line.)")
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Auto-markers from TOC headings
    # ------------------------------------------------------------------
    st_write(bs.sub, "Auto-Markers from TOC Headings", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        Instead of placing markers manually, you can bridge TOC headings
        to markers automatically via the auto_marker_on_toc setting
        in MarkerConfig:
    """))
    st_space("v", 1)

    show_code(file="examples/nav/marker_auto_toc.py")
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Per-heading control — marker= parameter
    # ------------------------------------------------------------------
    st_write(bs.sub, "Per-Heading Control — marker= Parameter",
             toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        Even when auto_marker_on_toc is active, you can override the
        behavior for individual headings using the marker= parameter
        on st_write:
    """))
    st_space("v", 1)

    show_code(file="examples/nav/marker_per_heading.py")
    st_space("v", 2)

    show_details(textwrap.dedent("""\
        The marker= parameter only applies to headings that have a
        toc_lvl. It has no effect on non-TOC text.
        When marker=None (default), the auto_marker_on_toc setting
        decides whether the heading becomes a marker.
    """))
