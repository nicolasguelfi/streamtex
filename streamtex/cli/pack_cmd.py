"""stx pack — add / remove / list / sync / validate packs in a project.

Surface and semantics: PLAN.md §6.2 + §29.4.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import click

from . import _stx_toml
from ._shared import _find_project_dir
from ._toml_helpers import (
    ensure_pypi_dependency,
    get_uv_sources,
    remove_uv_source,
    set_uv_source,
    set_uv_source_git,
)
from .console import get_console

# git:[<scheme>://]<host>/<owner>/<repo>[.git][@<rev>][#subdirectory=<dir>]
# - scheme (http/https) is tolerated but stripped — the canonical form stored
#   in stx.toml is ``host/owner/repo`` (without scheme, without .git).
# - the ``#subdirectory=`` fragment lets the user point at a sub-package inside
#   a monorepo (e.g. ``streamtex-packs/streamtex-pack-design``).
REF_GIT_RE = re.compile(
    r"^git:"
    r"(?:https?://)?"
    r"(?P<url>[^@#\s]+?)"
    r"(?:\.git)?"
    r"(?:@(?P<rev>[^#\s]+))?"
    r"(?:\#subdirectory=(?P<subdir>\S+))?"
    r"$"
)
REF_LOCAL_RE = re.compile(r"^local:(?P<path>.+)$")
REF_PYPI_RE = re.compile(r"^pypi:(?P<name>[A-Za-z0-9_\-]+)(?:@(?P<constraint>.+))?$")


def _parse_ref(ref: str) -> dict[str, Any]:
    m = REF_GIT_RE.match(ref)
    if m:
        url = m.group("url")
        rev = m.group("rev")
        subdir = m.group("subdir")
        entry: dict[str, Any] = {"type": "git", "ref": url}
        if rev:
            entry["rev"] = rev
        if subdir:
            entry["subdirectory"] = subdir
            # Sub-package basename is the meaningful pack identity in a monorepo.
            entry["name"] = subdir.rstrip("/").split("/")[-1]
        else:
            entry["name"] = url.rstrip("/").split("/")[-1]
        return entry
    m = REF_LOCAL_RE.match(ref)
    if m:
        path = m.group("path")
        return {"type": "local", "name": Path(path).name, "path": path, "primary": False}
    m = REF_PYPI_RE.match(ref)
    if m:
        entry = {"type": "pypi", "name": m.group("name")}
        if m.group("constraint"):
            entry["constraint"] = m.group("constraint")
        return entry
    raise click.ClickException(
        f"Unsupported pack reference: {ref!r}. "
        "Use git:<url>[@rev][#subdirectory=<dir>], local:<path>, "
        "or pypi:<name>[@constraint]."
    )


def _read_pack_manifest_name(pack_root: Path) -> str | None:
    """Try to read pack.name from a local pack's _pack_manifest.toml."""
    import tomllib

    # The manifest may sit at the top of the pack root, or inside the inner
    # package directory (e.g. mypack/mypack/_pack_manifest.toml).
    candidates = [pack_root / "_pack_manifest.toml"]
    for sub in pack_root.iterdir():
        if sub.is_dir():
            candidates.append(sub / "_pack_manifest.toml")
    for c in candidates:
        if c.is_file():
            try:
                with c.open("rb") as fh:
                    data = tomllib.load(fh)
                pack = data.get("pack") or {}
                if pack.get("name"):
                    return pack["name"]
            except Exception:
                continue
    return None


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------


@click.group()
def pack():
    """Manage packs declared in stx.toml."""


