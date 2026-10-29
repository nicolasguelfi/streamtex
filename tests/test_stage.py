"""Stage mode: the document in a fixed virtual screen scaled to the window (#105)."""
import sys
import textwrap

import pytest
from click.testing import CliRunner

from streamtex.export_enrich import enrich_export_html
from streamtex.stage import DEFAULT_STAGE, export_stage_js, parse_stage, requested_stage, stage_href


@pytest.mark.parametrize("value, size", [
    ((1920, 1080), (1920, 1080)), ([1280, 720], (1280, 720)), ("3840x2160", (3840, 2160)),
    ("1024×768", (1024, 768)), (True, DEFAULT_STAGE), (False, None), (None, None)])
def test_parse_stage(value, size):
    assert parse_stage(value) == size


@pytest.mark.parametrize("value", ["big", (1920,), "50x50", (1920, 99999), 1920])
def test_parse_stage_refuses(value):
    with pytest.raises(ValueError, match="stage"):
        parse_stage(value)


def test_the_url_asks_for_the_stage():
    assert requested_stage({}, DEFAULT_STAGE) is None
    assert requested_stage({"stage": "1280x720"}, DEFAULT_STAGE) == (1280, 720)
    assert requested_stage({"stage": "1"}, (1600, 900)) == (1600, 900)    # the document's size
    assert requested_stage({"stage": "1280x720"}, None) is None            # stage=False: off


def test_the_link_keeps_the_other_parameters():
    assert stage_href({"marker": "intro", "lang": "fr", "stage": "x"}, (1920, 1080)) == \
        "?marker=intro&lang=fr&stage=1920x1080"


RAW = "<html><head><title>d</title><style></style></head><body><h1 id='a'>A</h1></body></html>"
TOC = [{"level": 1, "title": "A", "key_anchor": "a", "page_idx": 0}]


def test_the_export_sidebar_gets_the_link_and_the_script():
    html = enrich_export_html(RAW, toc=TOC, stage=(1280, 720))
    assert '<a id="stx-stage-link" class="stx-stage-link" href="?stage=1280x720" target="_blank"' in html
    assert ">Stage 1280×720</a>" in html
    assert "function stxStage(win, w, h)" in html and "var W = 1280, H = 720;" in html


def test_no_stage_no_link():
    html = enrich_export_html(RAW, toc=TOC)
    assert 'id="stx-stage-link"' not in html and "stxStage" not in html


def test_the_stage_script_skips_a_framed_document():
    js = export_stage_js((1920, 1080))
    assert "win.self !== win.top" in js and "searchParams.delete('stage')" in js
    assert "requestFullscreen" in js and "frame.contentWindow.focus()" in js


@pytest.fixture
def deck(tmp_path):
    p = tmp_path / "deck"
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    (p / "blocks" / "bck_one.py").write_text(textwrap.dedent("""
        import streamtex as stx
        def build(**k):
            stx.st_write("One", toc_lvl="1")
    """))
    yield p
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


@pytest.mark.parametrize("arg, link", [("", "Stage 1920×1080"), ("stage=(1280, 720)", "Stage 1280×720"),
                                       ("stage=False", None)])
def test_the_export_follows_st_book_stage(deck, tmp_path, arg, link):
    from streamtex.cli.export_cmd import export_html
    (deck / "book.py").write_text(textwrap.dedent(f"""
        import streamtex as stx
        from blocks import bck_one
        stx.st_book([bck_one], toc_config=stx.TOCConfig(), {arg})
    """))
    out = tmp_path / "out"
    r = CliRunner().invoke(export_html, [str(deck), "-o", str(out)])
    assert r.exit_code == 0, r.output
    html = next(out.rglob("deck.html")).read_text(encoding="utf-8")
    assert (link in html) if link else ('id="stx-stage-link"' not in html)


def test_stx_toml_sets_the_stage_size(tmp_path):
    """34 courses share one stx.toml: [book.defaults] stage = [1280, 720]."""
    from streamtex import book as bm
    (tmp_path / "stx.toml").write_text("[book.defaults]\nstage = [1280, 720]\n")
    assert bm._book_defaults(str(tmp_path)) == {"stage": [1280, 720]}
    assert parse_stage([1280, 720]) == (1280, 720)
