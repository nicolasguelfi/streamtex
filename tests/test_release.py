"""stx release (#136, #111): site list, passwords per site and their conversion, state import, Dockerfiles."""
import json
import subprocess
import textwrap
from datetime import date
from pathlib import Path

import pytest

from streamtex.release import ReleaseError
from streamtex.release import passwords as pw
from streamtex.release.config import load_config
from streamtex.release.coolify import compose_dockerfile, domains_for
from streamtex.release.ops import program_conf
from streamtex.release.state import import_prototype, load_state


def _project(tmp_path, release: str):
    (tmp_path / "stx.toml").write_text(textwrap.dedent(release))
    return tmp_path


SITES = """
    [release]
    project = "trainings"
    langs = ["en", "fr"]
    pythonpath = ["trainings_pack"]

    [[release.sites]]
    site = "chat1d-slides"
    book = "trainings/CHAT1D/slides/book.py"
    group = "CHAT1D"
    legacy = ["CHAT1D", "slides"]

    [[release.sites]]
    site = "chat1d-pack"
    book = "trainings/CHAT1D/pack/book.py"
    group = "CHAT1D"
    legacy = ["CHAT1D", "pack"]

    [[release.sites]]
    site = "chat1d"
    book = "trainings/CHAT1D/home/book.py"
    group = "CHAT1D"
    faces = ["html"]
    explicit = true
    legacy = ["CHAT1D", "home"]
"""


# -- the site list ------------------------------------------------------------------------

def test_sites_are_read_with_their_defaults(tmp_path):
    cfg = load_config(_project(tmp_path, SITES))
    s = cfg.site("chat1d-slides")
    assert s.faces == ("live", "html") and s.paths == ("trainings/CHAT1D/slides",)
    assert s.doc_dir == "trainings/CHAT1D/slides" and s.export_name == "slides"
    assert [x.site for x in cfg.select(())] == ["chat1d-slides", "chat1d-pack"]   # explicit ones wait
    assert [x.site for x in cfg.select(("chat1d",))] == ["chat1d"]
    assert [x.site for x in cfg.select((), ("CHAT1D",))] == ["chat1d-slides", "chat1d-pack"]


@pytest.mark.parametrize("extra,match", [
    ('[[release.sites]]\nsite = "chat1d-slides"\nbook = "x/book.py"\n', "used twice"),
    ('[[release.sites]]\nsite = "Bad_Name"\nbook = "x/book.py"\n', "DNS label"),
    ('[[release.sites]]\nsite = "ok"\nbook = "x/book.py"\nfaces = ["pdf"]\n', "faces"),
    ('[[release.sites]]\nsite = "ok"\nbook = "x/main"\n', "book.py"),
    ('[[release.sites]]\nsite = "ok"\nbook = "x/book.py"\nport = 1\n', "unknown key"),
])
def test_a_wrong_site_list_is_refused(tmp_path, extra, match):
    with pytest.raises(ReleaseError, match=match):
        load_config(_project(tmp_path, SITES + extra))


def test_sites_can_come_from_a_project_function(tmp_path):
    (tmp_path / "proj_sites.py").write_text(
        "def sites():\n    return [{'site': f'doc-{i}', 'book': f'd{i}/book.py'} for i in range(3)]\n")
    cfg = load_config(_project(tmp_path, '[release]\nproject = "p"\nsites_from = "proj_sites:sites"\n'))
    assert [s.site for s in cfg.sites] == ["doc-0", "doc-1", "doc-2"] and cfg.site("doc-1").group == "doc-1"


def test_live_program_runs_the_site_from_its_current_release(tmp_path):
    cfg = load_config(_project(tmp_path, SITES))
    conf = program_conf(cfg, cfg.site("chat1d-slides"), 9004)
    assert "directory=/srv/live/sites/chat1d-slides/current/trainings/CHAT1D/slides" in conf
    assert "--server.port=9004 --server.address=127.0.0.1" in conf
    assert 'PYTHONPATH="/srv/live/sites/chat1d-slides/current/trainings_pack"' in conf


