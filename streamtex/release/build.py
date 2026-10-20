"""What a publication is made of, on this machine: the code snapshot and the checked HTML export.

- ``require_committed``: the release is the commit; a dirty tree is refused.
- ``require_lock`` and ``check_version``: the live image's streamtex (``<dir>/stx-version``,
  ``<dir>/requirements.txt``, written by ``lock_files``) must be the one that exports here, and that one
  must not be a modified working copy — unless ``--allow-skew`` (rel version=a).
- ``snapshot``: ``git archive HEAD`` of the project's and the site's paths, minus the site's excludes.
- ``export``: ``stx export html`` once per language, checked (the page exists, enough words, no keypad
  gate), with redirects, ``version.txt`` and identical media shared between languages.
"""

from __future__ import annotations

import datetime as dt
import filecmp
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from . import ReleaseError
from .config import ReleaseConfig, Site

GATE_MARK = "stx_gate_header"        # the keypad gate's mark in a page: never exported online


def git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if r.returncode:
        raise ReleaseError(f"git {' '.join(args)}: {r.stderr.strip()[-300:]}")
    return r.stdout.strip()


def require_committed(root: Path) -> str:
    """The release name: the short commit of a clean tree."""
    from .state import STATE_FILE
    dirty = "\n".join(line for line in git(root, "status", "--porcelain", "--untracked-files=no").splitlines()
                      if not line.endswith(STATE_FILE))       # written by stx release itself
    if dirty:
        raise ReleaseError("the repository has uncommitted changes — a publication is a commit:\n" + dirty[:800])
    return git(root, "rev-parse", "--short=12", "HEAD")


# -- the live image's dependencies ---------------------------------------------------------

def lock_files(cfg: ReleaseConfig) -> tuple[str, str]:
    """``requirements.txt`` and ``stx-version`` of the live image, as uv.lock gives them today."""
    argv = ["uv", "export", "--no-hashes", "--no-emit-project", "--no-dev", "--frozen",
            "--no-emit-package", "streamtex"]
    for pkg in cfg.lock_exclude:
        argv += ["--no-emit-package", pkg]
    r = subprocess.run(argv, cwd=cfg.root, text=True, capture_output=True)
    if r.returncode:
        raise ReleaseError(f"uv export: {r.stderr[-600:]}")
    req = "".join(line + "\n" for line in r.stdout.splitlines() if line and not line.startswith(("#", " ")))
    return req, installed_version(cfg) + "\n"


def installed_version(cfg: ReleaseConfig) -> str:
    return _project_python(cfg, "import streamtex; print(streamtex.__version__)")


def _project_python(cfg: ReleaseConfig, code: str) -> str:
    r = subprocess.run(["uv", "run", "--project", str(cfg.root), "python", "-c", code],
                       cwd=cfg.root, text=True, capture_output=True)
    if r.returncode:
        raise ReleaseError(f"the project's python: {r.stderr[-400:]}")
    return r.stdout.strip()


def write_lock(cfg: ReleaseConfig) -> tuple[int, str]:
    req, ver = lock_files(cfg)
    cfg.lock_dir.mkdir(parents=True, exist_ok=True)
    (cfg.lock_dir / "requirements.txt").write_text(req, encoding="utf-8")
    (cfg.lock_dir / "stx-version").write_text(ver, encoding="utf-8")
    return len(req.splitlines()), ver.strip()


def require_lock(cfg: ReleaseConfig) -> None:
    req, ver = lock_files(cfg)
    have_req = (cfg.lock_dir / "requirements.txt").read_text(encoding="utf-8") \
        if (cfg.lock_dir / "requirements.txt").exists() else ""
    have_ver = (cfg.lock_dir / "stx-version").read_text(encoding="utf-8") \
        if (cfg.lock_dir / "stx-version").exists() else ""
    if req != have_req or ver != have_ver:
        raise ReleaseError(
            f"the live image's dependencies are no longer uv.lock's (streamtex {ver.strip()} here, "
            f"{have_ver.strip() or '?'} in the image): `stx release lock`, commit, then rebuild the live application")


def library_skew(cfg: ReleaseConfig) -> str:
    """Why the exporting streamtex is not the image's, or ``""`` (rel version=a)."""
    info = json.loads(_project_python(cfg, (
        "import json, importlib.metadata as m, streamtex\n"
        "d = m.distribution('streamtex')\n"
        "u = d.read_text('direct_url.json')\n"
        "print(json.dumps({'version': streamtex.__version__, 'direct_url': json.loads(u) if u else None}))")))
    want = (cfg.lock_dir / "stx-version").read_text(encoding="utf-8").strip() \
        if (cfg.lock_dir / "stx-version").exists() else ""
    if want and info["version"] != want:
        return f"streamtex {info['version']} exports here, the live image runs {want}"
    url = info.get("direct_url") or {}
    if url.get("dir_info", {}).get("editable"):
        path = url.get("url", "").removeprefix("file://")
        from urllib.parse import unquote
        path = unquote(path)
        r = subprocess.run(["git", "-C", path, "status", "--porcelain", "--untracked-files=no"],
                           text=True, capture_output=True)
        if r.returncode == 0 and r.stdout.strip():
            return f"streamtex comes from a working copy with uncommitted changes ({path})"
    return ""


