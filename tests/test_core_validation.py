"""Tests for streamtex.core.validation — components, design systems, kits, packs."""

import textwrap
from pathlib import Path
from types import ModuleType

from streamtex.core import validation
from streamtex.styles import Style


def _make_module(name: str, source: str) -> ModuleType:
    """Build a synthetic module from source code for validation tests."""
    mod = ModuleType(name)
    mod.__file__ = f"/tmp/{name}.py"
    exec(compile(textwrap.dedent(source), f"<{name}>", "exec"), mod.__dict__)
    return mod


# ---------------------------------------------------------------------------
# Component validation
# ---------------------------------------------------------------------------


_VALID_COMPONENT_SRC = """\
'''
# Callout — Highlighted box for emphasized content

## Visual
ASCII rectangle with title + body.

## Structure
- title row
- body row
- optional icon

## Styling rules
| element | style |
|---|---|
| title | bold |
| body | regular |
| icon | colored |

## Extrapolation rules
### INVARIANTS
- title always present
- body always present
### PARAMS
- kind: info|warn|error|success
- size: regular|wide
### INTERDITS
- no nesting
- no callout in callout

## When to use
- emphasizing a key takeaway
- warning the reader

## When NOT to use
- for primary content
- for decoration

## Design system bundles required
- callouts.info
- callouts.title
'''
from streamtex.styles import Style

__component_meta__ = {
    "name": "callout",
    "description": "Highlighted box for emphasized content",
    "tags": ["callout", "container"],
    "extrapolable": True,
    "since": "2026-05-19",
    "bundles_required": ["callouts.info", "callouts.title"],
    "granularity": "primitive",
}

def callout(*, title: str = "", body: str = "", kind: str = "info") -> None:
    '''Render a callout box.'''
    pass
"""


def test_valid_component_passes():
    mod = _make_module("callout", _VALID_COMPONENT_SRC)
    issues = validation.validate_component(mod)
    errors = [i for i in issues if i.is_error()]
    assert errors == [], f"unexpected errors: {errors}"


def test_missing_docstring_fails_cv001():
    mod = _make_module(
        "nodoc",
        """\
        __component_meta__ = {
            "name": "nodoc",
            "description": "x",
            "tags": ["x"],
            "extrapolable": False,
            "since": "2026-05-19",
            "bundles_required": [],
            "granularity": "primitive",
        }
        def nodoc():
            pass
        """,
    )
    issues = validation.validate_component(mod)
    codes = {i.code for i in issues if i.is_error()}
    assert "CV001" in codes


def test_missing_section_fails_cv002():
    short_src = '''
"""# Header only docstring.

## Visual
x
"""
__component_meta__ = {
    "name": "halfdoc",
    "description": "x",
    "tags": ["x"],
    "extrapolable": False,
    "since": "2026-05-19",
    "bundles_required": [],
    "granularity": "primitive",
}
def halfdoc(*, x: str = "") -> None:
    pass
'''
    mod = _make_module("halfdoc", short_src)
    issues = validation.validate_component(mod)
    codes = {i.code for i in issues if i.is_error()}
    assert "CV002" in codes


def test_missing_meta_fails_cv004():
    mod = _make_module(
        "nometa",
        '''"""# X

## Visual
x

## Structure
- a

## Styling rules
x

## Extrapolation rules
### INVARIANTS
- a
- b
### PARAMS
- a
- b
### INTERDITS
- a
- b

## When to use
- a
- b

## When NOT to use
- a
- b

## Design system bundles required
- colors.primary
"""
def nometa(*, x: str = "") -> None:
    pass
''',
    )
    issues = validation.validate_component(mod)
    codes = {i.code for i in issues if i.is_error()}
    assert "CV004" in codes


def test_positional_param_fails_cv007():
    src = '''
"""# C

## Visual
x

## Structure
- a

## Styling rules
x

## Extrapolation rules
### INVARIANTS
- a
- b
### PARAMS
- a
- b
### INTERDITS
- a
- b

## When to use
- a
- b

## When NOT to use
- a
- b

## Design system bundles required
- colors.primary
"""
__component_meta__ = {
    "name": "positional",
    "description": "x",
    "tags": ["x"],
    "extrapolable": True,
    "since": "2026-05-19",
    "bundles_required": ["colors.primary"],
    "granularity": "primitive",
}
def positional(title, body=""):
    pass
'''
    mod = _make_module("positional", src)
    issues = validation.validate_component(mod)
    codes = {i.code for i in issues if i.is_error()}
    assert "CV007" in codes


# ---------------------------------------------------------------------------
# Design system validation
# ---------------------------------------------------------------------------


