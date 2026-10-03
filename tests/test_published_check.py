"""Versions and the published wheel: .stx-version / pyproject / uv.lock coherence, stx validate --build --published (#87)."""

import subprocess
from pathlib import Path

from streamtex.cli import published_check

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
