"""E2E pixel measurement — st_image(crop=...) geometry in a real browser.

Renders the HTML emitted by ``st_image(crop=...)`` in headless Chromium
and measures the real boxes:

* the crop container's box matches the visible zone's aspect ratio
  (1000x600 source, crop=(5, 20, 15, 10) → visible 700x480);
* the inner ``<img>`` is enlarged and shifted so the cropped edges align
  exactly — verified by sampling a landmark pixel: the source image has
  four distinctly-colored quadrants, and the pixel rendered at the
  container's top-left corner must belong to the source pixel at
  (left%, top%) of the natural dimensions;
* the crop container under a CSS ``zoom`` (the st_zoom mechanism)
  multiplies correctly.

Run with:
    uv run pytest -m e2e tests/e2e/test_crop_geometry.py -v -s
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.e2e

# Quadrant colors of the 1000x600 test source (RGB).
TOP_LEFT = (200, 30, 30)
TOP_RIGHT = (30, 160, 30)
BOTTOM_LEFT = (30, 30, 200)
BOTTOM_RIGHT = (200, 180, 30)


def _make_quadrant_png(path, w=1000, h=600):
    from PIL import Image
    img = Image.new("RGB", (w, h))
    for x in range(w):
        for y in range(h):
            if x < w // 2:
                img.putpixel((x, y), TOP_LEFT if y < h // 2 else BOTTOM_LEFT)
            else:
                img.putpixel((x, y), TOP_RIGHT if y < h // 2 else BOTTOM_RIGHT)
    img.save(path)


def _st_image_html(uri, **kwargs):
    from streamtex.image import st_image
    captured = []
    with patch("streamtex.image._render", side_effect=lambda html, **kw: captured.append(html)):
        st_image(uri=uri, **kwargs)
    assert len(captured) == 1
    return captured[0]


def _page_screenshot_rgb(page_html, tmp_path, viewport=(1400, 900)):
    from PIL import Image
    from playwright.sync_api import sync_playwright
    shot = tmp_path / "shot.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": viewport[0], "height": viewport[1]},
            device_scale_factor=1,
        )
        page.set_content(page_html)
        page.wait_for_load_state("networkidle")
        boxes = {
            "container": page.locator(".stx-crop-box").first.bounding_box(),
            "img": page.locator(".stx-crop-box img").first.bounding_box(),
        }
        page.screenshot(path=str(shot), full_page=True)
        browser.close()
    return boxes, Image.open(str(shot)).convert("RGB")


def _wrap_page(fragment, zoom=None):
    zoom_css = f"zoom:{zoom / 100};" if zoom else ""
    return (
        "<!doctype html><html><head><style>"
        "html,body{margin:0;padding:0;}"
        "</style></head><body>"
        f'<div style="{zoom_css}">{fragment}</div>'
        "</body></html>"
    )


class TestCropGeometry:
    def test_visible_zone_and_pixel_alignment(self, tmp_path):
        src = tmp_path / "quad.png"
        _make_quadrant_png(str(src))
        html = _st_image_html(str(src), width="700px", crop=(5, 20, 15, 10))
        # The base64 data URI must be embedded (local file path).
        assert "data:image/png;base64," in html

        boxes, shot = _page_screenshot_rgb(_wrap_page(html), tmp_path)

        # Container box = visible zone: 700x480 (ratio 35/24).
        assert boxes["container"]["width"] == pytest.approx(700, abs=1)
        assert boxes["container"]["height"] == pytest.approx(480, abs=1)

        # Inner img box = full natural size at this scale: 1000x600,
        # shifted up-left by (left%, top%) of itself = (100, 30).
        assert boxes["img"]["width"] == pytest.approx(1000, abs=1)
        assert boxes["img"]["height"] == pytest.approx(600, abs=1)
        assert boxes["img"]["x"] == pytest.approx(boxes["container"]["x"] - 100, abs=1)
        assert boxes["img"]["y"] == pytest.approx(boxes["container"]["y"] - 30, abs=1)

        # Landmark pixels: the container's top-left corner shows the
        # source pixel at (10% * 1000, 5% * 600) = (100, 30) → TOP_LEFT
        # quadrant; the container's bottom-right corner shows the source
        # pixel just inside (80%, 85%) → BOTTOM_RIGHT quadrant.
        cx, cy = int(boxes["container"]["x"]), int(boxes["container"]["y"])
        assert shot.getpixel((cx + 2, cy + 2)) == TOP_LEFT
        assert shot.getpixel((cx + 697, cy + 477)) == BOTTOM_RIGHT
        # Quadrant boundary lands at source (500, 300) → container
        # (400, 270): TOP_RIGHT just right of it, above the middle.
        assert shot.getpixel((cx + 405, cy + 200)) == TOP_RIGHT
        assert shot.getpixel((cx + 200, cy + 350)) == BOTTOM_LEFT

    def test_crop_under_css_zoom_multiplies(self, tmp_path):
        src = tmp_path / "quad.png"
        _make_quadrant_png(str(src), 500, 300)
        html = _st_image_html(str(src), width="400px", crop=(10, 0, 10, 0))
        boxes, _ = _page_screenshot_rgb(_wrap_page(html, zoom=130), tmp_path)
        # 400px wide, visible ratio 500/240, all multiplied by 1.3.
        assert boxes["container"]["width"] == pytest.approx(400 * 1.3, abs=2)
        assert boxes["container"]["height"] == pytest.approx(400 * 240 / 500 * 1.3, abs=2)

    def test_crop_with_overlay_badge_inside_visible_zone(self, tmp_path):
        from streamtex.media_overlay import MediaOverlay
        src = tmp_path / "quad.png"
        _make_quadrant_png(str(src), 500, 300)
        html = _st_image_html(
            str(src), width="400px", crop=(10, 0, 10, 0),
            overlay=MediaOverlay(text="AI"),
        )
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.set_content(_wrap_page(html))
            page.wait_for_load_state("networkidle")
            container = page.locator(".stx-crop-box").first.bounding_box()
            badge = page.locator(".stx-media-overlay").first.bounding_box()
            browser.close()
        # The badge sits fully inside the visible (cropped) zone.
        assert badge["x"] >= container["x"]
        assert badge["y"] >= container["y"]
        assert badge["x"] + badge["width"] <= container["x"] + container["width"] + 1
        assert badge["y"] + badge["height"] <= container["y"] + container["height"] + 1


class TestCropExportParity:
    def test_export_buffer_carries_the_same_crop_fragment(self, tmp_path):
        """The export pipeline receives the exact same crop HTML as the
        live app (pure inline CSS — no runtime needed)."""
        from streamtex.export import (
            ExportConfig,
            generate_export_html,
            is_export_active,
            reset_export_buffer,
        )
        from streamtex.image import st_image

        src = tmp_path / "quad.png"
        _make_quadrant_png(str(src), 500, 300)

        reset_export_buffer(ExportConfig(enabled=True))
        try:
            assert is_export_active()
            with patch("streamlit.html"):
                st_image(uri=str(src), width="400px", crop=(10, 0, 10, 0))
            exported = generate_export_html()
        finally:
            reset_export_buffer(None)
        assert "stx-crop-box" in exported
        assert 'aspect-ratio:500 / 240;' in exported
        assert "data:image/png;base64," in exported