# -- passwords per site --------------------------------------------------------------------

PASSWORDS = """
    [default]
    live = "TRAINER:t1"
    html = [["PROMO-OCT", "o1"], ["PROMO-NOV", "n1", "2026-11-30"]]

    [CHAT1D]
    html = "PROMO-DEC:decsecret:2026-12-31,GUEST:g1"

    [CHAT1D.sites.chat1d]
    open = ["html"]
"""


def test_three_levels_and_an_explicit_open(tmp_path):
    import tomllib
    cfg = load_config(_project(tmp_path, SITES))
    data = tomllib.loads(textwrap.dedent(PASSWORDS))
    slides = pw.for_site(data, cfg.site("chat1d-slides"))
    assert [(e.label, e.password) for e in slides["live"]] == [("TRAINER", "t1")]
    assert [(e.label, e.valid_until) for e in slides["html"]] == [("PROMO-DEC", date(2026, 12, 31)), ("GUEST", None)]
    assert pw.for_site(data, cfg.site("chat1d")) == {"html": None}          # html-only, open
    assert pw.pass_text(None) == "open\n"
    lines = pw.pass_text(slides["html"]).splitlines()
    assert lines[0].startswith("PROMO-DEC:scrypt$") and lines[0].endswith(":2026-12-31")
    assert "decsecret" not in pw.pass_text(slides["html"])                         # hashed, never the password


@pytest.mark.parametrize("text,match", [
    ('[default]\nlive = ""\nhtml = "x"\n', "empty string"),
    ('[default]\nhtml = "x"\n', "an omission never opens"),
    ('[default]\nlive = "x"\nhtml = "y"\nopen = ["live"]\n', "both open and given"),
    ('[default]\nlive = "A:same,B:same"\nhtml = "y"\n', "share a password"),
])
def test_password_mistakes_are_refused(tmp_path, text, match):
    import tomllib
    cfg = load_config(_project(tmp_path, SITES))
    with pytest.raises(ReleaseError, match=match):
        pw.for_site(tomllib.loads(text), cfg.site("chat1d-slides"))


# -- the prototype's password file → this grammar ------------------------------------------

OLD = """
    [default]
    live = "TRAINER:t1"
    html = [["PROMO-OCT", "o1"], ["PROMO-NOV", "n1", "2026-11-30"]]

    [CHAT1D]
    html = "PROMO-DEC:d1:2026-12-31,GUEST:g1"

    [CHAT1D.home]
    html = ""

    [CHAT1D.pack]
    live = { TEAM = "k1:2027-01-31" }
"""


def test_convert_keeps_every_password_and_proves_it(tmp_path):
    cfg = load_config(_project(tmp_path, SITES))
    old, new = tmp_path / "old.toml", tmp_path / "new.toml"
    old.write_text(textwrap.dedent(OLD))
    report = pw.convert(cfg, old, new)
    assert any(r.startswith("chat1d: html open") for r in report)
    import tomllib
    data = tomllib.loads(new.read_text())
    assert data["CHAT1D"]["sites"]["chat1d"] == {"open": ["html"]}
    assert data["CHAT1D"]["sites"]["chat1d-pack"]["live"] == {"TEAM": "k1:2027-01-31"}   # same form, untouched
    assert data["default"]["html"] == [["PROMO-OCT", "o1"], ["PROMO-NOV", "n1", "2026-11-30"]]
    pack = pw.for_site(data, cfg.site("chat1d-pack"))
    assert [(e.label, e.password, e.valid_until) for e in pack["live"]] == [("TEAM", "k1", date(2027, 1, 31))]
    assert oct(new.stat().st_mode & 0o777) == "0o600"


def test_convert_refuses_what_it_cannot_map_or_check(tmp_path):
    cfg = load_config(_project(tmp_path, SITES))
    old = tmp_path / "old.toml"
    old.write_text(textwrap.dedent(OLD) + '\n[CHAT1D.solutions]\nhtml = "s"\n')
    with pytest.raises(ReleaseError, match=r"no site for \[CHAT1D.solutions\]"):
        pw.convert(cfg, old, tmp_path / "new.toml")
    old.write_text('[default]\nlive = "A:x,B:x"\nhtml = "h"\n')
    with pytest.raises(ReleaseError, match="share a password"):
        pw.convert(cfg, old, tmp_path / "new.toml")
    assert not (tmp_path / "new.toml").exists()                                 # nothing written