@pack.command("add")
@click.argument("ref")
@click.option("--dev", is_flag=True, help="Editable install (auteur de pack, Q17).")
def add_cmd(ref: str, dev: bool) -> None:
    """Add a pack to the current project's stx.toml.

    REF can be:

      * `git:<url>[@rev][#subdirectory=<dir>]` — Git repository (the
        ``#subdirectory=`` fragment is required for monorepos like
        ``streamtex-packs/streamtex-pack-design``)
      * `local:<path>`      — local path (use `--dev` for editable)
      * `pypi:<name>[@spec]` — PyPI release
      * a plain path        — same as `local:<path>` when --dev is passed
    """
    console = get_console()
    project_dir = _find_project_dir()

    if dev:
        # `stx pack add --dev <path-or-url>` per Q17.
        # For v1 we only support local paths; URL cloning is documented and
        # explicitly delegated to plain `git clone`.
        path_str = ref.removeprefix("local:")
        pack_root = (project_dir / path_str).resolve() if not Path(path_str).is_absolute() else Path(path_str)
        if not pack_root.is_dir():
            raise click.ClickException(f"--dev path does not exist: {pack_root}")

        # Validate manifest
        from streamtex.core import validation

        issues = validation.validate_pack(pack_root)
        errors = [i for i in issues if i.is_error()]
        if errors:
            console.print(f"[red]Pack at {pack_root} failed validation:[/red]")
            for issue in errors:
                console.print(f"  [{issue.code}] {issue.message}")
            raise click.ClickException("Pack validation failed; see above.")

        pack_name = _read_pack_manifest_name(pack_root) or pack_root.name
        try:
            set_uv_source(project_dir, pack_name, str(pack_root), editable=True)
        except FileNotFoundError as exc:
            raise click.ClickException(str(exc)) from exc
        try:
            _stx_toml.add_pack(
                project_dir,
                {
                    "type": "local",
                    "name": pack_name,
                    "path": str(pack_root),
                    "editable": True,
                    "primary": False,
                },
            )
        except ValueError as exc:
            console.print(f"[yellow]stx.toml: {exc}[/yellow]")
        console.print(
            f"[green]Pack '{pack_name}' linked in editable mode. "
            f"Changes reflect immediately on next `stx run`.[/green]"
        )
        return

    entry = _parse_ref(ref)
    try:
        _stx_toml.add_pack(project_dir, entry)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if entry["type"] == "local":
        set_uv_source(
            project_dir,
            entry["name"],
            entry["path"],
            editable=entry.get("editable", False),
        )

    console.print(f"[green]Pack '{entry.get('name')}' added to stx.toml.[/green]")
    console.print("Run `stx pack sync` to install.")


@pack.command("remove")
@click.argument("name")
def remove_cmd(name: str) -> None:
    """Remove a pack from stx.toml."""
    console = get_console()
    project_dir = _find_project_dir()
    if _stx_toml.remove_pack(project_dir, name):
        remove_uv_source(project_dir, name)
        console.print(f"[green]Pack '{name}' removed.[/green]")
    else:
        raise click.ClickException(f"Pack '{name}' not found in stx.toml.")


@pack.command("list")
@click.option("--trace", is_flag=True, help="Show lifecycle transitions (§5.6bis).")
def list_cmd(trace: bool) -> None:
    """List packs declared in stx.toml and their lifecycle state."""
    from ._divergence import maybe_warn_divergence

    maybe_warn_divergence("pack list")
    from streamtex.core import discovery

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    if not stx_toml.is_file():
        console.print("[yellow]No stx.toml in this project.[/yellow]")
        return

    trace_buf: list[discovery.TraceEntry] | None = [] if trace else None
    packs = discovery.discover_packs(stx_toml, trace=trace_buf)
    if not packs:
        console.print("No packs declared.")
        return

    uv_editables = set(get_uv_sources(project_dir).keys())
    for p in packs:
        flags = []
        if p.state != "nominal":
            flags.append(p.state)
        if p.indirect:
            flags.append("indirect")
        if p.name in uv_editables:
            flags.append("editable")
        suffix = f" [{', '.join(flags)}]" if flags else ""
        console.print(f"  • {p.name}{suffix}")
        for issue in p.issues:
            console.print(f"      ! {issue}")

    if trace_buf:
        console.print("\n[dim]Trace:[/dim]")
        for t in trace_buf:
            console.print(f"  {t.pack_name}: {t.transition}" + (f" ({t.detail})" if t.detail else ""))


