"""Configurable banner system for paginated navigation in StreamTeX books."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import streamlit as st


class BannerMode(Enum):
    """Display mode for paginated navigation banners."""

    FULL = "full"
    """Prominent banner — large text, rounded corners, dividers."""

    COMPACT = "compact"
    """Slim, discreet banner — smaller text, tighter padding."""

    HIDDEN = "hidden"
    """No visual banner — auto-scroll / keyboard navigation preserved."""


# Mode-specific defaults (font_size, font_weight, padding, border_radius, show_dividers)
_MODE_DEFAULTS: dict[BannerMode, dict] = {
    BannerMode.FULL: {
        "font_size": "1.3rem",
        "font_weight": "bold",
        "padding": "18px 24px",
        "border_radius": "8px",
        "show_dividers": True,
    },
    BannerMode.COMPACT: {
        "font_size": "0.8rem",
        "font_weight": "500",
        "padding": "5px 16px",
        "border_radius": "4px",
        "show_dividers": False,
    },
}


@dataclass
class BannerConfig:
    """Configuration for paginated navigation banners.

    Pass an instance to ``st_book(banner=...)`` to customise banner appearance.
    Use factory classmethods for common presets::

        st_book(modules, paginate=True, banner=BannerConfig.compact())
        st_book(modules, paginate=True, banner=BannerConfig.hidden())
    """

    mode: BannerMode = BannerMode.FULL
    """Display mode (FULL, COMPACT, HIDDEN)."""

    color: str = "rgba(211, 47, 47, 0.8)"
    """Background colour (any CSS value)."""

    text_color: str = "white"
    """Text colour (any CSS value)."""

    font_size: str | None = None
    """Font size override. ``None`` → auto per mode."""

    font_weight: str | None = None
    """Font weight override. ``None`` → auto per mode."""

    padding: str | None = None
    """Padding override. ``None`` → auto per mode."""

    border_radius: str | None = None
    """Border radius override. ``None`` → auto per mode."""

    show_title: bool = True
    """Show the target page title in the banner."""

    show_arrows: bool = True
    """Show directional arrows (◂ / ▸)."""

    show_dividers: bool | None = None
    """Show Streamlit dividers between banner and content. ``None`` → auto per mode."""

    # ------------------------------------------------------------------
    # Factory presets
    # ------------------------------------------------------------------

    @classmethod
    def full(cls, color: str = "rgba(211, 47, 47, 0.8)") -> BannerConfig:
        """Full-size banner (default look)."""
        return cls(mode=BannerMode.FULL, color=color)

    @classmethod
    def compact(cls, color: str = "rgba(211, 47, 47, 0.8)") -> BannerConfig:
        """Compact / slim banner."""
        return cls(mode=BannerMode.COMPACT, color=color)

    @classmethod
    def compact_gray(cls) -> BannerConfig:
        """Compact banner with a neutral gray background."""
        return cls(mode=BannerMode.COMPACT, color="rgba(128, 128, 128, 0.7)", text_color="white")

    @classmethod
    def hidden(cls) -> BannerConfig:
        """No visual banner — navigation still works via keyboard / auto-scroll."""
        return cls(mode=BannerMode.HIDDEN)

    # ------------------------------------------------------------------
    # Internal resolution
    # ------------------------------------------------------------------

    def _resolve(self) -> dict | None:
        """Resolve final CSS properties (mode defaults + explicit overrides).

        Returns ``None`` for HIDDEN mode (no visual rendering needed).
        """
        if self.mode == BannerMode.HIDDEN:
            return None

        defaults = _MODE_DEFAULTS.get(self.mode, _MODE_DEFAULTS[BannerMode.FULL])

        show_dividers = self.show_dividers if self.show_dividers is not None else defaults["show_dividers"]

        return {
            "color": self.color,
            "text_color": self.text_color,
            "font_size": self.font_size if self.font_size is not None else defaults["font_size"],
            "font_weight": self.font_weight if self.font_weight is not None else defaults["font_weight"],
            "padding": self.padding if self.padding is not None else defaults["padding"],
            "border_radius": self.border_radius if self.border_radius is not None else defaults["border_radius"],
            "show_title": self.show_title,
            "show_arrows": self.show_arrows,
            "show_dividers": show_dividers,
        }


def _render_banner(banner_id: str, label: str, arrow: str, config: BannerConfig) -> None:
    """Render a single navigation banner via ``st.markdown``.

    Parameters
    ----------
    banner_id:
        HTML id for the banner div (e.g. ``"stx-banner-prev"``).
    label:
        Page title to display.
    arrow:
        Directional arrow character (``"◂"`` or ``"▸"``).
    config:
        The resolved :class:`BannerConfig`.
    """
    css = config._resolve()
    if css is None:
        return  # HIDDEN mode — nothing to render

    # Build label content
    parts: list[str] = []
    if css["show_arrows"] and arrow == "◂":
        parts.append("◂&ensp;")
    if css["show_title"]:
        parts.append(label)
    if css["show_arrows"] and arrow == "▸":
        parts.append("&ensp;▸")
    inner = "".join(parts)

    style = (
        f'background:{css["color"]};'
        f'color:{css["text_color"]};'
        f'font-weight:{css["font_weight"]};'
        f'font-size:{css["font_size"]};'
        f'padding:{css["padding"]};'
        f"text-align:center;"
        f"cursor:pointer;"
        f'border-radius:{css["border_radius"]};'
        f"user-select:none;"
    )

    st.markdown(
        f'<div id="{banner_id}" style="{style}">{inner}</div>',
        unsafe_allow_html=True,
    )
