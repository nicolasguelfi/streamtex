"""Guard test — ensures every content-rendering st.html() goes through _render().

Scans the AST of all *.py files under streamtex/ and verifies that each file
has exactly the expected number of ``st.html()`` calls.  Any file absent from
the whitelist MUST have zero calls.

If this test fails, you probably added a ``st.html(...)`` call in a content
module.  Replace it with ``_render(...)`` from ``streamtex.export``.
"""

import ast
import os
from pathlib import Path

import pytest

# Expected st.html() call counts per file (infrastructure only).
# Content calls MUST use _render() from export.py instead.
EXPECTED_ST_HTML_COUNTS = {
    "export.py": 1,         # _render() — the only authorised bridge
    "container.py": 4,      # 2 CSS injections + 2 hidden markers
    "grid.py": 2,           # 1 CSS + 1 hidden marker
    "list.py": 4,           # 2 CSS injections + 2 hidden markers
    "zoom.py": 1,           # CSS injection
    "link_preview.py": 2,   # CSS + JS scaffold
    "book.py": 4,           # 2 load_css + 1 populate_toc + 1 populate_markers
}

STREAMTEX_DIR = Path(__file__).resolve().parent.parent / "streamtex"


def _count_st_html_calls(filepath: Path) -> int:
    """Parse *filepath* and return the number of ``st.html(...)`` calls."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        # Match  st.html(...)
        if (isinstance(func, ast.Attribute)
                and func.attr == "html"
                and isinstance(func.value, ast.Name)
                and func.value.id == "st"):
            count += 1
    return count


class TestStHtmlGuard:
    """Verify that st.html() calls are only in whitelisted infrastructure files."""

    def test_st_html_counts(self):
        errors = []
        for py_file in sorted(STREAMTEX_DIR.rglob("*.py")):
            rel = str(py_file.relative_to(STREAMTEX_DIR))
            actual = _count_st_html_calls(py_file)
            expected = EXPECTED_ST_HTML_COUNTS.get(rel, 0)
            if actual != expected:
                errors.append(
                    f"  {py_file.relative_to(STREAMTEX_DIR)}: "
                    f"expected {expected} st.html() calls, found {actual}. "
                    f"Use _render() from streamtex.export for content rendering."
                )
        assert not errors, (
            "st.html() call count mismatch — content calls must use _render():\n"
            + "\n".join(errors)
        )
