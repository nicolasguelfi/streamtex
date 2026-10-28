"""stx release safety points (#145: G9, G10, G12, G15) and the project's check of an export (#144)."""
import subprocess
import sys
import textwrap
from datetime import date, timedelta

import pytest
from click.testing import CliRunner

from streamtex.cli.deploy_auth_cmd import PlainEntry
from streamtex.cli.release_cmd import publish_cmd, setup_cmd
from streamtex.release import ReleaseError, build, coolify, ops
from streamtex.release import passwords as pw
from streamtex.release.config import load_config

STX_TOML = """
    [release]
    project = "demo"
    {extra}
    [[release.sites]]
    site = "deck"
    book = "docs/deck/book.py"
"""


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    (tmp_path / "stx.toml").write_text(textwrap.dedent(STX_TOML.format(extra="")))
    monkeypatch.chdir(tmp_path)
    return load_config(tmp_path)


# -- G10: publishing every site is asked for -------------------------------------------------------

def test_publish_without_sites_needs_all():
    r = CliRunner().invoke(publish_cmd, [])
    assert r.exit_code == 1 and "--all for every site" in r.output


def test_all_goes_alone():
    r = CliRunner().invoke(publish_cmd, ["--all", "deck"])
    assert r.exit_code == 1 and "name no site and no group" in r.output


# -- G12: the check logs in with a password still valid --------------------------------------------

def _dated(*rows):
    return [PlainEntry(label, word, until) for label, word, until in rows]


def test_an_expired_password_is_not_the_one_checked():
    past, future = date.today() - timedelta(days=3), date.today() + timedelta(days=3)
    entries = _dated(("OCT", "old", past), ("NOV", "new", future), ("ADMIN", "root", None))
    assert [e.label for e in pw.usable(entries)] == ["NOV", "ADMIN"]
    assert pw.first_password(entries) == "new"
    assert pw.first_password(_dated(("OCT", "old", past))) == "" and pw.first_password(None) == ""


class Seen:
    """Serves the release to the passwords that still open the site, 401 to the others."""

    name = "prod"

    def __init__(self, valid):
        self.valid, self.tried = valid, []

    def login(self, site, password):
        self.tried.append(password)
        return password

    def get(self, base_key, site, path, cookie=""):
        return (200, "r2\n") if cookie in self.valid else (401, "")


def test_the_check_after_the_switch_skips_an_expired_password(cfg):
    past = date.today() - timedelta(days=1)
    entries = _dated(("OCT", "old", past), ("NOV", "new", None))
    t = Seen({"new"})
    assert ops.check_levels(t, cfg.site("deck"), {}, entries, {}, "r2", {}) == []        # was: OCT sees HTTP 401
    assert t.tried == ["new"]
    t = Seen({"new"})
    assert ops.check_levels(t, cfg.site("deck"), {}, entries, {"OCT": "all", "NOV": "all"}, "r2", {}) == []
    assert t.tried == ["new"]


def test_every_password_expired_is_said_plainly(cfg):
    entries = _dated(("OCT", "old", date.today() - timedelta(days=1)))
    assert ops.check_levels(Seen(set()), cfg.site("deck"), {}, entries, {}, "r2", {}) == \
        ["every password of the html face has expired — nobody can log in"]


# -- G15: an editable streamtex ahead of its tag --------------------------------------------------

def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _editable(tmp_path, monkeypatch, cfg, version="1.2.3"):
    repo = tmp_path / "lib"
    (repo / "streamtex").mkdir(parents=True)
    (repo / "streamtex" / "a.py").write_text("x = 1\n")
    _git(repo, "init", "-q")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "start")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "release")
    info = {"version": version, "direct_url": {"url": f"file://{repo}", "dir_info": {"editable": True}}}
    import json
    monkeypatch.setattr(build, "_project_python", lambda c, code: json.dumps(info))
    return repo


def _commit(repo, path, text):
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text(text)
    _git(repo, "add", ".")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", f"change {path}")


def test_an_editable_library_at_its_tag_is_fine(tmp_path, monkeypatch, cfg):
    repo = _editable(tmp_path, monkeypatch, cfg)
    _git(repo, "tag", "v1.2.3")
    assert build.library_skew(cfg) == ""
    _commit(repo, "docs/notes.md", "outside the package")        # not code the image runs
    assert build.library_skew(cfg) == ""


def test_an_editable_library_ahead_of_its_tag_is_a_skew(tmp_path, monkeypatch, cfg):
    repo = _editable(tmp_path, monkeypatch, cfg)
    _git(repo, "tag", "v1.2.3")
    _commit(repo, "streamtex/a.py", "x = 2\n")
    assert "1 commit(s) ahead of v1.2.3" in build.library_skew(cfg)