# -- the prototype's state ------------------------------------------------------------------

def test_import_takes_the_prototype_state_over_without_touching_the_server(tmp_path):
    cfg = load_config(_project(tmp_path, SITES))
    old = tmp_path / "state.json"
    old.write_text(json.dumps({
        "default_target": "prod",
        "targets": {"prod": {"type": "ssh", "host": "root@h", "root": "/data/stx/trainings", "domain": "example.org"}},
        "sites": {"prod": {
            "chat1d-slides": {"training": "CHAT1D", "kind": "slides", "target": "prod", "port": 9003,
                              "html_open": False, "release": "abc", "previous": "def", "date": "d", "asleep": False},
            "gone-site": {"training": "X", "kind": "slides", "port": 9009, "release": "zzz"}}}}))
    new = import_prototype(cfg.root, old, set(cfg.by_name))
    assert new["_unknown"] == ["prod/gone-site"]
    state = load_state(cfg.root)
    assert state["sites"]["prod"]["chat1d-slides"] == {"port": 9003, "release": "abc", "previous": "def",
                                                       "date": "d", "asleep": False, "html_open": False}
    assert state["targets"]["prod"]["root"] == "/data/stx/trainings"
    with pytest.raises(ReleaseError, match="already exists"):
        import_prototype(cfg.root, old, set(cfg.by_name))


# -- Coolify ------------------------------------------------------------------------------------

def test_dockerfiles_are_self_contained(tmp_path):
    cfg = load_config(_project(tmp_path, SITES))
    with pytest.raises(ReleaseError, match="stx release lock"):
        compose_dockerfile(cfg, "live")
    (cfg.lock_dir).mkdir()
    (cfg.lock_dir / "stx-version").write_text("0.7.57\n")
    (cfg.lock_dir / "requirements.txt").write_text("rich==13.0\n")
    live = compose_dockerfile(cfg, "live")
    assert "COPY <<'STX_HEREDOC_EOF' ./stx-version\n0.7.57\nSTX_HEREDOC_EOF" in live
    assert "COPY <<'STX_HEREDOC_EOF' /opt/stx/stx_auth_lib.py" in live and "AUTH_INTERFACE" in live
    static = compose_dockerfile(cfg, "static")
    assert "COPY --chmod=755 <<'STX_HEREDOC_EOF' /docker-entrypoint.d/10-stx-init.sh" in static
    assert "\nCOPY nginx.conf" not in static                                    # every local COPY is inlined


def test_domains_follow_the_faces(tmp_path):
    cfg = load_config(_project(tmp_path, SITES))
    d = domains_for(cfg, {"domain": "example.org"})
    assert d["live"] == "https://chat1d-slides.example.org,https://chat1d-pack.example.org"
    assert d["static"] == ("https://chat1d-slides.example.org/html,https://chat1d-pack.example.org/html,"
                           "https://chat1d.example.org")


def test_templates_ship_with_the_package():
    from streamtex.release.ops import TEMPLATES
    for f in ("static/Dockerfile", "static/stx-http.conf", "live/Dockerfile", "live/supervisord.conf"):
        assert (TEMPLATES / f).is_file()


# -- 0.7.59: one export, system packages, git packs, provisional names ------------------------

