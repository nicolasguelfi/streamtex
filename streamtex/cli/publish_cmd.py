"""Publish commands: check readiness and upload to PyPI."""

import os
import subprocess
from dataclasses import dataclass

import click

from .console import get_console
from .deploy_cmd import _find_uv

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class PublishCheck:
    """Result of a single publish-readiness check."""

    name: str
    status: str  # "pass" | "warn" | "fail"
    message: str


# ---------------------------------------------------------------------------
# Publish checks
# ---------------------------------------------------------------------------


def run_publish_checks(
    project_path: str,
    *,
    skip_tests: bool = False,
    skip_lint: bool = False,
) -> list[PublishCheck]:
    """Run pre-publish checks. Return a list of check results."""
    checks: list[PublishCheck] = []
    p = os.path.abspath(project_path)

    # 1. pyproject.toml valid
    pyproject_path = os.path.join(p, "pyproject.toml")
    data = None
    if os.path.isfile(pyproject_path):
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            checks.append(PublishCheck("pyproject.toml", "pass", "Valid"))
        except Exception as exc:
            checks.append(PublishCheck("pyproject.toml", "fail", f"Parse error: {exc}"))
    else:
        checks.append(PublishCheck("pyproject.toml", "fail", "Missing"))

    # 2. version present
    version = data.get("project", {}).get("version", "") if data else ""
    if version:
        checks.append(PublishCheck("version", "pass", version))
    else:
        checks.append(PublishCheck("version", "fail", "No project.version found"))

    # 3. README.md exists
    if os.path.isfile(os.path.join(p, "README.md")):
        checks.append(PublishCheck("README.md", "pass", "Found"))
    else:
        checks.append(PublishCheck("README.md", "fail", "Missing"))

    # 4. LICENSE file exists
    license_found = any(
        os.path.isfile(os.path.join(p, name))
        for name in ("LICENSE", "LICENSE.txt", "LICENSE.md")
    )
    if license_found:
        checks.append(PublishCheck("LICENSE", "pass", "Found"))
    else:
        checks.append(PublishCheck("LICENSE", "fail", "Missing"))

    # 5. __version__ matches pyproject.toml
    init_path = os.path.join(p, "streamtex", "__init__.py")
    if version and os.path.isfile(init_path):
        try:
            init_version = None
            with open(init_path, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("__version__"):
                        init_version = line.split("=", 1)[1].strip().strip("\"'")
                        break
            if init_version == version:
                checks.append(PublishCheck("__version__", "pass", f"Matches ({version})"))
            elif init_version is None:
                checks.append(
                    PublishCheck("__version__", "fail", "Not found in __init__.py")
                )
            else:
                checks.append(
                    PublishCheck(
                        "__version__", "fail",
                        f"Mismatch: __init__={init_version}, pyproject={version}",
                    )
                )
        except OSError:
            checks.append(PublishCheck("__version__", "warn", "Could not read __init__.py"))
    elif not version:
        checks.append(PublishCheck("__version__", "fail", "No version to compare"))
    else:
        checks.append(PublishCheck("__version__", "warn", "streamtex/__init__.py not found"))

    # 6. No dev deps in dependencies
    if data:
        deps = data.get("project", {}).get("dependencies", [])
        dev_pkgs = {"pytest", "ruff", "rich", "click"}
        found_dev = [d for d in deps if any(d.split("[")[0].strip() in dev_pkgs for _ in [0])]
        if found_dev:
            checks.append(
                PublishCheck(
                    "no dev deps", "fail",
                    f"Dev packages in dependencies: {', '.join(found_dev)}",
                )
            )
        else:
            checks.append(PublishCheck("no dev deps", "pass", "Clean"))
    else:
        checks.append(PublishCheck("no dev deps", "fail", "No pyproject.toml to check"))

    # 7. Tests pass (skippable)
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
                    checks.append(PublishCheck("tests", "pass", "All tests pass"))
                else:
                    checks.append(PublishCheck("tests", "fail", "Tests failed"))
            except (subprocess.TimeoutExpired, OSError):
                checks.append(PublishCheck("tests", "fail", "Test run error"))
        else:
            checks.append(PublishCheck("tests", "warn", "uv not found — skipped"))

    # 8. Lint clean (skippable)
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
                    checks.append(PublishCheck("lint", "pass", "Clean"))
                else:
                    checks.append(PublishCheck("lint", "warn", "Lint issues found"))
            except (subprocess.TimeoutExpired, OSError):
                checks.append(PublishCheck("lint", "warn", "Lint run error"))
        else:
            checks.append(PublishCheck("lint", "warn", "uv not found — skipped"))

    # 9. Package builds
    uv = _find_uv()
    if uv:
        try:
            result = subprocess.run(
                [uv, "build"],
                cwd=p,
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                checks.append(PublishCheck("build", "pass", "uv build succeeded"))
            else:
                checks.append(PublishCheck("build", "fail", "uv build failed"))
        except (subprocess.TimeoutExpired, OSError):
            checks.append(PublishCheck("build", "fail", "Build error"))
    else:
        checks.append(PublishCheck("build", "warn", "uv not found — skipped"))

    # 10. dist files exist after build
    dist_dir = os.path.join(p, "dist")
    if os.path.isdir(dist_dir):
        dist_files = os.listdir(dist_dir)
        has_whl = any(f.endswith(".whl") for f in dist_files)
        has_tar = any(f.endswith(".tar.gz") for f in dist_files)
        if has_whl and has_tar:
            checks.append(PublishCheck("dist files", "pass", "Found .whl and .tar.gz"))
        else:
            missing = []
            if not has_whl:
                missing.append(".whl")
            if not has_tar:
                missing.append(".tar.gz")
            checks.append(
                PublishCheck("dist files", "fail", f"Missing: {', '.join(missing)}")
            )
    else:
        checks.append(PublishCheck("dist files", "fail", "No dist/ directory"))

    return checks


# ---------------------------------------------------------------------------
# Click commands
# ---------------------------------------------------------------------------


@click.command("check")
@click.argument("path", default=".")
@click.option("--skip-tests", is_flag=True, help="Skip running tests.")
@click.option("--skip-lint", is_flag=True, help="Skip running linter.")
def check_cmd(path: str, skip_tests: bool, skip_lint: bool) -> None:
    """Check package readiness for PyPI publication."""
    console = get_console()
    checks = run_publish_checks(path, skip_tests=skip_tests, skip_lint=skip_lint)

    from rich.table import Table

    table = Table(title=f"Publish check: {os.path.abspath(path)}")
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
        console.print("\n[bold red]PUBLISH CHECK FAILED[/bold red] — fix issues above.")
    else:
        console.print("\n[bold green]PUBLISH CHECK PASSED[/bold green] — ready to publish!")


@click.command("pypi")
@click.argument("path", default=".")
@click.option("--test", "use_test_pypi", is_flag=True, help="Publish to TestPyPI.")
@click.option("--skip-tests", is_flag=True, help="Skip tests in pre-publish check.")
@click.option("--skip-lint", is_flag=True, help="Skip lint in pre-publish check.")
def pypi_cmd(path: str, use_test_pypi: bool, skip_tests: bool, skip_lint: bool) -> None:
    """Build and publish package to PyPI."""
    console = get_console()
    p = os.path.abspath(path)

    # 1. Run publish checks
    checks = run_publish_checks(p, skip_tests=skip_tests, skip_lint=skip_lint)
    fails = [c for c in checks if c.status == "fail"]
    if fails:
        for c in fails:
            console.print(f"  [red]\u2717 {c.name}[/red]: {c.message}")
        raise click.ClickException(
            "Publish checks failed. Run 'stx publish check' for details."
        )

    # 2. Extract version for display
    version = next((c.message for c in checks if c.name == "version"), "unknown")

    # 3. Build
    uv = _find_uv()
    if not uv:
        raise click.ClickException("uv not found in PATH.")

    console.print("[cyan]Building package…[/cyan]")
    result = subprocess.run(
        [uv, "build"],
        cwd=p,
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        console.print(result.stderr)
        raise click.ClickException("Build failed.")

    console.print("[green]Build succeeded[/green]")

    # 4. Upload
    publish_cmd = [uv, "publish"]
    if use_test_pypi:
        publish_cmd.extend(["--index", "testpypi"])

    console.print(f"[cyan]Publishing to {'TestPyPI' if use_test_pypi else 'PyPI'}…[/cyan]")
    result = subprocess.run(
        publish_cmd,
        cwd=p,
        timeout=120,
    )
    if result.returncode != 0:
        raise click.ClickException("Publish failed.")

    # 5. Success message
    if use_test_pypi:
        url = f"https://test.pypi.org/project/streamtex/{version}/"
    else:
        url = f"https://pypi.org/project/streamtex/{version}/"

    console.print(f"\n[bold green]Published![/bold green] → {url}")
