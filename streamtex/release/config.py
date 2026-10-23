"""The ``[release]`` table of stx.toml and the list of published sites.

::

    [release]
    project = "trainings"          # the media folder on the server and the Coolify project name
    langs = ["en", "fr"]           # one HTML export per language (STX_LANG); default ["en"];
                                   # [] = one export, no STX_LANG, no language folder in /html/
    snapshot = ["content", "shared", "trainings_pack"]   # in every code snapshot, besides the site's paths
    media = "assets"               # copied once per project, linked into every snapshot (optional)
    media_exclude = [".DS_Store", "*-original.*"]
    pythonpath = ["trainings_pack"]  # PYTHONPATH of the live process, relative to the snapshot
    lock_exclude = ["trainings-pack"]  # local packages kept out of the live image's requirements
    lock_no_sources = false        # true: requirements resolved without [tool.uv.sources] (git packs)
    apt = ["texlive-latex-base"]   # system packages added to the live image
    sites_from = "shared.release:sites"   # a function of the project returning the sites, or:

    [[release.sites]]
    site = "chat1d-slides"         # the first word of its address — written, never invented
    book = "trainings/CHAT1D/slides/book.py"
    group = "CHAT1D"               # its password group (default: the site)
    faces = ["live", "html"]       # default: both
    paths = ["trainings/CHAT1D"]   # its part of the code snapshot (default: the book's folder)
    exclude = ["trainings/CHAT1D/pack"]   # removed from the snapshot
    explicit = false               # true: published only when named (a home page)
    zoom = 80                      # the HTML face opens as at this browser zoom, in percent (optional)
"""

from __future__ import annotations

import importlib
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from . import ReleaseError

FACES = ("live", "html")
SITE_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
_SITE_KEYS = {"site", "book", "group", "faces", "paths", "exclude", "explicit", "legacy", "zoom"}
_RELEASE_KEYS = {"project", "langs", "snapshot", "media", "media_exclude", "pythonpath", "lock_exclude",
                 "lock_no_sources", "apt", "min_words", "port_base", "dir", "sites", "sites_from", "checks"}
_APT_RE = re.compile(r"^[a-z0-9][a-z0-9.+-]+$")


@dataclass(frozen=True)
class Site:
    """One published document."""

    site: str
    book: str
    group: str
    faces: tuple[str, ...] = FACES
    paths: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    explicit: bool = False
    legacy: tuple[str, ...] = ()          # the prototype's (training, kind), for convert-passwords
    zoom: float | None = None             # the HTML face's zoom in percent (stx export html --zoom)

    @property
    def doc_dir(self) -> str:
        """The document's folder, relative to the project root."""
        return str(Path(self.book).parent)

    @property
    def export_name(self) -> str:
        """The base name ``stx export html`` gives the document (its folder's name)."""
        return Path(self.doc_dir).name.replace("stx_manual_", "")


@dataclass
class ReleaseConfig:
    root: Path
    project: str
    sites: list[Site]
    langs: tuple[str, ...] = ("en",)
    snapshot: tuple[str, ...] = ()
    media: str | None = None
    media_exclude: tuple[str, ...] = (".DS_Store",)
    pythonpath: tuple[str, ...] = ()
    lock_exclude: tuple[str, ...] = ()
    lock_no_sources: bool = False
    apt: tuple[str, ...] = ()
    min_words: int = 100
    port_base: int = 9000
    dir: str = ".stx-release"
    checks: str | None = None
    by_name: dict[str, Site] = field(default_factory=dict)

    def __post_init__(self):
        self.by_name = {s.site: s for s in self.sites}

    def site(self, name: str) -> Site:
        if name not in self.by_name:
            raise ReleaseError(f"unknown site '{name}' — sites: {', '.join(sorted(self.by_name)) or 'none'}")
        return self.by_name[name]

    def select(self, names: tuple[str, ...], groups: tuple[str, ...] = ()) -> list[Site]:
        """The sites named, or of the groups named; with neither, every site not marked explicit."""
        if not names and not groups:
            return [s for s in self.sites if not s.explicit]
        chosen = [self.site(n) for n in names]
        for g in groups:
            members = [s for s in self.sites if s.group == g and not s.explicit]
            if not members:
                raise ReleaseError(f"no site in group '{g}'")
            chosen += [s for s in members if s not in chosen]
        return chosen

    @property
    def lock_dir(self) -> Path:
        return self.root / self.dir


def find_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for d in (cur, *cur.parents):
        if (d / "stx.toml").is_file():
            return d
    raise ReleaseError("no stx.toml here or above — stx release reads its [release] table")


def _call(spec: str, root: Path, what: str):
    if ":" not in spec:
        raise ReleaseError(f"[release] {what} = '{spec}' — expected 'module:function'")
    mod, func = spec.split(":", 1)
    sys.path.insert(0, str(root))
    try:
        return getattr(importlib.import_module(mod), func)
    except (ImportError, AttributeError) as e:
        raise ReleaseError(f"[release] {what} = '{spec}': {e}") from None
    finally:
        sys.path.remove(str(root))