def test_one_export_without_language_folder_and_system_packages(tmp_path):
    cfg = load_config(_project(tmp_path, SITES.replace('langs = ["en", "fr"]', 'langs = []\n    apt = ["texlive-latex-base", "texlive-pictures"]\n    lock_no_sources = true')))
    assert cfg.langs == () and cfg.apt == ("texlive-latex-base", "texlive-pictures") and cfg.lock_no_sources
    (cfg.lock_dir).mkdir()
    (cfg.lock_dir / "stx-version").write_text("0.7.59\n")
    (cfg.lock_dir / "requirements.txt").write_text("")
    live = compose_dockerfile(cfg, "live")
    assert ("RUN apt-get update && apt-get install -y --no-install-recommends texlive-latex-base texlive-pictures"
            in live) and "STX_RELEASE_APT" not in live
    with pytest.raises(ReleaseError, match="package name"):
        load_config(_project(tmp_path, SITES.replace('langs = ["en", "fr"]', 'apt = ["bad name"]')))


def test_lock_without_sources_drops_frozen(tmp_path, monkeypatch):
    from streamtex.release import build
    cfg = load_config(_project(tmp_path, SITES.replace('langs = ["en", "fr"]', "lock_no_sources = true")))
    seen = {}

    class R:
        returncode, stdout, stderr = 0, "rich==13\n", ""

    def fake_run(argv, **kw):
        seen.setdefault("argv", argv)
        return R()

    monkeypatch.setattr(build.subprocess, "run", fake_run)
    monkeypatch.setattr(build, "installed_version", lambda cfg: "0.7.59")
    build.lock_files(cfg)
    assert "--no-sources" in seen["argv"] and "--frozen" not in seen["argv"]


def test_provisional_suffix_in_nginx_domains_and_urls(tmp_path):
    from streamtex.release.ops import http_conf
    from streamtex.release.target import Target
    plain = http_conf("static")
    assert "~^(?<label>[a-z0-9-]+)\\.  $label;" in plain
    nxt = http_conf("live", "-next")
    assert "~^(?<label>[a-z0-9-]+?)\\-next\\.  $label;" in nxt
    with pytest.raises(ReleaseError, match="site_suffix"):
        http_conf("static", "next")
    cfg = load_config(_project(tmp_path, SITES))
    d = domains_for(cfg, {"domain": "example.org", "site_suffix": "-next"})
    assert d["live"].startswith("https://chat1d-slides-next.example.org,")
    t = Target("p", {"type": "ssh", "host": "h", "root": "/r", "domain": "example.org", "site_suffix": "-next"})
    assert t.url_of("live_url", "chat1d-slides", "/x") == ("https://chat1d-slides-next.example.org/x", None)


# -- 0.7.60: behind a CDN, and a clean tree after a publication --------------------------------

def test_visitor_checks_send_a_user_agent(monkeypatch):
    from streamtex.release.target import Target
    seen = {}

    class Resp:
        status = 200
        def read(self):
            return b"rel\n"
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    def fake_open(req, timeout=0):
        seen["ua"] = req.get_header("User-agent")
        return Resp()

    monkeypatch.setattr("urllib.request.urlopen", fake_open)
    t = Target("p", {"type": "ssh", "host": "h", "root": "/r", "domain": "example.org"})
    assert t.get("static_url", "s", "/html/version.txt") == (200, "rel\n")
    assert seen["ua"].startswith("stx-release/")


def test_uv_lock_is_put_back(tmp_path):
    from streamtex.release.build import keep_lock
    lock = tmp_path / "uv.lock"
    lock.write_text("original\n")
    with keep_lock(tmp_path):
        lock.write_text("rewritten by uv\n")
    assert lock.read_text() == "original\n"
    with keep_lock(tmp_path / "nowhere"):
        pass                                                   # no lock: nothing to do


# -- 0.7.61: the live image built from a public repository ---------------------------------------

class FakeCoolify:
    """Coolify's API as the release code uses it: applications by uuid, deployments that finish."""

    def __init__(self, apps):
        self.apps = {a["uuid"]: dict(a) for a in apps}
        self.calls = []

    def call(self, method, path, body=None):
        self.calls.append((method, path, body))
        if path == "/projects":
            return [{"name": "docs", "uuid": "p1"}]
        if path == "/servers":
            return [{"name": "localhost", "uuid": "s1"}]
        if path == "/applications" and method == "GET":
            return list(self.apps.values())
        if path == "/applications/public":
            self.apps["new1"] = {"uuid": "new1", "name": body["name"], "git_repository": body["git_repository"]}
            return {"uuid": "new1"}
        if path.startswith("/applications/") and method == "GET":
            return self.apps[path.split("/")[2]]
        if path.startswith("/applications/") and method == "PATCH":
            self.apps[path.split("/")[2]].update(body)
            return {}
        if path.startswith("/deployments/"):
            return {"status": "finished"}
        if path.startswith("/deploy?"):
            return {"deployments": [{"deployment_uuid": "d1"}]}
        if path.endswith("/restart"):
            return {"deployment_uuid": "d2"}
        return {}


