"""Where each slide is written, copied from the browser in one gesture (#157).

Every stop of a book records its **source** when it is registered
(``MarkerRegistry.register``): the file and the line of the ``with
st_slide(...)`` / ``st_marker(...)`` call (the first frame outside the
library, ``contextlib`` and the project's helper modules), the book entry
being rendered, its rank among the stops of that file in that entry and a
stable key (``<file without bck_>#<rank>``, the key of ``slide_map.py``)::

    entry["source"] == {"file": "content/atoms/bck_trainer_ng_who.py", "line": 33,
                        "entry": "bck_who", "rank": 1, "of": 1, "key": "trainer_ng_who#1"}

The source is always recorded (``marker_entries()``, the page cache). A page
carries it only when its side is turned on — two independent settings, the
live app and the HTML export, both ``"off"`` by default::

    st_book([...], source={"live": "on"})       # or [book.defaults.source] in stx.toml

With ``"on"``, in the floating marker bar: Option-click on the counter
``n / N`` (or a click on the footer's ``Slide n / N``, or Ctrl+Option+Cmd+L)
copies the line of the slide shown::

    GAI4AS21H/slides · 5/407 · content/atoms/bck_trainer_ng_who.py:33 · trainer_ng_who#1 · « Qui ? » · release da8a1dde

and Cmd-click on the counter (or Ctrl+Option+Cmd+O) opens the file at that
line in the editor (Cursor by default), in the live app run on this computer.
Every key and click is a setting; the environment variables ``STX_SOURCE_*``
override the book for a run or an export without editing it. A site
published by ``stx release`` carries none of it unless its target says so.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field, fields, replace

logger = logging.getLogger(__name__)

#: Written by ``stx release`` at the root of a published snapshot: the release name and the target's
#: source settings, which win over the book's (a published site shows no path unless its target says so).
PUBLISHED_FILE = "stx-published.json"

SIDES = ("live", "html")
_ON = {"on", "hidden", "visible", "true", "yes", "1"}
_OFF = {"off", "false", "no", "0", ""}
#: ``STX_SOURCE_<FIELD>`` overrides the book for each field of :class:`SourceConfig` (``skip``: commas).
ENV_PREFIX = "STX_SOURCE_"


@dataclass
class SourceConfig:
    """The settings of the source gesture (#157); see the module docstring.

    :param live: ``"on"`` / ``"off"`` (default) — the live app.
    :param html: ``"on"`` / ``"off"`` (default) — the HTML export, independent of *live*.
    :param copy_key: the shortcut that copies the line (``"ctrl+alt+meta+l"``; ``""``: none).
    :param open_key: the shortcut that opens the file in the editor (``"ctrl+alt+meta+o"``).
    :param copy_click: the modifiers held while clicking the counter to copy (``"alt"``).
    :param open_click: the modifiers held while clicking the counter to open the editor (``"meta"``).
    :param editor: the address that opens a file, ``{abs}`` (absolute path), ``{file}``
        (relative path) and ``{line}`` filled in (``"cursor://file/{abs}:{line}"``;
        ``"vscode://file/{abs}:{line}"`` for VS Code; ``""``: no editor).
    :param document: the document's name in the line (default: the book's folder).
    :param skip: module names (or prefixes ending with ``.``) of project helpers that
        open ``with st_slide(...)`` themselves for the blocks: the source is the frame
        that called them. A helper that only returns ``st_slide(...)`` (an alias) needs
        none: the slide is registered when the block's ``with`` enters it.
    """

    live: str = "off"
    html: str = "off"
    copy_key: str = "ctrl+alt+meta+l"
    open_key: str = "ctrl+alt+meta+o"
    copy_click: str = "alt"
    open_click: str = "meta"
    editor: str = "cursor://file/{abs}:{line}"
    document: str = ""
    skip: tuple[str, ...] = field(default_factory=tuple)

    def is_on(self, side: str) -> bool:
        return getattr(self, side) == "on"


def _switch(value, name: str) -> str:
    text = str(value).strip().lower() if not isinstance(value, bool) else ("on" if value else "off")
    if text in _ON:
        return "on"
    if text in _OFF:
        return "off"
    raise ValueError(f"source: {name} = {value!r}, expected \"on\" or \"off\"")


def _merge(cfg: SourceConfig, values) -> SourceConfig:
    """*cfg* with the fields of *values* (a mapping, a ``SourceConfig``, ``True``/``"on"`` = both sides)."""
    if values is None:
        return cfg
    if isinstance(values, SourceConfig):
        values = {f.name: getattr(values, f.name) for f in fields(values)}
    elif isinstance(values, (bool, str)):
        values = {"live": values, "html": values}
    if not isinstance(values, dict):
        raise TypeError(f"source: expected a dict or a SourceConfig, not {type(values).__name__}")
    known = {f.name for f in fields(SourceConfig)}
    unknown = set(values) - known
    if unknown:
        raise ValueError(f"source: unknown setting(s) {sorted(unknown)} (known: {', '.join(sorted(known))})")
    out = {}
    for name, value in values.items():
        if name in SIDES:
            out[name] = _switch(value, name)
        elif name == "skip":
            out[name] = tuple(value.split(",")) if isinstance(value, str) else tuple(value)
            out[name] = tuple(s.strip() for s in out[name] if s.strip())
        else:
            out[name] = "" if value is None else str(value)
    return replace(cfg, **out)


def _from_env(environ) -> dict:
    return {f.name: environ[ENV_PREFIX + f.name.upper()] for f in fields(SourceConfig)
            if ENV_PREFIX + f.name.upper() in environ}


# -- the keys and the clicks, for the page --------------------------------------------------

_MODS = {"ctrl": "ctrl", "control": "ctrl", "alt": "alt", "option": "alt", "opt": "alt",
         "meta": "meta", "cmd": "meta", "command": "meta", "super": "meta", "shift": "shift"}
_SYMBOLS = {"ctrl": "⌃", "alt": "⌥", "shift": "⇧", "meta": "⌘"}


def parse_combo(text: str, *, key: bool) -> dict | None:
    """``"ctrl+alt+meta+l"`` → ``{"ctrl": True, "alt": True, "meta": True, "shift": False, "code": "KeyL"}``.

    The physical key (``KeyboardEvent.code``): Option changes the character typed (Option+L is
    "¬"). *key* False: modifiers only, for a click (``"alt"``). ``""`` → ``None`` (turned off).
    """
    parts = [p.strip().lower() for p in text.replace("-", "+").split("+") if p.strip()]
    if not parts:
        return None
    combo = {"ctrl": False, "alt": False, "meta": False, "shift": False}
    code = None
    for p in parts:
        if p in _MODS:
            combo[_MODS[p]] = True
        elif key and code is None and len(p) == 1 and p.isalpha():
            code = "Key" + p.upper()
        elif key and code is None and len(p) == 1 and p.isdigit():
            code = "Digit" + p
        elif key and code is None and p[:1] == "f" and p[1:].isdigit() and 1 <= int(p[1:]) <= 12:
            code = p.upper()
        else:
            raise ValueError(f"source: {text!r} — unknown part {p!r}")
    if key and code is None:
        raise ValueError(f"source: {text!r} names no key")
    if not key and not any(combo.values()):
        raise ValueError(f"source: {text!r} — a click needs at least one modifier")
    if key:
        combo["code"] = code
    return combo


def combo_text(combo: dict | None) -> str:
    """``⌃⌥⌘L`` for the tooltips."""
    if not combo:
        return ""
    mods = "".join(sym for name, sym in _SYMBOLS.items() if combo.get(name))
    code = combo.get("code", "")
    return mods + (code[3:] if code.startswith("Key") else code[5:] if code.startswith("Digit") else code)


# -- the book being rendered ---------------------------------------------------------------

@dataclass
class _Book:
    config: SourceConfig = field(default_factory=SourceConfig)
    root: str | None = None
    document: str = ""
    published: dict | None = None
    entry: str | None = None


_book = _Book()
_release_cache: dict[str, tuple[float, str]] = {}


def _find_root(start: str) -> tuple[str, dict | None]:
    """The project root above *start* and the published record found there (``None`` locally).

    The nearest folder holding ``stx-published.json`` (a published snapshot) or ``.git``;
    otherwise the nearest ``stx.toml``; otherwise *start*.
    """
    cur = os.path.abspath(start)
    toml = None
    while True:
        pub = os.path.join(cur, PUBLISHED_FILE)
        if os.path.isfile(pub):
            try:
                with open(pub, encoding="utf-8") as fh:
                    return cur, json.load(fh)
            except (OSError, ValueError):
                logger.warning("%s unreadable: the site is taken as not published", pub)
                return cur, None
        if os.path.exists(os.path.join(cur, ".git")):
            return cur, None
        if toml is None and os.path.isfile(os.path.join(cur, "stx.toml")):
            toml = cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return toml or os.path.abspath(start), None
        cur = parent


def document_name(book_dir: str, root: str) -> str:
    """The book's folder from the project root, without its first folder when deeper than two.

    ``trainings/GAI4AS21H/slides`` → ``GAI4AS21H/slides``; the root itself → its own name.
    """
    rel = os.path.relpath(os.path.abspath(book_dir), root).replace(os.sep, "/")
    if rel in (".", "") or rel.startswith(".."):
        return os.path.basename(os.path.abspath(book_dir))
    parts = rel.split("/")
    return "/".join(parts[1:] if len(parts) > 2 else parts)


def begin_book(source, book_dir: str, environ=None) -> SourceConfig:
    """Resolve the settings for this run of ``st_book`` and remember the book.

    Lowest to highest: the defaults, ``st_book(source=)`` (or ``[book.defaults.source]``),
    the published record's ``source`` (a site of ``stx release``), ``STX_SOURCE_*``.
    """
    environ = os.environ if environ is None else environ
    root, published = _find_root(book_dir)
    cfg = _merge(SourceConfig(), source)
    if published and isinstance(published.get("source"), dict):
        cfg = _merge(cfg, {k: v for k, v in published["source"].items() if k in SIDES})
    elif published:
        cfg = replace(cfg, live="off", html="off")
    cfg = _merge(cfg, _from_env(environ))
    for name in ("copy_key", "open_key"):
        parse_combo(getattr(cfg, name), key=True)
    for name in ("copy_click", "open_click"):
        parse_combo(getattr(cfg, name), key=False)
    _book.config, _book.root, _book.published, _book.entry = cfg, root, published, None
    _book.document = cfg.document or document_name(book_dir, root)
    return cfg


def get_source_config() -> SourceConfig:
    """The settings resolved by the last ``st_book`` run."""
    return _book.config


def set_entry(module) -> None:
    """The book entry being rendered (called by ``st_book`` before each entry)."""
    name = getattr(module, "__name__", None) if module is not None else None
    _book.entry = name.rsplit(".", 1)[-1] if name else None


# -- recording ----------------------------------------------------------------------------

def _skipped(name: str, skip: tuple[str, ...]) -> bool:
    if name == "streamtex" or name.startswith("streamtex.") or name == "contextlib":
        return True
    return any(name == s or (s.endswith(".") and name.startswith(s)) for s in skip)


def capture(depth: int = 2) -> dict | None:
    """``{"file", "line", "entry"}`` of the first frame outside the library, or ``None``.

    The file is relative to the project root (POSIX separators). A plain walk of the
    frames: no source file is read.
    """
    try:
        frame = sys._getframe(depth)
    except ValueError:
        return None
    skip = _book.config.skip
    while frame is not None and _skipped(frame.f_globals.get("__name__", ""), skip):
        frame = frame.f_back
    if frame is None:
        return None
    path = frame.f_code.co_filename
    root = _book.root or os.getcwd()
    if os.path.isabs(path):
        rel = os.path.relpath(path, root)
        path = (path if rel.startswith("..") else rel).replace(os.sep, "/")
    return {"file": path, "line": frame.f_lineno, "entry": _book.entry}


def _stem(path: str) -> str:
    name = path.replace("\\", "/").rsplit("/", 1)[-1]
    name = name[:-3] if name.endswith(".py") else name
    return name[4:] if name.startswith("bck_") else name


def annotate_sources(entries: list[dict]) -> list[dict]:
    """Write ``rank``, ``of`` and ``key`` into the source of each stop, in place.

    The rank counts the stops of one file within one run of the same entry, as
    ``slide_map.py`` did: a block included by another has its own ranks, and the
    host block takes its own back after it. The key is always
    ``<file without bck_>#<rank>``, even for a marker with its own ``key=``: the
    author's notes on the slides are filed under it (board t157, y1).
    """
    counts: dict[tuple[int, str], int] = {}
    stops = []
    run, prev = -1, object()
    for e in entries:
        src = e.get("source")
        if not src or not e.get("stop", True):
            continue
        if src.get("entry") != prev:
            run, prev = run + 1, src.get("entry")
        k = (run, src.get("file", ""))
        counts[k] = counts.get(k, 0) + 1
        src["rank"] = counts[k]
        stops.append((k, src, e))
    for k, src, _e in stops:
        src["of"] = counts[k]
        src["key"] = f"{_stem(src.get('file', ''))}#{src['rank']}"
    return entries


def without_sources(entries: list[dict] | None) -> list[dict]:
    """*entries* as the page receives them when its side is off: no ``source`` at all."""
    return [{k: v for k, v in e.items() if k != "source"} if "source" in e else e for e in (entries or [])]


# -- the page ----------------------------------------------------------------------------

def release_name(root: str | None = None) -> str:
    """The published release; locally the short commit, ``+`` when tracked files are modified."""
    if _book.published and _book.published.get("release"):
        return str(_book.published["release"])
    root = root or _book.root
    if not root:
        return ""
    hit = _release_cache.get(root)
    if hit and time.monotonic() - hit[0] < 10:
        return hit[1]
    name = ""
    try:
        sha = subprocess.run(["git", "-C", root, "rev-parse", "--short=8", "HEAD"],
                             capture_output=True, text=True, timeout=5)
        if sha.returncode == 0:
            dirty = subprocess.run(["git", "-C", root, "status", "--porcelain", "--untracked-files=no"],
                                   capture_output=True, text=True, timeout=5)
            name = sha.stdout.strip() + ("+" if dirty.stdout.strip() else "")
    except (OSError, subprocess.SubprocessError):
        name = ""
    _release_cache[root] = (time.monotonic(), name)
    return name


def page_payload(side: str) -> dict | None:
    """What the page of *side* (``"live"`` / ``"html"``) needs, or ``None`` when that side is off.

    The absolute root (for the editor) only in the live app of an unpublished book.
    """
    cfg = _book.config
    if not cfg.is_on(side):
        return None
    copy_key, open_key = parse_combo(cfg.copy_key, key=True), parse_combo(cfg.open_key, key=True)
    copy_click, open_click = parse_combo(cfg.copy_click, key=False), parse_combo(cfg.open_click, key=False)
    root = _book.root if side == "live" and not _book.published and cfg.editor else ""
    hints = []
    if copy_click:
        hints.append(f"{combo_text(copy_click)}-click or {combo_text(copy_key) or '—'}: "
                     "copy where this slide is written")
    if open_click and root:
        hints.append(f"{combo_text(open_click)}-click or {combo_text(open_key) or '—'}: open it in the editor")
    return {"doc": _book.document, "release": release_name(), "copyKey": copy_key, "openKey": open_key,
            "copyClick": copy_click, "openClick": open_click, "editor": cfg.editor if root else "",
            "root": (root or "").replace(os.sep, "/"), "hint": " · ".join(hints),
            "footHint": f"Click or {combo_text(copy_key) or '—'}: copy where this slide is written"}


#: Runs inside the marker bar's script (live widget and export bar): needs ``markers``,
#: ``stops``, ``stopOf``, ``stopNumber``, ``currentLabel``, ``currentIdx`` and ``counter``, plus
#: ``srcDoc`` / ``srcWin`` (the page's document and window) and ``S`` (:func:`page_payload`).
_SOURCE_JS = r"""
    /* #157 — where the slide is written: copy it, open it in the editor */
    (function () {
        function stopEntry() { var s = stopOf(currentIdx); return s >= 0 ? stops[s] : null; }
        function lineText() {
            var m = stopEntry(), src = m && m.source, parts = [];
            if (S.doc) parts.push(S.doc);
            parts.push(stopNumber() + '/' + stops.length);
            parts.push(src ? src.file + ':' + src.line : '?');
            if (src && src.key) parts.push(src.key);
            var lb = currentLabel();
            if (lb) parts.push('« ' + lb + ' »');
            if (S.release) parts.push('release ' + S.release);
            return parts.join(' · ');
        }
        function toast(msg) {
            var d = srcDoc.getElementById('stx-src-toast');
            if (!d) {
                d = srcDoc.createElement('div');
                d.id = 'stx-src-toast';
                d.setAttribute('role', 'status');
                d.style.cssText = 'position:fixed;left:50%;bottom:72px;transform:translateX(-50%);z-index:2147483646;'
                    + 'max-width:90vw;padding:6px 12px;border-radius:6px;background:rgba(30,30,30,.92);color:#eee;'
                    + 'font:12px/1.4 system-ui,sans-serif;pointer-events:none;transition:opacity .2s;opacity:0;';
                srcDoc.body.appendChild(d);
            }
            d.textContent = msg;
            d.style.opacity = '1';
            clearTimeout(srcWin._stxSrcToastTimer);
            srcWin._stxSrcToastTimer = setTimeout(function () { d.style.opacity = '0'; }, 2200);
        }
        function fallbackCopy(text) {
            var prev = srcDoc.activeElement, ta = srcDoc.createElement('textarea'), ok = false;
            ta.value = text;
            ta.setAttribute('readonly', '');
            ta.style.cssText = 'position:fixed;top:-1000px;left:0;opacity:0;';
            srcDoc.body.appendChild(ta);
            ta.select();
            try { ok = srcDoc.execCommand('copy'); } catch (e) {}
            srcDoc.body.removeChild(ta);
            try { if (prev && prev.focus) prev.focus(); } catch (e) {}
            return ok;
        }
        function copySource() {
            var text = lineText();
            function done(ok) { toast((ok ? 'Copied: ' : 'Could not copy: ') + text); }
            try {
                srcWin.navigator.clipboard.writeText(text).then(function () { done(true); },
                                                              function () { done(fallbackCopy(text)); });
            } catch (e) { done(fallbackCopy(text)); }
        }
        function openSource() {
            var m = stopEntry(), src = m && m.source;
            if (!S.root || !S.editor) {
                toast('Open in the editor: in the live app run on this computer only');
                return;
            }
            if (!src) { toast('No source recorded for this slide'); return; }
            var abs = S.root.replace(/\/$/, '') + '/' + src.file;
            var url = S.editor.split('{abs}').join(encodeURI(abs)).split('{file}').join(encodeURI(src.file))
                .split('{line}').join(String(src.line));
            var a = srcDoc.createElement('a');
            a.href = url;
            a.style.display = 'none';
            srcDoc.body.appendChild(a);
            a.click();
            srcDoc.body.removeChild(a);
            toast('Opening ' + src.file + ':' + src.line);
        }
        function held(e, k) {
            return !!k && e.ctrlKey === !!k.ctrl && e.altKey === !!k.alt
                && e.metaKey === !!k.meta && e.shiftKey === !!k.shift;
        }
        function onKey(e) {
            var t = e.target || {}, tag = (t.tagName || '').toUpperCase();
            if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || t.isContentEditable) return;
            var act = (held(e, S.copyKey) && e.code === S.copyKey.code) ? copySource
                : (held(e, S.openKey) && e.code === S.openKey.code) ? openSource : null;
            if (!act) return;
            e.preventDefault(); e.stopImmediatePropagation();
            act();
        }
        function onCounter(e) {
            var act = held(e, S.copyClick) ? copySource : held(e, S.openClick) ? openSource : null;
            if (!act) return;            /* a plain click keeps its role */
            e.preventDefault(); e.stopImmediatePropagation();
            act();
        }
        function onFooter(e) {
            var t = e.target && e.target.closest ? e.target.closest('.stx-pf-counter') : null;
            if (!t) return;
            e.preventDefault();
            (held(e, S.openClick) ? openSource : copySource)();
        }
        /* one listener per page: a rerun of the live app replaces the previous run's */
        if (srcWin._stxSrcKey) srcDoc.removeEventListener('keydown', srcWin._stxSrcKey, true);
        if (srcWin._stxSrcFoot) srcDoc.removeEventListener('click', srcWin._stxSrcFoot, true);
        srcWin._stxSrcKey = onKey;
        srcWin._stxSrcFoot = onFooter;
        srcDoc.addEventListener('keydown', onKey, true);
        srcDoc.addEventListener('click', onFooter, true);
        counter.addEventListener('click', onCounter, true);
        if (S.hint) counter.title = (counter.title ? counter.title + ' · ' : '') + S.hint;
        var css = srcDoc.getElementById('stx-src-css');
        if (!css) {
            css = srcDoc.createElement('style');
            css.id = 'stx-src-css';
            css.textContent = '.stx-pf-counter { cursor: copy; }';
            srcDoc.head.appendChild(css);
        }
        var feet = srcDoc.querySelectorAll('.stx-pf-counter');
        for (var i = 0; i < feet.length; i++) feet[i].title = S.footHint;
    })();
"""


def source_script(payload: dict, doc: str, win: str) -> str:
    """The gesture's code for the marker bar script, *doc* / *win* naming the page's document and window."""
    return (f"    var srcDoc = {doc}, srcWin = {win}, S = {json.dumps(payload, ensure_ascii=False)};\n"
            + _SOURCE_JS)