def test_an_editable_library_without_its_tag_is_a_skew(tmp_path, monkeypatch, cfg):
    _editable(tmp_path, monkeypatch, cfg)
    assert "without the tag v1.2.3" in build.library_skew(cfg)


# -- G9: the domains shown before they are written -------------------------------------------------

class FakeCoolify:
    def __init__(self):
        self.calls = []
        self.apps = {"st1": {"fqdn": "https://deck.example.org/html,https://gone.example.org/html"},
                     "lv1": {"fqdn": ""}}

    def call(self, method, path, body=None):
        self.calls.append((method, path, body))
        return self.apps[path.split("/")[2]] if method == "GET" else {}


def test_domains_dry_run_writes_nothing(cfg, monkeypatch):
    fake = FakeCoolify()
    monkeypatch.setattr(coolify, "Coolify", lambda root, env: fake)
    monkeypatch.setattr(coolify, "domains_for", lambda c, t: {"static": "https://deck.example.org/html",
                                                               "live": "https://deck.example.org"})
    tcfg = {"coolify_env": "x", "static_uuid": "st1", "live_uuid": "lv1",
            "static_app": "demo-static", "live_app": "demo-live"}
    said = []
    coolify.apply_domains(cfg, tcfg, said.append, dry_run=True)
    assert all(m == "GET" for m, _, _ in fake.calls)
    assert said == ["  demo-static: 1 domain(s), 0 added, 1 removed", "    - https://gone.example.org/html",
                    "  demo-live: 1 domain(s), 1 added, 0 removed", "    + https://deck.example.org"]


def test_dry_run_goes_with_domains_and_never_deploys():
    r = CliRunner().invoke(setup_cmd, ["--dry-run"])
    assert r.exit_code == 1 and "goes with --domains" in r.output
    r = CliRunner().invoke(setup_cmd, ["--domains", "--dry-run", "--deploy"])
    assert r.exit_code == 1 and "cannot --deploy" in r.output


# -- #144: the project's check of an export --------------------------------------------------------

CHECKS = '''
def accept(site, html):
    print("noise on stdout")
    return None

def refuse(site, html):
    return f"{site}: 3 pages in {html.name}, 40 expected"

def boom(site, html):
    raise ValueError("no sequence")

def no(site, html):
    return False
'''


def _verifying(tmp_path, monkeypatch, spec):
    (tmp_path / "stx.toml").write_text(textwrap.dedent(STX_TOML.format(extra=f'verify = "{spec}"')))
    (tmp_path / "project_checks.py").write_text(CHECKS)
    monkeypatch.chdir(tmp_path)

    def run(c, code):          # the project's python, here this one
        r = subprocess.run([sys.executable, "-c", code], text=True, capture_output=True)
        if r.returncode:
            raise ReleaseError(f"the project's python: {r.stderr[-400:]}")
        return r.stdout.strip()

    monkeypatch.setattr(build, "_project_python", run)
    return load_config(tmp_path)


def test_verify_accepts(tmp_path, monkeypatch):
    cfg = _verifying(tmp_path, monkeypatch, "project_checks:accept")
    build.verify_export(cfg, cfg.site("deck"), tmp_path / "html")


@pytest.mark.parametrize("func, said", [
    ("refuse", "deck: 3 pages in html, 40 expected"),
    ("boom", "ValueError: no sequence"),
    ("no", "it returned False"),
])
def test_verify_refuses(tmp_path, monkeypatch, func, said):
    cfg = _verifying(tmp_path, monkeypatch, f"project_checks:{func}")
    with pytest.raises(ReleaseError, match="verify refused the export") as e:
        build.verify_export(cfg, cfg.site("deck"), tmp_path / "html")
    assert said in str(e.value) and "the site serves what it served" in str(e.value)


def test_verify_that_cannot_run_is_a_refusal(tmp_path, monkeypatch):
    cfg = _verifying(tmp_path, monkeypatch, "project_checks:missing")
    with pytest.raises(ReleaseError, match="could not run"):
        build.verify_export(cfg, cfg.site("deck"), tmp_path / "html")


def test_verify_must_name_a_function(tmp_path, monkeypatch):
    (tmp_path / "stx.toml").write_text(textwrap.dedent(STX_TOML.format(extra='verify = "checks.py"')))
    with pytest.raises(ReleaseError, match="expected 'module:function'"):
        load_config(tmp_path)


