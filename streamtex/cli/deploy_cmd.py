"""Deploy commands: preflight, docker, and render."""

import glob
import os
import re
import shutil
import subprocess
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
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

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
