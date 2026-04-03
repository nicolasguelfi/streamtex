"""Section spacing — configurable margins around blocks and sections.

Provides two pure types — ``Spacing`` (value object for margins) and
``SpacingConfig`` (bundles block + section spacing) — plus DI functions
and a 5-level override hierarchy:

    Built-in → Book (global DI) → Profile → Block → Call-site
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .presentation_profile import PresentationProfile


# ── Data classes ──────────────────────────────────────────────────────────


@dataclass
class Spacing:
    """Margin box around content.  Pure value object, reusable in any context.

    All fields are optional.  ``None`` = inherit from parent level in the
    override hierarchy.  When all fields are ``None``, no spacing is injected.

    Example::

        from streamtex import Spacing

        Spacing(top=3, bottom=0)          # int → st_space("v", N)
        Spacing(top="70px", left="5%")    # str → CSS value as-is
    """

    top: int | str | None = None
    """Vertical space before content.
    ``int`` → passed to ``st_space("v", N)`` as-is (library units).
    ``str`` → CSS value passed to ``st_space("v", "70px")`` as-is."""

    bottom: int | str | None = None
    """Vertical space after content.  Same conventions as *top*."""

    left: str | None = None
    """Horizontal left inset, CSS value (``"5%"``, ``"2em"``, ``"40px"``).
    Applied inside the effective width container."""

    right: str | None = None
    """Horizontal right inset, CSS value.  Same conventions as *left*."""

    width: int | None = None
    """Content width as % of page container.  Overrides ``PageLayout.width``
    locally.  ``None`` = inherit from ``PageLayout.width`` (sidebar slider).
    When set alone (no left/right), content is centered (auto margins)."""

    zoom: int | None = None
    """CSS zoom level as % applied to this scope (block or section).
    ``100`` = normal size, ``50`` = half, ``200`` = double.
    ``None`` = inherit from parent level in the override hierarchy.
    Composes multiplicatively with the global page zoom."""


@dataclass
class SpacingConfig:
    """Spacing configuration for a document or profile.

    Bundles the two spacing contexts: between blocks and between sections.
    Used at the global DI level (:func:`set_spacing`) and in
    :class:`PresentationProfile`.

    Example::

        from streamtex import Spacing, SpacingConfig, set_spacing

        set_spacing(SpacingConfig(
            block=Spacing(top=3, bottom=0),
            section=Spacing(top=2),
        ))
    """

    block: Spacing | None = None
    """Margins around blocks in the document flow (``st_book``).
    ``block.top`` = space before each block.
    ``block.bottom`` = space after each block (replaces hardcoded 70px)."""

    section: Spacing | None = None
    """Margins between sections within a block (``st_slide_break`` / title markers).
    ``section.top`` = space before each section (after a break point).
    ``section.bottom`` = space after each section (before the next break)."""


# ── Built-in defaults ─────────────────────────────────────────────────────

_BUILTIN_BLOCK = Spacing(bottom="70px")
"""Default block spacing — preserves the existing 70px inter-block gap."""

_BUILTIN_SECTION = Spacing()
"""Default section spacing — no section spacing (current behaviour)."""


# ── Global DI ─────────────────────────────────────────────────────────────

_spacing: SpacingConfig = SpacingConfig()
_block_spacing: Spacing | None = None
_active_profile: PresentationProfile | None = None


def set_spacing(config: SpacingConfig) -> None:
    """Set the global spacing config.  Call once in ``book.py``.

    Example::

        set_spacing(SpacingConfig(
            block=Spacing(top=3, bottom=0),
            section=Spacing(top=2),
        ))
    """
    global _spacing
    _spacing = config


def get_spacing() -> SpacingConfig:
    """Return the current global spacing config."""
    return _spacing


def set_block_spacing(spacing: Spacing | None) -> None:
    """Override section spacing for the current block.

    Called inside ``build()``.  Automatically reset to ``None`` by
    ``st_book`` after each ``build()`` call.
    """
    global _block_spacing
    _block_spacing = spacing


def get_block_spacing() -> Spacing | None:
    """Return the current block-level spacing override."""
    return _block_spacing


def reset_block_spacing() -> None:
    """Reset the block-level override.  Called by ``st_book`` after each ``build()``."""
    global _block_spacing
    _block_spacing = None


def set_active_profile(profile: PresentationProfile | None) -> None:
    """Store the active profile for section spacing resolution.

    Called by ``st_book`` when the active profile is determined.
    This allows ``resolve_section_spacing()`` (called from ``st_slide_break``
    and ``st_write``) to access the profile without passing it explicitly.
    """
    global _active_profile
    _active_profile = profile


def get_active_profile() -> PresentationProfile | None:
    """Return the active profile set by ``st_book``."""
    return _active_profile


# ── Double-spacing prevention ─────────────────────────────────────────────

_block_top_injected: bool = False


def mark_block_top_injected() -> None:
    """Mark that ``block.top`` was injected before the current ``build()``.

    Called by ``st_book`` after injecting block-level top spacing.
    """
    global _block_top_injected
    _block_top_injected = True


def consume_block_top_injected() -> bool:
    """Check and consume the block-top flag.

    Returns ``True`` (and resets the flag) if ``block.top`` was already
    injected for this block.  When ``True``, the caller should skip its
    own ``section.top`` injection to avoid double spacing.
    """
    global _block_top_injected
    if _block_top_injected:
        _block_top_injected = False
        return True
    return False


# ── Section-level horizontal state (Phase 3) ──────────────────────────────

_section_horizontal: Spacing | None = None


def set_section_horizontal(spacing: Spacing | None) -> None:
    """Activate horizontal spacing for the current section.

    When set, :func:`st_html` (the rendering gateway) wraps each
    HTML fragment with ``padding-left`` / ``padding-right``.
    Call with ``None`` to deactivate.
    """
    global _section_horizontal
    _section_horizontal = spacing


def get_section_horizontal() -> Spacing | None:
    """Return the active section horizontal spacing, or ``None``."""
    return _section_horizontal


# ── Section-level zoom state (Phase: per-section zoom) ───────────────────

_section_zoom: int | None = None


def set_section_zoom(zoom: int | None) -> None:
    """Activate CSS zoom for the current section.

    When set, :func:`st_html` (the rendering gateway) wraps each
    HTML fragment with ``zoom: <value>``.
    Call with ``None`` to deactivate.
    """
    global _section_zoom
    _section_zoom = zoom


def get_section_zoom() -> int | None:
    """Return the active section zoom percentage, or ``None``."""
    return _section_zoom


# ── Resolution ────────────────────────────────────────────────────────────


def _resolve_field(*values):
    """Return the first non-None value, or ``None`` if all are ``None``."""
    for v in values:
        if v is not None:
            return v
    return None


def _extract_spacing_field(spacing: Spacing | None, field: str):
    """Safely extract a field from a Spacing that may be None."""
    if spacing is None:
        return None
    return getattr(spacing, field, None)


def _profile_spacing(profile: PresentationProfile | None, context: str, field: str):
    """Extract a spacing field from a profile's SpacingConfig.

    *context* is ``"block"`` or ``"section"``.
    """
    if profile is None:
        return None
    cfg = getattr(profile, "spacing", None)
    if cfg is None:
        return None
    spacing = getattr(cfg, context, None)
    if spacing is None:
        return None
    return getattr(spacing, field, None)


def resolve_block_spacing(
    profile: PresentationProfile | None = None,
) -> Spacing:
    """Resolve effective block spacing (3 levels: built-in → global → profile).

    Returns a fully-resolved :class:`Spacing` with no ``None`` fields
    remaining (they fall back to the built-in defaults).
    """
    base = get_spacing()

    top = _resolve_field(
        _profile_spacing(profile, "block", "top"),
        _extract_spacing_field(base.block, "top"),
        _BUILTIN_BLOCK.top,
    )
    bottom = _resolve_field(
        _profile_spacing(profile, "block", "bottom"),
        _extract_spacing_field(base.block, "bottom"),
        _BUILTIN_BLOCK.bottom,
    )
    left = _resolve_field(
        _profile_spacing(profile, "block", "left"),
        _extract_spacing_field(base.block, "left"),
        _BUILTIN_BLOCK.left,
    )
    right = _resolve_field(
        _profile_spacing(profile, "block", "right"),
        _extract_spacing_field(base.block, "right"),
        _BUILTIN_BLOCK.right,
    )
    width = _resolve_field(
        _profile_spacing(profile, "block", "width"),
        _extract_spacing_field(base.block, "width"),
        _BUILTIN_BLOCK.width,
    )
    zoom = _resolve_field(
        _profile_spacing(profile, "block", "zoom"),
        _extract_spacing_field(base.block, "zoom"),
        _BUILTIN_BLOCK.zoom,
    )

    return Spacing(top=top, bottom=bottom, left=left, right=right, width=width, zoom=zoom)


def resolve_section_spacing(
    call_site: Spacing | None = None,
    profile: PresentationProfile | None = None,
) -> Spacing:
    """Resolve effective section spacing (5 levels).

    Level 5 (call_site) > Level 4 (block) > Level 3 (profile) >
    Level 2 (global) > Level 1 (built-in).

    When *profile* is ``None``, the active profile set by ``st_book``
    via :func:`set_active_profile` is used automatically.
    """
    if profile is None:
        profile = get_active_profile()
    base = get_spacing()
    block_override = get_block_spacing()

    fields = {}
    for f in ("top", "bottom", "left", "right", "width", "zoom"):
        fields[f] = _resolve_field(
            _extract_spacing_field(call_site, f),        # L5
            _extract_spacing_field(block_override, f),   # L4
            _profile_spacing(profile, "section", f),     # L3
            _extract_spacing_field(base.section, f),     # L2
            _extract_spacing_field(_BUILTIN_SECTION, f), # L1
        )

    return Spacing(**fields)
