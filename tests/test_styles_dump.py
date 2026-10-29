"""stx styles dump: the styles reference generated from the code, and its drift check (#6)."""

import os
import re
import stat
import sys

import pytest
from click.testing import CliRunner

from streamtex.cli import styles_cmd as sd
from streamtex.cli.commands import cli


@pytest.fixture
def project(tmp_path):
    """A project with its own styles (custom/styles.py) and a .claude reference citing styles."""
    p = tmp_path / "proj"
    (p / "custom").mkdir(parents=True)
    (p / "custom" / "__init__.py").write_text("")
    (p / "custom" / "styles.py").write_text(
        "from streamtex.styles import Style, StxStyles\n"
        "class Colors:\n    primary = Style('color: #123456;', 'primary')\n"
        "class Project:\n    colors = Colors\n"
        "class Styles(StxStyles):\n    project = Project\n")
    (p / ".claude" / "references").mkdir(parents=True)
    (p / ".claude" / "references" / "guide.md").write_text(
        "Use s.Large or s.text.sizes.pt36, s.text_* aliases, s.scale[3].\n")
    yield p
    for n in [n for n in sys.modules if n == "custom" or n.startswith("custom.")]:
        del sys.modules[n]


def test_the_reference_lists_the_pt_scale_and_the_named_sizes():
    from streamtex.styles import StxStyles
    text = sd.render()
    assert re.search(r"`s\.text\.sizes\.ptN` sets `font-size: Npt`: .*\bpt36\b", text)
    assert StxStyles.text.sizes.pt36.css.strip() == "font-size: 36pt;"
    assert "| `s.text.sizes.Large_size` | 48pt | 36pt | 26pt |" in text      # default.css, three screens
    assert "| `s.Large` | `s.text.sizes.Large_size` |" in text


def test_every_style_appears_exactly_once():
    from streamtex.styles.core import Style
    library, _shortcuts, _ = sd.collect()
    assert len({p for p, _ in library}) == len(library) == len({id(s) for _, s in library})
    assert all(isinstance(s, Style) for _, s in library)
    full = sd.render("full")
    for p, _ in library:
        group, name = p.rsplit(".", 1)
        assert f"`{p}`" in full or (f"### `{group}`" in full and f"| `{name}` |" in full) \
            or re.fullmatch(r"s\.text\.sizes\.(pt|idx_)\d+", p), p


def test_the_indexed_table_is_compute_scale():
    from streamtex.styles.scale import ScaleConfig, compute_scale
    rows = re.findall(r"^\| (\d+) \| (\d+)pt \| (\d+)pt \| (\d+)pt \|$", sd.render(), flags=re.M)
    d, t, m = compute_scale(ScaleConfig(count=29))
    assert [(int(a), int(b), int(c), int(e)) for a, b, c, e in rows] == list(zip(range(29), d, t, m))


def test_the_project_styles_are_listed(project):
    styles, pfile, warn = sd.load_project_styles(project)
    assert not warn and pfile == project / "custom" / "styles.py"
    text = sd.render("full", styles, pfile)
    assert "### `s.project.colors`" in text and "| `primary` | `color: #123456;` |" in text


def test_the_output_is_deterministic(project):
    styles, pfile, _ = sd.load_project_styles(project)
    assert sd.render("compact", styles, pfile) == sd.render("compact", styles, pfile)


def test_the_library_has_no_drift(project):
    """The code, default.css and compute_scale() agree; the fixture's citations all resolve."""
    styles, _, _ = sd.load_project_styles(project)
    assert sd.drifts(project, styles) == []


def test_check_finds_a_wrong_citation(project):
    (project / ".claude" / "references" / "guide.md").write_text("st_write(s.idx_6, 'x')  # s.project.colors.nope\n")
    r = CliRunner().invoke(cli, ["styles", "dump", str(project), "--check"])
    assert r.exit_code == 1
    assert "guide.md:1: s.idx_6 does not exist" in r.output
    assert "s.project.colors.nope does not exist" in r.output     # the project's styles are known


