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


# ---------------------------------------------------------------------------
# Server-side login screen (#104): wired in, inactive unless STX_AUTH_* is set
# ---------------------------------------------------------------------------

import base64  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402

import pytest  # noqa: E402

from streamtex.cli.deploy_cmd import generate_nginx_conf  # noqa: E402


def _location(conf: str, header: str) -> str:
    """The body of the nginx location whose opening line is *header*."""
    start = conf.index(header)
    depth, i = 0, conf.index("{", start)
    for j in range(i, len(conf)):
        depth += {"{": 1, "}": -1}.get(conf[j], 0)
        if depth == 0:
            return conf[i:j]
    raise AssertionError(header)


def test_nginx_protects_both_faces_and_media_but_not_health():
    conf = generate_nginx_conf()
    assert "include /etc/nginx/stx-auth/live.conf;" in _location(conf, "location / {")
    assert "include /etc/nginx/stx-auth/html.conf;" in _location(conf, "location /html/ {")
    assert "include /etc/nginx/stx-auth/html.conf;" in _location(conf, "location = /html/ {")
    assert "include /etc/nginx/stx-auth/media.conf;" in _location(conf, "location /app/static/ {")
    assert "stx-auth" not in _location(conf, "location = /_stcore/health {")
    assert "@@" not in conf


@pytest.mark.parametrize("face,login,home", [("live", "/_login", "/"), ("html", "/html/_login", "/html/")])
def test_nginx_sets_every_header_stx_auth_trusts(face, login, home):
    conf = generate_nginx_conf()
    for header in (f"location = /_stx_auth_{face} {{", f"location @stx_login_{face} {{",
                   f"location = {login} {{"):
        body = _location(conf, header)
        assert f"proxy_set_header X-Stx-Site {face};" in body
        assert f"proxy_set_header X-Stx-Cookie stx_{face};" in body
        assert f"proxy_set_header X-Stx-Login {login};" in body
        assert f"proxy_set_header X-Stx-Home {home};" in body
        assert 'proxy_set_header X-Forwarded-Prefix "";' in body
        assert "proxy_set_header X-Original-URI $request_uri;" in body
    assert "internal;" in _location(conf, f"location = /_stx_auth_{face} {{")
    assert "limit_req zone=stxlogin" in _location(conf, f"location = {login} {{")


def test_nginx_keeps_connections_to_stx_auth_alive():
    """#108: one TCP connect per checked file filled the service's backlog."""
    conf = generate_nginx_conf()
    assert re.search(r"upstream stx_auth \{\s*server 127\.0\.0\.1:9100;\s*keepalive \d+;", conf)
    body = _location(conf, "location = /_stx_auth_live {")
    assert "proxy_http_version 1.1;" in body and 'proxy_set_header Connection "";' in body


def test_dockerfile_creates_empty_login_snippets():
    assert "touch /etc/nginx/stx-auth/live.conf /etc/nginx/stx-auth/html.conf" in generate_dockerfile()


def _auth_section(tmp_path):
    """The entrypoint's login section, pointed at *tmp_path*, with stub commands."""
    entry = generate_entrypoint()
    section = entry[entry.index("# --- Server-side login screen"):entry.index("# --- Start services")]
    section = (section.replace("/etc/nginx/stx-auth", str(tmp_path / "conf"))
               .replace("/var/lib/stx-auth", str(tmp_path / "state")))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, body in {
        "uv": f'[ -f "{tmp_path}/stx_auth.py" ] && echo "{tmp_path}/stx_auth.py" || exit 1',
        "python3": f'echo "$STX_AUTH_ROOT" > "{tmp_path}/started"; exec sleep 3 </dev/null >/dev/null 2>&1',
        "curl": "exit 0",
    }.items():
        (bin_dir / name).write_text(f"#!/bin/bash\n{body}\n")
        (bin_dir / name).chmod(0o755)
    prelude = ('set -e\nMODE="${STX_SERVE_MODE:-dual}"\n'
               f'report_failure() {{ echo "FAIL $1" >> "{tmp_path}/failures"; }}\n')
    return prelude + section + "\nkill %1 2>/dev/null || true\n"


