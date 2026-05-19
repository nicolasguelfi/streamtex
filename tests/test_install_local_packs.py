"""Tests for streamtex.cli._install_local_packs (G4a fix)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from streamtex.cli._install_local_packs import install_local_packs


def _make_pack(project: Path, name: str) -> Path:
    """Create a minimal installable pack inside the project."""
    pack_dir = project / name
    pack_dir.mkdir()
    (pack_dir / "pyproject.toml").write_text(
        f'[project]\nname = "{name}"\nversion = "0.1.0"\n'
        '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
    )
    return pack_dir


def test_install_local_packs_skips_when_no_stx_toml(tmp_path: Path, capsys):
    rc = install_local_packs(tmp_path)
    assert rc == 0
    assert "no stx.toml" in capsys.readouterr().out


def test_install_local_packs_installs_relative_path(tmp_path: Path, capsys):
    _make_pack(tmp_path, "mypack")
    (tmp_path / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[[packs]]\ntype = "local"\nname = "mypack"\npath = "./mypack"\nprimary = true\n'
    )
    with patch(
        "streamtex.cli._install_local_packs.subprocess.run"
    ) as fake_run:
        fake_run.return_value.returncode = 0
        rc = install_local_packs(tmp_path)
    assert rc == 0
    fake_run.assert_called_once()
    args = fake_run.call_args[0][0]
    assert args[:3] == ["uv", "pip", "install"]
    assert "--no-deps" in args
    assert "-e" in args
    assert any("mypack" in a for a in args)
    assert "installing 'mypack'" in capsys.readouterr().out


def test_install_local_packs_skips_absolute_path(tmp_path: Path, capsys):
    (tmp_path / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[[packs]]\ntype = "local"\nname = "external"\npath = "/Users/dev/external"\n'
    )
    with patch(
        "streamtex.cli._install_local_packs.subprocess.run"
    ) as fake_run:
        rc = install_local_packs(tmp_path)
    assert rc == 0  # absolute path is skipped (warn), not failure
    fake_run.assert_not_called()
    out = capsys.readouterr().out
    assert "WARN" in out
    assert "absolute" in out
    assert "external" in out


def test_install_local_packs_skips_missing_directory(tmp_path: Path, capsys):
    (tmp_path / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[[packs]]\ntype = "local"\nname = "ghost"\npath = "./ghost"\n'
    )
    rc = install_local_packs(tmp_path)
    assert rc == 0
    assert "does not exist" in capsys.readouterr().out


def test_install_local_packs_skips_no_pyproject(tmp_path: Path, capsys):
    (tmp_path / "broken").mkdir()
    (tmp_path / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[[packs]]\ntype = "local"\nname = "broken"\npath = "./broken"\n'
    )
    rc = install_local_packs(tmp_path)
    assert rc == 0
    assert "no pyproject.toml" in capsys.readouterr().out


def test_install_local_packs_ignores_non_local_packs(tmp_path: Path, capsys):
    (tmp_path / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[[packs]]\ntype = "git"\nname = "remote_pack"\nref = "github.com/x/y"\nrev = "v0.1.0"\n'
    )
    with patch(
        "streamtex.cli._install_local_packs.subprocess.run"
    ) as fake_run:
        rc = install_local_packs(tmp_path)
    assert rc == 0
    fake_run.assert_not_called()


def test_install_local_packs_propagates_failure(tmp_path: Path):
    _make_pack(tmp_path, "mypack")
    (tmp_path / "stx.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[[packs]]\ntype = "local"\nname = "mypack"\npath = "./mypack"\nprimary = true\n'
    )
    with patch(
        "streamtex.cli._install_local_packs.subprocess.run"
    ) as fake_run:
        fake_run.return_value.returncode = 1
        rc = install_local_packs(tmp_path)
    assert rc == 1