def test_valid_design_system_passes():
    src = """\
'''Test design system.'''
from streamtex.styles import Style

class _Colors:
    primary = Style("c: 1", "primary")
    accent = Style("c: 2", "accent")
    bg = Style("c: 3", "bg")
    surface = Style("c: 4", "surface")
    text = Style("c: 5", "text")
    muted = Style("c: 6", "muted")

class _Titles:
    slide = Style("s: 1", "slide")
    section = Style("s: 2", "section")
    subtitle = Style("s: 3", "subtitle")
    body = Style("s: 4", "body")
    caption = Style("s: 5", "caption")

class _Callouts:
    info = Style("c: 1", "info")
    warn = Style("c: 2", "warn")
    error = Style("c: 3", "error")
    success = Style("c: 4", "success")
    icon = Style("c: 5", "icon")
    title = Style("c: 6", "title")
    body = Style("c: 7", "body")

class _Body:
    paragraph = Style("p: 1", "paragraph")
    emphasis = Style("e: 1", "emphasis")
    code = Style("c: 1", "code")

class DesignSystem:
    name = "test"
    colors = _Colors
    titles = _Titles
    callouts = _Callouts
    body = _Body
"""
    mod = _make_module("ds_test", src)
    issues = validation.validate_design_system(mod)
    errors = [i for i in issues if i.is_error()]
    assert errors == []


def test_missing_design_system_fails_dv001():
    mod = _make_module("ds_empty", "pass\n")
    issues = validation.validate_design_system(mod)
    codes = {i.code for i in issues if i.is_error()}
    assert "DV001" in codes


def test_missing_bundle_fails_dv003():
    src = """\
'''DS missing callouts.'''
class _C:
    primary = "p"
    accent = "a"
    bg = "bg"
    surface = "s"
    text = "t"
    muted = "m"

class _T:
    slide = "1"
    section = "2"
    subtitle = "3"
    body = "4"
    caption = "5"

class _B:
    paragraph = "p"
    emphasis = "e"
    code = "c"

class DesignSystem:
    name = "incomplete"
    colors = _C
    titles = _T
    body = _B
    # callouts intentionally missing
"""
    mod = _make_module("ds_incomplete", src)
    issues = validation.validate_design_system(mod)
    codes = {i.code for i in issues if i.is_error()}
    assert "DV003" in codes


# ---------------------------------------------------------------------------
# Kit and pack validation
# ---------------------------------------------------------------------------


def test_valid_kit(tmp_path: Path):
    kit_path = tmp_path / "course.toml"
    kit_path.write_text(
        textwrap.dedent(
            """\
            name = "course-default"
            description = "Default course kit"
            since = "2026-05-19"

            [design_system]
            ref = "default"

            [components]
            include = ["callout", "title_slide", "takeaways"]
            """
        )
    )
    issues = validation.validate_kit(kit_path)
    assert [i for i in issues if i.is_error()] == []


def test_kit_missing_design_system(tmp_path: Path):
    kit_path = tmp_path / "broken.toml"
    kit_path.write_text(
        "name = 'x'\ndescription = 'y'\nsince = '2026-05-19'\n[components]\ninclude = ['a']\n"
    )
    issues = validation.validate_kit(kit_path)
    codes = {i.code for i in issues if i.is_error()}
    assert "KV004" in codes


def test_pack_missing_manifest(tmp_path: Path):
    issues = validation.validate_pack(tmp_path)
    codes = {i.code for i in issues if i.is_error()}
    assert "PV001" in codes


def test_valid_pack(tmp_path: Path):
    manifest = tmp_path / "_pack_manifest.toml"
    manifest.write_text(
        textwrap.dedent(
            """\
            [manifest]
            format = "0.1"

            [pack]
            name = "streamtex-design"
            version = "0.1.0"
            author = "x"
            license = "MIT"
            streamtex_compat = ">=0.7,<1.0"

            [entrypoint]
            module = "streamtex_design"
            """
        )
    )
    (tmp_path / "components").mkdir()
    (tmp_path / "components" / "callout.py").write_text("# stub\n")
    issues = validation.validate_pack(tmp_path)
    errors = [i for i in issues if i.is_error()]
    assert errors == [], f"unexpected errors: {errors}"


def test_validate_bundles_required_ok():
    class _Callouts:
        info = Style("c", "info")
        title = Style("c", "title")

    class DS:
        callouts = _Callouts

    meta = {
        "name": "callout",
        "bundles_required": ["callouts.info", "callouts.title"],
    }
    issues = validation.validate_bundles_required(meta, DS)
    assert issues == []


def test_validate_bundles_required_bv001():
    class DS:
        pass  # missing 'callouts'

    meta = {"name": "callout", "bundles_required": ["callouts.info"]}
    issues = validation.validate_bundles_required(meta, DS)
    assert any(i.code == "BV001" for i in issues)


def test_validate_bundles_required_bv002():
    class _Callouts:
        info = Style("c", "info")
        # title missing

    class DS:
        callouts = _Callouts

    meta = {"name": "callout", "bundles_required": ["callouts.title"]}
    issues = validation.validate_bundles_required(meta, DS)
    assert any(i.code == "BV002" for i in issues)
