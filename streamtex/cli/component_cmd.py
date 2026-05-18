"""stx component — list / show / new / validate / find / promote.

Surface: PLAN.md §7.2. The 4-branch promote policy (Q12, §8.3) routes via
`_classify_destination`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Literal

import click

from . import _stx_toml
from .console import get_console

DestinationClass = Literal["primary_local", "secondary_local_with_git", "git_remote", "pypi"]


def _find_project_dir() -> Path:
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file():
        return cwd
    raise click.ClickException(
        "No pyproject.toml in current directory. Run from a StreamTeX project root."
    )


def _classify_destination(entry: dict) -> DestinationClass:
    """Pure router for `stx component promote`. Per §29.4 and §8.3.

    Branches:

    * primary_local — local pack with primary=true (capture target, no PR)
    * secondary_local_with_git — local pack containing its own .git directory
    * git_remote — type=git (open a PR to the upstream repo)
    * pypi — type=pypi (PyPI is read-only; refuse with PR001)
    """
    t = entry.get("type")
    if t == "pypi":
        return "pypi"
    if t == "git":
        return "git_remote"
    if t == "local":
        if entry.get("primary") is True:
            return "primary_local"
        # Secondary local — detect a sibling .git directory
        path = entry.get("path")
        if path and (Path(path) / ".git").is_dir():
            return "secondary_local_with_git"
        return "primary_local"  # plain copy mode
    raise click.ClickException(f"Unknown pack type: {t!r}")


@click.group()
def component():
    """Manage StreamTeX components across configured packs."""


@component.command("list")
@click.option("--pack", "pack_filter", default=None, help="Only list components from <pack>.")
def list_cmd(pack_filter: str | None) -> None:
    """List components from every installed pack."""
    from streamtex.core import discovery

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    artifacts = discovery.discover_components(packs)
    if pack_filter:
        artifacts = [a for a in artifacts if a.pack_name == pack_filter]
    if not artifacts:
        console.print("No components found.")
        return
    by_pack: dict[str, list[str]] = {}
    for a in artifacts:
        by_pack.setdefault(a.pack_name, []).append(a.name)
    for pack_name in sorted(by_pack):
        console.print(f"[bold]{pack_name}[/bold]")
        for cname in sorted(by_pack[pack_name]):
            console.print(f"  • {cname}")


@component.command("show")
@click.argument("name")
def show_cmd(name: str) -> None:
    """Print a component's source (path + module docstring)."""
    from streamtex.core import discovery

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    try:
        art = discovery.resolve_component(name, packs)
    except discovery.PackResolutionError as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(f"[bold]{art.pack_name}:{art.name}[/bold]")
    if art.path:
        console.print(f"path: {art.path}")
        try:
            console.print("---")
            console.print(art.path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]read error: {exc}[/red]")


@component.command("validate")
@click.argument("name", required=False)
def validate_cmd(name: str | None) -> None:
    """Validate one (or every) component module."""
    from streamtex.core import discovery, validation

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    artifacts = discovery.discover_components(packs)
    if name:
        artifacts = [a for a in artifacts if a.name == name]
        if not artifacts:
            raise click.ClickException(f"Component '{name}' not found in installed packs.")

    any_error = False
    for art in artifacts:
        if art.module is None:
            continue
        issues = validation.validate_component(art.module)
        errors = [i for i in issues if i.is_error()]
        if errors:
            any_error = True
            console.print(f"[red]{art.pack_name}:{art.name} FAIL[/red]")
            for i in errors:
                console.print(f"  [{i.code}] {i.message}")
        else:
            console.print(f"[green]{art.pack_name}:{art.name} OK[/green]")
    if any_error:
        raise click.ClickException("Some components failed validation.")


@component.command("find")
@click.argument("query")
def find_cmd(query: str) -> None:
    """Substring search across component names + tags."""
    from streamtex.core import discovery

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"
    packs = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    artifacts = discovery.discover_components(packs)
    q = query.lower()
    hits = []
    for art in artifacts:
        meta = getattr(art.module, "__component_meta__", None) if art.module else None
        tags = (meta or {}).get("tags", []) if isinstance(meta, dict) else []
        if q in art.name.lower() or any(q in t.lower() for t in tags):
            hits.append(art)
    for art in hits:
        console.print(f"  • {art.pack_name}:{art.name}")


@component.command("new")
@click.argument("name")
@click.option("--pack", "pack_name", default=None, help="Destination pack (default: primary local).")
@click.option("--granularity", default="primitive", type=click.Choice(["primitive", "composition", "block"]))
def new_cmd(name: str, pack_name: str | None, granularity: str) -> None:
    """Scaffold a new component in the chosen (or primary local) pack."""
    from streamtex.core import discovery

    console = get_console()
    project_dir = _find_project_dir()
    stx_toml = project_dir / "stx.toml"

    primary = discovery.get_primary_local_pack(stx_toml if stx_toml.is_file() else None)
    if pack_name is None and primary is None:
        raise click.ClickException(
            "No primary local pack declared in stx.toml. "
            "Run `stx pack new <name>` then `stx pack set-primary <name>`."
        )
    target_pack = pack_name or primary["name"]
    target_path = pack_name and Path(pack_name) or Path(primary["path"])
    if not target_path.is_absolute():
        target_path = (project_dir / target_path).resolve()
    components_dir = target_path / target_pack / "components"
    if not components_dir.exists():
        components_dir = target_path / "components"
        components_dir.mkdir(parents=True, exist_ok=True)

    target_file = components_dir / f"{name}.py"
    if target_file.exists():
        raise click.ClickException(f"{target_file} already exists.")

    template = _component_skeleton(name, granularity)
    target_file.write_text(template, encoding="utf-8")
    console.print(f"[green]Component scaffolded: {target_file}[/green]")
    console.print("Edit the docstring sections, then run `stx component validate`.")


