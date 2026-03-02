"""Shortcut commands: test and lint wrappers."""

import subprocess
import sys


def run_test(*, verbose: bool = False, extra_args: tuple = ()) -> None:
    """Run pytest via subprocess."""
    cmd = [sys.executable, "-m", "pytest", "tests/"]
    if verbose:
        cmd.append("-v")
    cmd.extend(extra_args)
    result = subprocess.run(cmd)
    raise SystemExit(result.returncode)


def run_lint(*, extra_args: tuple = ()) -> None:
    """Run ruff check via subprocess."""
    cmd = [sys.executable, "-m", "ruff", "check", "streamtex/"]
    cmd.extend(extra_args)
    result = subprocess.run(cmd)
    raise SystemExit(result.returncode)
