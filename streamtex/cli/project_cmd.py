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

from streamtex import st_book

from blocks import registry

st.set_page_config(page_title="{name}", layout="wide")

st_book(
    registry,
    title="{name}",
    paginate=True,
)
"""


def generate_collection_book_py(name: str) -> str:
    """Generate a collection-mode book.py using st_collection."""
    return f"""\
\"\"\"StreamTeX collection: {name}.\"\"\"

import streamlit as st

from streamtex import st_collection

st.set_page_config(page_title="{name}", layout="wide")

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

from streamtex import st_write


def build():
    \"\"\"Render this block.\"\"\"
    st_write("Hello from StreamTeX!")
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

[theme]
base = "dark"
"""


def generate_pyproject_toml(name: str) -> str:
    """Generate pyproject.toml for a StreamTeX project."""
    return f"""\
[project]
name = "{name}-streamtex"
version = "0.1.0"
description = "StreamTeX project: {name}"
requires-python = ">=3.10"
dependencies = [
    "streamtex>=0.3.0",
    "streamlit>=1.54.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""


def generate_setup_py(name: str) -> str:
    """Generate a docstring-only setup.py."""
    return f"""\
\"\"\"Setup for {name}-streamtex project.\"\"\"
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
    target_dir: str, name: str, *, collection: bool = False
) -> list[str]:
    """Create all scaffold files. Return the list of relative paths created."""
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
    _write("pyproject.toml", generate_pyproject_toml(name))
    _write("setup.py", generate_setup_py(name))
    _write(".gitignore", generate_gitignore())

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

    If inside a workspace with ``projects/``, use ``projects/<name>-streamtex/``.
    Otherwise, use ``./<name>-streamtex/``.

    Raises:
        click.ClickException: if the target directory already exists.
    """
    dir_name = f"{name}-streamtex"

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
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

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


@click.command("new")
@click.argument("name")
@click.option("--profile", default="project", help="Claude AI profile.")
@click.option("--collection", "is_collection", is_flag=True, help="Collection hub.")
@click.option("--no-git", is_flag=True, help="Skip git init.")
@click.option("--no-sync", is_flag=True, help="Skip uv sync.")
@click.option("--no-claude", is_flag=True, help="Skip Claude profile.")
def new(name: str, profile: str, is_collection: bool, no_git: bool, no_sync: bool, no_claude: bool) -> None:
    """Create a new StreamTeX project."""
    console = get_console()

    # 1. Resolve target directory
    target = resolve_project_dir(name)
    os.makedirs(target, exist_ok=True)

    # 2. Scaffold files
    files = scaffold_project(target, name, collection=is_collection)
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

    # 4. Claude profile
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
