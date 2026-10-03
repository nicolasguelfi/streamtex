"""Lot D — writing slides: st_slide (L4), image bounds and placement (L5, L6),
the lecture-hall scale preset (L3), the language helpers (L1)."""

import os
from unittest.mock import patch

import pytest

import streamtex as stx
from streamtex import i18n
from streamtex.image import st_image
from streamtex.styles import Style


def _capture(captured):
    def _fake(html, **_kw):
        captured.append(html)
    return _fake


def _png(path, w, h):
    from PIL import Image

    Image.new("RGB", (w, h), (200, 100, 50)).save(path)
    return str(path)


# --- L3 ---------------------------------------------------------------------

def test_scale_amphi_preset_and_override():
    a = stx.ScaleConfig.amphi()
    assert (a.base_pt_desktop, a.tablet_scale, a.mobile_scale) == (30, 0.70, 0.55)
    b = stx.ScaleConfig.amphi(base_pt_desktop=28)
    assert b.base_pt_desktop == 28 and b.mobile_scale == 0.55
    assert stx.ScaleConfig.amphi() == stx.ScaleConfig(base_pt_desktop=30, tablet_scale=0.7, mobile_scale=0.55)


# --- L4 ---------------------------------------------------------------------

def test_st_slide_writes_exactly_break_then_container():
    calls = []
    import contextlib

    @contextlib.contextmanager
    def fake_block(style):
        calls.append(("block", str(style)))
        yield

    with patch("streamtex.slide.st_slide_break", lambda: calls.append(("break",))), \
         patch("streamtex.container.st_block", fake_block):
        with stx.st_slide():
            calls.append(("content",))
        with stx.st_slide(cut=True, style=Style("min-height: 60vh;", "short")):
            calls.append(("content",))
    box = str(stx.SLIDE_CONTAINER)
    assert calls[0] == ("block", box)
    assert calls[1] == ("content",)
    assert calls[2] == ("break",)
    assert calls[3][0] == "block" and box in calls[3][1] and "min-height: 60vh;" in calls[3][1]


def test_set_slide_container():
    mine = Style("min-height: 70vh;", "mine")
    try:
        stx.set_slide_container(mine)
        assert stx.get_slide_container() is mine
    finally:
        stx.set_slide_container(None)
    assert stx.get_slide_container() is stx.SLIDE_CONTAINER


# --- L5 ---------------------------------------------------------------------