def _site(raw: object, where: str) -> Site:
    if not isinstance(raw, dict):
        raise ReleaseError(f"{where}: a site is a table")
    unknown = set(raw) - _SITE_KEYS
    if unknown:
        raise ReleaseError(f"{where}: unknown key(s) {sorted(unknown)} — {', '.join(sorted(_SITE_KEYS))}")
    name, book = raw.get("site"), raw.get("book")
    if not isinstance(name, str) or not SITE_RE.match(name):
        raise ReleaseError(f"{where}: site {name!r} — a DNS label: a-z, 0-9 and '-', at most 63 characters")
    if not isinstance(book, str) or not book.endswith(".py"):
        raise ReleaseError(f"{where} ({name}): book must be the path of its book.py")
    faces = tuple(raw.get("faces", FACES))
    if not faces or any(f not in FACES for f in faces) or len(set(faces)) != len(faces):
        raise ReleaseError(f"{where} ({name}): faces {list(faces)} — 'live' and/or 'html'")
    legacy = tuple(raw.get("legacy", ()))
    if legacy and (len(legacy) != 2 or not all(isinstance(x, str) for x in legacy)):
        raise ReleaseError(f"{where} ({name}): legacy must be [group, kind]")
    paths = tuple(raw.get("paths") or (str(Path(book).parent),))
    zoom = raw.get("zoom")
    if zoom is not None and (isinstance(zoom, bool) or not isinstance(zoom, (int, float)) or zoom <= 0):
        raise ReleaseError(f"{where} ({name}): zoom {zoom!r} — a positive percentage, such as 80")
    return Site(site=name, book=book, group=str(raw.get("group") or name), faces=faces, paths=paths,
                exclude=tuple(raw.get("exclude", ())), explicit=bool(raw.get("explicit", False)), legacy=legacy,
                zoom=float(zoom) if zoom is not None else None)


def load_config(root: Path | None = None) -> ReleaseConfig:
    root = root or find_root()
    data = tomllib.loads((root / "stx.toml").read_text(encoding="utf-8")).get("release")
    if not isinstance(data, dict):
        raise ReleaseError(f"{root / 'stx.toml'} has no [release] table")
    unknown = set(data) - _RELEASE_KEYS
    if unknown:
        raise ReleaseError(f"[release]: unknown key(s) {sorted(unknown)} — {', '.join(sorted(_RELEASE_KEYS))}")
    project = data.get("project")
    if not isinstance(project, str) or not SITE_RE.match(project):
        raise ReleaseError("[release] project = '…' is required (a-z, 0-9, '-')")
    if "sites_from" in data:
        raw_sites = _call(data["sites_from"], root, "sites_from")()
        where = f"[release] sites_from ({data['sites_from']})"
    else:
        raw_sites = data.get("sites", [])
        where = "[[release.sites]]"
    sites = [_site(r, f"{where} #{i}") for i, r in enumerate(raw_sites)]
    if not sites:
        raise ReleaseError(f"{where}: no site")
    seen: dict[str, int] = {}
    for s in sites:
        seen[s.site] = seen.get(s.site, 0) + 1
    twice = sorted(n for n, k in seen.items() if k > 1)
    if twice:
        raise ReleaseError(f"{where}: site name(s) used twice: {', '.join(twice)}")
    langs = tuple(data.get("langs", ("en",)))
    if not all(isinstance(x, str) and re.fullmatch(r"[a-z]{2,3}", x) for x in langs):
        raise ReleaseError("[release] langs: language codes such as ['en', 'fr'], or [] for one export")
    apt = tuple(data.get("apt", ()))
    bad = [p for p in apt if not isinstance(p, str) or not _APT_RE.match(p)]
    if bad:
        raise ReleaseError(f"[release] apt: not a package name: {bad}")
    return ReleaseConfig(
        root=root, project=project, sites=sites, langs=langs,
        snapshot=tuple(data.get("snapshot", ())), media=data.get("media"),
        media_exclude=tuple(data.get("media_exclude", (".DS_Store",))),
        pythonpath=tuple(data.get("pythonpath", ())), lock_exclude=tuple(data.get("lock_exclude", ())),
        lock_no_sources=bool(data.get("lock_no_sources", False)), apt=apt,
        min_words=int(data.get("min_words", 100)), port_base=int(data.get("port_base", 9000)),
        dir=str(data.get("dir", ".stx-release")), checks=data.get("checks"))


def run_checks(cfg: ReleaseConfig, sites: list[Site]) -> None:
    """The project's own checks before publishing (``[release] checks = 'module:function'``)."""
    if cfg.checks:
        _call(cfg.checks, cfg.root, "checks")(sites)
