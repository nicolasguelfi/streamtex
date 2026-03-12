"""Presentation mode — fullscreen 16/9 slide deck with footer and centering."""

from dataclasses import dataclass
from typing import Optional

import streamlit as st

from .export import _render


@dataclass
class PresentationConfig:
    """Configuration for fullscreen presentation mode.

    Call :func:`set_presentation_config` once in ``book.py`` to activate
    presentation mode. This injects CSS that:

    - Enforces a 16/9 (or custom) aspect ratio on the slide container
    - Centres content vertically within each slide
    - Hides Streamlit chrome (header, footer, deploy button)
    - Adds a fixed footer bar with slide counter and title

    Example::

        from streamtex import PresentationConfig, set_presentation_config

        set_presentation_config(PresentationConfig(
            title="Introduction to Docker",
            aspect_ratio="16/9",
            footer=True,
            center_content=True,
        ))
    """

    # Identity
    title: str = ""
    """Title displayed in the presentation footer."""

    subtitle: str = ""
    """Optional subtitle (not currently rendered in the footer)."""

    # Aspect ratio
    aspect_ratio: str = "16/9"
    """CSS aspect-ratio value ("16/9", "4/3", "16/10")."""

    enforce_ratio: bool = True
    """When True, apply aspect-ratio + overflow:hidden to the slide container."""

    # Footer
    footer: bool = True
    """Show a fixed slide counter bar at the bottom of the viewport."""

    footer_height: str = "48px"
    """CSS height of the footer bar."""

    footer_bg: Optional[str] = None
    """Background colour of the footer (None = inherit from theme)."""

    footer_text_color: Optional[str] = None
    """Text colour of the footer (None = inherit from theme)."""

    footer_font_size: str = "18px"
    """Font size for footer text."""

    # Layout
    center_content: bool = True
    """Vertically centre slide content within the viewport."""

    content_padding: str = "48px 64px"
    """CSS padding inside each slide container."""

    # Streamlit UI
    hide_streamlit_header: bool = True
    """Hide the Streamlit header bar."""

    hide_streamlit_footer: bool = True
    """Hide the 'Made with Streamlit' footer."""

    hide_deploy_button: bool = True
    """Hide the Streamlit deploy button."""

    sidebar_default: str = "collapsed"
    """Initial sidebar state ('collapsed' or 'expanded')."""

    # Transitions (future)
    slide_transition: str = "none"
    """Transition effect between slides ('none', 'fade', 'slide')."""

    transition_duration: str = "0.3s"
    """CSS transition duration."""


# ---------------------------------------------------------------------------
# DI pattern — matches AIImageConfig, GSheetConfig, LinkConfig
# ---------------------------------------------------------------------------

_PRESENTATION_CONFIG_KEY = "_stx_presentation_config"


def set_presentation_config(config: PresentationConfig) -> None:
    """Set the global presentation configuration.

    Call once at the top of ``book.py`` before ``st_book()``.
    Injects the CSS needed for fullscreen presentation mode.
    """
    st.session_state[_PRESENTATION_CONFIG_KEY] = config
    _inject_presentation_css(config)


def get_presentation_config() -> Optional[PresentationConfig]:
    """Return the current presentation config, or None if not set."""
    return st.session_state.get(_PRESENTATION_CONFIG_KEY)


# ---------------------------------------------------------------------------
# Session state keys for sidebar controls
# ---------------------------------------------------------------------------

_PRES_FOOTER_KEY = "_stx_pres_footer"
_PRES_FULLSCREEN_KEY = "_stx_pres_fullscreen"
_PRES_SLIDE_JUMP_KEY = "_stx_pres_slide_jump"


# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

