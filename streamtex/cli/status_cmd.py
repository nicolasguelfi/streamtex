"""Enhanced status command: comprehensive StreamTeX environment diagnostic."""

import json as _json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field

import click

from .console import get_console
from .workspace_cmd import (
    _get_dirty_files,
    find_workspace_root,
    get_repo_status,
    load_stx_toml,
)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Recommendation:
    level: str  # "info", "warning", "error"
    message: str
    command: str = ""


@dataclass
class RepoInfo:
    name: str
    path: str
    branch: str = "?"
    clean: bool = True
    ahead: int = 0
    behind: int = 0
    dirty_files: list[str] = field(default_factory=list)
    cloned: bool = True
    repo_type: str = ""


@dataclass
class ProjectInfo:
    name: str
    path: str
    stx_dep: str = ""
    has_editable_source: bool = False


@dataclass
class StatusReport:
    # Environment
    python_version: str = ""
    python_path: str = ""
    uv_version: str = ""
    uv_path: str = ""
    platform_info: str = ""
    venv_status: str = ""  # "active", "inactive", "wrong"
    venv_path: str = ""
    conda_env: str = ""

    # Versions
    cli_version: str = ""
    installed_version: str = ""
    install_type: str = ""  # "tool", "editable", "venv", "unknown"
    install_location: str = ""
    pypi_version: str | None = None
    source_version: str | None = None
    source_path: str | None = None

    # Workspace
    workspace_name: str | None = None
    workspace_root: str | None = None
    workspace_preset: str | None = None

    # Repos and projects
    repos: list[RepoInfo] = field(default_factory=list)
    projects: list[ProjectInfo] = field(default_factory=list)

    # Recommendations
    recommendations: list[Recommendation] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Data collection helpers
# ---------------------------------------------------------------------------


def _get_environment_info(report: StatusReport) -> None:
    """Populate environment fields."""
    report.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    report.python_path = sys.executable
    report.platform_info = f"{platform.system()} {platform.release()} ({platform.machine()})"

    # uv
    uv = shutil.which("uv")
    if uv:
        report.uv_path = uv
        try:
            result = subprocess.run(
                [uv, "--version"], capture_output=True, text=True, timeout=5,
            )
            # output is like "uv 0.6.12 (abcdef 2026-03-15)"
            report.uv_version = result.stdout.strip().split()[1] if result.returncode == 0 else "?"
        except (subprocess.TimeoutExpired, OSError, IndexError):
            report.uv_version = "?"


def _detect_venv_status(report: StatusReport, ws_root: str | None) -> None:
    """Detect virtual environment activation state."""
    # Check conda
    conda_env = os.environ.get("CONDA_DEFAULT_ENV", "")
    if conda_env:
        report.conda_env = conda_env

    # Check VIRTUAL_ENV
    venv_env = os.environ.get("VIRTUAL_ENV", "")

    if venv_env:
        report.venv_path = venv_env
        report.venv_status = "active"
        # Check if it's the workspace .venv
        if ws_root:
            if not os.path.realpath(venv_env).startswith(os.path.realpath(ws_root)):
                report.venv_status = "wrong"
    elif ws_root and os.path.isdir(os.path.join(ws_root, ".venv")):
        report.venv_path = os.path.join(ws_root, ".venv")
        report.venv_status = "inactive"
    else:
        report.venv_status = "none"


