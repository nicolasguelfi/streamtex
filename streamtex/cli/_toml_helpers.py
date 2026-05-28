"""Shared helpers to mutate pyproject.toml's [tool.uv.sources] non-destructively.

The pre-existing regex-based logic in `dev_cmd._add_uv_source` rewrites the
whole section and assumes a single key. The new pack architecture supports
multiple editable packs side by side; this module replaces that approach
with a tomlkit-based round-trip that preserves comments and other keys.

See PLAN.md §29.4 step 0 and decision D17.
"""

from __future__ import annotations

import re
from pathlib import Path

import tomlkit
from tomlkit import inline_table


def _load_pyproject(project_dir: Path) -> tomlkit.TOMLDocument:
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.is_file():
        raise FileNotFoundError(f"No pyproject.toml in {project_dir}")
    return tomlkit.parse(pyproject.read_text(encoding="utf-8"))


def _save_pyproject(project_dir: Path, doc: tomlkit.TOMLDocument) -> None:
    (project_dir / "pyproject.toml").write_text(tomlkit.dumps(doc), encoding="utf-8")


def _ensure_section(doc: tomlkit.TOMLDocument, path: tuple[str, ...]) -> tomlkit.items.Table:
    current: tomlkit.items.Table | tomlkit.TOMLDocument = doc
    for key in path:
        if key not in current:
            current[key] = tomlkit.table()
        current = current[key]  # type: ignore[assignment]
    return current  # type: ignore[return-value]


def _canonical_dist_name(name: str) -> str:
    return name.lower().replace("_", "-")


def _ensure_dependency(doc: tomlkit.TOMLDocument, name: str) -> None:
    """Ensure `name` is listed in `[project].dependencies`.

    `[tool.uv.sources]` is only honored by uv when the package is also a real
    dependency. Without this step, packs declared in stx.toml end up written
    to uv.sources but `uv sync` never installs them — surfaces as PR002 at
    discovery time.
    """
    project = doc.get("project")
    if project is None:
        project = tomlkit.table()
        doc["project"] = project
    # Don't add the project itself as a self-dependency.
    project_name = project.get("name")
    if project_name and _canonical_dist_name(str(project_name)) == _canonical_dist_name(name):
        return
    deps = project.get("dependencies")
    if deps is None:
        deps = tomlkit.array()
        project["dependencies"] = deps
    target = _canonical_dist_name(name)
    for existing in deps:
        head = re.split(r"[<>=!~\[\s;]", str(existing).strip(), maxsplit=1)[0]
        if _canonical_dist_name(head) == target:
            return
    deps.append(name)


def _remove_dependency(doc: tomlkit.TOMLDocument, name: str) -> None:
    project = doc.get("project")
    if project is None:
        return
    deps = project.get("dependencies")
    if deps is None:
        return
    target = _canonical_dist_name(name)
    kept = tomlkit.array()
    changed = False
    for existing in deps:
        head = re.split(r"[<>=!~\[\s;]", str(existing).strip(), maxsplit=1)[0]
        if _canonical_dist_name(head) == target:
            changed = True
            continue
        kept.append(existing)
    if changed:
        project["dependencies"] = kept


def set_uv_source(project_dir: Path, name: str, path: str, *, editable: bool = True) -> None:
    """Add or update a `[tool.uv.sources].<name>` entry without touching others.

    `editable=True` produces ``{ path = "<path>", editable = true }`` ; with
    ``editable=False`` only the path is set, which lets users pin a wheel-only
    dependency. The package name is also added to ``[project].dependencies``
    so ``uv sync`` actually installs the pack.
    """
    doc = _load_pyproject(project_dir)
    section = _ensure_section(doc, ("tool", "uv", "sources"))
    entry = inline_table()
    entry["path"] = path
    if editable:
        entry["editable"] = True
    section[name] = entry
    _ensure_dependency(doc, name)
    _save_pyproject(project_dir, doc)


def set_uv_source_git(
    project_dir: Path,
    name: str,
    url: str,
    *,
    rev: str | None = None,
    subdirectory: str | None = None,
) -> None:
    """Add or update a `[tool.uv.sources].<name>` git entry.

    Produces ``{ git = "<url>", rev = "...", subdirectory = "..." }`` and adds
    the package to ``[project].dependencies`` so ``uv sync`` resolves and
    installs it from the git source.
    """
    doc = _load_pyproject(project_dir)
    section = _ensure_section(doc, ("tool", "uv", "sources"))
    entry = inline_table()
    entry["git"] = url
    if rev:
        entry["rev"] = rev
    if subdirectory:
        entry["subdirectory"] = subdirectory
    section[name] = entry
    _ensure_dependency(doc, name)
    _save_pyproject(project_dir, doc)


def ensure_pypi_dependency(project_dir: Path, spec: str) -> None:
    """Ensure a PyPI dependency spec (e.g. ``foo>=1.0``) is in pyproject.

    Used by ``stx pack sync`` for ``type="pypi"`` packs so that ``uv sync``
    resolves them from the index instead of relying on a one-off pip call.
    """
    doc = _load_pyproject(project_dir)
    dist = re.split(r"[<>=!~\[\s;]", spec.strip(), maxsplit=1)[0]
    _ensure_dependency(doc, dist)
    # If the user passed a constraint, prefer the constrained form.
    if dist != spec.strip():
        project = doc.get("project")
        deps = project.get("dependencies") if project is not None else None
        if deps is not None:
            target = _canonical_dist_name(dist)
            for i, existing in enumerate(deps):
                head = re.split(r"[<>=!~\[\s;]", str(existing).strip(), maxsplit=1)[0]
                if _canonical_dist_name(head) == target:
                    deps[i] = spec
                    break
    _save_pyproject(project_dir, doc)


def remove_uv_source(project_dir: Path, name: str) -> bool:
    """Remove `[tool.uv.sources].<name>`. Returns True if the entry existed.

    If the section becomes empty after removal, the section header is dropped
    too (parent [tool.uv] is preserved). The matching entry in
    ``[project].dependencies`` is also removed.
    """
    doc = _load_pyproject(project_dir)
    tool = doc.get("tool")
    if tool is None:
        return False
    uv = tool.get("uv")
    if uv is None:
        return False
    sources = uv.get("sources")
    if sources is None or name not in sources:
        return False
    del sources[name]
    if len(sources) == 0:
        del uv["sources"]
    _remove_dependency(doc, name)
    _save_pyproject(project_dir, doc)
    return True


def get_uv_sources(project_dir: Path) -> dict[str, dict]:
    """Return the current `[tool.uv.sources]` as a plain dict (read-only view)."""
    try:
        doc = _load_pyproject(project_dir)
    except FileNotFoundError:
        return {}
    tool = doc.get("tool")
    if tool is None:
        return {}
    uv = tool.get("uv")
    if uv is None:
        return {}
    sources = uv.get("sources")
    if sources is None:
        return {}
    return {k: dict(v) for k, v in sources.items()}


__all__ = [
    "set_uv_source",
    "set_uv_source_git",
    "ensure_pypi_dependency",
    "remove_uv_source",
    "get_uv_sources",
]
