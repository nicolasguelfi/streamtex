"""Tests for v3 composite selection: resolver, picker menu, declarative CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from streamtex.cli.patterns_cmd import patterns
from streamtex.patterns import PatternError
from streamtex.patterns.installer import resolve_selection
from streamtex.patterns.manifest import PatternSelection
from streamtex.patterns.picker import (
    InteractiveAborted,
    collect_pattern_catalog,
    select_patterns_compositely,
)

# ---------------------------------------------------------------------------
# Fixtures — patterns source with 2 presets, 4 patterns
# ---------------------------------------------------------------------------

_MANIFEST = """\
[repo]
name = "streamtex-patterns"
version = "0.1.0"
description = "fixture"
spec_version = "A2"
since = "2026-05-10"

[scopes]
core = "Universal"
slides = "Slide-based"

[presets]
core = "core.toml"
slides = "slides.toml"
"""

_PATTERN_TEMPLATE = """\
---
name: {name}
type: pattern
description: {description}
tags: [{tags}]
extrapolable: true
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


def _write_pattern(folder: Path, name: str, description: str, tags: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.md").write_text(
        _PATTERN_TEMPLATE.format(name=name, description=description, tags=tags),
        encoding="utf-8",
    )


@pytest.fixture()
def source(tmp_path: Path) -> Path:
    """Source with: core/{alpha,beta}, slides/{hero,title}, 2 presets."""
    src = tmp_path / "src-patterns"
    src.mkdir()
    (src / "manifest.toml").write_text(_MANIFEST, encoding="utf-8")
    _write_pattern(src / "core", "ptn_alpha", "Alpha atom", "atom")
    _write_pattern(src / "core", "ptn_beta", "Beta atom", "atom")
    _write_pattern(src / "slides", "ptn_hero", "Hero slide", "slide")
    _write_pattern(src / "slides", "ptn_title", "Title slide", "slide")
    (src / "presets").mkdir()
    # core preset = core/*
    (src / "presets" / "core.toml").write_text(
        '[patterns]\ninclude = ["core/*.md"]\n', encoding="utf-8",
    )
    # slides preset = slides/*
    (src / "presets" / "slides.toml").write_text(
        '[patterns]\ninclude = ["slides/*.md"]\n', encoding="utf-8",
    )
    return src


class _FakeAsk:
    def __init__(self, answer):
        self.answer = answer

    def ask(self):
        return self.answer


# ---------------------------------------------------------------------------
# resolve_selection — composition algebra
# ---------------------------------------------------------------------------

def test_resolve_empty_selection(source: Path) -> None:
    assert resolve_selection(PatternSelection(), source) == ()


def test_resolve_single_preset(source: Path) -> None:
    sel = PatternSelection(presets=("core",))
    assert resolve_selection(sel, source) == ("ptn_alpha", "ptn_beta")


def test_resolve_multi_preset_unions(source: Path) -> None:
    sel = PatternSelection(presets=("core", "slides"))
    assert resolve_selection(sel, source) == (
        "ptn_alpha", "ptn_beta", "ptn_hero", "ptn_title",
    )


def test_resolve_individuals(source: Path) -> None:
    sel = PatternSelection(individuals=("ptn_hero",))
    assert resolve_selection(sel, source) == ("ptn_hero",)


def test_resolve_unknown_individual_raises(source: Path) -> None:
    with pytest.raises(PatternError):
        resolve_selection(PatternSelection(individuals=("ptn_nope",)), source)


def test_resolve_excludes_subtract(source: Path) -> None:
    sel = PatternSelection(
        presets=("core",),
        excludes=("ptn_beta",),
    )
    assert resolve_selection(sel, source) == ("ptn_alpha",)


def test_resolve_all_flag(source: Path) -> None:
    sel = PatternSelection(all_flag=True)
    assert resolve_selection(sel, source) == (
        "ptn_alpha", "ptn_beta", "ptn_hero", "ptn_title",
    )


def test_resolve_all_with_excludes(source: Path) -> None:
    sel = PatternSelection(all_flag=True, excludes=("ptn_hero", "ptn_title"))
    assert resolve_selection(sel, source) == ("ptn_alpha", "ptn_beta")


