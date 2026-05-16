"""Tests for ``.patterns-meta.json`` schema v3 + project_toml selection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from streamtex.patterns import (
    SUPPORTED_SCHEMA_VERSIONS,
    MetaError,
    __version_schema__,
)
from streamtex.patterns.manifest import (
    EFFECTIVE_MODES,
    PatternRecord,
    PatternSelection,
    PatternsMeta,
    load_meta,
    save_meta,
)
from streamtex.patterns.project_toml import (
    read_project_selection,
    write_project_selection,
)

# ---------------------------------------------------------------------------
# Schema version constants
# ---------------------------------------------------------------------------

def test_schema_version_is_v3() -> None:
    assert __version_schema__ == 3
    assert SUPPORTED_SCHEMA_VERSIONS == (1, 2, 3)


def test_effective_modes_constants() -> None:
    assert set(EFFECTIVE_MODES) == {"empty", "preset", "individual", "all", "composite"}


# ---------------------------------------------------------------------------
# PatternSelection construction & validation
# ---------------------------------------------------------------------------

def test_empty_selection_has_empty_mode() -> None:
    sel = PatternSelection()
    assert sel.is_empty()
    assert sel.effective_mode == "empty"
    assert sel.presets == sel.individuals == sel.excludes == ()
    assert sel.all_flag is False


def test_selection_all_flag_classified_all() -> None:
    sel = PatternSelection(all_flag=True)
    assert sel.effective_mode == "all"
    assert not sel.is_empty()


def test_selection_single_preset_classified_preset() -> None:
    sel = PatternSelection(presets=("slides",))
    assert sel.effective_mode == "preset"


def test_selection_multi_preset_classified_composite() -> None:
    sel = PatternSelection(presets=("slides", "docs"))
    assert sel.effective_mode == "composite"


def test_selection_individuals_only_classified_individual() -> None:
    sel = PatternSelection(individuals=("ptn_a", "ptn_b"))
    assert sel.effective_mode == "individual"


def test_selection_mix_classified_composite() -> None:
    sel = PatternSelection(presets=("slides",), individuals=("ptn_x",))
    assert sel.effective_mode == "composite"


def test_all_flag_exclusive_with_presets() -> None:
    with pytest.raises(MetaError):
        PatternSelection(all_flag=True, presets=("X",))


def test_all_flag_exclusive_with_individuals() -> None:
    with pytest.raises(MetaError):
        PatternSelection(all_flag=True, individuals=("ptn_x",))


def test_all_flag_with_excludes_is_allowed() -> None:
    # all + excludes is the natural way to express "everything except these".
    sel = PatternSelection(all_flag=True, excludes=("ptn_takeaways",))
    assert sel.effective_mode == "all"


def test_selection_coerces_lists_to_tuples() -> None:
    sel = PatternSelection(presets=["a", "b"], individuals=["c"])
    assert sel.presets == ("a", "b")
    assert sel.individuals == ("c",)


# ---------------------------------------------------------------------------
# Round-trip + back-compat read
# ---------------------------------------------------------------------------

def test_v3_round_trip_via_to_dict_from_dict() -> None:
    sel = PatternSelection(
        presets=("slides", "docs"),
        individuals=("ptn_extra",),
        excludes=("ptn_takeaways",),
    )
    restored = PatternSelection.from_dict(sel.to_dict())
    assert restored == sel


def test_from_dict_accepts_v2_mode_items() -> None:
    # v2 shape — must migrate cleanly into v3 fields.
    sel = PatternSelection.from_dict({"mode": "preset", "items": ["docs"]})
    assert sel.presets == ("docs",)
    assert sel.individuals == sel.excludes == ()
    assert sel.all_flag is False


def test_from_dict_accepts_v2_individual() -> None:
    sel = PatternSelection.from_dict({"mode": "individual", "items": ["a", "b"]})
    assert sel.individuals == ("a", "b")


def test_from_dict_accepts_v2_all() -> None:
    sel = PatternSelection.from_dict({"mode": "all", "items": []})
    assert sel.all_flag is True


def test_from_legacy_rejects_unknown_mode() -> None:
    with pytest.raises(MetaError):
        PatternSelection.from_legacy(mode="bogus", items=())


# ---------------------------------------------------------------------------
# .patterns-meta.json migration v1 → v3
# ---------------------------------------------------------------------------

def _write_v1_meta(target: Path, *, preset: str | None) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "source": "../../streamtex-patterns",
        "source_commit": "abc123",
        "preset": preset,
        "mode": "copy",
        "installed_at": "2026-05-10T00:00:00Z",
        "patterns": [
            {
                "name": "ptn_alpha",
                "from": "core/ptn_alpha.md",
                "sha": "0" * 64,
                "installed_sha": "0" * 64,
            },
        ],
    }
    path = target / ".patterns-meta.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_v1_meta_with_preset_infers_selection(tmp_path: Path) -> None:
    target = tmp_path / ".claude" / "custom" / "streamtex-patterns"
    _write_v1_meta(target, preset="slides")
    meta = load_meta(target)
    assert meta.schema_version == 3  # upgraded in-memory all the way to v3
    assert meta.selection is not None
    assert meta.selection.presets == ("slides",)
    assert meta.selection.effective_mode == "preset"
    assert meta.preset == "slides"
    assert len(meta.patterns) == 1


def test_load_v1_meta_without_preset_leaves_selection_none(tmp_path: Path) -> None:
    target = tmp_path / "patterns"
    _write_v1_meta(target, preset=None)
    meta = load_meta(target)
    assert meta.schema_version == 3
    assert meta.selection is None


def _write_v2_meta(target: Path, mode: str, items: list[str]) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 2,
        "source": "../../streamtex-patterns",
        "source_commit": "abc",
        "preset": None,
        "mode": "copy",
        "installed_at": "2026-05-10T00:00:00Z",
        "patterns": [],
        "selection": {"mode": mode, "items": items},
    }
    path = target / ".patterns-meta.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_v2_meta_migrates_to_v3(tmp_path: Path) -> None:
    target = tmp_path / "patterns"
    _write_v2_meta(target, mode="individual", items=["ptn_a", "ptn_b"])
    meta = load_meta(target)
    assert meta.schema_version == 3
    assert meta.selection == PatternSelection(individuals=("ptn_a", "ptn_b"))


def test_load_v3_meta_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "patterns"
    target.mkdir()
    meta = PatternsMeta(
        schema_version=3,
        source="../../streamtex-patterns",
        source_commit="deadbeef",
        preset=None,
        mode="copy",
        installed_at="2026-05-16T10:00:00Z",
        patterns=[
            PatternRecord(
                name="ptn_x",
                from_="core/ptn_x.md",
                sha="a" * 64,
                installed_sha="a" * 64,
            ),
        ],
        selection=PatternSelection(
            presets=("slides",),
            individuals=("ptn_extra",),
            excludes=("ptn_drop",),
        ),
    )
    save_meta(target, meta)
    reloaded = load_meta(target)
    assert reloaded.selection == meta.selection
    assert reloaded.schema_version == 3


def test_load_meta_rejects_unknown_schema(tmp_path: Path) -> None:
    target = tmp_path / "patterns"
    target.mkdir()
    (target / ".patterns-meta.json").write_text(
        json.dumps({"schema_version": 99, "patterns": []}), encoding="utf-8",
    )
    with pytest.raises(MetaError):
        load_meta(target)


# ---------------------------------------------------------------------------
# project_toml: write / read / round-trip with v3
# ---------------------------------------------------------------------------

def test_write_then_read_v3_selection_stx_toml(tmp_path: Path) -> None:
    sel = PatternSelection(individuals=("ptn_a", "ptn_b"))
    written = write_project_selection(tmp_path, sel, source="./streamtex-patterns")
    assert written.name == "stx.toml"
    assert read_project_selection(tmp_path) == sel
    # Source preserved on a second write (should not duplicate).
    sel2 = PatternSelection(presets=("slides",))
    write_project_selection(tmp_path, sel2)
    content = written.read_text(encoding="utf-8")
    assert content.count('source = ') == 1
    assert read_project_selection(tmp_path) == sel2


def test_write_composite_selection(tmp_path: Path) -> None:
    sel = PatternSelection(
        presets=("slides", "docs"),
        individuals=("ptn_inline_emphasis",),
        excludes=("ptn_takeaways",),
    )
    write_project_selection(tmp_path, sel)
    text = (tmp_path / "stx.toml").read_text(encoding="utf-8")
    assert "[patterns.selection]" in text
    assert "presets = " in text
    assert "individuals = " in text
    assert "excludes = " in text
    assert "all = false" in text
    assert read_project_selection(tmp_path) == sel


def test_write_preserves_other_keys_in_stx_toml(tmp_path: Path) -> None:
    stx = tmp_path / "stx.toml"
    stx.write_text(
        "[workspace]\nname = \"demo\"\n\n[patterns]\nsource = \"./X\"\n",
        encoding="utf-8",
    )
    sel = PatternSelection(all_flag=True)
    write_project_selection(tmp_path, sel)
    text = stx.read_text(encoding="utf-8")
    assert "[workspace]" in text
    assert 'name = "demo"' in text
    assert read_project_selection(tmp_path) == sel


def test_read_shortcut_preset(tmp_path: Path) -> None:
    (tmp_path / "stx.toml").write_text(
        "[patterns]\npreset = \"core\"\n", encoding="utf-8",
    )
    assert read_project_selection(tmp_path) == PatternSelection(presets=("core",))


def test_read_shortcut_selected_list(tmp_path: Path) -> None:
    (tmp_path / "stx.toml").write_text(
        "[patterns]\nselected = [\"ptn_a\", \"ptn_b\"]\n", encoding="utf-8",
    )
    assert read_project_selection(tmp_path) == PatternSelection(
        individuals=("ptn_a", "ptn_b"),
    )


def test_read_shortcut_all(tmp_path: Path) -> None:
    (tmp_path / "stx.toml").write_text(
        "[patterns]\nall = true\n", encoding="utf-8",
    )
    assert read_project_selection(tmp_path) == PatternSelection(all_flag=True)


def test_read_v2_shape_in_stx_toml(tmp_path: Path) -> None:
    # Still accept the v2 mode/items shape in stx.toml — it's migrated on read.
    (tmp_path / "stx.toml").write_text(
        "[patterns.selection]\nmode = \"individual\"\nitems = [\"x\", \"y\"]\n",
        encoding="utf-8",
    )
    assert read_project_selection(tmp_path) == PatternSelection(
        individuals=("x", "y"),
    )


def test_write_removes_legacy_shortcuts(tmp_path: Path) -> None:
    (tmp_path / "stx.toml").write_text(
        "[patterns]\npreset = \"core\"\nselected = [\"x\"]\nall = true\n",
        encoding="utf-8",
    )
    sel = PatternSelection(individuals=("ptn_z",))
    write_project_selection(tmp_path, sel)
    text = (tmp_path / "stx.toml").read_text(encoding="utf-8")
    assert "preset = " not in text
    assert "all = true" not in text
    assert read_project_selection(tmp_path) == sel


def test_read_returns_none_when_no_config(tmp_path: Path) -> None:
    assert read_project_selection(tmp_path) is None


def test_read_pyproject_tool_patterns(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.patterns]\npreset = \"docs\"\n", encoding="utf-8",
    )
    assert read_project_selection(tmp_path) == PatternSelection(presets=("docs",))


def test_stx_toml_precedence_over_pyproject(tmp_path: Path) -> None:
    (tmp_path / "stx.toml").write_text(
        "[patterns]\npreset = \"slides\"\n", encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        "[tool.patterns]\npreset = \"docs\"\n", encoding="utf-8",
    )
    assert read_project_selection(tmp_path) == PatternSelection(presets=("slides",))
