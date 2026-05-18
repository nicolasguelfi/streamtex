"""Tests for streamtex.core.discovery — lifecycle states, resolution, helpers."""

import textwrap
from pathlib import Path

import pytest

from streamtex.core import discovery


def _write_stx_toml(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content))


# ---------------------------------------------------------------------------
# get_primary_local_pack
# ---------------------------------------------------------------------------


def test_get_primary_local_pack_none(tmp_path: Path):
    _write_stx_toml(
        tmp_path / "stx.toml",
        """\
        [project]
        name = "x"
        """,
    )
    assert discovery.get_primary_local_pack(tmp_path / "stx.toml") is None


def test_get_primary_local_pack_unique(tmp_path: Path):
    _write_stx_toml(
        tmp_path / "stx.toml",
        """\
        [[packs]]
        type = "local"
        name = "mypack"
        path = "./mypack"
        primary = true
        [[packs]]
        type = "local"
        name = "experiments"
        path = "./experiments"
        primary = false
        """,
    )
    primary = discovery.get_primary_local_pack(tmp_path / "stx.toml")
    assert primary is not None
    assert primary["name"] == "mypack"


def test_get_primary_local_pack_duplicate_raises(tmp_path: Path):
    _write_stx_toml(
        tmp_path / "stx.toml",
        """\
        [[packs]]
        type = "local"
        name = "a"
        path = "./a"
        primary = true
        [[packs]]
        type = "local"
        name = "b"
        path = "./b"
        primary = true
        """,
    )
    with pytest.raises(discovery.PackResolutionError) as exc:
        discovery.get_primary_local_pack(tmp_path / "stx.toml")
    assert exc.value.code == "PR005"


# ---------------------------------------------------------------------------
# discover_packs — drift / indirect / collision
# ---------------------------------------------------------------------------


def test_discover_drift_install(tmp_path: Path):
    """State 2 — declared in stx.toml but no entry point installed."""
    _write_stx_toml(
        tmp_path / "stx.toml",
        """\
        [[packs]]
        type = "git"
        name = "nonexistent-pack"
        ref = "github.com/x/nonexistent-pack"
        rev = "v0.0.0"
        """,
    )
    packs = discovery.discover_packs(tmp_path / "stx.toml")
    drift = [p for p in packs if p.state == "drift_install"]
    assert len(drift) == 1
    assert drift[0].name == "nonexistent-pack"
    assert any("PR002" in iss for iss in drift[0].issues)


def test_discover_no_stx_toml_returns_only_indirect():
    """No stx.toml — anything found via entry points becomes 'indirect'."""
    packs = discovery.discover_packs(None)
    for p in packs:
        assert p.state in ("indirect",)


# ---------------------------------------------------------------------------
# resolve_component — prefer is a sort
# ---------------------------------------------------------------------------


def test_resolve_component_not_found_raises():
    with pytest.raises(discovery.PackResolutionError) as exc:
        discovery.resolve_component("nonexistent", packs=[], prefer=None)
    assert exc.value.code == "PR006"


# ---------------------------------------------------------------------------
# get_bundle_attr
# ---------------------------------------------------------------------------


def test_get_bundle_attr_hit():
    class Bundle:
        info = "info-style"

    assert discovery.get_bundle_attr(Bundle, "info", "callout") == "info-style"


def test_get_bundle_attr_miss_raises():
    class Bundle:
        pass

    with pytest.raises(discovery.BundleMissingError) as exc:
        discovery.get_bundle_attr(Bundle, "info", "callout")
    assert exc.value.code == "BV001"
    assert "callout" in str(exc.value)
    assert "info" in str(exc.value)


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


def test_exception_hierarchy():
    assert issubclass(discovery.PackResolutionError, discovery.ReuseArchitectureError)
    assert issubclass(discovery.PackManifestError, discovery.ReuseArchitectureError)
    assert issubclass(discovery.KitResolutionError, discovery.ReuseArchitectureError)
    assert issubclass(discovery.ComponentValidationError, discovery.ReuseArchitectureError)
    assert issubclass(discovery.BundleMissingError, discovery.ReuseArchitectureError)


def test_trace_entry_dataclass():
    entry = discovery.TraceEntry("mypack", "declared", "from stx.toml")
    assert entry.pack_name == "mypack"
    assert entry.transition == "declared"
    assert entry.detail == "from stx.toml"