def test_a_refused_export_copies_nothing(tmp_path, monkeypatch):
    cfg = _verifying(tmp_path, monkeypatch, "project_checks:refuse")
    (tmp_path / "html").mkdir()
    monkeypatch.setattr(build, "snapshot", lambda c, s, w: tmp_path)
    monkeypatch.setattr(build, "export", lambda c, s, code, w, r, env: (tmp_path / "html", r))

    class Target:
        name = "prod"
        cmds: list = []

        def path(self, *parts):
            return "/".join(parts)

        def sh(self, cmd, check=True):
            self.cmds.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "", "")

        def rsync(self, *a):
            self.cmds.append("rsync")

    t, state = Target(), {"sites": {}}
    with pytest.raises(ReleaseError, match="verify refused"):
        ops.publish_site(t, cfg, state, cfg.site("deck"), "r2", {"live": None, "html": None}, lambda m: None)
    assert not any(c == "rsync" or c.startswith("switch") or "mkdir" in c for c in t.cmds)


# -- #143: stx release remove ---------------------------------------------------------------------

class LocalTarget:
    """Runs the shell commands in a temporary root; records what goes to the containers."""

    name = "prod"

    def __init__(self, root):
        self.root, self.dexecs = root, []

    def path(self, *parts):
        return str(self.root.joinpath(*parts))

    def sh(self, cmd, check=True):
        return subprocess.run(["sh", "-c", cmd], text=True, capture_output=True)

    def write(self, dest, content, mode=None):
        from pathlib import Path
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Path(dest).write_text(content)

    def dexec(self, app, cmd, check=True):
        self.dexecs.append((app, cmd))
        return subprocess.CompletedProcess(cmd, 0, "", "")


def _two_sites_on(tmp_path):
    root = tmp_path / "srv"
    for site in ("old", "deck"):
        (root / "static" / "sites" / site / "releases" / "r1").mkdir(parents=True)
        (root / "live" / "sites" / site / "releases" / "r1").mkdir(parents=True)
        (root / "live" / "conf" / "programs").mkdir(parents=True, exist_ok=True)
        (root / "live" / "conf" / "programs" / f"{site}.conf").write_text("[program]\n")
    (root / "live" / "media" / "demo").mkdir(parents=True)
    state = {"sites": {"prod": {"old": {"release": "r1", "port": 9001}, "deck": {"release": "r1", "port": 9002}}}}
    return LocalTarget(root), state


def test_remove_takes_one_site_off_and_nothing_else(cfg, tmp_path):
    t, state = _two_sites_on(tmp_path)
    plan = ops.remove_plan(t, state, "old")
    assert len(plan) == 5 and any("ports.map" in p for p in plan)
    ops.remove_site(t, cfg, state, "old", lambda m: None)
    root = t.root
    assert not (root / "static/sites/old").exists() and not (root / "live/sites/old").exists()
    assert not (root / "live/conf/programs/old.conf").exists()
    assert (root / "static/sites/deck/releases/r1").is_dir() and (root / "live/conf/programs/deck.conf").exists()
    assert (root / "live/media/demo").is_dir()
    assert (root / "live/conf/ports.map").read_text() == "deck 9002;\n"
    assert list(state["sites"]["prod"]) == ["deck"]
    assert ("live", "supervisorctl stop old") in t.dexecs and ("live", "supervisorctl update") in t.dexecs
    assert ops.remove_plan(t, state, "old") == []


def test_remove_refuses_a_bad_name(cfg, tmp_path):
    t, state = _two_sites_on(tmp_path)
    for bad in ("../static", "a b", ""):
        with pytest.raises(ReleaseError, match="not a site name"):
            ops.remove_plan(t, state, bad)
        with pytest.raises(ReleaseError, match="not a site name"):
            ops.remove_site(t, cfg, state, bad, lambda m: None)


def test_remove_refuses_a_declared_site(cfg, monkeypatch, tmp_path):
    from streamtex.cli import release_cmd
    t, state = _two_sites_on(tmp_path)
    monkeypatch.setattr(release_cmd, "_ctx", lambda target: (cfg, state, t))
    r = CliRunner().invoke(release_cmd.remove_cmd, ["deck"])
    assert r.exit_code == 1 and "still declared in stx.toml" in r.output
    r = CliRunner().invoke(release_cmd.remove_cmd, ["old"], input="n\n")
    assert r.exit_code == 1 and "nothing removed" in r.output and (t.root / "live/sites/old").is_dir()
    r = CliRunner().invoke(release_cmd.remove_cmd, ["old", "--yes"])
    assert r.exit_code == 0 and not (t.root / "live/sites/old").exists() and "--domains --dry-run" in r.output
