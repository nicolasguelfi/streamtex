"""Tests for the opt-in design-patterns prompt at the end of `stx install`.

We exercise the private helper ``_maybe_offer_patterns`` directly: spinning
a full ``stx install --project ...`` E2E would require git, uv, and a
template repo, which the helper itself does not.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from streamtex.cli.install_cmd import _maybe_offer_patterns

# Tiny fixture: a valid streamtex-patterns source repo.

_MANIFEST = """\
[repo]
name = "streamtex-patterns"
version = "0.1.0"
description = "fixture"
spec_version = "A2"
since = "2026-05-10"

[scopes]
core = "Universal"

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


def _write_patterns_source(at: Path) -> None:
    at.mkdir(parents=True, exist_ok=True)
    (at / "manifest.toml").write_text(_MANIFEST, encoding="utf-8")
    (at / "core").mkdir()
    for name, desc, tags in [
        ("ptn_alpha", "Alpha", "atom, layout"),
        ("ptn_beta", "Beta", "atom, text"),
    ]:
        (at / "core" / f"{name}.md").write_text(
            _PATTERN_TEMPLATE.format(name=name, description=desc, tags=tags),
            encoding="utf-8",
        )
    (at / "presets").mkdir()
    (at / "presets" / "core.toml").write_text(
        '[patterns]\ninclude = ["core/*.md"]\n', encoding="utf-8",
    )


def _make_workspace_with_project(tmp_path: Path, project: str = "p1") -> Path:
    """Build <ws_root>/{stx.toml, projects/<project>/} and return ws_root."""
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(
        '[workspace]\nname = "demo"\npreset = "standard"\n', encoding="utf-8",
    )
    (ws / "projects" / project).mkdir(parents=True)
    return ws


class _FakeAsk:
    def __init__(self, answer):
        self.answer = answer

    def ask(self):
        return self.answer


class _RecordingConsole:
    """Tiny console that records `.print(...)` calls instead of writing."""

    def __init__(self):
        self.lines: list[str] = []

    def print(self, *args, **kwargs):
        self.lines.append(" ".join(str(a) for a in args))

    @property
    def output(self) -> str:
        return "\n".join(self.lines)


# ---------------------------------------------------------------------------
# Non-TTY / --no-patterns short-circuits
# ---------------------------------------------------------------------------

def test_non_tty_skips_silently(tmp_path: Path, monkeypatch) -> None:
    ws = _make_workspace_with_project(tmp_path)
    monkeypatch.setattr(
        "streamtex.cli.install_cmd._install_is_interactive", lambda: False,
    )
    console = _RecordingConsole()
    # Should be a no-op (no print, no confirm).
    with patch("click.confirm", side_effect=AssertionError("must not prompt")):
        _maybe_offer_patterns(str(ws), "p1", console)
    assert console.output == ""


# ---------------------------------------------------------------------------
# Stage 1 (clone) — declined
# ---------------------------------------------------------------------------

def test_user_declines_clone(tmp_path: Path, monkeypatch) -> None:
    ws = _make_workspace_with_project(tmp_path)
    monkeypatch.setattr(
        "streamtex.cli.install_cmd._install_is_interactive", lambda: True,
    )
    console = _RecordingConsole()
    with patch("click.confirm", return_value=False) as confirm_mock:
        _maybe_offer_patterns(str(ws), "p1", console)
    # Only one prompt should have been shown (Stage 1).
    assert confirm_mock.call_count == 1
    assert "Skipped" in console.output
    # No clone happened.
    assert not (ws / "streamtex-patterns").exists()


# ---------------------------------------------------------------------------
# Stage 1 accepted, Stage 2 declined
# ---------------------------------------------------------------------------

