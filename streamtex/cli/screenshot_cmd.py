"""Screenshot command: render a StreamTeX project to PNG images.

Launches the project with Streamlit in headless mode, drives a headless
Chromium via Playwright, and captures one PNG per slide (per ``.stx-block``
element) plus a full-page render. The output is meant to be consumed by a
vision model (Claude) for automated visual review — see the CE PROTOTYPE
gate — so that obvious defects (unreadable fonts, content overflow, empty
viewport) are detected automatically before asking the user to validate.

Requires the optional ``pdf`` extra (Playwright) and the Chromium browser::

    uv add "streamtex[pdf]"
    playwright install chromium

This reuses the proven launch pattern from ``tests/e2e/`` (headless
Streamlit on a free port + Chromium). The only new primitive versus PDF
export is ``page.screenshot()``.
"""

import json
import socket
import subprocess
import sys
import time
import urllib.request
from contextlib import closing
from pathlib import Path

import click

from .console import get_console

# Stable selector emitted around every rendered block (see book.py /
# the e2e readout JS which already relies on ``.stx-block``).
_BLOCK_SELECTOR = ".stx-block"

_PLAYWRIGHT_HINT = (
    "Screenshot capture requires Playwright + Chromium. Install with:\n"
    '  uv add "streamtex[pdf]"\n'
    "  uv run playwright install chromium"
)


def _free_port() -> int:
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_http(url: str, timeout_s: float = 60.0) -> None:
    """Block until *url* answers HTTP 200 or *timeout_s* elapses."""
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001 — connection refused is normal while booting
            last_err = exc
        time.sleep(0.4)
    raise TimeoutError(f"Streamlit never became ready on {url}: {last_err}")


def _streamlit_importable() -> bool:
    """True if the *current* interpreter can import Streamlit."""
    import importlib.util

    return importlib.util.find_spec("streamlit") is not None


def _streamlit_cmd(entry: str, port: int) -> list[str]:
    """Build the headless Streamlit launch command.

    Prefer the *current* interpreter when it can already import Streamlit —
    this is the case under pytest, an activated project venv, or when the CLI
    runs from the project's own ``.venv``, and it avoids a nested ``uv run``.
    Fall back to ``uv run streamlit`` (project venv resolution) only when the
    running interpreter lacks Streamlit, e.g. ``stx`` installed as a uv tool.
    """
    import shutil

    base = [
        "run", entry,
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.runOnSave", "false",
        "--browser.gatherUsageStats", "false",
    ]
    if _streamlit_importable():
        return [sys.executable, "-m", "streamlit", *base]
    uv = shutil.which("uv")
    if uv:
        return [uv, "run", "streamlit", *base]
    return [sys.executable, "-m", "streamlit", *base]