def _repo_target():
    return {"coolify_env": "x.env", "coolify_project": "docs", "root": "/data/stx/docs", "domain": "example.org",
            "static_app": "docs-static", "live_app": "docs-live", "static_uuid": "st1", "live_uuid": "old1",
            "repo": "owner/docs"}


def _locked(tmp_path):
    cfg = load_config(_project(tmp_path, SITES))
    cfg.lock_dir.mkdir()
    (cfg.lock_dir / "stx-version").write_text("0.7.61\n")
    (cfg.lock_dir / "requirements.txt").write_text("rich==13.0\n")
    return cfg


def test_repo_faces_and_their_dockerfile(tmp_path):
    from streamtex.release import coolify
    cfg = _locked(tmp_path)
    assert coolify.repo_faces({}) == () and coolify.repo_faces(_repo_target()) == ("live",)
    with pytest.raises(ReleaseError, match="repo_faces"):
        coolify.repo_faces({"repo": "o/r", "repo_faces": ["web"]})
    [path] = coolify.write_dockerfiles(cfg, ("live",))
    assert path == cfg.lock_dir / "Dockerfile.live" and path.read_text() == compose_dockerfile(cfg, "live")
    assert coolify.repo_url("owner/docs") == "https://github.com/owner/docs"


def test_a_missing_live_app_is_created_from_the_repository(tmp_path, monkeypatch):
    from streamtex.release import coolify
    cfg = _locked(tmp_path)
    fake = FakeCoolify([{"uuid": "st1", "name": "docs-static", "dockerfile": "FROM nginx"}])
    monkeypatch.setattr(coolify, "Coolify", lambda root, env: fake)
    uuids = coolify.setup(cfg, _repo_target(), lambda m: None)
    assert uuids == {"static_uuid": "st1", "live_uuid": "new1"}
    [body] = [b for m, p, b in fake.calls if p == "/applications/public"]
    assert body["git_repository"] == "https://github.com/owner/docs" and body["build_pack"] == "dockerfile"
    assert body["dockerfile_location"] == "/.stx-release/Dockerfile.live" and body["is_auto_deploy_enabled"] is False


def test_migration_moves_the_domains_in_two_runs(tmp_path, monkeypatch):
    from streamtex.release import coolify
    cfg = _locked(tmp_path)
    fake = FakeCoolify([{"uuid": "old1", "name": "docs-live", "dockerfile": "FROM python"}])
    monkeypatch.setattr(coolify, "Coolify", lambda root, env: fake)
    monkeypatch.setattr(coolify, "require_pushed_dockerfile", lambda *a: None)
    t, said = _repo_target(), []
    assert coolify.migrate(cfg, t, "live", lambda u: True, said.append) is False
    assert t["live_uuid"] == "new1" and t["live_uuid_inline"] == "old1"
    assert fake.apps["old1"]["name"] == "docs-live-inline" and any("Directory Mount" in m for m in said)
    with pytest.raises(ReleaseError, match="not mounted"):
        coolify.migrate(cfg, t, "live", lambda u: False, said.append)
    assert fake.apps["old1"].get("domains") is None                         # nothing moved without the volume
    assert coolify.migrate(cfg, t, "live", lambda u: True, said.append) is True
    assert fake.apps["old1"]["domains"] == "" and fake.apps["new1"]["domains"].startswith("https://chat1d-slides.")
    order = [p for m, p, b in fake.calls if p in ("/applications/old1", "/applications/new1") and m == "PATCH"]
    assert order[-2:] == ["/applications/old1", "/applications/new1"]       # freed before it is taken
    assert ("POST", "/applications/old1/stop", None) in fake.calls and "live_uuid_inline" not in t
    assert coolify.migrate(cfg, t, "live", lambda u: True, said.append) is True   # nothing left to do


