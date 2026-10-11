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


# ---------------------------------------------------------------------------
# #55: badge proportional to the image (container-query units)
# ---------------------------------------------------------------------------

_IMG = '<img src="x.png" style="width:100%;">'


class TestProportional:
    def test_off_by_default_is_byte_identical(self):
        plain = MediaOverlay(text="✦ AI")
        assert plain.proportional is False
        out = wrap_media_overlay(_IMG, plain, width="40vw")
        assert "container-type" not in out and "cqw" not in out
        assert "font-size:12px;" in out and "padding:2px 8px;" in out
        # Same text as an explicit proportional=False
        assert out == wrap_media_overlay(_IMG, MediaOverlay(text="✦ AI", proportional=False), width="40vw")

    def test_on_declares_container_and_relative_pill(self):
        out = wrap_media_overlay(_IMG, MediaOverlay(text="✦ AI", proportional=True), width="6vw")
        assert "container-type:inline-size;" in out
        assert "font-size:clamp(9px, 7cqw, 22px);" in out
        assert "font-size:12px" not in out

    @pytest.mark.parametrize("width", ["", "auto"])
    def test_auto_width_keeps_box_shrink_wrapping(self, width):
        out = wrap_media_overlay(_IMG, MediaOverlay(text="AI", proportional=True), width=width)
        assert "container-type" not in out  # would collapse a shrink-to-fit box
        assert "7cqw" in out

    def test_centered_auto_width_no_container(self):
        out = wrap_media_overlay(_IMG, MediaOverlay(text="AI", proportional=True), caller_css="margin: 0 auto;")
        assert "fit-content" in out and "container-type" not in out

    def test_caller_css_still_wins(self):
        out = build_overlay_span(MediaOverlay(text="AI", proportional=True, css="font-size:8cqw;"))
        assert out.index("7cqw") < out.index("font-size:8cqw;")


def test_proportional_badges_in_chromium():
    """A 6vw thumbnail and a 40vw hero get badges ~7 % of their own width (#55)."""
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import Error, sync_playwright

    def box(width, prop):
        ov = MediaOverlay(text="✦ AI", proportional=prop)
        img = ('<img src="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 '
               'width=%22100%22 height=%22100%22/%3E" style="width:100%; height:auto; display:block;">')
        return wrap_media_overlay(img, ov, width=width)

    html_doc = ("<html><body style='margin:0'>" + box("6vw", True) + box("40vw", True)
                + box("40vw", False) + box("auto", True) + "</body></html>")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.set_content(html_doc)
            sizes = page.eval_on_selector_all(
                ".stx-media-overlay", "els => els.map(e => parseFloat(getComputedStyle(e).fontSize))")
            boxes = page.eval_on_selector_all(
                ".stx-media-box", "els => els.map(e => e.getBoundingClientRect().width)")
            browser.close()
    except Error as e:
        pytest.skip(f"Chromium not available: {e}")
    small, hero, legacy, auto = sizes
    assert boxes[0] == pytest.approx(1920 * 0.06, abs=1) and boxes[1] == pytest.approx(1920 * 0.40, abs=1)
    assert small == pytest.approx(max(9, 0.07 * boxes[0]), abs=0.5)    # 8.06 -> clamped to 9
    assert hero == pytest.approx(min(22, 0.07 * boxes[1]), abs=0.5)    # 53.8 -> clamped to 22
    assert legacy == 12
    assert boxes[3] > 0  # the auto-width box did not collapse
