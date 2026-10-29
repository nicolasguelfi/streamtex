"""stx styles dump — the styles reference, generated from the code (#6).

Claude writes blocks from references written by hand; they drift from the style code and never listed
the pt scale or the project's styles. This command walks ``StxStyles`` (and the project's ``Styles``),
resolves every ``var(--stx-X, fallback)`` against ``default.css`` (desktop, tablet, mobile), takes the
indexed scale from ``compute_scale()`` and writes ``.claude/references/streamtex_styles_api.md``.
``stx claude install`` and ``update`` regenerate it when the version or its inputs change.

``--check`` reports the drifts instead: a fallback that differs from ``default.css``, a shortcut whose
docstring says another size, an indexed scale in ``default.css`` that differs from ``compute_scale()``,
and every ``s.xxx`` cited in ``.claude/`` that resolves nowhere (a name the same file defines with
``Style(...)``, ``s.text_*``, ``s.project.*`` — generic examples, not the project's styles — and a line
saying the name "does not exist" are left out).
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import os
import re
import sys
from pathlib import Path

import click

REFERENCE = os.path.join(".claude", "references", "streamtex_styles_api.md")
_PROJECT_STYLES = os.path.join("custom", "styles.py")
_VAR_RE = re.compile(r"var\((--stx-[\w-]+),\s*([^)]+)\)")
_CITE_RE = re.compile(r"(?<![\w.])s\.([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)")
_HASH_RE = re.compile(r"inputs ([0-9a-f]{12})")
_DEFINED_RE = re.compile(r"^\s*(\w+)\s*=\s*(?:Style|ns)\(", flags=re.M)
_DENIED_RE = re.compile(r"does (?:\*\*)?not(?:\*\*)? exist")


def _styles_root():
    from streamtex.styles import StxStyles
    return StxStyles


def css_vars(text: str) -> dict[str, dict[str, str]]:
    """The ``--stx-*`` values of ``:root`` in default.css, per screen: desktop, tablet (≤1024px), mobile (≤480px)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out: dict[str, dict[str, str]] = {"desktop": {}, "tablet": {}, "mobile": {}}
    stack: list[str] = []
    buf = ""

    def decl(s: str) -> None:
        m = re.fullmatch(r"\s*(--stx-[\w-]+)\s*:\s*(.+?)\s*", s, flags=re.S)
        if not m or not stack or ":root" not in stack[-1]:
            return
        ctx = " ".join(stack)
        if "prefers-color-scheme" in ctx:
            return
        screen = "mobile" if "480px" in ctx else "tablet" if "1024px" in ctx else "desktop"
        out[screen].setdefault(m.group(1), m.group(2))

    for ch in text:
        if ch == "{":
            stack.append(buf.strip())
            buf = ""
        elif ch in ";}":
            decl(buf)
            buf = ""
            if ch == "}" and stack:
                stack.pop()
        else:
            buf += ch
    return out


def walk(cls, prefix: str, seen: dict[int, str], out: list, visited: set[int] | None = None) -> None:
    """Every Style under *cls*, in definition order, once (the first path wins)."""
    from streamtex.styles.core import Style
    visited = set() if visited is None else visited
    if id(cls) in visited:
        return
    visited.add(id(cls))
    for name, value in vars(cls).items():
        if name.startswith("_"):
            continue
        if isinstance(value, Style):
            if id(value) not in seen:
                seen[id(value)] = f"{prefix}.{name}"
                out.append((f"{prefix}.{name}", value))
        elif isinstance(value, type):
            walk(value, f"{prefix}.{name}", seen, out, visited)


def collect(styles=None) -> tuple[list, list, list]:
    """(library styles, shortcuts, project styles): lists of (path, Style); a shortcut's path is ``s.x``."""
    from streamtex.styles.core import Style
    root = _styles_root()
    seen: dict[int, str] = {}
    library: list = []
    for cat in ("text", "container", "visibility"):
        walk(getattr(root, cat), f"s.{cat}", seen, library)
    shortcuts = [(f"s.{k}", v) for k, v in vars(root).items() if isinstance(v, Style) and not k.startswith("_")]
    project: list = []
    if styles is not None and styles is not root:
        for k, v in vars(styles).items():
            if k.startswith("_") or k in vars(root):
                continue
            if isinstance(v, Style):
                project.append((f"s.{k}", v))
            elif isinstance(v, type):
                walk(v, f"s.{k}", seen, project)
    return library, shortcuts, project