def _detect_install_type(report: StatusReport) -> None:
    """Detect how streamtex is installed (tool, editable, venv, unknown)."""
    import importlib.metadata

    # CLI version (the stx binary itself)
    try:
        report.cli_version = importlib.metadata.version("streamtex")
    except importlib.metadata.PackageNotFoundError:
        report.cli_version = "?"

    report.installed_version = report.cli_version

    try:
        dist = importlib.metadata.distribution("streamtex")
    except importlib.metadata.PackageNotFoundError:
        report.install_type = "unknown"
        return

    # Method 1: PEP 610 direct_url.json (detects editable installs)
    try:
        direct_url_text = dist.read_text("direct_url.json")
        if direct_url_text:
            data = _json.loads(direct_url_text)
            if data.get("dir_info", {}).get("editable", False):
                location = data.get("url", "").replace("file://", "")
                report.install_type = "editable"
                report.install_location = location
                return
    except Exception:
        pass

    # Method 2: Check if stx binary is a uv tool install
    # uv tool installs go to ~/.local/bin/ (symlink) or ~/.local/share/uv/tools/
    stx_bin = shutil.which("stx")
    if stx_bin:
        home = os.path.expanduser("~")
        # Check both the symlink path and the resolved real path
        for check_path in [stx_bin, os.path.realpath(stx_bin)]:
            if (os.path.join(home, ".local", "bin") in check_path
                    or os.path.join(home, ".local", "share", "uv", "tools") in check_path):
                report.install_type = "tool"
                report.install_location = "~/.local/bin/stx"
                return

    # Method 3: Check if in a .venv
    if ".venv" in (sys.prefix or ""):
        report.install_type = "venv"
        report.install_location = sys.prefix
        return

    report.install_type = "unknown"
    report.install_location = str(getattr(dist, "_path", ""))


def _fetch_pypi_version() -> str | None:
    """Fetch the latest streamtex version from PyPI. Returns None on failure."""
    import urllib.request

    try:
        url = "https://pypi.org/pypi/streamtex/json"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = _json.loads(resp.read())
            return data["info"]["version"]
    except Exception:
        return None


def _get_source_version(ws_root: str, config: dict) -> tuple[str | None, str | None]:
    """Read version from local library source. Returns (version, path) or (None, None)."""
    repos = config.get("repos", {})
    for _repo_name, repo_conf in repos.items():
        if repo_conf.get("type") == "library":
            lib_path = os.path.join(ws_root, repo_conf.get("path", _repo_name))
            # Try __init__.py
            init_file = os.path.join(lib_path, "streamtex", "__init__.py")
            if os.path.isfile(init_file):
                try:
                    with open(init_file, encoding="utf-8") as f:
                        content = f.read()
                    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return (match.group(1), lib_path)
                except OSError:
                    pass
            # Fallback: pyproject.toml
            pyproject = os.path.join(lib_path, "pyproject.toml")
            if os.path.isfile(pyproject):
                try:
                    import tomllib

                    with open(pyproject, "rb") as f:
                        data = tomllib.load(f)
                    ver = data.get("project", {}).get("version")
                    if ver:
                        return (ver, lib_path)
                except (OSError, ValueError):
                    pass
    return (None, None)


def _get_repos_info(report: StatusReport, ws_root: str, config: dict) -> None:
    """Populate repo status information."""
    repos = config.get("repos", {})
    for repo_name, repo_conf in repos.items():
        repo_path = os.path.join(ws_root, repo_conf.get("path", repo_name))
        ri = RepoInfo(
            name=repo_name,
            path=repo_path,
            repo_type=repo_conf.get("type", ""),
        )
        if not os.path.isdir(repo_path):
            ri.cloned = False
            report.repos.append(ri)
            continue
        info = get_repo_status(repo_path)
        ri.branch = info["branch"]
        ri.clean = info["clean"]
        ri.ahead = info["ahead"]
        ri.behind = info["behind"]
        if not info["clean"]:
            ri.dirty_files = _get_dirty_files(repo_path)
        report.repos.append(ri)


