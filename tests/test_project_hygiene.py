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
