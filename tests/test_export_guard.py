"""Guard test — ensures every content-rendering st.html() goes through st_html().

Scans the AST of all *.py files under streamtex/ and verifies that each file
has exactly the expected number of ``st.html()`` calls.  Any file absent from
the whitelist MUST have zero calls.

If this test fails, you probably added a ``st.html(...)`` call in a content
module.  Replace it with ``st_html(...)`` from ``streamtex.export``.
"""

import ast
import os
from pathlib import Path

import pytest

# Expected st.html() call counts per file (infrastructure only).
# Content calls MUST use st_html() from export.py instead.
EXPECTED_ST_HTML_COUNTS = {
    "export.py": 1,         # st_html() — the only authorised bridge
    "container.py": 4,      # 2 CSS injections + 2 hidden markers
    "grid.py": 2,           # 1 CSS + 1 hidden marker
    "list.py": 4,           # 2 CSS injections + 2 hidden markers
    "zoom.py": 1,           # CSS injection
    "link_preview.py": 2,   # CSS + JS scaffold
    "bib_preview.py": 1,    # CSS only (JS via components.html)
    "book.py": 4,           # 2 load_css + 1 populate_toc (no-search branch) + 1 populate_markers
    "inspector.py": 3,      # 1 global CSS + 1 sidebar width CSS + 1 hidden marker (edit button)
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
                    f"Use st_html() from streamtex.export for content rendering."
                )
        assert not errors, (
            "st.html() call count mismatch — content calls must use st_html():\n"
            + "\n".join(errors)
        )