def test_resolve_composite_mix(source: Path) -> None:
    # preset slides + individual ptn_alpha + exclude ptn_title
    # → {hero, title} ∪ {alpha} − {title} = {alpha, hero}
    sel = PatternSelection(
        presets=("slides",),
        individuals=("ptn_alpha",),
        excludes=("ptn_title",),
    )
    assert resolve_selection(sel, source) == ("ptn_alpha", "ptn_hero")


def test_resolve_dedupes_overlap(source: Path) -> None:
    # core ∪ individuals=[ptn_alpha] = {alpha, beta} (no duplicate)
    sel = PatternSelection(
        presets=("core",),
        individuals=("ptn_alpha",),
    )
    assert resolve_selection(sel, source) == ("ptn_alpha", "ptn_beta")


# ---------------------------------------------------------------------------
# select_patterns_compositely — menu state machine (questionary mocked)
# ---------------------------------------------------------------------------

def _run_picker(source: Path, menu_answers, checkbox_answer=None,
                confirm_answer=False):
    """Helper: run select_patterns_compositely with mocked sub-prompts."""
    catalog = collect_pattern_catalog(source)
    menu_iter = iter(menu_answers)
    with (
        patch("questionary.select",
              side_effect=lambda *a, **kw: _FakeAsk(next(menu_iter))),
        patch("questionary.checkbox",
              return_value=_FakeAsk(checkbox_answer)),
        patch("questionary.confirm",
              return_value=_FakeAsk(confirm_answer)),
        patch("questionary.print"),
    ):
        return select_patterns_compositely(catalog, source)


def test_picker_add_preset_then_done(source: Path) -> None:
    result = _run_picker(
        source,
        menu_answers=["add_preset", "done"],
        checkbox_answer=["core"],
    )
    assert result == PatternSelection(presets=("core",))


def test_picker_add_two_presets(source: Path) -> None:
    result = _run_picker(
        source,
        menu_answers=["add_preset", "done"],
        checkbox_answer=["core", "slides"],
    )
    assert result == PatternSelection(presets=("core", "slides"))


def test_picker_add_individual(source: Path) -> None:
    result = _run_picker(
        source,
        menu_answers=["add_individual", "done"],
        checkbox_answer=["ptn_hero"],
    )
    assert result == PatternSelection(individuals=("ptn_hero",))


def test_picker_toggle_all(source: Path) -> None:
    result = _run_picker(
        source,
        menu_answers=["toggle_all", "done"],
        checkbox_answer=None,
    )
    assert result == PatternSelection(all_flag=True)


def test_picker_cancel_raises(source: Path) -> None:
    with pytest.raises(InteractiveAborted):
        _run_picker(source, menu_answers=["cancel"])


def test_picker_empty_done_then_confirm_cancels(source: Path) -> None:
    # User picks Done with empty selection → confirm prompt asks "really
    # cancel?" → answers True → abort.
    with pytest.raises(InteractiveAborted):
        _run_picker(
            source,
            menu_answers=["done"],
            confirm_answer=True,
        )


def test_picker_remove_adds_to_excludes(source: Path) -> None:
    # Compose: add preset 'core' (→ alpha + beta), then remove ptn_beta
    # → excludes={ptn_beta}
    catalog = collect_pattern_catalog(source)
    menu_iter = iter(["add_preset", "remove", "done"])
    checkbox_calls = iter([
        ["core"],         # add_preset → select 'core'
        ["ptn_beta"],     # remove → uncheck ptn_beta
    ])
    with (
        patch("questionary.select",
              side_effect=lambda *a, **kw: _FakeAsk(next(menu_iter))),
        patch("questionary.checkbox",
              side_effect=lambda *a, **kw: _FakeAsk(next(checkbox_calls))),
        patch("questionary.confirm", return_value=_FakeAsk(False)),
        patch("questionary.print"),
    ):
        result = select_patterns_compositely(catalog, source)
    assert result.presets == ("core",)
    assert "ptn_beta" in result.excludes
    # Resolution check: only ptn_alpha remains
    assert resolve_selection(result, source) == ("ptn_alpha",)