def _inject_presentation_css(config: PresentationConfig) -> None:
    """Inject CSS for presentation mode via st.html()."""
    css_parts = []

    # 1. Hide Streamlit chrome
    if config.hide_streamlit_header:
        css_parts.append(
            "header[data-testid='stHeader'] { display: none !important; }"
        )
    if config.hide_streamlit_footer:
        css_parts.append("footer { display: none !important; }")
    if config.hide_deploy_button:
        css_parts.append(".stDeployButton { display: none !important; }")

    # 2. Aspect-ratio constraint on main container
    if config.enforce_ratio:
        css_parts.append(f"""
        .stMain .block-container {{
            max-width: 100vw !important;
            max-height: 100vh;
            overflow: hidden;
            padding: {config.content_padding};
        }}
        """)

    # 3. Vertical centering
    if config.center_content:
        css_parts.append("""
        .stMain .block-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        """)

    # 4. Footer styling
    if config.footer:
        bg = config.footer_bg or "var(--background-color, #0e1117)"
        text = config.footer_text_color or "var(--text-color, #fafafa)"
        css_parts.append(f"""
        .stx-presentation-footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: {config.footer_height};
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            font-size: {config.footer_font_size};
            font-family: inherit;
            z-index: 999;
            border-top: 1px solid rgba(128, 128, 128, 0.3);
            background: {bg};
            color: {text};
        }}
        .stx-presentation-footer .stx-pf-title {{
            opacity: 0.7;
        }}
        .stx-presentation-footer .stx-pf-counter {{
            font-weight: 600;
        }}
        """)

    # 5. Bottom padding so content doesn't hide behind footer
    if config.footer:
        css_parts.append(f"""
        .stMain .block-container {{
            padding-bottom: calc({config.content_padding.split()[-1]} + {config.footer_height}) !important;
        }}
        """)

    # 6. Transitions (future)
    if config.slide_transition != "none":
        css_parts.append(f"""
        .stx-slide-container {{
            transition: opacity {config.transition_duration} ease-in-out;
        }}
        """)

    if css_parts:
        css = "<style>\n" + "\n".join(css_parts) + "\n</style>"
        st.html(css)


# ---------------------------------------------------------------------------
# Footer rendering
# ---------------------------------------------------------------------------

def st_presentation_footer(
    current_slide: int = 1,
    total_slides: int = 1,
    title: Optional[str] = None,
    config: Optional[PresentationConfig] = None,
) -> None:
    """Render the presentation footer bar with slide counter.

    Usually called automatically by ``st_book()`` when a
    :class:`PresentationConfig` is active. Can also be called
    manually for custom setups.

    Args:
        current_slide: Current slide number (1-based).
        total_slides: Total number of slides.
        title: Presentation title (falls back to config.title).
        config: Per-call config override. Falls back to
                :func:`get_presentation_config`.
    """
    cfg = config or get_presentation_config()
    if cfg is None or not cfg.footer:
        return

    display_title = title or cfg.title
    title_html = (
        f'<span class="stx-pf-title">{display_title}</span>'
        if display_title
        else ""
    )

    html = (
        f'<div class="stx-presentation-footer">'
        f"  {title_html}"
        f'  <span class="stx-pf-counter">'
        f"    Slide {current_slide} / {total_slides}"
        f"  </span>"
        f"</div>"
    )
    _render(html)


# ---------------------------------------------------------------------------
# Sidebar presenter controls
# ---------------------------------------------------------------------------

def add_presentation_options(container=None) -> None:
    """Add presenter controls to the sidebar.

    Provides toggles for:
    - Footer visibility
    - Fullscreen mode on/off
    - Jump to slide N (number input)

    Args:
        container: Streamlit container to render into (default: sidebar).
    """
    cfg = get_presentation_config()
    if cfg is None:
        return

    ctx = container if container is not None else st.sidebar

    if _PRES_FOOTER_KEY not in st.session_state:
        st.session_state[_PRES_FOOTER_KEY] = cfg.footer
    if _PRES_FULLSCREEN_KEY not in st.session_state:
        st.session_state[_PRES_FULLSCREEN_KEY] = True

    ctx.toggle("Show footer", key=_PRES_FOOTER_KEY)
    ctx.toggle("Fullscreen mode", key=_PRES_FULLSCREEN_KEY)
