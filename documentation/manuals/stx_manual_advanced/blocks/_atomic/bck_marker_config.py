"""MarkerConfig Reference — complete field-by-field documentation.

Covers every MarkerConfig field, modifier key syntax, a full book.py
example, and keyboard safety notes.
"""

from streamtex import (
    st_write, st_block, st_space, st_grid,
)
from streamtex.enums import Tags as t
from streamtex.styles import Style, StyleGrid
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """MarkerConfig reference styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    feature = s.project.titles.feature_title
    field_name = s.bold + s.large
    field_desc = s.large


bs = BlockStyles


def build():
    st_write(bs.heading, "MarkerConfig Reference", tag=t.div, toc_lvl="1")
    st_space("v", 2)

    show_explanation(textwrap.dedent("""\
        MarkerConfig is a dataclass that controls the marker navigation
        system. Pass it to st_book() via the marker_config= parameter.
        All fields have sensible defaults — you only need to set what
        you want to customize.
    """))
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Field reference grid
    # ------------------------------------------------------------------
    st_write(bs.sub, "Field Reference", toc_lvl="+1")
    st_space("v", 1)

    _field_row("show_nav_ui", "bool", "True",
               "Show or hide the floating navigation widget "
               "(counter, prev/next buttons, popup list).")

    _field_row("auto_marker_on_toc", "bool | int", "False",
               "Bridge TOC headings to markers automatically. "
               "True = all levels, int N = up to level N, False = none. "
               "Recommended: 1 for paginated books.")

    _field_row("nav_position", "str", '"bottom-right"',
               'Widget position. Supported values: '
               '"bottom-right", "bottom-center".')

    _field_row("nav_label_chars", "int", "40",
               "Max characters shown for the current marker label "
               "in the widget. Set to 0 to hide the label.")

    _field_row("popup_open", "bool", "False",
               "Initial state of the marker popup list "
               "(open or closed on first render).")

    _field_row("next_keys", "list[str]", '["PageDown"]',
               "Keyboard keys to navigate to the next marker. "
               "Supports modifier syntax (see below).")

    _field_row("prev_keys", "list[str]", '["PageUp"]',
               "Keyboard keys to navigate to the previous marker. "
               "Supports modifier syntax (see below).")

    st_space("v", 2)

    # ------------------------------------------------------------------
    # Modifier key syntax
    # ------------------------------------------------------------------
    st_write(bs.sub, "Keyboard Modifier Syntax", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, textwrap.dedent("""\
        Key definitions use the JavaScript KeyboardEvent.key values.
        Combine a modifier with a key using the + separator:
    """))
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        # Single keys
        next_keys=["PageDown", "ArrowRight"]

        # With modifiers: Ctrl, Shift, Alt, Meta (Cmd on macOS)
        next_keys=["PageDown", "Ctrl+ArrowRight"]
        prev_keys=["PageUp", "Ctrl+ArrowLeft"]

        # Multiple modifiers are NOT chained — use one modifier per entry
    """))
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Complete example
    # ------------------------------------------------------------------
    st_write(bs.sub, "Complete Example in book.py", toc_lvl="+1")
    st_space("v", 1)

    show_code(textwrap.dedent("""\
        from streamtex import st_book, TOCConfig, MarkerConfig, BannerConfig

        marker_config = MarkerConfig(
            auto_marker_on_toc=1,             # Level-1 TOC headings = markers
            nav_position="bottom-right",       # Widget in bottom-right corner
            next_keys=["PageDown", "ArrowRight"],
            prev_keys=["PageUp", "ArrowLeft"],
            nav_label_chars=40,                # Show up to 40 chars of label
        )

        st_book(
            [...],
            marker_config=marker_config,
            paginate=True,
            banner=BannerConfig.full(),        # Navigation banner style
        )
    """))
    st_space("v", 2)

    # ------------------------------------------------------------------
    # Keyboard safety
    # ------------------------------------------------------------------
    st_write(bs.sub, "Keyboard Safety", toc_lvl="+1")
    st_space("v", 1)

    show_details(textwrap.dedent("""\
        The keyboard handler automatically ignores key presses when
        the focus is on an input, textarea, select, or contentEditable
        element. This prevents marker navigation from interfering
        with form fields and text editing.

        Pressing Escape while the popup is open closes it without
        triggering any navigation.
    """))


def _field_row(name: str, type_str: str, default: str, desc: str):
    """Render a single field documentation row."""
    with st_block(s.project.containers.explanation_box):
        st_write(bs.field_name, f"{name}")
        st_write(s.large,
                 (s.bold, f"Type: "), f"{type_str}  —  ",
                 (s.bold, "Default: "), f"{default}")
        st_write(bs.field_desc, desc)
