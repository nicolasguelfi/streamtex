"""Stage mode: the document in a fixed virtual screen scaled to the window (#105)."""
import sys
import textwrap

import pytest
from click.testing import CliRunner

from streamtex.stage import DEFAULT_STAGE, parse_stage, requested_stage, stage_href, stage_script


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
    assert stage_href({"marker": "intro", "lang": "fr", "stage": "x", "stage_frame": "1"}, (1920, 1080)) == \
        "?marker=intro&lang=fr&stage=1920x1080"


def test_the_stage_script_skips_a_framed_document_and_can_be_left():
    js = stage_script()
    assert "win.self !== win.top" in js and "searchParams.delete('stage')" in js
    assert "searchParams.set('stage_frame', '1')" in js and "frame.src = inside.href" in js
    assert "Exit stage" in js and "exit.href = url.href" in js
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


@pytest.mark.parametrize("arg", ["", "stage=(1280, 720)", "stage=False"])
def test_the_html_export_never_carries_the_stage(deck, tmp_path, arg):
    """0.7.81: the stage is for the live app only (NG, 2026-10-29)."""
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
    assert "stx-stage" not in html and "stxStage" not in html


def test_stx_toml_sets_the_stage_size(tmp_path):
    """34 courses share one stx.toml: [book.defaults] stage = [1280, 720]."""
    from streamtex import book as bm
    (tmp_path / "stx.toml").write_text("[book.defaults]\nstage = [1280, 720]\n")
    assert bm._book_defaults(str(tmp_path)) == {"stage": [1280, 720]}
    assert parse_stage([1280, 720]) == (1280, 720)


def test_a_published_site_gets_the_book_defaults(tmp_path):
    """0.7.81: the snapshot carries [book.defaults] (stage = false never reached a published site)."""
    import subprocess

    from streamtex import book as bm
    from streamtex.release import build
    from streamtex.release.config import load_config
    root = tmp_path / "proj"
    (root / "docs" / "deck").mkdir(parents=True)
    (root / "docs" / "deck" / "book.py").write_text("")
    (root / "stx.toml").write_text(textwrap.dedent("""
        [[packs]]
        name = "secret-pack"
        [release]
        project = "demo"
        [[release.sites]]
        site = "deck"
        book = "docs/deck/book.py"
        [book.defaults]
        stage = false
        zoom = 90
        export_title = "Deck \\"one\\""
    """))
    for cmd in (["init", "-q"], ["add", "."], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True)
    cfg = load_config(root)
    work = tmp_path / "work"
    work.mkdir()
    code = build.snapshot(cfg, cfg.site("deck"), work)
    text = (code / "stx.toml").read_text()
    assert "secret-pack" not in text and "[release]" not in text
    assert bm._book_defaults(str(code / "docs" / "deck")) == {"stage": False, "zoom": 90,
                                                               "export_title": 'Deck "one"'}


def test_no_book_defaults_no_file(tmp_path):
    import subprocess

    from streamtex.release import build
    (tmp_path / "stx.toml").write_text("[release]\nproject = 'demo'\n")
    for cmd in (["init", "-q"], ["add", "."], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"]):
        subprocess.run(["git", "-C", str(tmp_path), *cmd], check=True)
    assert build.book_defaults_toml(tmp_path) is None