def test_picker_remove_individual_drops_from_individuals(source: Path) -> None:
    # add individuals=[alpha, hero], then remove [hero]
    # → individuals=(alpha,), excludes=()
    catalog = collect_pattern_catalog(source)
    menu_iter = iter(["add_individual", "remove", "done"])
    checkbox_calls = iter([
        ["ptn_alpha", "ptn_hero"],
        ["ptn_hero"],
    ])
    with (
        patch("questionary.select",
              side_effect=lambda *a, **kw: _FakeAsk(next(menu_iter))),
        patch("questionary.checkbox",
              side_effect=lambda *a, **kw: _FakeAsk(next(checkbox_calls))),
        patch("questionary.confirm", return_value=_FakeAsk(False)),
        patch("questionary.print"),
    ):
        result = select_patterns_compositely(catalog, source)
    # ptn_hero was removed from individuals (not added to excludes)
    assert result.individuals == ("ptn_alpha",)
    assert result.excludes == ()


# ---------------------------------------------------------------------------
# Declarative CLI — composite via flags
# ---------------------------------------------------------------------------

def test_install_cli_multi_preset(source: Path, tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    runner = CliRunner()
    result = runner.invoke(
        patterns,
        ["install", "--source", str(source),
         "--preset", "core", "--preset", "slides"],
    )
    assert result.exit_code == 0, result.output
    target = project / ".claude" / "custom" / "streamtex-patterns"
    for name in ("ptn_alpha", "ptn_beta", "ptn_hero", "ptn_title"):
        assert (target / f"{name}.md").is_file()
    # Composite intent persisted to stx.toml
    text = (project / "stx.toml").read_text(encoding="utf-8")
    assert "presets = " in text
    assert "core" in text and "slides" in text


def test_install_cli_preset_plus_exclude(
    source: Path, tmp_path: Path, monkeypatch,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    runner = CliRunner()
    result = runner.invoke(
        patterns,
        ["install", "--source", str(source),
         "--preset", "core", "--exclude", "ptn_beta"],
    )
    assert result.exit_code == 0, result.output
    target = project / ".claude" / "custom" / "streamtex-patterns"
    assert (target / "ptn_alpha.md").is_file()
    assert not (target / "ptn_beta.md").exists()


def test_install_cli_preset_plus_individual(
    source: Path, tmp_path: Path, monkeypatch,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    runner = CliRunner()
    result = runner.invoke(
        patterns,
        ["install", "--source", str(source),
         "--preset", "slides", "--pattern", "ptn_alpha"],
    )
    assert result.exit_code == 0, result.output
    target = project / ".claude" / "custom" / "streamtex-patterns"
    # slides preset → ptn_hero, ptn_title
    # individual → ptn_alpha
    for name in ("ptn_alpha", "ptn_hero", "ptn_title"):
        assert (target / f"{name}.md").is_file()
    assert not (target / "ptn_beta.md").exists()


def test_install_cli_all_with_exclude(
    source: Path, tmp_path: Path, monkeypatch,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    runner = CliRunner()
    result = runner.invoke(
        patterns,
        ["install", "--source", str(source),
         "--all", "--exclude", "ptn_hero,ptn_title"],
    )
    assert result.exit_code == 0, result.output
    target = project / ".claude" / "custom" / "streamtex-patterns"
    assert (target / "ptn_alpha.md").is_file()
    assert (target / "ptn_beta.md").is_file()
    assert not (target / "ptn_hero.md").exists()
    assert not (target / "ptn_title.md").exists()


def test_install_cli_all_exclusive_with_preset(
    source: Path, tmp_path: Path, monkeypatch,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    runner = CliRunner()
    result = runner.invoke(
        patterns,
        ["install", "--source", str(source),
         "--all", "--preset", "core"],
    )
    assert result.exit_code != 0
    assert "exclusive" in result.output.lower()


def test_install_cli_all_exclusive_with_pattern(
    source: Path, tmp_path: Path, monkeypatch,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    runner = CliRunner()
    result = runner.invoke(
        patterns,
        ["install", "--source", str(source),
         "--all", "--pattern", "ptn_alpha"],
    )
    assert result.exit_code != 0
    assert "exclusive" in result.output.lower()
