"""stx export html --up-to-slide N (#146): the export stops after the block holding slide N."""
import json
import sys
import textwrap

import pytest
from click.testing import CliRunner

# three blocks: one slide, then two slides, then one — slides 1, 2-3, 4
BLOCKS = {"bck_one": ["s1"], "bck_two": ["s2", "s3"], "bck_three": ["s4"]}


@pytest.fixture
def deck(tmp_path):
    p = tmp_path / "deck"
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    for name, slides in BLOCKS.items():
        body = "".join(f'    stx.st_marker("{s}")\n    stx.st_write("text-{s}", toc_lvl="1")\n'
                       for s in slides)
        (p / "blocks" / f"{name}.py").write_text(f"import streamtex as stx\ndef build(**k):\n{body}")
    (p / "book.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from blocks import bck_one, bck_two, bck_three
        stx.st_book([bck_one, bck_two, bck_three], toc_config=stx.TOCConfig(search=True),
                    marker_config=stx.MarkerConfig(), html_export_mode="both")
    """))
    yield p
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def _export(project, out, *extra):
    from streamtex.cli.export_cmd import export_html
    return CliRunner().invoke(export_html, [str(project), "-o", str(out), *extra])


def _text(out):
    return "\n".join(f.read_text(encoding="utf-8") for f in sorted(out.rglob("*.html")))


@pytest.mark.parametrize("slide,last,entries,kept,dropped", [
    (1, 1, 1, ["s1"], ["s2", "s3", "s4"]),
    (2, 3, 2, ["s1", "s2", "s3"], ["s4"]),        # the block of slide 2 is kept whole
    (3, 3, 2, ["s1", "s2", "s3"], ["s4"]),
    (4, 4, 3, ["s1", "s2", "s3", "s4"], []),
])
def test_the_export_stops_after_the_block_of_the_slide(deck, tmp_path, slide, last, entries, kept, dropped):
    out = tmp_path / "out"
    r = _export(deck, out, "--up-to-slide", str(slide))
    assert r.exit_code == 0, r.output
    assert f"slides 1 to {last}, block(s) 1 to {entries}" in r.output
    text = _text(out)
    for s in kept:
        assert f"text-{s}" in text
    for s in dropped:
        assert f"text-{s}" not in text and f'"{s}"' not in text      # not in the page, nav or search
    limit = json.loads((out / "stx-limit.json").read_text())
    assert limit == {"up_to_slide": slide, "last_slide": last, "entries": entries, "stops": last}


def test_a_limit_past_the_end_keeps_everything(deck, tmp_path):
    out = tmp_path / "out"
    r = _export(deck, out, "--up-to-slide", "40")
    assert r.exit_code == 0, r.output
    assert "the document has 4 slide(s) only" in r.output
    assert "text-s4" in _text(out)


def test_the_page_files_stop_too(deck, tmp_path):
    out = tmp_path / "out"
    assert _export(deck, out, "--up-to-slide", "1").exit_code == 0
    full = tmp_path / "full"
    assert _export(deck, full).exit_code == 0
    assert len(list(out.rglob("pages/*.html"))) < len(list(full.rglob("pages/*.html")))


def test_without_the_option_nothing_changes(deck, tmp_path):
    out = tmp_path / "out"
    r = _export(deck, out)
    assert r.exit_code == 0, r.output
    assert "Limit" not in r.output and not (out / "stx-limit.json").exists()
    assert "text-s4" in _text(out)


def test_the_page_cache_is_not_saved(deck, tmp_path, monkeypatch):
    import streamtex.book as book
    saved = []
    monkeypatch.setattr(book, "_save_file_cache", lambda *a: saved.append(a))
    assert _export(deck, tmp_path / "out", "--up-to-slide", "1").exit_code == 0
    assert saved == []
    assert _export(deck, tmp_path / "full").exit_code == 0
    assert len(saved) == 1


@pytest.mark.parametrize("value", ["0", "-3"])
def test_a_wrong_number_is_refused(deck, tmp_path, value):
    r = _export(deck, tmp_path / "out", "--up-to-slide", value)
    assert r.exit_code == 1 and "--up-to-slide must be a slide number" in r.output


def test_a_document_without_stops_is_refused(tmp_path):
    p = tmp_path / "plain"
    p.mkdir()
    (p / "book.py").write_text(textwrap.dedent("""
        import types
        import streamtex as stx
        m = types.ModuleType("bck_plain")
        m.build = lambda **k: stx.st_write("plain text")
        stx.st_book([m])
    """))
    r = _export(p, tmp_path / "out", "--up-to-slide", "2")
    assert r.exit_code == 1 and "no slide stops" in r.output
    assert not (tmp_path / "out").exists()