def capture_screenshots(
    book: str = "book.py",
    out_dir: str = "docs/_screens",
    *,
    viewport: tuple[int, int] = (1920, 1080),
    per_slide: bool = True,
    full_page: bool = True,
    settle_s: float = 3.0,
    boot_timeout_s: float = 90.0,
    console=None,
) -> dict:
    """Render *book* and capture PNG screenshots into *out_dir*.

    :param book: path to the project entry point (``book.py``).
    :param out_dir: directory where PNGs and ``manifest.json`` are written.
    :param viewport: Chromium viewport ``(width, height)`` — defaults to a
        projection-like 1920x1080 so per-slide font sizes reflect a real
        auditorium render.
    :param per_slide: capture one PNG per ``.stx-block`` element.
    :param full_page: also capture a full-page PNG of the whole render.
    :param settle_s: extra seconds to let Streamlit finish its cache-build
        overlay and the marker observer settle after the DOM is ready.
    :param boot_timeout_s: how long to wait for Streamlit to answer HTTP.
    :returns: the manifest dict (also written to ``out_dir/manifest.json``).
    :raises click.ClickException: if Playwright/Chromium is unavailable.
    """
    console = console or get_console()

    entry = Path(book)
    if not entry.is_file():
        raise click.ClickException(f"File not found: {book}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise click.ClickException(_PLAYWRIGHT_HINT) from exc

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    images: list[dict] = []

    # Streamlit is launched with cwd = the book's directory, so it must be
    # given the bare filename (a path relative to a different cwd would not
    # resolve and Streamlit would never start serving).
    console.print(f"[bold]Booting[/bold] {entry} headless on port [cyan]{port}[/cyan] …")
    proc = subprocess.Popen(
        _streamlit_cmd(entry.name, port),
        cwd=str(entry.resolve().parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_http(url, timeout_s=boot_timeout_s)

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as exc:  # noqa: BLE001
                # Most common cause: Chromium binary not downloaded yet.
                raise click.ClickException(
                    f"Could not launch Chromium ({exc}).\n{_PLAYWRIGHT_HINT}"
                ) from exc

            page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
            page.goto(url, wait_until="domcontentloaded")
            # Wait for the first rendered block, then let the app settle
            # (cache-build overlay disappears, marker observer finishes).
            try:
                page.wait_for_selector(_BLOCK_SELECTOR, timeout=int(boot_timeout_s * 1000))
            except Exception as exc:  # noqa: BLE001
                raise click.ClickException(
                    f"No rendered block ({_BLOCK_SELECTOR}) appeared — the project "
                    f"may have failed to render. ({exc})"
                ) from exc
            page.wait_for_timeout(int(settle_s * 1000))

            if full_page:
                full_path = out / "full.png"
                page.screenshot(path=str(full_path), full_page=True)
                images.append({"kind": "full", "file": full_path.name})
                console.print(f"  [green]✓[/green] {full_path.name}")

            if per_slide:
                blocks = page.query_selector_all(_BLOCK_SELECTOR)
                if not blocks:
                    console.print("  [yellow]No .stx-block elements found for per-slide capture.[/yellow]")
                for idx, el in enumerate(blocks, start=1):
                    name = f"slide-{idx:02d}.png"
                    try:
                        el.scroll_into_view_if_needed()
                        el.screenshot(path=str(out / name))
                        images.append({"kind": "slide", "index": idx, "file": name})
                    except Exception as exc:  # noqa: BLE001 — skip a non-capturable block, don't abort
                        console.print(f"  [yellow]skip {name}: {exc}[/yellow]")
                console.print(f"  [green]✓[/green] {len(blocks)} per-slide screenshot(s)")

            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    manifest = {
        "book": str(entry),
        "viewport": {"width": viewport[0], "height": viewport[1]},
        "count": len(images),
        "images": images,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    console.print(
        f"[bold green]Captured {len(images)} image(s)[/bold green] → {out}/ "
        f"(manifest.json)"
    )
    return manifest


@click.command(name="screenshot")
@click.argument("book", required=False, default="book.py")
@click.option("-o", "--out", "out_dir", default="docs/_screens",
              help="Output directory for PNGs + manifest.json.")
@click.option("--viewport", default="1920x1080",
              help="Chromium viewport WIDTHxHEIGHT (default: 1920x1080, projection-like).")
@click.option("--no-per-slide", is_flag=True,
              help="Skip per-block (.stx-block) screenshots.")
@click.option("--no-full-page", is_flag=True,
              help="Skip the full-page screenshot.")
@click.option("--settle", type=float, default=3.0,
              help="Seconds to wait after first render before capturing.")
def screenshot(book, out_dir, viewport, no_per_slide, no_full_page, settle):
    """Render a StreamTeX project to PNG screenshots (for visual review).

    Captures one PNG per slide (.stx-block) plus a full-page render, ready
    for automated vision review. Requires streamtex[pdf] + Chromium.
    """
    console = get_console()
    try:
        w_str, _, h_str = viewport.lower().partition("x")
        vp = (int(w_str), int(h_str))
    except ValueError as exc:
        raise click.ClickException(f"Invalid --viewport '{viewport}', expected WIDTHxHEIGHT.") from exc

    capture_screenshots(
        book=book,
        out_dir=out_dir,
        viewport=vp,
        per_slide=not no_per_slide,
        full_page=not no_full_page,
        settle_s=settle,
        console=console,
    )
