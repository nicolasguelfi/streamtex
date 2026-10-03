"""Lot F — widget values that survive pagination (L22), versioned facts (L23)."""

import textwrap

import pytest
from click.testing import CliRunner

from streamtex import watch
from streamtex.cli.commands import cli
from streamtex.facts import fact, stale_facts


@pytest.fixture(autouse=True)
def _clean():
    watch._reset_for_tests()
    yield
    watch._reset_for_tests()


# --- L22 ------------------------------------------------------------------

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


# --- L23 ------------------------------------------------------------------

def _facts(tmp_path, recorded="0.85.0", current="0.86.0"):
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n')
    (tmp_path / "facts").mkdir()
    (tmp_path / "gse").mkdir()
    (tmp_path / "gse" / "VERSION").write_text(current + "\n")
    (tmp_path / "facts" / "gse-one.toml").write_text(textwrap.dedent(f"""
        [source]
        name = "GSE-One"
        version = "{recorded}"
        current = "../gse/VERSION"
        [facts]
        agents = 23
        commands = 41
        paths.registry = ".gse/registry"
    """))
    return tmp_path


def test_fact_lookup_and_strictness(tmp_path):
    root = _facts(tmp_path)
    assert fact("gse-one", "agents", root=root) == 23
    assert fact("gse-one", "paths.registry", root=root) == ".gse/registry"
    with pytest.raises(KeyError, match="nope"):
        fact("gse-one", "nope", root=root)
    with pytest.raises(KeyError, match="no facts file"):
        fact("other", "x", root=root)


def test_stale_facts(tmp_path):
    root = _facts(tmp_path)
    stale = stale_facts(root)
    assert [(s.source, s.recorded, s.current, s.count) for s in stale] == [("gse-one", "0.85.0", "0.86.0", 3)]
    assert stale_facts(_facts(tmp_path / "fresh", current="0.85.0")) == []


def test_validate_reports_stale_facts(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    root = _facts(tmp_path)
    (root / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    monkeypatch.chdir(root)
    r = CliRunner().invoke(cli, ["validate"])
    assert r.exit_code == 1, r.output
    assert "read from 0.85.0, the source is now 0.86.0" in r.output