# -- the code snapshot ---------------------------------------------------------------------

def snapshot(cfg: ReleaseConfig, site: Site, work: Path) -> Path:
    code = work / "code"
    code.mkdir()
    paths = [p for p in (*cfg.snapshot, *site.paths) if (cfg.root / p).exists()]
    missing = [p for p in site.paths if not (cfg.root / p).exists()]
    if missing:
        raise ReleaseError(f"{site.site}: path(s) not in the project: {', '.join(missing)}")
    arch = subprocess.run(["git", "-C", str(cfg.root), "archive", "--format=tar", "HEAD", *paths],
                          capture_output=True)
    if arch.returncode:
        raise ReleaseError(f"{site.site}: git archive: {arch.stderr.decode()[-400:]}")
    subprocess.run(["tar", "-x", "-C", str(code)], input=arch.stdout, check=True)
    for ex in site.exclude:
        target = code / ex
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    if not (code / site.book).is_file():
        raise ReleaseError(f"{site.site}: {site.book} is not in the commit")
    return code


# -- the HTML export -----------------------------------------------------------------------

def redirect(to: str) -> str:
    return (f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={to}">'
            f'<link rel="canonical" href="{to}"><a href="{to}">{to}</a>\n')


def export(cfg: ReleaseConfig, site: Site, code: Path, work: Path, release: str,
           html_env: dict[str, str] | None = None) -> Path:
    """The HTML face: one checked export per language, from the snapshot, with this machine's media."""
    html = work / "html"
    doc = code / site.doc_dir
    name = site.export_name
    linked_media = None
    if cfg.media:
        media = code / cfg.media
        if media.is_dir() and not media.is_symlink():
            shutil.rmtree(media)
        media.parent.mkdir(parents=True, exist_ok=True)
        media.symlink_to(cfg.root / cfg.media)       # the media of this machine (the commit is clean)
        linked_media = media
    env = {k: v for k, v in os.environ.items()
           if k not in ("STX_PASSWORD", "STX_GATE") and not k.startswith(("STX_URL_", "STX_EXPORT_URL_"))}
    for lang in cfg.langs:
        out = html / lang
        r = subprocess.run(["uv", "run", "--project", str(cfg.root), "stx", "export", "html", "--output",
                            str(out), "."], cwd=doc, text=True, capture_output=True,
                           env={**env, "STX_LANG": lang, **(html_env or {})})
        page = out / name / f"{name}.html"
        if r.returncode or not page.exists():
            raise ReleaseError(f"{site.site}: the {lang} export failed (code {r.returncode}):\n"
                               f"{(r.stderr or r.stdout)[-1500:]}")
        files = [page] + sorted((page.parent / "pages").glob("*.html"))
        text = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files)
        words = len(re.sub(r"<[^>]+>", " ", text).split())
        if GATE_MARK in text:
            raise ReleaseError(f"{site.site}: the {lang} export holds the keypad gate")
        if words < cfg.min_words:
            raise ReleaseError(f"{site.site}: the {lang} export has {words} words only (< {cfg.min_words})")
        (out / "index.html").write_text(redirect(f"/html/{lang}/{name}/{name}.html"), encoding="utf-8")
    first = cfg.langs[0]
    (html / "index.html").write_text(redirect(f"/html/{first}/{name}/{name}.html"), encoding="utf-8")
    (html / "version.txt").write_text(f"{release}\n{site.site}\n{dt.datetime.now().isoformat(timespec='seconds')}\n",
                                      encoding="utf-8")
    if linked_media is not None:
        linked_media.unlink()
    share_media(html, cfg.langs)
    return html


def share_media(html: Path, langs: tuple[str, ...]) -> int:
    """Each language exports its own copy of the media: a file identical from one language to the next
    becomes a hard link, which ``rsync -H`` carries as such."""
    first: dict[str, Path] = {}
    linked = 0
    for lang in langs:
        for f in sorted((html / lang).rglob("*")):
            if not f.is_file() or "/data/" not in f.as_posix():
                continue
            key = f.relative_to(html / lang).as_posix()
            if key not in first:
                first[key] = f
            elif filecmp.cmp(first[key], f, shallow=False):
                f.unlink()
                os.link(first[key], f)
                linked += 1
    return linked
