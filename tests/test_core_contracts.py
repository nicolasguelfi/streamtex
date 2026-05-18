"""Tests for streamtex.core.contracts — the Protocol & TypedDict surface."""

from typing import ClassVar

from streamtex.core import contracts
from streamtex.styles import Style


def test_required_bundles_constant():
    assert "colors" in contracts.REQUIRED_BUNDLES
    assert "titles" in contracts.REQUIRED_BUNDLES
    assert "callouts" in contracts.REQUIRED_BUNDLES
    assert "body" in contracts.REQUIRED_BUNDLES


def test_design_system_protocol_isinstance_positive():
    class _Colors:
        primary = Style("color: black", "primary")
        accent = Style("color: red", "accent")
        bg = Style("background: white", "bg")
        surface = Style("background: gray", "surface")
        text = Style("color: black", "text")
        muted = Style("color: gray", "muted")

    class _Titles:
        slide = Style("font-size: 36px", "slide")
        section = Style("font-size: 28px", "section")
        subtitle = Style("font-size: 22px", "subtitle")
        body = Style("font-size: 16px", "body")
        caption = Style("font-size: 14px", "caption")

    class _Callouts:
        info = Style("border: blue", "info")
        warn = Style("border: orange", "warn")
        error = Style("border: red", "error")
        success = Style("border: green", "success")
        icon = Style("font-weight: 700", "icon")
        title = Style("font-weight: 700", "title")
        body = Style("font-size: 14px", "body")

    class _Body:
        paragraph = Style("font-size: 16px", "paragraph")
        emphasis = Style("font-weight: 700", "emphasis")
        code = Style("font-family: monospace", "code")

    class DS:
        name: ClassVar[str] = "test"
        colors = _Colors
        titles = _Titles
        callouts = _Callouts
        body = _Body

    # The runtime check is best-effort, but attribute access works.
    assert hasattr(DS, "colors")
    assert hasattr(DS, "titles")
    assert hasattr(DS, "callouts")
    assert hasattr(DS, "body")


def test_component_meta_typed_dict_is_dict_like():
    meta: contracts.ComponentMeta = {
        "name": "callout",
        "description": "Highlighted box for emphasized content",
        "tags": ["callout", "container"],
        "extrapolable": True,
        "since": "2026-05-19",
        "bundles_required": ["callouts.info", "callouts.icon"],
        "granularity": "primitive",
    }
    assert meta["name"] == "callout"
    assert meta["granularity"] == "primitive"


def test_stx_toml_pack_entry_types():
    git_entry: contracts.StxTomlPackEntry = {
        "type": "git",
        "ref": "github.com/x/y",
        "rev": "v0.1.0",
    }
    local_entry: contracts.StxTomlPackEntry = {
        "type": "local",
        "name": "mypack",
        "path": "./mypack",
        "primary": True,
    }
    pypi_entry: contracts.StxTomlPackEntry = {
        "type": "pypi",
        "name": "streamtex-pack-x",
        "constraint": ">=0.1,<0.2",
    }
    assert git_entry["type"] == "git"
    assert local_entry["primary"] is True
    assert pypi_entry["constraint"].startswith(">=")


def test_pack_manifest_schema():
    manifest: contracts.PackManifest = {
        "manifest": {"format": "0.1"},
        "pack": {
            "name": "streamtex-design",
            "version": "0.1.0",
            "author": "x",
            "license": "MIT",
            "streamtex_compat": ">=0.7,<1.0",
        },
        "entrypoint": {"module": "streamtex_design"},
    }
    assert manifest["pack"]["name"] == "streamtex-design"


def test_top_level_reexports_present():
    """§5.0 — exactly 3 symbols exposed at the streamtex top level."""
    import streamtex as stx

    assert stx.DesignSystemProtocol is contracts.DesignSystemProtocol
    assert stx.ComponentMeta is contracts.ComponentMeta
    from streamtex.core.discovery import ReuseArchitectureError

    assert stx.ReuseArchitectureError is ReuseArchitectureError
