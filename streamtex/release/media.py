"""Media per site (#142): the live face serves only the files its site shows.

The router serves ``/app/static/`` from ``live/sites/<site>/static``, a link to the site's
``<doc>/static`` folder — in a project whose documents share one media folder, every file of every
document. With ``[release] media_per_site = true``, each release of the code holds a folder
``.stx-served`` of links to the files the site uses, and the router serves that folder instead:

* the files its HTML export shows: each file of the export's ``data/`` folders, found again in the
  static folder by its content (size, then SHA-256) — the export copies a served file unchanged;
* the files its HTML export links to under ``app/static/`` — a download offered by a link, at the
  site's address or another's (``href='https://<site>…/app/static/downloads/x.zip'``): the export
  leaves such a link as it is, and the live face must serve its file;
* the files ``media_keep`` names (``[release]`` and the site's table): glob patterns relative to the
  static folder, as in ``/app/static/<path>``; ``*`` also crosses ``/``.

A link to another site's file (``https://<other site>…/app/static/x.zip``) is served by that site, and
only while that site keeps the file: ``foreign`` lists such links, publish records them and checks,
after each publication, that the other site still serves each file (#155).

The code itself is unchanged: a block that reads a file of the static folder still finds it. A site
without an HTML face keeps serving its whole static folder. ``stx release media-report SITE`` shows
the plan without changing anything.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from pathlib import Path
from urllib.parse import unquote

from .config import ReleaseConfig, Site

SERVED = ".stx-served"

#: A path under the static folder named in a site's own files: ``static/…`` or ``app/static/…``.
_NAMED_RE = re.compile(r"""(?:app/)?static/([\w.~/-]+)""")
#: A link of the export to a served file, absolute or not: the path after ``app/static/``.
_LINKED_RE = re.compile(r"""app/static/([^"'\s()<>?#\\]+)""")
#: The same link with its address: the host, whose first label names the site that serves it.
_HOSTED_RE = re.compile(r"""https?://([A-Za-z0-9.-]+)(?::\d+)?/app/static/([^"'\s()<>?#\\]+)""")
_TEXT = {".py", ".md", ".html", ".css", ".js", ".toml", ".json", ".txt", ".yaml", ".yml"}


@dataclass
class MediaPlan:
    """What the live face of one site serves."""

    static: Path | None                       # the site's static folder, resolved (None: it has none)
    files: dict[str, int] = field(default_factory=dict)       # every file of it → its size
    kept: dict[str, str] = field(default_factory=dict)        # served → why: "export", "export link",
                                                              # or the media_keep pattern
    unmatched: int = 0                        # export files found in no static file (inlined, generated)
    named: list[str] = field(default_factory=list)            # named in the site's files, not kept
    foreign: dict[str, list[str]] = field(default_factory=dict)  # another site of the project → the
                                                              # files the export links to on it (#155)

    @property
    def dropped(self) -> list[str]:
        return sorted(set(self.files) - set(self.kept))

    def size(self, paths) -> int:
        return sum(self.files[p] for p in paths)


def _walk(root: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    for d, dirs, names in os.walk(root, followlinks=True):
        dirs[:] = [x for x in dirs if x != SERVED]
        for n in names:
            p = Path(d) / n
            try:
                out[p.relative_to(root).as_posix()] = p.stat().st_size
            except OSError:                    # a broken link: nothing to serve
                pass
    return out


def _digest(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def keep_patterns(cfg: ReleaseConfig, site: Site) -> tuple[str, ...]:
    return (*cfg.media_keep, *site.media_keep)


def _rel(match: str) -> str:
    return unquote(match.replace("&amp;", "&")).rstrip("/")


def site_of_host(cfg: ReleaseConfig, host: str, suffix: str = "") -> str:
    """The project's site an address names (its first label, without a provisional *suffix*), or ``""``."""
    label = host.split(".", 1)[0].lower()
    for name in (label, label.removesuffix(suffix) if suffix else label):
        if name in cfg.by_name:
            return name
    return ""


def plan(cfg: ReleaseConfig, site: Site, code: Path, html: Path, suffix: str = "") -> MediaPlan:
    """The files the live face of *site* serves, from its snapshot *code* and its HTML export *html*,
    both on this machine; the snapshot's media folder is linked to the project's while it is read."""
    linked = None
    if cfg.media and not (code / cfg.media).exists() and (cfg.root / cfg.media).is_dir():
        linked = code / cfg.media
        if linked.is_symlink():               # a link left dangling
            linked.unlink()
        linked.parent.mkdir(parents=True, exist_ok=True)
        linked.symlink_to(cfg.root / cfg.media)
    try:
        return _plan(cfg, site, code, html, suffix)
    finally:
        if linked is not None:
            linked.unlink()


def _plan(cfg: ReleaseConfig, site: Site, code: Path, html: Path, suffix: str) -> MediaPlan:
    folder = code / site.doc_dir / "static"
    if not folder.is_dir():
        return MediaPlan(static=None)
    mp = MediaPlan(static=folder.resolve(), files=_walk(folder))
    by_size: dict[int, list[str]] = defaultdict(list)
    for rel, size in mp.files.items():
        by_size[size].append(rel)
    digests: dict[str, str] = {}
    for f in sorted(html.rglob("*")):
        if not f.is_file() or "data" not in f.relative_to(html).parts[:-1]:
            continue
        same = by_size.get(f.stat().st_size, [])
        found = False
        if same:
            want = _digest(f)
            for rel in same:
                if rel not in digests:
                    digests[rel] = _digest(folder / rel)
                if digests[rel] == want:
                    mp.kept.setdefault(rel, "export")
                    found = True
        mp.unmatched += not found
    foreign: dict[str, set[str]] = defaultdict(set)
    for f in sorted(html.rglob("*")):
        if f.is_file() and f.suffix in (".html", ".css", ".js"):
            text = f.read_text(encoding="utf-8", errors="replace")
            for m in _LINKED_RE.findall(text):
                rel = _rel(m)
                if rel in mp.files:
                    mp.kept.setdefault(rel, "export link")
            for host, m in _HOSTED_RE.findall(text):
                other = site_of_host(cfg, host, suffix)
                if other and other != site.site:
                    foreign[other].add(_rel(m))
    mp.foreign = {k: sorted(v) for k, v in sorted(foreign.items())}
    for pat in keep_patterns(cfg, site):
        for rel in mp.files:
            if fnmatchcase(rel, pat):
                mp.kept.setdefault(rel, pat)
    named = set()
    for d, dirs, names in os.walk(code / site.doc_dir):
        dirs[:] = [x for x in dirs if x not in ("static", SERVED, "__pycache__")]
        for n in names:
            if Path(n).suffix in _TEXT:
                text = (Path(d) / n).read_text(encoding="utf-8", errors="replace")
                named.update(m.rstrip("/.") for m in _NAMED_RE.findall(text))
    mp.named = sorted(p for p in named if p in mp.files and p not in mp.kept)
    return mp


def build_served(code: Path, site: Site, kept) -> Path:
    """The folder ``.stx-served`` of the snapshot: one relative link per kept file, to the same file
    under ``<doc>/static`` — the links resolve on the server as they do here."""
    served = code / SERVED
    static = code / site.doc_dir / "static"
    for rel in sorted(kept):
        link = served / rel
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(os.path.relpath(static / rel, link.parent))
    served.mkdir(exist_ok=True)               # no file kept: the folder exists, empty — nothing served
    return served


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"
