"""``stx validate --build`` — run the REAL ``build()`` of every block (L11, L16).

A green count of imports says nothing about what reaches the screen: blocks
that raise at run time (a bad enum member, a wrong keyword), media that
resolve to nothing (an empty frame, no error) or media inlined as megabytes
of base64 all pass an import check. This check executes each ``book.py`` of
the project under Streamlit's ``AppTest`` (no browser), with a checking
``st_book`` that sets up what the real one sets up (bibliography, TOC,
markers) and then calls every block's ``build()`` separately, with the
book's own ``block_args`` / ``block_kwargs``, recording per block:

- the exception, if ``build()`` raises (error);
- every image whose URI resolves to nothing (warning: an empty frame);
- every image inlined as base64 above a size limit (warning: serve it with
  ``configure_image_path`` + ``set_static_sources``).

Each book runs in its own subprocess: books of one project share module
names (``blocks``, ``custom``…), and a fresh interpreter is the only clean
isolation. A static pass adds a warning for a styled ``st_block`` whose body
is empty — it renders nothing in the app (but something in the export).
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

INLINE_LIMIT_BYTES = 512 * 1024
_SKIP_DIRS = {".venv", "venv", "node_modules", "static", "__pycache__", ".git", ".stx_cache",
              "_archive", "_ARCHIVE", "site-packages", ".claude", "dist", "build"}

# The script AppTest executes. Kept as text: AppTest runs a file.
_RUNNER = r'''
import json, os, runpy, sys, traceback

OUT = os.environ["STX_BUILD_CHECK_OUT"]
BOOK = os.environ["STX_BUILD_CHECK_BOOK"]
LIMIT = int(os.environ.get("STX_BUILD_CHECK_INLINE_LIMIT", "524288"))
res = {"blocks": 0, "errors": [], "missing_media": [], "inlined_media": [], "book_error": None}
current = ["(book)"]

import streamtex
import streamtex.book as _book
import streamtex.image as _img

_orig_src = _img.get_image_src


def _served_path(uri):
    """Disk path behind a configure_image_path-served URI (the book's static dir)."""
    if _img._static_image_fs_root:
        return os.path.join(_img._static_image_fs_root, uri)
    prefix = _img._static_image_base
    if prefix == "app/static" or prefix.startswith("app/static/"):
        rest = prefix[len("app/static"):].lstrip("/")
        return os.path.join(os.path.dirname(BOOK), "static", rest, uri)  # = _crop._app_static_dir
    return None


def _src(uri):
    out = _orig_src(uri)
    if uri and not out:
        res["missing_media"].append([current[0], str(uri)])
    elif uri and out == f"{_img._static_image_base}/{uri}":
        path = _served_path(uri)
        if path is not None and not os.path.isfile(path):
            res["missing_media"].append([current[0], str(uri)])
    elif isinstance(out, str) and out.startswith("data:") and len(out) > LIMIT * 4 // 3:
        res["inlined_media"].append([current[0], str(uri), len(out) * 3 // 4])
    return out


_img.get_image_src = _src

# Under AppTest the main script is this runner, not the book: point
# Streamlit's app/static convention (used by crop= on served media) at the
# book's own static/ directory, as it is in the real app.
try:
    import streamtex.image_crop as _crop
    _crop._app_static_dir = lambda: os.path.join(os.path.dirname(BOOK), "static")
except Exception:
    pass


def _check_book(module_list, toc_config=None, marker_config=None, *args, block_args=(),
                block_kwargs=None, bib_sources=None, bib_config=None, lang=None, **kwargs):
    from streamtex.export import ExportConfig, reset_export_buffer

    if lang is not None:  # same rule as st_book(lang=…)
        from streamtex.i18n import current_lang
        block_kwargs = {"lang": current_lang() if lang == "auto" else lang, **(block_kwargs or {})}
    from streamtex.marker import reset_marker_registry
    from streamtex.toc import reset_toc_registry

    try:
        _book._setup_bibliography(bib_sources, bib_config)
    except Exception as e:  # a broken .bib is a book error, not a block error
        res["errors"].append(["(bibliography)", type(e).__name__, str(e)[:300], ""])
    reset_toc_registry(toc_config)
    if marker_config is not None:
        reset_marker_registry(marker_config)
    reset_export_buffer(ExportConfig(enabled=False))
    for m in module_list:
        name = getattr(m, "__name__", repr(m))
        current[0] = name
        if m is None:
            res["errors"].append([name, "BlockNotFound", "block module is None", ""])
            continue
        if not hasattr(m, "build"):
            res["errors"].append([name, "NoBuild", "no build() function", ""])
            continue
        res["blocks"] += 1
        try:
            m.build(*block_args, **(block_kwargs or {}))
        except Exception as e:
            res["errors"].append([name, type(e).__name__, str(e)[:300],
                                  traceback.format_exc(limit=-2)[-900:]])
    current[0] = "(book)"


# Optional capture of the HTML each block emits (stx validate --snapshot/--against).
if os.environ.get("STX_BUILD_CHECK_CAPTURE"):
    import hashlib, re
    import streamtex.export as _exp

    _orig_html = _exp.st_html
    res["html"] = {}
    _data_uri = re.compile(r"data:[^\"')\s]+")

    def _norm(html):
        return _data_uri.sub(lambda m: "data:" + hashlib.sha256(m.group(0).encode()).hexdigest()[:12],
                             str(html))

    def _capture(html, *a, **k):
        res["html"].setdefault(current[0], []).append(_norm(html))
        return _orig_html(html, *a, **k)

    for _m in list(sys.modules.values()):
        if getattr(_m, "__name__", "").startswith("streamtex"):
            for _attr in ("_render", "st_html"):
                if getattr(_m, _attr, None) is _orig_html:
                    setattr(_m, _attr, _capture)

streamtex.st_book = _check_book
_book.st_book = _check_book
os.chdir(os.path.dirname(BOOK))
sys.path.insert(0, os.path.dirname(BOOK))
try:
    runpy.run_path(BOOK, run_name="__main__")
except SystemExit:
    pass
except Exception as e:
    res["book_error"] = f"{type(e).__name__}: {e}"[:500]
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f)
'''


@dataclass
class BookResult:
    book: str
    blocks: int = 0
    errors: list = field(default_factory=list)          # [block, type, message, trace]
    missing_media: list = field(default_factory=list)   # [block, uri]
    inlined_media: list = field(default_factory=list)   # [block, uri, bytes]
    book_error: str | None = None
    html: dict = field(default_factory=dict)            # block -> [html fragments] (capture)


def discover_books(project_dir: str | os.PathLike, max_depth: int = 4) -> list[Path]:
    """Every ``book.py`` under *project_dir* (root, ``modules/*``, ``trainings/**``…)."""
    root = Path(project_dir).resolve()
    books: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_depth = len(Path(dirpath).relative_to(root).parts)
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS and not d.startswith("."))
        if rel_depth >= max_depth:
            dirnames[:] = []
        if "book.py" in filenames:
            books.append(Path(dirpath) / "book.py")
    return sorted(books)


def run_book(book: Path, timeout: int = 120, *, capture: bool = False) -> BookResult:
    """Execute *book* under AppTest in a subprocess and collect per-block results."""
    with tempfile.TemporaryDirectory(prefix="stx-build-") as tmp:
        runner = Path(tmp) / "stx_build_runner.py"
        runner.write_text(_RUNNER, encoding="utf-8")
        out = Path(tmp) / "result.json"
        driver = (
            "import sys\n"
            "from streamlit.testing.v1 import AppTest\n"
            f"at = AppTest.from_file({str(runner)!r}, default_timeout={int(timeout)})\n"
            "at.run()\n"
            "if at.exception:\n"
            "    print('APPTEST_EXCEPTION', [e.value for e in at.exception], file=sys.stderr)\n"
        )
        env = {**os.environ, "STX_BUILD_CHECK_OUT": str(out), "STX_BUILD_CHECK_BOOK": str(book),
               "STX_BUILD_CHECK_INLINE_LIMIT": str(INLINE_LIMIT_BYTES)}
        if capture:
            env["STX_BUILD_CHECK_CAPTURE"] = "1"
        try:
            proc = subprocess.run([sys.executable, "-c", driver], cwd=str(book.parent), env=env,
                                  capture_output=True, text=True, timeout=timeout + 60)
        except subprocess.TimeoutExpired:
            return BookResult(str(book), book_error=f"timed out after {timeout}s")
        if not out.is_file():
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-3:]
            return BookResult(str(book), book_error="runner produced no result: " + " | ".join(tail))
        data = json.loads(out.read_text(encoding="utf-8"))
    return BookResult(str(book), data["blocks"], data["errors"], data["missing_media"],
                      data["inlined_media"], data["book_error"], data.get("html", {}))


def block_fingerprints(result: BookResult) -> dict[str, str]:
    """``{block: sha256}`` of the HTML each block emitted (base64 media hashed)."""
    import hashlib

    return {block: hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
            for block, parts in sorted(result.html.items())}


def empty_styled_blocks(project_dir: str | os.PathLike) -> list[tuple[str, int]]:
    """``with st_block(<style>):`` whose body is only ``pass`` / ``...`` / a docstring.

    It renders nothing in the app but a styled box in the HTML export.
    """
    found: list[tuple[str, int]] = []
    root = Path(project_dir).resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            if not f.endswith(".py"):
                continue
            p = Path(dirpath) / f
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
            except (SyntaxError, ValueError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.With):
                    continue
                for item in node.items:
                    call = item.context_expr
                    if not (isinstance(call, ast.Call) and getattr(call.func, "id", None) == "st_block"
                            and (call.args or call.keywords)):
                        continue
                    if all(isinstance(s, ast.Pass) or (isinstance(s, ast.Expr)
                           and isinstance(s.value, ast.Constant)) for s in node.body):
                        found.append((str(p.relative_to(root)), node.lineno))
    return found
