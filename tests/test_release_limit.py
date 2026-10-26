"""stx release limit (#146, #148): each session's level on the HTML face, the levels file, the line of
.stx-passwords.toml written by `limit --label`, rollback."""
import json
import subprocess
import textwrap
import tomllib

import pytest
from click.testing import CliRunner

from streamtex.cli.deploy_auth_cmd import PlainEntry
from streamtex.release import ReleaseError, build, ops
from streamtex.release import levels as lv
from streamtex.release import passwords as pw
from streamtex.release.config import load_config
from streamtex.release.state import SITE_KEYS, import_prototype

STX_TOML = """
    [release]
    project = "demo"
    [[release.sites]]
    site = "deck"
    book = "docs/deck/book.py"
    group = "GAI"
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
    """Records the link switches, the files written and the commands; every folder exists."""
    name = "prod"

    def __init__(self):
        self.links: dict[str, str] = {}
        self.reloads: list[tuple[str, str]] = []
        self.files: dict[str, str] = {}
        self.cmds: list[str] = []

    def path(self, *parts):
        return "/".join(parts)

    def switch_cmd(self, base, release, link="current"):
        return f"switch {base} {release} {link}"

    def write(self, dest, content, mode=None):
        self.files[dest] = content

    def sh(self, cmd, check=True):
        self.cmds.append(cmd)
        if cmd.startswith("switch "):
            _, base, release, link = cmd.split()
            self.links[f"{base}/{link}"] = release
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def dexec(self, app, cmd, check=True):
        self.reloads.append((app, cmd))
        return subprocess.CompletedProcess(cmd, 0, "", "")


class Seen(FakeTarget):
    """Serves to each password the folder its level opens (*views*: password → release or "closed")."""

    def __init__(self, views):
        super().__init__()
        self.views = views

    def login(self, site, password):
        return password

    def get(self, base_key, site, path, cookie=""):
        got = self.views.get(cookie, "closed")
        return (200, "<meta name=\"stx-closed\">") if got == "closed" else (200, got + "\n")


def _state(**site):
    return {"targets": {}, "sites": {"prod": {"deck": {"release": "r2", "previous": "r1", **site}}}}


def _entries(*pairs):
    return [PlainEntry(label, word, None) for label, word in pairs]


# -- levels.py ---------------------------------------------------------------------------------

def test_the_levels_file():
    levels = {"S1": 120, "S2": None, "ADMIN": "all", "OLD": pw.DEFAULT, "S3": ((100, 50), (200, "all"))}
    names = {120: "r2-s121", 50: "r2-s52", 30: "r2-s30"}
    assert lv.cuts(levels, 30) == {120, 50, 30}
    assert lv.cuts(levels, None) == {120, 50}
    assert lv.text(levels, 30, names) == ("ADMIN\tcurrent\nOLD\treleases/r2-s30\nS1\treleases/r2-s121\n"
                                          "S2\tclosed\nS3\t100=releases/r2-s52;200=current\n")
    assert [lv.now_of(levels["S3"], None, t) for t in (50, 150, 250)] == [None, 50, "all"]


# -- passwords: one line per session -----------------------------------------------------------

LINES = """
    [admin]
    html = "ADMIN:root"
    live = "ADMIN:root"
    [GAI]
    html = "OTHER:o"
    [GAI.sites.deck]
    html = [
      { seance = "S1027", mot = "a1", limite = 120, fin = "2026-12-31" },
      { seance = "S1103", mot = "b2" },
      { label = "S1110", password = "c3", limit = [["2026-11-10T09:00", 50], ["2026-11-10T14:00", "all"]] },
    ]
