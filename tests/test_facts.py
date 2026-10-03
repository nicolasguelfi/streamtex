"""streamtex.facts: versioned facts, fact(), stale_facts() and stx validate (#95)."""

import textwrap

import pytest
from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.facts import fact, stale_facts

pytestmark = pytest.mark.usefixtures("reset_watch")


def _facts(tmp_path, recorded="0.85.0", current="0.86.0"):
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n')
    (tmp_path / "facts").mkdir()
    (tmp_path / "gse").mkdir()
    (tmp_path / "gse" / "VERSION").write_text(current + "\n")
    (tmp_path / "facts" / "gse-one.toml").write_text(textwrap.dedent(f"""
        [source]
        name = "GSE-One"
        version = "{recorded}"
        current = "../gse/VERSION"
        [facts]
        agents = 23
        commands = 41
        paths.registry = ".gse/registry"
    """))
    return tmp_path


def test_fact_lookup_and_strictness(tmp_path):
    root = _facts(tmp_path)
    assert fact("gse-one", "agents", root=root) == 23
    assert fact("gse-one", "paths.registry", root=root) == ".gse/registry"
    with pytest.raises(KeyError, match="nope"):
        fact("gse-one", "nope", root=root)
    with pytest.raises(KeyError, match="no facts file"):
        fact("other", "x", root=root)


def test_stale_facts(tmp_path):
    root = _facts(tmp_path)
    stale = stale_facts(root)
    assert [(s.source, s.recorded, s.current, s.count) for s in stale] == [("gse-one", "0.85.0", "0.86.0", 3)]
    assert stale_facts(_facts(tmp_path / "fresh", current="0.85.0")) == []


def test_stale_facts_ignores_an_empty_version_file(tmp_path):
    root = _facts(tmp_path)
    (root / "gse" / "VERSION").write_text("\n")
    assert stale_facts(root) == []


def test_validate_reports_stale_facts(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    root = _facts(tmp_path)
    (root / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    monkeypatch.chdir(root)
    r = CliRunner().invoke(cli, ["validate"])
    assert r.exit_code == 1, r.output
    assert "read from 0.85.0, the source is now 0.86.0" in r.output
