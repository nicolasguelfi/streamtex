"""Real-Chromium e2e for served-media materialisation in HTML exports (#48).

A deck following the "served, never inlined" pattern
(``configure_image_path``) exports HTML whose ``src="app/static/..."``
references only a running server can resolve — broken over ``file://``.
After ``materialize_served_media`` the export must paint the image from
the local ``data/`` folder (EXTERNAL) or from a data URI (EMBEDDED),
with no server anywhere.

Run:  uv run pytest -m e2e tests/e2e/test_export_served_media.py -v
"""
from __future__ import annotations

import struct
import zlib

import pytest

playwright = pytest.importorskip("playwright.sync_api")

pytestmark = pytest.mark.e2e


def _png_bytes(width: int = 97, height: int = 53) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\xE8\x3E\x3E" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


_DOC = """<html><head><title>deck</title></head><body>
<h1>Figure</h1>
<img id="served" src="app/static/media/portrait.png" alt="portrait">
</body></html>"""


@pytest.fixture()
def media_root(monkeypatch, tmp_path):
    import streamtex.image as image_mod
    media = tmp_path / "media"
    media.mkdir()
    (media / "portrait.png").write_bytes(_png_bytes())
    monkeypatch.setattr(image_mod, "_static_image_base", "app/static/media")
    monkeypatch.setattr(image_mod, "_static_image_fs_root", str(media))
    return tmp_path


@pytest.fixture(scope="module")
def browser():
    with playwright.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _natural_width(browser, url: str) -> int:
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state("networkidle")
    w = page.evaluate("document.getElementById('served').naturalWidth")
    page.close()
    return int(w)


def test_raw_export_is_broken_over_file(browser, media_root, tmp_path):
    """Pin the pre-#48 behaviour: the served ref paints nothing."""
    out = tmp_path / "raw.html"
    out.write_text(_DOC, encoding="utf-8")
    assert _natural_width(browser, out.as_uri()) == 0


def test_external_mode_paints_from_data_folder(browser, media_root, tmp_path):
    from streamtex.export import AssetCollector, materialize_served_media
    collector = AssetCollector()
    html = materialize_served_media(_DOC, collector)
    assert 'src="data/images/portrait_' in html
    html_path = collector.write_to_disk(html, str(tmp_path / "out"), "deck")
    from pathlib import Path
    assert _natural_width(browser, Path(html_path).as_uri()) == 97


def test_embedded_mode_paints_from_data_uri(browser, media_root, tmp_path):
    from streamtex.export import materialize_served_media
    html = materialize_served_media(_DOC, None)
    out = tmp_path / "embedded.html"
    out.write_text(html, encoding="utf-8")
    assert _natural_width(browser, out.as_uri()) == 97
