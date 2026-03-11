"""Compatibility checker — static analysis for breaking changes.

Scans Python files in a project for imports and usages that have been
removed or renamed in newer versions of streamtex.
"""

import ast
import os
from dataclasses import dataclass

from .registry import _version_tuple

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class CompatIssue:
    """A single compatibility issue found in a source file."""

    file: str
    line: int
    severity: str  # "error" | "warning"
    code: str  # e.g. "REMOVED", "RENAMED", "PARAM_REMOVED"
    message: str
    suggestion: str | None = None


# ---------------------------------------------------------------------------
# Breaking changes registry (populated per version)
# ---------------------------------------------------------------------------

# Each entry: {type, old, new?, note?, version}
BREAKING_CHANGES: list[dict] = [
    # Example entries — extend as real breaking changes happen:
    #
    # {
    #     "version": "0.5.0",
    #     "type": "removed",
    #     "name": "st_markdown_file",
    #     "note": "Use st_markdown(file=...) instead.",
    # },
    # {
    #     "version": "0.5.0",
    #     "type": "renamed",
    #     "old": "st_grid_layout",
    #     "new": "st_grid",
    # },
    # {
    #     "version": "0.5.0",
    #     "type": "param_removed",
    #     "func": "st_book",
    #     "param": "show_toc",
    #     "note": "Use toc_config=None to disable TOC.",
    # },
]


def _get_changes_in_range(
    current_version: str, target_version: str,
) -> list[dict]:
    """Filter breaking changes between current (exclusive) and target (inclusive)."""
    cur = _version_tuple(current_version)
    tgt = _version_tuple(target_version)
    return [
        c for c in BREAKING_CHANGES
        if cur < _version_tuple(c["version"]) <= tgt
    ]


# ---------------------------------------------------------------------------
# AST scanning
# ---------------------------------------------------------------------------

def _find_py_files(project_path: str) -> list[str]:
    """Find all .py files in a project (excluding .venv, __pycache__)."""
    results: list[str] = []
    for root, dirs, files in os.walk(project_path):
        # Skip common non-project directories
        dirs[:] = [
            d for d in dirs
            if d not in {".venv", "__pycache__", ".git", ".ruff_cache", "node_modules"}
        ]
        for f in files:
            if f.endswith(".py"):
                results.append(os.path.join(root, f))
    return results


def _check_file(
    filepath: str,
    tree: ast.Module,
    changes: list[dict],
) -> list[CompatIssue]:
    """Check a single parsed AST for compatibility issues."""
    issues: list[CompatIssue] = []

    # Collect all names imported from streamtex
    stx_imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "streamtex" in node.module:
            for alias in node.names:
                stx_imports.add(alias.name)

    removed = {c["name"]: c for c in changes if c["type"] == "removed"}
    renamed = {c["old"]: c for c in changes if c["type"] == "renamed"}
    param_removed = {c["func"]: c for c in changes if c["type"] == "param_removed"}

    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.ImportFrom) and node.module and "streamtex" in node.module:
            for alias in node.names:
                name = alias.name
                if name in removed:
                    issues.append(CompatIssue(
                        file=filepath,
                        line=node.lineno,
                        severity="error",
                        code="REMOVED",
                        message=f"'{name}' has been removed.",
                        suggestion=removed[name].get("note"),
                    ))
                elif name in renamed:
                    c = renamed[name]
                    issues.append(CompatIssue(
                        file=filepath,
                        line=node.lineno,
                        severity="error",
                        code="RENAMED",
                        message=f"'{name}' has been renamed to '{c['new']}'.",
                        suggestion=f"Replace with: {c['new']}",
                    ))

        # Check function calls for removed parameters
        if isinstance(node, ast.Call) and param_removed:
            func_name = _get_call_name(node)
            if func_name and func_name in param_removed and func_name in stx_imports:
                c = param_removed[func_name]
                for kw in node.keywords:
                    if kw.arg == c["param"]:
                        issues.append(CompatIssue(
                            file=filepath,
                            line=node.lineno,
                            severity="error",
                            code="PARAM_REMOVED",
                            message=f"Parameter '{c['param']}' of '{func_name}' has been removed.",
                            suggestion=c.get("note"),
                        ))

    return issues


def _get_call_name(node: ast.Call) -> str | None:
    """Extract function name from a Call node."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_compatibility(
    project_path: str,
    current_version: str,
    target_version: str,
) -> list[CompatIssue]:
    """Scan all .py files in a project for compatibility issues.

    Returns a list of :class:`CompatIssue` sorted by file and line.
    """
    changes = _get_changes_in_range(current_version, target_version)
    if not changes:
        return []

    issues: list[CompatIssue] = []
    for filepath in _find_py_files(project_path):
        try:
            with open(filepath, encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filepath)
            issues.extend(_check_file(filepath, tree, changes))
        except SyntaxError:
            issues.append(CompatIssue(
                file=filepath,
                line=0,
                severity="warning",
                code="PARSE_ERROR",
                message="Could not parse file (syntax error).",
            ))

    return sorted(issues, key=lambda i: (i.file, i.line))
