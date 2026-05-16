"""Tests for the interactive pattern picker and its catalog helper."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from streamtex.cli.patterns_cmd import patterns
from streamtex.patterns.picker import (
    InteractiveAborted,
    collect_pattern_catalog,
    filter_by_tag,
    select_patterns_interactively,
)

# ---------------------------------------------------------------------------
# Fixtures — small but valid patterns source
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
def fake_source(tmp_path: Path) -> Path:
    src = tmp_path / "src-patterns"
    src.mkdir()
    (src / "manifest.toml").write_text(_MANIFEST, encoding="utf-8")
    _write_pattern(src / "core", "ptn_alpha", "Alpha atom", "atom, layout")
    _write_pattern(src / "core", "ptn_beta", "Beta atom", "atom, text")
    _write_pattern(src / "slides", "ptn_hero", "Hero slide", "slide, hero")
    (src / "presets").mkdir()
    (src / "presets" / "core.toml").write_text(
        "[patterns]\ninclude = [\"core/*.md\"]\n", encoding="utf-8",
    )
    return src


# ---------------------------------------------------------------------------
# collect_pattern_catalog
# ---------------------------------------------------------------------------

def test_collect_catalog_returns_one_entry_per_pattern(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    names = [e.name for e in catalog]
    assert names == sorted(["ptn_alpha", "ptn_beta", "ptn_hero"])
    # Scope correctly derived from folder
    scope_of = {e.name: e.scope for e in catalog}
    assert scope_of["ptn_alpha"] == "core"
    assert scope_of["ptn_hero"] == "slides"


def test_collect_catalog_parses_frontmatter(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    hero = next(e for e in catalog if e.name == "ptn_hero")
    assert hero.description == "Hero slide"
    assert "slide" in hero.tags
    assert hero.extrapolable is True


def test_collect_catalog_skips_malformed(fake_source: Path) -> None:
    # Add a broken pattern: no frontmatter
    (fake_source / "core" / "ptn_broken.md").write_text("# nope\n", encoding="utf-8")
    catalog = collect_pattern_catalog(fake_source)
    assert "ptn_broken" not in [e.name for e in catalog]
    # the three valid ones still load
    assert {e.name for e in catalog} == {"ptn_alpha", "ptn_beta", "ptn_hero"}


# ---------------------------------------------------------------------------
# filter_by_tag
# ---------------------------------------------------------------------------

def test_filter_by_tag_case_insensitive(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    out = filter_by_tag(catalog, "Atom")
    assert {e.name for e in out} == {"ptn_alpha", "ptn_beta"}


def test_filter_by_tag_returns_all_when_none(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    assert len(filter_by_tag(catalog, None)) == len(catalog)


def test_filter_by_tag_empty_when_no_match(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    assert filter_by_tag(catalog, "nonexistent") == []


# ---------------------------------------------------------------------------
# select_patterns_interactively (questionary mocked)
# ---------------------------------------------------------------------------

class _FakeAsk:
    """Stand-in for questionary's prompt object — captures choices for asserts."""

    def __init__(self, answer):
        self.answer = answer
        self.choices_seen = None

    def ask(self):
        return self.answer


