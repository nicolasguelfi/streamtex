"""Workspace commands: init, update, status, upgrade (+ deprecated clone/link/sync/hooks)."""

import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import click

from .console import get_console

# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------

PRESET_REPOS = {
    "basic": [],
    "user": ["claude"],
    "standard": ["docs", "claude"],
    "power": ["docs", "claude"],
    "developer": ["library", "docs", "claude"],
}

PRESET_ORDER = ["basic", "user", "standard", "power", "developer"]

# Extras automatically added to projects based on preset level
PRESET_EXTRAS = {
    "basic": ["cli", "pdf"],
    "user": ["cli", "pdf"],
    "standard": ["cli", "pdf", "ai"],
    "power": ["cli", "pdf", "ai", "inspector"],
    "developer": ["cli", "pdf", "ai", "inspector"],
}

ALL_REPOS = {
    "library": {
        "name": "streamtex",
        "url": "https://github.com/nicolasguelfi/streamtex.git",
        "path": "streamtex",
        "type": "library",
    },
    "docs": {
        "name": "streamtex-docs",
        "url": "https://github.com/nicolasguelfi/streamtex-docs.git",
        "path": "streamtex-docs",
        "type": "docs",
    },
    "claude": {
        "name": "streamtex-claude",
        "url": "https://github.com/nicolasguelfi/streamtex-claude.git",
        "path": "streamtex-claude",
        "type": "claude",
    },
}

# ---------------------------------------------------------------------------
# TOML helpers
# ---------------------------------------------------------------------------

def generate_stx_toml(name: str, created: str, preset: str = "standard") -> str:
    """Generate the content of a stx.toml file."""
    lines = [
        "[workspace]",
        f'name = "{name}"',
        f'created = "{created}"',
        f'preset = "{preset}"',
        "",
        "[repos]",
    ]

    for repo_key in PRESET_REPOS.get(preset, []):
        repo = ALL_REPOS[repo_key]
        lines.append("")
        lines.append(f"[repos.{repo['name']}]")
        lines.append(f'url = "{repo["url"]}"')
        lines.append(f'path = "{repo["path"]}"')
        lines.append(f'type = "{repo["type"]}"')

    lines.append("")
    lines.append("[deploy]")
    lines.append("# render_owner = \"nicolasguelfi\"")
    lines.append("# render_region = \"oregon\"")
    lines.append("")

    if "claude" in PRESET_REPOS.get(preset, []):
        lines.append("[claude]")
        lines.append('source = "streamtex-claude"')
    else:
        lines.append("[claude]")

    lines.append("")
    return "\n".join(lines)


def load_stx_toml(workspace_path: str) -> dict:
    """Load and parse a stx.toml file.

    Raises:
        click.ClickException: if the file does not exist or is invalid.
    """
    toml_path = os.path.join(workspace_path, "stx.toml")
    if not os.path.isfile(toml_path):
        raise click.ClickException(f"stx.toml not found in {workspace_path}")

    import tomllib

    with open(toml_path, "rb") as f:
        return tomllib.load(f)


def find_workspace_root(start_path: str | None = None) -> str | None:
    """Walk up from *start_path* looking for a directory containing stx.toml."""
    current = Path(start_path) if start_path else Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "stx.toml").is_file():
            return str(parent)
    return None


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def get_repo_status(repo_path: str) -> dict:
    """Return a dict with branch, clean, ahead, behind for a git repo."""
    result = {"path": repo_path, "branch": "?", "clean": True, "ahead": 0, "behind": 0}

    if not os.path.isdir(os.path.join(repo_path, ".git")):
        result["branch"] = "(not a git repo)"
        return result

    try:
        branch = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        result["branch"] = branch.stdout.strip() or "?"

        status = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )
        result["clean"] = len(status.stdout.strip()) == 0

        ahead_behind = subprocess.run(
            ["git", "-C", repo_path, "rev-list", "--left-right", "--count", "HEAD...@{u}"],
            capture_output=True, text=True, timeout=5,
        )
        if ahead_behind.returncode == 0:
            parts = ahead_behind.stdout.strip().split()
            if len(parts) == 2:
                result["ahead"] = int(parts[0])
                result["behind"] = int(parts[1])
    except (subprocess.TimeoutExpired, OSError):
        pass

    return result


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------

@click.command()
@click.argument("path", default=".")
@click.option("--name", default=None, help="Workspace name (defaults to directory name).")
@click.option(
    "--preset", default="standard",
    type=click.Choice(PRESET_ORDER),
    help="Installation preset (default: standard).",
)
def init(path, name, preset):
    """Initialize a StreamTeX workspace with stx.toml."""
    target = os.path.abspath(path)
    toml_path = os.path.join(target, "stx.toml")

    if os.path.isfile(toml_path):
        raise click.ClickException(f"stx.toml already exists in {target}")

    os.makedirs(target, exist_ok=True)

    ws_name = name or os.path.basename(target)
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    content = generate_stx_toml(ws_name, created, preset=preset)
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Create projects/ subdirectory
    projects_dir = os.path.join(target, "projects")
    os.makedirs(projects_dir, exist_ok=True)

    console = get_console()
    console.print(f"[green]Workspace initialized:[/green] {target}")
    console.print(f"  stx.toml created (name={ws_name!r}, preset={preset!r})")
    console.print("  projects/ directory created")




