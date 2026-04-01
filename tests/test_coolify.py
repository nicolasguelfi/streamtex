"""Unit tests for streamtex.cli.coolify — Coolify API client."""

import json
from unittest.mock import patch

import pytest

from streamtex.cli.coolify import (
    COOLIFY_DASHBOARD_PORT,
    DEFAULT_DEPLOY_TIMEOUT,
    DEFAULT_SERVER_IMAGE,
    DEFAULT_SERVER_LOCATION,
    DEFAULT_SERVER_NAME,
    DEFAULT_SERVER_TYPE,
    DEFAULT_SSH_KEY_NAME,
    DEFAULT_SSH_KEY_PATH,
    DEFAULT_SSH_USER,
    STREAMLIT_PORT,
    AppEntry,
    AppInfo,
    CoolifyClient,
    CoolifyError,
    CoolifyInfo,
    DeployResult,
    DeployState,
    DomainInfo,
    ServerInfo,
    _parse_env_file,
    load_deploy_state,
    load_typed_state,
    save_deploy_state,
    save_typed_state,
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
                body={"key": "FOO", "value": "bar"},
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


# ── Constants ─────────────────────────────────────────────────────────

class TestConstants:
    def test_default_ssh_key_path(self):
        assert DEFAULT_SSH_KEY_PATH == "~/.ssh/hetzner_streamtex"

    def test_default_ssh_key_name(self):
        assert DEFAULT_SSH_KEY_NAME == "streamtex-deploy"

    def test_default_ssh_user(self):
        assert DEFAULT_SSH_USER == "deploy"

    def test_default_server_type(self):
        assert DEFAULT_SERVER_TYPE == "cax21"

    def test_default_server_location(self):
        assert DEFAULT_SERVER_LOCATION == "fsn1"

    def test_default_server_image(self):
        assert DEFAULT_SERVER_IMAGE == "ubuntu-24.04"

    def test_default_server_name(self):
        assert DEFAULT_SERVER_NAME == "streamtex-prod"

    def test_default_deploy_timeout(self):
        assert DEFAULT_DEPLOY_TIMEOUT == 300

    def test_streamlit_port(self):
        assert STREAMLIT_PORT == 8501

    def test_coolify_dashboard_port(self):
        assert COOLIFY_DASHBOARD_PORT == 8000


# ── DeployState dataclass ─────────────────────────────────────────────

class TestDeployState:
    def test_default_construction(self):
        state = DeployState()
        assert state.version == "2.0"
        assert state.server is None
        assert state.domain is None
        assert state.coolify is None
        assert state.applications is None
        assert state.phases_completed is None
        assert state.cdn is None
        assert state.security is None

    def test_to_dict_empty(self):
        state = DeployState()
        d = state.to_dict()
        assert d == {"version": "2.0"}

    def test_to_dict_with_infrastructure(self):
        state = DeployState(
            server=ServerInfo(name="test-srv", id=123, ipv4="1.2.3.4"),
            domain=DomainInfo(base="example.org", registrar="ovh"),
            coolify=CoolifyInfo(url="https://coolify.example.org", server_uuid="su1"),
            phases_completed={"provision": "2026-03-20T10:00:00"},
            applications=[
                AppEntry(name="app1", uuid="u1", subdomain="app1", url="https://app1.example.org"),
            ],
        )
        d = state.to_dict()
        assert d["version"] == "2.0"
        assert d["infrastructure"]["server"]["name"] == "test-srv"
        assert d["infrastructure"]["server"]["id"] == 123
        assert d["infrastructure"]["domain"]["base"] == "example.org"
        assert d["infrastructure"]["coolify"]["url"] == "https://coolify.example.org"
        assert d["phases_completed"]["provision"] == "2026-03-20T10:00:00"
        assert len(d["applications"]) == 1
        assert d["applications"][0]["name"] == "app1"

    def test_from_dict_round_trip(self):
        original = DeployState(
            server=ServerInfo(name="srv", id=42, ipv4="10.0.0.1"),
            domain=DomainInfo(base="test.org"),
            coolify=CoolifyInfo(url="https://c.test", server_uuid="s1"),
            phases_completed={"provision": "ts1", "secure": "ts2"},
            applications=[
                AppEntry(name="a1", uuid="u1", url="https://a1.test"),
                AppEntry(name="a2", uuid="u2", folder="manuals/intro"),
            ],
        )
        d = original.to_dict()
        restored = DeployState.from_dict(d)
        assert restored.version == original.version
        assert restored.server.name == "srv"
        assert restored.server.id == 42
        assert restored.domain.base == "test.org"
        assert restored.coolify.url == "https://c.test"
        assert restored.phases_completed == {"provision": "ts1", "secure": "ts2"}
        assert len(restored.applications) == 2
        assert restored.applications[0].name == "a1"
        assert restored.applications[1].folder == "manuals/intro"

    def test_from_dict_v1_format(self):
        """Test with a v1-style dict (production .stx-deploy.json format)."""
        v1_data = {
            "version": "1.0",
            "infrastructure": {
                "server": {"name": "streamtex-prod", "id": 99, "ipv4": "138.199.148.59"},
                "coolify": {"url": "https://coolify.streamtex.org", "server_uuid": "abc"},
                "domain": {"base": "streamtex.org", "registrar": "ovh"},
            },
            "applications": [
                {"name": "docs", "uuid": "x1", "subdomain": "docs", "url": "https://docs.streamtex.org"},
            ],
            "phases_completed": {"provision": "2026-03-20"},
        }
        state = DeployState.from_dict(v1_data)
        assert state.version == "1.0"
        assert state.server.name == "streamtex-prod"
        assert state.server.ipv4 == "138.199.148.59"
        assert state.coolify.url == "https://coolify.streamtex.org"
        assert state.domain.base == "streamtex.org"
        assert len(state.applications) == 1
        assert state.applications[0].uuid == "x1"
        assert state.phases_completed["provision"] == "2026-03-20"

    def test_from_dict_empty(self):
        state = DeployState.from_dict({})
        assert state.version == "1.0"  # default when missing
        assert state.server is None
        assert state.domain is None
        assert state.coolify is None
        assert state.applications is None
        assert state.phases_completed is None

    def test_from_dict_partial_server_only(self):
        data = {
            "infrastructure": {
                "server": {"name": "my-srv", "ipv4": "5.6.7.8"},
            },
        }
        state = DeployState.from_dict(data)
        assert state.server is not None
        assert state.server.name == "my-srv"
        assert state.server.ipv4 == "5.6.7.8"
        assert state.coolify is None
        assert state.domain is None
        assert state.applications is None


# ── ServerInfo, DomainInfo, CoolifyInfo, AppEntry ─────────────────────

class TestServerInfo:
    def test_defaults(self):
        s = ServerInfo()
        assert s.name == ""
        assert s.id == 0
        assert s.type == DEFAULT_SERVER_TYPE
        assert s.location == DEFAULT_SERVER_LOCATION
        assert s.image == DEFAULT_SERVER_IMAGE
        assert s.ipv4 == ""
        assert s.ssh_key_path == DEFAULT_SSH_KEY_PATH
        assert s.ssh_key_name == DEFAULT_SSH_KEY_NAME
        assert s.ssh_key_id == 0

    def test_with_values(self):
        s = ServerInfo(name="prod", id=42, ipv4="1.2.3.4", type="cx22")
        assert s.name == "prod"
        assert s.id == 42
        assert s.ipv4 == "1.2.3.4"
        assert s.type == "cx22"


class TestDomainInfo:
    def test_defaults(self):
        d = DomainInfo()
        assert d.base == ""
        assert d.registrar == ""
        assert d.wildcard_dns == ""

    def test_with_values(self):
        d = DomainInfo(base="example.org", registrar="ovh", wildcard_dns="*.example.org")
        assert d.base == "example.org"
        assert d.registrar == "ovh"


class TestCoolifyInfo:
    def test_defaults(self):
        c = CoolifyInfo()
        assert c.url == ""
        assert c.server_uuid == ""
        assert c.project_uuid == ""
        assert c.environment == "production"
        assert c.environment_uuid == ""

    def test_with_values(self):
        c = CoolifyInfo(url="https://c.org", server_uuid="s1", project_uuid="p1")
        assert c.url == "https://c.org"
        assert c.server_uuid == "s1"


class TestAppEntry:
    def test_defaults(self):
        a = AppEntry()
        assert a.name == ""
        assert a.uuid == ""
        assert a.subdomain == ""
        assert a.url == ""
        assert a.folder == ""
        assert a.github_repo == ""
        assert a.branch == "main"
        assert a.deployed_at == ""

    def test_with_values(self):
        a = AppEntry(name="docs", uuid="u1", subdomain="docs",
                     url="https://docs.example.org", folder="manuals/intro")
        assert a.name == "docs"
        assert a.uuid == "u1"
        assert a.folder == "manuals/intro"


# ── load_typed_state / save_typed_state ───────────────────────────────

class TestTypedState:
    def test_load_typed_state_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        state = load_typed_state()
        assert isinstance(state, DeployState)
        assert state.version == "2.0"
        assert state.server is None

    def test_save_and_load_round_trip(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        original = DeployState(
            server=ServerInfo(name="test", id=1, ipv4="10.0.0.1"),
            coolify=CoolifyInfo(url="https://c.test"),
            applications=[AppEntry(name="app1", uuid="u1")],
        )
        save_typed_state(original)
        loaded = load_typed_state()
        assert isinstance(loaded, DeployState)
        assert loaded.server.name == "test"
        assert loaded.coolify.url == "https://c.test"
        assert len(loaded.applications) == 1
        assert loaded.applications[0].name == "app1"

    def test_save_to_explicit_path(self, tmp_path):
        p = tmp_path / "state.json"
        state = DeployState(server=ServerInfo(name="srv"))
        save_typed_state(state, path=p)
        loaded = load_typed_state(path=p)
        assert loaded.server.name == "srv"


# ── CoolifyClient new methods (mocked) ───────────────────────────────

class TestCoolifyClientNewMethods:
    def _client(self):
        return CoolifyClient("https://coolify.test", "testtoken")

    def test_create_app(self):
        c = self._client()
        mock_resp = {"uuid": "new-uuid", "name": "my-app"}
        with patch.object(c, "_post", return_value=mock_resp) as mock:
            result = c.create_app(
                project_uuid="proj1",
                server_uuid="srv1",
                name="my-app",
                repository="owner/repo",
                branch="main",
            )
            mock.assert_called_once_with("/api/v1/applications", body={
                "project_uuid": "proj1",
                "server_uuid": "srv1",
                "environment_name": "production",
                "name": "my-app",
                "git_repository": "owner/repo",
                "git_branch": "main",
                "build_pack": "dockerfile",
                "dockerfile_location": "/Dockerfile",
            })
            assert result["uuid"] == "new-uuid"

    def test_create_app_custom_params(self):
        c = self._client()
        with patch.object(c, "_post", return_value={"uuid": "u"}) as mock:
            c.create_app(
                project_uuid="p", server_uuid="s", name="n",
                repository="r", branch="dev",
                build_pack="nixpacks", dockerfile_location="/docker/Dockerfile",
                environment_name="staging",
            )
            call_body = mock.call_args[1]["body"] if "body" in mock.call_args[1] else mock.call_args[0][1]
            # Access via keyword
            body = mock.call_args.kwargs.get("body", mock.call_args[0][1] if len(mock.call_args[0]) > 1 else None)
            assert body["build_pack"] == "nixpacks"
            assert body["environment_name"] == "staging"
            assert body["git_branch"] == "dev"

    def test_delete_app(self):
        c = self._client()
        with patch.object(c, "_delete", return_value={"message": "deleted"}) as mock:
            result = c.delete_app("uuid-to-delete")
            mock.assert_called_once_with("/api/v1/applications/uuid-to-delete")
            assert result["message"] == "deleted"

    def test_verify_token_success(self):
        c = self._client()
        with patch.object(c, "_get", return_value=[]):
            assert c.verify_token() is True

    def test_verify_token_failure(self):
        c = self._client()
        with patch.object(c, "_get", side_effect=CoolifyError("HTTP 401")):
            assert c.verify_token() is False

    def test_stop(self):
        c = self._client()
        with patch.object(c, "_post", return_value={"message": "Stop queued."}) as mock:
            result = c.stop("u1")
            mock.assert_called_once_with("/api/v1/applications/u1/stop")
            assert result.success is True