def _component_skeleton(name: str, granularity: str) -> str:
    return f'''"""
# {name.replace("_", " ").title()} — short description (TODO)

## Visual
TODO ASCII mockup or short prose (≤ 500 chars).

## Structure
- bullet 1
- bullet 2

## Styling rules
| element | style |
|---|---|
| TODO | TODO |
| TODO | TODO |
| TODO | TODO |

## Extrapolation rules
### INVARIANTS
- TODO
- TODO
### PARAMS
- TODO
- TODO
### INTERDITS
- TODO
- TODO

## When to use
- TODO
- TODO

## When NOT to use
- TODO
- TODO

## Design system bundles required
- TODO bundle.attr
"""

__component_meta__ = {{
    "name": "{name}",
    "description": "TODO",
    "tags": ["TODO"],
    "extrapolable": True,
    "since": "2026-05-19",
    "bundles_required": [],
    "granularity": "{granularity}",
}}


def {name}(*, **kwargs) -> None:
    """Render {name} — TODO."""
    raise NotImplementedError("Implement {name}() body.")
'''


@component.command("promote")
@click.argument("name")
@click.option("--to", "destination", required=True, help="Target pack name (in stx.toml).")
@click.option("--no-commit", is_flag=True, help="Skip auto-commit for branches that support it.")
def promote_cmd(name: str, destination: str, no_commit: bool) -> None:
    """Promote a component from the project to a configured pack.

    Routing (Q12 — D17 §29.4):

    * primary_local       → plain copy (no commit), the dev commits with the project
    * secondary_local_w/git → copy + optional commit
    * git_remote          → clone cache → branch → push → `gh pr create`
    * pypi                → refused with PR001 (use --to=<git_pack_name>)
    """
    from streamtex.core import discovery, validation

    console = get_console()
    project_dir = _find_project_dir()
    packs = _stx_toml.list_packs(project_dir)
    target_entry = next((p for p in packs if p.get("name") == destination), None)
    if target_entry is None:
        raise click.ClickException(f"Destination pack '{destination}' not in stx.toml.")

    dest_class = _classify_destination(target_entry)
    if dest_class == "pypi":
        err = discovery.PackResolutionError(
            "PR001: cannot promote to a PyPI destination directly. "
            "Use `--to=<git_pack_name>` for the upstream repo of that PyPI package."
        )
        err.code = "PR001"
        raise click.ClickException(str(err))

    # Locate the component source in any pack
    stx_toml = project_dir / "stx.toml"
    packs_disc = discovery.discover_packs(stx_toml if stx_toml.is_file() else None)
    artifacts = discovery.discover_components(packs_disc)
    art = next((a for a in artifacts if a.name == name), None)
    if art is None or art.path is None:
        raise click.ClickException(f"Component '{name}' not found in installed packs.")

    # Validate before promoting
    if art.module is not None:
        issues = validation.validate_component(art.module)
        errors = [i for i in issues if i.is_error()]
        if errors:
            console.print(f"[red]Component {name} failed validation; aborting promote.[/red]")
            for issue in errors:
                console.print(f"  [{issue.code}] {issue.message}")
            raise click.ClickException("Promote aborted: component is invalid.")

    if dest_class in ("primary_local", "secondary_local_with_git"):
        target_root = Path(target_entry.get("path", ""))
        if not target_root.is_absolute():
            target_root = (project_dir / target_root).resolve()
        # Compute target components directory
        comp_dir = None
        for cand in (target_root / target_entry["name"] / "components", target_root / "components"):
            if cand.exists() or cand.parent.exists():
                comp_dir = cand
                break
        if comp_dir is None:
            comp_dir = target_root / "components"
        comp_dir.mkdir(parents=True, exist_ok=True)
        target_file = comp_dir / f"{name}.py"
        shutil.copy2(art.path, target_file)
        console.print(f"[green]Copied to {target_file}.[/green]")

        if dest_class == "secondary_local_with_git" and not no_commit:
            console.print(
                f"[yellow]Tip: cd {target_root} && git add {target_file.relative_to(target_root)} "
                f'&& git commit -m "promote {name}".[/yellow]'
            )
        return

    if dest_class == "git_remote":
        # v1 hands off to the user — the QCM+PR workflow is documented in
        # PLAN.md §8.3 but lives outside MIG-2's core surface.
        console.print(
            "[yellow]git_remote destination: copy the component into a fresh checkout "
            f"of {target_entry.get('ref')!r}, push a feat/promote-{name} branch and open "
            "a PR. Full automation is queued for a follow-up MIG.[/yellow]"
        )
        return