# ---------------------------------------------------------------------------
# Helpers for clone / link / sync
# ---------------------------------------------------------------------------

def _require_workspace() -> tuple[str, dict]:
    """Find workspace root and load config, or raise ClickException."""
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "Not inside a StreamTeX workspace (no stx.toml found in parent directories)."
        )
    config = load_stx_toml(ws_root)
    return ws_root, config


def _get_dirty_files(repo_path: str) -> list[str]:
    """Return the list of dirty file paths in a git repo."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "--name-only"],
            capture_output=True, text=True, timeout=5,
        )
        tracked = [f for f in result.stdout.strip().splitlines() if f]
        # Also check staged changes
        result_staged = subprocess.run(
            ["git", "-C", repo_path, "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=5,
        )
        staged = [f for f in result_staged.stdout.strip().splitlines() if f]
        # Also check untracked files
        result2 = subprocess.run(
            ["git", "-C", repo_path, "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, timeout=5,
        )
        untracked = [f for f in result2.stdout.strip().splitlines() if f]
        return list(dict.fromkeys(tracked + staged + untracked))
    except (subprocess.TimeoutExpired, OSError):
        return ["(unknown)"]


def _find_uv() -> str:
    """Locate the uv binary."""
    uv = shutil.which("uv")
    if uv is None:
        raise click.ClickException(
            "uv not found in PATH.\n\n"
            "Install uv with one of these commands:\n\n"
            "  curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux\n"
            "  brew install uv                                     # Homebrew\n"
            "  pip install uv                                      # pip\n"
            "  powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"  # Windows\n\n"
            "More info: https://docs.astral.sh/uv/getting-started/installation/"
        )
    return uv


def _has_missing_local_sources(repo_path: str) -> bool:
    """Return True if pyproject.toml has [tool.uv.sources] with local paths that don't exist."""
    pyproject = os.path.join(repo_path, "pyproject.toml")
    import tomllib
    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
    except (OSError, ValueError):
        return False
    sources = data.get("tool", {}).get("uv", {}).get("sources", {})
    for _name, spec in sources.items():
        if isinstance(spec, dict) and "path" in spec:
            resolved = os.path.join(repo_path, spec["path"])
            if not os.path.exists(resolved):
                return True
    return False


