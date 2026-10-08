"""PDF availability is read from disk, once per process (#98)."""

import json

import pytest

from streamtex import book


@pytest.fixture
def fake_playwright(tmp_path, monkeypatch):
    """A playwright package dir with browsers.json, and an empty browsers dir."""
    pkg = tmp_path / "playwright"
    (pkg / "driver" / "package").mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "driver" / "package" / "browsers.json").write_text(json.dumps(
        {"browsers": [{"name": "chromium", "revision": "1208"},
                      {"name": "firefox", "revision": "1482"}]}))
    browsers = tmp_path / "browsers"
    browsers.mkdir()
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(browsers))

    class _Spec:
        origin = str(pkg / "__init__.py")

    import importlib.util
    real_find_spec = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, "find_spec",
                        lambda name, *a: _Spec() if name == "playwright" else real_find_spec(name, *a))
    # the driver must never start
    import playwright.sync_api
    monkeypatch.setattr(playwright.sync_api, "sync_playwright",
                        lambda: (_ for _ in ()).throw(AssertionError("driver started")))
    book._is_pdf_available.cache_clear()
    yield browsers
    book._is_pdf_available.cache_clear()


def test_installed_chromium_is_found_without_the_driver(fake_playwright):
    done = fake_playwright / "chromium-1208"
    done.mkdir()
    (done / "INSTALLATION_COMPLETE").write_text("")
    assert book._is_pdf_available() is True


def test_missing_or_unfinished_chromium_is_not_available(fake_playwright):
    (fake_playwright / "chromium-1169").mkdir()              # another revision
    (fake_playwright / "chromium-1169" / "INSTALLATION_COMPLETE").write_text("")
    (fake_playwright / "chromium-1208").mkdir()              # no marker: unfinished
    assert book._is_pdf_available() is False


def test_checked_once_per_process(fake_playwright, monkeypatch):
    calls = []
    monkeypatch.setattr(book, "_chromium_installed_on_disk", lambda: calls.append(1) or True)
    book._is_pdf_available.cache_clear()
    assert book._is_pdf_available() and book._is_pdf_available()
    assert len(calls) == 1


def test_browsers_dir_zero_means_inside_the_package(monkeypatch, tmp_path):
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", "0")
    assert book._playwright_browsers_dir(str(tmp_path)) == str(
        tmp_path / "driver" / "package" / ".local-browsers")