def test_image_without_new_params_is_byte_identical(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(uri="https://example.com/a.png", width="300px", alt="x")
    assert captured == ['<img src="https://example.com/a.png" alt="x" style=" width: 300px; height: auto;">']


def test_image_bounds_use_the_natural_ratio(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    uri = _png(tmp_path / "wide.png", 200, 100)          # ratio 2
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(uri="./wide.png", max_vw=80, max_vh=40)
        st_image(uri="./wide.png", max_vh=50, natural_size=(300, 100))   # explicit ratio 3
    assert "width: min(100%, 80vw, calc(40vh * 2.000000)); height: auto;" in captured[0]
    assert "width: min(100%, calc(50vh * 3.000000)); height: auto;" in captured[1]
    assert os.path.isfile(uri)


def test_image_bounds_without_natural_size_fall_back_to_css_limits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(uri="https://example.com/a.png", max_vw=50, max_vh=30)
    assert "width: auto; height: auto; max-width: min(100%, 50vw); max-height: 30vh;" in captured[0]


def test_image_bounds_follow_the_cropped_zone(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _png(tmp_path / "tall.png", 100, 200)
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(uri="./tall.png", max_vh=50, crop=(0, 0, 50, 0))   # visible 100x100 -> ratio 1
    assert "calc(50vh * 1.000000)" in captured[0]


@pytest.mark.parametrize("kwargs, msg", [
    ({"max_vh": 0}, "positive"),
    ({"max_vw": -5}, "positive"),
    ({"max_vh": 40, "height": "300px"}, "incompatible"),
    ({"align": "middle"}, "align="),
])
def test_image_bound_and_align_validation(kwargs, msg, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("streamtex.image._render"), pytest.raises(ValueError, match=msg):
        st_image(uri="https://example.com/a.png", **kwargs)


# --- L6 ---------------------------------------------------------------------

def test_align_places_the_image_and_style_text_align_stays_a_no_op(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(Style("text-align: center;", "c"), uri="https://example.com/a.png", width="50%")
        st_image(uri="https://example.com/a.png", width="50%", align="right")
    assert "stx-image-align" not in captured[0]           # unchanged: no inferred placement
    assert captured[1].startswith('<div class="stx-image-align" style="text-align: right; width: 100%; line-height: 0;">')


# --- L1 ---------------------------------------------------------------------

@pytest.fixture
def langs():
    i18n.set_languages(("en", "fr"), "en")
    yield
    i18n.set_languages(("en", "fr"), "en")


def test_T_fallbacks_and_strict(langs, monkeypatch):
    monkeypatch.delenv("STX_LANG", raising=False)
    leaf = {"en": "Hello", "fr": "Bonjour", "de": ""}
    assert i18n.T(leaf, "fr") == "Bonjour"
    assert i18n.T({"en": "Hello"}, "fr") == "Hello"           # missing -> default language
    assert i18n.T({"fr": "Bonjour"}, "en") == "Bonjour"       # no default -> first value
    i18n.set_languages(("en", "fr", "de"))
    assert i18n.T(leaf, "de") == ""                            # empty is a value, not a hole
    assert i18n.T("raw") == "raw"
    with pytest.raises(TypeError):
        i18n.T("raw", strict=True)
    assert i18n.TF({"en": ("a ", ("S", "b"))}, "en") == ("a ", ("S", "b"))
    assert i18n.TF({"en": "one"}, "en") == ("one",)


def test_current_lang_order(langs, monkeypatch):
    monkeypatch.delenv("STX_LANG", raising=False)
    assert i18n.current_lang() == "en"
    assert i18n.current_lang(default="fr") == "fr"
    monkeypatch.setenv("STX_LANG", "fr")
    assert i18n.current_lang() == "fr"
    monkeypatch.setenv("STX_LANG", "xx")
    with pytest.raises(ValueError):
        i18n.current_lang()


def test_with_lang_and_set_languages(langs):
    assert i18n.with_lang("http://h/x", "fr") == "http://h/x?lang=fr"
    assert i18n.with_lang("http://h/x?a=1", "fr") == "http://h/x?a=1&lang=fr"
    # an existing lang= is replaced, not repeated; the #fragment stays last
    assert i18n.with_lang("http://h/x?lang=en&a=1", "fr") == "http://h/x?a=1&lang=fr"
    assert i18n.with_lang("http://h/x#sec", "fr") == "http://h/x?lang=fr#sec"
    with pytest.raises(ValueError):
        i18n.set_languages(("en",), "fr")


def test_i18n_names_stay_out_of_the_star_import():
    ns = {}
    exec("from streamtex import *", ns)  # noqa: S102
    for name in ("T", "TF", "current_lang", "with_lang", "set_languages"):
        assert name not in ns


def test_st_book_lang_reaches_every_block(tmp_path, monkeypatch):
    """lang="auto" resolves $STX_LANG and hands it to build(); block_kwargs wins."""
    import textwrap

    from streamtex.cli.build_check import run_book

    (tmp_path / "blocks").mkdir()
    (tmp_path / "blocks" / "__init__.py").write_text("")
    out = tmp_path / "seen.txt"
    (tmp_path / "blocks" / "bck_a.py").write_text(textwrap.dedent(f"""
        def build(lang="?", x=None, **_):
            open({str(out)!r}, "a").write(f"{{lang}}:{{x}}\\n")
    """))
    (tmp_path / "book.py").write_text(textwrap.dedent("""
        from streamtex import st_book
        import blocks.bck_a as a
        st_book([a], lang="auto", block_kwargs={"x": 1})
        st_book([a], lang="auto", block_kwargs={"lang": "en"})
    """))
    monkeypatch.setenv("STX_LANG", "fr")
    r = run_book(tmp_path / "book.py", timeout=60)
    assert r.book_error is None and not r.errors, (r.book_error, r.errors)
    assert out.read_text().splitlines() == ["fr:1", "en:None"]


def test_real_st_book_resolves_lang_before_anything_else(monkeypatch, langs):
    """The real st_book: lang= becomes block_kwargs["lang"] (warmup path observes it)."""
    import types

    import streamtex.book as book

    monkeypatch.delenv("STX_LANG", raising=False)
    seen = []
    monkeypatch.setattr(book, "_warmup_mode", True)
    monkeypatch.setattr(book, "_warmup_build_cache",
                        lambda *a, block_args=(), block_kwargs=None, **k: seen.append(block_kwargs))
    blk = types.ModuleType("b")
    book.st_book([blk], lang="fr", block_kwargs={"x": 1}, export=False, loading=False)
    book.st_book([blk], lang="auto", block_kwargs={"lang": "en"}, export=False, loading=False)
    book.st_book([blk], export=False, loading=False)
    assert seen == [{"lang": "fr", "x": 1}, {"lang": "en"}, {}]