def _restore_uv_lock_if_only_dirty(repo_path: str) -> None:
    """Restore uv.lock via ``git checkout`` when it is the only modified file.

    ``uv sync --no-sources`` rewrites uv.lock (replaces local editable paths
    with PyPI versions).  This blocks ``git pull`` because of uncommitted
    changes, even though Step 3 will regenerate the file anyway.

    We only restore when uv.lock is the *sole* dirty file so we never
    discard intentional user edits to other files.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "--name-only"],
            capture_output=True, text=True, timeout=10,
        )
        dirty_files = [f for f in result.stdout.strip().splitlines() if f]
        if dirty_files == ["uv.lock"]:
            subprocess.run(
                ["git", "-C", repo_path, "checkout", "--", "uv.lock"],
                capture_output=True, timeout=10,
            )
    except (subprocess.TimeoutExpired, OSError):
        pass  # best-effort; pull will report the real error if needed


def _depends_on_streamtex(repo_path: str) -> bool:
    """Return True if pyproject.toml lists streamtex as a dependency."""
    import tomllib

    pyproject = os.path.join(repo_path, "pyproject.toml")
    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
    except (OSError, ValueError):
        return False
    deps = data.get("project", {}).get("dependencies", [])
    return any("streamtex" in d for d in deps)


def _collect_sync_targets(
    repos: dict,
    ws_root: str,
    type_filter: set[str] | None = None,
) -> list[tuple[str, str]]:
    """Collect (name, path) pairs for all syncable targets.

    Includes repos from stx.toml AND projects under ``projects/``.
    """
    targets: list[tuple[str, str]] = []

    # 1. Repos from stx.toml
    for repo_name, repo_conf in repos.items():
        repo_type = repo_conf.get("type", "")
        if type_filter and repo_type not in type_filter:
            continue
        repo_path = os.path.join(ws_root, repo_conf.get("path", repo_name))
        if os.path.isdir(repo_path) and os.path.isfile(os.path.join(repo_path, "pyproject.toml")):
            targets.append((repo_name, repo_path))

    # 2. Projects under projects/
    projects_dir = os.path.join(ws_root, "projects")
    if os.path.isdir(projects_dir):
        for entry in sorted(os.listdir(projects_dir)):
            proj_path = os.path.join(projects_dir, entry)
            if (
                os.path.isdir(proj_path)
                and os.path.isfile(os.path.join(proj_path, "pyproject.toml"))
                and not any(name == entry or path == proj_path for name, path in targets)
            ):
                targets.append((f"projects/{entry}", proj_path))

    return targets


def _run_uv_sync(
    repos: dict,
    ws_root: str,
    type_filter: set[str] | None = None,
) -> None:
    """Run ``uv sync`` in selected repos and projects.

    Parameters
    ----------
    repos:
        The ``[repos]`` mapping from stx.toml.
    ws_root:
        Absolute path to the workspace root.
    type_filter:
        If provided, only sync repos whose *type* is in this set.
    """
    uv = _find_uv()
    console = get_console()
    synced = 0
    skipped = 0

    targets = _collect_sync_targets(repos, ws_root, type_filter)

    if not targets:
        console.print("  [yellow]No syncable targets found.[/yellow]")
        return

    for target_name, target_path in targets:
        # Upgrade streamtex in the lock file first (skip for the library itself)
        if _depends_on_streamtex(target_path):
            no_src = _has_missing_local_sources(target_path)
            lock_cmd = [uv, "lock", "--upgrade-package", "streamtex"]
            if no_src:
                lock_cmd.append("--no-sources")
            lock_result = subprocess.run(
                lock_cmd,
                cwd=target_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if lock_result.returncode != 0:
                console.print(f"  [red]{target_name}[/red]: lock upgrade failed")
                if lock_result.stderr:
                    console.print(f"    {lock_result.stderr.strip()}")
                skipped += 1
                continue

        # If local editable sources are missing, fall back to PyPI
        cmd = [uv, "sync"]
        if _has_missing_local_sources(target_path):
            cmd.append("--no-sources")
            console.print(f"  [cyan]{target_name}[/cyan]: running uv sync --no-sources (editable source not found) …")
        else:
            console.print(f"  [cyan]{target_name}[/cyan]: running uv sync …")
        result = subprocess.run(
            cmd,
            cwd=target_path,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            console.print(f"  [green]{target_name}[/green]: ok")
            synced += 1
            # --no-sources rewrites uv.lock (local paths → PyPI).
            # Restore the committed version so the repo stays clean.
            if "--no-sources" in cmd:
                _restore_uv_lock_if_only_dirty(target_path)
        else:
            console.print(f"  [red]{target_name}[/red]: failed")
            if result.stderr:
                console.print(f"    {result.stderr.strip()}")
            skipped += 1

    console.print(f"\n[bold]Done:[/bold] {synced} synced, {skipped} skipped")


# ---------------------------------------------------------------------------
# Shared helper: install global commands
# ---------------------------------------------------------------------------

def _install_global_commands(ws_root: str, config: dict, console) -> None:
    """Copy ``shared/commands/`` to ``~/.claude/commands/`` (read-only)."""
    try:
        from .claude_cmd import find_claude_repo

        claude_repo = find_claude_repo(ws_root, config)
        shared_cmd_dir = os.path.join(claude_repo, "shared", "commands")
        if os.path.isdir(shared_cmd_dir):
            global_claude_cmd = os.path.join(Path.home(), ".claude", "commands")
            os.makedirs(global_claude_cmd, exist_ok=True)
            count = 0
            for fname in os.listdir(shared_cmd_dir):
                src = os.path.join(shared_cmd_dir, fname)
                if os.path.isdir(src):
                    dst_dir = os.path.join(global_claude_cmd, fname)
                    if os.path.exists(dst_dir):
                        # Remove read-only on existing files before overwrite
                        for root, _dirs, files in os.walk(dst_dir):
                            for f in files:
                                os.chmod(os.path.join(root, f), 0o644)
                        shutil.rmtree(dst_dir)
                    shutil.copytree(src, dst_dir)
                    for root, _dirs, files in os.walk(dst_dir):
                        for f in files:
                            os.chmod(os.path.join(root, f), 0o444)
                            count += 1
                elif os.path.isfile(src):
                    dst = os.path.join(global_claude_cmd, fname)
                    # Remove read-only before overwrite
                    if os.path.exists(dst):
                        os.chmod(dst, 0o644)
                    shutil.copy2(src, dst)
                    os.chmod(dst, 0o444)
                    count += 1
            if count:
                console.print(
                    f"  [green]global[/green]: {count} shared command(s) → ~/.claude/commands/"
                )
    except click.ClickException:
        pass  # No claude repo configured/cloned yet — skip silently


def _deprecation_warning(old_cmd: str, new_cmd: str) -> None:
    """Print a deprecation warning directing users to the new command."""
    console = get_console()
    console.print(
        f"\n[yellow]'stx workspace {old_cmd}' is deprecated. "
        f"Use 'stx {new_cmd}' instead.[/yellow]\n"
    )


def _install_precommit_hooks(ws_root: str, config: dict, console, *, dry_run: bool = False) -> None:
    """Install pre-commit hooks in all workspace repos and projects."""
    uv = _find_uv()
    installed = 0
    skipped = 0

    dirs_to_process: list[tuple[str, str]] = []

    for repo_name, repo_conf in config.get("repos", {}).items():
        repo_type = repo_conf.get("type", "")
        if repo_type == "claude":
            continue
        repo_path = os.path.join(ws_root, repo_conf.get("path", repo_name))
        dirs_to_process.append((repo_name, repo_path))

    # Collect paths already added from repos config to avoid duplicates
    known_paths = {os.path.normpath(p) for _, p in dirs_to_process}

    projects_dir = os.path.join(ws_root, "projects")
    if os.path.isdir(projects_dir):
        for entry in sorted(os.listdir(projects_dir)):
            proj_path = os.path.join(projects_dir, entry)
            if os.path.isdir(proj_path) and os.path.isfile(
                os.path.join(proj_path, "pyproject.toml")
            ) and os.path.normpath(proj_path) not in known_paths:
                dirs_to_process.append((f"projects/{entry}", proj_path))

    for name, path in dirs_to_process:
        if not os.path.isdir(path):
            console.print(f"  [yellow]{name}[/yellow]: not found — skipped")
            skipped += 1
            continue

        if not os.path.isfile(os.path.join(path, ".pre-commit-config.yaml")):
            console.print(f"  [yellow]{name}[/yellow]: no .pre-commit-config.yaml — skipped")
            skipped += 1
            continue

        if dry_run:
            console.print(f"  [cyan]{name}[/cyan]: would install hooks")
            installed += 1
            continue

        env = None
        missing_sources = _has_missing_local_sources(path)
        if missing_sources:
            env = {**os.environ, "UV_NO_SOURCES": "1"}

        try:
            result = subprocess.run(
                [uv, "run", "pre-commit", "install"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )
        except subprocess.TimeoutExpired:
            console.print(f"  [yellow]{name}[/yellow]: timed out — skipped")
            skipped += 1
            continue

        if result.returncode == 0:
            console.print(f"  [green]{name}[/green]: ok")
            installed += 1
            # uv run re-syncs implicitly and may dirty uv.lock again
            if missing_sources:
                _restore_uv_lock_if_only_dirty(path)
        else:
            stderr = (result.stderr or "").strip()
            # Detect common failure: local editable source not found
            if "Distribution not found" in stderr or "not found at" in stderr:
                console.print(
                    f"  [yellow]{name}[/yellow]: skipped (editable source not available)"
                )
                console.print(
                    "    [dim]Tip: pre-commit hooks require all dependencies to be resolvable.[/dim]"
                )
                console.print(
                    "    [dim]This is expected in standard/user presets where the library repo is not cloned.[/dim]"
                )
            else:
                console.print(f"  [yellow]{name}[/yellow]: failed")
                if stderr:
                    # Show only the last meaningful line, not the full traceback
                    last_line = stderr.splitlines()[-1]
                    console.print(f"    [dim]{last_line}[/dim]")
            skipped += 1

    console.print(f"  {installed} installed, {skipped} skipped")


def _run_repair_checks(ws_root: str, config: dict, console, *, dry_run: bool = False) -> None:
    """Run repair checks on the workspace."""
    repos = config.get("repos", {})
    issues = 0

    # Collect all directories (repos + projects/)
    dirs: list[tuple[str, str]] = []
    for repo_name, repo_conf in repos.items():
        repo_path = os.path.join(ws_root, repo_conf.get("path", repo_name))
        if os.path.isdir(repo_path):
            dirs.append((repo_name, repo_path))
    projects_dir = os.path.join(ws_root, "projects")
    if os.path.isdir(projects_dir):
        for entry in sorted(os.listdir(projects_dir)):
            proj_path = os.path.join(projects_dir, entry)
            if os.path.isdir(proj_path):
                dirs.append((f"projects/{entry}", proj_path))

    for name, path in dirs:
        # 1. Broken .venv detection
        venv_cfg = os.path.join(path, ".venv", "pyvenv.cfg")
        if os.path.isfile(venv_cfg):
            try:
                with open(venv_cfg, encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("home"):
                            home_path = line.split("=", 1)[1].strip()
                            if not os.path.isdir(home_path):
                                issues += 1
                                if dry_run:
                                    console.print(
                                        f"  [yellow]{name}[/yellow]: broken .venv — would delete"
                                    )
                                else:
                                    shutil.rmtree(os.path.join(path, ".venv"))
                                    console.print(
                                        f"  [green]{name}[/green]: deleted broken .venv"
                                    )
                            break
            except OSError:
                pass

        # 2. Missing custom/__init__.py
        custom_dir = os.path.join(path, "custom")
        custom_init = os.path.join(custom_dir, "__init__.py")
        if os.path.isdir(custom_dir) and not os.path.isfile(custom_init):
            issues += 1
            if dry_run:
                console.print(f"  [yellow]{name}[/yellow]: missing custom/__init__.py — would create")
            else:
                with open(custom_init, "w") as f:
                    f.write("")
                console.print(f"  [green]{name}[/green]: created custom/__init__.py")

        # 3. Missing blocks/__init__.py
        blocks_dir = os.path.join(path, "blocks")
        blocks_init = os.path.join(blocks_dir, "__init__.py")
        if os.path.isdir(blocks_dir) and not os.path.isfile(blocks_init):
            issues += 1
            if dry_run:
                console.print(f"  [yellow]{name}[/yellow]: missing blocks/__init__.py — would create")
            else:
                with open(blocks_init, "w", encoding="utf-8") as f:
                    f.write(
                        "from pathlib import Path\n"
                        "from streamtex import ProjectBlockRegistry\n\n"
                        "registry = ProjectBlockRegistry(Path(__file__).parent)\n"
                    )
                console.print(f"  [green]{name}[/green]: created blocks/__init__.py with ProjectBlockRegistry")

        # 4. Broken [tool.uv.sources] paths
        if _has_missing_local_sources(path):
            issues += 1
            console.print(f"  [yellow]{name}[/yellow]: broken [tool.uv.sources] paths in pyproject.toml")

    if issues == 0:
        console.print("  [green]No issues found.[/green]")


# ---------------------------------------------------------------------------
# Project migrations (applied during stx update)
# ---------------------------------------------------------------------------


def _upgrade_projects(
    repos: dict, ws_root: str, console, *, dry_run: bool = False,
) -> None:
    """Apply pending migrations to all projects in the workspace."""
    from importlib.metadata import version as pkg_version

    from .migrations import detect_project_version, get_pending_migrations
    from .migrations.registry import _version_tuple, write_version_marker

    try:
        installed_ver = pkg_version("streamtex")
    except Exception:
        console.print("  [yellow]Cannot determine installed version — skipped[/yellow]")
        return

    # Collect all project paths (from repos + projects/ directory)
    project_paths: list[tuple[str, str]] = []
    for repo_name, repo_conf in repos.items():
        if repo_conf.get("type") == "project":
            path = os.path.join(ws_root, repo_conf.get("path", repo_name))
            if os.path.isdir(path) and os.path.isfile(os.path.join(path, "pyproject.toml")):
                project_paths.append((repo_name, path))

    projects_dir = os.path.join(ws_root, "projects")
    if os.path.isdir(projects_dir):
        listed = {p for _, p in project_paths}
        for entry in sorted(os.listdir(projects_dir)):
            if entry.startswith(("_", ".")):
                continue
            path = os.path.join(projects_dir, entry)
            if path not in listed and os.path.isfile(os.path.join(path, "pyproject.toml")):
                project_paths.append((entry, path))

    if not project_paths:
        console.print("  No projects found.")
        return

    upgraded = 0
    skipped = 0
    for name, path in project_paths:
        current_ver = detect_project_version(path)
        if _version_tuple(current_ver) >= _version_tuple(installed_ver):
            skipped += 1
            continue

        pending = get_pending_migrations(current_ver, installed_ver)
        if not pending:
            skipped += 1
            continue

        rel = os.path.relpath(path, ws_root)
        console.print(f"  [cyan]{rel}[/cyan]: {len(pending)} migration(s) ({current_ver} → {installed_ver})")

        for migration in pending:
            if migration.check(path):
                result = migration.apply(path, dry_run=dry_run)
                prefix = "[dim](dry-run)[/dim] " if dry_run else ""
                if result.applied:
                    console.print(f"    {prefix}[green]v{result.version}[/green]: {result.description}")
                    for change in result.changes:
                        console.print(f"      - {change}")
                else:
                    console.print(
                        f"    {prefix}[dim]v{result.version}: skipped"
                        f" ({result.skipped_reason})[/dim]"
                    )
            else:
                console.print(f"    [dim]v{migration.version}: already applied[/dim]")

        if not dry_run:
            write_version_marker(path, installed_ver)
        upgraded += 1

    if upgraded:
        console.print(f"\n  {upgraded} upgraded, {skipped} already up to date")
    else:
        console.print("  All projects up to date.")


# ---------------------------------------------------------------------------
# CLI tool upgrade (developer workspaces)
# ---------------------------------------------------------------------------


def _get_source_version(lib_path: str) -> str | None:
    """Read the library version from pyproject.toml (single source of truth)."""
    pyproject = os.path.join(lib_path, "pyproject.toml")
    if os.path.isfile(pyproject):
        try:
            with open(pyproject, encoding="utf-8") as f:
                for line in f:
                    m = re.match(r'^version\s*=\s*"([^"]+)"', line)
                    if m:
                        return m.group(1)
        except OSError:
            pass
    return None


def _get_installed_cli_version() -> str | None:
    """Return the currently installed stx CLI version."""
    try:
        from importlib.metadata import version as pkg_version
        return pkg_version("streamtex")
    except Exception:
        return None


def _upgrade_cli_tool(
    ws_root: str, lib_path: str, console, *, dry_run: bool = False,
) -> None:
    """Reinstall the stx CLI from local source if version differs."""
    source_ver = _get_source_version(lib_path)
    installed_ver = _get_installed_cli_version()

    if not source_ver:
        console.print("  [yellow]Could not read source version — skipped[/yellow]")
        return

    if source_ver == installed_ver:
        console.print(
            f"  CLI [green]{installed_ver}[/green] matches source — "
            "no upgrade needed"
        )
        return

    console.print(
        f"  CLI [yellow]{installed_ver}[/yellow] differs from "
        f"source [cyan]{source_ver}[/cyan]"
    )

    # Detect the Python interpreter used by the existing uv tool environment
    # so we can pass --python and avoid falling back to the system interpreter.
    uv = _find_uv()
    tool_python = None
    try:
        probe = subprocess.run(
            [uv, "tool", "run", "--from", "streamtex[cli]", "python", "--version"],
            capture_output=True, text=True, timeout=15,
        )
        if probe.returncode == 0:
            # Output: "Python 3.11.x" → extract "3.11"
            m = re.match(r"Python (\d+\.\d+)", probe.stdout.strip())
            if m:
                tool_python = m.group(1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    python_flag = f" --python {tool_python}" if tool_python else ""
    if dry_run:
        console.print(
            f'  Would run: uv tool install{python_flag} --force --reinstall "{lib_path}[cli]"'
        )
        return

    console.print("  Reinstalling CLI from local source …")
    cmd = [uv, "tool", "install"]
    if tool_python:
        cmd += ["--python", tool_python]
    cmd += ["--force", "--reinstall", f"{lib_path}[cli]"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 0:
        console.print(
            f"  [green]CLI upgraded: {installed_ver} → {source_ver}[/green]"
        )
    else:
        console.print("  [red]CLI upgrade failed[/red]")
        if result.stderr:
            for line in result.stderr.strip().splitlines()[:5]:
                console.print(f"    {line}")


# ---------------------------------------------------------------------------
# clone / link / sync commands (deprecated — kept for backward compat)
# ---------------------------------------------------------------------------

@click.command(deprecated=True)
def clone():
    """Clone all repos declared in stx.toml. [deprecated: use 'stx workspace update']"""
    _deprecation_warning("clone", "update")
    ws_root, config = _require_workspace()
    repos = config.get("repos", {})

    if not repos:
        console = get_console()
        console.print("[yellow]No repos configured in stx.toml[/yellow]")
        return

    console = get_console()
    cloned = 0
    skipped = 0

    for repo_name, repo_conf in repos.items():
        url = repo_conf.get("url", "")
        rel_path = repo_conf.get("path", repo_name)
        target_path = os.path.join(ws_root, rel_path)

        if not url:
            console.print(f"  [yellow]{repo_name}[/yellow]: no url — skipped")
            skipped += 1
            continue

        if os.path.isdir(target_path):
            console.print(f"  [yellow]{repo_name}[/yellow]: already exists — skipped")
            skipped += 1
            continue

        # Ensure parent directory exists (e.g. projects/)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        console.print(f"  [cyan]{repo_name}[/cyan]: cloning {url} …")
        result = subprocess.run(
            ["git", "clone", url, target_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            console.print(f"  [green]{repo_name}[/green]: cloned")
            cloned += 1
        else:
            console.print(f"  [red]{repo_name}[/red]: clone failed")
            if result.stderr:
                console.print(f"    {result.stderr.strip()}")
            skipped += 1

    # --- Install shared commands globally (~/.claude/commands/) ---
    _install_global_commands(ws_root, config, console)

    console.print(f"\n[bold]Done:[/bold] {cloned} cloned, {skipped} skipped")


@click.command(deprecated=True)
def link():
    """Configure editable installs (uv sync in docs/project repos). [deprecated: use 'stx workspace update']"""
    _deprecation_warning("link", "update")
    ws_root, config = _require_workspace()
    repos = config.get("repos", {})

    console = get_console()
    console.print("[bold]Linking docs & project repos …[/bold]\n")
    _run_uv_sync(repos, ws_root, type_filter={"docs", "project"})


@click.command(deprecated=True)
def sync():
    """Run uv sync in all workspace repos. [deprecated: use 'stx workspace update']"""
    _deprecation_warning("sync", "update")
    ws_root, config = _require_workspace()
    repos = config.get("repos", {})

    console = get_console()
    console.print("[bold]Syncing all repos …[/bold]\n")
    _run_uv_sync(repos, ws_root)


# ---------------------------------------------------------------------------
# update command
# ---------------------------------------------------------------------------

@click.command()
@click.option("--skip-sync", is_flag=True, help="Skip uv sync step.")
@click.option("--skip-profiles", is_flag=True, help="Skip Claude profile update step.")
@click.option("--dry-run", is_flag=True, help="Show steps without executing.")
@click.option("--repair", is_flag=True, help="Run repair checks (broken venv, missing __init__.py).")
@click.option("--force", is_flag=True, help="Overwrite locally modified profile files (backup in .claude/.backup/).")
def update(skip_sync, skip_profiles, dry_run, repair, force):
    """Pull repos, clone missing, sync deps, install hooks, update profiles."""
    ws_root, config = _require_workspace()
    repos = config.get("repos", {})
    console = get_console()

    # Does this workspace have a local library repo? (developer preset)
    _lib_path = None
    for _rn, _rc in repos.items():
        if _rc.get("type") == "library":
            _candidate = os.path.join(ws_root, _rc.get("path", _rn))
            if os.path.isdir(_candidate):
                _lib_path = _candidate
            break
    _needs_cli_upgrade = _lib_path is not None and not skip_sync

    # Dynamic step counter
    total_steps = 7  # pull, clone, sync, migrations, global commands, profiles, hooks
    if skip_sync:
        total_steps -= 2  # skip sync AND migrations (migrations need synced deps)
    if skip_profiles:
        total_steps -= 1
    if repair:
        total_steps += 1
    if _needs_cli_upgrade:
        total_steps += 1
    step = 0

    def _step(label: str) -> None:
        nonlocal step
        step += 1
        console.print(f"\n[bold cyan]Step {step}/{total_steps}:[/bold cyan] {label}\n")

    if dry_run:
        console.print("[bold]Updating workspace (dry run) …[/bold]")
    else:
        console.print("[bold]Updating workspace …[/bold]")

    # --- Detect dev-linked repos (skip pull/clone for these) ---
    _dev_linked: set[str] = set()
    try:
        from .dev_config import resolve_repo_path
        for repo_name in repos:
            try:
                _path, is_dev = resolve_repo_path(repo_name, ws_root, config)
                if is_dev:
                    _dev_linked.add(repo_name)
            except FileNotFoundError:
                pass
    except Exception:
        pass

    # --- git pull existing repos ---
    _step("Pulling latest changes …")
    pulled = 0
    for repo_name, repo_conf in repos.items():
        if repo_name in _dev_linked:
            console.print(
                f"  [cyan]{repo_name}[/cyan]: dev-linked — skip pull"
            )
            pulled += 1
            continue

        rel_path = repo_conf.get("path", repo_name)
        repo_path = os.path.join(ws_root, rel_path)

        if not os.path.isdir(repo_path):
            continue

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            console.print(f"  [yellow]{repo_name}[/yellow]: not a git repo — skipped")
            continue

        if dry_run:
            console.print(f"  [cyan]{repo_name}[/cyan]: would git pull")
            pulled += 1
            continue

        # Safety: skip repos with uncommitted changes (except uv.lock-only)
        dirty = _get_dirty_files(repo_path)
        if dirty and dirty != ["uv.lock"]:
            file_list = ", ".join(dirty[:5])
            if len(dirty) > 5:
                file_list += f" (+{len(dirty) - 5} more)"
            console.print(
                f"  [yellow]{repo_name}[/yellow]: skipped pull"
                f" — uncommitted changes: {file_list}"
            )
            console.print(
                "    [dim]Commit or stash changes, then re-run stx update.[/dim]"
            )
            continue

        console.print(f"  [cyan]{repo_name}[/cyan]: git pull …")

        # If uv.lock is the only dirty file, restore it before pulling.
        # uv sync --no-sources rewrites uv.lock (replaces local paths with PyPI),
        # but git pull needs a clean tree.  Step 3 will regenerate it anyway.
        _restore_uv_lock_if_only_dirty(repo_path)

        result = subprocess.run(
            ["git", "-C", repo_path, "pull", "--ff-only"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if "Already up to date" in output:
                console.print(f"  [green]{repo_name}[/green]: already up to date")
            else:
                console.print(f"  [green]{repo_name}[/green]: updated")
            pulled += 1
        else:
            console.print(f"  [red]{repo_name}[/red]: pull failed")
            if result.stderr:
                console.print(f"    {result.stderr.strip()}")

    # --- clone missing repos (skip dev-linked) ---
    missing = []
    for repo_name, repo_conf in repos.items():
        if repo_name in _dev_linked:
            continue
        rel_path = repo_conf.get("path", repo_name)
        target_path = os.path.join(ws_root, rel_path)
        url = repo_conf.get("url", "")
        if url and not os.path.isdir(target_path):
            missing.append((repo_name, url, target_path))

    _step(f"Cloning {len(missing)} missing repo(s) …")
    if missing:
        for repo_name, url, target_path in missing:
            if dry_run:
                console.print(f"  [cyan]{repo_name}[/cyan]: would clone {url}")
                continue
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            console.print(f"  [cyan]{repo_name}[/cyan]: cloning {url} …")
            result = subprocess.run(
                ["git", "clone", url, target_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                console.print(f"  [green]{repo_name}[/green]: cloned")
            else:
                console.print(f"  [red]{repo_name}[/red]: clone failed")
                if result.stderr:
                    console.print(f"    {result.stderr.strip()}")
    else:
        console.print("  No missing repos.")

    # --- uv sync ---
    if not skip_sync:
        _step("Syncing dependencies …")
        if dry_run:
            for target_name, target_path in _collect_sync_targets(repos, ws_root):
                upgrade = " (+ upgrade streamtex)" if _depends_on_streamtex(target_path) else ""
                console.print(f"  [cyan]{target_name}[/cyan]: would uv sync{upgrade}")
        else:
            _run_uv_sync(repos, ws_root)

    # --- project migrations ---
    if not skip_sync:
        _step("Upgrading projects …")
        _upgrade_projects(repos, ws_root, console, dry_run=dry_run)

    # --- install global commands ---
    _step("Installing global commands …")
    if dry_run:
        console.print("  Would install shared commands → ~/.claude/commands/")
    else:
        _install_global_commands(ws_root, config, console)

    # --- update Claude profiles ---
    if not skip_profiles:
        _step("Updating Claude profiles …")
        if dry_run:
            console.print("  Would update all Claude profiles")
        else:
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
                        console.print(f"  [bold cyan]── {rel} [/bold cyan]([cyan]{profile}[/cyan])")
                        _update_single_target(claude_repo, profile, target_path, force, console)
                else:
                    console.print("  [yellow]No projects with Claude profiles found.[/yellow]")
            except click.ClickException:
                console.print("  [yellow]Claude repo not available — skipped.[/yellow]")

    # --- install pre-commit hooks ---
    _step("Installing pre-commit hooks …")
    _install_precommit_hooks(ws_root, config, console, dry_run=dry_run)

    # --- CLI tool upgrade (developer only) ---
    if _needs_cli_upgrade:
        _step("Checking CLI tool version …")
        _upgrade_cli_tool(ws_root, _lib_path, console, dry_run=dry_run)

    # --- repair checks ---
    if repair:
        _step("Running repair checks …")
        _run_repair_checks(ws_root, config, console, dry_run=dry_run)

    console.print("\n[bold green]Workspace update complete.[/bold green]")


# ---------------------------------------------------------------------------
# upgrade command
# ---------------------------------------------------------------------------

@click.command()
@click.argument("preset", type=click.Choice(PRESET_ORDER))
def upgrade(preset):
    """Upgrade workspace to a higher preset."""
    ws_root, config = _require_workspace()
    console = get_console()

    # Current preset — backwards compat: missing field → "developer"
    current = config.get("workspace", {}).get("preset", "developer")
    current_idx = PRESET_ORDER.index(current) if current in PRESET_ORDER else len(PRESET_ORDER) - 1
    new_idx = PRESET_ORDER.index(preset)

    if new_idx < current_idx:
        raise click.ClickException(
            f"Cannot downgrade from '{current}' to '{preset}'."
        )

    if new_idx == current_idx:
        console.print(f"[yellow]Already at preset '{current}'.[/yellow]")
        return

    # Repos to add
    current_repos = set(PRESET_REPOS.get(current, []))
    new_repos = set(PRESET_REPOS[preset])
    to_add = new_repos - current_repos

    # Rewrite stx.toml
    toml_path = os.path.join(ws_root, "stx.toml")
    with open(toml_path, encoding="utf-8") as f:
        text = f.read()

    # Update preset line
    if re.search(r'^preset\s*=', text, re.MULTILINE):
        text = re.sub(
            r'^(preset\s*=\s*).*$',
            f'preset = "{preset}"',
            text,
            flags=re.MULTILINE,
        )
    else:
        # Insert preset after created line in [workspace]
        text = re.sub(
            r'^(created\s*=\s*".+")$',
            f'\\1\npreset = "{preset}"',
            text,
            flags=re.MULTILINE,
        )

    # Add missing repo sections before [deploy]
    if to_add:
        new_sections = []
        for repo_key in PRESET_REPOS[preset]:
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

    console.print(f"[green]Upgraded from '{current}' to '{preset}'.[/green]")
    for repo_key in sorted(to_add):
        console.print(f"  + {ALL_REPOS[repo_key]['name']}")
    console.print("\nRun [bold]stx update[/bold] to clone the new repos.")


# ---------------------------------------------------------------------------
# hooks command
# ---------------------------------------------------------------------------

@click.command(deprecated=True)
def hooks():
    """Install pre-commit hooks in all workspace repos and projects. [deprecated: use 'stx workspace update']"""
    _deprecation_warning("hooks", "update")
    ws_root, config = _require_workspace()
    console = get_console()

    console.print("[bold]Installing pre-commit hooks …[/bold]\n")
    _install_precommit_hooks(ws_root, config, console)
