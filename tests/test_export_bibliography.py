"""stx export html loads the book's bibliography: citations resolved, list filled."""
import sys
import textwrap

import pytest
from click.testing import CliRunner


@pytest.fixture
def deck(tmp_path):
    p = tmp_path / "deck"
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    (p / "refs.bib").write_text("@book{knuth84, author = {Knuth, Donald}, year = {1984}, title = {The TeXbook}}\n")
    (p / "blocks" / "bck_cite.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from streamtex.bib import cite, st_bibliography
        def build(**k):
            stx.st_marker("cite")
            stx.st_write("As shown " + cite("knuth84"), toc_lvl="1")
            st_bibliography()
    """))
    (p / "book.py").write_text(textwrap.dedent("""
        from pathlib import Path
        import streamtex as stx
        from blocks import bck_cite
        stx.st_book([bck_cite], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(),
                    bib_sources=[str(Path(__file__).parent / "refs.bib")],
                    html_export_mode="continuous")
    """))
    yield p
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def test_the_export_resolves_citations_and_lists_the_references(deck, tmp_path):
    from streamtex.cli.export_cmd import export_html
    out = tmp_path / "out"
    r = CliRunner().invoke(export_html, [str(deck), "-o", str(out)])
    assert r.exit_code == 0, r.output
    html = next(out.rglob("deck.html")).read_text(encoding="utf-8")
    assert "[knuth84?]" not in html
    assert 'id="bib-knuth84"' in html and "The TeXbook" in html
