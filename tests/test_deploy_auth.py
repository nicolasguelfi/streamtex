"""Tests for stx deploy lock / unlock / passwd / auth-status (#10, #104), against a fake Coolify."""

import base64
from datetime import date

import click
import pytest
from click.testing import CliRunner

from streamtex.cli import deploy_auth_cmd
from streamtex.cli.commands import cli
from streamtex.cli.coolify import CoolifyClient, DeployResult
from streamtex.cli.deploy_auth_cmd import (
    AUTH_MODES,
    AuthMode,
    describe_face,
    parse_password_spec,
    register_auth_mode,
)
from streamtex.deploy.stx_auth import check_password, parse_records

UUID = "abc123-def456-ghi789"


class FakeCoolify:
    """The parts of CoolifyClient the access-control commands use."""

    def __init__(self, basic_patchable=True):
        self.envs: list[dict] = []
        self.app = {"is_http_basic_auth_enabled": False, "http_basic_auth_username": None}
        self.basic_patchable = basic_patchable
        self.restarts: list[str] = []
        self.literal: dict[str, bool] = {}
        self.sources = {}

    def get_env_vars(self, uuid):
        return [dict(e) for e in self.envs]

    def set_env_var(self, uuid, key, value, is_build=False, is_literal=False):
        self.envs = [e for e in self.envs if e["key"] != key]
        self.envs.append({"uuid": f"env-{key}", "key": key, "value": value, "is_preview": False})
        self.literal[key] = is_literal
        return {}

    def delete_env_var(self, uuid, key):
        n = len(self.envs)
        self.envs = [e for e in self.envs if e["key"] != key]
        return n - len(self.envs)

    def update_app(self, uuid, **fields):
        if self.basic_patchable:
            self.app.update(fields)
        return {}

    def get_app_raw(self, uuid):
        return dict(self.app)

    def restart(self, uuid):
        self.restarts.append(uuid)
        return DeployResult(uuid=uuid)

    def env(self):
        return {e["key"]: e["value"] for e in self.envs}


@pytest.fixture
def fake(tmp_path, monkeypatch):
    client = FakeCoolify()
    monkeypatch.setattr(CoolifyClient, "from_env", classmethod(lambda cls, env_path=None: client))
    monkeypatch.chdir(tmp_path)
    return client


def _run(*args, input=None):
    return CliRunner().invoke(cli, ["deploy", *args], input=input, catch_exceptions=False)


def _decode(value):
    return parse_records(base64.b64decode(value).decode())


PASSWORDS = """
[default]
live = "COHORT1:Pw-one-1,COHORT2:Pw-two-2"
html = "Html-only-3"

[special.live]
GUESTS = { password = "Guest-4", valid_until = "2027-01-31" }

[special]
html = "x"
"""


# ---------------------------------------------------------------------------
# Password lists
# ---------------------------------------------------------------------------


class TestPasswordSpec:
    def test_single_password(self):
        [e] = parse_password_spec("secret", "w")
        assert (e.label, e.password, e.valid_until) == ("default", "secret", None)

    def test_pairs(self):
        es = parse_password_spec("PROMPT261013:PT790948,PROMPT270115:PT599038", "w")
        assert [(e.label, e.password) for e in es] == [("PROMPT261013", "PT790948"), ("PROMPT270115", "PT599038")]

    def test_table_with_end_date(self):
        es = parse_password_spec({"A": "p:with,colon", "B": {"password": "q", "valid_until": date(2027, 1, 31)}}, "w")
        assert es[0].password == "p:with,colon"
        assert es[1].valid_until == date(2027, 1, 31)

    @pytest.mark.parametrize("spec,message", [
        ("A:same,B:same", "share a password"),
        ("A:x,A:y", "appears twice"),
        ("bad label:x", "label"),
        ("A:", "empty password"),
        ("A:two words", "whitespace"),
        ({"A": "tab\there"}, "whitespace"),
        ({"A": "nbsp\u00a0here"}, "whitespace"),
        ("A:x,nocolon", "not label:password"),
        ({"A": 3}, "expected a password"),
        ({"A": {"password": "x", "valid_until": "soon"}}, "valid_until"),
        (",".join(f"L{i}:p{i}" for i in range(33)), "at most 32"),
    ])
    def test_refused(self, spec, message):
        with pytest.raises(click.ClickException, match=message):
            parse_password_spec(spec, "w")

    def test_describe_face_never_shows_a_secret(self):
        value = deploy_auth_cmd.encode_face(parse_password_spec("A:topsecret", "w"))
        text = describe_face(value)
        assert text == "password (1: A)"
        assert "topsecret" not in text
        assert describe_face(None) == "off"
        assert describe_face("open") == "open"
        assert describe_face("!!!").startswith("closed")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


