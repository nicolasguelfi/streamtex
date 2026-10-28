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
         patch("streamtex.export.st_html", side_effect=lambda h: rec.append(("html", h))), \
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
        assert "bottom: 7vh" in n and "opacity: 1.0" in n                  # the 0.7.70 rendering
        assert 'href="?marker=legal-notice" target="_blank"' in n
        assert "© 2026 ACME — participants only" in n and "font-size: 0.75rem" in n
        # under the content (note3), its link clickable through a transparent copy above it
        assert "stx-sn-under" in n and "stx-sn-click" in n

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

    def test_the_app_keeps_its_parameters_while_it_fills_the_export_buffer(self):
        """st_book fills the export buffer while the app renders (all-trainings, 2026-10-28): the link of a
        French reader must stay French; the exported file reads ?marker= and ignores the rest."""
        with patch("streamtex.export.is_export_active", return_value=True), \
             patch("streamlit.query_params") as q:
            q.to_dict.return_value = {"lang": "fr", "ctx": "ul"}
            assert stx.marker_href("legal-notice") == "?lang=fr&ctx=ul&marker=legal-notice"

    def test_without_parameters_the_marker_alone(self):
        with patch("streamlit.query_params") as q:
            q.to_dict.return_value = {}
            assert stx.marker_href("legal-notice") == "?marker=legal-notice"
        with patch("streamlit.query_params") as q:
            q.to_dict.side_effect = RuntimeError("no session")
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
    # each slide: the note under the content, plus its transparent clickable copy
    assert cont.count("NOTE-LINE") == 12 and 'href="?marker=legal"' in cont     # continuous: the file itself
    assert "stx-sn-export" in cont and "isolation: isolate" in cont
    for f in ("bck_intro.html", "bck_rag.html", "bck_legal.html"):
        page = (folder / "pages" / f).read_text()
        assert page.count("NOTE-LINE") == 4 and "stx-sn-export" in page
        assert 'href="../deck.html?marker=legal" target="_blank"' in page and 'href="?marker=' not in page


# ---------------------------------------------------------------------------
# Several notes: place, text per mode, opacity, layer (board note3)
# ---------------------------------------------------------------------------

from streamtex.slide_note import (  # noqa: E402
    SlideNote,
    apply_slide_notes,
    bar_notes_html,
    screen_notes_html,
    slide_notes_html,
)


@pytest.fixture
def clean():
    stx.set_slide_notes()
    yield
    stx.set_slide_notes()


class TestSlideNote:
    def test_validation(self):
        with pytest.raises(ValueError, match="place="):
            SlideNote("x", place="middle")
        with pytest.raises(ValueError, match="opacity"):
            SlideNote("x", opacity=2)
        with pytest.raises(ValueError, match="layer="):
            SlideNote("x", layer="top")
        with pytest.raises(ValueError, match="unknown mode"):
            SlideNote({"slides": "a", "tablet": "b"})
        with pytest.raises(TypeError):
            SlideNote("")
        with pytest.raises(TypeError):
            stx.set_slide_notes("plain text")

    def test_text_per_mode_falls_back_on_default(self):
        n = SlideNote({"slides": "S", "html": {"fr": "H-fr", "en": "H-en"}, "phone": None, "default": "D"})
        assert n.text_for("slides") == "S" and n.text_for("document") == "D"
        assert n.text_for("phone") is None
        with patch("streamtex.i18n.current_lang", return_value="fr"):
            assert n.text_for("html") == "H-fr"
        assert SlideNote({"fr": "lang leaf"}).text_for("html") == "lang leaf"   # a leaf, not modes

    def test_defaults_by_place(self):
        assert SlideNote("x", place="across").look[1] == 0.08
        assert SlideNote("x", place="screen-left").look[1] == 0.7
        assert SlideNote("x", opacity=0.3).look[1] == 0.3


