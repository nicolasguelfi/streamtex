"""Unified install command: stx install.

Replaces the old stx workspace init / update / upgrade workflow with a
single entry point that handles first-time installation, project creation,
and subsequent updates.
"""

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone

import click

from .console import get_console
from .workspace_cmd import (
    ALL_REPOS,
    PRESET_EXTRAS,
    PRESET_ORDER,
    PRESET_REPOS,
    _install_global_commands,
    _install_precommit_hooks,
    _run_uv_sync,
    find_workspace_root,
    generate_stx_toml,
    load_stx_toml,
)

# ---------------------------------------------------------------------------
# Available templates (static list — extended over time)
# ---------------------------------------------------------------------------

AVAILABLE_TEMPLATES = ["project", "collection", "slides"]

# ---------------------------------------------------------------------------
# Install state file helpers
# ---------------------------------------------------------------------------

_STATE_FILE = ".stx-install.json"


def _load_state(ws_root: str) -> dict:
    """Load the install state file, or return empty dict."""
    path = os.path.join(ws_root, _STATE_FILE)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_state(ws_root: str, state: dict) -> None:
    """Write the install state file."""
    path = os.path.join(ws_root, _STATE_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _clear_state(ws_root: str) -> None:
    """Remove the install state file."""
    path = os.path.join(ws_root, _STATE_FILE)
    if os.path.isfile(path):
        os.remove(path)


def _step_done(state: dict, step: str) -> bool:
    """Check if a step was already completed."""
    return state.get("steps", {}).get(step) == "done"


def _mark_step(ws_root: str, state: dict, step: str, status: str = "done") -> None:
    """Mark a step as done and persist."""
    state.setdefault("steps", {})[step] = status
    _save_state(ws_root, state)


def _install_chromium(run_dir: str, console) -> bool:
    """Download the Chromium browser used by ``stx screenshot`` and PDF export.

    Cross-platform (Playwright handles macOS/Linux/Windows) and idempotent —
    the browser is cached per user, not per venv, so re-running is cheap.
    **Non-fatal**: on any failure the manual command is printed and the
    install continues. Returns True on success.
    """
    manual = f"    Run later: cd {run_dir} && uv run playwright install chromium"
    # Escape hatch for CI / offline / hermetic test environments.
    if os.environ.get("STX_SKIP_BROWSER_INSTALL"):
        console.print("  [yellow]Skipping Chromium download (STX_SKIP_BROWSER_INSTALL set).[/yellow]")
        console.print(manual)
        return False
    console.print("  Downloading Chromium (~150 MB, up to a few minutes) ...")
    try:
        result = subprocess.run(
            ["uv", "run", "playwright", "install", "chromium"],
            cwd=run_dir, capture_output=True, text=True, timeout=600,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        console.print(f"  [yellow]Chromium install skipped:[/yellow] {exc}")
        console.print(manual)
        return False
    if result.returncode == 0:
        console.print("  [green]Chromium ready (screenshots + PDF export).[/green]")
        return True
    console.print("  [yellow]Chromium install did not complete.[/yellow]")
    console.print(manual)
    return False


# ---------------------------------------------------------------------------
# Template availability check
# ---------------------------------------------------------------------------

def _check_template_available(template: str, console) -> str | None:
    """Check if a template name is available.

    Returns the template name to use, or None if the user chose to skip.
    """
    if template in AVAILABLE_TEMPLATES:
        return template

    console.print(
        f"\n[cyan]The '{template}' template is not yet available.[/cyan]\n"
        "  We're actively working on expanding our template catalog!\n"
    )
    console.print(f"  Available templates: {', '.join(AVAILABLE_TEMPLATES)}\n")

    if click.confirm(
        "  Would you like to continue with the 'project' template?",
        default=True,
    ):
        return "project"
    return None


# ---------------------------------------------------------------------------
# Docs repo confirmation for basic/user presets
# ---------------------------------------------------------------------------

def _maybe_clone_docs_for_template(
    ws_root: str, config: dict, preset: str, console,
) -> bool:
    """If preset lacks docs repo but user wants a template, offer to clone it.

    Returns True if docs repo is available (already or freshly cloned).
    """
    preset_repos = PRESET_REPOS.get(preset, [])
    if "docs" in preset_repos:
        return True  # already included

    # Honor dev-link first — no clone needed if user has registered a local source.
    from .dev_config import resolve_repo_path

    try:
        _resolved, is_dev = resolve_repo_path("streamtex-docs", ws_root, config)
        if is_dev:
            console.print(
                "  [dim]streamtex-docs: dev-linked — no clone needed.[/dim]"
            )
            return True
    except FileNotFoundError:
        pass

    docs_path = os.path.join(ws_root, "streamtex-docs")
    if os.path.isdir(docs_path):
        return True  # already cloned from a previous session

    console.print(
        f"\n[yellow]The template requires the streamtex-docs repository.[/yellow]\n"
        f"  Your preset '{preset}' does not include it.\n"
    )
    if click.confirm("  Clone streamtex-docs to access templates?", default=True):
        url = ALL_REPOS["docs"]["url"]
        console.print(f"  Cloning {url} ...")
        result = subprocess.run(
            ["git", "clone", url, docs_path],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            console.print("  [green]streamtex-docs cloned.[/green]")
            return True
        console.print(f"  [red]Clone failed:[/red] {result.stderr.strip()}")
        return False

    return False


# ---------------------------------------------------------------------------
# Main install command
# ---------------------------------------------------------------------------

@click.command()
@click.option(
    "--preset",
    default=None,
    type=click.Choice(PRESET_ORDER),
    help="Installation preset (default: standard).",
)
@click.option(
    "--project",
    default=None,
    help="Create a project with this name.",
)
@click.option(
    "--template",
    default=None,
    help="Project template (project, collection, slides).",
)
@click.option(
    "--dev",
    is_flag=True,
    default=False,
    help="Link the globally-registered streamtex dev source into the new "
         "project's venv (equivalent to `stx dev link streamtex` inside it). "
         "Requires `stx dev register streamtex /path/...` first. "
         "No-op without --project.",
)
@click.option(
    "--no-design-pack",
    is_flag=True,
    default=False,
    help="Skip the auto-add of the `streamtex-design` pack to the project's "
         "stx.toml after project creation.",
)
def install(preset, project, template, dev, no_design_pack):
    """Install or update a StreamTeX workspace, optionally creating a project.

    First run:  stx install --preset power --project hello
    Add project: stx install --project myapp --template collection
    Dev mode:    stx install --project myapp --dev
    """
    console = get_console()
    ws_root = find_workspace_root()

    # --- Determine mode ---
    if ws_root is not None:
        # Workspace exists
        config = load_stx_toml(ws_root)
        existing_preset = config.get("workspace", {}).get("preset", "standard")

        if preset is not None and preset != existing_preset:
            # User wants to change preset → upgrade
            _do_upgrade(ws_root, config, existing_preset, preset, console)
            # Reload config after upgrade
            config = load_stx_toml(ws_root)
            existing_preset = preset

        effective_preset = preset or existing_preset

        if project is None and preset is None:
            raise click.ClickException(
                "Already in a workspace. Use:\n"
                "  stx install --project <name>   to create a new project\n"
                "  stx update                     to sync workspace"
            )
    else:
        # Fresh install
        if project is None and preset is None:
            # Default: standard preset, no project
            preset = "standard"

        effective_preset = preset or "standard"

        ws_root = os.path.abspath(".")

    # --- Load or create state file ---
    state = _load_state(ws_root)
    if state:
        console.print(
            f"[cyan]Resuming previous installation (started {state.get('started', '?')}).[/cyan]"
        )
    else:
        state = {
            "started": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "preset": effective_preset,
            "project": project,
            "template": template,
            "steps": {},
        }

    # Validate flag combinations
    if dev and project is None:
        console.print(
            "[yellow]--dev has no effect without --project (no project to link).[/yellow]"
        )

    # Count total steps
    total_steps = 7  # init, clone, sync, global_commands, profiles, hooks, chromium
    has_project = project is not None
    if has_project:
        total_steps += 1  # project creation
        if dev:
            total_steps += 1  # dev-link streamtex into project
    step = 0

    def _step(label: str) -> None:
        nonlocal step
        step += 1
        console.print(f"\n[bold cyan][{step}/{total_steps}][/bold cyan] {label}")

    # --- Step 1: Init workspace ---
    toml_path = os.path.join(ws_root, "stx.toml")
    if not _step_done(state, "init"):
        _step("Creating workspace ...")
        if not os.path.isfile(toml_path):
            ws_name = os.path.basename(ws_root)
            created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            content = generate_stx_toml(ws_name, created, preset=effective_preset)
            with open(toml_path, "w", encoding="utf-8") as f:
                f.write(content)
            projects_dir = os.path.join(ws_root, "projects")
            os.makedirs(projects_dir, exist_ok=True)
            console.print(f"  stx.toml created (preset={effective_preset!r})")
            console.print("  projects/ directory created")
        else:
            console.print("  stx.toml already exists — skipping init")
        _mark_step(ws_root, state, "init")
    else:
        step += 1  # count the skipped step

    config = load_stx_toml(ws_root)
    repos = config.get("repos", {})

    # --- Step 2: Clone missing repos ---
    if not _step_done(state, "clone"):
        # Detect dev-linked repos so we never clone over a registered source.
        from .dev_config import resolve_repo_path

        dev_linked: dict[str, str] = {}
        for repo_name in repos:
            try:
                resolved, is_dev = resolve_repo_path(repo_name, ws_root, config)
                if is_dev:
                    dev_linked[repo_name] = resolved
            except FileNotFoundError:
                pass

        missing = []
        for repo_name, repo_conf in repos.items():
            if repo_name in dev_linked:
                continue
            rel_path = repo_conf.get("path", repo_name)
            target_path = os.path.join(ws_root, rel_path)
            url = repo_conf.get("url", "")
            if url and not os.path.isdir(target_path):
                missing.append((repo_name, url, target_path))

        _step(f"Cloning {len(missing)} missing repo(s) ...")
        if dev_linked:
            for repo_name, resolved in dev_linked.items():
                console.print(
                    f"  [cyan]{repo_name}[/cyan]: dev-linked — skip clone "
                    f"[dim]({resolved})[/dim]"
                )
        if missing:
            for repo_name, url, target_path in missing:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                console.print(f"  [cyan]{repo_name}[/cyan]: cloning {url} ...")
                result = subprocess.run(
                    ["git", "clone", url, target_path],
                    capture_output=True, text=True, timeout=120,
                )
                if result.returncode == 0:
                    console.print(f"  [green]{repo_name}[/green]: cloned")
                else:
                    console.print(f"  [red]{repo_name}[/red]: clone failed")
                    if result.stderr:
                        console.print(f"    {result.stderr.strip()}")
        elif not dev_linked:
            console.print("  No missing repos.")
        _mark_step(ws_root, state, "clone")
    else:
        step += 1

    # --- Step 3: Sync dependencies ---
    if not _step_done(state, "sync"):
        _step("Syncing dependencies ...")
        _run_uv_sync(repos, ws_root)
        _mark_step(ws_root, state, "sync")
    else:
        step += 1

    # --- Step 4: Create project (if requested) ---
    if has_project:
        if not _step_done(state, "project"):
            _step(f"Creating project {project} ...")
            _create_project(
                ws_root, config, project, template, effective_preset, console,
            )
            _mark_step(ws_root, state, "project")
        else:
            step += 1

    # --- Step 4b: Link streamtex dev source into project (if --dev) ---
    if has_project and dev:
        if not _step_done(state, "dev_link"):
            _step(f"Linking dev streamtex into projects/{project} ...")
            _apply_dev_link_to_project(ws_root, project, console)
            _mark_step(ws_root, state, "dev_link")
        else:
            step += 1

    # --- Step 5: Install global commands ---
    if not _step_done(state, "global_commands"):
        _step("Installing global commands ...")
        _install_global_commands(ws_root, config, console)
        _mark_step(ws_root, state, "global_commands")
    else:
        step += 1

    # --- Step 6: Update Claude profiles ---
    if not _step_done(state, "profiles"):
        _step("Updating Claude profiles ...")
        try:
            from .claude_cmd import (
                _update_single_target,
                find_claude_repo,
                find_profile_targets,
            )

            claude_repo = find_claude_repo(ws_root, config)
            targets = find_profile_targets(ws_root)
            if targets:
                for target_path, profile in targets:
                    rel = os.path.relpath(target_path, ws_root)
                    console.print(f"  [bold cyan]-- {rel} [/bold cyan]([cyan]{profile}[/cyan])")
                    _update_single_target(claude_repo, profile, target_path, False, console)
            else:
                console.print("  [yellow]No projects with Claude profiles found.[/yellow]")
        except click.ClickException:
            console.print("  [yellow]Claude repo not available — skipped.[/yellow]")
        _mark_step(ws_root, state, "profiles")
    else:
        step += 1

    # --- Step 7: Install pre-commit hooks ---
    if not _step_done(state, "hooks"):
        _step("Installing pre-commit hooks ...")
        _install_precommit_hooks(ws_root, config, console)
        _mark_step(ws_root, state, "hooks")
    else:
        step += 1

    # --- Optional: auto-add streamtex-design pack to project (project only) ---
    if has_project and not no_design_pack:
        _add_default_design_pack(ws_root, project, effective_preset, console)

    # --- Step: install Chromium (powers `stx screenshot` + PDF export) ---
    # Playwright ships in every preset via the `pdf` extra; the browser binary
    # is downloaded here so visual capture and PDF export work out of the box.
    if not _step_done(state, "chromium"):
        _step("Installing Chromium (screenshots + PDF export) ...")
        chromium_dir = (
            os.path.join(ws_root, "projects", project) if has_project else ws_root
        )
        _install_chromium(chromium_dir, console)
        _mark_step(ws_root, state, "chromium")
    else:
        step += 1  # count the skipped step

    # --- Done ---
    _clear_state(ws_root)
    console.print("\n[bold green]Installation complete![/bold green]")

    if has_project:
        proj_path = os.path.join("projects", project)
        console.print("\n  To run your project:")
        console.print(f"    cd {proj_path} && stx run")
        console.print("\n  To capture slide screenshots for review:")
        console.print(f"    cd {proj_path} && stx screenshot")


# ---------------------------------------------------------------------------
# Project creation helper
# ---------------------------------------------------------------------------

def _create_project(
    ws_root: str,
    config: dict,
    name: str,
    template: str | None,
    preset: str,
    console,
) -> None:
    """Create a project within the workspace."""
    from .claude_cmd import find_claude_repo, install_profile
    from .project_cmd import (
        _copy_rich_template,
        generate_pyproject_toml,
        scaffold_project,
    )

    projects_dir = os.path.join(ws_root, "projects")
    os.makedirs(projects_dir, exist_ok=True)
    target = os.path.join(projects_dir, name)

    if os.path.isdir(target):
        console.print(f"  [yellow]projects/{name} already exists — skipping.[/yellow]")
        return

    os.makedirs(target, exist_ok=True)
    extras = PRESET_EXTRAS.get(preset, [])

    # Handle template
    use_template = None
    if template:
        use_template = _check_template_available(template, console)
        if use_template:
            # Ensure docs repo is available for template
            if not _maybe_clone_docs_for_template(ws_root, config, preset, console):
                console.print("  [yellow]Template skipped — using minimal scaffold.[/yellow]")
                use_template = None

    if use_template:
        _copy_rich_template(use_template, target, name)
        # Overwrite pyproject.toml with extras
        pyproject_path = os.path.join(target, "pyproject.toml")
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(generate_pyproject_toml(name, extras=extras))
        console.print(f"  Project created from template '{use_template}'")
    else:
        scaffold_project(target, name, extras=extras)
        console.print(f"  Project scaffolded: projects/{name}/")

    # Git init
    result = subprocess.run(
        ["git", "init", target],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode == 0:
        console.print("  [green]git init:[/green] ok")

    # Claude profile
    try:
        claude_repo = find_claude_repo(ws_root, config)
        installed = install_profile(claude_repo, "project", target)
        console.print(f"  [green]Claude profile:[/green] {len(installed)} files")
    except click.ClickException:
        console.print("  [yellow]Claude profile:[/yellow] not available — skipped")

    # uv sync in the project
    uv = shutil.which("uv")
    if uv:
        result = subprocess.run(
            [uv, "sync"], cwd=target,
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            console.print("  [green]uv sync:[/green] ok")
        else:
            console.print(f"  [yellow]uv sync:[/yellow] {result.stderr.strip()}")


# ---------------------------------------------------------------------------
# Upgrade helper (absorbed from stx workspace upgrade)
# ---------------------------------------------------------------------------

def _do_upgrade(
    ws_root: str, config: dict, current: str, target_preset: str, console,
) -> None:
    """Upgrade workspace preset in stx.toml."""
    import re

    current_idx = PRESET_ORDER.index(current) if current in PRESET_ORDER else len(PRESET_ORDER) - 1
    new_idx = PRESET_ORDER.index(target_preset)

    if new_idx < current_idx:
        raise click.ClickException(
            f"Cannot downgrade from '{current}' to '{target_preset}'."
        )

    if new_idx == current_idx:
        console.print(f"[yellow]Already at preset '{current}'.[/yellow]")
        return

    # Repos to add
    current_repos = set(PRESET_REPOS.get(current, []))
    new_repos = set(PRESET_REPOS[target_preset])
    to_add = new_repos - current_repos

    # Rewrite stx.toml
    toml_path = os.path.join(ws_root, "stx.toml")
    with open(toml_path, encoding="utf-8") as f:
        text = f.read()

    # Update preset line
    if re.search(r'^preset\s*=', text, re.MULTILINE):
        text = re.sub(
            r'^(preset\s*=\s*).*$',
            f'preset = "{target_preset}"',
            text,
            flags=re.MULTILINE,
        )
    else:
        text = re.sub(
            r'^(created\s*=\s*".+")$',
            f'\\1\npreset = "{target_preset}"',
            text,
            flags=re.MULTILINE,
        )

    # Add missing repo sections before [deploy]
    if to_add:
        new_sections = []
        for repo_key in PRESET_REPOS[target_preset]:
            if repo_key in to_add:
                repo = ALL_REPOS[repo_key]
                new_sections.append(f"\n[repos.{repo['name']}]")
                new_sections.append(f'url = "{repo["url"]}"')
                new_sections.append(f'path = "{repo["path"]}"')
                new_sections.append(f'type = "{repo["type"]}"')
        insert_block = "\n".join(new_sections) + "\n"
        text = text.replace("\n[deploy]", f"{insert_block}\n[deploy]")

    # Add claude.source if upgrading to a preset that includes claude
    if "claude" in to_add:
        if re.search(r'^\[claude\]\s*$', text, re.MULTILINE):
            text = re.sub(
                r'^\[claude\]\s*$',
                '[claude]\nsource = "streamtex-claude"',
                text,
                flags=re.MULTILINE,
            )

    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(text)

    console.print(f"[green]Upgraded from '{current}' to '{target_preset}'.[/green]")
    for repo_key in sorted(to_add):
        console.print(f"  + {ALL_REPOS[repo_key]['name']}")


# ---------------------------------------------------------------------------
# Dev-link integration (--dev flag)
# ---------------------------------------------------------------------------

def _apply_dev_link_to_project(ws_root: str, project_name: str, console) -> None:
    """Link the globally-registered streamtex source into a project's venv.

    Mirrors the effect of running `stx dev link streamtex` inside the project:
    writes `[tool.uv.sources]` to pyproject.toml and re-syncs uv so that the
    project's .venv uses the dev source instead of the PyPI release.

    No-op when streamtex is not registered globally (prints a hint).
    """
    from pathlib import Path

    from .dev_cmd import _add_uv_source, _ensure_gitignore, _uv_sync
    from .dev_config import GlobalDevConfig, validate_repo_path

    project_dir = Path(ws_root) / "projects" / project_name
    if not project_dir.is_dir():
        console.print(
            f"  [yellow]projects/{project_name} not found — skipped.[/yellow]"
        )
        return

    gcfg = GlobalDevConfig.load()
    streamtex_path = gcfg.repos.get("streamtex")
    if not streamtex_path:
        console.print(
            "  [yellow]streamtex is not registered globally — nothing to link.[/yellow]\n"
            "  [dim]Run: stx dev register streamtex /path/to/streamtex[/dim]"
        )
        return

    try:
        resolved = validate_repo_path("streamtex", streamtex_path)
    except ValueError as e:
        console.print(f"  [red]Invalid registered path:[/red] {e}")
        return

    console.print(f"  [cyan]streamtex[/cyan] → {resolved}")
    _add_uv_source(project_dir, str(resolved))
    _uv_sync(project_dir, console)
    _ensure_gitignore(project_dir)


# ---------------------------------------------------------------------------
# Opt-in patterns offer (called after project creation; never imposes anything)
# ---------------------------------------------------------------------------

def _install_is_interactive() -> bool:
    """True iff stdin is a terminal. Extracted so tests can monkeypatch it."""
    import sys

    return sys.stdin.isatty()


_DEFAULT_DESIGN_PACK = {
    "name": "streamtex-design",
    "ref": "github.com/nicolasguelfi/streamtex-design",
    "rev": "v0.1.0",
}

# Presets that opt in to the streamtex-design pack by default (PLAN §29.6).
_DESIGN_PACK_PRESETS = {"standard", "power", "developer"}


def _add_default_design_pack(
    ws_root: str, project_name: str, preset: str, console
) -> None:
    """Add the official ``streamtex-design`` pack to the project's stx.toml.

    Activated only for presets that opt in (``standard``, ``power``,
    ``developer``); the ``basic`` and ``user`` presets stay minimal. The
    entry is added idempotently via the Wave 1 helper ``_stx_toml.add_pack``.
    """
    from pathlib import Path

    if preset not in _DESIGN_PACK_PRESETS:
        return

    project_dir = Path(ws_root) / "projects" / project_name
    stx_toml_path = project_dir / "stx.toml"
    if not stx_toml_path.is_file():
        # stx.toml is generated for newly-created projects. If absent,
        # the project was bootstrapped outside `stx project new` — skip
        # silently rather than risk overwriting bespoke layouts.
        return

    try:
        from . import _stx_toml as _proj_toml

        existing = {p.get("name") for p in _proj_toml.list_packs(project_dir)}
        if _DEFAULT_DESIGN_PACK["name"] in existing:
            return

        _proj_toml.add_pack(
            project_dir,
            {
                "type": "git",
                "name": _DEFAULT_DESIGN_PACK["name"],
                "ref": _DEFAULT_DESIGN_PACK["ref"],
                "rev": _DEFAULT_DESIGN_PACK["rev"],
            },
        )
        console.print(
            f"[green]streamtex-design:[/green] added to "
            f"{stx_toml_path.relative_to(ws_root)} "
            f"(rev={_DEFAULT_DESIGN_PACK['rev']})"
        )
    except Exception as exc:
        # Auto-add is convenience; never break the install flow if it fails.
        console.print(f"[yellow]streamtex-design auto-add:[/yellow] {exc}")