def test_picker_returns_user_selection(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    fake = _FakeAsk(["ptn_alpha", "ptn_hero"])

    def _capture_checkbox(message, choices):
        # Sanity: choices include separators ('── core ──') and Choice objects
        titles = [getattr(c, "title", str(c)) for c in choices]
        assert any("core" in t for t in titles)
        return fake

    with patch("questionary.checkbox", side_effect=_capture_checkbox):
        chosen = select_patterns_interactively(catalog)
    assert chosen == ["ptn_alpha", "ptn_hero"]


def test_picker_pre_checks_installed(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)

    captured = {}

    def _capture_checkbox(message, choices):
        captured["choices"] = choices
        return _FakeAsk(["ptn_alpha"])

    with patch("questionary.checkbox", side_effect=_capture_checkbox):
        select_patterns_interactively(catalog, preselected={"ptn_alpha"})

    # Find ptn_alpha's Choice; checked must be True; the rest False.
    from questionary import Choice
    checked_by_name = {
        c.value: c.checked for c in captured["choices"] if isinstance(c, Choice)
    }
    assert checked_by_name["ptn_alpha"] is True
    assert checked_by_name["ptn_beta"] is False
    assert checked_by_name["ptn_hero"] is False


def test_picker_aborts_on_none(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    with patch("questionary.checkbox", return_value=_FakeAsk(None)):
        with pytest.raises(InteractiveAborted):
            select_patterns_interactively(catalog)


def test_picker_aborts_on_empty(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    with patch("questionary.checkbox", return_value=_FakeAsk([])):
        with pytest.raises(InteractiveAborted):
            select_patterns_interactively(catalog)


def test_picker_tag_filter_narrows_choices(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)

    captured = {}

    def _capture(message, choices):
        captured["choices"] = choices
        return _FakeAsk(["ptn_hero"])

    with patch("questionary.checkbox", side_effect=_capture):
        select_patterns_interactively(catalog, tag_filter="slide")

    from questionary import Choice, Separator
    visible_values = [
        c.value for c in captured["choices"]
        if isinstance(c, Choice) and not isinstance(c, Separator)
    ]
    assert visible_values == ["ptn_hero"]


def test_picker_empty_after_filter_aborts(fake_source: Path) -> None:
    catalog = collect_pattern_catalog(fake_source)
    with pytest.raises(InteractiveAborted):
        select_patterns_interactively(catalog, tag_filter="does-not-exist")


# ---------------------------------------------------------------------------
# install_cmd dispatch — TTY vs non-TTY
# ---------------------------------------------------------------------------

def test_install_cmd_refuses_no_selector_non_tty(
    fake_source: Path, tmp_path: Path, monkeypatch,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    runner = CliRunner()
    # CliRunner's stdin is not a TTY → should trigger the refusal path.
    result = runner.invoke(
        patterns, ["install", "--source", str(fake_source)],
    )
    assert result.exit_code != 0
    assert "not a terminal" in result.output


def test_install_cmd_interactive_writes_intent(
    fake_source: Path, tmp_path: Path, monkeypatch,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    # Force interactive path by overriding the helper (CliRunner replaces
    # sys.stdin with a non-tty stream).
    monkeypatch.setattr("streamtex.cli.patterns_cmd._is_interactive", lambda: True)

    # The composite picker shows a menu (questionary.select) then opens
    # sub-prompts (questionary.checkbox). Simulate:
    #   1. select → "add_individual"
    #   2. checkbox of available patterns → ["ptn_alpha", "ptn_hero"]
    #   3. select → "done"
    menu_answers = iter(["add_individual", "done"])
    individuals_picked = _FakeAsk(["ptn_alpha", "ptn_hero"])
    with (
        patch("questionary.select",
              side_effect=lambda *a, **kw: _FakeAsk(next(menu_answers))),
        patch("questionary.checkbox", return_value=individuals_picked),
    ):
        runner = CliRunner()
        result = runner.invoke(
            patterns, ["install", "--source", str(fake_source)],
        )
    assert result.exit_code == 0, result.output
    # The two picked patterns ended up on disk
    target = project / ".claude" / "custom" / "streamtex-patterns"
    assert (target / "ptn_alpha.md").is_file()
    assert (target / "ptn_hero.md").is_file()
    assert not (target / "ptn_beta.md").exists()
    # Intent persisted to stx.toml as v3 composite selection.
    stx_text = (project / "stx.toml").read_text(encoding="utf-8")
    assert "[patterns.selection]" in stx_text
    assert "individuals = " in stx_text
    assert "ptn_alpha" in stx_text and "ptn_hero" in stx_text
