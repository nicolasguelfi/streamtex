"""Tests for `stx pack`."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.pack_cmd import _parse_ref


def _make_project(tmp_path: Path) -> Path:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\nversion = "0.1.0"\n')
    (tmp_path / "stx.toml").write_text('[project]\nname = "demo"\n')
    return tmp_path


def _read_deps(project: Path) -> list[str]:
    """Return [project].dependencies as a list of strings."""
    import tomllib

    with (project / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    return list(data.get("project", {}).get("dependencies", []))


def _dep_names(deps: list[str]) -> set[str]:
    """Strip constraints/extras off dependency specs and return the name set."""
    import re

    return {
        re.split(r"[<>=!~\[\s;]", spec.strip(), maxsplit=1)[0].lower().replace("_", "-")
        for spec in deps
    }


def _run(cmd: list[str], cwd: Path):
    runner = CliRunner()
    prev = os.getcwd()
    try:
        os.chdir(cwd)
        return runner.invoke(cli, cmd)
    finally:
        os.chdir(prev)


def test_pack_help_lists_subcommands():
    runner = CliRunner()
    result = runner.invoke(cli, ["pack", "--help"])
    assert result.exit_code == 0
    for sub in ("add", "remove", "list", "sync", "info", "validate", "new", "set-primary"):
        assert sub in result.output


def test_pack_add_git_ref(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "add", "git:github.com/x/y@v0.1.0"], project)
    assert result.exit_code == 0, result.output
    stx_toml = (project / "stx.toml").read_text()
    assert 'type = "git"' in stx_toml
    assert "github.com/x/y" in stx_toml


def test_pack_add_pypi_ref(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "add", "pypi:streamtex-pack-x@>=0.1,<0.2"], project)
    assert result.exit_code == 0, result.output
    stx_toml = (project / "stx.toml").read_text()
    assert 'type = "pypi"' in stx_toml


def test_pack_new_creates_local_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "new", "mypack"], project)
    assert result.exit_code == 0, result.output
    pkg_root = project / "mypack" / "mypack"
    assert (pkg_root / "_pack_manifest.toml").is_file()
    assert (pkg_root / "components").is_dir()
    assert (pkg_root / "design_systems").is_dir()
    # Declared in stx.toml
    stx_toml = (project / "stx.toml").read_text()
    assert 'name = "mypack"' in stx_toml


def test_pack_set_primary_round_trip(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "new", "a"], project)
    _run(["pack", "new", "b"], project)
    r1 = _run(["pack", "set-primary", "b"], project)
    assert r1.exit_code == 0, r1.output
    stx_toml = (project / "stx.toml").read_text()
    # b should be primary
    assert "primary = true" in stx_toml


def test_pack_remove(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "add", "git:github.com/x/y@v0.1.0"], project)
    result = _run(["pack", "remove", "y"], project)
    assert result.exit_code == 0, result.output
    assert "github.com/x/y" not in (project / "stx.toml").read_text()


def test_pack_add_unsupported_ref(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "add", "not-a-ref"], project)
    assert result.exit_code != 0
    assert "Unsupported" in result.output or "git:" in result.output


def test_pack_add_dev_local_with_manifest(tmp_path: Path):
    project = _make_project(tmp_path)
    # First create a valid local pack
    _run(["pack", "new", "auxpack"], project)
    # Drop a stub component so the pack satisfies PV009
    (project / "auxpack" / "auxpack" / "components" / "stub.py").write_text("# stub\n")
    # Remove its [[packs]] entry so we can re-add via --dev
    _run(["pack", "remove", "auxpack"], project)
    result = _run(["pack", "add", "--dev", str(project / "auxpack" / "auxpack")], project)
    assert result.exit_code == 0, result.output
    stx_toml = (project / "stx.toml").read_text()
    assert 'name = "auxpack"' in stx_toml
    assert "editable = true" in stx_toml


def _read_pack_path(project: Path, name: str) -> str | None:
    """Return the recorded filesystem path for a declared local pack."""
    import tomllib

    with (project / "stx.toml").open("rb") as fh:
        data = tomllib.load(fh)
    for entry in data.get("packs", []):
        if entry.get("name") == name:
            return entry.get("path")
    return None


def test_pack_add_dev_monorepo_root_records_buildable_source(tmp_path: Path):
    """Regression: `pack add --dev <repo-root>` must succeed when the manifest
    lives in the inner package module (monorepo layout, e.g. streamtex-pack-
    design), and the recorded editable source must be the buildable root that
    `uv` can install — not the inner module dir without a pyproject.toml."""
    project = _make_project(tmp_path)
    _run(["pack", "new", "auxpack"], project)
    (project / "auxpack" / "auxpack" / "components" / "stub.py").write_text("# stub\n")
    _run(["pack", "remove", "auxpack"], project)
    # Point at the OUTER distribution root (pyproject.toml), manifest is inside.
    result = _run(["pack", "add", "--dev", str(project / "auxpack")], project)
    assert result.exit_code == 0, result.output
    recorded = _read_pack_path(project, "auxpack")
    assert recorded is not None
    # The invariant the bug violated: the editable source must be buildable.
    assert (Path(recorded) / "pyproject.toml").is_file(), recorded


def test_pack_add_dev_inner_module_resolves_to_buildable_root(tmp_path: Path):
    """Pointing --dev at the inner package module (where _pack_manifest.toml
    lives) must still record the buildable outer root as the editable source."""
    project = _make_project(tmp_path)
    _run(["pack", "new", "auxpack"], project)
    (project / "auxpack" / "auxpack" / "components" / "stub.py").write_text("# stub\n")
    _run(["pack", "remove", "auxpack"], project)
    # Point at the INNER module dir; resolver must climb to the buildable root.
    result = _run(["pack", "add", "--dev", str(project / "auxpack" / "auxpack")], project)
    assert result.exit_code == 0, result.output
    recorded = _read_pack_path(project, "auxpack")
    assert recorded is not None
    assert (Path(recorded) / "pyproject.toml").is_file(), recorded


def test_pack_add_dev_missing_path_fails(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(["pack", "add", "--dev", "/does/not/exist"], project)
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_pack_add_git_with_subdirectory(tmp_path: Path):
    """Monorepo: the #subdirectory= fragment must be parsed out and the pack
    name must be the sub-package basename, not the URL fragment."""
    project = _make_project(tmp_path)
    result = _run(
        [
            "pack",
            "add",
            "git:https://github.com/nicolasguelfi/streamtex-packs#subdirectory=streamtex-pack-design",
        ],
        project,
    )
    assert result.exit_code == 0, result.output
    stx_toml = (project / "stx.toml").read_text()
    assert 'name = "streamtex-pack-design"' in stx_toml
    assert 'subdirectory = "streamtex-pack-design"' in stx_toml
    # Scheme is stripped — canonical form stored in stx.toml.
    assert "https://" not in stx_toml.split("[[packs]]", 1)[1].split("[", 1)[0]
    assert 'ref = "github.com/nicolasguelfi/streamtex-packs"' in stx_toml


def test_pack_add_git_tolerates_scheme_and_dot_git(tmp_path: Path):
    project = _make_project(tmp_path)
    result = _run(
        ["pack", "add", "git:https://github.com/foo/bar.git@v1.2.3"], project
    )
    assert result.exit_code == 0, result.output
    stx_toml = (project / "stx.toml").read_text()
    assert 'ref = "github.com/foo/bar"' in stx_toml
    assert 'rev = "v1.2.3"' in stx_toml
    assert 'name = "bar"' in stx_toml


def test_pack_sync_writes_git_source_with_subdirectory(tmp_path: Path):
    """`pack sync` must translate a git+subdirectory [[packs]] entry into a
    valid [tool.uv.sources].<name> = { git = "...", subdirectory = "..." }."""
    project = _make_project(tmp_path)
    _run(
        [
            "pack",
            "add",
            "git:https://github.com/nicolasguelfi/streamtex-packs#subdirectory=streamtex-pack-design",
        ],
        project,
    )
    result = _run(["pack", "sync"], project)
    assert result.exit_code == 0, result.output
    pyproject = (project / "pyproject.toml").read_text()
    # uv.sources entry with git + subdirectory
    assert "[tool.uv.sources]" in pyproject
    assert 'git = "https://github.com/nicolasguelfi/streamtex-packs"' in pyproject
    assert 'subdirectory = "streamtex-pack-design"' in pyproject
    # Dependency declared so `uv sync` actually installs the pack.
    assert "streamtex-pack-design" in pyproject.split("dependencies", 1)[1]


def test_pack_sync_writes_git_source_with_rev(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "add", "git:github.com/foo/bar@v1.0.0"], project)
    result = _run(["pack", "sync"], project)
    assert result.exit_code == 0, result.output
    pyproject = (project / "pyproject.toml").read_text()
    assert 'git = "https://github.com/foo/bar"' in pyproject
    assert 'rev = "v1.0.0"' in pyproject


# --------------------------------------------------------------------------- #
# Parametrized: _parse_ref must canonicalize a wide range of real-world inputs #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "ref, expected",
    [
        # bare host/owner/repo
        (
            "git:github.com/foo/bar",
            {"type": "git", "ref": "github.com/foo/bar", "name": "bar"},
        ),
        # with @rev
        (
            "git:github.com/foo/bar@v1.0.0",
            {"type": "git", "ref": "github.com/foo/bar", "rev": "v1.0.0", "name": "bar"},
        ),
        # https:// scheme stripped
        (
            "git:https://github.com/foo/bar",
            {"type": "git", "ref": "github.com/foo/bar", "name": "bar"},
        ),
        # http:// scheme also stripped
        (
            "git:http://gitlab.example.com/foo/bar",
            {"type": "git", "ref": "gitlab.example.com/foo/bar", "name": "bar"},
        ),
        # .git suffix stripped
        (
            "git:https://github.com/foo/bar.git",
            {"type": "git", "ref": "github.com/foo/bar", "name": "bar"},
        ),
        # .git + @rev combined
        (
            "git:https://github.com/foo/bar.git@main",
            {"type": "git", "ref": "github.com/foo/bar", "rev": "main", "name": "bar"},
        ),
        # monorepo: subdirectory drives the pack name
        (
            "git:https://github.com/x/monorepo#subdirectory=pkg-a",
            {
                "type": "git",
                "ref": "github.com/x/monorepo",
                "subdirectory": "pkg-a",
                "name": "pkg-a",
            },
        ),
        # monorepo + nested subdirectory: last segment is the name
        (
            "git:github.com/x/monorepo#subdirectory=packs/inner-pack",
            {
                "type": "git",
                "ref": "github.com/x/monorepo",
                "subdirectory": "packs/inner-pack",
                "name": "inner-pack",
            },
        ),
        # full real-world form: scheme + .git + @rev + #subdirectory=
        (
            "git:https://github.com/owner/mono.git@v2.1#subdirectory=apps/web",
            {
                "type": "git",
                "ref": "github.com/owner/mono",
                "rev": "v2.1",
                "subdirectory": "apps/web",
                "name": "web",
            },
        ),
        # SHA as rev
        (
            "git:github.com/foo/bar@abc1234",
            {"type": "git", "ref": "github.com/foo/bar", "rev": "abc1234", "name": "bar"},
        ),
        # local plain
        (
            "local:./mypack",
            {"type": "local", "name": "mypack", "path": "./mypack", "primary": False},
        ),
        # local absolute path
        (
            "local:/abs/path/to/pack",
            {
                "type": "local",
                "name": "pack",
                "path": "/abs/path/to/pack",
                "primary": False,
            },
        ),
        # pypi bare
        ("pypi:streamtex-pack-x", {"type": "pypi", "name": "streamtex-pack-x"}),
        # pypi with constraint
        (
            "pypi:streamtex-pack-x@>=0.1,<0.2",
            {
                "type": "pypi",
                "name": "streamtex-pack-x",
                "constraint": ">=0.1,<0.2",
            },
        ),
    ],
)
def test_parse_ref_variants(ref: str, expected: dict):
    """Canonicalize 14 ref shapes seen in the wild.

    Regression cover for the bug where ``git:https://.../#subdirectory=foo``
    silently absorbed the fragment into the URL and produced a corrupted name.
    """
    assert _parse_ref(ref) == expected


@pytest.mark.parametrize(
    "ref",
    [
        "not-a-ref",
        "",
        "github.com/foo/bar",  # missing git: prefix
        "git:",  # empty body
        "https://github.com/foo/bar",  # raw URL without git: prefix
    ],
)
def test_parse_ref_rejects_invalid(ref: str):
    import click

    with pytest.raises(click.ClickException):
        _parse_ref(ref)


# --------------------------------------------------------------------------- #
# E2E sync — for each pack type, sync must leave pyproject.toml in a state    #
# `uv sync` can resolve.                                                      #
# --------------------------------------------------------------------------- #


def test_sync_e2e_local_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "new", "auxpack"], project)
    result = _run(["pack", "sync"], project)
    assert result.exit_code == 0, result.output
    pyproject = (project / "pyproject.toml").read_text()
    # [tool.uv.sources] entry + dependency declared
    assert 'path = "./auxpack"' in pyproject
    assert "editable = true" in pyproject
    deps_block = _read_deps(project)
    assert "auxpack" in deps_block


def test_sync_e2e_git_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "add", "git:github.com/foo/bar@v1.0"], project)
    result = _run(["pack", "sync"], project)
    assert result.exit_code == 0, result.output
    pyproject = (project / "pyproject.toml").read_text()
    assert 'git = "https://github.com/foo/bar"' in pyproject
    assert 'rev = "v1.0"' in pyproject
    deps_block = _read_deps(project)
    assert "bar" in deps_block


def test_sync_e2e_git_pack_with_subdirectory(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(
        [
            "pack",
            "add",
            "git:https://github.com/nicolasguelfi/streamtex-packs#subdirectory=streamtex-pack-design",
        ],
        project,
    )
    result = _run(["pack", "sync"], project)
    assert result.exit_code == 0, result.output
    pyproject = (project / "pyproject.toml").read_text()
    assert 'git = "https://github.com/nicolasguelfi/streamtex-packs"' in pyproject
    assert 'subdirectory = "streamtex-pack-design"' in pyproject
    deps_block = _read_deps(project)
    assert "streamtex-pack-design" in deps_block


def test_sync_e2e_pypi_pack(tmp_path: Path):
    project = _make_project(tmp_path)
    _run(["pack", "add", "pypi:streamtex-pack-x@>=0.1,<0.2"], project)
    result = _run(["pack", "sync"], project)
    assert result.exit_code == 0, result.output
    deps = _read_deps(project)
    # The constrained form should land in dependencies; sources untouched
    # because PyPI packs don't need a uv.sources mapping.
    assert "streamtex-pack-x" in _dep_names(deps)
    assert any(">=0.1,<0.2" in d for d in deps)


def test_sync_e2e_idempotent(tmp_path: Path):
    """Running sync twice must produce identical pyproject.toml content."""
    project = _make_project(tmp_path)
    _run(["pack", "add", "git:github.com/foo/bar@v1.0"], project)
    _run(["pack", "sync"], project)
    snapshot = (project / "pyproject.toml").read_text()
    _run(["pack", "sync"], project)
    assert (project / "pyproject.toml").read_text() == snapshot


def test_sync_e2e_multiple_packs_coexist(tmp_path: Path):
    """A local + git + pypi triple must all land in pyproject without conflict."""
    project = _make_project(tmp_path)
    _run(["pack", "new", "localpack"], project)
    _run(["pack", "add", "git:github.com/x/y@v1.0"], project)
    _run(["pack", "add", "pypi:streamtex-pack-z@>=0.1"], project)
    _run(["pack", "sync"], project)
    names = _dep_names(_read_deps(project))
    for name in ("localpack", "y", "streamtex-pack-z"):
        assert name in names, f"missing {name} in deps: {names}"


# --------------------------------------------------------------------------- #
# Opt-in live smoke test (network required).                                  #
# Run with: `pytest tests/test_cli_pack.py -m live`                           #
# --------------------------------------------------------------------------- #


@pytest.mark.live
def test_smoke_install_real_pack_design(tmp_path: Path):
    """Full chain against the real streamtex-pack-design on GitHub.

    Performs: pack add → pack sync → uv sync → assert the 19 expected
    components are discovered. Requires network + uv binary. Skipped unless
    invoked with `pytest -m live`.
    """
    import subprocess
    import sys

    project = _make_project(tmp_path)
    # Project needs `streamtex` available because the pack imports it
    # transitively when discovery loads the components.
    (project / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.1.0"\n'
        'requires-python = ">=3.11"\n'
        'dependencies = ["streamtex[cli]"]\n'
    )
    res = _run(
        [
            "pack",
            "add",
            "git:https://github.com/nicolasguelfi/streamtex-packs#subdirectory=streamtex-pack-design",
        ],
        project,
    )
    assert res.exit_code == 0, res.output
    res = _run(["pack", "sync"], project)
    assert res.exit_code == 0, res.output

    # Force a uv sync from within the project venv.
    uv_sync = subprocess.run(
        ["uv", "sync"], cwd=str(project), capture_output=True, text=True
    )
    assert uv_sync.returncode == 0, uv_sync.stderr

    # Discover via stx component list, run inside the project venv (uv run).
    listing = subprocess.run(
        ["uv", "run", sys.executable, "-m", "streamtex.cli.commands", "component", "list"],
        cwd=str(project),
        capture_output=True,
        text=True,
    )
    assert listing.returncode == 0, listing.stderr
    # Spot-check a few of the 19 components.
    for name in ("callout", "stat_hero", "title_slide", "takeaways"):
        assert name in listing.stdout, f"missing {name}: {listing.stdout}"


def test_pack_remove_strips_dependency(tmp_path: Path):
    """Removing a pack must also remove the matching [project].dependencies
    entry so the project no longer carries a ghost dep."""
    project = _make_project(tmp_path)
    _run(
        [
            "pack",
            "add",
            "git:https://github.com/nicolasguelfi/streamtex-packs#subdirectory=streamtex-pack-design",
        ],
        project,
    )
    _run(["pack", "sync"], project)
    pyproject_before = (project / "pyproject.toml").read_text()
    assert "streamtex-pack-design" in pyproject_before

    result = _run(["pack", "remove", "streamtex-pack-design"], project)
    assert result.exit_code == 0, result.output
    pyproject_after = (project / "pyproject.toml").read_text()
    deps_section = pyproject_after.split("dependencies", 1)
    # If a dependencies section still exists, our pack must not be in it.
    if len(deps_section) > 1:
        assert "streamtex-pack-design" not in deps_section[1].split("[", 1)[0]
