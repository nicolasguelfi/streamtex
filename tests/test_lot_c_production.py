"""Lot C — production: versions and the published wheel (L18), deployment
templates and CI (L19), guard rails (L20)."""

import subprocess
from pathlib import Path

from click.testing import CliRunner

from streamtex.cli import published_check
from streamtex.cli.commands import cli
from streamtex.cli.deploy_cmd import generate_ci_workflow, generate_dockerfile, generate_entrypoint
from streamtex.cli.project_cmd import generate_pre_commit_config
from streamtex.cli.project_rules import conflict_markers, deprecated_config

LOCK = """version = 1
[[package]]
name = "streamtex"
version = "{v}"
source = {src}
"""


def _proj(tmp_path, *, stx_version=None, minimum="0.7.0", locked="0.7.30",
          src='{ registry = "https://pypi.org/simple" }'):
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nname = "p"\nversion = "0.1.0"\ndependencies = ["streamtex[cli]>={minimum},<0.8"]\n')
    (tmp_path / "uv.lock").write_text(LOCK.format(v=locked, src=src))
    if stx_version is not None:
        (tmp_path / ".stx-version").write_text(stx_version + "\n")
    return tmp_path


# --- L18 ------------------------------------------------------------------

def test_versions_consistent_project_has_no_problem(tmp_path):
    assert published_check.version_problems(_proj(tmp_path, stx_version="0.7.30")) == []


def test_stx_version_above_the_lock_is_an_error(tmp_path):
    probs = published_check.version_problems(_proj(tmp_path, stx_version="0.7.31"))
    assert [p.severity for p in probs] == ["error"] and "build guard will fail" in probs[0].message


def test_stx_version_below_the_pyproject_minimum_is_a_warning(tmp_path):   # the ai4se6d "0.3.3" case
    probs = published_check.version_problems(_proj(tmp_path, stx_version="0.3.3", minimum="0.6.10"))
    assert [p.severity for p in probs] == ["warning"] and "0.3.3" in probs[0].message


def test_local_streamtex_source_is_reported(tmp_path):
    probs = published_check.version_problems(_proj(tmp_path, src='{ editable = "../streamtex" }'))
    assert probs and "local source" in probs[0].message and "--published" in probs[0].message


def test_published_python_keeps_local_packs_and_drops_only_streamtex_source(tmp_path, monkeypatch):
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        if cmd[:2] == ["uv", "venv"]:
            (Path(cmd[-1]) / "bin").mkdir(parents=True)
            (Path(cmd[-1]) / "bin" / "python").write_text("")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(published_check.subprocess, "run", fake_run)
    py, _log = published_check.published_python(_proj(tmp_path), cache_root=tmp_path / "cache")
    assert py and py.endswith("bin/python")
    compile_cmd = calls[0]
    assert "--no-sources-package" in compile_cmd and "streamtex" in compile_cmd
    assert "--no-sources" not in compile_cmd


def test_published_python_reports_a_project_that_does_not_resolve(tmp_path, monkeypatch):
    monkeypatch.setattr(published_check.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1, "", "No solution found"))
    py, log = published_check.published_python(_proj(tmp_path), cache_root=tmp_path / "cache")
    assert py is None and "No solution found" in log


# --- L19 ------------------------------------------------------------------

def test_dockerfile_exports_once_and_entrypoint_never_hides_a_failure():
    dockerfile = generate_dockerfile()
    assert "RUN uv run stx export html" not in dockerfile and "stx export html --theme" not in dockerfile
    entry = generate_entrypoint()
    assert "2>/dev/null || true" not in entry
    assert 'report_failure "stx export html"' in entry
    assert 'report_failure "stx cache warmup"' in entry
    # the error log is written outside the folder nginx serves (autoindex on)
    assert ">> /app/STX_ERRORS.txt" in entry and "static-html/STX_ERRORS" not in entry


def test_deploy_diff(tmp_path):
    (tmp_path / "Dockerfile").write_text(generate_dockerfile())
    (tmp_path / "entrypoint.sh").write_text(generate_entrypoint().replace("set -e", "set -eu"))
    r = CliRunner().invoke(cli, ["deploy", "diff", str(tmp_path)])
    assert r.exit_code == 0, r.output
    assert "Dockerfile: identical" in r.output
    assert "entrypoint.sh: differs" in r.output and "+set -eu" in r.output
    assert "nginx.conf: absent" in r.output


def test_deploy_ci_writes_the_workflow_once(tmp_path):
    r = CliRunner().invoke(cli, ["deploy", "ci", str(tmp_path)])
    assert r.exit_code == 0, r.output
    wf = tmp_path / ".github" / "workflows" / "stx-validate.yml"
    assert wf.read_text() == generate_ci_workflow()
    assert "stx validate --build" in wf.read_text()
    r = CliRunner().invoke(cli, ["deploy", "ci", str(tmp_path)])
    assert r.exit_code != 0 and "--force" in r.output


# --- L20 ------------------------------------------------------------------

def test_new_projects_get_conflict_marker_hook():
    cfg = generate_pre_commit_config()
    assert "id: ruff" in cfg and "id: check-merge-conflict" in cfg and "id: check-toml" in cfg


def test_conflict_markers_and_deprecated_config(tmp_path):
    (tmp_path / "blocks").mkdir()
    (tmp_path / "blocks" / "bck_a.py").write_text("x = 1\n<<<<<<< HEAD\ny = 2\n=======\ny = 3\n>>>>>>> other\n")
    (tmp_path / "blocks" / "bck_b.py").write_text("ok = True\n")
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n[patterns]\nuse = ["x"]\n')
    assert conflict_markers(tmp_path) == [("blocks/bck_a.py", 2)]
    assert deprecated_config(tmp_path) and deprecated_config(tmp_path)[0].startswith("[patterns]")


def test_validate_reports_hygiene(tmp_path, monkeypatch):
    from streamtex.core import discovery

    monkeypatch.setattr(discovery, "discover_packs", lambda *_a, **_k: [])
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "p"\nversion = "0.1.0"\n')
    (tmp_path / "stx.toml").write_text('[project]\nname = "p"\n[patterns]\nuse = []\n')
    (tmp_path / "a.py").write_text("<<<<<<< HEAD\n")
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(cli, ["validate"])
    assert r.exit_code == 2 and "conflict marker" in r.output and "deprecated" in r.output
