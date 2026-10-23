"""stx export html --zoom / --page-width (#139), and the per-site zoom of stx release."""
import sys
import textwrap

import pytest
from click.testing import CliRunner


@pytest.fixture
def deck(tmp_path):
    p = tmp_path / "deck"
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    for name in ("bck_intro", "bck_end"):
        (p / "blocks" / f"{name}.py").write_text(textwrap.dedent(f"""
            import streamtex as stx
            def build(**k):
                stx.st_marker("{name}")
                stx.st_write("text-{name}", toc_lvl="1")
        """))
    (p / "book.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from blocks import bck_intro, bck_end
        stx.st_book([bck_intro, bck_end], toc_config=stx.TOCConfig(),
                    marker_config=stx.MarkerConfig(), html_export_mode="both")
    """))
    yield p
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def _export(project, out, *extra):
    from streamtex.cli.export_cmd import export_html
    return CliRunner().invoke(export_html, [str(project), "-o", str(out), *extra])


def _files(out):
    return sorted(f for f in out.rglob("*.html"))


def test_zoom_and_page_width_reach_every_file(deck, tmp_path):
    out = tmp_path / "out"
    r = _export(deck, out, "--zoom", "80", "--page-width", "90")
    assert r.exit_code == 0, r.output
    files = _files(out)
    assert len(files) >= 3                                   # continuous + one per page
    for f in files:
        html = f.read_text(encoding="utf-8")
        assert "zoom: 0.8;" in html and "max-width: 90%;" in html, f


def _page_rule(html):
    return html.split(".streamtex-page {", 1)[1].split("}", 1)[0]


def test_without_the_options_the_page_rule_is_unchanged(deck, tmp_path):
    from streamtex.constants import PAGE_WIDTH
    out = tmp_path / "out"
    r = _export(deck, out)
    assert r.exit_code == 0, r.output
    for f in _files(out):
        rule = _page_rule(f.read_text(encoding="utf-8"))
        assert "zoom" not in rule and f"max-width: {PAGE_WIDTH};" in rule, f


@pytest.mark.parametrize("args", [["--zoom", "0"], ["--zoom", "-50"], ["--page-width", "0"], ["--page-width", "120"]])
def test_a_wrong_value_is_refused(deck, tmp_path, args):
    out = tmp_path / "out"
    r = _export(deck, out, *args)
    assert r.exit_code == 1 and "must be" in r.output
    assert not out.exists()


# -- stx release: zoom = 80 in [[release.sites]] -------------------------------------------

def _cfg(tmp_path, extra):
    from streamtex.release.config import load_config
    (tmp_path / "stx.toml").write_text(textwrap.dedent(f"""
        [release]
        project = "p"
        langs = []

        [[release.sites]]
        site = "deck"
        book = "deck/book.py"
        {extra}
    """))
    return load_config(tmp_path)


def test_a_site_zoom_is_read_and_checked(tmp_path):
    from streamtex.release import ReleaseError
    assert _cfg(tmp_path, "").site("deck").zoom is None
    assert _cfg(tmp_path, "zoom = 80").site("deck").zoom == 80.0
    for bad in ("0", "-5", '"80"', "true"):
        with pytest.raises(ReleaseError, match="zoom"):
            _cfg(tmp_path, f"zoom = {bad}")


@pytest.mark.parametrize("extra,expected", [("zoom = 80", ["--zoom", "80"]), ("", [])])
def test_the_html_face_is_exported_with_the_site_zoom(tmp_path, monkeypatch, extra, expected):
    from streamtex.release import build
    cfg = _cfg(tmp_path, extra)
    code, work = tmp_path / "code", tmp_path / "work"
    (code / "deck").mkdir(parents=True)
    seen = []

    class R:
        returncode, stdout, stderr = 0, "", ""

    def fake_run(argv, **kw):
        seen.append(argv)
        out = build.Path(argv[argv.index("--output") + 1]) / "deck"
        out.mkdir(parents=True, exist_ok=True)
        (out / "deck.html").write_text("word " * 200)
        return R()

    monkeypatch.setattr(build.subprocess, "run", fake_run)
    build.export(cfg, cfg.site("deck"), code, work, "rel1")
    argv = seen[0]
    tail = argv[argv.index("--output") + 2:]
    assert tail == [*expected, "."]