def _docstring_sizes() -> dict[str, str]:
    """``s.Large`` → ``48pt``, read from the attribute docstrings of StxStyles (``\"\"\"48pt on desktop\"\"\"``)."""
    tree = ast.parse(inspect.getsource(_styles_root()))
    body = tree.body[0].body
    out = {}
    for a, b in zip(body, body[1:]):
        if isinstance(a, ast.Assign) and isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant) \
                and isinstance(b.value.value, str) and len(a.targets) == 1 and isinstance(a.targets[0], ast.Name):
            m = re.match(r"\s*(\d+pt) on desktop", b.value.value)
            if m:
                out[f"s.{a.targets[0].id}"] = m.group(1)
    return out


def declared_module(project: Path) -> str:
    """``[claude] styles = "shared.styles"`` in the project's stx.toml: where its ``Styles`` class lives when it
    is not ``custom/styles.py``."""
    import tomllib
    try:
        with open(project / "stx.toml", "rb") as f:
            value = tomllib.load(f).get("claude", {}).get("styles", "")
    except (OSError, tomllib.TOMLDecodeError, AttributeError):
        return ""
    return value if isinstance(value, str) else ""


def load_project_styles(project: Path, module: str = ""):
    """The project's ``Styles`` class: *module* (dotted, e.g. ``shared.styles``), the one stx.toml declares,
    or ``custom/styles.py``. Returns ``(Styles or None, the file read or None, a warning or "")``."""
    module = module or declared_module(project)
    if not module:
        if not (project / _PROJECT_STYLES).is_file():
            return None, None, ""
        module = "custom.styles"
    path = project.joinpath(*module.split(".")).with_suffix(".py")
    top = module.split(".")[0]

    def forget() -> None:       # `stx claude update --all`: each project imports its own custom.styles
        for name in [n for n in sys.modules if n == top or n.startswith(top + ".")]:
            del sys.modules[name]
    forget()
    sys.path.insert(0, str(project))
    try:
        mod = importlib.import_module(module)
        return getattr(mod, "Styles", None), path if path.is_file() else None, ""
    except Exception as exc:  # noqa: BLE001 — a broken project file must not stop the library reference
        return None, None, f"the project styles ({module}) could not be imported: {exc}"
    finally:
        sys.path.remove(str(project))
        forget()


def _inputs_hash(fmt: str, project_file: Path | None) -> str:
    import streamtex
    lib = Path(streamtex.__file__).parent
    h = hashlib.sha256(fmt.encode())
    for p in [lib / "static" / "default.css", *sorted((lib / "styles").glob("*.py")),
              *sorted((lib / "styles").glob("*.toml")), *([project_file] if project_file else [])]:
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def _version() -> str:
    try:
        from importlib.metadata import version
        return version("streamtex")
    except Exception:  # noqa: BLE001
        return "?"


def _css_of(style, screens: dict) -> tuple[str, str, str]:
    m = _VAR_RE.search(style.css)
    if not m:
        return ("", "", "")
    var, fb = m.group(1), m.group(2).strip()
    d = screens["desktop"].get(var, fb)
    return (d, screens["tablet"].get(var, d), screens["mobile"].get(var, d))


