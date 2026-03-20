"""Project commands: new and validate."""

import os
import shutil
import subprocess
from dataclasses import dataclass

import click

from .console import get_console
from .workspace_cmd import find_workspace_root

# ---------------------------------------------------------------------------
# Template generators (pure functions)
# ---------------------------------------------------------------------------


def generate_book_py(name: str) -> str:
    """Generate a standard book.py for a StreamTeX project."""
    return f"""\
\"\"\"StreamTeX project: {name}.\"\"\"

import streamlit as st
from importlib.resources import files as pkg_files

import streamtex as stx
from streamtex import st_book, TOCConfig, NumberingMode, MarkerConfig, BannerConfig, PdfConfig, ExportConfig, ExportMode

from blocks import registry

_logo = str(pkg_files("streamtex.static").joinpath("logo-stx.png"))
st.set_page_config(page_title="{name}", page_icon=_logo, layout="wide", initial_sidebar_state="expanded")

# Table of Contents — numbered headings in sidebar only, up to level 2
toc = TOCConfig(
    numbering=NumberingMode.SIDEBAR_ONLY,
    toc_position=None,
    sidebar_max_level=2,
    search=True,
)

# Marker navigation (PageUp/PageDown)
marker_config = MarkerConfig(
    auto_marker_on_toc=1,
    next_keys=["PageDown"],
    prev_keys=["PageUp"],
)

st_book(
    registry,
    title="{name}",
    toc_config=toc,
    marker_config=marker_config,
    paginate=True,
    banner=BannerConfig.full(),
    # pdf_config=PdfConfig(format="A4", landscape=True, page_numbers=True),
    # Auto-export to disk (disabled by default — change NEVER to ALWAYS to enable)
    exports=[
        ExportConfig(
            format="html",
            mode=ExportMode.NEVER,
            output_dir="./exports",
            filename="{name}",
            timestamp=True,
        ),
        ExportConfig(
            format="pdf",
            mode=ExportMode.NEVER,
            output_dir="./exports",
            filename="{name}",
            timestamp=True,
            pdf=PdfConfig(format="A4", landscape=True),
        ),
    ],
)
"""


def generate_collection_book_py(name: str) -> str:
    """Generate a collection-mode book.py using st_collection."""
    return f"""\
\"\"\"StreamTeX collection: {name}.\"\"\"

import streamlit as st
from importlib.resources import files as pkg_files

from streamtex import st_collection

_logo = str(pkg_files("streamtex.static").joinpath("logo-stx.png"))
st.set_page_config(page_title="{name}", page_icon=_logo, layout="wide", initial_sidebar_state="expanded")

st_collection(
    "{name}",
    config_path="collection.toml",
)
"""


def generate_blocks_init() -> str:
    """Generate blocks/__init__.py with ProjectBlockRegistry."""
    return """\
\"\"\"Block registry for this project.\"\"\"

from streamtex.blocks import ProjectBlockRegistry

registry = ProjectBlockRegistry(__file__)
"""


def generate_block_hello() -> str:
    """Generate a starter block: blocks/bck_hello.py."""
    return """\
\"\"\"Hello block — starter template.\"\"\"

from streamtex import st_write, st_slide_break, st_space


def build():
    \"\"\"Render this block.\"\"\"
    st_write("Hello from StreamTeX!")
    st_space("v", 1)
    st_write("Use st_slide_break() to separate presentation sections:")

    st_slide_break()

    st_write("This section appears after a slide break.")
    st_write("PageDown will stop here during presentations.")
"""


def generate_custom_styles() -> str:
    """Generate custom/styles.py with Styles class."""
    return """\
\"\"\"Custom styles for this project.\"\"\"

from streamtex.styles import StxStyles


class Styles(StxStyles):
    \"\"\"Project-specific styles.\"\"\"
"""


def generate_streamlit_config() -> str:
    """Generate .streamlit/config.toml."""
    return """\
[server]
enableStaticServing = true
fileWatcherType = "poll"
runOnSave = true

[theme]
base = "dark"
"""


def generate_pyproject_toml(name: str, extras: list[str] | None = None) -> str:
    """Generate pyproject.toml for a StreamTeX project.

    Parameters
    ----------
    name:
        Project name.
    extras:
        Optional list of streamtex extras (e.g. ``["pdf", "ai", "inspector"]``).
        When provided, the streamtex dependency becomes ``streamtex[pdf,ai,inspector]>=0.3.0``.
    """
    if extras:
        extras_str = ",".join(extras)
        stx_dep = f'"streamtex[{extras_str}]>=0.3.0"'
    else:
        stx_dep = '"streamtex>=0.3.0"'

    return f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "StreamTeX project: {name}"
requires-python = ">=3.11"
dependencies = [
    {stx_dep},
    "streamlit>=1.54.0",
]

