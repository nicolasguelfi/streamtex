"""Password gate for deployed StreamTeX apps.

When ``STX_PASSWORD`` is set, a branded login screen is shown: gradient
header, progress indicator, and a 6x6 grid of randomly shuffled letters
and digits.  The user must click **or type** S -> T -> X in sequence.
A wrong input silently resets the sequence.

In local dev (no env var), no gate — everything works unchanged.
"""

import os
import random

import streamlit as st
import streamlit.components.v1 as components

from .container import st_block
from .enums import Tags as t
from .space import st_space
from .styles import Style
from .write import st_write

_AUTH_KEY = "_stx_authenticated"
_SEQ_KEY = "_stx_seq"
_GRID_KEY = "_stx_grid"
_TARGET = ("S", "T", "X")

# ── Gate styles (StreamTeX Style objects) ─────────────────────────────

_HEADER_STYLE = Style(
    "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
    "padding: 40px 20px; border-radius: 8px; text-align: center;",
    "stx_gate_header",
)
_TITLE_STYLE = Style(
    "color: white; font-size: 2.5em; font-weight: bold;",
    "stx_gate_title",
)
_SUBTITLE_STYLE = Style(
    "color: white; font-size: 1.2em; opacity: 0.85;",
    "stx_gate_subtitle",
)

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

def _render_progress(seq):
    """Render the 3-circle progress indicator (S / T / X)."""
    circles = []
    for i, letter in enumerate(_TARGET):
        if i < len(seq):
            circles.append(
                f'<span style="display:inline-block;width:44px;height:44px;'
                f'line-height:44px;text-align:center;border-radius:50%;'
                f'background:linear-gradient(135deg,#667eea,#764ba2);'
                f'color:white;font-weight:bold;font-size:1.2em;">{letter}</span>'
            )
        else:
            circles.append(
                '<span style="display:inline-block;width:44px;height:44px;'
                'line-height:44px;text-align:center;border-radius:50%;'
                'border:2px solid rgba(128,128,128,0.3);'
                'color:rgba(128,128,128,0.3);font-size:1.2em;">\u2022</span>'
            )
    st.markdown(
        f'<div style="text-align:center;margin:16px 0;">'
        f'{"&nbsp;&nbsp;".join(circles)}</div>',
        unsafe_allow_html=True,
    )


# ── Main gate ─────────────────────────────────────────────────────────

def _password_gate() -> None:
    """Block rendering until the S-T-X sequence is entered.

    Called as the very first action inside :func:`st_book`.
    """
    expected = os.environ.get("STX_PASSWORD", "").strip()
    if not expected:
        return  # no gate in local dev

    if st.session_state.get(_AUTH_KEY):
        return  # already authenticated

    # --- Stable random grid per session ---
    if _GRID_KEY not in st.session_state:
        chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        random.shuffle(chars)
        st.session_state[_GRID_KEY] = chars
    if _SEQ_KEY not in st.session_state:
        st.session_state[_SEQ_KEY] = []

    grid = st.session_state[_GRID_KEY]
    seq = st.session_state[_SEQ_KEY]

    # --- Gradient header (StreamTeX components) ---
    st_space("v", 4)
    with st_block(_HEADER_STYLE):
        st_write(_TITLE_STYLE, "StreamTeX", tag=t.div)
        st_write(_SUBTITLE_STYLE,
                 "A Streamlit-based content rendering framework", tag=t.div)
    st_space("v", 1)

    # --- Progress circles ---
    _render_progress(seq)
    st_space("v", 1)

    # --- Keyboard listener ---
    components.html(_KEYBOARD_JS, height=0)

    # --- 6x6 grid ---
    clicked = None
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
        step = len(seq)
        if step < len(_TARGET) and clicked == _TARGET[step]:
            seq.append(clicked)
            st.session_state[_SEQ_KEY] = seq
            if len(seq) == len(_TARGET):
                st.session_state[_AUTH_KEY] = True
            st.rerun()
        else:
            st.session_state[_SEQ_KEY] = []
            st.rerun()

    st.stop()
