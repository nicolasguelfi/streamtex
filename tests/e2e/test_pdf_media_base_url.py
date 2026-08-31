"""Real-Chromium e2e for PDF relative-media resolution (issue #44).

A local ``http.server`` plays the Streamlit static-serving role: it
serves a generated PNG under ``app/static/media/``.  The document
references it RELATIVELY (the "served, never inlined" pattern).

  * without ``base_url``  -> the image cannot load: no Image XObject in
    the PDF (the 0.7.27 bug, kept as the documented no-base behaviour);
  * with ``base_url``     -> the image is painted: an Image XObject is
    embedded and the PDF grows accordingly;
  * a relative ``poster=`` on a <video> prints the poster the same way.

Run:  uv run pytest -m e2e tests/e2e/test_pdf_media_base_url.py -v
Prerequisite (one-time): uv run playwright install chromium
"""
from __future__ import annotations

import http.server
import socket
import struct
import threading
import zlib
from contextlib import closing

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from streamtex.pdf_export import PdfConfig, export_pdf  # noqa: E402

pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Minimal PNG (no Pillow dependency in the serving path)
# ---------------------------------------------------------------------------

def _png_bytes(width: int = 97, height: int = 53) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\xE8\x3E\x3E" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _free_port() -> int:
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def media_server(tmp_path_factory):
    """Serve app/static/media/portrait.png like a Streamlit server would."""
    root = tmp_path_factory.mktemp("srv")
    media = root / "app" / "static" / "media"
    media.mkdir(parents=True)
    (media / "portrait.png").write_bytes(_png_bytes())

    port = _free_port()
    handler = type(
        "Quiet",
        (http.server.SimpleHTTPRequestHandler,),
        {"log_message": lambda self, *a: None,
         "directory": str(root)},
    )

    def factory(*args, **kwargs):
        return handler(*args, directory=str(root), **kwargs)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), factory)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}/"
    finally:
        srv.shutdown()


_DOC = """<html><head><title>deck</title></head><body>
<h1>Figure slide</h1>
<img src="app/static/media/portrait.png" alt="portrait" width="200">
</body></html>"""

_DOC_POSTER = """<html><head><title>deck</title></head><body>
<h1>Video slide</h1>
<video poster="app/static/media/portrait.png" width="320" height="180">
  <source src="https://cdn.example.invalid/clip.mp4" type="video/mp4">
</video>
</body></html>"""


def _served_png_painted(pdf: bytes) -> bool:
    """True when the 97x53 served PNG is embedded as an Image XObject.

    A bare ``/Subtype /Image`` count cannot discriminate: when the load
    FAILS, Chromium paints the broken-image placeholder icon, which is
    itself an Image XObject.  The served PNG's distinctive dimensions
    (97x53) appear in its XObject dict only when it actually loaded.
    """
    if b"/Subtype /Image" not in pdf and b"/Subtype/Image" not in pdf:
        return False
    return b"/Width 97" in pdf and b"/Height 53" in pdf


def test_without_base_url_image_missing(media_server):
    pdf = export_pdf(_DOC, config=PdfConfig())
    assert pdf.startswith(b"%PDF")
    assert not _served_png_painted(pdf)  # the documented no-base behaviour


def test_with_base_url_image_painted(media_server):
    pdf = export_pdf(_DOC, config=PdfConfig(base_url=media_server))
    assert _served_png_painted(pdf)


def test_relative_poster_prints(media_server):
    pdf = export_pdf(_DOC_POSTER, config=PdfConfig(base_url=media_server))
    assert _served_png_painted(pdf)


def test_base_url_without_trailing_slash(media_server):
    pdf = export_pdf(_DOC, config=PdfConfig(base_url=media_server.rstrip("/")))
    assert _served_png_painted(pdf)