def test_rebuild_refuses_a_pasted_dockerfile(tmp_path, monkeypatch):
    from streamtex.release import coolify
    cfg = _locked(tmp_path)
    with pytest.raises(ReleaseError, match="paste"):
        coolify.rebuild(cfg, {**_repo_target(), "repo": ""}, "live", print)
    fake = FakeCoolify([{"uuid": "old1", "name": "docs-live", "dockerfile": "FROM python"}])
    monkeypatch.setattr(coolify, "Coolify", lambda root, env: fake)
    monkeypatch.setattr(coolify, "require_pushed_dockerfile", lambda *a: None)
    with pytest.raises(ReleaseError, match="--migrate live"):
        coolify.rebuild(cfg, _repo_target(), "live", print)


def test_rebuild_needs_the_dockerfile_pushed(tmp_path):
    import subprocess

    from streamtex.release import coolify
    remote, work = tmp_path / "remote.git", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    work.mkdir()
    cfg = _locked(work)

    def g(*a):
        subprocess.run(["git", "-C", str(work), *a], check=True, capture_output=True)

    g("init", "-q", "-b", "main")
    g("remote", "add", "origin", str(remote))
    g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start")
    g("push", "-q", "origin", "main")
    with pytest.raises(ReleaseError, match="stx release lock"):
        coolify.require_pushed_dockerfile(cfg, _repo_target(), "live")
    coolify.write_dockerfiles(cfg, ("live",))
    with pytest.raises(ReleaseError, match="push it"):
        coolify.require_pushed_dockerfile(cfg, _repo_target(), "live")
    g("add", ".")
    g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "lock")
    g("push", "-q", "origin", "main")
    coolify.require_pushed_dockerfile(cfg, _repo_target(), "live")


SESSIONS = """
    [default]
    live = "TRAINER:t1"
    html = "PROMO-OCT:o1"

    [CHAT1D.home]
    html = ""

    [CHAT1D.slides]
    html = [
      { seance = "ADMIN", mot = "root", limite = "all" },
      { seance = "S1027", mot = "a1", limite = 304, fin = "2026-12-31" },
      { seance = "S1103", mot = "b2" },
    ]
"""


def test_convert_keeps_the_session_lines_and_their_levels(tmp_path):
    """#148: the all-trainings file, one line per session (acces3/f1), converted as it is."""
    import tomllib
    cfg = load_config(_project(tmp_path, SITES))
    old, new = tmp_path / "old.toml", tmp_path / "new.toml"
    old.write_text(textwrap.dedent(SESSIONS))
    report = pw.convert(cfg, old, new)
    assert any("chat1d-slides" in r and "S1027 304" in r and "S1103 None" in r for r in report)
    text = new.read_text()
    assert '  { seance = "S1027", mot = "a1", limite = 304, fin = "2026-12-31" },\n' in text   # one per line
    data = tomllib.loads(text)
    levels = pw.levels_for(data, cfg.site("chat1d-slides"))
    assert levels == {"ADMIN": "all", "S1027": 304, "S1103": None}
    assert pw.write_limit(new, cfg.site("chat1d-slides"), ["S1103"], 50) == ["S1103: not open yet → 50"]


def test_ssh_shares_one_connection():
    """The server resets new SSH connections beyond about 18 in a burst: one shared connection."""
    from streamtex.release.target import Target
    argv = Target("prod", {"type": "ssh", "root": "/srv", "host": "me@example.org"}).ssh_argv()
    assert "ControlMaster=auto" in argv and any(a.startswith("ControlPath=") for a in argv)
    assert argv[-1] == "me@example.org"


