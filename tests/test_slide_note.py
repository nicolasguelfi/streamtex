"""set_slide_note: a note at the foot of every st_slide, per session, and its link in every export (board note1)."""

import contextlib
import sys
import textwrap
from unittest.mock import patch

import pytest
from click.testing import CliRunner

import streamtex as stx
import streamtex.marker as mk
import streamtex.toc as toc_mod
from streamtex.export_paginate import to_entry_links
from streamtex.marker import MarkerConfig, reset_marker_registry
from streamtex.slide import st_slide
from streamtex.styles import Style
from streamtex.toc import TOCConfig, reset_toc_registry


@pytest.fixture
def out():
    toc_mod.toc = None
    mk._registry = None
    reset_toc_registry(TOCConfig())
    reset_marker_registry(MarkerConfig())
    rec = []

    @contextlib.contextmanager
    def fake_block(style):
        rec.append(("box", str(style)))
        yield

    with patch("streamtex.slide._render", side_effect=lambda h: rec.append(("html", h))), \
         patch("streamtex.marker._render", side_effect=lambda h: rec.append(("marker", h))), \
         patch("streamtex.space._render", side_effect=lambda h: rec.append(("space", h))), \
         patch("streamtex.container.st_block", fake_block), \
         patch("streamlit.session_state", {}):
        try:
            yield rec
        finally:
            stx.set_slide_note(None)
    mk._registry = None
    toc_mod.toc = None


def _notes(rec):
    return [h for kind, h in rec if kind == "html" and "stx-slide-note" in h]


class TestNote:
    def test_no_note_by_default(self, out):
        with st_slide():
            out.append(("content", ""))
        assert _notes(out) == [] and out[-1] == ("content", "")

    def test_text_note_closes_every_slide_in_the_bottom_margin(self, out):
        stx.set_slide_note("© 2026 ACME — participants only", link="legal-notice")
        with st_slide():
            out.append(("content", ""))
        with st_slide(cut=True):
            out.append(("content", ""))
        notes = _notes(out)
        assert len(notes) == 2 and out[-1][0] == "html" and out[2][1] == notes[0]
        n = notes[0]
        assert "stx-slide-note-foot" in n and "height: 0" in n            # no height added (p1)
        assert 'href="?marker=legal-notice" target="_blank"' in n
        assert "© 2026 ACME — participants only" in n and "font-size: 0.75rem" in n

    def test_box_false_puts_the_note_after_the_content(self, out):
        stx.set_slide_note("note")
        with st_slide(box=False):
            out.append(("content", ""))
        assert out[-2] == ("content", "") and "stx-slide-note-foot" not in out[-1][1]
        assert "<a " not in out[-1][1]                                     # no link= : plain text

    def test_language_leaf_style_and_escaping(self, out):
        stx.set_slide_note({"en": "for <participants>", "fr": "pour les participants"},
                           style=Style("color: red;", "red"))
        with patch("streamtex.i18n.current_lang", return_value="en"):
            stx.st_slide_note()
        assert "for &lt;participants&gt;" in out[-1][1] and "color: red;" in out[-1][1]
        with patch("streamtex.i18n.current_lang", return_value="fr"):
            stx.st_slide_note()
        assert "pour les participants" in out[-1][1]

    def test_a_function_draws_its_own_note(self, out):
        stx.set_slide_note(lambda: out.append(("mine", "")))
        with st_slide():
            pass
        assert out[-1] == ("mine", "")

    def test_wrong_arguments(self, out):
        with pytest.raises(ValueError, match="function draws"):
            stx.set_slide_note(lambda: None, link="x")
        with pytest.raises(ValueError, match="need a note"):
            stx.set_slide_note(link="x")
        with pytest.raises(TypeError):
            stx.set_slide_note(42)

    def test_st_slide_note_without_note_draws_nothing(self, out):
        stx.st_slide_note()
        assert out == []


SCRIPT = textwrap.dedent("""
    import streamlit as st
    import streamtex as stx
    which = st.query_params.get("w", "a")
    if not st.session_state.get("_set"):
        stx.set_slide_note("note-" + which)
        st.session_state["_set"] = True
    st.text(stx.get_slide_note().text)
""")


def test_two_sessions_keep_their_own_note():
    from streamlit.testing.v1 import AppTest
    a = AppTest.from_string(SCRIPT)
    a.query_params["w"] = "a"
    a.run()
    b = AppTest.from_string(SCRIPT)
    b.query_params["w"] = "b"
    b.run()
    a.run()
    assert a.text[0].value == "note-a" and b.text[0].value == "note-b"
    assert stx.get_slide_note() is None                # the process-wide value is untouched


class TestMarkerHref:
    def test_keeps_the_app_parameters(self):
        with patch("streamlit.query_params") as q:
            q.to_dict.return_value = {"lang": "fr", "marker": "old", "page": "3"}
            assert stx.marker_href("legal-notice") == "?lang=fr&marker=legal-notice"

    def test_in_an_export_the_marker_alone(self):
        with patch("streamtex.export.is_export_active", return_value=True):
            assert stx.marker_href("legal-notice") == "?marker=legal-notice"


class TestEntryLinks:
    def test_deep_links_go_to_the_entry_file(self):
        html = ('<a href="?marker=legal-notice" target="_blank">x</a> <a href="?lang=fr&amp;slide=3">y</a>'
                ' <a href="bck_intro.html#m1">z</a> <a href="?page=2#top">p</a> <a href="?q=1">q</a>')
        out = to_entry_links(html, "../deck.html")
        assert 'href="../deck.html?marker=legal-notice"' in out
        assert 'href="../deck.html?lang=fr&amp;slide=3"' in out
        assert 'href="../deck.html?page=2#top"' in out
        assert 'href="bck_intro.html#m1"' in out and 'href="?q=1"' in out


@pytest.fixture
def note_project(tmp_path):
    p = tmp_path / "deck"
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    for name in ("bck_intro", "bck_rag", "bck_legal"):
        (p / "blocks" / f"{name}.py").write_text(textwrap.dedent(f"""
            import streamtex as stx
            def build(**k):
                with stx.st_slide(marker="{name}", key="{name.replace('bck_', '')}"):
                    stx.st_write("text-{name}", toc_lvl="1")
                with stx.st_slide(cut=True):
                    stx.st_write("more-{name}")
        """))
    (p / "book.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from blocks import bck_intro, bck_rag, bck_legal
        stx.set_slide_note("NOTE-LINE", link="legal")
        stx.st_book([bck_intro, bck_rag, bck_legal], toc_config=stx.TOCConfig(),
                    marker_config=stx.MarkerConfig(), paginate=True, html_export_mode="both")
    """))
    yield p
    stx.set_slide_note(None)
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def test_export_every_slide_carries_the_note_and_its_link(note_project, tmp_path):
    from streamtex.cli.export_cmd import export_html
    out = tmp_path / "out"
    r = CliRunner().invoke(export_html, [str(note_project), "-o", str(out)])
    assert r.exit_code == 0, r.output
    folder = out / "deck"
    cont = (folder / "deck.html").read_text()
    assert cont.count("NOTE-LINE") == 6 and 'href="?marker=legal"' in cont      # continuous: the file itself
    for f in ("bck_intro.html", "bck_rag.html", "bck_legal.html"):
        page = (folder / "pages" / f).read_text()
        assert page.count("NOTE-LINE") == 2
        assert 'href="../deck.html?marker=legal" target="_blank"' in page and 'href="?marker=' not in page
