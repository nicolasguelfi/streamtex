"""stx artifact — list / show / validate for the generic artifact engine.

A single uniform CLI for all manifest-0.2 artifact categories (palette,
ai_prompt, archetype, guideline, skill, agent, asset, integration). Per-kind
formatting lives in the per-category render helpers below.

See `streamtex.core.artifacts` for the engine API and the RFC at
`documentation/maintenance/design-packs/RFC-extended-artifacts.md`.
"""

from __future__ import annotations

from pathlib import Path

import click

from streamtex.core.artifacts import (
    ArtifactKind,
    discover_artifacts,
    install_claude_artifact,
    resolve_artifact,
    validate_artifact,
)

from ._shared import _find_project_dir
from .console import get_console

_KIND_CHOICES = [k.value for k in ArtifactKind]


def _parse_kind(value: str | None) -> ArtifactKind | None:
    if value is None:
        return None
    try:
        return ArtifactKind(value)
    except ValueError as exc:
        raise click.BadParameter(
            f"unknown artifact kind {value!r} ; supported: {', '.join(_KIND_CHOICES)}"
        ) from exc


def _kinds_to_scan(kind: ArtifactKind | None) -> list[ArtifactKind]:
    return [kind] if kind else list(ArtifactKind)


@click.group()
def artifact() -> None:
    """Manage extended pack artifacts (manifest 0.2 — palettes, prompts, …)."""


@artifact.command("list")
@click.option(
    "--kind",
    "kind_str",
    type=click.Choice(_KIND_CHOICES),
    default=None,
    help="Filter by artifact category. Default: all categories.",
)
@click.option("--pack", "pack_filter", default=None, help="Filter by pack name.")
def list_cmd(kind_str: str | None, pack_filter: str | None) -> None:
    """Enumerate artifacts across installed packs."""
    console = get_console()
    kind = _parse_kind(kind_str)
    total = 0
    for k in _kinds_to_scan(kind):
        found = discover_artifacts(k, pack=pack_filter)
        if not found:
            continue
        total += len(found)
        console.print(f"[bold]{k.value}[/bold] ({len(found)})")
        for art in found:
            console.print(f"  {art.pack}:{art.name}  [dim]({art.path})[/dim]")
    if total == 0:
        scope = f"kind={kind.value}" if kind else "any kind"
        pack_scope = f" pack={pack_filter}" if pack_filter else ""
        console.print(f"[dim]No artifacts found ({scope}{pack_scope}).[/dim]")