@pack.command("sync")
def sync_cmd() -> None:
    """Reinstall all declared packs at their pinned version."""
    console = get_console()
    project_dir = _find_project_dir()
    packs = _stx_toml.list_packs(project_dir)
    if not packs:
        console.print("No packs to sync.")
        return

    for entry in packs:
        t = entry.get("type")
        name = entry.get("name") or entry.get("ref") or "<unnamed>"
        try:
            if t == "local":
                path = entry.get("path")
                if not path:
                    continue
                # editable=True → uv add --editable, otherwise plain editable install
                set_uv_source(
                    project_dir, name, path, editable=bool(entry.get("editable", True))
                )
                console.print(f"  uv sources updated for {name} → {path}")
            elif t == "git":
                ref = entry.get("ref") or ""
                rev = entry.get("rev")
                subdir = entry.get("subdirectory")
                # Tolerate legacy entries that stored an explicit scheme.
                canonical = re.sub(r"^https?://", "", ref).rstrip("/")
                canonical = re.sub(r"\.git$", "", canonical)
                url = f"https://{canonical}"
                set_uv_source_git(
                    project_dir, name, url, rev=rev, subdirectory=subdir
                )
                bits = [f"git+{url}"]
                if rev:
                    bits.append(f"@{rev}")
                if subdir:
                    bits.append(f"#subdirectory={subdir}")
                console.print(f"  uv sources updated for {name} → {''.join(bits)}")
            elif t == "pypi":
                # PyPI entries are honored by uv via [project].dependencies; no
                # uv.sources mapping needed. We just make sure the constraint
                # is reflected as a dependency so `uv sync` resolves it.
                spec = name + (entry.get("constraint") or "")
                ensure_pypi_dependency(project_dir, spec)
                console.print(f"  pyproject dependency ensured for {spec}")
        except Exception as exc:  # noqa: BLE001 — surface but don't crash sync
            console.print(f"[red]sync error on {name}: {exc}[/red]")
    console.print("[green]Sync complete (run `uv sync` to apply [tool.uv.sources] changes).[/green]")


@pack.command("info")
@click.argument("name")
def info_cmd(name: str) -> None:
    """Show details about a configured pack."""
    from streamtex.core import discovery

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    target = next((p for p in packs if p.name == name), None)
    if target is None:
        raise click.ClickException(f"Pack '{name}' not in stx.toml.")
    console.print(f"name:        {target.name}")
    console.print(f"state:       {target.state}")
    console.print(f"declared:    {target.declared}")
    console.print(f"installed:   {target.installed}")
    console.print(f"module:      {target.entry_point_module or '<none>'}")
    if target.manifest:
        pack_info = target.manifest.get("pack", {})
        console.print(f"version:     {pack_info.get('version', '?')}")
        console.print(f"streamtex_compat: {pack_info.get('streamtex_compat', '?')}")


@pack.command("validate")
@click.argument("name", required=False)
def validate_cmd(name: str | None) -> None:
    """Validate one (or all) installed packs against the manifest schema."""
    from ._divergence import maybe_warn_divergence

    maybe_warn_divergence("pack validate")
    from streamtex.core import discovery, validation

    console = get_console()
    project_dir = _find_project_dir()
    packs = discovery.discover_packs(project_dir / "stx.toml" if (project_dir / "stx.toml").is_file() else None)
    targets = packs if name is None else [p for p in packs if p.name == name]
    if not targets:
        raise click.ClickException(f"Pack '{name}' not found." if name else "No packs to validate.")

    any_error = False
    for pack_obj in targets:
        if pack_obj.entry_point_module is None:
            console.print(f"[red]{pack_obj.name}: not installed[/red]")
            any_error = True
            continue
        import importlib

        mod = importlib.import_module(pack_obj.entry_point_module)
        pack_root = Path(mod.__file__).resolve().parent  # type: ignore[arg-type]
        issues = validation.validate_pack(pack_root)
        errors = [i for i in issues if i.is_error()]
        if errors:
            any_error = True
            console.print(f"[red]{pack_obj.name}: FAIL[/red]")
            for issue in errors:
                console.print(f"  [{issue.code}] {issue.message}")
        else:
            console.print(f"[green]{pack_obj.name}: OK[/green]")
    if any_error:
        raise click.ClickException("Some packs failed validation.")