"""


def test_the_session_lines(cfg):
    data = tomllib.loads(textwrap.dedent(LINES))
    entries = pw.for_site(data, cfg.site("deck"))["html"]
    assert [(e.label, e.password, str(e.valid_until)) for e in entries] == [
        ("S1027", "a1", "2026-12-31"), ("S1103", "b2", "None"), ("S1110", "c3", "None"), ("ADMIN", "root", "None")]
    levels = pw.levels_for(data, cfg.site("deck"))
    assert levels["S1027"] == 120 and levels["S1103"] is None and levels["ADMIN"] == "all"
    assert [v for _, v in levels["S1110"]] == [50, "all"]


def test_the_other_forms_take_the_site_level(cfg):
    data = tomllib.loads('[GAI]\nhtml = "P:p,Q:q"\nfull = ["Q"]\n')
    assert pw.levels_for(data, cfg.site("deck")) == {"P": pw.DEFAULT, "Q": "all"}


@pytest.mark.parametrize("line,match", [
    ('{ seance = "S", mot = "m", limite = 0 }', "slide number"),
    ('{ seance = "S", mot = "m", limite = "half" }', "slide number"),
    ('{ seance = "S", mot = "m", room = 3 }', "unknown key 'room'"),
    ('{ seance = "S", label = "T", mot = "m" }', "alias are both given"),
    ('{ seance = "S" }', 'mot = '),
    ('{ seance = "S", mot = "m", limite = [["tomorrow", 3]] }', "is not a time"),
])
def test_a_wrong_line_is_refused(cfg, line, match):
    data = tomllib.loads(f"[GAI.sites.deck]\nhtml = [ {line} ]\nlive = \"L:l\"\n")
    with pytest.raises(ReleaseError, match=match):
        pw.for_site(data, cfg.site("deck")), pw.levels_for(data, cfg.site("deck"))


# -- write_limit: the session's line, its limite alone -----------------------------------------

def _file(tmp_path):
    p = tmp_path / ".stx-passwords.toml"
    p.write_text(textwrap.dedent(LINES))
    return p


def test_limit_label_changes_the_number_only(cfg, tmp_path):
    p = _file(tmp_path)
    before = p.read_text()
    assert pw.write_limit(p, cfg.site("deck"), ["S1027"], 150) == ["S1027: 120 → 150"]
    after = p.read_text()
    assert after == before.replace("limite = 120", "limite = 150")


def test_limit_label_adds_removes_and_writes_all(cfg, tmp_path):
    p = _file(tmp_path)
    pw.write_limit(p, cfg.site("deck"), ["S1103"], 40)
    assert '{ seance = "S1103", mot = "b2", limite = 40 }' in p.read_text()
    pw.write_limit(p, cfg.site("deck"), ["S1103", "S1110"], "all")
    data = tomllib.loads(p.read_text())
    assert pw.levels_for(data, cfg.site("deck"))["S1110"] == "all"
    assert 'limit = "all"' in p.read_text()                    # the English key family is kept
    pw.write_limit(p, cfg.site("deck"), ["S1027"], None)
    assert pw.levels_for(tomllib.loads(p.read_text()), cfg.site("deck"))["S1027"] is None
    assert 'fin = "2026-12-31"' in p.read_text()               # the rest of the line stays


def test_limit_label_refusals(cfg, tmp_path):
    p = _file(tmp_path)
    with pytest.raises(ReleaseError, match=r'no line for session S9 in \[GAI.sites.deck\]'):
        pw.write_limit(p, cfg.site("deck"), ["S9"], 3)
    p.write_text('[GAI]\nhtml = [ { seance = "S", mot = "m" } ]\n')
    with pytest.raises(ReleaseError, match=r"no section \[GAI.sites.deck\]"):
        pw.write_limit(p, cfg.site("deck"), ["S"], 3)


# -- ops --------------------------------------------------------------------------------------

def test_the_check_logs_in_once_per_level(cfg):
    entries = _entries(("S1", "a"), ("S2", "b"), ("ADMIN", "root"))
    levels = {"S1": 12, "S2": None, "ADMIN": "all"}
    names = {12: "r2-s12"}
    good = Seen({"a": "r2-s12", "root": "r2"})
    assert ops.check_levels(good, cfg.site("deck"), {}, entries, levels, "r2", names) == []
    wrong = Seen({"a": "r2", "root": "r2"})                     # S1 would see everything
    assert ops.check_levels(wrong, cfg.site("deck"), {}, entries, levels, "r2", names) == ["S1 sees r2, not r2-s12"]


def test_no_levels_means_everyone_sees_current(cfg):
    t = Seen({"p": "r2"})
    assert ops.check_levels(t, cfg.site("deck"), {}, _entries(("P", "p")), {}, "r2", {}) == []
    ops.write_levels(t, cfg.site("deck"), "")
    assert "static/sites/deck/levels" not in t.files and any("rm -f" in c and c.endswith("levels") for c in t.cmds)


def test_rollback_of_a_limit_restores_the_levels_alone(cfg):
    t, state = FakeTarget(), _state(cuts={"12": "r2-s12"}, cuts_previous={}, up_to_slide=None,
                                    up_to_slide_previous=30, last="limit")
    message = ops.rollback(t, cfg, state, cfg.site("deck"))
    assert "previous levels are back (slides 1 to 30 by default)" in message and "live face is unchanged" in message
    assert "still holds the new levels" in message
    assert t.links == {} and any("levels.previous" in c for c in t.cmds)
    assert all(app != "live" for app, _ in t.reloads)
    v = state["sites"]["prod"]["deck"]
    assert (v["cuts"], v["cuts_previous"], v["up_to_slide"]) == ({}, {"12": "r2-s12"}, 30)


def test_rollback_of_a_publication_moves_both_faces_and_their_levels(cfg):
    t, state = FakeTarget(), _state(cuts={"12": "r2-s12"}, cuts_previous={"12": "r1-s12"}, last="publish")
    assert "both faces are back on r1" in ops.rollback(t, cfg, state, cfg.site("deck"))
    assert t.links == {"static/sites/deck/current": "r1", "live/sites/deck/current": "r1"}
    assert state["sites"]["prod"]["deck"]["cuts"] == {"12": "r1-s12"}


def test_a_limit_needs_an_html_face_a_publication_and_the_whole_release(cfg):
    class Missing(FakeTarget):
        def sh(self, cmd, check=True):
            return subprocess.CompletedProcess(cmd, 1 if cmd.startswith("test -d") else 0, "", "")

    with pytest.raises(ReleaseError, match="no HTML face"):
        ops.limit_site(FakeTarget(), cfg, _state(), cfg.site("live-only"), None, {}, print)
    with pytest.raises(ReleaseError, match="not published on prod — publish it first"):
        ops.limit_site(FakeTarget(), cfg, {"sites": {}}, cfg.site("deck"), None, {}, print)
    with pytest.raises(ReleaseError, match="publish the site again first"):
        ops.limit_site(Missing(), cfg, _state(), cfg.site("deck"), None, {}, print)


def test_levels_already_exported_are_not_exported_again(cfg, monkeypatch):
    class Present(Seen):
        def sh(self, cmd, check=True):
            out = "r2\nr2-s12\n" if cmd.startswith("ls -1") else ""
            self.cmds.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, out, "")

    monkeypatch.setattr(build, "export", lambda *a, **k: pytest.fail("no export: the cut is there"))
    t = Present({"a": "r2-s12", "root": "r2"})
    state = _state(cuts={"12": "r2-s12"})
    entries = _entries(("S1", "a"), ("ADMIN", "root"))
    ops.limit_site(t, cfg, state, cfg.site("deck"), entries, {"S1": 12, "ADMIN": "all"}, print)
    assert t.files["static/sites/deck/levels"] == "ADMIN\tcurrent\nS1\treleases/r2-s12\n"
    assert state["sites"]["prod"]["deck"]["last"] == "limit"


def test_the_site_level_without_label(cfg, monkeypatch):
    monkeypatch.setattr(build, "export", lambda *a, **k: pytest.fail("`all` needs no export"))
    t = Seen({"p": "r2"})
    state = _state(up_to_slide=12, cuts={"12": "r2-s12"})
    ops.limit_site(t, cfg, state, cfg.site("deck"), _entries(("P", "p")), {"P": pw.DEFAULT}, print,
                   slide=None, default=True)
    v = state["sites"]["prod"]["deck"]
    assert v["up_to_slide"] is None and v["up_to_slide_previous"] == 12
    assert t.files["static/sites/deck/levels"] == "P\tcurrent\n"


@pytest.mark.parametrize("value", ["0", "-2", "twelve", "3.5"])
def test_the_command_refuses_what_is_not_a_slide(value):
    from streamtex.cli.release_cmd import limit_cmd
    r = CliRunner().invoke(limit_cmd, ["deck", "--", value])
    assert r.exit_code == 1 and "a slide number (1 or more), `all` or `none`" in r.output


def test_the_export_names_a_cut_after_its_last_slide(cfg, tmp_path, monkeypatch):
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
    for key in ("up_to_slide", "up_to_slide_previous", "last"):
        assert key in SITE_KEYS
    src = tmp_path / "state.json"
    src.write_text(json.dumps({"sites": {"prod": {"deck": {"release": "r1", "up_to_slide": 30}}}}))
    new = import_prototype(tmp_path, src, {"deck"})
    assert new["sites"]["prod"]["deck"] == {"release": "r1", "up_to_slide": 30}


def test_a_rollback_to_a_release_no_longer_on_the_target_is_refused(cfg):
    """After `import`, the prototype may have pruned the previous HTML export: switching to it would break
    the site."""
    class Pruned(FakeTarget):
        def sh(self, cmd, check=True):
            self.cmds.append(cmd)
            gone = cmd.startswith("test -d") and "static/sites/deck/releases/r1" in cmd
            return subprocess.CompletedProcess(cmd, 1 if gone else 0, "", "")

    t, state = Pruned(), _state(last="publish")
    with pytest.raises(ReleaseError, match=r"previous release r1 is no longer on prod \(static/r1\) — nothing changed"):
        ops.rollback(t, cfg, state, cfg.site("deck"))
    assert t.links == {} and state["sites"]["prod"]["deck"]["release"] == "r2"