@artifact.command("show")
@click.argument("name")
@click.option(
    "--kind",
    "kind_str",
    type=click.Choice(_KIND_CHOICES),
    required=True,
    help="Artifact category.",
)
@click.option("--pack", "pack_filter", default=None, help="Disambiguate by pack name.")
def show_cmd(name: str, kind_str: str, pack_filter: str | None) -> None:
    """Show one artifact's content (formatted per kind)."""
    console = get_console()
    kind = ArtifactKind(kind_str)
    try:
        discovered = resolve_artifact(
            name, kind, prefer=[pack_filter] if pack_filter else None
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(f"[bold]{discovered.pack}:{discovered.name}[/bold]  ({kind.value})")
    console.print(f"[dim]{discovered.path}[/dim]")
    console.print()

    if kind == ArtifactKind.PALETTE:
        _render_palette(discovered, console)
    elif kind == ArtifactKind.AI_PROMPT:
        _render_ai_prompt(discovered, console)
    elif kind == ArtifactKind.ARCHETYPE:
        _render_archetype(discovered, console)
    elif kind == ArtifactKind.GUIDELINE:
        _render_guideline(discovered, console)
    elif kind in (ArtifactKind.SKILL, ArtifactKind.AGENT):
        _render_skill_or_agent(discovered, console, kind)
    else:
        # Fallback: dump path + first lines for categories not yet rendered.
        try:
            if discovered.path.is_file():
                console.print(discovered.path.read_text()[:2000])
            else:
                for child in sorted(discovered.path.iterdir())[:20]:
                    console.print(f"  {child.name}")
        except Exception as exc:
            console.print(f"[red]Could not preview: {exc}[/red]")


@artifact.command("validate")
@click.argument("name", required=False)
@click.option(
    "--kind",
    "kind_str",
    type=click.Choice(_KIND_CHOICES),
    default=None,
    help="Filter by artifact category. Default: all categories.",
)
@click.option("--pack", "pack_filter", default=None, help="Filter by pack name.")
def validate_cmd(name: str | None, kind_str: str | None, pack_filter: str | None) -> None:
    """Validate one (NAME + --kind) or all matching artifacts.

    Exit code 0 if no errors ; 1 otherwise.
    """
    console = get_console()
    kind = _parse_kind(kind_str)
    targets = []
    for k in _kinds_to_scan(kind):
        for art in discover_artifacts(k, pack=pack_filter):
            if name is None or art.name == name:
                targets.append((k, art))

    if not targets:
        console.print("[yellow]No artifacts matched the filters.[/yellow]")
        return

    total_errors = 0
    for k, art in targets:
        issues = validate_artifact(art.path, k)
        errors = [i for i in issues if i.is_error()]
        warnings = [i for i in issues if i.severity == "warning"]
        status = "[green]OK[/green]" if not errors else f"[red]{len(errors)} error(s)[/red]"
        warn_tag = f" [yellow]({len(warnings)} warn)[/yellow]" if warnings else ""
        console.print(f"{art.pack}:{art.name}  ({k.value})  {status}{warn_tag}")
        for issue in errors + warnings:
            tag_color = "red" if issue.severity == "error" else "yellow"
            console.print(f"  [{tag_color}][{issue.code}][/{tag_color}] {issue.message}")
        total_errors += len(errors)

    if total_errors:
        raise click.ClickException(
            f"{total_errors} validation error(s) across {len(targets)} artifact(s)."
        )


@artifact.command("install")
@click.argument("name")
@click.option(
    "--kind",
    "kind_str",
    type=click.Choice(["skill", "agent"]),
    required=True,
    help="Only skills and agents are installable to .claude/custom/.",
)
@click.option("--pack", "pack_filter", default=None, help="Disambiguate by pack name.")
@click.option("--yes", "auto_yes", is_flag=True, help="Skip confirmation prompt.")
@click.option(
    "--overwrite", is_flag=True, help="Overwrite an existing installed file."
)
def install_cmd(
    name: str,
    kind_str: str,
    pack_filter: str | None,
    auto_yes: bool,
    overwrite: bool,
) -> None:
    """Install a pack-shipped skill or agent into .claude/custom/.

    Lifecycle decision EAR-4: confirmation by default, ``--yes`` to skip.
    Files are namespaced as ``<pack_slug>__<name>.md`` to avoid collisions.
    """
    console = get_console()
    kind = ArtifactKind(kind_str)
    try:
        discovered = resolve_artifact(
            name, kind, prefer=[pack_filter] if pack_filter else None
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    project_dir = _find_project_dir() or Path.cwd()
    target_dir = project_dir / ".claude" / "custom" / (
        "skills" if kind == ArtifactKind.SKILL else "agents"
    )
    pack_slug = discovered.pack.replace("streamtex-pack-", "").replace("-", "_")
    target = target_dir / f"{pack_slug}__{discovered.name}.md"

    console.print(
        f"Install {discovered.pack}:{discovered.name} ({kind.value}) "
        f"\n  from: {discovered.path}"
        f"\n  to:   {target}"
    )

    if not auto_yes:
        if not click.confirm("Proceed?", default=True):
            console.print("[yellow]Cancelled.[/yellow]")
            return

    report = install_claude_artifact(
        name, kind, project_dir, pack=pack_filter, overwrite=overwrite
    )
    if report.action == "skipped":
        console.print(
            "[yellow]Skipped[/yellow] — destination already exists. Use "
            "--overwrite to replace."
        )
    else:
        console.print(f"[green]{report.action}[/green] → {report.destination}")


# ---------------------------------------------------------------------------
# Per-kind renderers
# ---------------------------------------------------------------------------


def _render_palette(discovered, console) -> None:
    from streamtex.core.artifacts.palette import load_palette_from_path

    palette = load_palette_from_path(discovered.path, pack=discovered.pack)
    console.print(f"version: {palette.version}")
    console.print(f"colors ({len(palette.colors)}):")
    for token, color in palette.colors.items():
        role = f" — {color.role}" if color.role else ""
        console.print(f"  {token:<16}  {color.hex}{role}")
    if palette.dimensions:
        console.print(f"dimensions ({len(palette.dimensions)}):")
        for dim, target in palette.dimensions.items():
            console.print(f"  {dim:<16} → {target}")


def _render_ai_prompt(discovered, console) -> None:
    from streamtex.core.artifacts.ai_prompt import load_ai_prompt_from_path

    prompt = load_ai_prompt_from_path(discovered.path, pack=discovered.pack)
    console.print(f"orientations: {', '.join(sorted(prompt.suffixes)) or '(none)'}")
    console.print()
    console.print("[bold]prefix[/bold]:")
    console.print(prompt.prefix)
    console.print()
    for orient in sorted(prompt.suffixes):
        console.print(f"[bold]suffix-{orient}[/bold]:")
        console.print(prompt.suffixes[orient])
        console.print()


def _render_archetype(discovered, console) -> None:
    from streamtex.core.artifacts.archetype import load_archetype_from_path

    arch = load_archetype_from_path(discovered.path, pack=discovered.pack)
    console.print(f"description: {arch.description}")
    console.print(
        f"orientation: {arch.orientation}  •  status: {arch.status}  •  since: {arch.since}"
    )
    if arch.tags:
        console.print(f"tags: {', '.join(arch.tags)}")
    if arch.palette_refs:
        console.print(f"palette refs: {', '.join(arch.palette_refs)}")
    console.print(f"extrapolable: {arch.extrapolable}")
    console.print()
    body = arch.body.lstrip()
    console.print(body[:1500])
    if len(body) > 1500:
        console.print("[dim]… (truncated)[/dim]")


def _render_guideline(discovered, console) -> None:
    from streamtex.core.artifacts.guideline import load_guideline_from_path

    gl = load_guideline_from_path(discovered.path, pack=discovered.pack)
    console.print(f"description: {gl.description}")
    console.print(f"since: {gl.since}")
    if gl.rules:
        console.print(f"rules: {', '.join(gl.rules)}")
    if gl.applies_to:
        console.print(f"applies to: {', '.join(gl.applies_to)}")
    console.print()
    body = gl.body.lstrip()
    console.print(body[:1500])
    if len(body) > 1500:
        console.print("[dim]… (truncated)[/dim]")


def _render_skill_or_agent(discovered, console, kind: ArtifactKind) -> None:
    if kind == ArtifactKind.SKILL:
        from streamtex.core.artifacts.skill import load_skill_from_path
        loaded = load_skill_from_path(discovered.path, pack=discovered.pack)
    else:
        from streamtex.core.artifacts.agent import load_agent_from_path
        loaded = load_agent_from_path(discovered.path, pack=discovered.pack)
    console.print(f"description: {loaded.description}")
    console.print(f"namespace: {loaded.namespaced_name}")
    console.print(f"install filename: {loaded.install_filename}")
    console.print()
    body = loaded.body.lstrip()
    console.print(body[:1500])
    if len(body) > 1500:
        console.print("[dim]… (truncated)[/dim]")
