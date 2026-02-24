"""Password gate for deployed StreamTeX apps.

When the ``STX_PASSWORD`` environment variable is set, a login form is shown
before any content.  In local dev (no env var), no gate — everything works
unchanged.
"""

import os

import streamlit as st

_AUTH_KEY = "_stx_authenticated"


def _password_gate() -> None:
    """Block rendering until the correct password is entered.

    Called as the very first action inside :func:`st_book`.
    """
    expected = os.environ.get("STX_PASSWORD", "").strip()
    if not expected:
        return  # no gate in local dev

    if st.session_state.get(_AUTH_KEY):
        return  # already authenticated

    st.markdown(
        "<h2 style='text-align:center;margin-top:20vh'>StreamTeX</h2>",
        unsafe_allow_html=True,
    )
    password = st.text_input("Password", type="password", key="_stx_pw_input")
    if st.button("Login", key="_stx_pw_btn"):
        if password == expected:
            st.session_state[_AUTH_KEY] = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.stop()
