"""Parity tests between the two project-creation paths.

`stx project new X` (project_cmd.new) and `stx install --project X`
(install_cmd._create_project) must produce the same reuse-architecture-ready
project structure — notably stx.toml + the local mypack pack. They had drifted:
the install path only ran scaffold_project and omitted stx.toml/mypack.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from streamtex.cli import install_cmd


@pytest.fixture
def no_subprocess(monkeypatch):
    """Neutralize git/uv/pre-commit subprocess calls and skip uv (which→None)
    so the tests exercise file generation only, fast and offline."""
    monkeypatch.setattr(
        install_cmd.subprocess,
        "run",
        lambda *a, **k: MagicMock(returncode=0, stderr="", stdout=""),
    )
    monkeypatch.setattr(install_cmd.shutil, "which", lambda _x: None)
    # Claude profile resolution must not require a real workspace clone.
    import click

    import streamtex.cli.claude_cmd as claude_cmd

    def _raise(*_a, **_k):
        raise click.ClickException("no claude repo in test")

    monkeypatch.setattr(claude_cmd, "find_claude_repo", _raise)


def _make_workspace(tmp_path: Path, preset: str = "power") -> Path:
    ws_root = tmp_path / "ws"
    (ws_root / "projects").mkdir(parents=True)
    (ws_root / "stx.toml").write_text(
        f'[workspace]\nname = "ws"\npreset = "{preset}"\n'
    )
    return ws_root


def test_install_create_project_generates_stx_toml(tmp_path, no_subprocess):
    """RED before the fix: stx install --project omitted stx.toml."""
    ws_root = _make_workspace(tmp_path)
    install_cmd._create_project(
        str(ws_root), {"preset": "power"}, "demo", None, "power", MagicMock()
    )
    proj = ws_root / "projects" / "demo"
    assert (proj / "stx.toml").is_file(), "install path must generate stx.toml"


def test_install_create_project_generates_mypack(tmp_path, no_subprocess):
    """RED before the fix: stx install --project omitted the local mypack."""
    ws_root = _make_workspace(tmp_path)
    install_cmd._create_project(
        str(ws_root), {"preset": "power"}, "demo", None, "power", MagicMock()
    )
    manifest = (
        ws_root / "projects" / "demo" / "mypack" / "mypack" / "_pack_manifest.toml"
    )
    assert manifest.is_file(), "install path must scaffold the local mypack pack"


def test_install_project_stx_toml_declares_local_pack(tmp_path, no_subprocess):
    """The generated stx.toml must declare mypack as the primary local pack."""
    import tomllib

    ws_root = _make_workspace(tmp_path)
    install_cmd._create_project(
        str(ws_root), {"preset": "power"}, "demo", None, "power", MagicMock()
    )
    data = tomllib.loads((ws_root / "projects" / "demo" / "stx.toml").read_text())
    packs = data.get("packs", [])
    assert any(
        p.get("name") == "mypack" and p.get("primary") is True for p in packs
    ), f"mypack not declared primary in {packs}"


def test_new_and_install_parity_file_set(tmp_path, no_subprocess, monkeypatch):
    """The set of generated project files must match between the two paths
    (ignoring uv/venv artifacts, which are skipped here)."""
    import streamtex.cli.project_cmd as project_cmd

    # --- install path ---
    ws_root = _make_workspace(tmp_path)
    install_cmd._create_project(
        str(ws_root), {"preset": "power"}, "viainstall", None, "power", MagicMock()
    )
    install_proj = ws_root / "projects" / "viainstall"

    # --- project new path: call the scaffold + metadata helpers directly to
    #     compare pure file generation without the Click command wrapper ---
    new_proj = tmp_path / "vianew"
    new_proj.mkdir()
    extras = install_cmd.PRESET_EXTRAS.get("power", [])
    project_cmd.scaffold_project(str(new_proj), "vianew", extras=extras)
    project_cmd.scaffold_project_metadata(str(new_proj), "vianew")

    def _tree(root: Path) -> set[str]:
        return {
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file() and ".git" not in p.parts
        }

    install_files = _tree(install_proj)
    new_files = _tree(new_proj)
    # Both must contain the reuse-architecture essentials.
    for essential in ("stx.toml", "book.py", "mypack/mypack/_pack_manifest.toml"):
        assert essential in install_files, f"install missing {essential}"
        assert essential in new_files, f"new missing {essential}"
    # And the file sets must be identical.
    assert install_files == new_files, (
        f"divergence:\n  only in install: {sorted(install_files - new_files)}\n"
        f"  only in new: {sorted(new_files - install_files)}"
    )


def test_apply_dev_link_delegates_to_shared_helper(tmp_path, monkeypatch):
    """install._apply_dev_link_to_project must go through the single shared
    auto_link_streamtex_if_registered implementation, producing the editable
    [tool.uv.sources].streamtex entry."""
    import streamtex.cli.dev_cmd as dev_cmd

    ws_root = _make_workspace(tmp_path)
    proj = ws_root / "projects" / "demo"
    proj.mkdir(parents=True)
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
    )

    # Fake a registered, valid streamtex clone.
    clone = tmp_path / "streamtex-clone"
    (clone / "streamtex").mkdir(parents=True)
    (clone / "streamtex" / "__init__.py").write_text('__version__ = "0.0.0-dev"\n')
    (clone / "pyproject.toml").write_text(
        '[project]\nname = "streamtex"\nversion = "0.0.0-dev"\n'
    )
    monkeypatch.setattr(
        dev_cmd.GlobalDevConfig,
        "load",
        classmethod(lambda cls: MagicMock(repos={"streamtex": str(clone)})),
    )
    monkeypatch.setattr(dev_cmd, "_uv_sync", lambda *a, **k: None)

    install_cmd._apply_dev_link_to_project(str(ws_root), "demo", MagicMock())

    import tomllib

    data = tomllib.loads((proj / "pyproject.toml").read_text())
    src = data["tool"]["uv"]["sources"]["streamtex"]
    assert src == {"path": str(clone), "editable": True}


def test_apply_dev_link_no_op_when_unregistered(tmp_path, monkeypatch):
    """When streamtex isn't registered, the helper returns False and install
    prints the hint without writing any source."""
    import streamtex.cli.dev_cmd as dev_cmd

    ws_root = _make_workspace(tmp_path)
    proj = ws_root / "projects" / "demo"
    proj.mkdir(parents=True)
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
    )
    monkeypatch.setattr(
        dev_cmd.GlobalDevConfig,
        "load",
        classmethod(lambda cls: MagicMock(repos={})),
    )
    console = MagicMock()
    install_cmd._apply_dev_link_to_project(str(ws_root), "demo", console)

    import tomllib

    data = tomllib.loads((proj / "pyproject.toml").read_text())
    assert "streamtex" not in data.get("tool", {}).get("uv", {}).get("sources", {})
    assert console.print.called  # hint emitted
