"""Machine-level Claude commands: what stx copied into ``~/.claude/commands``.

- ``stx claude global status`` / ``remove`` (#74): classify and remove only
  what stx wrote there, never a file the user changed or added.
- Duplicate detection (#73): a ``stx-*`` group present both in
  ``~/.claude/commands`` and in a project's ``.claude/commands``.

Every copy made by ``_install_global_commands`` is recorded in
``~/.config/streamtex/global-commands.json`` (path → sha256). Copies made by
older versions carry no record; they are recognised by their read-only mode
(``0o444``, which stx always set) — a user editing one has to make it
writable first.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import click

from .console import get_console

# Groups once shipped in shared/commands and since removed from streamtex-claude.
RETIRED_GROUPS = frozenset({"stx-pattern"})


def global_commands_dir() -> Path:
    return Path.home() / ".claude" / "commands"


def record_path() -> Path:
    return Path.home() / ".config" / "streamtex" / "global-commands.json"


def load_record() -> dict[str, str]:
    p = record_path()
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("files", {})
    except (OSError, json.JSONDecodeError):
        return {}


def save_record(files: dict[str, str], source: str) -> None:
    p = record_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"source": source, "files": files}, indent=2, sort_keys=True) + "\n",
                 encoding="utf-8")


def _is_stx_name(name: str) -> bool:
    return name.startswith("stx-")


def _files_of(entry: Path) -> list[Path]:
    if entry.is_dir():
        return sorted(p for p in entry.rglob("*") if p.is_file())
    return [entry] if entry.is_file() else []


@dataclass
class GlobalEntry:
    name: str           # group dir or top-level file, e.g. "stx-ds", "stx-guide.md"
    state: str          # current | outdated | obsolete | modified
    files: list[str]    # relative to ~/.claude/commands


def classify(shared_commands: str | None) -> list[GlobalEntry]:
    """Classify every ``stx-*`` entry of ``~/.claude/commands``.

    - current  : identical to streamtex-claude ``shared/commands``
    - outdated : an older stx copy (read-only or recorded) of a group that still exists
    - obsolete : a stx copy of a group no longer shipped (e.g. ``stx-pattern``)
    - modified : at least one file was changed by the user (writable and not
      matching the record) — never removed
    """
    from ._claude_files import sha256_file

    gdir = global_commands_dir()
    if not gdir.is_dir():
        return []
    record = load_record()
    shared = Path(shared_commands) if shared_commands and os.path.isdir(shared_commands) else None
    out: list[GlobalEntry] = []
    for entry in sorted(gdir.iterdir()):
        if not _is_stx_name(entry.name):
            continue
        files = _files_of(entry)
        rels = [str(f.relative_to(gdir)) for f in files]
        src_entry = shared / entry.name if shared else None
        user_touched = False
        identical = src_entry is not None and src_entry.exists()
        for f, rel in zip(files, rels):
            src = (shared / rel) if shared else None
            same_as_src = bool(src and src.is_file() and src.read_bytes() == f.read_bytes())
            identical = identical and same_as_src
            if same_as_src:
                continue
            recorded = record.get(rel)
            stx_written = (recorded is not None and recorded == sha256_file(str(f))) or (
                not os.access(f, os.W_OK) or (f.stat().st_mode & 0o222) == 0)
            if not stx_written:
                user_touched = True
        if src_entry is not None and src_entry.exists():
            src_files = {str(p.relative_to(shared)) for p in _files_of(src_entry)}
            identical = identical and src_files == set(rels)
        if user_touched:
            state = "modified"
        elif src_entry is None or not src_entry.exists():
            state = "obsolete"
        elif identical:
            state = "current"
        else:
            state = "outdated"
        out.append(GlobalEntry(entry.name, state, rels))
    return out


def project_command_groups(target: str) -> set[str]:
    d = Path(target) / ".claude" / "commands"
    if not d.is_dir():
        return set()
    return {p.name for p in d.iterdir() if _is_stx_name(p.name)}


def duplicated_groups(target: str) -> list[str]:
    """``stx-*`` groups present both globally and in the project (#73)."""
    gdir = global_commands_dir()
    if not gdir.is_dir():
        return []
    global_names = {p.name for p in gdir.iterdir() if _is_stx_name(p.name)}
    return sorted(global_names & project_command_groups(target))


def obsolete_global_groups(shared_commands: str | None) -> list[str]:
    return [e.name for e in classify(shared_commands) if e.state == "obsolete"]


def _shared_commands_dir() -> str | None:
    from .claude_cmd import find_claude_repo
    from .workspace_cmd import find_workspace_root, load_stx_toml

    ws_root = find_workspace_root()
    try:
        config = load_stx_toml(ws_root) if ws_root else {}
        repo = find_claude_repo(ws_root or os.getcwd(), config)
    except click.ClickException:
        return None
    return os.path.join(repo, "shared", "commands")


def print_commands_report(ws_root: str | None, targets: list[tuple[str, str]], claude_repo: str | None,
                          console) -> None:
    """Warnings about duplicated / obsolete / missing Claude commands (#73).

    Prints nothing when there is nothing to report.
    """
    from ._claude_files import global_commands_enabled

    lines: list[str] = []
    for target, profile in targets:
        dups = duplicated_groups(target)
        if dups:
            rel = os.path.relpath(target, ws_root) if ws_root else target
            lines.append(
                f"[yellow]![/yellow] {rel} ({profile}) — {len(dups)} command group(s) also in "
                f"~/.claude/commands (both load): {', '.join(dups)}"
            )
    shared = os.path.join(claude_repo, "shared", "commands") if claude_repo else None
    obsolete = obsolete_global_groups(shared) if shared else []
    if obsolete:
        lines.append(
            f"[yellow]![/yellow] ~/.claude/commands — obsolete group(s) no longer shipped: "
            f"{', '.join(obsolete)} (stx claude global remove)"
        )
    if not global_commands_enabled() and ws_root and not targets:
        lines.append(
                "[yellow]![/yellow] global commands are off and no project here has a local "
                "profile: Claude Code has no stx command (stx claude install / sync)"
            )
    if lines:
        console.print("\n[bold]Claude commands[/bold]")
        for line in lines:
            console.print("  " + line)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group("global")
def global_group():
    """Inspect or remove the stx commands copied into ~/.claude/commands."""


_ICONS = {
    "current": "[green]current[/green]",
    "outdated": "[cyan]outdated[/cyan]",
    "obsolete": "[yellow]obsolete[/yellow]",
    "modified": "[red]modified by you[/red]",
}


@global_group.command("status")
def global_status() -> None:
    """Classify each stx-* entry of ~/.claude/commands."""
    from ._claude_files import global_commands_enabled

    console = get_console()
    entries = classify(_shared_commands_dir())
    console.print(f"[bold]~/.claude/commands[/bold] — global copy "
                  f"{'enabled' if global_commands_enabled() else 'disabled'}")
    if not entries:
        console.print("  (no stx-* commands)")
        return
    for e in entries:
        console.print(f"  {e.name:<22} {_ICONS[e.state]}  ({len(e.files)} file(s))")


@global_group.command("remove")
@click.option("-y", "--yes", is_flag=True, help="Remove (default: show what would be removed).")
def global_remove(yes: bool) -> None:
    """Remove the stx commands stx copied into ~/.claude/commands.

    Only stx copies are removed (current, outdated or obsolete); a file you
    changed is kept and listed. Without --yes nothing is removed.
    """
    import shutil

    from ._claude_files import global_commands_enabled

    console = get_console()
    entries = classify(_shared_commands_dir())
    removable = [e for e in entries if e.state != "modified"]
    kept = [e for e in entries if e.state == "modified"]
    if not entries:
        console.print("No stx-* commands in ~/.claude/commands.")
        return
    verb = "Removing" if yes else "Would remove"
    for e in removable:
        console.print(f"  {verb} {e.name} ({_ICONS[e.state]}, {len(e.files)} file(s))")
    for e in kept:
        console.print(f"  [red]Keeping[/red] {e.name}: modified by you")
    if not yes:
        console.print("\nDry run — rerun with --yes to remove.")
        return
    gdir = global_commands_dir()
    for e in removable:
        p = gdir / e.name
        for f in _files_of(p):
            os.chmod(f, 0o644)
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    record = {k: v for k, v in load_record().items()
              if k.split(os.sep)[0] not in {e.name for e in removable}}
    save_record(record, source="")
    console.print(f"\n[green]Removed {len(removable)} entr(y/ies).[/green]")
    if global_commands_enabled():
        console.print(
            "[yellow]The next `stx update` would copy them again.[/yellow] Turn the copy off "
            "in ~/.config/streamtex/config.toml:\n"
            "  \\[claude]\n  global_commands = false\n"
            "or pass --no-global-commands to stx update / stx install."
        )
