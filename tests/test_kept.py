"""kept_widget() / kept_value(): a widget value that survives pagination (#94)."""

import textwrap

import pytest

pytestmark = pytest.mark.usefixtures("reset_watch")


SCRIPT = textwrap.dedent("""
    import streamlit as st
    import streamtex as stx
    page = st.session_state.get("page", 1)
    if page == 1:
        st.radio("Language", ["en", "fr"], **stx.kept_widget("lang", default="en"))
    st.write("lang=" + stx.kept_value("lang", "en"))
""")


def test_kept_value_survives_pages_without_the_widget():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string(SCRIPT).run()
    at.radio[0].set_value("fr").run()
    assert at.markdown[-1].value == "lang=fr"
    for page in (2, 3, 4):                     # the widget is absent on these pages
        at.session_state["page"] = page
        at.run()
        assert at.markdown[-1].value == "lang=fr", page
    at.session_state["page"] = 1
    at.run()                                   # back on page 1: the widget shows the kept value
    assert at.radio[0].value == "fr"


def test_without_the_pattern_the_value_is_lost():
    """The defect the helper exists for (measured in sumvadis): a plain widget key is purged."""
    from streamlit.testing.v1 import AppTest

    plain = SCRIPT.replace('**stx.kept_widget("lang", default="en")', 'key="lang_plain"').replace(
        'stx.kept_value("lang", "en")', 'st.session_state.get("lang_plain", "en")')
    at = AppTest.from_string(plain).run()
    at.radio[0].set_value("fr").run()
    at.session_state["page"] = 2
    at.run()
    at.session_state["page"] = 3
    at.run()
    assert at.markdown[-1].value == "lang=en"