def _run_auth(tmp_path, **env):
    script = _auth_section(tmp_path)
    full_env = {"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", **env}
    return subprocess.run(["bash", "-c", script], env=full_env, capture_output=True, text=True, timeout=30)


def _read(p):
    return p.read_text() if p.exists() else None


@pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")
class TestEntrypointLogin:
    def test_off_by_default(self, tmp_path):
        r = _run_auth(tmp_path)
        assert r.returncode == 0, r.stderr
        for f in ("live", "html", "media"):
            assert _read(tmp_path / "conf" / f"{f}.conf") == ""
        assert not (tmp_path / "started").exists()

    def test_on_writes_records_snippets_and_starts_the_service(self, tmp_path):
        (tmp_path / "stx_auth.py").write_text("")
        records = "A:scrypt$16$1$1$00$00\n"
        r = _run_auth(tmp_path, STX_AUTH_LIVE=base64.b64encode(records.encode()).decode(), STX_AUTH_HTML="open")
        assert r.returncode == 0, r.stderr
        assert _read(tmp_path / "state/sites/live/pass") == records
        assert _read(tmp_path / "state/sites/html/pass") == "open\n"
        assert "auth_request /_stx_auth_live;" in _read(tmp_path / "conf/live.conf")
        assert "auth_request /_stx_auth_html;" in _read(tmp_path / "conf/html.conf")
        assert _read(tmp_path / "conf/media.conf") == _read(tmp_path / "conf/live.conf")
        assert oct((tmp_path / "state/sites/live/pass").stat().st_mode)[-3:] == "600"
        assert "live: password, html: open" in r.stdout
        assert _read(tmp_path / "started").strip() == str(tmp_path / "state")

    def test_face_without_value_is_closed(self, tmp_path):
        (tmp_path / "stx_auth.py").write_text("")
        r = _run_auth(tmp_path, STX_AUTH_HTML="open")
        assert r.returncode == 0, r.stderr
        assert not (tmp_path / "state/sites/live/pass").exists()
        assert "auth_request /_stx_auth_live;" in _read(tmp_path / "conf/live.conf")

    def test_public_media(self, tmp_path):
        (tmp_path / "stx_auth.py").write_text("")
        r = _run_auth(tmp_path, STX_AUTH_LIVE="open", STX_AUTH_PUBLIC_MEDIA="1")
        assert r.returncode == 0, r.stderr
        assert _read(tmp_path / "conf/media.conf") == ""

    def test_bad_base64_closes_the_face_and_says_so(self, tmp_path):
        (tmp_path / "stx_auth.py").write_text("")
        r = _run_auth(tmp_path, STX_AUTH_LIVE="not base64 !!", STX_AUTH_HTML="open")
        assert r.returncode == 0, r.stderr
        assert not (tmp_path / "state/sites/live/pass").exists()
        assert "STX_AUTH_LIVE" in _read(tmp_path / "failures")

    def test_missing_service_closes_the_site(self, tmp_path):
        r = _run_auth(tmp_path, STX_AUTH_LIVE="open")
        assert r.returncode == 0, r.stderr
        for f in ("live", "html", "media"):
            assert _read(tmp_path / "conf" / f"{f}.conf").strip() == "return 503;"
        assert "stx_auth.py not found" in _read(tmp_path / "failures")

    def test_streamlit_only_refuses_to_start(self, tmp_path):
        r = _run_auth(tmp_path, STX_AUTH_LIVE="open", STX_SERVE_MODE="streamlit-only")
        assert r.returncode == 1
        assert "needs Nginx" in r.stderr

    def test_service_is_restarted_after_it_stops(self, tmp_path):
        """Found in a container: under `set -e` the loop died with the service."""
        (tmp_path / "stx_auth.py").write_text("")
        script = _auth_section(tmp_path)  # writes the stubs; the service then dies at once
        (tmp_path / "bin" / "python3").write_text(f'#!/bin/bash\necho x >> "{tmp_path}/runs"\nexit 137\n')
        script = script.replace("\nkill %1", "\nsleep 2.5\nkill %1")
        env = {"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "STX_AUTH_LIVE": "open"}
        r = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, r.stderr
        assert len(_read(tmp_path / "runs").split()) >= 2
        assert "stx_auth stopped (exit 137), restarting" in r.stderr