class TestPlaces:
    def test_slide_places_around_the_box(self, clean):
        stx.set_slide_notes(SlideNote("UP", place="above"), SlideNote("SIDE", place="left"),
                            SlideNote("MARK", place="across"), SlideNote("SCREEN", place="screen-top"))
        h = slide_notes_html(foot=True)
        assert "UP" in h and "bottom: 91vh" in h
        assert "SIDE" in h and "writing-mode: vertical-rl" in h
        assert "MARK" in h and "rotate(-30deg)" in h and "opacity: 0.08" in h
        assert "SCREEN" not in h                                    # drawn once, not per slide
        lines = slide_notes_html(foot=False)                        # box=False / st_slide_note
        assert "position" not in lines and "UP" in lines

    def test_screen_notes_fixed_and_layered(self, clean):
        stx.set_slide_notes(SlideNote("UNDER", place="screen-bottom", link="legal"),
                            SlideNote("OVER", place="screen-right", layer="over"))
        h = screen_notes_html()
        assert h.count("position: fixed") == 3                      # under + its clickable copy + over
        assert "stx-sn-under" in h and "stx-sn-click" in h and "stx-sn-over" in h
        assert "var(--stx-sn-bottom" in h                           # above the presentation bar

    def test_text_per_mode_gives_one_span_per_target(self, clean):
        stx.set_slide_notes(SlideNote({"slides": "APP", "html": "HTML", "phone": "PH"}, place="below"))
        h = slide_notes_html(foot=True)
        assert '<span class="stx-sn-app">APP</span>' in h
        assert '<span class="stx-sn-html">HTML</span>' in h and '<span class="stx-sn-phone">PH</span>' in h

    def test_bar_places(self, clean):
        stx.set_slide_notes(SlideNote("BEFORE", place="bar-before-counter"),
                            SlideNote("INSTEAD", place="bar-title"))
        assert "BEFORE" in bar_notes_html("bar-before-counter") and bar_notes_html("bar-after-title") == ""
        from streamtex.presentation import PresentationConfig, st_presentation_footer
        rec = []
        with patch("streamtex.presentation._render", side_effect=rec.append):
            st_presentation_footer(3, 9, title="Deck", config=PresentationConfig(footer=True))
        bar = rec[-1]
        assert "INSTEAD" in bar and "Deck" not in bar
        assert bar.index("BEFORE") < bar.index("3 / 9")

    def test_export_carries_rules_and_screen_notes(self, clean):
        assert apply_slide_notes("<html><body>x</body></html>") == "<html><body>x</body></html>"
        stx.set_slide_notes(SlideNote("FIX", place="screen-top"))
        out = apply_slide_notes("<html><body>x</body></html>")
        assert out.index("FIX") < out.index("</body>") and ".stx-sn-html { display: inline" in out


# ---------------------------------------------------------------------------
# Downloads, the pdf mode, new lines (board note5)
# ---------------------------------------------------------------------------

from streamtex.slide_note import has_choice  # noqa: E402


class TestDownloads:
    def test_validation_and_default(self):
        assert SlideNote("x").downloads == "always"
        with pytest.raises(ValueError, match="downloads="):
            SlideNote("x", downloads="sometimes")

    def test_pdf_text_falls_back_on_html_then_default(self):
        assert SlideNote({"html": "H", "pdf": "P"}).text_for("pdf") == "P"
        assert SlideNote({"html": "H", "default": "D"}).text_for("pdf") == "H"
        assert SlideNote({"slides": "S", "default": "D"}).text_for("pdf") == "D"

    def test_a_new_line_in_a_text(self, clean):
        stx.set_slide_notes(SlideNote("ONE\nTWO", place="across"))
        assert "ONE<br>TWO" in slide_notes_html(foot=True)

    def test_notes_carry_their_number(self, clean):
        stx.set_slide_notes(SlideNote("A"), SlideNote("B", place="screen-top"))
        assert 'data-stx-note="0"' in slide_notes_html(foot=True)
        assert 'data-stx-note="1"' in screen_notes_html()

    def test_published_html_keeps_every_note(self, clean):
        stx.set_slide_notes(SlideNote("MARK", place="across", downloads="never"))
        out = apply_slide_notes("<body>x</body>")
        assert 'data-stx-note="0"] { display: none' not in out

    def test_download_leaves_out_never_and_unticked_choice(self, clean):
        stx.set_slide_notes(SlideNote("KEEP"), SlideNote("NEVER", downloads="never"),
                            SlideNote("CHOICE", place="across", downloads="choice"))
        assert has_choice()
        kept = apply_slide_notes("<body>x</body>", download=True, chosen=True)
        assert '[data-stx-note="1"] { display: none' in kept and 'data-stx-note="2"] { display' not in kept
        assert 'data-stx-note="0"] { display' not in kept
        dropped = apply_slide_notes("<body>x</body>", download=True, chosen=False)
        assert '[data-stx-note="2"] { display: none' in dropped

    def test_pdf_shows_the_pdf_texts(self, clean):
        stx.set_slide_notes(SlideNote({"html": "H", "pdf": "P"}))
        assert '<span class="stx-sn-pdf">P</span>' in slide_notes_html(foot=True)
        pdf = apply_slide_notes("<body>x</body>", pdf=True)
        assert pdf.rfind(".stx-sn-pdf { display: inline") > pdf.rfind(".stx-sn-html { display: inline")
        assert not has_choice()
