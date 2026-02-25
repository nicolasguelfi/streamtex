"""Password gate for deployed StreamTeX apps.

When ``STX_PASSWORD`` is set, a branded login screen is shown: gradient
header, 6 activity circles, and a 6x6 grid of A-Z + 0-9 in order.
The user must click **or type** S -> T -> X in sequence (at any point
in the stream of clicks).  Each input fills a circle; circles loop
infinitely.  The sequence is invisible — circles show only colours,
never the letters typed.

In local dev, the gate is off by default.  Set ``STX_GATE=1`` (without
``STX_PASSWORD``) to preview it locally.
"""

import os

import streamlit as st
import streamlit.components.v1 as components

from .container import st_block
from .enums import Tags as t
from .space import st_space
from .styles import Style
from .write import st_write

# ── Session-state keys ────────────────────────────────────────────────

_AUTH_KEY = "_stx_authenticated"
_MATCH_KEY = "_stx_match"        # int (0-2): progress in S→T→X
_CIRCLES_KEY = "_stx_circles"    # list[6]: None or colour string
_NEXT_KEY = "_stx_next"          # int (0-5): next circle slot
_TOTAL_KEY = "_stx_total"        # int: total clicks (detects wrap)
_GRID_KEY = "_stx_grid"          # list[36]: ordered chars

_TARGET = ("S", "T", "X")

# Ordered grid: A-Z then 0-9 (36 chars for a 6×6 grid)
_ORDERED_CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

# ══════════════════════════════════════════════════════════════════════
# LAYOUT TUNABLES — adjust these to fine-tune the gate appearance
# ══════════════════════════════════════════════════════════════════════

_TOP_SPACE = "0.5em"        # padding above the banner
_HEADER_VPAD = "12px"       # vertical padding inside the banner
_HEADER_RADIUS = "8px"      # banner border-radius
_TITLE_SIZE = "4em"         # banner title font-size
_SUBTITLE_SIZE = "2em"      # banner subtitle font-size
_GAP_HEADER = 0.3           # em — gap between banner and circles
_CIRCLE_SIZE = "72px"       # diameter of each activity circle
_GAP_CIRCLES = 0.2          # em — gap between circles and grid
_GRID_RATIO = [1, 2, 1]     # column ratio for centering the grid
_CELL_HEIGHT = 5             # vh — cell height (viewport-relative, -20%)
_FONT_RATIO = 1.5           # font-size as fraction of cell height
_CELL_RADIUS = "10px"        # cell border-radius

# ── Bright gradient palettes (dark-mode friendly) ─────────────────────

_CELL_GRADIENTS = (
    "linear-gradient(135deg, #667eea, #7b93f2)",  # intro blue
    "linear-gradient(135deg, #9b59b6, #b07cc9)",  # advanced purple
    "linear-gradient(135deg, #2EC4B6, #52ddd0)",  # collection teal
)

_CIRCLE_COLORS = (
    "#7b93f2",  # bright blue
    "#b07cc9",  # bright purple
    "#52ddd0",  # bright teal
    "#56e8a7",  # bright green
    "#7b93f2",  # bright blue
    "#b07cc9",  # bright purple
)

# ══════════════════════════════════════════════════════════════════════
# END TUNABLES
# ══════════════════════════════════════════════════════════════════════

# ── Gate styles (StreamTeX Style objects) ─────────────────────────────

_HEADER_STYLE = Style(
    "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
    f"padding: {_HEADER_VPAD} 20px; border-radius: {_HEADER_RADIUS}; "
    "text-align: center;",
    "stx_gate_header",
)
_TITLE_STYLE = Style(
    f"color: white; font-size: {_TITLE_SIZE}; font-weight: bold;",
    "stx_gate_title",
)
_SUBTITLE_STYLE = Style(
    f"color: white; font-size: {_SUBTITLE_SIZE}; opacity: 0.85;",
    "stx_gate_subtitle",
)


# ── Cell CSS (generated from tunables) ────────────────────────────────

def _build_cell_css() -> str:
    """Generate the <style> block for grid cells from tunables."""
    h = _CELL_HEIGHT
    fs = round(h * _FONT_RATIO, 1)
    g = _CELL_GRADIENTS

    return (
        "<style>"
        # --- Reduce Streamlit default top padding ---
        f".stMainBlockContainer {{ padding-top: {_TOP_SPACE} !important; }}"
        # --- Button base ---
        "[data-testid='stColumn'] button[kind='secondary'] {"
        f"  min-height: 0 !important;"
        f"  font-size: {fs}vh !important;"
        f"  border-radius: {_CELL_RADIUS};"
        "  border: none !important;"
        "  padding: 0 !important;"
        "}"
        # --- White bold text on buttons (font-size must target <p> too) ---
        "[data-testid='stColumn'] button[kind='secondary'] p {"
        "  color: white !important;"
        "  font-weight: bold !important;"
        f"  font-size: {fs}vh !important;"
        "  line-height: 1 !important;"
        "  margin: 0 !important;"
        "  padding: 4px 0 !important;"
        "}"
        # --- Bright gradient backgrounds (cycling 3 colours across 6 cols) ---
        # Prefix with [stColumn] so nested outer columns don't interfere
        "[data-testid='stColumn'] [data-testid='stHorizontalBlock'] "
        "[data-testid='stColumn']:nth-child(3n+1) "
        f"button[kind='secondary'] {{ background: {g[0]} !important; }}"
        "[data-testid='stColumn'] [data-testid='stHorizontalBlock'] "
        "[data-testid='stColumn']:nth-child(3n+2) "
        f"button[kind='secondary'] {{ background: {g[1]} !important; }}"
        "[data-testid='stColumn'] [data-testid='stHorizontalBlock'] "
        "[data-testid='stColumn']:nth-child(3n+3) "
        f"button[kind='secondary'] {{ background: {g[2]} !important; }}"
        "</style>"
    )


