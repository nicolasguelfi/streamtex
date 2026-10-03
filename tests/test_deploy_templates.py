"""Deployment templates: Dockerfile, entrypoint that never hides a failure, stx deploy diff / ci (#88)."""

from click.testing import CliRunner

from streamtex.cli.commands import cli
from streamtex.cli.deploy_cmd import generate_ci_workflow, generate_dockerfile, generate_entrypoint


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


def test_generated_files_install_streamtex_from_pypi_for_every_uv_command():
    """--frozen with --no-sources is refused by uv; a frozen local-streamtex lock fails (audit2)."""
    dockerfile = generate_dockerfile()
    assert "UV_NO_SOURCES_PACKAGE=streamtex" in dockerfile          # ENV: build AND entrypoint
    assert "RUN uv sync --no-dev" in dockerfile and "uv sync --frozen" not in dockerfile
    assert 'if uv run python -c "import playwright"' in dockerfile   # pdf extra is optional
    assert '"tomlkit>=0.13"' in dockerfile and '"click>=8.0"' in dockerfile
    workflow = generate_ci_workflow()
    assert "UV_NO_SOURCES_PACKAGE: streamtex" in workflow and "uv sync --frozen" not in workflow