def render(fmt: str = "compact", styles=None, project_file: Path | None = None) -> str:
    """The reference, in Markdown."""
    import streamtex
    from streamtex.styles.scale import ScaleConfig, compute_scale
    screens = css_vars((Path(streamtex.__file__).parent / "static" / "default.css").read_text(encoding="utf-8"))
    library, shortcuts, project = collect(styles)
    canonical = {id(s): p for p, s in library + project}
    sizes = [(p, s) for p, s in library if p.startswith("s.text.sizes.")]
    named = [(p, s) for p, s in sizes if re.search(r"var\(--stx-[A-Za-z]+-size", s.css)]
    pts = [(p, s) for p, s in sizes if re.fullmatch(r"s\.text\.sizes\.pt\d+", p)]
    L = [
        "# StreamTeX styles API",
        "",
        f"> Generated by `stx styles dump` from the code — streamtex {_version()} · inputs "
        f"{_inputs_hash(fmt, project_file)}. Do not edit: `stx claude update` regenerates it.",
        "> Use these names instead of raw CSS (`s.text.sizes.pt36`, never `ns(\"font-size: 36pt;\")`).",
        "",
        "## Shortcuts (`s.*`)",
        "",
        "| Shortcut | Same as | CSS |",
        "|---|---|---|",
    ]
    for p, s in shortcuts:
        L.append(f"| `{p}` | `{canonical.get(id(s), '—')}` | `{s.css.strip()}` |")
    L += ["", "## Named sizes (responsive, from default.css)", "",
          "| Style | Desktop | Tablet (≤1024px) | Mobile (≤480px) |", "|---|---|---|---|"]
    for p, s in named:
        d, t, m = _css_of(s, screens)
        L.append(f"| `{p}` | {d} | {t} | {m} |")
    L += ["", "## pt scale (fixed, same on every screen)", "",
          "`s.text.sizes.ptN` sets `font-size: Npt`: " + ", ".join(p.rsplit(".", 1)[1] for p, _ in pts) + ".", ""]
    desktop, tablet, mobile = compute_scale(ScaleConfig(count=29))
    L += ["## Indexed scale (`s.scale[i]` = `s.text.sizes.idx_i`)", "",
          "Computed by `compute_scale()` (default curve; `st_book(scale=ScaleConfig(...))` changes it).", "",
          "| i | Desktop | Tablet | Mobile |", "|---|---|---|---|"]
    L += [f"| {i} | {d}pt | {t}pt | {m}pt |" for i, (d, t, m) in enumerate(zip(desktop, tablet, mobile))]
    done = {p for p, _ in named + pts} | {p for p, _ in sizes if re.fullmatch(r"s\.text\.sizes\.idx_\d+", p)}
    for title, items in (("Other styles", [(p, s) for p, s in library if p not in done]), ("Project styles", project)):
        if not items:
            continue
        L += ["", f"## {title}", ""]
        groups: dict[str, list] = {}
        for p, s in items:
            groups.setdefault(p.rsplit(".", 1)[0], []).append((p.rsplit(".", 1)[1], s))
        for g, members in groups.items():
            if fmt == "full":
                L += [f"### `{g}`", "", "| Name | CSS |", "|---|---|"]
                L += [f"| `{n}` | `{s.css.strip()}` |" for n, s in members] + [""]
            else:
                L.append(f"- `{g}`: " + ", ".join(n for n, _ in members))
    return "\n".join(L).rstrip() + "\n"


def resolves(path: str, root) -> bool:
    obj = root
    for part in path.split("."):
        if not hasattr(obj, part):
            return False
        obj = getattr(obj, part)
    return True


