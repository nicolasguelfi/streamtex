"""The headless Streamlit of `stx export html` / `stx cache` runs ordinary widget code.

Since 0.7.54 a block that raises stops the export (#134); these idioms of the
advanced manual raised under the headless stand-ins and stopped it.
"""
import textwrap

from streamtex.cli.cache_cmd import _headless_streamlit


def _run(code):
    with _headless_streamlit():
        import streamlit as st
        ns = {"st": st}
        exec(textwrap.dedent(code), ns)  # noqa: S102
        return ns


def test_number_input_takes_its_bounds_by_position():
    ns = _run("""
        age = st.number_input("Age", 0, 120, 25)
        low = st.number_input("Low", 5, 10)
        bare = st.number_input("Bare")
        kw = st.number_input("Kw", min_value=1.5, value=2.5)
    """)
    assert (ns["age"], ns["low"], ns["bare"], ns["kw"]) == (25, 5, 0, 2.5)


def test_session_state_takes_attributes():
    ns = _run("""
        if "step" not in st.session_state:
            st.session_state.step = 1
        st.session_state.step += 1
        by_key = st.session_state["step"]
        missing = hasattr(st.session_state, "nothing")
    """)
    assert ns["by_key"] == 2 and ns["missing"] is False


def test_widgets_on_columns_and_sidebar_return_values():
    ns = _run("""
        col1, col2 = st.columns(2)
        a = col1.checkbox("A", value=True)
        n = col2.number_input("N", 0, 9, 3) + 1
        s = st.sidebar.selectbox("S", ["x", "y"], index=1)
    """)
    assert (ns["a"], ns["n"], ns["s"]) == (True, 4, "y")


def test_streamlit_is_restored():
    import streamlit as st
    before = (st.number_input, st.session_state)
    with _headless_streamlit():
        assert st.number_input is not before[0]
    assert (st.number_input, st.session_state) == before
