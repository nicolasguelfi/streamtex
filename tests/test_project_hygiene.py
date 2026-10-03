"""Project guard rails: conflict-marker hook, conflict markers and deprecated config in stx validate (#89)."""

from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.project_cmd import generate_pre_commit_config
from streamtex.cli.project_rules import conflict_markers, deprecated_config


def test_new_projects_get_conflict_marker_hook():
    cfg = generate_pre_commit_config()
    assert "id: ruff" in cfg and "id: check-merge-conflict" in cfg and "id: check-toml" in cfg


def test_conflict_markers_and_deprecated_config(tmp_path):
    (tmp_path / "blocks").mkdir()
    (tmp_path / "blocks" / "bck_a.py").write_text("x = 1\n<<<<<<< HEAD\ny = 2\n=======\ny = 3\n>>>>>>> other\n")
    (tmp_path / "blocks" / "bck_b.py").write_text("ok = True\n")
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n[patterns]\nuse = ["x"]\n')
    assert conflict_markers(tmp_path) == [("blocks/bck_a.py", 2)]
    assert deprecated_config(tmp_path) and deprecated_config(tmp_path)[0].startswith("[patterns]")


def test_validate_reports_hygiene(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n[patterns]\nuse = []\n')
    (tmp_path / "a.py").write_text("<<<<<<< HEAD\n")
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(cli, ["validate"])
    assert r.exit_code == 2 and "conflict marker" in r.output and "deprecated" in r.output
    # the section name is printed, not swallowed as Rich markup
    assert "remove [patterns]" in " ".join(r.output.split())


def test_stx_toml_sections_typos_and_bad_documents_are_warned(tmp_path):
    from streamtex.cli.project_rules import stx_toml_section_problems

    (tmp_path / "book.py").write_text("")
    (tmp_path / "stx.toml").write_text(
        '[book.defaults]\npaginate = true\npagewidth = 80\n'
        '[[run.documents]]\nid = "a"\nbook = "book.py"\nport = 8601\n'
        '[[run.documents]]\nid = "a"\nbook = "book.py"\nport = 8602\n')
    problems = stx_toml_section_problems(tmp_path)
    assert len(problems) == 2
    assert "pagewidth" in problems[0] and "page_width" in problems[0]
    assert "duplicate" in problems[1]


def test_stx_toml_sections_valid_or_absent_say_nothing(tmp_path):
    from streamtex.cli.project_rules import stx_toml_section_problems

    (tmp_path / "book.py").write_text("")
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n')
    assert stx_toml_section_problems(tmp_path) == []
    (tmp_path / "stx.toml").write_text(
        '[book.defaults]\npage_width = 80\n[[run.documents]]\nid = "a"\nbook = "book.py"\nport = 8601\n')
    assert stx_toml_section_problems(tmp_path) == []


def test_validate_prints_stx_toml_section_warnings(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n[book.defaults]\nbanner_colour = "red"\n')
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(cli, ["validate"])
    assert "banner_colour" in r.output and r.exit_code == 1, r.output
    assert "[book.defaults]" in r.output
