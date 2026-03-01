"""Markers in Paginated Mode — cross-page navigation & widget details.

Covers continuous vs paginated behaviour, cross-page navigation,
the floating widget internals, and the 3-file architecture.
"""

from streamtex import st_write, st_block, st_space
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Marker pagination styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    feature = s.project.titles.feature_title


bs = BlockStyles


def build():
    st_write(bs.heading, "Markers in Paginated Mode",
             tag=t.div, toc_lvl="1")
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Continuous vs Paginated
    # ------------------------------------------------------------------
    st_write(bs.sub, "Continuous vs Paginated", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        In continuous mode (paginate=False), navigating between markers
        triggers a smooth scroll to the target element on the same page.

        In paginated mode (paginate=True), markers may span multiple
        pages. The navigation system handles page changes automatically:
    """))
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        When you press Next at the last marker of a page, the system
        switches to the next page and scrolls to its first marker.

        Similarly, pressing Prev at the first marker of a page returns
        to the previous page and scrolls to its last marker.
    """))
    st_space("v", 2)

    # ------------------------------------------------------------------
    # The floating widget
    # ------------------------------------------------------------------
    st_write(bs.sub, "The Floating Widget", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        When show_nav_ui=True (default), a floating widget appears
        with the following elements:
    """))
    st_space("v", 1)

    show_explanation(textwrap.dedent("""\
        - Position counter showing "current / total" (e.g. "3 / 12")
        - Prev (◀) and Next (▶) buttons
        - A list button (☰) that opens a popup with all markers
        - An optional label showing the current marker name
    """))
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        The popup lists markers from all pages. In paginated mode,
        clicking a marker on a different page triggers a page change
        followed by a scroll to the target marker.
    """))
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        A scroll tracker updates the current marker as you scroll
        manually, keeping the counter and popup highlight in sync.
    """))
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Architecture (for maintainers)
    # ------------------------------------------------------------------
    st_write(bs.sub, "Architecture Overview", toc_lvl="+1")
    st_space("v", 1)

    show_details(textwrap.dedent("""\
        Three files collaborate to implement the marker system:

        marker.py — MarkerConfig dataclass, MarkerRegistry singleton,
        st_marker() for manual placement, and inject_marker_navigation()
        which emits the floating widget + keyboard/scroll JavaScript.

        book.py — Lifecycle integration. Calls reset_marker_registry()
        before rendering blocks, then inject_marker_navigation() after.
        In paginated mode, passes page metadata so the JS can handle
        cross-page navigation via _stxMarkerBoundary and _stxMarkerGoToPage.

        write.py — The _handle_toc() function bridges TOC headings
        to markers. When a heading has a toc_lvl and the MarkerConfig
        is active, it calls register_marker() based on auto_marker_on_toc
        and the per-heading marker= parameter.
    """))
    st_space("v", 1)

    show_code("""\
# Lifecycle in book.py (simplified)
reset_marker_registry(marker_config)  # 1. Init registry

for block in blocks:                   # 2. Render blocks
    st_include(block)                  #    (st_write auto-registers markers)

inject_marker_navigation()             # 3. Emit widget + JS""")
