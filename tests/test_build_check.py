"""``stx validate --build`` and the other lot-B checks (#75, #76, #79, #80)."""

import textwrap
from pathlib import Path

from click.testing import CliRunner

from streamtex.cli.build_check import (
    INLINE_LIMIT_BYTES,
    block_fingerprints,
    discover_books,
    empty_styled_blocks,
    normalize_auto_numbers,
    run_book,
)
from streamtex.cli.commands import cli
from streamtex.cli.project_rules import check_rules, local_copies_of_public_api


def _project(tmp_path: Path) -> Path:
    """A tiny one-book project: a good block, a raising block, a missing and a huge image."""
    p = tmp_path / "proj"
    (p / "blocks").mkdir(parents=True)
    (p / "static" / "images").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    (p / "blocks" / "bck_good.py").write_text(textwrap.dedent("""
        from streamtex import st_write, st_marker
        def build(lang="en", **_):
            st_marker("good")
            st_write("hello " + lang)
    """))
    (p / "blocks" / "bck_boom.py").write_text(textwrap.dedent("""
        def build(**_):
            raise NameError("name 'null' is not defined")
    """))
    (p / "blocks" / "bck_media.py").write_text(textwrap.dedent("""
        from streamtex import st_image, st_block
        from streamtex.styles import Style
        def build(**_):
            st_image(uri="images/nope.png")
            st_image(uri="images/huge.png")
            with st_block(Style("color: red;", "red_box")):
                pass
    """))
    # a "PNG" larger than the inline limit (content does not matter for the check)
    (p / "static" / "images" / "huge.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * (INLINE_LIMIT_BYTES + 1024))
    (p / "book.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from streamtex import st_book
        import blocks.bck_good as g, blocks.bck_boom as b, blocks.bck_media as m
        stx.set_static_sources(["static"])
        st_book([g, b, m], block_kwargs={"lang": "fr"})
    """))
    return p


def test_discover_books(tmp_path):
    p = _project(tmp_path)
    (p / "modules" / "m1").mkdir(parents=True)
    (p / "modules" / "m1" / "book.py").write_text("")
    (p / ".venv" / "lib").mkdir(parents=True)
    (p / ".venv" / "lib" / "book.py").write_text("")
    books = [b.relative_to(p).as_posix() for b in discover_books(p)]
    assert books == ["book.py", "modules/m1/book.py"]


def test_run_book_reports_errors_missing_and_inlined_media(tmp_path):
    p = _project(tmp_path)
    r = run_book(p / "book.py", timeout=120)
    assert r.book_error is None, r.book_error
    assert r.blocks == 3
    assert [(e[0], e[1]) for e in r.errors] == [("blocks.bck_boom", "NameError")]
    assert [m[1] for m in r.missing_media] == ["images/nope.png"]
    assert [m[1] for m in r.inlined_media] == ["images/huge.png"]
    assert r.inlined_media[0][2] > INLINE_LIMIT_BYTES


def test_run_book_reports_a_book_that_does_not_load(tmp_path):
    p = tmp_path / "broken"
    p.mkdir()
    (p / "book.py").write_text("import does_not_exist\n")
    r = run_book(p / "book.py", timeout=60)
    assert r.book_error and "does_not_exist" in r.book_error


def _snapshot_project(tmp_path: Path, *, intro: bool, md_text: str, numbering: str = "none") -> Path:
    """Two books in one: an optional first block, then a section block with Markdown text."""
    p = tmp_path / ("with" if intro else "without")
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    (p / "blocks" / "bck_intro.py").write_text(textwrap.dedent("""
        from streamtex import st_write
        def build(**_):
            st_write("intro", toc_lvl="1")
    """))
    (p / "blocks" / "bck_section.py").write_text(textwrap.dedent(f"""
        from streamtex import st_write, st_marker
        from streamtex.markdown import st_markdown
        def build(**_):
            st_marker("section")
            st_write("Section", toc_lvl="1")
            st_markdown({md_text!r})
    """))
    mods = "i, s" if intro else "s"
    (p / "book.py").write_text(textwrap.dedent(f"""
        from streamtex import st_book, TOCConfig
        import blocks.bck_intro as i, blocks.bck_section as s
        st_book([{mods}], toc_config=TOCConfig(numbering={numbering!r}))
    """))
    return p


def test_snapshot_sees_markdown_text_and_ignores_position_numbers(tmp_path):
    base = block_fingerprints(run_book(_snapshot_project(tmp_path / "a", intro=False, md_text="Old text.") / "book.py",
                                       timeout=120, capture=True))
    moved = block_fingerprints(run_book(_snapshot_project(tmp_path / "b", intro=True, md_text="Old text.") / "book.py",
                                        timeout=120, capture=True))
    edited = block_fingerprints(run_book(_snapshot_project(tmp_path / "c", intro=False, md_text="New text.") / "book.py",
                                         timeout=120, capture=True))
    key = "blocks.bck_section"
    assert key in base and key in moved and key in edited
    assert moved[key] == base[key]      # a block inserted before it shifts anchors, not content
    assert edited[key] != base[key]     # a changed Markdown text is seen
    # with visible section numbers, the shift IS on screen ("1 Section" -> "2 Section"): reported
    shown = [block_fingerprints(run_book(_snapshot_project(tmp_path / f"n{i}", intro=intro, md_text="Old text.",
                                                           numbering="both") / "book.py",
                                         timeout=120, capture=True))[key]
             for i, intro in enumerate((False, True))]
    assert shown[0] != shown[1]


def test_normalize_auto_numbers_keeps_visible_text():
    html = ("<div id='42-1-faq'><a href=\"#42-faq\">Chapter 42</a>"
            "<div id=\"stx-marker-phase2-26\" data-marker-index=\"26\"></div>"
            "<input id=\"stx-wrap-stx-wrap-1026\"></div>")
    assert normalize_auto_numbers(html) == (
        "<div id='N-faq'><a href=\"#N-faq\">Chapter 42</a>"
        "<div id=\"stx-marker-phase2-N\" data-marker-index=\"N\"></div>"
        "<input id=\"stx-wrap-stx-wrap-N\"></div>")


def test_empty_styled_block_static_check(tmp_path):
    p = _project(tmp_path)
    found = empty_styled_blocks(p)
    assert found == [("blocks/bck_media.py", 7)]


def test_validate_build_cli(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    p = _project(tmp_path)
    (p / "stx.toml").write_text('[project]\nname = "p"\n')
    (p / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    monkeypatch.chdir(p)
    r = CliRunner().invoke(cli, ["validate", "--build", "--timeout", "120"])
    assert r.exit_code == 2, r.output                     # an error (the raising block)
    assert "bck_boom: NameError" in r.output
    assert "media not found: images/nope.png" in r.output
    assert "inlined" in r.output and "huge.png" in r.output
    assert "empty styled st_block" in r.output


def test_project_rules(tmp_path):
    p = tmp_path
    (p / "content").mkdir()
    (p / "content" / "bck_a.py").write_text("COLOR = '#ff00aa'\nst_marker('a')\n")
    (p / "content" / "bck_b.py").write_text("x = 1\n")
    (p / "seq.toml").write_text('[[block]]\norder = 3\n')
    rules = [
        {"id": "no-hex", "glob": "content/**/*.py", "forbid": r"#[0-9a-fA-F]{6}\b"},
        {"id": "marker", "glob": "content/*.py", "require": r"st_marker\(", "severity": "warning"},
        {"id": "V21", "glob": "*.toml", "forbid": r"^\s*order\s*="},
        {"id": "script-ok", "run": "python -c 'import sys; sys.exit(0)'"},
        {"id": "script-ko", "run": "python -c 'import sys; print(\"3 invariants fail\"); sys.exit(1)'"},
        {"id": "bad", "glob": "x"},
    ]
    vs = check_rules(p, rules)
    got = sorted((v.rule, v.severity, v.where) for v in vs)
    assert ("no-hex", "error", "content/bck_a.py:1") in got
    assert ("marker", "warning", "content/bck_b.py") in got
    assert ("V21", "error", "seq.toml:2") in got
    assert any(v.rule == "script-ko" and "3 invariants fail" in v.message for v in vs)
    assert not any(v.rule == "script-ok" for v in vs)
    assert any(v.rule == "bad" and "forbid" in v.message for v in vs)


def test_validate_runs_declared_rules(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    (tmp_path / "stx.toml").write_text(textwrap.dedent('''
        [project]
        name = "p"
        [[validate.rules]]
        id = "no-hex"
        message = "the colour is a role"
        glob = "*.py"
        forbid = '#[0-9a-fA-F]{6}'
    '''))
    (tmp_path / "bck.py").write_text("c = '#123456'\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(cli, ["validate"])
    assert r.exit_code == 2 and "no-hex: 1 violation(s)" in r.output and "bck.py:1" in r.output


def test_validate_shows_the_violation_of_a_rule_without_id(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    (tmp_path / "stx.toml").write_text(textwrap.dedent('''
        [project]
        name = "p"
        [[validate.rules]]
        glob = "*.py"
        forbid = '#[0-9a-fA-F]{6}'
    '''))
    (tmp_path / "bck.py").write_text("c = '#123456'\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(cli, ["validate"])
    assert r.exit_code == 2 and "rule-1: 1 violation(s)" in r.output and ": OK" not in r.output


def test_local_copies_of_public_api_are_reported_not_counted(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    (tmp_path / "shared").mkdir()
    (tmp_path / "shared" / "widgets.py").write_text("def st_hover_tooltip(x):\n    return x\n"
                                                    "def my_helper():\n    pass\n")
    assert local_copies_of_public_api(tmp_path) == [("shared/widgets.py", 1, "st_hover_tooltip")]
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n')
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(cli, ["validate"])
    assert r.exit_code == 0, r.output                   # information only
    assert "defines st_hover_tooltip" in r.output


def test_build_uses_the_project_environment(tmp_path, monkeypatch):
    """A global stx renders the books with the project's .venv, not its own (s2 pilot)."""
    import sys

    from streamtex.cli.build_check import project_python
    from streamtex.core import discovery

    assert project_python(tmp_path) is None
    p = _project(tmp_path)
    (p / ".venv").symlink_to(sys.prefix)               # like a Dropbox project: .venv -> ~/.venvs/x
    assert project_python(p) == str(p / ".venv" / "bin" / "python")
    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    (p / "stx.toml").write_text('[project]\nname = "p"\n')
    (p / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    monkeypatch.chdir(p)
    r = CliRunner().invoke(cli, ["validate", "--build", "--timeout", "120"])
    assert str(p / ".venv" / "bin" / "python") in r.output.replace("\n", "")
    assert "bck_boom: NameError" in r.output              # the books did run with it