def test_local_openrsync_drops_hard_links_with_link_dest(monkeypatch):
    """macOS's rsync stops on -H with --link-dest (all-trainings, 2026-10-26): -H goes, --link-dest stays."""
    from streamtex.release import target
    seen = []
    monkeypatch.setattr(target, "_openrsync", lambda: True)
    monkeypatch.setattr(target.subprocess, "run",
                        lambda argv, **kw: seen.append(argv) or subprocess.CompletedProcess(argv, 0, "", ""))
    t = target.Target("local", {"type": "local", "root": "/tmp/x"})
    t.rsync("a/", "b/", "--delete", "-H", "-c", "--link-dest", "prev")
    t.rsync("a/", "c/", "--delete", "-H")
    assert seen[0] == ["rsync", "-a", "--delete", "-c", "--link-dest", "prev", "a/", "b/"]
    assert "-H" in seen[1]
    monkeypatch.setattr(target, "_openrsync", lambda: False)
    t.rsync("a/", "d/", "-H", "--link-dest", "prev")
    assert "-H" in seen[2]


def test_passwords_file_from_the_environment(monkeypatch, tmp_path):
    """STX_PASSWORDS_FILE names another file (a rehearsal with dummy passwords); unset: the usual one."""
    monkeypatch.delenv(pw.PASSWORDS_ENV, raising=False)
    assert pw.passwords_path(tmp_path) == tmp_path / ".stx-passwords.toml"
    monkeypatch.setenv(pw.PASSWORDS_ENV, "rehearsal.toml")
    assert pw.passwords_path(tmp_path) == tmp_path / "rehearsal.toml"
    monkeypatch.setenv(pw.PASSWORDS_ENV, str(tmp_path / "abs.toml"))
    assert pw.passwords_path(Path("/elsewhere")) == tmp_path / "abs.toml"
    with pytest.raises(ReleaseError, match="abs.toml not found at"):
        pw.load_file(pw.passwords_path(tmp_path))


# -- #149: an application built from a Dockerfile kept in Coolify, rebuilt without a paste -------------

class CoolifyDb:
    """The server as rebuild_pasted uses it over ssh: Coolify's database (psql), files under the root."""

    kind, name = "ssh", "prod"

    def __init__(self, dockerfile, broken=False, garble=False):
        self.cfg = {**_repo_target(), "repo": "", "live_uuid": "old1"}
        self.db = {"old1": dockerfile}
        self.files, self.cmds = {}, []
        self.broken, self.garble = broken, garble

    def path(self, *parts):
        return "/".join(["/data/stx/docs", *parts])

    def sh(self, cmd, check=True, input=None):
        import base64
        import re
        self.cmds.append(cmd)
        out = ""
        if cmd.startswith("docker exec -i coolify-db psql"):
            if self.broken:
                return subprocess.CompletedProcess(cmd, 1, "", 'ERROR:  column "dockerfile" does not exist')
            uuid = re.search(r"uuid = '([^']+)'", input).group(1)
            m = re.search(r"dockerfile = \$stx_dockerfile\$(.*)\$stx_dockerfile\$, updated_at", input, re.S)
            if m and uuid in self.db:
                self.db[uuid] = m.group(1) + ("garbled" if self.garble else "")
                out = f"{len(self.db[uuid])}\n"
            elif not m and uuid in self.db:
                b64 = base64.b64encode(self.db[uuid].encode()).decode()
                out = "stx:" + "\n".join(b64[i:i + 76] for i in range(0, len(b64), 76)) + "\n"
        elif cmd.startswith("ls -1"):
            out = "\n".join(sorted(p.rsplit("/", 1)[1] for p in self.files)) + "\n"
        elif cmd.startswith("cat "):
            out = self.files[cmd.split(" ", 1)[1].strip("'")]
        return subprocess.CompletedProcess(cmd, 0, out, "")

    def write(self, dest, content, mode=None):
        self.files[dest] = content


@pytest.fixture
def pasted(tmp_path, monkeypatch):
    from streamtex.release import coolify
    cfg = _locked(tmp_path)
    fake = FakeCoolify([{"uuid": "old1", "name": "docs-live", "dockerfile": "FROM python"}])
    monkeypatch.setattr(coolify, "Coolify", lambda root, env: fake)
    return cfg, fake


