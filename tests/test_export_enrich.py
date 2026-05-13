"""Unit tests for streamtex.export_enrich — sidebar theming via CSS vars.

These tests pin the contract that:

  * The static export sidebar resolves its colors from CSS custom properties
    (``var(--stx-export-sidebar-bg)``, ``var(--stx-export-link)``)
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
    _SIDEBAR_RESIZE_JS,
    _build_sidebar_html,
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
        assert "--stx-export-link" in css

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

    def test_sidebar_uses_var_for_link(self):
        assert "var(--stx-export-link" in _SIDEBAR_CSS

    def test_sidebar_uses_var_for_text(self):
        assert "var(--stx-export-sidebar-fg" in _SIDEBAR_CSS

    def test_toc_entries_styled_as_hyperlinks_underlined(self):
        """The live Streamlit sidebar renders TOC entries as hyperlinks
        in ``linkColor`` with an underline; the static export must
        match.  Pre-0.6.30 the entries were ``color: inherit;
        text-decoration: none`` — white text in dark themes, regardless
        of the project's link colour (FC slide regression observed by
        the user, the export showed white items instead of #43A9FB).
        """
        # Capture the first TOC selector block — assert both color
        # variable and underline are present.
        import re as _re
        block = _re.search(
            r"\.stx-toc-entry a\s*\{[^}]*\}", _SIDEBAR_CSS
        )
        assert block is not None, "No .stx-toc-entry a rule found"
        text = block.group(0)
        assert "var(--stx-export-link" in text, (
            f".stx-toc-entry a must use var(--stx-export-link, …) for color. Got: {text!r}"
        )
        assert "text-decoration: underline" in text, (
            f".stx-toc-entry a must be underlined (matches live sidebar). Got: {text!r}"
        )

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

    def test_sidebar_width_uses_css_variable(self):
        """The sidebar width MUST come from --stx-sidebar-width so the
        resize JS can update it; the previous hardcoded 280px would
        ignore any localStorage value the JS persists."""
        assert "var(--stx-sidebar-width" in _SIDEBAR_CSS

    def test_main_content_margin_uses_same_variable(self):
        """The main content's margin-left must read the SAME variable so
        sidebar resize and content reflow stay in lockstep with a
        single CSS write."""
        import re as _re
        # There are several .streamtex-page rules (main + override during
        # drag).  At least one must read the variable for margin-left.
        blocks = _re.findall(r"\.streamtex-page\s*\{[^}]*\}", _SIDEBAR_CSS, _re.DOTALL)
        assert blocks, "No .streamtex-page rule found"
        with_var = [b for b in blocks if "var(--stx-sidebar-width" in b]
        assert with_var, (
            ".streamtex-page must set margin-left via var(--stx-sidebar-width). "
            f"Found blocks: {blocks!r}"
        )

    def test_no_bold_on_toc_entries(self):
        """Per user request: no font-weight bolding on TOC items at any
        level.  The active entry is marked by a left-border ::before
        pseudo-element instead of a font-weight change.

        Scope: only the .stx-toc-* selectors.  The .stx-sidebar-logo
        header text legitimately keeps font-weight: 700 (it is a brand
        element, not a TOC entry).
        """
        import re as _re
        # No level-class rule sets font-weight to anything bold.
        for selector in (r"\.stx-toc-l1", r"\.stx-toc-l2",
                         r"\.stx-toc-l3", r"\.stx-toc-l4"):
            m = _re.search(rf"{selector}[^{{]*\{{[^}}]*\}}", _SIDEBAR_CSS, _re.DOTALL)
            if m is not None:
                body = m.group(0)
                assert "font-weight" not in body or "normal" in body, (
                    f"{selector!r} block must not bold TOC items.  Got: {body!r}"
                )
        # Active marker must NOT use font-weight at all on .stx-toc-active
        # (it now uses a ::before pseudo-element).
        m = _re.search(r"\.stx-toc-entry\.stx-toc-active a\s*\{[^}]*\}",
                       _SIDEBAR_CSS, _re.DOTALL)
        if m is not None:
            assert "font-weight" not in m.group(0), (
                "Active TOC entry must not be bolded; use ::before indicator instead."
            )
        # And the new ::before indicator is in place.
        assert ".stx-toc-active::before" in _SIDEBAR_CSS


# ---------------------------------------------------------------------------
# Sidebar drag-resize handle (P1 + P4 reset on double-click)
# ---------------------------------------------------------------------------

class TestSidebarResizeHandle:
    def test_handle_emitted_in_sidebar_html(self):
        toc = [{"level": 1, "title": "Hello", "_reg_label": "Hello",
                "key_anchor": "h1"}]
        html = _build_sidebar_html(toc)
        assert "stx-sidebar-resize-handle" in html
        # Accessible: keyboard-focusable + role=separator.
        assert 'role="separator"' in html
        assert 'tabindex="0"' in html

    def test_resize_js_uses_pointer_events_and_storage(self):
        """The handler MUST use pointer events (works with mouse + touch
        + pen) and persist the chosen width across reloads."""
        assert "pointerdown" in _SIDEBAR_RESIZE_JS
        assert "pointermove" in _SIDEBAR_RESIZE_JS
        assert "pointerup" in _SIDEBAR_RESIZE_JS
        assert "setPointerCapture" in _SIDEBAR_RESIZE_JS
        assert "localStorage" in _SIDEBAR_RESIZE_JS
        assert "--stx-sidebar-width" in _SIDEBAR_RESIZE_JS

    def test_resize_js_clamps_to_min_max(self):
        """A negative drag or one past the viewport must not collapse
        the sidebar to 0 or push it past sane bounds."""
        assert "MIN" in _SIDEBAR_RESIZE_JS
        assert "MAX_FRAC" in _SIDEBAR_RESIZE_JS
        assert "function clamp" in _SIDEBAR_RESIZE_JS

    def test_resize_js_dblclick_resets_to_default(self):
        """Double-click on the handle resets to the 280px default (P4)."""
        assert "dblclick" in _SIDEBAR_RESIZE_JS

    def test_resize_js_keyboard_accessibility(self):
        """ArrowLeft / ArrowRight on the focused handle adjust the
        width; Shift increases the step."""
        assert "ArrowLeft" in _SIDEBAR_RESIZE_JS
        assert "ArrowRight" in _SIDEBAR_RESIZE_JS
        assert "shiftKey" in _SIDEBAR_RESIZE_JS

    def test_resize_js_wired_into_enrich(self):
        """The resize JS must reach the output when a TOC is present."""
        toc = [{"level": 1, "title": "Hello", "_reg_label": "Hello",
                "key_anchor": "h1"}]
        raw = ("<!DOCTYPE html><html><head><title>T</title><style></style>"
               "</head><body><div class=\"streamtex-page\">x</div>"
               "</body></html>")
        with patch("streamtex.export.st.get_option") as mock_opt:
            mock_opt.return_value = None
            out = enrich_export_html(raw, toc=toc)
        assert "stx-sidebar-resize-handle" in out
        assert "pointerdown" in out


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
