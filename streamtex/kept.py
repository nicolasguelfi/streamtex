"""Widget values that survive pagination (L22).

Streamlit purges a widget's session key as soon as a rerun ends without that
widget — and in a paginated book a widget only lives on its own page. The
value then holds ONE page and falls back to the default (sumvadis 5b4e219:
French on page 2, English again on page 3). The fix is the two-key pattern:
the widget has its own key and copies its value, on change, into a plain
session key that the purge never touches::

    st.radio("Language", ["en", "fr"], **stx.kept_widget("lang", default="en"))
    ...
    lang = stx.kept_value("lang", "en")          # on any page

Do not pass ``value=`` / ``index=`` to the widget: the kept value is its
initial state.
"""

from __future__ import annotations

from typing import Any

_WIDGET = "_stx_w_{}"
_STORE = "_stx_keep_{}"


def kept_widget(name: str, default: Any = None) -> dict:
    """``key=`` and ``on_change=`` for a widget whose value must outlive its page."""
    import streamlit as st

    widget_key, store = _WIDGET.format(name), _STORE.format(name)
    if store not in st.session_state:
        st.session_state[store] = default
    if widget_key not in st.session_state and st.session_state[store] is not None:
        st.session_state[widget_key] = st.session_state[store]

    def _copy() -> None:
        st.session_state[store] = st.session_state[widget_key]

    return {"key": widget_key, "on_change": _copy}


def kept_value(name: str, default: Any = None) -> Any:
    """The kept value of *name* (``default`` before the widget was ever shown)."""
    import streamlit as st

    return st.session_state.get(_STORE.format(name), default)
