"""stx export html stops when a block raises, unless --keep-going (#134)."""
import sys
import textwrap

import pytest
from click.testing import CliRunner


def _blocks(p, failing):
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    for name in ("bck_intro", "bck_end"):
        (p / "blocks" / f"{name}.py").write_text(textwrap.dedent(f"""
            import streamtex as stx
            def build(**k):
                stx.st_marker("{name}")
                stx.st_write("text-{name}", toc_lvl="1")
        """))
    (p / "blocks" / "bck_outer.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from blocks import bck_inner
        def build(**k):
            stx.st_marker("bck_outer")
            stx.st_write("text-bck_outer", toc_lvl="1")
            stx.st_include(bck_inner)
    """))
    body = 'raise RuntimeError("inner block fails")' if failing else 'pass'
    (p / "blocks" / "bck_inner.py").write_text(textwrap.dedent(f"""
        import streamtex as stx
        def build(**k):
            stx.st_write("before-the-error")
            {body}
    """))
    (p / "book.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from blocks import bck_intro, bck_outer, bck_end
        stx.st_book([bck_intro, bck_outer, bck_end], toc_config=stx.TOCConfig(),
                    marker_config=stx.MarkerConfig(), html_export_mode="continuous")
    """))
    return p


@pytest.fixture
def deck(tmp_path):
    def make(failing=True):
        return _blocks(tmp_path / "deck", failing)
    yield make
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def _export(project, out, *extra):
    from streamtex.cli.export_cmd import export_html
    return CliRunner().invoke(export_html, [str(project), "-o", str(out), *extra])


def test_a_failing_block_stops_the_export(deck, tmp_path):
    out = tmp_path / "out"
    r = _export(deck(), out)
    assert r.exit_code == 1, r.output
    assert "bck_inner" in r.output and "inner block fails" in r.output
    assert "nothing is written" in r.output
    assert not out.exists() or not list(out.rglob("*.html"))


def test_keep_going_writes_the_export_and_lists_the_block(deck, tmp_path):
    out = tmp_path / "out"
    r = _export(deck(), out, "--keep-going")
    assert r.exit_code == 0, r.output
    html = (out / "deck" / "deck.html").read_text()
    assert "text-bck_intro" in html and "text-bck_end" in html
    tail = r.output[r.output.rfind("--keep-going"):]
    assert "1 block(s) left incomplete: blocks.bck_inner" in tail


def test_no_failing_block_exports_as_before(deck, tmp_path):
    out = tmp_path / "out"
    r = _export(deck(failing=False), out)
    assert r.exit_code == 0, r.output
    assert "Error in block" not in r.output and "--keep-going" not in r.output
    assert "before-the-error" in (out / "deck" / "deck.html").read_text()
