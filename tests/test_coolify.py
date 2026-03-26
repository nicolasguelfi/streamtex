"""Unit tests for streamtex.cli.coolify — Coolify API client."""

import json
from unittest.mock import patch

import pytest

from streamtex.cli.coolify import (
    AppInfo,
    CoolifyClient,
    CoolifyError,
    DeployResult,
    _parse_env_file,
    load_deploy_state,
    save_deploy_state,
)

# ── _parse_env_file ──────────────────────────────────────────────────────

class TestParseEnvFile:
    def test_basic(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("KEY1=value1\nKEY2=value2\n")
        result = _parse_env_file(f)
        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_comments_and_blanks(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("# comment\n\nKEY=val\n  # another\n")
        result = _parse_env_file(f)
        assert result == {"KEY": "val"}

    def test_value_with_equals(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("TOKEN=abc=def=ghi\n")
        result = _parse_env_file(f)
        assert result == {"TOKEN": "abc=def=ghi"}

    def test_empty_file(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("")
        assert _parse_env_file(f) == {}


# ── CoolifyClient construction ───────────────────────────────────────────

class TestCoolifyClientInit:
    def test_basic(self):
        c = CoolifyClient("https://coolify.example.org", "mytoken")
        assert c.url == "https://coolify.example.org"
        assert c.token == "mytoken"

    def test_strips_trailing_slash(self):
        c = CoolifyClient("https://coolify.example.org/", "t")
        assert c.url == "https://coolify.example.org"


class TestCoolifyClientFromEnv:
    def test_from_env_file(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".stx-deploy.env"
        env_file.write_text("COOLIFY_URL=https://c.example.org\nCOOLIFY_API_TOKEN=tok123\n")
        monkeypatch.chdir(tmp_path)
        c = CoolifyClient.from_env()
        assert c.url == "https://c.example.org"
        assert c.token == "tok123"

    def test_from_env_vars(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("COOLIFY_URL", "https://env.example.org")
        monkeypatch.setenv("COOLIFY_API_TOKEN", "envtok")
        c = CoolifyClient.from_env()
        assert c.url == "https://env.example.org"
        assert c.token == "envtok"

    def test_missing_raises(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("COOLIFY_URL", raising=False)
        monkeypatch.delenv("COOLIFY_API_TOKEN", raising=False)
        with pytest.raises(CoolifyError, match="Coolify URL not found"):
            CoolifyClient.from_env()

    def test_from_deploy_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("COOLIFY_API_TOKEN", "tok")
        deploy_json = tmp_path / ".stx-deploy.json"
        deploy_json.write_text(json.dumps({
            "infrastructure": {"coolify": {"url": "https://json.example.org"}}
        }))
        c = CoolifyClient.from_env()
        assert c.url == "https://json.example.org"


# ── DeployResult ──────────────────────────────────────────────────────────

class TestDeployResult:
    def test_defaults(self):
        r = DeployResult(uuid="abc")
        assert r.success is True
        assert r.healthy is False
        assert r.deployment_uuid == ""

    def test_failure(self):
        r = DeployResult(uuid="abc", success=False, message="error")
        assert r.success is False
        assert r.message == "error"


# ── AppInfo ───────────────────────────────────────────────────────────────

class TestAppInfo:
    def test_basic(self):
        a = AppInfo(uuid="u", name="n", status="running:healthy", fqdn="https://x.org")
        assert a.uuid == "u"
        assert a.name == "n"
        assert "healthy" in a.status


# ── API methods (mocked) ─────────────────────────────────────────────────

class TestCoolifyAPI:
    def _mock_client(self):
        return CoolifyClient("https://coolify.test", "testtoken")

    def test_list_apps(self):
        c = self._mock_client()
        mock_data = [
            {"uuid": "u1", "name": "app1", "status": "running:healthy",
             "fqdn": "https://app1.test", "git_repository": "owner/repo", "git_branch": "main"},
        ]
        with patch.object(c, "_get", return_value=mock_data):
            apps = c.list_apps()
            assert len(apps) == 1
            assert apps[0].uuid == "u1"
            assert apps[0].name == "app1"
            assert apps[0].repository == "owner/repo"

    def test_get_app(self):
        c = self._mock_client()
        mock_data = {"uuid": "u1", "name": "app1", "status": "running:healthy", "fqdn": "https://a.test"}
        with patch.object(c, "_get", return_value=mock_data):
            app = c.get_app("u1")
            assert app.uuid == "u1"

    def test_rebuild(self):
        c = self._mock_client()
        mock_resp = {"message": "Deployment request queued.", "deployment_uuid": "dep1"}
        with patch.object(c, "_post", return_value=mock_resp):
            result = c.rebuild("u1")
            assert result.success is True
            assert result.deployment_uuid == "dep1"

    def test_rebuild_failure(self):
        c = self._mock_client()
        with patch.object(c, "_post", side_effect=CoolifyError("HTTP 404")):
            result = c.rebuild("u1")
            assert result.success is False
            assert "404" in result.message

    def test_restart(self):
        c = self._mock_client()
        mock_resp = {"message": "Restart queued.", "deployment_uuid": "dep2"}
        with patch.object(c, "_post", return_value=mock_resp):
            result = c.restart("u1")
            assert result.success is True

    def test_rebuild_calls_start_endpoint(self):
        c = self._mock_client()
        with patch.object(c, "_post", return_value={"message": "ok"}) as mock:
            c.rebuild("myuuid")
            mock.assert_called_once_with("/api/v1/applications/myuuid/start")

    def test_restart_calls_restart_endpoint(self):
        c = self._mock_client()
        with patch.object(c, "_post", return_value={"message": "ok"}) as mock:
            c.restart("myuuid")
            mock.assert_called_once_with("/api/v1/applications/myuuid/restart")

    def test_wait_healthy_immediate(self):
        c = self._mock_client()
        with patch.object(c, "get_app", return_value=AppInfo(
            uuid="u1", name="a", status="running:healthy", fqdn=""
        )):
            assert c.wait_healthy("u1", timeout=5) is True

    def test_wait_healthy_timeout(self):
        c = self._mock_client()
        with patch.object(c, "get_app", return_value=AppInfo(
            uuid="u1", name="a", status="building", fqdn=""
        )):
            assert c.wait_healthy("u1", timeout=1, poll_interval=1) is False

    def test_wait_healthy_error_status(self):
        c = self._mock_client()
        with patch.object(c, "get_app", return_value=AppInfo(
            uuid="u1", name="a", status="error", fqdn=""
        )):
            assert c.wait_healthy("u1", timeout=5) is False

    def test_set_env_var(self):
        c = self._mock_client()
        with patch.object(c, "_post", return_value={"id": 1}) as mock:
            c.set_env_var("u1", "FOO", "bar")
            mock.assert_called_once_with(
                "/api/v1/applications/u1/envs",
                body={"key": "FOO", "value": "bar", "is_build_time": False},
            )

    def test_set_fqdn(self):
        c = self._mock_client()
        with patch.object(c, "_patch", return_value={}) as mock:
            c.set_fqdn("u1", "https://my.domain.org")
            mock.assert_called_once_with(
                "/api/v1/applications/u1",
                body={"fqdn": "https://my.domain.org"},
            )


# ── State file helpers ────────────────────────────────────────────────────

class TestStateFile:
    def test_load_missing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert load_deploy_state() == {}

    def test_save_and_load(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        state = {"version": "1.0", "infrastructure": {"provider": "hetzner"}}
        out = save_deploy_state(state)
        assert out.exists()
        loaded = load_deploy_state()
        assert loaded["version"] == "1.0"

    def test_save_to_explicit_path(self, tmp_path):
        p = tmp_path / "custom.json"
        save_deploy_state({"test": True}, path=p)
        assert p.exists()
        assert json.loads(p.read_text())["test"] is True