def test_check_finds_a_fallback_that_differs(monkeypatch, project):
    from streamtex.styles import StxStyles
    from streamtex.styles.core import Style
    monkeypatch.setattr(StxStyles.text.sizes, "Large_size", Style("font-size: var(--stx-Large-size, 32pt);", "Large_size"))
    assert any("Large_size: fallback 32pt, default.css says 48pt" in p for p in sd.drifts(project))


def test_check_finds_a_docstring_that_differs(monkeypatch, project):
    monkeypatch.setattr(sd, "_docstring_sizes", lambda: {"s.Large": "32pt"})
    assert sd.drifts(project) == ["s.Large: its docstring says 32pt, default.css says 48pt"]


def test_dump_writes_a_read_only_file(project):
    r = CliRunner().invoke(cli, ["styles", "dump", str(project)])
    assert r.exit_code == 0, r.output
    out = project / sd.REFERENCE
    assert out.is_file() and not (out.stat().st_mode & stat.S_IWUSR)
    assert CliRunner().invoke(cli, ["styles", "dump", str(project)]).exit_code == 0     # rewritten over 0o444


def test_refresh_writes_once_then_only_when_the_inputs_change(project, monkeypatch):
    assert sd.refresh_reference(str(project)) == sd.REFERENCE
    assert sd.refresh_reference(str(project)) is None
    monkeypatch.setattr(sd, "_inputs_hash", lambda fmt, pfile: "0123456789ab")
    assert sd.refresh_reference(str(project)) == sd.REFERENCE


def test_a_broken_project_file_does_not_stop_the_library_reference(project):
    (project / "custom" / "styles.py").write_text("raise RuntimeError('boom')\n")
    styles, _, warn = sd.load_project_styles(project)
    assert styles is None and "boom" in warn
    assert sd.refresh_reference(str(project)) == sd.REFERENCE


def test_claude_install_and_update_keep_the_reference(tmp_path):
    from streamtex.cli.claude_cmd import install_profile
    from tests.test_cli_claude import _make_workspace
    ws = _make_workspace(tmp_path)
    target = tmp_path / "my-project"
    target.mkdir()
    installed = install_profile(str(ws / "streamtex-claude"), "project", str(target))
    out = target / sd.REFERENCE
    assert sd.REFERENCE in installed and out.is_file() and not (out.stat().st_mode & stat.S_IWUSR)
    cwd = os.getcwd()
    try:
        os.chdir(ws)
        r = CliRunner().invoke(cli, ["claude", "update", str(target), "--yes"])
    finally:
        os.chdir(cwd)
    assert r.exit_code == 0, r.output
    assert out.is_file() and "up to date" in r.output                 # neither pruned nor rewritten


def test_two_projects_each_get_their_own_styles(project, tmp_path):
    other = tmp_path / "other"
    (other / "custom").mkdir(parents=True)
    (other / "custom" / "__init__.py").write_text("")
    (other / "custom" / "styles.py").write_text(
        "from streamtex.styles import Style, StxStyles\n"
        "class Styles(StxStyles):\n    accent = Style('color: red;', 'accent')\n")
    a, _, _ = sd.load_project_styles(project)
    b, _, _ = sd.load_project_styles(other)
    assert hasattr(a, "project") and not hasattr(b, "project") and hasattr(b, "accent")


def test_stx_toml_names_the_styles_module(project):
    """all-trainings keeps its Styles in shared/styles.py: [claude] styles = "shared.styles"."""
    (project / "custom").rename(project / "shared")
    (project / "stx.toml").write_text('[claude]\nstyles = "shared.styles"\n')
    styles, pfile, warn = sd.load_project_styles(project)
    assert not warn and pfile == project / "shared" / "styles.py" and hasattr(styles, "project")


def test_check_skips_what_the_file_defines_or_denies(project):
    (project / ".claude" / "references" / "guide.md").write_text(
        "class Styles(StxStyles):\n    heading = Style('font-size: 40px;', 'heading')\n"
        "st_write(s.heading, 'x')\n`s.idx_6` does **not** exist: use s.text.sizes.idx_6.\nst_write(s.body, 'y')\n")
    assert [p.split(": ", 1)[1] for p in sd.drifts(project)] == ["s.body does not exist"]
