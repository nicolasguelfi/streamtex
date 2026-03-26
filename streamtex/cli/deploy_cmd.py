"""Deploy commands: preflight, docker, render, huggingface, and status."""

import glob
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass

import click

from .console import get_console

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class PreflightCheck:
    """Result of a single pre-deployment check."""

    name: str
    status: str  # "pass" | "warn" | "fail"
    message: str


@dataclass
class DeployStatus:
    """Status of a single deployed service."""

    name: str
    status: str  # "live" | "sleep" | "down" | "error"
    url: str
    message: str


# ---------------------------------------------------------------------------
# Dockerfile template
# ---------------------------------------------------------------------------


def generate_dockerfile() -> str:
    """Generate a simplified Dockerfile for StreamTeX projects."""
    return """\
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \\
    STREAMLIT_SERVER_HEADLESS=true UV_LINK_MODE=copy
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
ENV PORT=8501
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["uv", "run", "streamlit", "run", "book.py", \\
            "--server.port=8501", "--server.address=0.0.0.0"]
"""


# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------


def _find_uv() -> str | None:
    """Locate the uv binary. Returns None if not found."""
    return shutil.which("uv")


def run_preflight(
    project_path: str,
    *,
    skip_tests: bool = False,
    skip_lint: bool = False,
) -> list[PreflightCheck]:
    """Run pre-deployment checks. Return a list of check results."""
    checks: list[PreflightCheck] = []
    p = os.path.abspath(project_path)

    # 1. book.py exists
    if os.path.isfile(os.path.join(p, "book.py")):
        checks.append(PreflightCheck("book.py", "pass", "Found"))
    else:
        checks.append(PreflightCheck("book.py", "fail", "Missing"))

    # 2. .streamlit/config.toml with enableStaticServing
    config_path = os.path.join(p, ".streamlit", "config.toml")
    if os.path.isfile(config_path):
        content = open(config_path, encoding="utf-8").read()
        if "enableStaticServing" in content and "true" in content:
            checks.append(
                PreflightCheck("enableStaticServing", "pass", "Enabled")
            )
        else:
            checks.append(
                PreflightCheck("enableStaticServing", "fail", "Not enabled")
            )
    else:
        checks.append(
            PreflightCheck("enableStaticServing", "fail", "Config missing")
        )

    # 3. pyproject.toml with streamtex dependency
    pyproject_path = os.path.join(p, "pyproject.toml")
    if os.path.isfile(pyproject_path):
        import tomllib

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        deps = data.get("project", {}).get("dependencies", [])
        if any("streamtex" in d for d in deps):
            checks.append(
                PreflightCheck("pyproject.toml", "pass", "streamtex dependency found")
            )
        else:
            checks.append(
                PreflightCheck("pyproject.toml", "fail", "No streamtex dependency")
            )
    else:
        checks.append(PreflightCheck("pyproject.toml", "fail", "Missing"))

    # 4. Git working tree clean
    try:
        result = subprocess.run(
            ["git", "-C", p, "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and len(result.stdout.strip()) == 0:
            checks.append(PreflightCheck("git clean", "pass", "Working tree clean"))
        elif result.returncode == 0:
            checks.append(PreflightCheck("git clean", "warn", "Uncommitted changes"))
        else:
            checks.append(PreflightCheck("git clean", "warn", "Not a git repo"))
    except (subprocess.TimeoutExpired, OSError):
        checks.append(PreflightCheck("git clean", "warn", "Could not check git status"))

    # 5. No sensitive files
    sensitive_patterns = [".env", "credentials*", "*.key", "*.pem"]
    found_sensitive: list[str] = []
    for pattern in sensitive_patterns:
        found_sensitive.extend(
            os.path.basename(f)
            for f in glob.glob(os.path.join(p, pattern))
            if os.path.isfile(f)
        )
    if found_sensitive:
        checks.append(
            PreflightCheck(
                "sensitive files", "warn",
                f"Found: {', '.join(found_sensitive)}",
            )
        )
    else:
        checks.append(PreflightCheck("sensitive files", "pass", "None found"))

    # 6. static/ directory exists
    if os.path.isdir(os.path.join(p, "static")):
        checks.append(PreflightCheck("static/", "pass", "Found"))
    else:
        checks.append(PreflightCheck("static/", "warn", "Missing"))

    # 7. Dockerfile present
    if os.path.isfile(os.path.join(p, "Dockerfile")):
        checks.append(PreflightCheck("Dockerfile", "pass", "Found"))
    else:
        checks.append(PreflightCheck("Dockerfile", "warn", "Missing"))

    # 8. Tests pass (skippable)
    if not skip_tests:
        uv = _find_uv()
        if uv:
            try:
                result = subprocess.run(
                    [uv, "run", "pytest", "tests/", "-q"],
                    cwd=p,
                    capture_output=True, text=True, timeout=300,
                )
                if result.returncode == 0:
                    checks.append(PreflightCheck("tests", "pass", "All tests pass"))
                else:
                    checks.append(PreflightCheck("tests", "fail", "Tests failed"))
            except (subprocess.TimeoutExpired, OSError):
                checks.append(PreflightCheck("tests", "fail", "Test run error"))
        else:
            checks.append(PreflightCheck("tests", "warn", "uv not found — skipped"))

    # 9. Lint clean (skippable)
    if not skip_lint:
        uv = _find_uv()
        if uv:
            try:
                result = subprocess.run(
                    [uv, "run", "ruff", "check", "."],
                    cwd=p,
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0:
                    checks.append(PreflightCheck("lint", "pass", "Clean"))
                else:
                    checks.append(PreflightCheck("lint", "warn", "Lint issues found"))
            except (subprocess.TimeoutExpired, OSError):
                checks.append(PreflightCheck("lint", "warn", "Lint run error"))
        else:
            checks.append(PreflightCheck("lint", "warn", "uv not found — skipped"))

    return checks


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------


def detect_git_remote(project_path: str) -> str | None:
    """Detect the git remote origin URL and normalise to HTTPS.

    Converts ``git@github.com:user/repo.git`` →
    ``https://github.com/user/repo`` and strips trailing ``.git``.
    Returns *None* when no remote is configured or git fails.
    """
    try:
        result = subprocess.run(
            ["git", "-C", project_path, "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        url = result.stdout.strip()
        if not url:
            return None
    except (subprocess.TimeoutExpired, OSError):
        return None

    # SSH → HTTPS normalisation
    m = re.match(r"git@([^:]+):(.+)", url)
    if m:
        url = f"https://{m.group(1)}/{m.group(2)}"

    # Strip trailing .git
    if url.endswith(".git"):
        url = url[:-4]

    return url


def discover_manuals(project_path: str) -> list[str]:
    """Scan ``manuals/`` for ``stx_manual_*`` / ``stx_manuals_*`` directories.

    Returns sorted relative paths (e.g. ``manuals/stx_manual_intro``).
    """
    manuals_dir = os.path.join(project_path, "manuals")
    if not os.path.isdir(manuals_dir):
        return []

    found: list[str] = []
    for entry in sorted(os.listdir(manuals_dir)):
        full = os.path.join(manuals_dir, entry)
        if os.path.isdir(full) and (
            entry.startswith("stx_manual_") or entry.startswith("stx_manuals_")
        ):
            found.append(f"manuals/{entry}")
    return found


def derive_service_name(manual_path: str) -> str:
    """Derive a Render service name from a manual directory path.

    ``manuals/stx_manual_intro`` → ``streamtex-intro``
    ``manuals/stx_manuals_collection`` → ``streamtex-collection``
    """
    basename = os.path.basename(manual_path)
    for prefix in ("stx_manuals_", "stx_manual_"):
        if basename.startswith(prefix):
            return f"streamtex-{basename[len(prefix):]}"
    return basename


def parse_env_vars(env_list: tuple[str, ...]) -> list[tuple[str, str]]:
    """Parse ``KEY=VALUE`` pairs from CLI ``--env`` options.

    Uses :func:`str.partition` so values containing ``=`` are preserved.

    Raises:
        click.BadParameter: if a value has no ``=``.
    """
    result: list[tuple[str, str]] = []
    for item in env_list:
        key, sep, value = item.partition("=")
        if not sep:
            raise click.BadParameter(
                f"Invalid format: '{item}'. Expected KEY=VALUE."
            )
        result.append((key, value))
    return result


def generate_render_service(
    *,
    name: str,
    repo: str,
    branch: str,
    plan: str,
    env_vars: list[tuple[str, str]],
    folder: str | None = None,
    build_filter: bool = False,
) -> str:
    """Generate a single Render service YAML block."""
    lines = [
        "  - type: web",
        f"    name: {name}",
        "    runtime: docker",
        f"    repo: {repo}",
        f"    branch: {branch}",
        f"    plan: {plan}",
    ]

    if build_filter:
        lines.append("    buildFilter:")
        lines.append("      paths:")
        lines.append("        - \"**\"")

    # Collect env vars
    all_env: list[tuple[str, str]] = list(env_vars)
    if folder:
        all_env.append(("FOLDER", folder))

    # Add STX_PASSWORD=changeme unless user already specified it
    if not any(k == "STX_PASSWORD" for k, _ in all_env):
        all_env.append(("STX_PASSWORD", "changeme"))

    lines.append("    envVars:")
    for key, value in all_env:
        lines.append(f"      - key: {key}")
        lines.append(f"        value: {value}")

    return "\n".join(lines)


def generate_render_yaml(services: list[str]) -> str:
    """Assemble a complete ``render.yaml`` from service blocks."""
    return "services:\n" + "\n\n".join(services) + "\n"


# ---------------------------------------------------------------------------
# Hugging Face helpers
# ---------------------------------------------------------------------------

HF_LFS_PATTERNS = [
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.svg", "*.webp",
    "*.mp4", "*.mp3", "*.wav", "*.ogg",
    "*.pdf", "*.zip", "*.tar.gz",
    "*.woff", "*.woff2", "*.ttf", "*.otf",
]


def verify_git_lfs() -> bool:
    """Check that ``git lfs`` is installed.

    Returns ``True`` when ``git lfs version`` succeeds.
    """
    try:
        result = subprocess.run(
            ["git", "lfs", "version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def verify_hf_cli() -> bool:
    """Check that ``huggingface-cli`` is installed and authenticated.

    Returns ``True`` when ``huggingface-cli whoami`` succeeds.
    """
    hf = shutil.which("huggingface-cli")
    if hf is None:
        return False
    try:
        result = subprocess.run(
            [hf, "whoami"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def setup_lfs_tracking(project_path: str) -> bool:
    """Write/update ``.gitattributes`` with LFS patterns for heavy assets.

    Returns ``True`` if the file was modified.
    """
    ga_path = os.path.join(project_path, ".gitattributes")
    existing_lines: list[str] = []
    if os.path.isfile(ga_path):
        with open(ga_path, encoding="utf-8") as f:
            existing_lines = f.read().splitlines()

    new_lines: list[str] = []
    for pattern in HF_LFS_PATTERNS:
        entry = f"{pattern} filter=lfs diff=lfs merge=lfs -text"
        if not any(line.startswith(f"{pattern} ") for line in existing_lines):
            new_lines.append(entry)

    if not new_lines:
        return False

    with open(ga_path, "a", encoding="utf-8") as f:
        if existing_lines and existing_lines[-1] != "":
            f.write("\n")
        f.write("\n".join(new_lines) + "\n")
    return True


def generate_hf_frontmatter(
    title: str,
    emoji: str,
    app_port: int = 8501,
) -> str:
    """Generate YAML front-matter for a Hugging Face Space README."""
    return (
        "---\n"
        f"title: {title}\n"
        f"emoji: {emoji}\n"
        "colorFrom: blue\n"
        "colorTo: indigo\n"
        "sdk: docker\n"
        f"app_port: {app_port}\n"
        "pinned: false\n"
        "---\n"
    )


def update_readme_frontmatter(project_path: str, frontmatter: str) -> bool:
    """Insert or replace YAML front-matter in the project ``README.md``.

    Returns ``True`` if the file was created or modified.
    """
    readme_path = os.path.join(project_path, "README.md")

    if not os.path.isfile(readme_path):
        title = os.path.basename(os.path.abspath(project_path))
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(frontmatter + f"\n# {title}\n")
        return True

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    # Detect existing front-matter delimited by ---
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end != -1:
            # Replace existing front-matter (including closing ---)
            new_content = frontmatter + content[end + 5:]
        else:
            # Malformed: only opening ---, replace first line
            new_content = frontmatter + content
    else:
        new_content = frontmatter + "\n" + content

    if new_content == content:
        return False

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def setup_hf_remote(project_path: str, space_url: str) -> None:
    """Add or update a ``hf`` git remote pointing to the HF Space repo.

    Converts ``https://huggingface.co/spaces/user/repo`` to
    ``https://huggingface.co/spaces/user/repo`` (git clone URL is the same).
    """
    url = space_url.rstrip("/")
    if not url.endswith(".git"):
        url = url + ".git"

    # Check if remote already exists
    result = subprocess.run(
        ["git", "-C", project_path, "remote", "get-url", "hf"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode == 0:
        subprocess.run(
            ["git", "-C", project_path, "remote", "set-url", "hf", url],
            capture_output=True, text=True, timeout=10,
        )
    else:
        subprocess.run(
            ["git", "-C", project_path, "remote", "add", "hf", url],
            capture_output=True, text=True, timeout=10,
        )


# ---------------------------------------------------------------------------
# Deploy status helpers
# ---------------------------------------------------------------------------


def render_service_url(name: str) -> str:
    """Derive the public URL for a deployed service on Hetzner/Coolify."""
    if name == "streamtex":
        subdomain = "docs"
    elif name.startswith("streamtex-"):
        subdomain = "docs-" + name[len("streamtex-"):]
    else:
        subdomain = name
    return f"https://{subdomain}.streamtex.org"


def parse_render_yaml_services(project_path: str) -> list[str]:
    """Extract service names from ``render.yaml``.

    Returns a sorted list of service names. Empty list if file is missing.
    """
    yaml_path = os.path.join(project_path, "render.yaml")
    if not os.path.isfile(yaml_path):
        return []

    with open(yaml_path, encoding="utf-8") as f:
        content = f.read()

    names = re.findall(r"^\s+name:\s+(.+)$", content, re.MULTILINE)
    return sorted(n.strip() for n in names)


def http_probe(url: str, timeout: int = 10) -> tuple[str, str]:
    """Probe a URL with HTTP HEAD and return ``(status, message)``.

    Returns:
        A tuple of ``(status, message)`` where status is one of
        ``"live"``, ``"sleep"``, ``"down"``, or ``"error"``.
    """
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return ("live", f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        if e.code in (502, 503):
            return ("sleep", f"HTTP {e.code} — service may be waking up")
        if e.code == 404:
            return ("down", f"HTTP {e.code} — service not found")
        return ("error", f"HTTP {e.code}")
    except urllib.error.URLError:
        return ("sleep", "Timeout — service may be sleeping")
    except OSError as e:
        return ("error", str(e))


def parse_hf_remote(project_path: str) -> str | None:
    """Extract ``owner/repo`` from the ``hf`` git remote.

    Returns ``None`` if the remote is not configured or doesn't match.
    """
    try:
        result = subprocess.run(
            ["git", "-C", project_path, "remote", "get-url", "hf"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return None
        url = result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return None

    m = re.search(r"huggingface\.co/spaces/([^/]+/[^/]+?)(?:\.git)?$", url)
    return m.group(1) if m else None


def check_render_status(
    project_path: str,
    name: str | None = None,
    timeout: int = 10,
) -> list[DeployStatus]:
    """Check status of Render services.

    If *name* is provided, probe that single service. Otherwise discover
    services from ``render.yaml`` or ``manuals/``.
    """
    if name:
        url = render_service_url(name)
        st, msg = http_probe(url, timeout)
        return [DeployStatus(name=name, status=st, url=url, message=msg)]

    # Discovery: render.yaml first, fallback to manuals
    services = parse_render_yaml_services(project_path)
    if not services:
        manuals = discover_manuals(project_path)
        services = [derive_service_name(m) for m in manuals]

    results: list[DeployStatus] = []
    for svc in services:
        url = render_service_url(svc)
        st, msg = http_probe(url, timeout)
        results.append(DeployStatus(name=svc, status=st, url=url, message=msg))
    return results


def check_hf_status(
    project_path: str,
    name: str | None = None,
    timeout: int = 10,
) -> list[DeployStatus]:
    """Check status of a Hugging Face Space.

    *name* should be in ``owner/repo`` format. If not provided, the ``hf``
    git remote is parsed to discover the space.
    """
    owner_repo = name
    if not owner_repo:
        owner_repo = parse_hf_remote(project_path)

    if not owner_repo:
        return [
            DeployStatus(
                name="(unknown)",
                status="error",
                url="",
                message="No HF Space found. Pass name as owner/repo or add a 'hf' git remote.",
            )
        ]

    api_url = f"https://huggingface.co/api/spaces/{owner_repo}"
    space_url = f"https://huggingface.co/spaces/{owner_repo}"
    req = urllib.request.Request(api_url)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        return [
            DeployStatus(
                name=owner_repo,
                status="error",
                url=space_url,
                message=str(e),
            )
        ]
    except (json.JSONDecodeError, KeyError) as e:
        return [
            DeployStatus(
                name=owner_repo,
                status="error",
                url=space_url,
                message=f"Invalid API response: {e}",
            )
        ]

    stage = data.get("runtime", {}).get("stage", "UNKNOWN")
    stage_map = {
        "RUNNING": "live",
        "SLEEPING": "sleep",
        "PAUSED": "sleep",
        "BUILDING": "sleep",
    }
    st = stage_map.get(stage, "down")
    return [
        DeployStatus(
            name=owner_repo,
            status=st,
            url=space_url,
            message=f"Stage: {stage}",
        )
    ]


# ---------------------------------------------------------------------------
# Docker helpers
# ---------------------------------------------------------------------------


def find_docker() -> str:
    """Locate the docker binary.

    Raises:
        click.ClickException: if docker is not found in PATH.
    """
    docker = shutil.which("docker")
    if docker is None:
        raise click.ClickException(
            "docker not found in PATH. Install it: https://docs.docker.com/get-docker/"
        )
    return docker


def docker_build(project_path: str, tag: str) -> bool:
    """Run ``docker build``. Returns True on success."""
    docker = find_docker()
    console = get_console()
    console.print(f"[cyan]Building image:[/cyan] {tag}")

    result = subprocess.run(
        [docker, "build", "-t", tag, project_path],
        timeout=600,
    )
    return result.returncode == 0


def docker_run(tag: str, port: int) -> None:
    """Run a docker container from the given image tag."""
    docker = find_docker()
    console = get_console()
    console.print(f"[cyan]Running container:[/cyan] {tag} on port {port}")

    subprocess.run(
        [docker, "run", "-p", f"{port}:8501", tag],
        timeout=600,
    )


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------


@click.command("preflight")
@click.argument("path", default=".")
@click.option("--skip-tests", is_flag=True, help="Skip running tests.")
@click.option("--skip-lint", is_flag=True, help="Skip running linter.")
def preflight(path: str, skip_tests: bool, skip_lint: bool) -> None:
    """Run pre-deployment checks."""
    console = get_console()
    checks = run_preflight(path, skip_tests=skip_tests, skip_lint=skip_lint)

    from rich.table import Table

    table = Table(title=f"Deploy preflight: {os.path.abspath(path)}")
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
        console.print("\n[bold red]PREFLIGHT FAILED[/bold red] — fix the failing checks above.")
    else:
        console.print("\n[bold green]PREFLIGHT PASSED[/bold green] — ready to deploy!")


@click.command("docker")
@click.argument("path", default=".")
@click.option("--port", default=8501, type=int, help="Host port.")
@click.option("--tag", default=None, help="Docker image tag.")
@click.option("--build-only", is_flag=True, help="Build image without running.")
def docker(path: str, port: int, tag: str | None, build_only: bool) -> None:
    """Build and run a StreamTeX project with Docker."""
    console = get_console()
    p = os.path.abspath(path)

    # 1. Run preflight (skip tests for speed)
    checks = run_preflight(p, skip_tests=True, skip_lint=True)
    fails = [c for c in checks if c.status == "fail"]
    if fails:
        for c in fails:
            console.print(f"  [red]\u2717 {c.name}[/red]: {c.message}")
        raise click.ClickException(
            "Preflight failed. Run 'stx deploy preflight' for details."
        )

    # 2. Generate Dockerfile if missing
    dockerfile_path = os.path.join(p, "Dockerfile")
    if not os.path.isfile(dockerfile_path):
        content = generate_dockerfile()
        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print("[green]Dockerfile generated[/green]")

    # 3. Compute tag from directory name if not provided
    if tag is None:
        tag = os.path.basename(p).lower().replace(" ", "-")

    # 4. Build
    success = docker_build(p, tag)
    if not success:
        raise click.ClickException("Docker build failed.")

    console.print(f"[bold green]Image built:[/bold green] {tag}")

    # 5. Run (unless --build-only)
    if not build_only:
        console.print(f"[cyan]Starting container on port {port}…[/cyan]")
        docker_run(tag, port)
    else:
        console.print("[bold green]Done![/bold green] (build-only mode)")


@click.command("render")
@click.argument("path", default=".")
@click.option("--name", default=None, help="Render service name.")
@click.option("--branch", default="main", help="Git branch.")
@click.option("--plan", default="free", help="Render plan (free, starter, etc.).")
@click.option("--env", "env_pairs", multiple=True, help="KEY=VALUE (repeatable).")
@click.option("--multi", is_flag=True, help="Multi-service mode (one per manual).")
def render_cmd(
    path: str,
    name: str | None,
    branch: str,
    plan: str,
    env_pairs: tuple[str, ...],
    multi: bool,
) -> None:
    """Generate a render.yaml for Render deployment."""
    console = get_console()
    p = os.path.abspath(path)

    # 1. Detect git remote
    repo = detect_git_remote(p)
    if repo is None:
        raise click.ClickException(
            "No git remote 'origin' found. Add one with: git remote add origin <url>"
        )

    # 2. Parse --env pairs
    env_vars = parse_env_vars(env_pairs)

    # 3. Generate Dockerfile if absent
    dockerfile_path = os.path.join(p, "Dockerfile")
    if not os.path.isfile(dockerfile_path):
        content = generate_dockerfile()
        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print("[green]Dockerfile generated[/green]")

    # 4. Generate services
    services: list[str] = []

    if multi:
        manuals = discover_manuals(p)
        if not manuals:
            raise click.ClickException(
                "No manuals/ subdirectories found (stx_manual_* or stx_manuals_*)."
            )

        from rich.table import Table

        table = Table(title="Render services")
        table.add_column("Service", style="cyan")
        table.add_column("Folder")

        for manual in manuals:
            svc_name = derive_service_name(manual)
            svc = generate_render_service(
                name=svc_name,
                repo=repo,
                branch=branch,
                plan=plan,
                env_vars=env_vars,
                folder=manual,
            )
            services.append(svc)
            table.add_row(svc_name, manual)

        console.print(table)
    else:
        svc_name = name or os.path.basename(p).lower().replace(" ", "-")
        svc = generate_render_service(
            name=svc_name,
            repo=repo,
            branch=branch,
            plan=plan,
            env_vars=env_vars,
            build_filter=True,
        )
        services.append(svc)

    # 5. Write render.yaml
    yaml_content = generate_render_yaml(services)
    render_path = os.path.join(p, "render.yaml")
    with open(render_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    console.print(f"[bold green]render.yaml written[/bold green] → {render_path}")
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print("  1. Review render.yaml and update STX_PASSWORD")
    console.print("  2. git add render.yaml Dockerfile && git commit && git push")
    console.print("  3. Connect your repo on https://dashboard.render.com")


@click.command("huggingface")
@click.argument("path", default=".")
@click.option(
    "--space", required=True,
    help="HF Space URL (https://huggingface.co/spaces/user/repo).",
)
@click.option("--title", default=None, help="Space title (defaults to directory name).")
@click.option("--emoji", default="\U0001f4ca", help="Space emoji.")
@click.option("--skip-push", is_flag=True, help="Prepare without pushing to HF.")
def huggingface_cmd(
    path: str,
    space: str,
    title: str | None,
    emoji: str,
    skip_push: bool,
) -> None:
    """Deploy a StreamTeX project to Hugging Face Spaces."""
    console = get_console()
    p = os.path.abspath(path)

    # 1. Preflight (skip tests/lint for speed)
    checks = run_preflight(p, skip_tests=True, skip_lint=True)
    fails = [c for c in checks if c.status == "fail"]
    if fails:
        for c in fails:
            console.print(f"  [red]\u2717 {c.name}[/red]: {c.message}")
        raise click.ClickException(
            "Preflight failed. Run 'stx deploy preflight' for details."
        )

    # 2. Verify git-lfs
    if not verify_git_lfs():
        console.print("[yellow]\u26a0 git-lfs not found — large files may not be tracked[/yellow]")

    # 3. Verify huggingface-cli
    if not verify_hf_cli():
        console.print(
            "[yellow]\u26a0 huggingface-cli not found or not authenticated[/yellow]"
        )

    # 4. Generate Dockerfile if missing
    dockerfile_path = os.path.join(p, "Dockerfile")
    if not os.path.isfile(dockerfile_path):
        content = generate_dockerfile()
        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print("[green]Dockerfile generated[/green]")

    # 5. Setup LFS tracking
    if setup_lfs_tracking(p):
        console.print("[green].gitattributes updated with LFS patterns[/green]")

    # 6. Generate/update README front-matter
    space_title = title or os.path.basename(p)
    fm = generate_hf_frontmatter(space_title, emoji)
    if update_readme_frontmatter(p, fm):
        console.print("[green]README.md front-matter updated[/green]")

    # 7. Setup remote hf
    setup_hf_remote(p, space)
    console.print(f"[green]Git remote 'hf' set to {space}[/green]")

    # 8. Push (unless --skip-push)
    if not skip_push:
        subprocess.run(
            ["git", "-C", p, "add", "."],
            capture_output=True, text=True, timeout=30,
        )
        subprocess.run(
            ["git", "-C", p, "commit", "-m", "Deploy to HF Spaces"],
            capture_output=True, text=True, timeout=30,
        )
        result = subprocess.run(
            ["git", "-C", p, "push", "hf", "main"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            console.print(f"[red]Push failed:[/red] {result.stderr.strip()}")
            raise click.ClickException("git push to HF Spaces failed.")
        console.print("[bold green]Pushed to Hugging Face Spaces![/bold green]")
    else:
        console.print("[cyan]Skip-push mode — files prepared but not pushed[/cyan]")

    # 9. Show Space URL
    console.print(f"\n[bold cyan]Space URL:[/bold cyan] {space}")


@click.command("status")
@click.argument("platform", type=click.Choice(["render", "huggingface", "coolify"]))
@click.argument("name", required=False, default=None)
@click.option("--path", default=".", help="Project path (for service discovery).")
@click.option("--timeout", default=10, type=int, help="HTTP probe timeout in seconds.")
def status_cmd(
    platform: str,
    name: str | None,
    path: str,
    timeout: int,
) -> None:
    """Check deployment status for Render, Hugging Face, or Coolify."""
    console = get_console()
    p = os.path.abspath(path)

    if platform == "coolify":
        _status_coolify(console, name)
        return

    if platform == "render":
        statuses = check_render_status(p, name=name, timeout=timeout)
    else:
        statuses = check_hf_status(p, name=name, timeout=timeout)

    if not statuses:
        console.print("[yellow]No services found.[/yellow]")
        console.print(
            "Hint: provide a service name, add a render.yaml, "
            "or configure a 'hf' git remote."
        )
        return

    from rich.table import Table

    table = Table(title=f"Deploy status: {platform}")
    table.add_column("Service", style="cyan")
    table.add_column("Status")
    table.add_column("URL")

    icons = {
        "live": "[green]\u2713 Live[/green]",
        "sleep": "[yellow]\u25cf Sleep[/yellow]",
        "down": "[red]\u2717 Down[/red]",
        "error": "[red]? Error[/red]",
    }

    for s in statuses:
        table.add_row(s.name, icons.get(s.status, s.status), s.url)

    console.print(table)

    # Show details for non-live services
    for s in statuses:
        if s.status != "live" and s.message:
            console.print(f"  [dim]{s.name}: {s.message}[/dim]")


def _status_coolify(console, name: str | None) -> None:
    """Show Coolify deployment status for all or a specific service."""
    from rich.table import Table

    from .coolify import CoolifyClient, CoolifyError

    try:
        client = CoolifyClient.from_env()
    except CoolifyError as e:
        console.print(f"[red]{e}[/red]")
        console.print("Run [cyan]stx deploy setup[/cyan] to configure credentials.")
        return

    try:
        apps = client.list_apps()
    except CoolifyError as e:
        console.print(f"[red]Failed to list applications: {e}[/red]")
        return

    if name:
        apps = [a for a in apps if name.lower() in a.name.lower() or name == a.uuid]

    if not apps:
        console.print("[yellow]No Coolify applications found.[/yellow]")
        return

    icons = {
        "running:healthy": "[green]\u2713 Healthy[/green]",
        "running:unhealthy": "[yellow]\u26a0 Unhealthy[/yellow]",
        "running:unknown": "[yellow]? Running[/yellow]",
        "exited": "[red]\u2717 Exited[/red]",
        "stopped": "[dim]Stopped[/dim]",
    }

    table = Table(title="Coolify Deployment Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status")
    table.add_column("URL")

    for app in sorted(apps, key=lambda a: a.name):
        status_icon = icons.get(app.status, f"[dim]{app.status}[/dim]")
        table.add_row(app.name, status_icon, app.fqdn)

    console.print(table)


# ---------------------------------------------------------------------------
# Env-sync helpers (Render API)
# ---------------------------------------------------------------------------


def _read_render_cli_config() -> dict[str, str]:
    """Read ``~/.render/cli.yaml`` and return ``{"api_key": ..., "owner_id": ...}``.

    The file is a simple YAML with ``api-key`` and optional ``owner-id`` fields.
    We parse it with basic string matching (no extra dependency needed).

    Raises:
        click.ClickException: if the file is missing or the API key is absent.
    """
    cli_yaml = os.path.expanduser("~/.render/cli.yaml")
    if not os.path.isfile(cli_yaml):
        raise click.ClickException(
            f"Render CLI config not found: {cli_yaml}\n"
            "Install the Render CLI and run 'render login' first."
        )

    with open(cli_yaml, encoding="utf-8") as f:
        content = f.read()

    api_key: str | None = None
    owner_id: str | None = None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("api-key:"):
            api_key = line.split(":", 1)[1].strip().strip("\"'")
        elif line.startswith("owner-id:"):
            owner_id = line.split(":", 1)[1].strip().strip("\"'")

    if not api_key:
        raise click.ClickException(
            f"No api-key found in {cli_yaml}. Run 'render login' first."
        )

    return {"api_key": api_key, "owner_id": owner_id or ""}


def _parse_render_yaml_env_vars(
    project_path: str,
) -> dict[str, list[tuple[str, str]]]:
    """Parse ``render.yaml`` and extract env vars per service.

    Returns ``{service_name: [(key, value), ...]}`` for every service
    that declares ``envVars``.  Uses regex parsing consistent with
    :func:`parse_render_yaml_services`.
    """
    yaml_path = os.path.join(project_path, "render.yaml")
    if not os.path.isfile(yaml_path):
        raise click.ClickException(f"render.yaml not found in {project_path}")

    with open(yaml_path, encoding="utf-8") as f:
        content = f.read()

    # Split into service blocks (each starts with "  - type:")
    blocks = re.split(r"(?=^\s+-\s+type:)", content, flags=re.MULTILINE)

    result: dict[str, list[tuple[str, str]]] = {}
    for block in blocks:
        name_m = re.search(r"^\s+name:\s+(.+)$", block, re.MULTILINE)
        if not name_m:
            continue
        svc_name = name_m.group(1).strip()

        # Extract envVars section
        env_section = re.search(
            r"^\s+envVars:\s*\n((?:\s+-.+\n?|\s+\w.+\n?)*)",
            block,
            re.MULTILINE,
        )
        if not env_section:
            result[svc_name] = []
            continue

        env_text = env_section.group(1)
        keys = re.findall(r"^\s+-\s+key:\s+(.+)$", env_text, re.MULTILINE)
        values = re.findall(r"^\s+value:\s+(.+)$", env_text, re.MULTILINE)

        result[svc_name] = [
            (k.strip(), v.strip()) for k, v in zip(keys, values)
        ]

    return result


def _render_api_get(path: str, api_key: str) -> object:
    """HTTP GET against the Render API v1."""
    url = f"https://api.render.com/v1/{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise click.ClickException(
            f"Render API error ({e.code}): {body}"
        ) from e
    except urllib.error.URLError as e:
        raise click.ClickException(f"Render API unreachable: {e}") from e


def _render_api_put(path: str, api_key: str, body: object) -> object:
    """HTTP PUT against the Render API v1."""
    url = f"https://api.render.com/v1/{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        raise click.ClickException(
            f"Render API error ({e.code}): {body_text}"
        ) from e
    except urllib.error.URLError as e:
        raise click.ClickException(f"Render API unreachable: {e}") from e


def _render_api_post(path: str, api_key: str, body: object = None) -> object:
    """HTTP POST against the Render API v1."""
    url = f"https://api.render.com/v1/{path}"
    data = json.dumps(body).encode() if body else b""
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        raise click.ClickException(
            f"Render API error ({e.code}): {body_text}"
        ) from e
    except urllib.error.URLError as e:
        raise click.ClickException(f"Render API unreachable: {e}") from e


def _resolve_render_service_ids(
    names: list[str],
    api_key: str,
    owner_id: str,
) -> dict[str, str]:
    """Map service *names* to Render service IDs via the API.

    Calls ``GET /services`` and filters by the names declared in
    ``render.yaml``.  Returns ``{name: service_id}``.
    """
    params = "limit=100"
    if owner_id:
        params += f"&ownerId={owner_id}"
    data = _render_api_get(f"services?{params}", api_key)

    # Response is a list of {"service": {...}} wrappers
    mapping: dict[str, str] = {}
    for item in data:
        svc = item.get("service", item)  # handle both shapes
        svc_name = svc.get("name", "")
        svc_id = svc.get("id", "")
        if svc_name in names:
            mapping[svc_name] = svc_id

    return mapping


# ---------------------------------------------------------------------------
# env-sync command
# ---------------------------------------------------------------------------


@click.command("env-sync")
@click.option("--path", default=".", help="Project directory containing render.yaml.")
@click.option("--dry-run", is_flag=True, help="Show changes without applying.")
@click.option("--service", default=None, help="Sync a specific service only.")
def env_sync_cmd(path: str, dry_run: bool, service: str | None) -> None:
    """Sync env vars from render.yaml to live Render services."""
    from rich.table import Table

    console = get_console()
    p = os.path.abspath(path)

    # 1. Parse render.yaml env vars
    yaml_env = _parse_render_yaml_env_vars(p)
    if not yaml_env:
        raise click.ClickException("No services found in render.yaml.")

    # Filter to a single service if requested
    if service:
        if service not in yaml_env:
            raise click.ClickException(
                f"Service '{service}' not found in render.yaml. "
                f"Available: {', '.join(sorted(yaml_env))}"
            )
        yaml_env = {service: yaml_env[service]}

    # 2. Read Render CLI config
    config = _read_render_cli_config()
    api_key = config["api_key"]
    owner_id = config["owner_id"]

    # 3. Resolve service IDs
    console.print("[cyan]Resolving Render service IDs…[/cyan]")
    id_map = _resolve_render_service_ids(list(yaml_env), api_key, owner_id)

    missing = set(yaml_env) - set(id_map)
    if missing:
        console.print(
            f"[yellow]⚠ Services not found on Render: {', '.join(sorted(missing))}[/yellow]"
        )

    # 4. Compare and sync
    any_changes = False

    for svc_name, desired_vars in sorted(yaml_env.items()):
        svc_id = id_map.get(svc_name)
        if not svc_id:
            continue

        # Fetch current env vars from Render
        current_raw = _render_api_get(
            f"services/{svc_id}/env-vars", api_key
        )
        current_map: dict[str, str] = {
            item["key"]: item["value"]
            for item in current_raw
            if "key" in item and "value" in item
        }

        desired_map = dict(desired_vars)

        # Compute diff
        changes: list[tuple[str, str, str]] = []  # (key, current, new)
        for key, new_val in desired_map.items():
            old_val = current_map.get(key, "")
            if old_val != new_val:
                changes.append((key, old_val, new_val))

        if not changes:
            console.print(f"[green]✓ {svc_name}[/green]: already in sync")
            continue

        any_changes = True

        # Display diff table
        table = Table(title=f"Changes for {svc_name}")
        table.add_column("Key", style="cyan")
        table.add_column("Current")
        table.add_column("→")
        table.add_column("New", style="green")

        for key, old_val, new_val in changes:
            display_old = old_val if old_val else "[dim](not set)[/dim]"
            table.add_row(key, display_old, "→", new_val)

        console.print(table)

        # Apply if not dry-run
        if not dry_run:
            # Build the full env var list for PUT (bulk replace)
            put_body = [
                {"key": k, "value": v} for k, v in desired_map.items()
            ]
            _render_api_put(
                f"services/{svc_id}/env-vars", api_key, put_body
            )
            console.print(
                f"  [bold green]✓ {svc_name}[/bold green]: "
                f"{len(changes)} env var(s) updated"
            )

    if dry_run and any_changes:
        console.print(
            "\n[yellow]Dry-run mode — no changes applied. "
            "Remove --dry-run to apply.[/yellow]"
        )
    elif not any_changes:
        console.print("\n[bold green]All services are already in sync.[/bold green]")
    else:
        # Propose redeploy
        console.print()
        if click.confirm("Trigger a redeploy for updated services?", default=False):
            for svc_name in sorted(yaml_env):
                svc_id = id_map.get(svc_name)
                if svc_id:
                    _render_api_post(f"services/{svc_id}/deploys", api_key)
                    console.print(f"  [cyan]↻ {svc_name}[/cyan]: deploy triggered")
            console.print("[bold green]Redeploy triggered![/bold green]")


# ---------------------------------------------------------------------------
# Hetzner / Coolify helpers
# ---------------------------------------------------------------------------


def _read_deploy_env(project_path: str = ".") -> dict[str, str]:
    """Read ``.stx-deploy.env`` from the project or parent directory.

    Returns a dict of KEY=VALUE pairs.  Raises :class:`click.ClickException`
    if the file cannot be found.
    """
    from pathlib import Path

    from .coolify import _parse_env_file

    candidates = [
        Path(project_path).resolve() / ".stx-deploy.env",
        Path(project_path).resolve().parent / ".stx-deploy.env",
        Path.cwd() / ".stx-deploy.env",
        Path.cwd().parent / ".stx-deploy.env",
    ]
    for p in candidates:
        if p.is_file():
            return _parse_env_file(p)

    raise click.ClickException(
        ".stx-deploy.env not found. Run 'stx deploy setup' first."
    )


def _ssh_run(
    ip: str,
    command: str,
    key_path: str = "~/.ssh/hetzner_streamtex",
    user: str = "root",
    timeout: int = 120,
) -> subprocess.CompletedProcess:
    """Run a command on a remote server via SSH."""
    key = os.path.expanduser(key_path)
    return subprocess.run(
        [
            "ssh", "-i", key,
            "-o", "StrictHostKeyChecking=accept-new",
            f"{user}@{ip}",
            command,
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# stx deploy setup — interactive local setup
# ---------------------------------------------------------------------------


@click.command("setup")
def setup_cmd() -> None:
    """Interactive setup for Hetzner/Coolify deployment."""
    console = get_console()
    env_vars: dict[str, str] = {}

    console.print("[bold cyan]StreamTeX Deploy Setup[/bold cyan]")
    console.print("This will configure your local environment for Hetzner deployment.\n")

    # 1. Check hcloud CLI
    hcloud = shutil.which("hcloud")
    if hcloud:
        console.print("[green]\u2713 hcloud CLI found[/green]")
    else:
        console.print("[yellow]\u26a0 hcloud CLI not found[/yellow]")
        if click.confirm("Install hcloud CLI now?", default=True):
            import platform as _platform

            if _platform.system() == "Darwin":
                subprocess.run(["brew", "install", "hcloud"], timeout=120)
            else:
                subprocess.run(
                    ["sh", "-c", "apt-get update && apt-get install -y hcloud-cli"],
                    timeout=120,
                )
            hcloud = shutil.which("hcloud")
            if hcloud:
                console.print("[green]\u2713 hcloud CLI installed[/green]")
            else:
                console.print("[red]\u2717 hcloud CLI installation failed[/red]")

    # 2. Check SSH key
    ssh_key_path = os.path.expanduser("~/.ssh/hetzner_streamtex")
    if os.path.isfile(ssh_key_path):
        console.print(f"[green]\u2713 SSH key found:[/green] {ssh_key_path}")
    else:
        console.print(f"[yellow]\u26a0 SSH key not found:[/yellow] {ssh_key_path}")
        if click.confirm("Generate SSH key now?", default=True):
            os.makedirs(os.path.dirname(ssh_key_path), exist_ok=True)
            subprocess.run(
                [
                    "ssh-keygen", "-t", "ed25519",
                    "-f", ssh_key_path,
                    "-N", "",
                    "-C", "streamtex-deploy",
                ],
                timeout=30,
            )
            if os.path.isfile(ssh_key_path):
                console.print("[green]\u2713 SSH key generated[/green]")
            else:
                console.print("[red]\u2717 SSH key generation failed[/red]")

    # 3. Hetzner API token
    console.print(
        "\n[cyan]Hetzner API token[/cyan] — "
        "create one at https://console.hetzner.cloud → Security → API Tokens"
    )
    hetzner_token = click.prompt("Hetzner API token", hide_input=True)
    env_vars["HETZNER_API_TOKEN"] = hetzner_token

    # 4. Register SSH key in Hetzner
    if hcloud and os.path.isfile(f"{ssh_key_path}.pub"):
        console.print("[cyan]Registering SSH key in Hetzner…[/cyan]")
        result = subprocess.run(
            [
                "hcloud", "ssh-key", "create",
                "--name", "streamtex-deploy",
                "--public-key-from-file", f"{ssh_key_path}.pub",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "HCLOUD_TOKEN": hetzner_token},
        )
        if result.returncode == 0:
            console.print("[green]\u2713 SSH key registered in Hetzner[/green]")
        else:
            console.print(
                f"[yellow]\u26a0 SSH key registration: {result.stderr.strip()}[/yellow]"
            )

    # 5. Domain name
    domain = click.prompt("Domain name (e.g. streamtex.org)")
    env_vars["DEPLOY_DOMAIN"] = domain

    # 6. Cloudflare API token (optional)
    if click.confirm("Configure Cloudflare DNS integration?", default=False):
        cf_token = click.prompt("Cloudflare API token", hide_input=True)
        env_vars["CLOUDFLARE_API_TOKEN"] = cf_token

    # 7. Save .stx-deploy.env
    env_path = os.path.join(".", ".stx-deploy.env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# StreamTeX Deploy Configuration\n")
        f.write("# Generated by: stx deploy setup\n\n")
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    console.print(f"\n[bold green]\u2713 Configuration saved to {env_path}[/bold green]")

    # Remind about .gitignore
    console.print(
        "\n[yellow]Important:[/yellow] Ensure .stx-deploy.env is in your .gitignore!"
    )


# ---------------------------------------------------------------------------
# stx deploy hetzner — deploy project to Hetzner/Coolify
# ---------------------------------------------------------------------------


@click.command("hetzner")
@click.argument("path", default=".")
@click.option("--subdomain", default=None, help="Subdomain for the service.")
@click.option("--uuid", default=None, help="Coolify application UUID (skip creation).")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts.")
def hetzner_cmd(path: str, subdomain: str | None, uuid: str | None, yes: bool) -> None:
    """Deploy a StreamTeX project to Hetzner via Coolify."""
    from .coolify import CoolifyClient, CoolifyError, load_deploy_state, save_deploy_state

    console = get_console()
    p = os.path.abspath(path)

    # 1. Read .stx-deploy.env
    try:
        env = _read_deploy_env(p)
    except click.ClickException:
        console.print(
            "[red]No .stx-deploy.env found.[/red]\n"
            "Run [cyan]stx deploy setup[/cyan] first."
        )
        raise

    # 2. Run preflight checks
    console.print("[cyan]Running preflight checks…[/cyan]")
    checks = run_preflight(p, skip_tests=True, skip_lint=True)
    fails = [c for c in checks if c.status == "fail"]
    if fails:
        for c in fails:
            console.print(f"  [red]\u2717 {c.name}[/red]: {c.message}")
        raise click.ClickException(
            "Preflight failed. Run 'stx deploy preflight' for details."
        )
    console.print("[green]\u2713 Preflight passed[/green]")

    # 3. Detect git remote
    repo = detect_git_remote(p)
    if repo is None:
        raise click.ClickException(
            "No git remote 'origin' found. Add one with: git remote add origin <url>"
        )
    console.print(f"[green]\u2713 Git remote:[/green] {repo}")

    # 4. Prompt for subdomain
    if not subdomain:
        domain = env.get("DEPLOY_DOMAIN", "streamtex.org")
        default_sub = os.path.basename(p).lower().replace("_", "-").replace(" ", "-")
        subdomain = click.prompt(
            f"Subdomain (*.{domain})", default=default_sub
        )

    domain = env.get("DEPLOY_DOMAIN", "streamtex.org")
    fqdn = f"https://{subdomain}.{domain}"
    console.print(f"[cyan]Target URL:[/cyan] {fqdn}")

    if not yes and not click.confirm("Proceed with deployment?", default=True):
        console.print("[yellow]Aborted.[/yellow]")
        return

    # 5. Connect to Coolify
    try:
        client = CoolifyClient.from_env()
    except CoolifyError as e:
        raise click.ClickException(str(e)) from e

    # 6. Resolve or guide application creation
    app_uuid = uuid
    if not app_uuid:
        # Check deploy state for existing UUID
        state = load_deploy_state()
        services = state.get("services", {})
        for _name, svc_info in services.items():
            if isinstance(svc_info, dict) and svc_info.get("subdomain") == subdomain:
                app_uuid = svc_info.get("uuid")
                console.print(f"[green]\u2713 Found existing app:[/green] {app_uuid}")
                break

    if not app_uuid:
        console.print(
            "\n[yellow]Coolify application not found.[/yellow]\n"
            "Please create the application in the Coolify UI:\n"
            f"  1. Go to your Coolify dashboard\n"
            f"  2. Create a new application from GitHub repo: {repo}\n"
            f"  3. Set the domain to: {fqdn}\n"
            "  4. Copy the application UUID from the URL\n"
        )
        app_uuid = click.prompt("Coolify application UUID")

    # 7. Set FOLDER env var if in manuals/ subdirectory
    rel_path = os.path.basename(p)
    parent = os.path.basename(os.path.dirname(p))
    if parent == "manuals" or rel_path.startswith("stx_manual"):
        folder = f"manuals/{rel_path}"
        console.print(f"[cyan]Setting FOLDER={folder}[/cyan]")
        try:
            client.set_env_var(app_uuid, "FOLDER", folder)
        except CoolifyError as e:
            console.print(f"[yellow]\u26a0 Could not set FOLDER: {e}[/yellow]")

    # 8. Set FQDN
    try:
        client.set_fqdn(app_uuid, fqdn)
        console.print(f"[green]\u2713 Domain set:[/green] {fqdn}")
    except CoolifyError as e:
        console.print(f"[yellow]\u26a0 Could not set domain: {e}[/yellow]")

    # 9. Trigger rebuild
    console.print("[cyan]Triggering rebuild…[/cyan]")
    result = client.rebuild(app_uuid)
    if not result.success:
        raise click.ClickException(f"Rebuild failed: {result.message}")
    console.print(f"[green]\u2713 Rebuild triggered:[/green] {result.message}")

    # 10. Wait for healthy
    console.print("[cyan]Waiting for service to become healthy…[/cyan]")
    healthy = client.wait_healthy(app_uuid, timeout=300)
    if healthy:
        console.print("[bold green]\u2713 Service is healthy![/bold green]")
    else:
        console.print(
            "[yellow]\u26a0 Service did not reach healthy state within timeout.[/yellow]\n"
            "Check the Coolify dashboard for deployment logs."
        )

    # 11. Update .stx-deploy.json
    state = load_deploy_state()
    if "services" not in state:
        state["services"] = {}
    state["services"][subdomain] = {
        "uuid": app_uuid,
        "subdomain": subdomain,
        "fqdn": fqdn,
        "repo": repo,
    }
    save_deploy_state(state)
    console.print("[green]\u2713 State saved to .stx-deploy.json[/green]")
    console.print(f"\n[bold cyan]Deployed:[/bold cyan] {fqdn}")


# ---------------------------------------------------------------------------
# stx deploy update — rebuild/restart services
# ---------------------------------------------------------------------------


@click.command("update")
@click.argument("target", required=False, default=None)
@click.option("--quick", is_flag=True, help="Quick restart (no rebuild).")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts.")
def update_cmd(target: str | None, quick: bool, yes: bool) -> None:
    """Rebuild or restart a Coolify service.

    TARGET can be a service name, subdomain, or Coolify UUID.
    If omitted, lists all services and prompts for selection.
    """
    from .coolify import CoolifyClient, CoolifyError, load_deploy_state

    console = get_console()

    try:
        client = CoolifyClient.from_env()
    except CoolifyError as e:
        raise click.ClickException(str(e)) from e

    # Resolve target UUID
    app_uuid = target
    app_name = target or "(unknown)"

    if target and not _looks_like_uuid(target):
        # Try to find UUID from deploy state
        state = load_deploy_state()
        services = state.get("services", {})
        for name, svc_info in services.items():
            if isinstance(svc_info, dict) and (
                name == target
                or svc_info.get("subdomain") == target
                or svc_info.get("uuid") == target
            ):
                app_uuid = svc_info.get("uuid")
                app_name = name
                break

    if not target:
        # List all services and prompt
        try:
            apps = client.list_apps()
        except CoolifyError as e:
            raise click.ClickException(str(e)) from e

        if not apps:
            raise click.ClickException("No applications found in Coolify.")

        from rich.table import Table

        table = Table(title="Coolify Applications")
        table.add_column("#", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Status")
        table.add_column("UUID", style="dim")

        for i, app in enumerate(apps, 1):
            table.add_row(str(i), app.name, app.status, app.uuid)

        console.print(table)
        choice = click.prompt("Select application number", type=int)
        if choice < 1 or choice > len(apps):
            raise click.ClickException(f"Invalid selection: {choice}")
        selected = apps[choice - 1]
        app_uuid = selected.uuid
        app_name = selected.name

    if not app_uuid:
        raise click.ClickException(
            f"Could not resolve target '{target}'. "
            "Provide a valid UUID, service name, or subdomain."
        )

    action = "restart" if quick else "rebuild"
    if not yes:
        if not click.confirm(f"{action.capitalize()} {app_name} ({app_uuid})?", default=True):
            console.print("[yellow]Aborted.[/yellow]")
            return

    console.print(f"[cyan]Triggering {action}…[/cyan]")
    if quick:
        result = client.restart(app_uuid)
    else:
        result = client.rebuild(app_uuid)

    if not result.success:
        raise click.ClickException(f"{action.capitalize()} failed: {result.message}")

    console.print(f"[bold green]\u2713 {action.capitalize()} triggered:[/bold green] {result.message}")

    if not quick:
        console.print("[cyan]Waiting for service to become healthy…[/cyan]")
        healthy = client.wait_healthy(app_uuid, timeout=300)
        if healthy:
            console.print("[bold green]\u2713 Service is healthy![/bold green]")
        else:
            console.print(
                "[yellow]\u26a0 Service did not reach healthy state within timeout.[/yellow]"
            )


def _looks_like_uuid(value: str) -> bool:
    """Check if a string looks like a Coolify UUID (contains hyphens and alphanums)."""
    return len(value) > 8 and "-" in value and all(
        c.isalnum() or c == "-" for c in value
    )


# ---------------------------------------------------------------------------
# stx deploy provision — create Hetzner server
# ---------------------------------------------------------------------------


@click.command("provision")
@click.option("--name", default="streamtex-prod", help="Server name.")
@click.option("--type", "server_type", default="cax21", help="Server type (e.g. cax21).")
@click.option("--image", default="ubuntu-24.04", help="OS image.")
@click.option("--location", default="fsn1", help="Datacenter location.")
@click.option("--ssh-key-name", default="streamtex-deploy", help="SSH key name in Hetzner.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts.")
def provision_cmd(
    name: str,
    server_type: str,
    image: str,
    location: str,
    ssh_key_name: str,
    yes: bool,
) -> None:
    """Create a Hetzner server for StreamTeX deployment."""
    from .coolify import load_deploy_state, save_deploy_state

    console = get_console()

    # Check hcloud CLI
    hcloud = shutil.which("hcloud")
    if not hcloud:
        raise click.ClickException(
            "hcloud CLI not found. Install it: brew install hcloud (macOS) "
            "or apt install hcloud-cli (Linux)."
        )

    # Read Hetzner token
    env = _read_deploy_env()
    hetzner_token = env.get("HETZNER_API_TOKEN")
    if not hetzner_token:
        raise click.ClickException(
            "HETZNER_API_TOKEN not found in .stx-deploy.env. Run 'stx deploy setup' first."
        )

    console.print("[cyan]Server configuration:[/cyan]")
    console.print(f"  Name:     {name}")
    console.print(f"  Type:     {server_type}")
    console.print(f"  Image:    {image}")
    console.print(f"  Location: {location}")
    console.print(f"  SSH key:  {ssh_key_name}")

    if not yes and not click.confirm("\nCreate this server?", default=True):
        console.print("[yellow]Aborted.[/yellow]")
        return

    console.print("[cyan]Creating server…[/cyan]")
    result = subprocess.run(
        [
            hcloud, "server", "create",
            "--name", name,
            "--type", server_type,
            "--image", image,
            "--location", location,
            "--ssh-key", ssh_key_name,
        ],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "HCLOUD_TOKEN": hetzner_token},
    )

    if result.returncode != 0:
        raise click.ClickException(f"Server creation failed:\n{result.stderr.strip()}")

    console.print("[green]\u2713 Server created[/green]")
    console.print(result.stdout.strip())

    # Extract IP address from hcloud output
    ip_result = subprocess.run(
        [hcloud, "server", "ip", name],
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "HCLOUD_TOKEN": hetzner_token},
    )
    server_ip = ip_result.stdout.strip() if ip_result.returncode == 0 else ""

    if server_ip:
        console.print(f"[bold green]Server IP:[/bold green] {server_ip}")

    # Save to .stx-deploy.json
    state = load_deploy_state()
    if "infrastructure" not in state:
        state["infrastructure"] = {}
    state["infrastructure"]["server"] = {
        "name": name,
        "type": server_type,
        "image": image,
        "location": location,
        "ip": server_ip,
    }
    save_deploy_state(state)
    console.print("[green]\u2713 Server info saved to .stx-deploy.json[/green]")

    console.print(
        "\n[cyan]Next steps:[/cyan]\n"
        "  1. stx deploy secure     — harden the server\n"
        "  2. stx deploy install-coolify — install Coolify\n"
        "  3. stx deploy configure-domain — setup DNS"
    )


# ---------------------------------------------------------------------------
# stx deploy secure — harden server via SSH
# ---------------------------------------------------------------------------


@click.command("secure")
@click.option("--ip", default=None, help="Server IP address.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts.")
def secure_cmd(ip: str | None, yes: bool) -> None:
    """Harden a Hetzner server (firewall, fail2ban, SSH hardening)."""
    from .coolify import load_deploy_state

    console = get_console()

    # Resolve IP
    if not ip:
        state = load_deploy_state()
        ip = state.get("infrastructure", {}).get("server", {}).get("ip")
    if not ip:
        ip = click.prompt("Server IP address")

    console.print(f"[cyan]Target server:[/cyan] {ip}")
    console.print(
        "\nThis will:\n"
        "  1. Create a deploy user with sudo access\n"
        "  2. Harden sshd_config (disable password auth, root login)\n"
        "  3. Setup UFW firewall (allow 22, 80, 443, 8000)\n"
        "  4. Install fail2ban\n"
        "  5. Enable unattended-upgrades\n"
    )

    if not yes and not click.confirm("Proceed with server hardening?", default=True):
        console.print("[yellow]Aborted.[/yellow]")
        return

    key_path = os.path.expanduser("~/.ssh/hetzner_streamtex")

    # Step 1: Create deploy user
    console.print("[cyan]Creating deploy user…[/cyan]")
    commands_to_run = [
        # Create user and copy SSH key
        (
            "useradd -m -s /bin/bash -G sudo deploy 2>/dev/null || true && "
            "mkdir -p /home/deploy/.ssh && "
            "cp /root/.ssh/authorized_keys /home/deploy/.ssh/ && "
            "chown -R deploy:deploy /home/deploy/.ssh && "
            "echo 'deploy ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/deploy"
        ),
        # Step 2: Harden sshd_config
        (
            "sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config && "
            "sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && "
            "sed -i 's/^#\\?ChallengeResponseAuthentication.*/"
            "ChallengeResponseAuthentication no/' /etc/ssh/sshd_config && "
            "systemctl restart sshd"
        ),
        # Step 3: Setup UFW
        (
            "apt-get update -qq && apt-get install -y -qq ufw > /dev/null && "
            "ufw default deny incoming && "
            "ufw default allow outgoing && "
            "ufw allow 22/tcp && "
            "ufw allow 80/tcp && "
            "ufw allow 443/tcp && "
            "ufw allow 8000/tcp && "
            "echo 'y' | ufw enable"
        ),
        # Step 4: Install fail2ban
        (
            "apt-get install -y -qq fail2ban > /dev/null && "
            "systemctl enable fail2ban && "
            "systemctl start fail2ban"
        ),
        # Step 5: Enable unattended-upgrades
        (
            "apt-get install -y -qq unattended-upgrades > /dev/null && "
            "dpkg-reconfigure -plow unattended-upgrades 2>/dev/null || "
            "echo 'Unattended-Upgrade::Automatic-Reboot \"false\";' > "
            "/etc/apt/apt.conf.d/50unattended-upgrades-local"
        ),
    ]

    step_names = [
        "Deploy user",
        "SSH hardening",
        "UFW firewall",
        "fail2ban",
        "Unattended upgrades",
    ]

    for step_name, cmd in zip(step_names, commands_to_run):
        console.print(f"  [cyan]{step_name}…[/cyan]")
        result = _ssh_run(ip, cmd, key_path, timeout=120)
        if result.returncode == 0:
            console.print(f"  [green]\u2713 {step_name}[/green]")
        else:
            console.print(
                f"  [yellow]\u26a0 {step_name}: {result.stderr.strip()[:200]}[/yellow]"
            )

    console.print("\n[bold green]\u2713 Server hardening complete![/bold green]")


# ---------------------------------------------------------------------------
# stx deploy install-coolify — install Coolify on server
# ---------------------------------------------------------------------------


@click.command("install-coolify")
@click.option("--ip", default=None, help="Server IP address.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts.")
def install_coolify_cmd(ip: str | None, yes: bool) -> None:
    """Install Coolify on a Hetzner server."""
    import time

    from .coolify import load_deploy_state, save_deploy_state

    console = get_console()

    # Resolve IP
    if not ip:
        state = load_deploy_state()
        ip = state.get("infrastructure", {}).get("server", {}).get("ip")
    if not ip:
        ip = click.prompt("Server IP address")

    console.print(f"[cyan]Target server:[/cyan] {ip}")

    if not yes and not click.confirm("Install Coolify on this server?", default=True):
        console.print("[yellow]Aborted.[/yellow]")
        return

    key_path = os.path.expanduser("~/.ssh/hetzner_streamtex")

    # Run the Coolify installer
    console.print("[cyan]Installing Coolify (this may take a few minutes)…[/cyan]")
    result = _ssh_run(
        ip,
        "curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash",
        key_path,
        timeout=600,
    )

    if result.returncode != 0:
        console.print(f"[red]Installation output:[/red]\n{result.stderr.strip()[:500]}")
        raise click.ClickException("Coolify installation failed.")

    console.print("[green]\u2713 Coolify installer completed[/green]")

    # Poll until port 8000 responds
    console.print("[cyan]Waiting for Coolify to start (port 8000)…[/cyan]")
    coolify_url = f"http://{ip}:8000"
    for attempt in range(30):
        try:
            req = urllib.request.Request(coolify_url, method="HEAD")
            with urllib.request.urlopen(req, timeout=5):  # noqa: S310
                console.print("[green]\u2713 Coolify is responding![/green]")
                break
        except (urllib.error.URLError, OSError):
            time.sleep(10)
    else:
        console.print(
            "[yellow]\u26a0 Coolify did not respond within timeout.[/yellow]\n"
            f"Try accessing manually: {coolify_url}"
        )

    # Guide browser onboarding
    console.print(
        f"\n[bold cyan]Complete setup in your browser:[/bold cyan]\n"
        f"  1. Open {coolify_url}\n"
        "  2. Create your admin account\n"
        "  3. Go to Settings → API → Generate a new token\n"
        "  4. Copy the API token\n"
    )

    coolify_token = click.prompt("Coolify API token", hide_input=True)

    # Save to .stx-deploy.env
    env_path = None
    from pathlib import Path

    for candidate in [Path.cwd() / ".stx-deploy.env", Path.cwd().parent / ".stx-deploy.env"]:
        if candidate.is_file():
            env_path = candidate
            break

    if env_path is None:
        env_path = Path.cwd() / ".stx-deploy.env"

    with open(env_path, "a", encoding="utf-8") as f:
        f.write(f"\n# Coolify\nCOOLIFY_URL=https://coolify.{_read_deploy_env().get('DEPLOY_DOMAIN', ip)}\n")
        f.write(f"COOLIFY_API_TOKEN={coolify_token}\n")

    console.print(f"[green]\u2713 Coolify credentials saved to {env_path}[/green]")

    # Update deploy state
    state = load_deploy_state()
    if "infrastructure" not in state:
        state["infrastructure"] = {}
    state["infrastructure"]["coolify"] = {
        "url": coolify_url,
    }
    save_deploy_state(state)
    console.print("[green]\u2713 State updated[/green]")
    console.print("\n[bold green]\u2713 Coolify installed and configured![/bold green]")


# ---------------------------------------------------------------------------
# stx deploy configure-domain — setup DNS + SSL
# ---------------------------------------------------------------------------


@click.command("configure-domain")
@click.option("--domain", default=None, help="Domain name to configure.")
@click.option("--ip", default=None, help="Server IP address.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts.")
def configure_domain_cmd(domain: str | None, ip: str | None, yes: bool) -> None:
    """Setup DNS records and SSL for the deployment domain."""
    from .coolify import CoolifyClient, CoolifyError, load_deploy_state

    console = get_console()

    # Resolve domain and IP
    env = _read_deploy_env()
    if not domain:
        domain = env.get("DEPLOY_DOMAIN")
    if not domain:
        domain = click.prompt("Domain name")

    if not ip:
        state = load_deploy_state()
        ip = state.get("infrastructure", {}).get("server", {}).get("ip")
    if not ip:
        ip = click.prompt("Server IP address")

    console.print(f"[cyan]Domain:[/cyan] {domain}")
    console.print(f"[cyan]Server IP:[/cyan] {ip}")

    # Display required DNS records
    console.print("\n[bold]Required DNS records:[/bold]")

    from rich.table import Table

    table = Table()
    table.add_column("Type", style="cyan")
    table.add_column("Name")
    table.add_column("Value")
    table.add_column("Proxy")

    records = [
        ("A", domain, ip, "Yes"),
        ("A", f"*.{domain}", ip, "Yes"),
        ("A", f"coolify.{domain}", ip, "No (DNS only)"),
    ]
    for rtype, name, value, proxy in records:
        table.add_row(rtype, name, value, proxy)

    console.print(table)

    # Try Cloudflare API if token available
    cf_token = env.get("CLOUDFLARE_API_TOKEN")
    if cf_token:
        console.print("\n[cyan]Cloudflare API token found — attempting DNS setup…[/cyan]")

        if not yes and not click.confirm("Create DNS records via Cloudflare API?", default=True):
            console.print("[yellow]Skipping Cloudflare DNS setup.[/yellow]")
        else:
            _setup_cloudflare_dns(cf_token, domain, ip, console)
    else:
        console.print(
            "\n[yellow]No Cloudflare API token found.[/yellow]\n"
            "Create the DNS records manually in your DNS provider.\n"
            "Once DNS propagates, Coolify will handle SSL via Let's Encrypt."
        )

    # Wait for DNS propagation
    if click.confirm("\nCheck DNS propagation now?", default=True):
        console.print("[cyan]Checking DNS…[/cyan]")
        try:
            import socket

            resolved = socket.gethostbyname(domain)
            if resolved == ip:
                console.print(f"[green]\u2713 {domain} resolves to {ip}[/green]")
            else:
                console.print(
                    f"[yellow]\u26a0 {domain} resolves to {resolved} (expected {ip})[/yellow]"
                )
        except socket.gaierror:
            console.print(f"[yellow]\u26a0 {domain} does not resolve yet[/yellow]")

    # Configure Coolify instance domain
    try:
        CoolifyClient.from_env()  # verify connectivity
        console.print("[cyan]Coolify domain configuration should be set via the UI.[/cyan]")
        console.print(
            f"  Go to Settings → FQDN and set it to: https://coolify.{domain}"
        )
    except CoolifyError:
        console.print(
            "[dim]Coolify client not available — configure domain via the Coolify UI.[/dim]"
        )

    console.print(f"\n[bold green]\u2713 Domain configuration complete for {domain}[/bold green]")


def _setup_cloudflare_dns(
    token: str, domain: str, ip: str, console: object
) -> None:
    """Create DNS records via the Cloudflare API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Get zone ID
    zone_url = f"https://api.cloudflare.com/client/v4/zones?name={domain}"
    req = urllib.request.Request(zone_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, OSError) as e:
        console.print(f"[red]Cloudflare API error: {e}[/red]")
        return

    zones = data.get("result", [])
    if not zones:
        console.print(f"[red]Zone '{domain}' not found in Cloudflare.[/red]")
        return

    zone_id = zones[0]["id"]
    console.print(f"[green]\u2713 Zone found:[/green] {zone_id}")

    # Create DNS records
    dns_records = [
        {"type": "A", "name": domain, "content": ip, "proxied": True},
        {"type": "A", "name": f"*.{domain}", "content": ip, "proxied": True},
        {"type": "A", "name": f"coolify.{domain}", "content": ip, "proxied": False},
    ]

    for record in dns_records:
        record_data = json.dumps(record).encode()
        create_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        req = urllib.request.Request(create_url, data=record_data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
                result = json.loads(resp.read().decode())
            if result.get("success"):
                console.print(f"  [green]\u2713 {record['type']} {record['name']}[/green]")
            else:
                errors = result.get("errors", [])
                msg = errors[0].get("message", "Unknown error") if errors else "Unknown error"
                console.print(f"  [yellow]\u26a0 {record['name']}: {msg}[/yellow]")
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            try:
                err_data = json.loads(body)
                errors = err_data.get("errors", [])
                msg = errors[0].get("message", body) if errors else body
            except (json.JSONDecodeError, IndexError):
                msg = body
            console.print(f"  [yellow]\u26a0 {record['name']}: {msg}[/yellow]")
        except (urllib.error.URLError, OSError) as e:
            console.print(f"  [red]{record['name']}: {e}[/red]")