def test_user_accepts_clone_declines_install(
    tmp_path: Path, monkeypatch,
) -> None:
    ws = _make_workspace_with_project(tmp_path)
    monkeypatch.setattr(
        "streamtex.cli.install_cmd._install_is_interactive", lambda: True,
    )
    # Pretend clone succeeds by populating the target directly.
    patterns_dir = ws / "streamtex-patterns"

    def fake_clone(url, target, branch=None, force=False, timeout_s=180):
        _write_patterns_source(patterns_dir)
        return patterns_dir

    console = _RecordingConsole()
    answers = iter([True, False])  # Stage1=yes, Stage2=no
    with (
        patch("click.confirm", side_effect=lambda *a, **kw: next(answers)),
        patch(
            "streamtex.patterns.installer.clone_patterns_source",
            side_effect=fake_clone,
        ),
    ):
        _maybe_offer_patterns(str(ws), "p1", console)
    # The clone happened (fixture created the dir).
    assert patterns_dir.is_dir()
    # No install happened: project has no .patterns-meta.json.
    proj_meta = ws / "projects" / "p1" / ".claude" / "custom" \
        / "streamtex-patterns" / ".patterns-meta.json"
    assert not proj_meta.exists()
    assert "Cloned" in console.output


# ---------------------------------------------------------------------------
# Stage 1 unreachable + Stage 2 accepted (source already present, no clone needed)
# ---------------------------------------------------------------------------

def test_user_accepts_install_when_source_already_present(
    tmp_path: Path, monkeypatch,
) -> None:
    ws = _make_workspace_with_project(tmp_path)
    # Pre-populate the sibling source so trace_source matches L4 immediately.
    _write_patterns_source(ws / "streamtex-patterns")
    monkeypatch.setattr(
        "streamtex.cli.install_cmd._install_is_interactive", lambda: True,
    )

    console = _RecordingConsole()
    # The composite picker requires two questionary.select answers and one
    # checkbox answer to install ptn_alpha:
    #   1. menu → "add_individual"
    #   2. checkbox of patterns → ["ptn_alpha"]
    #   3. menu → "done"
    menu_answers = iter(["add_individual", "done"])
    fake_checkbox = _FakeAsk(["ptn_alpha"])
    with (
        patch("click.confirm", return_value=True) as confirm_mock,
        patch("questionary.select",
              side_effect=lambda *a, **kw: _FakeAsk(next(menu_answers))),
        patch("questionary.checkbox", return_value=fake_checkbox),
    ):
        _maybe_offer_patterns(str(ws), "p1", console)
    assert confirm_mock.call_count == 1

    # Pattern was installed.
    target = ws / "projects" / "p1" / ".claude" / "custom" / "streamtex-patterns"
    assert (target / "ptn_alpha.md").is_file()
    assert (target / ".patterns-meta.json").is_file()
    # Intent persisted in project's stx.toml.
    proj_stx = ws / "projects" / "p1" / "stx.toml"
    assert proj_stx.is_file()
    text = proj_stx.read_text(encoding="utf-8")
    assert "[patterns.selection]" in text
    assert "ptn_alpha" in text


# ---------------------------------------------------------------------------
# Clone failure → warning, no crash
# ---------------------------------------------------------------------------

def test_clone_failure_is_a_warning_not_a_crash(
    tmp_path: Path, monkeypatch,
) -> None:
    from streamtex.patterns import PatternError

    ws = _make_workspace_with_project(tmp_path)
    monkeypatch.setattr(
        "streamtex.cli.install_cmd._install_is_interactive", lambda: True,
    )

    def fake_clone(url, target, **kw):
        raise PatternError("simulated clone failure")

    console = _RecordingConsole()
    with (
        patch("click.confirm", return_value=True),
        patch(
            "streamtex.patterns.installer.clone_patterns_source",
            side_effect=fake_clone,
        ),
    ):
        _maybe_offer_patterns(str(ws), "p1", console)
    # No exception escaped; a warning was printed.
    assert "Clone failed" in console.output


# ---------------------------------------------------------------------------
# Missing project dir → silent no-op
# ---------------------------------------------------------------------------

def test_missing_project_is_silent_noop(tmp_path: Path, monkeypatch) -> None:
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text(
        '[workspace]\nname = "demo"\n', encoding="utf-8",
    )
    # no projects/p1
    monkeypatch.setattr(
        "streamtex.cli.install_cmd._install_is_interactive", lambda: True,
    )
    console = _RecordingConsole()
    with patch("click.confirm", side_effect=AssertionError("must not prompt")):
        _maybe_offer_patterns(str(ws), "p1", console)
    assert console.output == ""
