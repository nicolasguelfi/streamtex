"""stx release limit (#146, #147): the slide limit kept per site, the HTML face alone, its rollback;
the whole release stays `current`, the limited one is `limited`."""
import json
import subprocess
import textwrap

import pytest
from click.testing import CliRunner

from streamtex.release import ReleaseError, build, ops
from streamtex.release.config import load_config
from streamtex.release.state import SITE_KEYS, import_prototype

STX_TOML = """
    [release]
    project = "demo"
    [[release.sites]]
    site = "deck"
    book = "docs/deck/book.py"
    [[release.sites]]
    site = "live-only"
    book = "docs/live/book.py"
    faces = ["live"]
"""


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    (tmp_path / "stx.toml").write_text(textwrap.dedent(STX_TOML))
    monkeypatch.chdir(tmp_path)
    return load_config(tmp_path)


class FakeTarget:
    """Records the link switches; every folder exists."""
    name = "prod"

    def __init__(self):
        self.links: dict[str, str] = {}
        self.reloads: list[tuple[str, str]] = []

    def path(self, *parts):
        return "/".join(parts)

    def switch_cmd(self, base, release, link="current"):
        return f"switch {base} {release} {link}"

    def sh(self, cmd, check=True):
        if cmd.startswith("switch "):
            _, base, release, link = cmd.split()
            self.links[f"{base}/{link}"] = release
        elif cmd.startswith("rm -f ") and cmd.endswith("/limited"):
            self.links.pop(cmd[6:], None)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def dexec(self, app, cmd, check=True):
        self.reloads.append((app, cmd))
        return subprocess.CompletedProcess(cmd, 0, "", "")


def _state(**site):
    return {"targets": {}, "sites": {"prod": {"deck": {"release": "r2", "previous": "r1", **site}}}}


def test_html_of():
    assert ops.html_of({"release": "r1"}) == "r1"
    assert ops.html_of({"release": "r1", "html_release": "r1-s12"}) == "r1-s12"


def test_rollback_of_a_limit_moves_the_html_face_alone(cfg):
    t, state = FakeTarget(), _state(html_release="r2-s12", html_previous="r2", up_to_slide=10,
                                    up_to_slide_previous=None, last="limit")
    message = ops.rollback(t, cfg, state, cfg.site("deck"))
    assert "participants see r2 again (all slides)" in message and "live face is unchanged" in message
    assert t.links == {}                                          # `limited` removed, `current` untouched
    assert all(app == "static" for app, _ in t.reloads)          # no supervisorctl, no live reload
    v = state["sites"]["prod"]["deck"]
    assert (v["html_release"], v["html_previous"], v["up_to_slide"], v["up_to_slide_previous"]) == \
        ("r2", "r2-s12", None, 10)
    ops.rollback(t, cfg, state, cfg.site("deck"))                 # and back again
    assert t.links == {"static/sites/deck/limited": "r2-s12"} and v["up_to_slide"] == 10


def test_rollback_of_a_publication_moves_both_faces_with_their_html(cfg):
    t, state = FakeTarget(), _state(html_release="r2-s12", html_previous="r1-s12", up_to_slide=10,
                                    up_to_slide_previous=10, last="publish")
    assert "both faces are back on r1 (HTML r1-s12)" in ops.rollback(t, cfg, state, cfg.site("deck"))
    assert t.links == {"static/sites/deck/current": "r1", "static/sites/deck/limited": "r1-s12",
                       "live/sites/deck/current": "r1"}


def test_rollback_of_a_site_without_limit_is_unchanged(cfg):
    t, state = FakeTarget(), _state()
    assert ops.rollback(t, cfg, state, cfg.site("deck")) == "both faces are back on r1"
    assert t.links == {"static/sites/deck/current": "r1", "live/sites/deck/current": "r1"}
    assert "html_release" not in state["sites"]["prod"]["deck"]


def test_a_limit_needs_an_html_face_and_a_publication(cfg):
    t = FakeTarget()
    with pytest.raises(ReleaseError, match="no HTML face"):
        ops.limit_site(t, cfg, _state(), cfg.site("live-only"), 3, "", print)
    with pytest.raises(ReleaseError, match="not published on prod — publish it first"):
        ops.limit_site(t, cfg, {"sites": {}}, cfg.site("deck"), 3, "", print)


@pytest.mark.parametrize("value", ["0", "-2", "twelve", "3.5"])
def test_the_command_refuses_what_is_not_a_slide(value):
    from streamtex.cli.release_cmd import limit_cmd
    r = CliRunner().invoke(limit_cmd, ["deck", "--", value])
    assert r.exit_code == 1 and "a slide number (1 or more) or `all`" in r.output


