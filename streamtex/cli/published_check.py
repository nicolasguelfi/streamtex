"""Editable in development, PyPI in production — check what production gets (#87).

Two measured failures behind this module (ai4se6d):

- ``.stx-version`` edited by hand to ``0.3.3`` while ``pyproject`` required
  ``>=0.6.10`` and the lock held ``0.6.10``; the next commits removed then
  restored parameters on the faith of that number;
- blocks written against the editable library used parameters the published
  wheel did not have yet: fine locally, broken in production.

:func:`version_problems` cross-checks ``.stx-version``, the ``streamtex``
requirement of ``pyproject.toml`` and the version locked in ``uv.lock``.
:func:`published_python` builds an isolated environment where streamtex
loses its local source (local packs keep theirs, as in the Docker image), so
that ``stx validate --build --published`` runs every block against the
published wheel.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VersionProblem:
    severity: str   # "error" | "warning"
    message: str


def _vtuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def locked_streamtex(project_dir: Path) -> tuple[str | None, str | None]:
    """``(version, source)`` of streamtex in ``uv.lock`` (source = 'registry' or the local path)."""
    lock = project_dir / "uv.lock"
    if not lock.is_file():
        return None, None
    try:
        data = tomllib.loads(lock.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None, None
    for pkg in data.get("package", []):
        if pkg.get("name") == "streamtex":
            src = pkg.get("source", {})
            if "registry" in src:
                return pkg.get("version"), "registry"
            return pkg.get("version"), src.get("editable") or src.get("path") or src.get("git") or "?"
    return None, None


def _minimum_from_pyproject(project_dir: Path) -> str | None:
    p = project_dir / "pyproject.toml"
    if not p.is_file():
        return None
    try:
        deps = tomllib.loads(p.read_text(encoding="utf-8")).get("project", {}).get("dependencies", [])
    except (OSError, tomllib.TOMLDecodeError):
        return None
    for d in deps:
        m = re.match(r"\s*streamtex(\[[^\]]*\])?\s*(.*)", d)
        if m:
            low = re.search(r">=\s*([\d.]+)", m.group(2))
            return low.group(1) if low else None
    return None


def version_problems(project_dir: Path) -> list[VersionProblem]:
    """Inconsistencies between ``.stx-version``, ``pyproject.toml`` and ``uv.lock``."""
    out: list[VersionProblem] = []
    locked, source = locked_streamtex(project_dir)
    minimum = _minimum_from_pyproject(project_dir)
    stx_version_file = project_dir / ".stx-version"
    required = None
    if stx_version_file.is_file():
        required = stx_version_file.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"\d+(\.\d+){0,2}", required):
            out.append(VersionProblem("error", f".stx-version is not a version: {required!r}"))
            required = None
    if required and locked and _vtuple(required) > _vtuple(locked):
        out.append(VersionProblem(
            "error", f".stx-version requires {required} but uv.lock holds streamtex {locked}: "
                     "the Docker build guard will fail"))
    if required and minimum and _vtuple(required) < _vtuple(minimum):
        out.append(VersionProblem(
            "warning", f".stx-version ({required}) is below the pyproject minimum (>={minimum}) — "
                       "the build guard checks less than the project needs; align it on the lock"))
    if source and source != "registry":
        out.append(VersionProblem(
            "warning", f"uv.lock takes streamtex from a local source ({source}); production "
                       "(uv sync --no-sources) installs the published wheel — check the blocks against it "
                       "with `stx validate --build --published`"))
    return out


def published_python(project_dir: Path, *, cache_root: Path | None = None,
                     extras: bool = True) -> tuple[str | None, str]:
    """An isolated interpreter with the project's dependencies resolved WITHOUT local sources.

    Returns ``(python_path, log)``; ``python_path`` is ``None`` when the
    resolution fails — which is itself the answer: production would fail too.
    """
    cache_root = cache_root or Path.home() / ".cache" / "streamtex" / "published"
    key = hashlib.sha256(str(project_dir.resolve()).encode()).hexdigest()[:12]
    env_dir = cache_root / key
    req = env_dir / "requirements.txt"
    env_dir.mkdir(parents=True, exist_ok=True)
    log = []

    def _run(cmd: list[str]) -> subprocess.CompletedProcess:
        log.append("$ " + " ".join(cmd))
        r = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, timeout=900)
        log.append((r.stdout + r.stderr).strip()[-2000:])
        return r

    # Only streamtex loses its local source: local packs keep theirs, as in
    # the Docker image (uv sync --no-sources, then the local packs installed).
    compile_cmd = ["uv", "pip", "compile", "pyproject.toml", "--no-sources-package", "streamtex",
                   "-q", "-o", str(req)]
    if extras:
        compile_cmd.insert(4, "--all-extras")
    if _run(compile_cmd).returncode != 0:
        return None, "\n".join(log)
    venv = env_dir / "venv"
    if not (venv / "bin" / "python").exists() and _run(["uv", "venv", "-q", str(venv)]).returncode != 0:
        return None, "\n".join(log)
    if _run(["uv", "pip", "install", "-q", "--python", str(venv / "bin" / "python"),
             "-r", str(req)]).returncode != 0:
        return None, "\n".join(log)
    return str(venv / "bin" / "python"), "\n".join(log)


def installed_streamtex(python: str) -> str:
    r = subprocess.run([python, "-c", "import importlib.metadata as m; print(m.version('streamtex'))"],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip() or "?"
