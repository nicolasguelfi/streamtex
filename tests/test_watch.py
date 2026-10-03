"""Data files kept live (#77) and the page-cache key (#53)."""

import os
import time
import types

import pytest

import streamtex as stx
from streamtex import watch
from streamtex.book import _compute_cache_hash


@pytest.fixture(autouse=True)
def _clean():
    watch._reset_for_tests()
    yield
    watch._reset_for_tests()


def _touch_later(path, text):
    """Rewrite *path* with a strictly later mtime (coarse filesystem clocks)."""
    before = os.path.getmtime(path)
    path.write_text(text)
    os.utime(path, (before + 2, before + 2))


def test_load_json_rereads_on_change_and_registers(tmp_path):
    f = tmp_path / "t.json"
    f.write_text('{"a": 1}')
    assert stx.load_json(f) == {"a": 1}
    assert stx.load_json(f) is stx.load_json(f)          # cached while unchanged
    _touch_later(f, '{"a": 2}')
    assert stx.load_json(f) == {"a": 2}
    assert str(f.resolve()) in watch.watched_files() or os.path.abspath(f) in watch.watched_files()


def test_load_toml_and_text(tmp_path):
    t = tmp_path / "s.toml"
    t.write_text("x = 1\n")
    assert stx.load_toml(t) == {"x": 1}
    m = tmp_path / "n.md"
    m.write_text("hello")
    assert stx.load_text(m) == "hello"
    _touch_later(m, "bye")
    assert stx.load_text(m) == "bye"


def test_snapshot_detects_a_change(tmp_path):
    f = tmp_path / "w.csv"
    f.write_text("a")
    stx.watch_file(f)
    snap = watch.watched_snapshot()
    assert watch.snapshot_is_current(snap)
    _touch_later(f, "b")
    assert not watch.snapshot_is_current(snap)
    assert watch.snapshot_is_current(None)


def _block(tmp_path, name):
    d = tmp_path / "proj" / "blocks"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{name}.py"
    f.write_text("def build(**_): pass\n")
    m = types.ModuleType(f"blocks.{name}")
    m.__file__ = str(f)
    return m


def test_cache_hash_covers_every_custom_module_and_block_helpers(tmp_path):
    m = _block(tmp_path, "bck_a")
    proj = tmp_path / "proj"
    (proj / "custom" / "sub").mkdir(parents=True)
    cfg = proj / "custom" / "config.py"
    cfg.write_text("X = 1\n")
    deep = proj / "custom" / "sub" / "timers.py"
    deep.write_text("T = 1\n")
    helper = proj / "blocks" / "shared_widgets.py"
    helper.write_text("def w(): pass\n")
    h0 = _compute_cache_hash([m])
    for f in (cfg, deep, helper):
        _touch_later(f, f.read_text() + "# edit\n")
        h1 = _compute_cache_hash([m])
        assert h1 != h0, f
        h0 = h1


def test_cache_hash_unchanged_without_extra_files(tmp_path):
    m = _block(tmp_path, "bck_a")
    assert _compute_cache_hash([m]) == _compute_cache_hash([m])
    time.sleep(0)  # no file touched: stable
