"""Project rules declared in ``stx.toml`` and run by ``stx validate`` (L12).

A rule written in prose is not checked by anything; a project's own
invariants become rules that can fail::

    [[validate.rules]]
    id = "no-hex"
    message = "no hexadecimal colour in a block — the colour is a role"
    glob = "content/**/bck_*.py"
    forbid = '#[0-9a-fA-F]{6}\\b'        # regex; every match is a violation

    [[validate.rules]]
    id = "has-marker"
    glob = "content/**/bck_*.py"
    require = 'st_marker\\('             # regex; a file without a match fails

    [[validate.rules]]
    id = "invariants"
    run = "uv run python _project/tools/verify.py --all"   # exit code != 0 fails
    severity = "warning"                  # "error" (default) or "warning"

Paths are relative to the project directory; ``glob`` accepts ``**``.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RuleViolation:
    rule: str
    severity: str        # "error" | "warning"
    where: str           # "path:line", or the command for a run rule
    message: str


def load_rules(project_dir: Path) -> list[dict]:
    path = project_dir / "stx.toml"
    if not path.is_file():
        return []
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return []
    rules = data.get("validate", {}).get("rules", [])
    return [r for r in rules if isinstance(r, dict)]


def _files(project_dir: Path, pattern: str) -> list[Path]:
    return sorted(p for p in project_dir.glob(pattern) if p.is_file()
                  and ".venv" not in p.parts and "node_modules" not in p.parts)


def check_rules(project_dir: Path, rules: list[dict] | None = None,
                *, timeout: int = 600) -> list[RuleViolation]:
    """Run every declared rule; return the violations (empty = all pass)."""
    rules = load_rules(project_dir) if rules is None else rules
    out: list[RuleViolation] = []
    for i, rule in enumerate(rules):
        rid = str(rule.get("id") or f"rule-{i + 1}")
        sev = "warning" if rule.get("severity") == "warning" else "error"
        msg = str(rule.get("message") or rid)
        if "run" in rule:
            cmd = str(rule["run"])
            try:
                proc = subprocess.run(shlex.split(cmd), cwd=project_dir, capture_output=True,
                                      text=True, timeout=timeout)
            except (OSError, subprocess.TimeoutExpired) as e:
                out.append(RuleViolation(rid, sev, cmd, f"{msg}: could not run ({e})"))
                continue
            if proc.returncode != 0:
                tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
                out.append(RuleViolation(rid, sev, cmd,
                                         f"{msg}: exit {proc.returncode} — " + " | ".join(tail)))
            continue
        glob = rule.get("glob")
        if not glob:
            out.append(RuleViolation(rid, "error", "stx.toml", "rule needs 'glob' (or 'run')"))
            continue
        try:
            forbid = re.compile(rule["forbid"], re.M) if "forbid" in rule else None
            require = re.compile(rule["require"], re.M) if "require" in rule else None
        except re.error as e:
            out.append(RuleViolation(rid, "error", "stx.toml", f"invalid regex: {e}"))
            continue
        if forbid is None and require is None:
            out.append(RuleViolation(rid, "error", "stx.toml", "rule needs 'forbid' or 'require'"))
            continue
        for path in _files(project_dir, str(glob)):
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = path.relative_to(project_dir)
            if forbid is not None:
                for m in forbid.finditer(text):
                    line = text.count("\n", 0, m.start()) + 1
                    out.append(RuleViolation(rid, sev, f"{rel}:{line}", msg))
            if require is not None and not require.search(text):
                out.append(RuleViolation(rid, sev, str(rel), msg))
    return out


def local_copies_of_public_api(project_dir: Path) -> list[tuple[str, int, str]]:
    """Top-level ``def st_*`` in the project that streamtex also provides (L15).

    Information only: a local copy may be a deliberate specialisation; the
    author decides whether to switch to the library's version.
    Returns ``(relative_path, line, name)``.
    """
    import ast
    import os

    import streamtex

    public = {n for n in getattr(streamtex, "__all__", ()) if n.startswith("st_")
              and callable(getattr(streamtex, n, None))}
    found: list[tuple[str, int, str]] = []
    skip = {".venv", "venv", "node_modules", "__pycache__", ".git", "site-packages", "static"}
    for dirpath, dirnames, filenames in os.walk(project_dir):
        dirnames[:] = [d for d in dirnames if d not in skip and not d.startswith(".")]
        for f in filenames:
            if not f.endswith(".py"):
                continue
            p = Path(dirpath) / f
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
            except (SyntaxError, ValueError):
                continue
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name in public:
                    found.append((str(p.relative_to(project_dir)), node.lineno, node.name))
    return sorted(found)