def test_rebuild_writes_today_s_dockerfile_in_coolify(pasted):
    from streamtex.release import coolify
    cfg, fake = pasted
    t, said = CoolifyDb("FROM python:3.11\n# old\n"), []
    assert coolify.rebuild_pasted(cfg, t, "live", said.append) is True
    today = coolify.compose_dockerfile(cfg, "live")
    assert t.db["old1"] == today                                               # written unchanged
    [(backup, old)] = t.files.items()
    assert backup.startswith("/data/stx/docs/dockerfiles/Dockerfile.live.") and old == "FROM python:3.11\n# old\n"
    assert ("GET", "/deploy?uuid=old1", None) in fake.calls                     # then rebuilt
    assert any(m.startswith("  difference: ") for m in said) and any("read back" in m for m in said)


def test_rebuild_dry_run_writes_nothing(pasted):
    from streamtex.release import coolify
    cfg, fake = pasted
    t, said = CoolifyDb("FROM python\n"), []
    assert coolify.rebuild_pasted(cfg, t, "live", said.append, dry_run=True) is False
    assert t.db["old1"] == "FROM python\n" and not t.files
    assert not any(p.startswith("/deploy") for _, p, _ in fake.calls)
    assert "  dry run: nothing written, nothing rebuilt" in said


def test_rebuild_restore_puts_back_the_last_one_kept(pasted):
    from streamtex.release import coolify
    cfg, _fake = pasted
    t = CoolifyDb("FROM python:3.11\n# before\n")
    coolify.rebuild_pasted(cfg, t, "live", lambda m: None)
    assert t.db["old1"] != "FROM python:3.11\n# before\n"
    coolify.rebuild_pasted(cfg, t, "live", lambda m: None, restore=True)
    assert t.db["old1"] == "FROM python:3.11\n# before\n"
    assert len(t.files) == 2                                                   # today's kept in turn


def test_rebuild_stops_when_the_database_is_not_as_expected(pasted):
    from streamtex.release import coolify
    cfg, fake = pasted
    with pytest.raises(ReleaseError, match="paste `stx release setup --show <face>`"):
        coolify.rebuild_pasted(cfg, CoolifyDb("FROM python\n", broken=True), "live", print)
    t = CoolifyDb("FROM python\n", garble=True)
    with pytest.raises(ReleaseError, match="read back from Coolify .* is not the one written"):
        coolify.rebuild_pasted(cfg, t, "live", print)
    assert not any(p.startswith("/deploy") for _, p, _ in fake.calls)          # never rebuilt
    with pytest.raises(ReleaseError, match="holds"):
        coolify.write_pasted(CoolifyDb(""), "old1", "x $stx_dockerfile$ y")
    with pytest.raises(ReleaseError, match="restore|no Dockerfile kept"):
        coolify.rebuild_pasted(cfg, CoolifyDb("FROM python\n"), "live", print, restore=True)


def test_rebuild_pasted_refuses_a_repository_application(pasted):
    from streamtex.release import coolify
    cfg, fake = pasted
    fake.apps["old1"]["dockerfile"] = ""
    with pytest.raises(ReleaseError, match="built from a repository"):
        coolify.rebuild_pasted(cfg, CoolifyDb("FROM python\n"), "live", print)


def test_rebuild_options_are_for_a_dockerfile_kept_in_coolify(tmp_path, monkeypatch):
    from click.testing import CliRunner

    from streamtex.cli.release_cmd import rebuild_cmd
    from streamtex.release.state import save_state
    cfg = _locked(tmp_path)
    save_state(cfg.root, {"default_target": "prod", "targets": {"prod": {"type": "ssh", "host": "h",
                                                                           **_repo_target()}}, "sites": {}})
    monkeypatch.chdir(cfg.root)
    r = CliRunner().invoke(rebuild_cmd, ["--dry-run"])
    assert r.exit_code == 1 and "built from the repository" in r.output