_CELL_CSS = _build_cell_css()


# ── Keyboard listener (injected as zero-height iframe) ────────────────

_KEYBOARD_JS = """<script>
(function() {
    var handler = function(e) {
        if (e.ctrlKey || e.altKey || e.metaKey) return;
        var key = e.key.toUpperCase();
        if (!/^[A-Z0-9]$/.test(key)) return;
        var btns = window.parent.document.querySelectorAll('button');
        var grid = [];
        for (var i = 0; i < btns.length; i++) {
            if (/^[A-Z0-9]$/.test(btns[i].textContent.trim())) grid.push(btns[i]);
        }
        if (grid.length === 0) {
            window.parent.document.removeEventListener('keydown', handler);
            return;
        }
        for (var j = 0; j < grid.length; j++) {
            if (grid[j].textContent.trim() === key) {
                grid[j].click();
                e.preventDefault();
                break;
            }
        }
    };
    window.parent.document.addEventListener('keydown', handler);
})();
</script>"""


# ── Rendering helpers ─────────────────────────────────────────────────

def _render_circles():
    """Render 6 activity circles — colours only, no letters revealed."""
    circles_state = st.session_state.get(_CIRCLES_KEY, [None] * 6)
    sz = _CIRCLE_SIZE
    parts = []
    for i in range(6):
        colour = circles_state[i]
        if colour:
            parts.append(
                f'<span style="display:inline-block;width:{sz};height:{sz};'
                f'border-radius:50%;background:{colour};'
                f'box-shadow:0 0 12px {colour}88;"></span>'
            )
        else:
            parts.append(
                f'<span style="display:inline-block;width:{sz};height:{sz};'
                'border-radius:50%;border:2px solid rgba(128,128,128,0.3);"></span>'
            )
    st.markdown(
        f'<div style="text-align:center;margin:4px 0;">'
        f'{"&nbsp;".join(parts)}</div>',
        unsafe_allow_html=True,
    )


# ── Main gate ─────────────────────────────────────────────────────────

def _password_gate() -> None:
    """Block rendering until the S-T-X sequence is entered.

    Called as the very first action inside :func:`st_book`.
    """
    has_password = bool(os.environ.get("STX_PASSWORD", "").strip())
    force_gate = os.environ.get("STX_GATE", "").strip() == "1"
    if not has_password and not force_gate:
        return  # no gate in local dev

    if st.session_state.get(_AUTH_KEY):
        return  # already authenticated

    # --- Initialise session state ---
    st.session_state.setdefault(_GRID_KEY, _ORDERED_CHARS[:])
    st.session_state.setdefault(_MATCH_KEY, 0)
    st.session_state.setdefault(_CIRCLES_KEY, [None] * 6)
    st.session_state.setdefault(_NEXT_KEY, 0)
    st.session_state.setdefault(_TOTAL_KEY, 0)

    grid = st.session_state[_GRID_KEY]

    # --- Cell + page CSS ---
    st.markdown(_CELL_CSS, unsafe_allow_html=True)

    # --- Gradient header (StreamTeX components) ---
    with st_block(_HEADER_STYLE):
        st_write(_TITLE_STYLE, "StreamTeX", tag=t.div)
        st_write(_SUBTITLE_STYLE,
                 "A Streamlit-based content rendering framework", tag=t.div)
    st_space("v", _GAP_HEADER)

    # --- 6 activity circles ---
    _render_circles()
    st_space("v", _GAP_CIRCLES)

    # --- Keyboard listener ---
    components.html(_KEYBOARD_JS, height=0)

    # --- 6×6 grid (centered) ---
    clicked = None
    _, center, _ = st.columns(_GRID_RATIO)
    with center:
        for row in range(6):
            cols = st.columns(6)
            for col in range(6):
                idx = row * 6 + col
                char = grid[idx]
                with cols[col]:
                    if st.button(char, key=f"_stx_g{idx}",
                                 use_container_width=True):
                        clicked = char

    # --- Process click / keystroke ---
    if clicked is not None:
        # 1. Advance circle display (infinite loop of 6)
        pos = st.session_state[_NEXT_KEY]
        total = st.session_state[_TOTAL_KEY]
        circles = st.session_state[_CIRCLES_KEY]

        if pos == 0 and total > 0:
            circles = [None] * 6  # new cycle — clear previous

        circles[pos] = _CIRCLE_COLORS[pos]
        st.session_state[_CIRCLES_KEY] = circles
        st.session_state[_NEXT_KEY] = (pos + 1) % 6
        st.session_state[_TOTAL_KEY] = total + 1

        # 2. Advance S→T→X match (embedded anywhere in the stream)
        match = st.session_state[_MATCH_KEY]
        if match < len(_TARGET) and clicked == _TARGET[match]:
            match += 1
        elif clicked == _TARGET[0]:
            match = 1  # restart from S
        else:
            match = 0
        st.session_state[_MATCH_KEY] = match

        if match == len(_TARGET):
            st.session_state[_AUTH_KEY] = True

        st.rerun()

    st.stop()
