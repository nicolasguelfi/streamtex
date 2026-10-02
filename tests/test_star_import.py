"""``from streamtex import *`` exports the API, never a sub-module (L14).

A sub-module named like a builtin (``streamtex/list.py``) used to shadow the
builtin ``list`` in every block that star-imports streamtex.
"""

import builtins
import types

import streamtex


def _star() -> dict:
    ns: dict = {}
    exec("from streamtex import *", ns)  # noqa: S102 — this is the behaviour under test
    return ns


def test_star_import_never_exports_a_module():
    ns = _star()
    modules = sorted(k for k, v in ns.items() if isinstance(v, types.ModuleType))
    assert modules == []


def test_star_import_keeps_the_builtins():
    ns = _star()
    for name in ("list", "type", "id", "format", "filter", "input", "open"):
        assert name not in ns or ns[name] is getattr(builtins, name), name


def test_all_names_exist_and_are_public():
    assert len(streamtex.__all__) == len(set(streamtex.__all__))
    for name in streamtex.__all__:
        assert hasattr(streamtex, name), name
        assert not isinstance(getattr(streamtex, name), types.ModuleType), name


def test_core_api_still_star_exported():
    ns = _star()
    for name in ("st_write", "st_block", "st_grid", "st_list", "st_image", "st_book", "st_zoom",
                 "st_space", "st_marker", "st_slide_break", "Style", "StxStyles", "Tags",
                 "ListStyle", "ViewMode", "PresentationConfig", "MarkerConfig", "cite",
                 "configure_image_path", "set_static_sources"):
        assert name in ns, name


def test_submodules_remain_importable_explicitly():
    import streamtex.list as stx_list
    from streamtex import styles  # noqa: F401

    assert hasattr(stx_list, "st_list")