def test_the_export_names_the_html_release_after_the_last_slide(cfg, tmp_path, monkeypatch):
    code, work = tmp_path / "code", tmp_path / "work"
    (code / "docs" / "deck").mkdir(parents=True)
    seen = []

    class R:
        returncode, stdout, stderr = 0, "", ""

    def fake_run(argv, **kw):
        seen.append(argv)
        out = build.Path(argv[argv.index("--output") + 1])
        (out / "deck").mkdir(parents=True, exist_ok=True)
        (out / "deck" / "deck.html").write_text("word " * 200)
        (out / build.LIMIT_FILE).write_text(json.dumps({"last_slide": 14}))
        return R()

    monkeypatch.setattr(build.subprocess, "run", fake_run)
    html, name = build.export(cfg, cfg.site("deck"), code, work, "r2", None, 12)
    assert name == "r2-s14"
    assert seen[0][-3:] == ["--up-to-slide", "12", "."]
    assert (html / "version.txt").read_text().startswith("r2-s14\n")
    assert not (html / build.LIMIT_FILE).exists()                 # never published


def test_the_state_import_keeps_the_limit(tmp_path):
    for key in ("html_release", "html_previous", "up_to_slide", "up_to_slide_previous", "last"):
        assert key in SITE_KEYS
    src = tmp_path / "state.json"
    src.write_text(json.dumps({"sites": {"prod": {"deck": {"release": "r1", "up_to_slide": 30,
                                                            "html_release": "r1-s31"}}}}))
    new = import_prototype(tmp_path, src, {"deck"})
    assert new["sites"]["prod"]["deck"] == {"release": "r1", "up_to_slide": 30, "html_release": "r1-s31"}


# -- #147: who sees the whole content ----------------------------------------------------------

class Seen(FakeTarget):
    """Serves, to each password, the release its view opens."""

    def __init__(self, full, release, limited):
        super().__init__()
        self.views = {"full": release, "limited": limited}
        self.full_words = full

    def login(self, site, password):
        return password

    def get(self, base_key, site, path, cookie=""):
        view = "full" if cookie in self.full_words else "limited"
        return 200, self.views[view] + "\n"


def _entries(*pairs):
    from streamtex.cli.deploy_auth_cmd import PlainEntry
    return [PlainEntry(label, word, None) for label, word in pairs]


def test_the_check_reads_each_view(cfg):
    entries, full = _entries(("PB", "pb"), ("ADMIN", "root")), frozenset({"ADMIN"})
    v = {"release": "r2"}
    good = Seen({"root"}, "r2", "r2-s12")
    assert ops.check_html(good, cfg.site("deck"), v, entries, full, "r2", "r2-s12") == []
    wrong = Seen({"root", "pb"}, "r2", "r2-s12")                 # the participant would see everything
    assert ops.check_html(wrong, cfg.site("deck"), v, entries, full, "r2", "r2-s12") == \
        ["limited sees r2, not r2-s12"]


def test_without_a_limit_one_password_is_enough(cfg):
    t = Seen({"pb"}, "r2", "never")
    assert ops.check_html(t, cfg.site("deck"), {}, _entries(("PB", "pb")), frozenset(), "r2", "r2") == []


def test_the_passwords_write_the_full_labels(cfg):
    t, written = FakeTarget(), {}
    t.write = lambda dest, content, mode=None: written.__setitem__(dest, content)
    state = _state(port=8601)
    faces = {"html": _entries(("PA", "pa"), ("PB", "pb"), ("ADMIN", "root")), "live": _entries(("ADMIN", "root"))}
    ops.apply_passwords(t, cfg, state, cfg.site("deck"), faces, frozenset({"ADMIN", "PA"}))
    assert written["static/sites/deck/full"] == "PA\nADMIN\n"
    html_admin = next(ln for ln in written["static/sites/deck/pass"].splitlines() if ln.startswith("ADMIN:"))
    live_admin = next(ln for ln in written["live/sites/deck/pass"].splitlines() if ln.startswith("ADMIN:"))
    assert html_admin == live_admin                               # one record: one login opens both


def test_a_limit_needs_the_whole_release_on_the_server(cfg):
    class Missing(FakeTarget):
        def sh(self, cmd, check=True):
            if cmd.startswith("test -d"):
                return subprocess.CompletedProcess(cmd, 1, "", "")
            return super().sh(cmd, check)

    with pytest.raises(ReleaseError, match="publish the site again first"):
        ops.limit_site(Missing(), cfg, _state(), cfg.site("deck"), 3, None, print)


def test_limit_all_removes_the_limited_link_without_exporting(cfg, monkeypatch):
    monkeypatch.setattr(build, "export", lambda *a, **k: pytest.fail("no export for `all`"))
    t = Seen(set(), "r2", "r2")
    state = _state(html_release="r2-s12", html_previous="r2", up_to_slide=10, html_open=True)
    ops.limit_site(t, cfg, state, cfg.site("deck"), None, None, print)
    v = state["sites"]["prod"]["deck"]
    assert (v["html_release"], v["up_to_slide"], v["last"]) == ("r2", None, "limit")
    assert "static/sites/deck/limited" not in t.links
