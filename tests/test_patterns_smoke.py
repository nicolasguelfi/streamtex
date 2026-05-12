"""Smoke tests for the ``stx patterns`` command surface.

These tests exercise the minimum end-to-end paths:
- ``stx patterns list --remote --source <fake>`` finds patterns in a tiny
  source repo.
- ``stx patterns install --preset minimal --source <fake> --target <tmp> --dry-run``
  produces a coherent install plan without writing.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from streamtex.cli.patterns_cmd import patterns
from streamtex.patterns.installer import build_install_plan
from streamtex.patterns.preset import resolve_preset
from streamtex.patterns.resolver import resolve_source

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_FRONTMATTER_TEMPLATE = """\
---
name: {name}
type: pattern
description: A demo pattern for smoke tests
tags: [demo, smoke]
extrapolable: false
since: 2026-05-10
---

# {name}

## Visual

```
demo
```

## Structure

- one element

## Styling rules

| Element | Property | Value |
|---|---|---|
| Wrapper | type | div |

## Code skeleton

```python
def build():
    return None
```

## When to use

- demo

## When NOT to use

- production
"""


@pytest.fixture()
def fake_source(tmp_path: Path) -> Path:
    """Create a minimal but valid streamtex-patterns source repo."""
    src = tmp_path / "streamtex-patterns"
    (src / "core").mkdir(parents=True)
    (src / "slides").mkdir()
    (src / "presets").mkdir()

    # Two core patterns, one slide pattern.
    for name in ("alpha", "beta"):
        (src / "core" / f"{name}.md").write_text(
            _FRONTMATTER_TEMPLATE.format(name=name), encoding="utf-8"
        )
    (src / "slides" / "title_demo.md").write_text(
        _FRONTMATTER_TEMPLATE.format(name="title_demo"), encoding="utf-8"
    )

    # manifest.toml
    (src / "manifest.toml").write_text(
        """
[repo]
name = "streamtex-patterns-test"
version = "0.0.1"
description = "test fixture"
spec_version = "A2"
since = "2026-05-10"

[scopes]
core = "atoms"
slides = "slides"

[presets]
core = "core.toml"
minimal = "minimal.toml"
""",
        encoding="utf-8",
    )

    # core preset
    (src / "presets" / "core.toml").write_text(
        """
[preset]
name = "core"
description = "core atoms"

[patterns]
include = ["core/alpha.md", "core/beta.md"]
exclude = []

[depends_on]
extends = ""
""",
        encoding="utf-8",
    )

    # minimal preset extends core + adds slide
    (src / "presets" / "minimal.toml").write_text(
        """
[preset]
name = "minimal"
description = "minimal preset for tests"

[patterns]
include = ["slides/title_demo.md"]
exclude = []

[depends_on]
extends = "core"
""",
        encoding="utf-8",
    )
    return src


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_resolver_cli_override(fake_source: Path, tmp_path: Path) -> None:
    """Resolver accepts a CLI override pointing at a valid source."""
    project = tmp_path / "project"
    project.mkdir()
    rs = resolve_source(project, cli_override=str(fake_source))
    assert rs.path == fake_source.resolve()
    assert rs.raw_value == str(fake_source)


def test_resolve_preset_chain(fake_source: Path) -> None:
    """``minimal`` preset resolves to core + slides files."""
    rp = resolve_preset(fake_source, "minimal")
    names = sorted(p.stem for p in rp.pattern_files)
    assert names == ["alpha", "beta", "title_demo"]


def test_list_patterns_in_repo(fake_source: Path, tmp_path: Path) -> None:
    """``stx patterns list --remote --source <fake>`` lists three patterns."""
    runner = CliRunner()
    project = tmp_path / "project"
    project.mkdir()

    with runner.isolated_filesystem(temp_dir=project):
        result = runner.invoke(
            patterns,
            ["list", "--remote", "--source", str(fake_source), "--format", "names"],
        )
    assert result.exit_code == 0, result.output
    names = sorted(line.strip() for line in result.output.splitlines() if line.strip())
    assert names == ["alpha", "beta", "title_demo"]


def test_install_dry_run(fake_source: Path, tmp_path: Path) -> None:
    """Dry-run install produces a plan without writing meta or files."""
    project = tmp_path / "project"
    target = project / ".claude" / "custom" / "streamtex-patterns"
    project.mkdir()

    plan = build_install_plan(
        target=target,
        source=fake_source,
        preset="minimal",
    )
    assert plan.is_initial is True
    assert sorted(p.stem for p in plan.selected_files) == ["alpha", "beta", "title_demo"]

    # Run the actual CLI in dry-run mode and verify no meta is written.
    runner = CliRunner()
    result = runner.invoke(
        patterns,
        [
            "install",
            "--source", str(fake_source),
            "--preset", "minimal",
            "--target", str(target),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "alpha" in result.output or "Dry-run" in result.output
    assert not (target / ".patterns-meta.json").exists()


def test_install_then_status(fake_source: Path, tmp_path: Path) -> None:
    """Real install writes meta, status reports CLEAN for all files."""
    project = tmp_path / "project"
    target = project / ".claude" / "custom" / "streamtex-patterns"
    project.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        patterns,
        [
            "install",
            "--source", str(fake_source),
            "--preset", "minimal",
            "--target", str(target),
        ],
    )
    assert result.exit_code == 0, result.output
    meta_path = target / ".patterns-meta.json"
    assert meta_path.is_file()
    assert (target / "alpha.md").is_file()
    assert (target / "_pattern_library.md").is_file()

    # Status should report all clean.
    result = runner.invoke(
        patterns,
        [
            "status",
            "--source", str(fake_source),
            "--target", str(target),
            "--format", "json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "clean" in result.output


def test_validate_cli(fake_source: Path, tmp_path: Path) -> None:
    """Validate runs against installed patterns and exits 0 on a clean fixture."""
    project = tmp_path / "project"
    target = project / ".claude" / "custom" / "streamtex-patterns"
    project.mkdir()

    runner = CliRunner()
    runner.invoke(
        patterns,
        [
            "install",
            "--source", str(fake_source),
            "--preset", "core",
            "--target", str(target),
        ],
    )
    result = runner.invoke(
        patterns,
        ["validate", "--all", "--target", str(target)],
    )
    assert result.exit_code == 0, result.output
