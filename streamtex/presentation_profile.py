"""Presentation profiles — named display configurations.

A ``PresentationProfile`` bundles a name and all presentation settings
(mode, layout, wrap, breaks) into a single switchable unit.  Users define
a list of profiles in ``book.py`` and switch between them at runtime via
the sidebar or the floating navigation bar.

A ``ProfileConfig`` wraps a named list of profiles and provides JSON
serialization for configuration export/import.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import streamlit as st

from .slide import SlideBreakMode

if TYPE_CHECKING:
    from collections.abc import Callable


# ── Enums ─────────────────────────────────────────────────────────────────


class ViewMode(Enum):
    """Document view mode."""

    PAGINATED = "Paginated"
    CONTINUOUS = "Continuous"


# ── Data classes ──────────────────────────────────────────────────────────


@dataclass
class PageLayout:
    """Physical page dimensions.

    No range limits — all numeric values are accepted.
    The CSS renderer handles edge cases gracefully:

    - ``width > 100``: horizontal scroll
    - ``zoom < 100``: content shrinks (ideal for mobile simulation)
    - ``zoom > 100``: content grows, user scrolls
    - Negative values: CSS treats them as-is (overlap effects)
    - ``zoom = "fit"``: auto-fit content to viewport height (JS-based)
    """

    width: int = 90
    """Page width as % of browser viewport.  No min/max."""

    zoom: int | str = 100
    """CSS zoom level as %, or ``"fit"`` for auto-fit to viewport.  No min/max."""


@dataclass
class SlideBreakDisplayConfig:
    """Slide break settings within a presentation profile."""

    enabled: bool = True
    """Whether slide breaks are rendered."""

    mode: SlideBreakMode = SlideBreakMode.FULL
    """Display mode: FULL, RULE_ONLY, SPACER_ONLY, MARKER_ONLY, HIDDEN."""

    space: int = 60
    """Vertical spacing in vh units.  No min/max."""


@dataclass
class PresentationProfile:
    """A named presentation configuration.

    Each field maps to a sidebar control in ``st_book()``.  All fields
    have sensible defaults — the user only overrides what matters for
    that profile.
    """

    name: str
    """Unique profile name displayed in sidebar and floating bar."""

    mode: ViewMode = ViewMode.PAGINATED
    """Paginated (one block at a time) or Continuous (full scroll)."""

    layout: PageLayout = field(default_factory=PageLayout)
    """Page dimensions: width % and zoom %."""

    wrap: bool = True
    """Global code-block wrapping toggle."""

    breaks: SlideBreakDisplayConfig = field(
        default_factory=SlideBreakDisplayConfig,
    )
    """Slide break appearance and spacing."""

    # ── Factory presets (Phase 2) ─────────────────────────────────────

    @classmethod
    def responsive_preset(cls) -> list[PresentationProfile]:
        """Return ``[Desktop, Tablet, Mobile]`` with sensible defaults."""
        return [
            cls(name="Desktop", layout=PageLayout(width=90, zoom=100)),
            cls(name="Tablet", layout=PageLayout(width=65, zoom=80)),
            cls(
                name="Mobile",
                layout=PageLayout(width=100, zoom=60),
                breaks=SlideBreakDisplayConfig(enabled=False),
            ),
        ]

    @classmethod
    def presentation_preset(cls) -> list[PresentationProfile]:
        """Return ``[Presenter, Audience, Handout]`` for slide decks."""
        return [
            cls(
                name="Presenter",
                mode=ViewMode.PAGINATED,
                layout=PageLayout(width=100, zoom=100),
                breaks=SlideBreakDisplayConfig(
                    mode=SlideBreakMode.FULL,
                    space=100,
                ),
            ),
            cls(
                name="Audience",
                mode=ViewMode.PAGINATED,
                layout=PageLayout(width=90, zoom=100),
            ),
            cls(
                name="Handout",
                mode=ViewMode.CONTINUOUS,
                layout=PageLayout(width=80, zoom=90),
                breaks=SlideBreakDisplayConfig(enabled=False),
            ),
        ]

    @classmethod
    def desktop_mobile_preset(cls) -> list[PresentationProfile]:
        """Return standard ``[Desktop, Mobile]`` pair for manuals/templates."""
        return [
            cls(name="Desktop", layout=PageLayout(width=90, zoom=100)),
            cls(
                name="Mobile",
                layout=PageLayout(width=100, zoom=60),
                breaks=SlideBreakDisplayConfig(enabled=False),
            ),
        ]


# ── Session state keys ────────────────────────────────────────────────────

_ACTIVE_PROFILE_KEY = "_stx_active_profile"

# SlideBreakMode → sidebar label mapping (mirrors slide.py label→enum)
_MODE_LABELS: dict[SlideBreakMode, str] = {
    SlideBreakMode.FULL: "Full",
    SlideBreakMode.RULE_ONLY: "Rule only",
    SlideBreakMode.SPACER_ONLY: "Spacer only",
}


# ── Centralized field mapping (DRY) ──────────────────────────────────────

def _get_field_mapping() -> list[tuple[str, Callable]]:
    """Return ``[(session_key, extractor(profile))]`` pairs.

    Lazy import to avoid circular dependencies between modules.
    This mapping is the **single source of truth** for both
    :func:`apply_profile` and :func:`is_profile_modified`.
    """
    from .book import _STX_VIEW_MODE_KEY
    from .code import _WRAP_ALL_KEY
    from .slide import _BREAK_ENABLED_KEY, _BREAK_MODE_KEY, _BREAK_SPACE_KEY
    from .zoom import _PAGE_WIDTH_KEY, _ZOOM_KEY

    return [
        (_STX_VIEW_MODE_KEY, lambda p: p.mode.value),
        (_PAGE_WIDTH_KEY, lambda p: p.layout.width),
        (_ZOOM_KEY, lambda p: p.layout.zoom),
        (_WRAP_ALL_KEY, lambda p: p.wrap),
        (_BREAK_ENABLED_KEY, lambda p: p.breaks.enabled),
        (_BREAK_MODE_KEY, lambda p: _MODE_LABELS.get(p.breaks.mode, "Full")),
        (_BREAK_SPACE_KEY, lambda p: p.breaks.space),
    ]


def apply_profile(profile: PresentationProfile) -> None:
    """Write a profile's values into ``session_state``.

    Called when the user selects or re-selects (reset) a profile.
    Uses :func:`_get_field_mapping` as single source of truth.
    """
    for key, extractor in _get_field_mapping():
        st.session_state[key] = extractor(profile)
    st.session_state[_ACTIVE_PROFILE_KEY] = profile.name
    # Sync the "Fit to page" toggle with the zoom value
    from .zoom import _ZOOM_FIT_KEY
    st.session_state[_ZOOM_FIT_KEY] = profile.layout.zoom == "fit"


def is_profile_modified(profile: PresentationProfile) -> bool:
    """Return ``True`` if current ``session_state`` differs from *profile*.

    Uses :func:`_get_field_mapping` as single source of truth.
    """
    return any(
        st.session_state.get(key) != extractor(profile)
        for key, extractor in _get_field_mapping()
    )


def build_default_profile(
    page_width: int = 90,
    zoom: int = 100,
    paginate: bool = False,
) -> PresentationProfile:
    """Build the implicit ``"Default"`` profile from ``st_book()`` params."""
    return PresentationProfile(
        name="Default",
        mode=ViewMode.PAGINATED if paginate else ViewMode.CONTINUOUS,
        layout=PageLayout(width=page_width, zoom=zoom),
    )


# ── ProfileConfig — JSON serialization (Phase 3) ─────────────────────────


@dataclass
class ProfileConfig:
    """A complete, serializable display configuration.

    Bundles a name and a list of :class:`PresentationProfile` instances.
    Can be serialized to/from JSON for sharing and reuse.

    .. note::

       Only layout settings are serializable.  Style overrides (Phase 5)
       remain Python-only and are **not** included in the JSON output.
    """

    name: str
    """Human-readable configuration name."""

    profiles: list[PresentationProfile]
    """The list of profiles in this configuration."""

    def to_dict(self) -> dict:
        """Serialize to a plain dict."""
        return {
            "name": self.name,
            "version": 1,
            "profiles": [
                {
                    "name": p.name,
                    "mode": p.mode.value,
                    "layout": {
                        "width": p.layout.width,
                        "zoom": p.layout.zoom,
                    },
                    "wrap": p.wrap,
                    "breaks": {
                        "enabled": p.breaks.enabled,
                        "mode": _MODE_LABELS.get(p.breaks.mode, "Full"),
                        "space": p.breaks.space,
                    },
                }
                for p in self.profiles
            ],
        }

    def to_json(self) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def save(self, path: str | Path) -> None:
        """Save configuration to a JSON file."""
        Path(path).write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> ProfileConfig:
        """Load configuration from a JSON file."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls._from_dict(data)

    @classmethod
    def from_json(cls, json_str: str) -> ProfileConfig:
        """Load configuration from a JSON string."""
        return cls._from_dict(json.loads(json_str))

    @classmethod
    def _from_dict(cls, data: dict) -> ProfileConfig:
        """Deserialize from a plain dict."""
        # Reverse label→enum mapping
        label_to_mode = {v: k for k, v in _MODE_LABELS.items()}

        profiles: list[PresentationProfile] = []
        for p_data in data.get("profiles", []):
            layout_data = p_data.get("layout", {})
            breaks_data = p_data.get("breaks", {})
            layout = PageLayout(
                width=layout_data.get("width", 90),
                zoom=layout_data.get("zoom", 100),
            )
            breaks = SlideBreakDisplayConfig(
                enabled=breaks_data.get("enabled", True),
                mode=label_to_mode.get(
                    breaks_data.get("mode", "Full"),
                    SlideBreakMode.FULL,
                ),
                space=breaks_data.get("space", 60),
            )
            profiles.append(
                PresentationProfile(
                    name=p_data.get("name", "Unnamed"),
                    mode=ViewMode(p_data.get("mode", "Paginated")),
                    layout=layout,
                    wrap=p_data.get("wrap", True),
                    breaks=breaks,
                ),
            )
        return cls(name=data.get("name", "Unnamed"), profiles=profiles)
