"""Tests for streamtex/media_overlay.py — MediaOverlay dataclass and emission."""

import pytest

from streamtex.media_overlay import (
    MediaOverlay,
    build_overlay_span,
    wrap_media_overlay,
)

# ---------------------------------------------------------------------------
# MediaOverlay dataclass
# ---------------------------------------------------------------------------

class TestMediaOverlayDataclass:
    def test_defaults(self):
        ov = MediaOverlay(text="✦ AI")
        assert ov.position == "bottom-right"
        assert ov.css == ""
        assert ov.aria_label == ""

    def test_frozen(self):
        ov = MediaOverlay(text="✦ AI")
        with pytest.raises(AttributeError):
            ov.text = "changed"

    @pytest.mark.parametrize(
        "position", ["bottom-right", "top-right", "bottom-left", "top-left"]
    )
    def test_valid_positions(self, position):
        assert MediaOverlay(text="x", position=position).position == position

    def test_invalid_position_raises(self):
        with pytest.raises(ValueError, match="MediaOverlay.position"):
            MediaOverlay(text="x", position="center")


# ---------------------------------------------------------------------------
# build_overlay_span — badge emission
# ---------------------------------------------------------------------------

class TestBuildOverlaySpan:
    def test_structure_and_default_pill(self):
        span = build_overlay_span(MediaOverlay(text="✦ AI"))
        assert span.startswith('<span class="stx-media-overlay" role="note"')
        assert span.endswith("✦ AI</span>")
        assert "position:absolute;" in span
        assert "right:8px; bottom:8px;" in span
        assert "background:rgba(113,113,122,0.35)" in span
        assert "pointer-events:none" in span
        assert "z-index:2" in span

    @pytest.mark.parametrize(
        ("position", "expected"),
        [
            ("bottom-right", "right:8px; bottom:8px;"),
            ("top-right", "right:8px; top:8px;"),
            ("bottom-left", "left:8px; bottom:8px;"),
            ("top-left", "left:8px; top:8px;"),
        ],
    )
    def test_position_translated_to_css(self, position, expected):
        span = build_overlay_span(MediaOverlay(text="x", position=position))
        assert expected in span

    def test_text_html_escaped(self):
        span = build_overlay_span(MediaOverlay(text='<b>"AI" & Co</b>'))
        assert "<b>" not in span
        assert "&lt;b&gt;&quot;AI&quot; &amp; Co&lt;/b&gt;" in span

    def test_aria_label_emitted_and_escaped(self):
        span = build_overlay_span(
            MediaOverlay(text="✦ AI", aria_label='AI-generated "image"')
        )
        assert 'aria-label="AI-generated &quot;image&quot;"' in span

    def test_aria_label_absent_when_empty(self):
        span = build_overlay_span(MediaOverlay(text="✦ AI"))
        assert "aria-label" not in span

    def test_custom_css_appended_after_defaults(self):
        span = build_overlay_span(MediaOverlay(text="x", css="background:#000;"))
        # Caller CSS comes after the default pill so it wins in cascade order
        assert span.index("rgba(113,113,122,0.35)") < span.index("background:#000;")


# ---------------------------------------------------------------------------
# wrap_media_overlay — stx-media-box wrapper
# ---------------------------------------------------------------------------

class TestWrapMediaOverlay:
    def test_wrapper_contains_media_then_badge(self):
        inner = '<img src="x.png" alt="" style="width: 100%;">'
        out = wrap_media_overlay(inner, MediaOverlay(text="✦ AI"), width="100%")
        assert out.startswith('<span class="stx-media-box"')
        assert out.endswith("</span>")
        assert out.index(inner) < out.index('class="stx-media-overlay"')

    def test_wrapper_carries_resolved_width(self):
        out = wrap_media_overlay("<img>", MediaOverlay(text="x"), width="80%")
        assert "width:80%;" in out
        assert "position:relative; display:inline-block;" in out
        assert "max-width:100%;" in out
        assert "line-height:0;" in out

    def test_auto_margins_transferred_to_wrapper(self):
        out = wrap_media_overlay(
            "<img>",
            MediaOverlay(text="x"),
            width="80%",
            caller_css="display:block; margin: 0 auto;",
        )
        assert "display:block;" in out
        assert "margin: 0 auto;" in out
        assert "width:80%;" in out

    def test_centered_auto_width_falls_back_to_fit_content(self):
        out = wrap_media_overlay(
            "<img>",
            MediaOverlay(text="x"),
            width="auto",
            caller_css="margin-left:auto; margin-right:auto;",
        )
        assert "width:fit-content;" in out
        assert "margin-left:auto;" in out
        assert "margin-right:auto;" in out

    def test_no_margin_auto_keeps_inline_block(self):
        out = wrap_media_overlay(
            "<img>",
            MediaOverlay(text="x"),
            width="100%",
            caller_css="margin: 4px 8px; border-radius:8px;",
        )
        assert "display:inline-block;" in out
        assert "margin: 4px 8px" not in out
