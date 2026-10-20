"""stx release (#136, #111): site list, passwords per site and their conversion, state import, Dockerfiles."""
import json
import textwrap
from datetime import date

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
