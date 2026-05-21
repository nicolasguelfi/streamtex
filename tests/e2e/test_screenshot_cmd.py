"""E2E — ``stx screenshot`` renders a project to PNGs via headless Chromium.

Validates the foundation of the automated visual-review gate (CE PROTOTYPE):
booting a project headless, driving Chromium, and capturing one PNG per
``.stx-block`` plus a full-page render.

Run with:
    uv run pytest -m e2e tests/e2e/test_screenshot_cmd.py -v -s

CI prerequisite (one-time per runner):
    uv run playwright install chromium
"""

import json
from pathlib import Path

import pytest

# Skip cleanly if Playwright (the `pdf` extra) is not installed.
pytest.importorskip("playwright.sync_api")

from streamtex.cli.screenshot_cmd import capture_screenshots  # noqa: E402

pytestmark = pytest.mark.e2e

FIXTURE_BOOK = (
    Path(__file__).resolve().parent / "fixtures" / "marker_observer_app" / "book.py"
)


def test_screenshot_captures_pngs(tmp_path):
    out_dir = tmp_path / "_screens"
    manifest = capture_screenshots(
        book=str(FIXTURE_BOOK),
        out_dir=str(out_dir),
        viewport=(1280, 720),
        per_slide=True,
        full_page=True,
        settle_s=3.0,
    )

    # Manifest is well-formed and persisted.
    assert manifest["count"] >= 1
    persisted = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert persisted["count"] == manifest["count"]
    assert persisted["viewport"] == {"width": 1280, "height": 720}

    # Full-page render exists and is a non-trivial PNG.
    full = out_dir / "full.png"
    assert full.is_file() and full.stat().st_size > 1000

    # At least one per-slide screenshot was produced and is non-empty.
    slides = sorted(out_dir.glob("slide-*.png"))
    assert slides, "no per-slide screenshots captured"
    assert all(s.stat().st_size > 0 for s in slides)

    # Every manifest entry points to a file that actually exists on disk.
    for img in manifest["images"]:
        assert (out_dir / img["file"]).is_file()


def test_screenshot_full_page_only(tmp_path):
    out_dir = tmp_path / "_screens"
    manifest = capture_screenshots(
        book=str(FIXTURE_BOOK),
        out_dir=str(out_dir),
        per_slide=False,
        full_page=True,
        settle_s=2.0,
    )
    assert manifest["count"] == 1
    assert manifest["images"][0]["kind"] == "full"
    assert not list(out_dir.glob("slide-*.png"))
