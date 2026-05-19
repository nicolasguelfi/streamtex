"""Project commands: new and validate."""

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass

import click

from .console import get_console
from .dev_config import resolve_repo_path
from .workspace_cmd import find_workspace_root, load_stx_toml

logger = logging.getLogger(__name__)

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
from streamtex import (
    st_book, TOCConfig, NumberingMode, MarkerConfig, BannerConfig,
    PdfConfig, ExportConfig, ExportMode, ViewMode,
    Spacing, SpacingConfig, set_spacing,
)

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

# Section spacing — configurable margins around blocks and sections
# set_spacing(SpacingConfig(
#     block=Spacing(top=2),          # vertical space before each block
#     section=Spacing(top=2),        # vertical space between slide_break sections
# ))

st_book(
    registry,
    toc_config=toc,
    marker_config=marker_config,
    paginate=True,
    banner=BannerConfig.full(),
    view_modes=[ViewMode.PAGINATED, ViewMode.CONTINUOUS],
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

from pathlib import Path

from streamtex.blocks import ProjectBlockRegistry

registry = ProjectBlockRegistry(Path(__file__).parent)
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
    # Always include "cli" for dual-mode deployment (stx export html needs rich)
    all_extras = list(dict.fromkeys(["cli"] + (extras or [])))
    extras_str = ",".join(all_extras)
    stx_dep = f'"streamtex[{extras_str}]>=0.3.0"'

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

# Claude profile — managed by stx claude install/update, not git
.claude/*
!.claude/custom/
!.claude/.stx-profile
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
# Reuse architecture generators (MIG-3 — Q7/Q8)
# ---------------------------------------------------------------------------


def _split_kit_ref(kit_ref: str) -> tuple[str, str]:
    """Split a kit reference ``<pack>:<kit_name>`` into a 2-tuple.

    Raises:
        click.ClickException: when the format is not exactly ``pack:name``.
    """
    if ":" not in kit_ref or kit_ref.count(":") != 1:
        raise click.ClickException(
            f"Invalid kit reference '{kit_ref}'. Expected '<pack>:<kit_name>' "
            "(e.g. 'streamtex_design:project-default')."
        )
    pack, kit_name = kit_ref.split(":", 1)
    pack = pack.strip()
    kit_name = kit_name.strip()
    if not pack or not kit_name:
        raise click.ClickException(
            f"Invalid kit reference '{kit_ref}'. Both pack and kit name must be non-empty."
        )
    return pack, kit_name


def _resolve_kit(kit_ref: str) -> dict:
    """Resolve a kit reference and return its parsed TOML manifest.

    Locates the kit by importing the pack module via entry-points (Q7
    discovery) and reading ``<pack>/kits/<kit_name>.toml``. Returns ``{}``
    if discovery fails so the caller can fall back to a minimal scaffold.
    """
    pack_name, kit_name = _split_kit_ref(kit_ref)
    try:
        import importlib
        import tomllib as _tomllib
        mod = importlib.import_module(pack_name)
        pack_root = os.path.dirname(mod.__file__ or "")
        kit_file = os.path.join(pack_root, "kits", f"{kit_name}.toml")
        if not os.path.isfile(kit_file):
            raise click.ClickException(
                f"Kit '{kit_name}' not found in pack '{pack_name}' "
                f"(expected at {kit_file})."
            )
        with open(kit_file, "rb") as f:
            return _tomllib.load(f)
    except click.ClickException:
        raise
    except ModuleNotFoundError as exc:
        raise click.ClickException(
            f"Pack '{pack_name}' is not installed. "
            f"Run: stx pack add <ref> (or pip install {pack_name})."
        ) from exc
    except Exception as exc:
        logger.debug("Kit resolution failed", exc_info=True)
        raise click.ClickException(f"Failed to resolve kit '{kit_ref}': {exc}") from exc


def generate_stx_toml(
    name: str,
    *,
    pack_name: str | None = "mypack",
    kit_ref: str | None = None,
    design_system_ref: str | None = None,
    additional_packs: list[str] | None = None,
) -> str:
    """Generate the project ``stx.toml`` (cf. PLAN §6.1).

    The schema declares the project, the local primary pack (when *pack_name*
    is non-None), the kit pack (when *kit_ref* is provided), any *additional
    packs* (as git URLs), the active design system, and a default resolution
    order.
    """
    lines: list[str] = []
    lines.append("# StreamTeX project configuration (cf. PLAN §6.1)")
    lines.append("")
    lines.append("[project]")
    lines.append(f'name = "{name}"')
    lines.append('version = "0.1.0"')
    lines.append("")

    declared_packs: list[str] = []

    if pack_name:
        lines.append("[[packs]]")
        lines.append('type = "local"')
        lines.append(f'name = "{pack_name}"')
        lines.append(f'path = "./{pack_name}"')
        lines.append("primary = true")
        lines.append("")
        declared_packs.append(pack_name)

    if kit_ref:
        kit_pack, _kit_name = _split_kit_ref(kit_ref)
        lines.append("[[packs]]")
        lines.append('type = "git"')
        lines.append(f'name = "{kit_pack}"')
        lines.append(f'ref = "github.com/nicolasguelfi/{kit_pack.replace("_", "-")}"')
        lines.append('rev = "main"')
        lines.append("")
        if kit_pack not in declared_packs:
            declared_packs.append(kit_pack)

    if additional_packs:
        for ref in additional_packs:
            lines.append("[[packs]]")
            lines.append('type = "git"')
            short = ref.rstrip("/").rsplit("/", 1)[-1]
            short = short.replace(".git", "")
            lines.append(f'name = "{short}"')
            lines.append(f'ref = "{ref}"')
            lines.append('rev = "main"')
            lines.append("")
            if short not in declared_packs:
                declared_packs.append(short)

    if design_system_ref:
        lines.append("[design_system]")
        lines.append(f'ref = "{design_system_ref}"')
        lines.append("")

    if kit_ref:
        lines.append("[kit]")
        lines.append(f'ref = "{kit_ref}"')
        lines.append("")

    if declared_packs:
        lines.append("[resolution]")
        prefer_list = ", ".join(f'"{p}"' for p in declared_packs)
        lines.append(f"prefer = [{prefer_list}]")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_mypack_pyproject_toml(pack_name: str) -> str:
    """Generate the ``pyproject.toml`` for the project's local primary pack."""
    return f"""\
[project]
name = "{pack_name}"
version = "0.1.0"
description = "Local primary pack for this StreamTeX project."
requires-python = ">=3.11"
dependencies = []

[project.entry-points."streamtex.packs"]
{pack_name} = "{pack_name}"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["{pack_name}"]
"""


def generate_mypack_manifest(pack_name: str) -> str:
    """Generate the ``_pack_manifest.toml`` for a project's primary pack."""
    return f"""\
# Pack manifest (cf. PLAN §4.6 — manifest format 0.1, mouvant pendant 0.x)

[manifest]
format = "0.1"

[pack]
name = "{pack_name}"
version = "0.1.0"
streamtex_compat = ">=0.6.42,<1.0"
"""


def scaffold_mypack(target_dir: str, pack_name: str) -> list[str]:
    """Create the local primary pack scaffold under *target_dir*.

    Layout::

        <target>/<pack_name>/pyproject.toml
        <target>/<pack_name>/<pack_name>/__init__.py
        <target>/<pack_name>/<pack_name>/_pack_manifest.toml
        <target>/<pack_name>/<pack_name>/components/.gitkeep
        <target>/<pack_name>/<pack_name>/design_systems/.gitkeep
        <target>/<pack_name>/<pack_name>/cli_templates/.gitkeep
        <target>/<pack_name>/<pack_name>/kits/.gitkeep
    """
    created: list[str] = []
    pack_root = os.path.join(target_dir, pack_name)
    pkg_dir = os.path.join(pack_root, pack_name)
    os.makedirs(pkg_dir, exist_ok=True)

    def _write(rel: str, content: str) -> None:
        full = os.path.join(target_dir, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        created.append(rel)

    _write(f"{pack_name}/pyproject.toml", generate_mypack_pyproject_toml(pack_name))
    _write(f"{pack_name}/{pack_name}/__init__.py", "")
    _write(
        f"{pack_name}/{pack_name}/_pack_manifest.toml",
        generate_mypack_manifest(pack_name),
    )

    for sub in ("components", "design_systems", "cli_templates", "kits"):
        sub_dir = os.path.join(pkg_dir, sub)
        os.makedirs(sub_dir, exist_ok=True)
        keep = os.path.join(sub_dir, ".gitkeep")
        if not os.path.exists(keep):
            with open(keep, "w") as f:
                f.write("")
            created.append(f"{pack_name}/{pack_name}/{sub}/.gitkeep")

    return created


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

    # Deployment files (dual-mode: Nginx + Streamlit)
    from .deploy_cmd import generate_dockerfile, generate_entrypoint, generate_nginx_conf

    _write("Dockerfile", generate_dockerfile())
    _write("nginx.conf", generate_nginx_conf())
    _write("entrypoint.sh", generate_entrypoint())

    # .stx-version — minimum streamtex version for Docker build guard
    from importlib.metadata import version as pkg_version
    try:
        stx_ver = pkg_version("streamtex")
    except Exception:
        stx_ver = "0.3.0"
    _write(".stx-version", stx_ver + "\n")

    # static/images/ (empty directory)
    images_dir = os.path.join(target_dir, "static", "images")
    os.makedirs(images_dir, exist_ok=True)

    # docs/ — CE (Compound Engineering) artifact directories
    ce_dirs = [
        "docs/collect",
        "docs/assess",
        "docs/plans",
        "docs/reviews",
        "docs/solutions/structure",
        "docs/solutions/style",
        "docs/solutions/content",
        "docs/solutions/process",
        "docs/solutions/pedagogy",
        "docs/solutions/assets",
        "docs/solutions/deployment",
        "docs/solutions/import",
        "docs/solutions/governance",
    ]
    for d in ce_dirs:
        dir_path = os.path.join(target_dir, d)
        os.makedirs(dir_path, exist_ok=True)
        gitkeep = os.path.join(dir_path, ".gitkeep")
        if not os.path.exists(gitkeep):
            with open(gitkeep, "w") as f:
                f.write("")

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

    # 11-14. Reuse-architecture checks (NEW — PLAN §7.1.4).
    stx_toml_path = os.path.join(p, "stx.toml")
    primary_packs: list[dict] = []
    if os.path.isfile(stx_toml_path):
        try:
            import tomllib as _tomllib
            with open(stx_toml_path, "rb") as f:
                stx_data = _tomllib.load(f)
            checks.append(ValidationCheck("stx.toml", "pass", "Found and parsable"))
            primary_packs = [
                pe for pe in stx_data.get("packs", [])
                if pe.get("type") == "local" and pe.get("primary") is True
            ]
        except Exception as exc:
            stx_data = {}
            checks.append(
                ValidationCheck("stx.toml", "fail", f"Parse error: {exc}")
            )
    else:
        stx_data = {}
        checks.append(ValidationCheck("stx.toml", "warn", "Missing"))

    # 12. <pack_name>/ exists with _pack_manifest.toml.
    if primary_packs:
        primary = primary_packs[0]
        pack_dir = os.path.join(p, primary.get("path", "").lstrip("./"))
        primary_name = primary.get("name", "mypack")
        manifest_path = os.path.join(pack_dir, primary_name, "_pack_manifest.toml")
        if os.path.isdir(pack_dir) and os.path.isfile(manifest_path):
            checks.append(
                ValidationCheck("primary pack dir", "pass", f"{primary_name}/ + manifest")
            )
        else:
            checks.append(
                ValidationCheck(
                    "primary pack dir", "warn",
                    f"Missing {primary_name}/ or _pack_manifest.toml",
                )
            )
    else:
        checks.append(ValidationCheck("primary pack dir", "warn", "No primary local pack declared"))

    # 13. Pack primary importable as editable install.
    if primary_packs:
        primary_name = primary_packs[0].get("name", "mypack")
        try:
            import importlib.util as _iu
            spec = _iu.find_spec(primary_name)
            if spec is not None:
                checks.append(
                    ValidationCheck("primary pack importable", "pass", primary_name)
                )
            else:
                checks.append(
                    ValidationCheck(
                        "primary pack importable", "warn",
                        f"{primary_name} not importable — run `uv pip install -e ./{primary_name}`",
                    )
                )
        except Exception as exc:
            checks.append(
                ValidationCheck("primary pack importable", "warn", str(exc))
            )

    # 14. Exactly one [[packs]] type=local primary=true.
    if stx_data:
        count = len(primary_packs)
        if count == 1:
            checks.append(
                ValidationCheck("primary pack unique", "pass", "Exactly one")
            )
        elif count == 0:
            checks.append(
                ValidationCheck("primary pack unique", "warn", "No primary local pack")
            )
        else:
            checks.append(
                ValidationCheck(
                    "primary pack unique", "fail",
                    f"{count} primary local packs (must be 1)",
                )
            )

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

    # Resolve streamtex-docs via dev-link first, fallback to workspace clone.
    try:
        config = load_stx_toml(ws_root)
        docs_root, _is_dev = resolve_repo_path("streamtex-docs", ws_root, config)
    except FileNotFoundError:
        raise click.ClickException(
            "streamtex-docs not found.\n"
            "Run: stx install --preset standard\n"
            "Or:  stx dev register streamtex-docs /path/to/streamtex-docs"
        ) from None

    src = os.path.join(docs_root, "templates", f"template_{template_name}")
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
    help="(legacy) Rich template from streamtex-docs/templates/. Prefer --kit.",
)
@click.option(
    "--kit",
    "kit_ref",
    default=None,
    help="Install a kit from a pack: --kit <pack>:<kit_name> (Q8 / PLAN §7.1).",
)
@click.option(
    "--pack",
    "extra_packs",
    multiple=True,
    help="Add an extra pack to stx.toml (git URL). Can be passed multiple times.",
)
@click.option(
    "--pack-name",
    default="mypack",
    show_default=True,
    help="Name of the local primary pack scaffolded inside the project (Q7).",
)
@click.option(
    "--no-mypack",
    is_flag=True,
    help="Skip creation of the local primary pack (consumer-only project).",
)
@click.option("--no-git", is_flag=True, help="Skip git init.")
@click.option("--no-sync", is_flag=True, help="Skip uv sync.")
@click.option("--no-claude", is_flag=True, help="Skip Claude profile.")
def new(
    name: str,
    profile: str,
    is_collection: bool,
    template: str | None,
    kit_ref: str | None,
    extra_packs: tuple[str, ...],
    pack_name: str,
    no_mypack: bool,
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
            logger.debug("Failed to load workspace preset extras", exc_info=True)

    # 1c. Legacy --template alias resolves to --kit when no explicit --kit given.
    # PLAN §7.1.1 : --template <X> → --kit streamtex_design:<X>-default (internal).
    # Special-cases: 'slides' maps to slides-modern-dark (existing kit in v0.1.0).
    _legacy_kit_alias = {
        "project": "streamtex_design:project-default",
        "collection": "streamtex_design:collection-default",
        "slides": "streamtex_design:slides-modern-dark",
    }
    if template and not kit_ref:
        kit_ref = _legacy_kit_alias[template]

    # 1d. Resolve kit (parses ref + reads manifest; errors if pack missing).
    kit_manifest: dict = {}
    kit_design_system: str | None = None
    if kit_ref:
        try:
            kit_manifest = _resolve_kit(kit_ref)
            kit_design_system = (
                kit_manifest.get("design_system", {}).get("ref")
                or None
            )
        except click.ClickException as exc:
            console.print(f"[yellow]kit:[/yellow] {exc.message}")
            kit_manifest = {}
            kit_design_system = None

    # 2. Scaffold files (rich template legacy preserved, OR minimal + kit DS).
    if template and not kit_manifest:
        # Legacy path: kit alias failed to resolve, fall back to streamtex-docs
        # rich template. Preserves the pre-MIG-3 behaviour for the 43 tests.
        files = _copy_rich_template(template, target, name, extras=extras)
        console.print(f"[green]Project created from template '{template}':[/green] {target}")
    else:
        files = scaffold_project(target, name, collection=is_collection, extras=extras)
        console.print(f"[green]Project scaffolded:[/green] {target}")
        if kit_design_system and kit_ref:
            # Inject the kit's design system into custom/styles.py.
            pack_module, _ = _split_kit_ref(kit_ref)
            styles_py = os.path.join(target, "custom", "styles.py")
            with open(styles_py, "w", encoding="utf-8") as f:
                f.write(
                    f'"""Custom styles for this project (kit: {kit_ref})."""\n'
                    f"# Auto-injected by `stx project new --kit` (PLAN §7.1.3).\n"
                    f"from {pack_module}.design_systems.{kit_design_system} "
                    f"import DesignSystem as Styles\n"
                    f"__all__ = [\"Styles\"]\n"
                )
    for f in files:
        console.print(f"  {f}")

    # 4bis. Generate stx.toml at project root (NEW — Q7/Q8 / PLAN §6.1).
    primary_pack = None if no_mypack else pack_name
    stx_toml_content = generate_stx_toml(
        name,
        pack_name=primary_pack,
        kit_ref=kit_ref,
        design_system_ref=kit_design_system,
        additional_packs=list(extra_packs) if extra_packs else None,
    )
    stx_toml_path = os.path.join(target, "stx.toml")
    with open(stx_toml_path, "w", encoding="utf-8") as f:
        f.write(stx_toml_content)
    console.print("[green]stx.toml:[/green] generated")

    # 6bis. Create local primary pack (NEW — Q7 / PLAN §7.1.2 step 6bis).
    pack_created: list[str] = []
    if not no_mypack:
        pack_created = scaffold_mypack(target, pack_name)
        console.print(f"[green]Local primary pack '{pack_name}':[/green] {len(pack_created)} files")

    # 5. Git init (preserved behaviour — step 5/PLAN renumbered as 5).
    if not no_git:
        result = subprocess.run(
            ["git", "init", target],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            console.print("[green]git init:[/green] ok")
        else:
            console.print(f"[yellow]git init:[/yellow] {result.stderr.strip()}")

    # 7. Claude profile (install_profile also creates .claude/custom/)
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

    # 8. uv sync
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

                # 8bis. pip install -e ./<pack_name> (NEW — Q7/Q8).
                if not no_mypack:
                    pack_path = os.path.join(target, pack_name)
                    result_pack = subprocess.run(
                        [uv, "pip", "install", "-e", pack_path],
                        cwd=target,
                        capture_output=True, text=True, timeout=120,
                    )
                    if result_pack.returncode == 0:
                        console.print(
                            f"[green]pip install -e ./{pack_name}:[/green] ok"
                        )
                    else:
                        console.print(
                            f"[yellow]pip install -e ./{pack_name}:[/yellow] "
                            f"{result_pack.stderr.strip()}"
                        )

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

    # 10. Final validation (NEW — non-strict).
    final_checks = validate_project(target)
    failed = [c for c in final_checks if c.status == "fail"]
    if failed:
        console.print(
            f"[yellow]final validate:[/yellow] {len(failed)} warnings — "
            "run `stx project validate` for details."
        )
    else:
        console.print("[green]final validate:[/green] all checks pass")

    console.print(f"\n[bold green]Done![/bold green] Project '{name}' ready at {target}")
    if no_mypack:
        console.print(
            "[dim]Tip:[/dim] add packs later with `stx pack new <name>` "
            "or `stx pack add <ref>`."
        )


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