def _get_projects_info(report: StatusReport, ws_root: str, config: dict) -> None:
    """Scan projects for their streamtex dependency spec."""
    import tomllib

    # Collect project paths from stx.toml repos (type=project)
    project_paths: list[tuple[str, str]] = []
    repos = config.get("repos", {})
    for repo_name, repo_conf in repos.items():
        if repo_conf.get("type") == "project":
            path = os.path.join(ws_root, repo_conf.get("path", repo_name))
            project_paths.append((repo_name, path))

    # Also scan projects/ directory for unlisted projects
    projects_dir = os.path.join(ws_root, "projects")
    if os.path.isdir(projects_dir):
        listed_paths = {p for _, p in project_paths}
        for entry in sorted(os.listdir(projects_dir)):
            if entry.startswith(("_", ".")):
                continue
            proj_path = os.path.join(projects_dir, entry)
            if proj_path not in listed_paths and os.path.isdir(proj_path):
                pyproject = os.path.join(proj_path, "pyproject.toml")
                if os.path.isfile(pyproject):
                    project_paths.append((entry, proj_path))

    for name, path in project_paths:
        pyproject = os.path.join(path, "pyproject.toml")
        if not os.path.isfile(pyproject):
            continue
        try:
            with open(pyproject, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            continue

        deps = data.get("project", {}).get("dependencies", [])
        stx_dep = next((d for d in deps if "streamtex" in d), "")

        sources = data.get("tool", {}).get("uv", {}).get("sources", {})
        stx_source = sources.get("streamtex", {})
        has_editable = bool(stx_source.get("path"))

        report.projects.append(ProjectInfo(
            name=name,
            path=path,
            stx_dep=stx_dep,
            has_editable_source=has_editable,
        ))


def _version_tuple(v: str) -> tuple[int, ...]:
    """Convert '0.5.11' to (0, 5, 11) for comparison."""
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


# ---------------------------------------------------------------------------
# Recommendation engine
# ---------------------------------------------------------------------------


def _rel(path: str) -> str:
    """Return a short relative path for display, or the original if it fails."""
    try:
        return os.path.relpath(path, os.getcwd())
    except ValueError:
        return path


def _build_recommendations(report: StatusReport) -> None:
    """Analyze the report and generate actionable recommendations."""
    recs = report.recommendations

    # 1. uv not found
    if not report.uv_path:
        recs.append(Recommendation(
            "error",
            "uv is not installed — required for StreamTeX",
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
        ))

    # 2. Wrong Python version
    if sys.version_info < (3, 11):
        recs.append(Recommendation(
            "error",
            f"Python {report.python_version} detected — StreamTeX requires >= 3.11",
            "uv python install 3.13",
        ))

    # 3. Conda / venv informational notes
    # stx commands and `uv run` auto-activate the correct project venv,
    # so a missing venv activation is only a problem for direct python/pytest calls.
    if report.conda_env and report.venv_status != "active":
        note = f"conda '{report.conda_env}' is active"
        if report.venv_status == "inactive":
            note += " and project .venv is not activated"
        recs.append(Recommendation(
            "info",
            f"{note} — stx commands use the correct venv automatically, "
            "but direct python/pytest calls will use conda instead",
            "conda deactivate && source .venv/bin/activate  (only needed for direct python calls)",
        ))
    elif report.venv_status == "inactive" and not report.conda_env:
        recs.append(Recommendation(
            "info",
            "Project .venv exists but is not activated — stx commands work fine, "
            "but direct python/pytest calls may use the wrong environment",
            "source .venv/bin/activate  (only needed for direct python calls)",
        ))
    elif report.venv_status == "wrong":
        recs.append(Recommendation(
            "warning",
            f"Active venv ({report.venv_path}) does not belong to this workspace "
            "— direct python calls will use the wrong packages",
            "deactivate && source .venv/bin/activate",
        ))

    # 6. CLI behind PyPI
    if report.pypi_version and report.cli_version and report.cli_version != "?":
        if _version_tuple(report.pypi_version) > _version_tuple(report.cli_version):
            if report.install_type == "tool":
                cmd = 'uv tool upgrade "streamtex[cli]"'
            else:
                cmd = "uv add streamtex --upgrade"
            recs.append(Recommendation(
                "warning",
                f"Installed {report.cli_version}, PyPI has {report.pypi_version}",
                cmd,
            ))

    # 7. Source version != CLI version (developer mismatch)
    if report.source_version and report.cli_version and report.cli_version != "?":
        if report.source_version != report.cli_version:
            src = _rel(report.source_path)
            if report.install_type == "tool":
                recs.append(Recommendation(
                    "warning",
                    f"CLI is {report.cli_version} but source is {report.source_version}"
                    " — CLI not in sync with local source",
                    f'uv tool install --force "{src}[cli]"',
                ))
            else:
                recs.append(Recommendation(
                    "info",
                    f"Installed {report.cli_version}, source is {report.source_version}",
                    f"uv sync --directory {src}",
                ))

    # 8. Repo issues
    for repo in report.repos:
        if not repo.cloned:
            recs.append(Recommendation(
                "info",
                f"{repo.name}: not cloned",
                "stx update",
            ))
        elif not repo.clean:
            if repo.dirty_files == ["uv.lock"]:
                recs.append(Recommendation(
                    "info",
                    f"{repo.name}: uv.lock modified locally (auto-fixed by stx update)",
                    "stx update",
                ))
            else:
                file_list = ", ".join(repo.dirty_files[:3])
                if len(repo.dirty_files) > 3:
                    file_list += f" (+{len(repo.dirty_files) - 3} more)"
                recs.append(Recommendation(
                    "warning",
                    f"{repo.name}: uncommitted changes ({file_list})",
                    "commit or stash before running stx update",
                ))
        if repo.behind:
            recs.append(Recommendation(
                "info",
                f"{repo.name}: {repo.behind} commit(s) behind remote",
                "stx update",
            ))
        if repo.ahead:
            recs.append(Recommendation(
                "info",
                f"{repo.name}: {repo.ahead} commit(s) ahead of remote",
                f"cd {repo.name} && git push",
            ))

    # 9. Projects with pending migrations
    installed = report.installed_version if report.installed_version != "?" else report.pypi_version
    if installed:
        try:
            from .migrations import detect_project_version, get_pending_migrations
        except ImportError:
            detect_project_version = None
            get_pending_migrations = None

        if detect_project_version and get_pending_migrations:
            for proj in report.projects:
                proj_ver = detect_project_version(proj.path)
                pending = get_pending_migrations(proj_ver, installed)
                if pending:
                    desc_list = ", ".join(m.description for m in pending[:3])
                    recs.append(Recommendation(
                        "info",
                        f"{proj.name}: {len(pending)} pending migration(s) "
                        f"from {proj_ver} ({desc_list})",
                        f"stx project upgrade {_rel(proj.path)}",
                    ))

    # 10. No workspace detected
    if report.workspace_root is None:
        recs.append(Recommendation(
            "info",
            "Not inside a StreamTeX workspace",
            "stx install",
        ))


# ---------------------------------------------------------------------------
# Output renderers
# ---------------------------------------------------------------------------


def _print_rich(report: StatusReport) -> None:
    """Render the status report with Rich formatting."""
    from rich.table import Table

    console = get_console()

    console.print()
    console.print("[bold]StreamTeX Status[/bold]")
    console.print("[dim]" + "=" * 50 + "[/dim]")

    # --- Environment ---
    console.print("\n[bold cyan]Environment[/bold cyan]")
    console.print(f"  Python:    {report.python_version}  [dim]({report.python_path})[/dim]")
    if report.uv_path:
        console.print(f"  uv:        {report.uv_version}  [dim]({report.uv_path})[/dim]")
    else:
        console.print("  uv:        [red]not found[/red]")
    console.print(f"  Platform:  {report.platform_info}")

    # Venv status
    if report.venv_status == "active":
        console.print(f"  Venv:      [green]active[/green]  [dim]({report.venv_path})[/dim]")
    elif report.venv_status == "inactive":
        console.print(f"  Venv:      [yellow]not activated[/yellow]  [dim]({report.venv_path} exists)[/dim]")
    elif report.venv_status == "wrong":
        console.print(f"  Venv:      [red]wrong venv active[/red]  [dim]({report.venv_path})[/dim]")
    elif report.venv_status == "none":
        console.print("  Venv:      [dim]none[/dim]")

    if report.conda_env:
        console.print(f"  Conda:     [yellow]{report.conda_env}[/yellow]")

    # --- Versions ---
    console.print("\n[bold cyan]Versions[/bold cyan]")

    install_labels = {"tool": "tool install", "editable": "editable", "venv": "venv", "unknown": "?"}
    loc = ""
    if report.install_location:
        loc = f"  [dim]({install_labels.get(report.install_type, '?')}: {report.install_location})[/dim]"
    console.print(f"  Installed:   {report.installed_version}{loc}")

    if report.source_version is not None:
        rel_path = report.source_path
        if report.workspace_root and report.source_path:
            try:
                rel_path = os.path.relpath(report.source_path, os.getcwd())
            except ValueError:
                pass
        console.print(f"  Source:      {report.source_version}  [dim]({rel_path})[/dim]")

    if report.pypi_version is not None:
        if report.pypi_version == report.installed_version:
            console.print(f"  PyPI:        {report.pypi_version}  [green]up to date[/green]")
        elif _version_tuple(report.pypi_version) > _version_tuple(report.installed_version):
            console.print(f"  PyPI:        {report.pypi_version}  [yellow]update available[/yellow]")
        else:
            console.print(f"  PyPI:        {report.pypi_version}  [green]up to date[/green]")
    else:
        console.print("  PyPI:        [dim]check failed (offline?)[/dim]")

    # --- Workspace ---
    if report.workspace_root:
        console.print(
            f"\n[bold cyan]Workspace:[/bold cyan] {report.workspace_name}"
            f"  [dim](preset: {report.workspace_preset})[/dim]"
        )
        console.print(f"  [dim]{report.workspace_root}[/dim]")
    else:
        console.print("\n[bold cyan]Workspace:[/bold cyan] [dim]not detected (no stx.toml found)[/dim]")

    # --- Repos ---
    if report.repos:
        console.print()
        table = Table(title="Repositories", title_style="bold cyan")
        table.add_column("Repo", style="cyan")
        table.add_column("Type", style="dim")
        table.add_column("Branch", style="green")
        table.add_column("Status")
        table.add_column("Ahead/Behind")

        for repo in report.repos:
            if not repo.cloned:
                table.add_row(repo.name, repo.repo_type, "-", "[red]not cloned[/red]", "-")
                continue
            status_text = "[green]clean[/green]" if repo.clean else "[red]dirty[/red]"
            ab = f"+{repo.ahead}/-{repo.behind}" if repo.ahead or repo.behind else "-"
            table.add_row(repo.name, repo.repo_type, repo.branch, status_text, ab)

        console.print(table)

    # --- Projects ---
    if report.projects:
        console.print()
        table = Table(title="Projects", title_style="bold cyan")
        table.add_column("Project", style="cyan")
        table.add_column("Requires")
        table.add_column("Source")

        for proj in report.projects:
            source = "[green]editable[/green]" if proj.has_editable_source else "PyPI"
            table.add_row(proj.name, proj.stx_dep or "[dim]-[/dim]", source)

        console.print(table)

    # --- Recommendations ---
    if report.recommendations:
        console.print("\n[bold cyan]Recommendations[/bold cyan]")
        icons = {"info": "[blue]i[/blue]", "warning": "[yellow]![/yellow]", "error": "[red]X[/red]"}
        for rec in report.recommendations:
            icon = icons.get(rec.level, "?")
            console.print(f"  {icon} {rec.message}")
            if rec.command:
                console.print(f"    [bold]-> {rec.command}[/bold]")
    else:
        console.print("\n[green]No issues detected.[/green]")

    console.print()


def _print_json(report: StatusReport) -> None:
    """Render the status report as JSON."""
    data = asdict(report)
    click.echo(_json.dumps(data, indent=2, default=str))


# ---------------------------------------------------------------------------
# Click command
# ---------------------------------------------------------------------------


@click.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON (for scripts).")
def status(as_json):
    """Show a comprehensive diagnostic of the StreamTeX environment."""
    report = StatusReport()

    # 1. Environment (always)
    _get_environment_info(report)

    # 2. Workspace detection (best-effort)
    ws_root = find_workspace_root()
    config = None
    if ws_root:
        try:
            config = load_stx_toml(ws_root)
            report.workspace_root = ws_root
            report.workspace_name = config.get("workspace", {}).get("name")
            report.workspace_preset = config.get("workspace", {}).get("preset")
        except Exception:
            pass

    # 3. Venv detection
    _detect_venv_status(report, ws_root)

    # 4. Version info
    _detect_install_type(report)
    report.pypi_version = _fetch_pypi_version()
    if ws_root and config:
        report.source_version, report.source_path = _get_source_version(ws_root, config)

    # 5. Repos (if in workspace)
    if ws_root and config:
        _get_repos_info(report, ws_root, config)
        _get_projects_info(report, ws_root, config)

    # 6. Recommendations
    _build_recommendations(report)

    # 7. Output
    if as_json:
        _print_json(report)
    else:
        _print_rich(report)
