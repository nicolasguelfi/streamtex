"""Unit tests for streamtex.export_enrich — sidebar theming via CSS vars.

These tests pin the contract that:

  * The static export sidebar resolves its colors from CSS custom properties
    (``var(--stx-export-sidebar-bg)``, ``var(--stx-export-link-active)``)
    rather than hardcoded literals.
  * The ``:root`` block of variables is emitted at the top of the injected
    CSS and reads values from the project's ``.streamlit/config.toml`` theme
    via ``_get_theme_color`` (with Streamlit 1.56 dark defaults — ``#1C1E1F``
    for the sidebar background, ``#43A9FB`` for links — when ``base="dark"``
    is set without per-key overrides).
  * The legacy ``@media (prefers-color-scheme: dark)`` overrides — which
    based the static dark mode on the reader's OS preference, decoupling
    it from the project's authored theme — are gone from the sidebar CSS.
"""
from __future__ import annotations

from unittest.mock import patch

from streamtex.export import _get_theme_color
from streamtex.export_enrich import (
    _SIDEBAR_CSS,
    _build_theme_vars_css,
    enrich_export_html,
)

# ---------------------------------------------------------------------------
# _get_theme_color — extended dark defaults (Streamlit 1.56)
# ---------------------------------------------------------------------------

class TestDarkDefaults:
    def test_secondary_background_color_dark_default(self):
        """``secondaryBackgroundColor`` is the sidebar background.  With
        ``base="dark"`` and no override, Streamlit's frontend resolves it
        to ``#1C1E1F`` — we encode that so the static export matches."""
        with patch("streamtex.export.st.get_option") as mock_opt:
            def side_effect(opt):
                if opt == "theme.base":
                    return "dark"
                return None
            mock_opt.side_effect = side_effect
            assert _get_theme_color("theme.secondaryBackgroundColor", "#fff") == "#1C1E1F"

    def test_link_color_dark_default(self):
        """Default link color in Streamlit 1.56 dark mode."""
        with patch("streamtex.export.st.get_option") as mock_opt:
            def side_effect(opt):
                if opt == "theme.base":
                    return "dark"
                return None
            mock_opt.side_effect = side_effect
            assert _get_theme_color("theme.linkColor", "#1155cc") == "#43A9FB"

    def test_explicit_value_wins_over_dark_default(self):
        """Project config wins over the dark default."""
        with patch("streamtex.export.st.get_option") as mock_opt:
            def side_effect(opt):
                if opt == "theme.secondaryBackgroundColor":
                    return "#1A2230"  # FC-260507's actual override
                if opt == "theme.base":
                    return "dark"
                return None
            mock_opt.side_effect = side_effect
            assert _get_theme_color("theme.secondaryBackgroundColor", "#fff") == "#1A2230"

    def test_light_base_uses_caller_fallback(self):
        """Light theme: fall back to the caller's supplied default."""
        with patch("streamtex.export.st.get_option") as mock_opt:
            mock_opt.return_value = None
            assert _get_theme_color("theme.linkColor", "#1155cc") == "#1155cc"


# ---------------------------------------------------------------------------
# _build_theme_vars_css — :root block emission
# ---------------------------------------------------------------------------

class TestBuildThemeVarsCss:
    def test_emits_root_block_with_three_vars(self):
        css = _build_theme_vars_css()
        assert ":root" in css
        assert "--stx-export-sidebar-bg" in css
        assert "--stx-export-sidebar-fg" in css
        assert "--stx-export-link-active" in css

    def test_dark_theme_values(self):
        """With ``base="dark"`` and no overrides, the :root block contains
        the Streamlit 1.56 resolved defaults."""
        with patch("streamtex.export.st.get_option") as mock_opt:
            def side_effect(opt):
                if opt == "theme.base":
                    return "dark"
                return None
            mock_opt.side_effect = side_effect
            css = _build_theme_vars_css()
            assert "#1C1E1F" in css       # sidebar bg
            assert "#43A9FB" in css       # link color
            assert "#fafafa" in css       # text color

    def test_project_overrides_propagate(self):
        """FC-260507's overrides reach the :root block."""
        with patch("streamtex.export.st.get_option") as mock_opt:
            def side_effect(opt):
                values = {
                    "theme.base": "dark",
                    "theme.secondaryBackgroundColor": "#1A2230",
                    "theme.textColor": "#F2EEE6",
                    "theme.linkColor": "#5C8AC2",
                }
                return values.get(opt)
            mock_opt.side_effect = side_effect
            css = _build_theme_vars_css()
            assert "#1A2230" in css
            assert "#F2EEE6" in css
            assert "#5C8AC2" in css