[dependency-groups]
dev = ["pytest>=7.0", "ruff>=0.4.0", "pre-commit>=3.0"]

[tool.uv]
default-groups = ["dev"]

[tool.ruff.lint]
ignore = ["F403", "F405", "E701", "E741"]

[tool.pyright]
extraPaths = [".."]
"""


def generate_setup_py(name: str) -> str:
    """Generate a docstring-only setup.py."""
    return f"""\
\"\"\"Setup for {name} project.\"\"\"
"""


def generate_gitignore() -> str:
    """Generate a .gitignore for StreamTeX projects."""
    return """\
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
build/
.ruff_cache/
"""


def generate_pre_commit_config() -> str:
    """Generate .pre-commit-config.yaml for a StreamTeX project."""
    return """\
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.2
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
"""


def generate_collection_toml(name: str) -> str:
    """Generate a collection.toml for --collection mode."""
    return f"""\
[collection]
name = "{name}"

# [[projects]]
# name = "project-1"
# port = 8501
# url = "http://localhost:8501"
"""


# ---------------------------------------------------------------------------
# Scaffold function
# ---------------------------------------------------------------------------


def scaffold_project(
    target_dir: str,
    name: str,
    *,
    collection: bool = False,
    extras: list[str] | None = None,
) -> list[str]:
    """Create all scaffold files. Return the list of relative paths created.

    Parameters
    ----------
    extras:
        Optional list of streamtex extras to include in pyproject.toml
        (e.g. ``["pdf", "ai", "inspector"]``).
    """
    created: list[str] = []

    def _write(rel_path: str, content: str) -> None:
        full = os.path.join(target_dir, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        created.append(rel_path)

    # book.py
    if collection:
        _write("book.py", generate_collection_book_py(name))
    else:
        _write("book.py", generate_book_py(name))

    # blocks/
    _write("blocks/__init__.py", generate_blocks_init())
    _write("blocks/bck_hello.py", generate_block_hello())

    # custom/
    _write("custom/__init__.py", "")
    _write("custom/styles.py", generate_custom_styles())

    # .streamlit/
    _write(".streamlit/config.toml", generate_streamlit_config())

    # Root files
    _write("pyproject.toml", generate_pyproject_toml(name, extras=extras))
    _write("setup.py", generate_setup_py(name))
    _write(".gitignore", generate_gitignore())
    _write(".pre-commit-config.yaml", generate_pre_commit_config())

    # static/images/ (empty directory)
    images_dir = os.path.join(target_dir, "static", "images")
    os.makedirs(images_dir, exist_ok=True)

    # collection.toml (only in collection mode)
    if collection:
        _write("collection.toml", generate_collection_toml(name))

    return created


# ---------------------------------------------------------------------------
# Workspace detection
# ---------------------------------------------------------------------------


def resolve_project_dir(name: str) -> str:
    """Determine target directory for a new project.

    If inside a workspace with ``projects/``, use ``projects/<name>/``.
    Otherwise, use ``./<name>/``.

    Raises:
        click.ClickException: if the target directory already exists.
    """
    dir_name = name

    ws_root = find_workspace_root()
    if ws_root is not None:
        projects_dir = os.path.join(ws_root, "projects")
        if os.path.isdir(projects_dir):
            target = os.path.join(projects_dir, dir_name)
            if os.path.isdir(target):
                raise click.ClickException(f"Directory already exists: {target}")
            return target

    target = os.path.join(os.getcwd(), dir_name)
    if os.path.isdir(target):
        raise click.ClickException(f"Directory already exists: {target}")
    return target


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass
class ValidationCheck:
    """Result of a single validation check."""

    name: str
    status: str  # "pass" | "warn" | "fail"
    message: str


def validate_project(project_path: str) -> list[ValidationCheck]:
    """Validate a StreamTeX project structure. Return a list of checks."""
    checks: list[ValidationCheck] = []
    p = os.path.abspath(project_path)

    # 1. book.py exists
    if os.path.isfile(os.path.join(p, "book.py")):
        checks.append(ValidationCheck("book.py", "pass", "Found"))
    else:
        checks.append(ValidationCheck("book.py", "fail", "Missing"))

    # 2. blocks/__init__.py with ProjectBlockRegistry
    blocks_init = os.path.join(p, "blocks", "__init__.py")
    if os.path.isfile(blocks_init):
        content = open(blocks_init, encoding="utf-8").read()
        if "ProjectBlockRegistry" in content:
            checks.append(
                ValidationCheck("blocks/__init__.py", "pass", "ProjectBlockRegistry found")
            )
        else:
            checks.append(
                ValidationCheck("blocks/__init__.py", "fail", "Missing ProjectBlockRegistry")
            )
    else:
        checks.append(ValidationCheck("blocks/__init__.py", "fail", "Missing"))

    # 3. custom/styles.py exists
    if os.path.isfile(os.path.join(p, "custom", "styles.py")):
        checks.append(ValidationCheck("custom/styles.py", "pass", "Found"))
    else:
        checks.append(ValidationCheck("custom/styles.py", "fail", "Missing"))

    # 4. .streamlit/config.toml exists
    config_path = os.path.join(p, ".streamlit", "config.toml")
    if os.path.isfile(config_path):
        checks.append(ValidationCheck(".streamlit/config.toml", "pass", "Found"))
    else:
        checks.append(ValidationCheck(".streamlit/config.toml", "fail", "Missing"))

    # 5. enableStaticServing = true
    if os.path.isfile(config_path):
        content = open(config_path, encoding="utf-8").read()
        if "enableStaticServing" in content and "true" in content:
            checks.append(
                ValidationCheck("enableStaticServing", "pass", "Enabled")
            )
        else:
            checks.append(
                ValidationCheck("enableStaticServing", "fail", "Not enabled")
            )
    else:
        checks.append(
            ValidationCheck("enableStaticServing", "fail", "Config missing")
        )

    # 6. pyproject.toml with streamtex dependency
    pyproject_path = os.path.join(p, "pyproject.toml")
    if os.path.isfile(pyproject_path):
        import tomllib

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        deps = data.get("project", {}).get("dependencies", [])
        if any("streamtex" in d for d in deps):
            checks.append(
                ValidationCheck("pyproject.toml", "pass", "streamtex dependency found")
            )
        else:
            checks.append(
                ValidationCheck("pyproject.toml", "fail", "No streamtex dependency")
            )
    else:
        checks.append(ValidationCheck("pyproject.toml", "fail", "Missing"))

    # 7. .claude/ directory
    if os.path.isdir(os.path.join(p, ".claude")):
        checks.append(ValidationCheck(".claude/", "pass", "Found"))
    else:
        checks.append(ValidationCheck(".claude/", "fail", "Missing"))

    # 8. CLAUDE.md exists
    if os.path.isfile(os.path.join(p, "CLAUDE.md")):
        checks.append(ValidationCheck("CLAUDE.md", "pass", "Found"))
    else:
        checks.append(ValidationCheck("CLAUDE.md", "fail", "Missing"))

    # 9. static/images/ directory
    if os.path.isdir(os.path.join(p, "static", "images")):
        checks.append(ValidationCheck("static/images/", "pass", "Found"))
    else:
        checks.append(ValidationCheck("static/images/", "warn", "Missing"))

    # 10. Block files have def build
    blocks_dir = os.path.join(p, "blocks")
    if os.path.isdir(blocks_dir):
        block_files = [
            f for f in os.listdir(blocks_dir)
            if f.startswith("bck_") and f.endswith(".py")
        ]
        if block_files:
            all_valid = True
            for bf in block_files:
                content = open(os.path.join(blocks_dir, bf), encoding="utf-8").read()
                if "def build" not in content:
                    all_valid = False
                    break
            if all_valid:
                checks.append(
                    ValidationCheck(
                        "block files", "pass",
                        f"{len(block_files)} block(s) with def build",
                    )
                )
            else:
                checks.append(
                    ValidationCheck("block files", "fail", "Some blocks missing def build")
                )
        else:
            checks.append(
                ValidationCheck("block files", "pass", "No block files to check")
            )
    else:
        checks.append(ValidationCheck("block files", "fail", "blocks/ directory missing"))

    return checks


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------


def _copy_rich_template(
    template_name: str, target: str, project_name: str,
    extras: list[str] | None = None,
) -> list[str]:
    """Copy a rich template from streamtex-docs/templates/ into *target*.

    Returns the list of copied relative paths, or raises ClickException.
    """
    ws_root = find_workspace_root()
    if ws_root is None:
        raise click.ClickException(
            "--template requires a StreamTeX workspace.\n"
            "Run: stx install --preset standard"
        )

    src = os.path.join(ws_root, "streamtex-docs", "templates", f"template_{template_name}")
    if not os.path.isdir(src):
        raise click.ClickException(
            f"Template not found: {src}\n"
            "streamtex-docs is required. "
            "Run: stx install --preset standard"
        )

    copied: list[str] = []
    for dirpath, _dirnames, filenames in os.walk(src):
        for fname in filenames:
            src_file = os.path.join(dirpath, fname)
            rel = os.path.relpath(src_file, src)
            dst_file = os.path.join(target, rel)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied.append(rel)

    # Always generate pyproject.toml (overwrite template version to ensure
    # correct project name and hatchling packages=[] config)
    pyproject_path = os.path.join(target, "pyproject.toml")
    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(generate_pyproject_toml(project_name, extras=extras))
    if "pyproject.toml" not in copied:
        copied.append("pyproject.toml")

    # Generate .gitignore (not in the template)
    gitignore_path = os.path.join(target, ".gitignore")
    if not os.path.isfile(gitignore_path):
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(generate_gitignore())
        copied.append(".gitignore")

    return copied


@click.command("new")
@click.argument("name")
@click.option("--profile", default="project", help="Claude AI profile.")
@click.option("--collection", "is_collection", is_flag=True, help="Collection hub.")
@click.option(
    "--template",
    default=None,
    type=click.Choice(["project", "collection", "slides"]),
    help="Use a rich template from streamtex-docs/templates/.",
)
@click.option("--no-git", is_flag=True, help="Skip git init.")
@click.option("--no-sync", is_flag=True, help="Skip uv sync.")
@click.option("--no-claude", is_flag=True, help="Skip Claude profile.")
def new(
    name: str,
    profile: str,
    is_collection: bool,
    template: str | None,
    no_git: bool,
    no_sync: bool,
    no_claude: bool,
) -> None:
    """Create a new StreamTeX project."""
    console = get_console()

    # 1. Resolve target directory
    target = resolve_project_dir(name)
    os.makedirs(target, exist_ok=True)

    # 1b. Read preset from stx.toml to determine extras (pdf, ai, etc.)
    from .workspace_cmd import PRESET_EXTRAS, load_stx_toml

    extras: list[str] | None = None
    ws_root = find_workspace_root()
    if ws_root is not None:
        try:
            config = load_stx_toml(ws_root)
            preset = config.get("preset", "developer")
            extras = PRESET_EXTRAS.get(preset, []) or None
        except Exception:
            pass

    # 2. Scaffold files (rich template or minimal)
    if template:
        files = _copy_rich_template(template, target, name, extras=extras)
        console.print(f"[green]Project created from template '{template}':[/green] {target}")
    else:
        files = scaffold_project(target, name, collection=is_collection, extras=extras)
        console.print(f"[green]Project scaffolded:[/green] {target}")
    for f in files:
        console.print(f"  {f}")

    # 3. Git init
    if not no_git:
        result = subprocess.run(
            ["git", "init", target],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            console.print("[green]git init:[/green] ok")
        else:
            console.print(f"[yellow]git init:[/yellow] {result.stderr.strip()}")

    # 4. Claude profile (install_profile also creates .claude/custom/)
    if not no_claude:
        try:
            from .claude_cmd import install_profile
            from .workspace_cmd import load_stx_toml

            ws_root = find_workspace_root()
            if ws_root is None:
                console.print("[yellow]Claude profile:[/yellow] not in workspace — skipped")
            else:
                config = load_stx_toml(ws_root)
                from .claude_cmd import find_claude_repo

                claude_repo = find_claude_repo(ws_root, config)
                installed = install_profile(claude_repo, profile, target)
                console.print(
                    f"[green]Claude profile '{profile}':[/green] {len(installed)} files"
                )
        except click.ClickException as exc:
            console.print(f"[yellow]Claude profile:[/yellow] {exc.message}")

    # 5. uv sync
    if not no_sync:
        uv = shutil.which("uv")
        if uv:
            result = subprocess.run(
                [uv, "sync"],
                cwd=target,
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                console.print("[green]uv sync:[/green] ok")
                # Install pre-commit hooks
                result = subprocess.run(
                    [uv, "run", "pre-commit", "install"],
                    cwd=target,
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0:
                    console.print("[green]pre-commit install:[/green] ok")
                else:
                    console.print(f"[yellow]pre-commit install:[/yellow] {result.stderr.strip()}")
            else:
                console.print(f"[yellow]uv sync:[/yellow] {result.stderr.strip()}")
        else:
            console.print("[yellow]uv sync:[/yellow] uv not found — skipped")

    console.print(f"\n[bold green]Done![/bold green] Project '{name}' ready at {target}")


@click.command()
@click.argument("path", default=".")
def validate(path: str) -> None:
    """Validate a StreamTeX project structure."""
    console = get_console()
    checks = validate_project(path)

    from rich.table import Table

    table = Table(title=f"Project validation: {os.path.abspath(path)}")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Message")

    has_fail = False
    for c in checks:
        if c.status == "pass":
            icon = "[green]\u2713[/green]"
        elif c.status == "warn":
            icon = "[yellow]\u26a0[/yellow]"
        else:
            icon = "[red]\u2717[/red]"
            has_fail = True
        table.add_row(c.name, icon, c.message)

    console.print(table)

    if has_fail:
        console.print("\n[bold red]INVALID[/bold red] — fix the failing checks above.")
    else:
        console.print("\n[bold green]VALID[/bold green] — project structure looks good!")