@pack.command("new")
@click.argument("name")
@click.option("--path", default=None, help="Where to create the pack (default: ./<name>/).")
def new_cmd(name: str, path: str | None) -> None:
    """Scaffold a new local pack in the project (Q7 multi-pack)."""
    console = get_console()
    project_dir = _find_project_dir()
    target = Path(path) if path else project_dir / name
    target = target.resolve()
    if target.exists():
        raise click.ClickException(f"{target} already exists; choose a different name.")

    # Layout: <target>/<name>/_pack_manifest.toml + sub-dirs
    pkg_dir = target / name
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text(
        f'"""Local pack {name}."""\n', encoding="utf-8"
    )
    manifest_body = (
        '[manifest]\n'
        'format = "0.1"\n'
        '\n'
        '[pack]\n'
        f'name = "{name}"\n'
        'version = "0.1.0"\n'
        'author = "TBD"\n'
        'license = "MIT"\n'
        'streamtex_compat = ">=0.7,<1.0"\n'
        '\n'
        '[entrypoint]\n'
        f'module = "{name}"\n'
    )
    (pkg_dir / "_pack_manifest.toml").write_text(manifest_body, encoding="utf-8")
    for sub in ("components", "design_systems", "cli_templates", "kits"):
        (pkg_dir / sub).mkdir()
        (pkg_dir / sub / ".gitkeep").touch()

    # Minimal pyproject for the editable install
    pyproject_body = (
        '[project]\n'
        f'name = "{name}"\n'
        'version = "0.1.0"\n'
        'requires-python = ">=3.11"\n'
        '\n'
        '[build-system]\n'
        'requires = ["setuptools>=68"]\n'
        'build-backend = "setuptools.build_meta"\n'
        '\n'
        '[project.entry-points."streamtex.packs"]\n'
        f'{name} = "{name}"\n'
    )
    (target / "pyproject.toml").write_text(pyproject_body, encoding="utf-8")

    # Declare in stx.toml + uv sources
    try:
        _stx_toml.add_pack(
            project_dir,
            {
                "type": "local",
                "name": name,
                "path": f"./{name}",
                "editable": True,
                "primary": False,
            },
        )
    except ValueError as exc:
        console.print(f"[yellow]stx.toml: {exc}[/yellow]")
    set_uv_source(project_dir, name, f"./{name}", editable=True)

    console.print(f"[green]Local pack '{name}' scaffolded at {target}[/green]")


@pack.command("set-primary")
@click.argument("name")
def set_primary_cmd(name: str) -> None:
    """Mark <name> as primary=true; clears primary on the others."""
    console = get_console()
    project_dir = _find_project_dir()
    packs = _stx_toml.list_packs(project_dir)
    target = next((p for p in packs if p.get("name") == name and p.get("type") == "local"), None)
    if target is None:
        raise click.ClickException(f"Local pack '{name}' not declared in stx.toml.")


    doc = _stx_toml.load(project_dir)
    for entry in doc.get("packs", []) or []:
        if entry.get("type") == "local":
            entry["primary"] = entry.get("name") == name
    _stx_toml.save(project_dir, doc)
    console.print(f"[green]Primary local pack: {name}[/green]")