class TestLockSession:
    def test_lock_hashes_locally_and_restarts(self, fake, tmp_path):
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS)
        r = _run("lock", UUID, "--yes")
        assert r.exit_code == 0, r.output
        env = fake.env()
        live, html = _decode(env["STX_AUTH_LIVE"]), _decode(env["STX_AUTH_HTML"])
        assert [e.label for e in live.entries] == ["COHORT1", "COHORT2"]
        assert check_password(live.entry("COHORT2").record, "Pw-two-2")
        assert check_password(html.entry("default").record, "Html-only-3")
        assert fake.literal["STX_AUTH_LIVE"] and fake.literal["STX_AUTH_HTML"]
        for secret in ("Pw-one-1", "Pw-two-2", "Html-only-3"):
            assert secret not in r.output
            assert all(secret not in v for v in env.values())
        assert fake.restarts == [UUID]
        assert "password (2: COHORT1, COHORT2)" in r.output

    def test_one_face_only_leaves_the_other_open(self, fake, tmp_path):
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS)
        r = _run("lock", UUID, "--yes", "--faces", "live", "--no-restart")
        assert r.exit_code == 0, r.output
        assert fake.env()["STX_AUTH_HTML"] == "open"
        assert fake.restarts == []
        assert "Not restarted" in r.output

    def test_section_and_end_date(self, fake, tmp_path):
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS)
        r = _run("lock", UUID, "--yes", "--section", "special")
        assert r.exit_code == 0, r.output
        [e] = _decode(fake.env()["STX_AUTH_LIVE"]).entries
        assert (e.label, e.valid_until) == ("GUESTS", date(2027, 1, 31))
        assert "GUESTS until 2027-01-31" in r.output

    def test_missing_file_or_face(self, fake, tmp_path):
        r = CliRunner().invoke(cli, ["deploy", "lock", UUID, "--yes"])
        assert r.exit_code != 0 and ".stx-passwords.toml not found" in r.output
        (tmp_path / ".stx-passwords.toml").write_text('[default]\nlive = "x"\n')
        r = CliRunner().invoke(cli, ["deploy", "lock", UUID, "--yes"])
        assert r.exit_code != 0 and "no 'html' passwords" in r.output
        assert fake.env() == {}

    def test_keypad_warning(self, fake, tmp_path):
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS)
        fake.set_env_var(UUID, "STX_PASSWORD", "demo")
        r = _run("lock", UUID, "--yes")
        assert "the keypad will not be shown" in r.output

    def test_warns_when_the_passwords_file_is_tracked(self, fake, tmp_path):
        import subprocess
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS)
        assert "not git-ignored" in _run("lock", UUID, "--yes").output
        (tmp_path / ".gitignore").write_text(".stx-passwords.toml\n")
        assert "not git-ignored" not in _run("lock", UUID, "--yes").output

    def test_passwd_reapplies(self, fake, tmp_path):
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS)
        _run("lock", UUID, "--yes")
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS.replace("COHORT1:Pw-one-1,", ""))
        r = _run("passwd", UUID, "--yes")
        assert r.exit_code == 0, r.output
        assert [e.label for e in _decode(fake.env()["STX_AUTH_LIVE"]).entries] == ["COHORT2"]
        assert fake.restarts == [UUID, UUID]


class TestOtherModes:
    def test_stx_password_prompted(self, fake):
        r = _run("lock", UUID, "--yes", "--mode", "stx-password", input="DEMO42\n")
        assert r.exit_code == 0, r.output
        assert fake.env()["STX_PASSWORD"] == "DEMO42"
        assert "DEMO42" not in r.output

    def test_basic(self, fake):
        r = _run("lock", UUID, "--yes", "--mode", "basic", "--user", "admin", input="pw\n")
        assert r.exit_code == 0, r.output
        assert fake.app["is_http_basic_auth_enabled"] is True
        assert fake.app["http_basic_auth_username"] == "admin"

    def test_basic_not_allowed_by_this_coolify(self, fake):
        fake.basic_patchable = False
        r = CliRunner().invoke(cli, ["deploy", "lock", UUID, "--yes", "--mode", "basic", "--user", "u",
                                     "--password", "p"])
        assert r.exit_code != 0
        assert "does not allow it through its API" in r.output
        assert fake.restarts == []

    def test_unknown_mode(self, fake):
        r = CliRunner().invoke(cli, ["deploy", "lock", UUID, "--mode", "oauth"])
        assert r.exit_code != 0 and "unknown mode" in r.output


class TestUnlockAndStatus:
    def test_status_and_unlock_all(self, fake, tmp_path):
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS)
        _run("lock", UUID, "--yes")
        fake.set_env_var(UUID, "STX_PASSWORD", "demo")
        _run("lock", UUID, "--yes", "--mode", "basic", "--user", "admin", "--password", "pw")
        r = _run("auth-status", UUID)
        assert r.exit_code == 0, r.output
        assert "COHORT1" in r.output and "Pw-one-1" not in r.output
        assert "not shown" in r.output
        assert "admin" in r.output and "pw" not in r.output.replace("password", "")
        r = _run("unlock", UUID, "--yes")
        assert r.exit_code == 0, r.output
        assert fake.env() == {}
        assert fake.app["is_http_basic_auth_enabled"] is False
        r = _run("unlock", UUID, "--yes")
        assert "Nothing to unlock" in r.output

    def test_unlock_one_mode(self, fake, tmp_path):
        (tmp_path / ".stx-passwords.toml").write_text(PASSWORDS)
        _run("lock", UUID, "--yes")
        fake.set_env_var(UUID, "STX_PASSWORD", "demo")
        _run("unlock", UUID, "--yes", "--mode", "session")
        assert fake.env() == {"STX_PASSWORD": "demo"}

    def test_face_without_value_reported_closed(self, fake):
        fake.set_env_var(UUID, "STX_AUTH_HTML", "open")
        r = _run("auth-status", UUID)
        assert "live: closed" in r.output and "html: open" in r.output


def test_registry_accepts_new_modes(fake):
    class IpMode(AuthMode):
        name, level, summary = "ip-test", "proxy", "test mode"
        enabled = False

        def enable(self, ctx):
            IpMode.enabled = True

        def disable(self, ctx):
            IpMode.enabled = False

        def status(self, ctx, env):
            return "on" if IpMode.enabled else "off"

    register_auth_mode(IpMode())
    try:
        r = _run("lock", UUID, "--yes", "--mode", "ip-test", "--no-restart")
        assert r.exit_code == 0, r.output
        assert IpMode.enabled
        assert "ip-test" in _run("auth-status", UUID).output
    finally:
        AUTH_MODES.pop("ip-test")