def drifts(project: Path, styles=None) -> list[str]:
    """The drifts, one line each; empty when the code, default.css and the references agree."""
    import streamtex
    from streamtex.styles.scale import ScaleConfig, compute_scale
    css = (Path(streamtex.__file__).parent / "static" / "default.css").read_text(encoding="utf-8")
    screens = css_vars(css)
    library, shortcuts, project_styles = collect(styles)
    problems = []
    for p, s in library + project_styles:
        m = _VAR_RE.search(s.css)
        if not m or re.fullmatch(r"--stx-scale-\d+", m.group(1)):
            continue
        var, fb = m.group(1), m.group(2).strip()
        if var not in screens["desktop"]:
            problems.append(f"{p}: {var} has no value in default.css (fallback {fb})")
        elif screens["desktop"][var] != fb:
            problems.append(f"{p}: fallback {fb}, default.css says {screens['desktop'][var]}")
    by_name = dict(shortcuts)
    for p, said in _docstring_sizes().items():
        d = _css_of(by_name[p], screens)[0] if p in by_name else ""
        if d and d != said:
            problems.append(f"{p}: its docstring says {said}, default.css says {d}")
    for screen, values in zip(("desktop", "tablet", "mobile"), compute_scale(ScaleConfig(count=29))):
        for i, v in enumerate(values):
            got = screens[screen].get(f"--stx-scale-{i}")
            if got is not None and got != f"{v}pt":
                problems.append(f"default.css --stx-scale-{i} ({screen}): {got}, compute_scale() gives {v}pt")
    root = styles or _styles_root()
    claude = project / ".claude"
    for f in sorted([*claude.glob("references/**/*.md"), *claude.glob("commands/**/*.md")]):
        if f.name == os.path.basename(REFERENCE):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        defined = set(_DEFINED_RE.findall(text))                # an example's own `heading = Style(...)`
        for n, line in enumerate(text.splitlines(), 1):
            if _DENIED_RE.search(line):
                continue                                        # "`s.idx_6` does not exist"
            for m in _CITE_RE.finditer(line):
                cited = m.group(1)
                if line[m.end():m.end() + 1] == "*" or cited.split(".")[0] in (*defined, "project", "xxx"):
                    continue    # s.text_*, an example's own names, a placeholder, and s.project.*: the installed
                    #             references are generic, their s.project examples name no real project's styles
                if not resolves(cited, root):
                    problems.append(f"{f.relative_to(project)}:{n}: s.{cited} does not exist")
    return problems


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        os.chmod(path, 0o644)
    path.write_text(content, encoding="utf-8")
    os.chmod(path, 0o444)


def refresh_reference(target: str) -> str | None:
    """For ``stx claude``: write the reference into *target* when it is missing or its inputs changed.
    Returns its relative path when written, None otherwise (a warning goes to stderr on failure)."""
    project = Path(target)
    styles, pfile, warn = load_project_styles(project)
    if warn:
        click.echo(f"  ⚠ styles reference: {warn}", err=True)
    out = project / REFERENCE
    old = out.read_text(encoding="utf-8") if out.is_file() else ""
    m = _HASH_RE.search(old)
    if m and m.group(1) == _inputs_hash("compact", pfile) and f"streamtex {_version()} " in old:
        return None
    try:
        _write(out, render("compact", styles, pfile))
    except OSError as exc:
        click.echo(f"  ⚠ styles reference not written: {exc}", err=True)
        return None
    return REFERENCE


@click.group()
def styles():
    """The styles reference, generated from the code."""


@styles.command("dump")
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", default="", help=f"Where to write (default: PATH/{REFERENCE}; '-' prints).")
@click.option("--format", "fmt", type=click.Choice(["compact", "full"]), default="compact", show_default=True,
              help="compact lists the names of the other styles; full gives each one's CSS.")
@click.option("--check", is_flag=True, help="Report the drifts (code, default.css, .claude references) and exit 1.")
@click.option("--styles", "module", default="",
              help="The project's styles module (default: [claude] styles in stx.toml, else custom/styles.py).")
def dump_cmd(path, output, fmt, check, module):
    """Write the styles reference of the library and the project (#6)."""
    project = Path(path).resolve()
    styles_cls, pfile, warn = load_project_styles(project, module)
    if warn:
        click.echo(f"⚠ {warn}", err=True)
    if check:
        problems = drifts(project, styles_cls)
        for p in problems:
            click.echo(f"✗ {p}")
        click.echo(f"{len(problems)} drift(s)" if problems else "✓ no drift")
        sys.exit(1 if problems else 0)
    content = render(fmt, styles_cls, pfile)
    if output == "-":
        click.echo(content, nl=False)
        return
    dest = Path(output) if output else project / REFERENCE
    _write(dest, content)
    click.echo(f"✓ {dest} ({content.count(chr(10))} lines)")