# ---------------------------------------------------------------------------
# _SIDEBAR_CSS — uses var() references, no @media prefers-color-scheme
# ---------------------------------------------------------------------------

class TestSidebarCssVars:
    def test_sidebar_uses_var_for_background(self):
        assert "var(--stx-export-sidebar-bg" in _SIDEBAR_CSS

    def test_sidebar_uses_var_for_link_active(self):
        assert "var(--stx-export-link-active" in _SIDEBAR_CSS

    def test_sidebar_uses_var_for_text(self):
        assert "var(--stx-export-sidebar-fg" in _SIDEBAR_CSS

    def test_no_prefers_color_scheme_overrides_in_sidebar(self):
        """The dark-mode fork by OS preference is removed: the static
        sidebar follows the project's authored theme, not the reader's
        OS setting."""
        assert "@media (prefers-color-scheme: dark)" not in _SIDEBAR_CSS

    def test_no_hardcoded_dark_sidebar_colors(self):
        """The previous hardcoded dark palette (``#1a1a2e``, ``#42D0F3``,
        ``#2a2a3e``) is gone — colors come from CSS vars now."""
        assert "#1a1a2e" not in _SIDEBAR_CSS
        assert "#42D0F3" not in _SIDEBAR_CSS
        assert "#2a2a3e" not in _SIDEBAR_CSS


# ---------------------------------------------------------------------------
# enrich_export_html — full integration
# ---------------------------------------------------------------------------

class TestEnrichExportHtml:
    _MINIMAL_RAW = (
        "<!DOCTYPE html><html><head><title>Test</title><style></style>"
        "</head><body><div class=\"streamtex-page\">x</div></body></html>"
    )

    def test_root_vars_present_in_output_when_toc(self):
        """The :root block is injected when a TOC is present (i.e. when
        the sidebar is rendered)."""
        toc = [{"level": 1, "title": "Hello", "_reg_label": "Hello",
                "anchor": "h1"}]
        with patch("streamtex.export.st.get_option") as mock_opt:
            mock_opt.return_value = None  # light theme
            out = enrich_export_html(self._MINIMAL_RAW, toc=toc)
        assert ":root" in out
        assert "--stx-export-sidebar-bg" in out

    def test_root_vars_carry_dark_defaults(self):
        toc = [{"level": 1, "title": "Hello", "_reg_label": "Hello",
                "anchor": "h1"}]
        with patch("streamtex.export.st.get_option") as mock_opt:
            def side_effect(opt):
                if opt == "theme.base":
                    return "dark"
                return None
            mock_opt.side_effect = side_effect
            out = enrich_export_html(self._MINIMAL_RAW, toc=toc)
        # Sidebar bg + link color resolved from dark defaults.
        assert "#1C1E1F" in out
        assert "#43A9FB" in out

    def test_no_toc_no_theme_vars(self):
        """When no sidebar is rendered (no TOC), don't waste bytes on
        sidebar theme vars."""
        with patch("streamtex.export.st.get_option") as mock_opt:
            mock_opt.return_value = None
            out = enrich_export_html(self._MINIMAL_RAW, toc=None)
        # No sidebar CSS at all when toc is empty.
        assert ".stx-export-sidebar" not in out
