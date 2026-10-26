"""stx release end to end on a local target: both applications in Docker on this machine (#136, #111).

A three-site project (both faces, html only, live only) is published, visited as a visitor (a list of
passwords with an end date, an open face, the live login), published again, rolled back, put to sleep
and woken, its passwords changed without publishing, pruned, and a broken document is refused while
the served release stays. Its shared media folder (``media``, ``media_exclude``) reaches the HTML export
of each language and the live face, through the link put in each snapshot.

Needs Docker (skipped otherwise). Run:  uv run pytest -m e2e tests/e2e/test_release_local.py -v
"""
from __future__ import annotations

import base64
import json
import re
import shutil
import socket
import subprocess
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e

LIB = Path(__file__).resolve().parents[2]
# a 1x1 PNG: the shared media of the project
DOT = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4z8DwHwAFAAH/iZk9HQAAAABJRU5ErkJggg==")


def _docker_ok() -> bool:
    return shutil.which("docker") is not None and subprocess.run(
        ["docker", "info"], capture_output=True).returncode == 0


def _port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _req(url, host, data=None, cookie=""):
    r = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    r.add_header("Host", host)
    if cookie:
        r.add_header("Cookie", cookie)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    try:
        resp = urllib.request.build_opener(NoRedirect).open(r, timeout=10)
        return resp.status, resp.headers, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers, ""


def _login(base, host, path, password) -> str:
    _, h, _ = _req(base + path, host, urllib.parse.urlencode({"password": password, "next": "/"}).encode())
    return (h.get("Set-Cookie") or "").split(";")[0]


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    if not _docker_ok():
        pytest.skip("Docker is not running")
    root = tmp_path_factory.mktemp("release-e2e")
    host = tmp_path_factory.mktemp("release-host")
    for d in "abc":
        (root / "docs" / d / "blocks").mkdir(parents=True)
        (root / "docs" / d / "book.py").write_text(textwrap.dedent("""
            import streamtex as stx
            from blocks import bck_main
            stx.st_book([bck_main], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig())
        """))
        (root / "docs" / d / "blocks" / "__init__.py").write_text("")
        (root / "docs" / d / "blocks" / "bck_main.py").write_text(textwrap.dedent(f"""
            from pathlib import Path
            import streamtex as stx
            from streamtex.i18n import T
            DOT = Path(__file__).resolve().parents[3] / "assets" / "img" / "dot.png"   # the snapshot's media link
            def build(**k):
                stx.st_marker("main")
                stx.st_image(uri=str(DOT), width=8)
                stx.st_write(T({{"en": "Document {d} version one", "fr": "Document {d} version un"}}), toc_lvl="1")
                for i in range(40):
                    stx.st_write(f"Paragraph {{i}} of document {d} with enough words for the minimum check.")
        """))
    # demo-d: three blocks, slides 1 | 2-3 | 4 — the slide limit (#146)
    (root / "docs" / "d" / "blocks").mkdir(parents=True)
    (root / "docs" / "d" / "blocks" / "__init__.py").write_text("")
    for name, slides in (("bck_one", ["s1"]), ("bck_two", ["s2", "s3"]), ("bck_three", ["s4"])):
        body = "".join(f'    stx.st_marker("{x}")\n    stx.st_write("Slide {x} of document d, version one", toc_lvl="1")\n'
                       f'    for i in range(15):\n        stx.st_write(f"Words {{i}} on slide {x} for the minimum check.")\n'
                       for x in slides)
        (root / "docs" / "d" / "blocks" / f"{name}.py").write_text(f"import streamtex as stx\ndef build(**k):\n{body}")
    (root / "docs" / "d" / "book.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from blocks import bck_one, bck_two, bck_three
        stx.st_book([bck_one, bck_two, bck_three], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig())
    """))
    (root / "assets" / "img").mkdir(parents=True)
    (root / "assets" / "img" / "dot.png").write_bytes(DOT)
    (root / "assets" / "img" / "dot-original.png").write_bytes(DOT)          # kept out by media_exclude
    (root / "pyproject.toml").write_text(textwrap.dedent(f"""
        [project]
        name = "release-e2e"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = ["streamtex[cli]"]
        [tool.uv.sources]
        streamtex = {{ path = "{LIB}", editable = true }}
    """))
    (root / "stx.toml").write_text(textwrap.dedent("""
        [release]
        project = "demo"
        langs = ["en", "fr"]
        media = "assets"
        media_exclude = [".DS_Store", "*-original.*"]
        [[release.sites]]
        site = "demo-a"
        book = "docs/a/book.py"
        group = "demo"
        [[release.sites]]
        site = "demo-b"
        book = "docs/b/book.py"
        group = "demo"
        faces = ["html"]
        [[release.sites]]
        site = "demo-c"
        book = "docs/c/book.py"
        group = "demo"
        faces = ["live"]
        [[release.sites]]
        site = "demo-d"
        book = "docs/d/book.py"
        explicit = true
    """))
    (root / ".stx-passwords.toml").write_text(textwrap.dedent("""
        [default]
        live = "LIVE-ALL:livepass1"
        html = [["PROMO-OCT", "octpass1"], ["PROMO-NOV", "novpass1", "2099-12-31"]]
        [demo.sites.demo-b]
        open = ["html"]
    """))
    (root / ".gitignore").write_text(".stx-passwords.toml\n.venv/\n")
    tag = root.name.replace("_", "-").lower()
    sp, lp = _port(), _port()
    (root / ".stx-release.json").write_text(json.dumps({
        "default_target": "local", "sites": {},
        "targets": {"local": {"type": "local", "root": str(host), "domain": "example.org",
                              "static": f"stxrel-{tag}-static", "live": f"stxrel-{tag}-live",
                              "static_url": f"http://127.0.0.1:{sp}", "live_url": f"http://127.0.0.1:{lp}"}}}))

    def stx(*args, check=True):
        r = subprocess.run(["uv", "run", "stx", "release", *args], cwd=root, text=True, capture_output=True)
        if check:
            assert r.returncode == 0, r.stdout + r.stderr
        return r

    def git(*args):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    git("init", "-q")
    subprocess.run(["uv", "lock", "-q"], cwd=root, check=True)
    stx("lock")
    git("add", "-A")
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "one")
    stx("local", "up")
    time.sleep(5)
    stx("server-config")
    yield {"root": root, "stx": stx, "git": git, "S": f"http://127.0.0.1:{sp}", "L": f"http://127.0.0.1:{lp}",
           "host": host, "live": f"stxrel-{tag}-live"}
    stx("local", "down", check=False)


def _html_version(p, site, password=""):
    cookie = _login(p["S"], f"{site}.example.org", "/html/_login", password) if password else ""
    code, _, body = _req(p["S"] + "/html/version.txt", f"{site}.example.org", cookie=cookie)
    return body.split("\n")[0] if code == 200 else code


def test_release_end_to_end(project):
    p, stx, git = project, project["stx"], project["git"]
    refused = stx("publish", check=False)
    assert refused.returncode == 1 and "--allow-skew" in refused.stderr        # rel version=a
    out = stx("publish", "--allow-skew").stdout
    assert out.count("✓") == 3
    r1 = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=p["root"], text=True,
                        capture_output=True).stdout.strip()

    # as a visitor: the password list, an end date in the future, a wrong password, an open face
    assert _html_version(p, "demo-a") == 401
    assert _html_version(p, "demo-a", "octpass1") == r1
    assert _html_version(p, "demo-a", "novpass1") == r1
    assert _login(p["S"], "demo-a.example.org", "/html/_login", "wrong") == ""
    assert _html_version(p, "demo-b") == r1
    assert _req(p["L"] + "/", "demo-a.example.org")[0] == 401
    cookie = _login(p["L"], "demo-a.example.org", "/_login", "livepass1")
    assert cookie and _req(p["L"] + "/", "demo-a.example.org", cookie=cookie)[0] == 200
    assert _req(p["L"] + "/_stcore/health", "demo-c.example.org")[0] == 200
    assert _req(p["L"] + "/", "demo-b.example.org")[0] == 404                 # no live face

    # the shared media: in the HTML export of each language, and on the live side through the link
    cookie_html = _login(p["S"], "demo-a.example.org", "/html/_login", "octpass1")
    release_html = p["host"] / "static" / "sites" / "demo-a" / "releases" / r1
    files = {}
    for lang in ("en", "fr"):
        code, _, page = _req(p["S"] + f"/html/{lang}/a/a.html", "demo-a.example.org", cookie=cookie_html)
        src = re.search(r'<img src="(data/images/[0-9a-f]+\.png)"[^>]*width: 8px', page)
        assert code == 200 and src, f"{lang}: the shared image is not in the export"
        assert _req(p["S"] + f"/html/{lang}/a/{src.group(1)}", "demo-a.example.org", cookie=cookie_html)[0] == 200
        files[lang] = release_html / lang / "a" / src.group(1)
        assert files[lang].read_bytes() == DOT
    assert files["en"].stat().st_ino == files["fr"].stat().st_ino            # one copy for both languages
    media = p["host"] / "live" / "media" / "demo" / "assets" / "img"
    assert (media / "dot.png").read_bytes() == DOT and not (media / "dot-original.png").exists()
    for site in ("demo-a", "demo-c"):
        link = p["host"] / "live" / "sites" / site / "releases" / r1 / "assets"
        assert link.is_symlink() and str(link.readlink()) == "/srv/live/media/demo/assets"
        seen = subprocess.run(["docker", "exec", p["live"], "test", "-f",
                               f"/srv/live/sites/{site}/current/assets/img/dot.png"])
        assert seen.returncode == 0, f"{site}: the live face does not see the shared media"
    assert not (p["host"] / "static" / "sites" / "demo-a" / "releases" / r1 / "assets").exists()

    # a second release, then back
    bck = p["root"] / "docs" / "a" / "blocks" / "bck_main.py"
    bck.write_text(bck.read_text().replace("version one", "version two"))
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "two")
    stx("publish", "demo-a", "--allow-skew")
    r2 = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=p["root"], text=True,
                        capture_output=True).stdout.strip()
    assert _html_version(p, "demo-a", "octpass1") == r2
    stx("rollback", "demo-a")
    time.sleep(2)
    assert _html_version(p, "demo-a", "octpass1") == r1

    # sleep and wake
    stx("sleep", "demo-c")
    time.sleep(2)
    assert _req(p["L"] + "/_stcore/health", "demo-c.example.org")[0] == 404
    stx("wake", "demo-c")
    for _ in range(20):
        if _req(p["L"] + "/_stcore/health", "demo-c.example.org")[0] == 200:
            break
        time.sleep(1)
    assert _req(p["L"] + "/_stcore/health", "demo-c.example.org")[0] == 200

    # passwords changed without publishing
    pwf = p["root"] / ".stx-passwords.toml"
    pwf.write_text(pwf.read_text().replace('["PROMO-NOV", "novpass1", "2099-12-31"]', '["PROMO-DEC", "decpass1"]'))
    pid = _live_pid(p, "demo-a")
    stx("passwd")
    assert _live_pid(p, "demo-a") == pid             # the login service reads the records: no restart
    assert _login(p["S"], "demo-a.example.org", "/html/_login", "novpass1") == ""
    assert _html_version(p, "demo-a", "decpass1") == r1

    # a third release: two releases kept
    bck.write_text(bck.read_text().replace("version two", "version three"))
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "three")
    assert "old release(s) removed" in stx("publish", "demo-a", "--allow-skew").stdout
    host = Path(json.loads((p["root"] / ".stx-release.json").read_text())["targets"]["local"]["root"])
    assert len(list((host / "static" / "sites" / "demo-a" / "releases").iterdir())) == 2
    r3 = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=p["root"], text=True,
                        capture_output=True).stdout.strip()

    # a broken document is refused and the served release stays
    bck.write_text(bck.read_text() + "\nraise RuntimeError('broken on purpose')\n")
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "broken")
    broken = stx("publish", "demo-a", "--allow-skew", check=False)
    assert broken.returncode == 1 and "export failed" in broken.stderr
    assert _html_version(p, "demo-a", "decpass1") == r3

    status = stx("status").stdout
    assert "demo-a" in status and "GAP" not in status


def _head(p) -> str:
    return subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=p["root"], text=True,
                          capture_output=True).stdout.strip()


def _live_pid(p, site) -> str:
    return subprocess.run(["docker", "exec", p["live"], "supervisorctl", "pid", site],
                          text=True, capture_output=True).stdout.strip()


def _html_page(p, site, cookie) -> str:
    code, _, page = _req(p["S"] + "/html/en/d/d.html", f"{site}.example.org", cookie=cookie)
    assert code == 200
    return page


def test_slide_limit_end_to_end(project):
    """#146: the limit changes the HTML face alone, participants stay logged in, publish keeps it."""
    p, stx, git = project, project["stx"], project["git"]
    git("checkout", "-q", "--", ".")
    stx("publish", "demo-d", "--allow-skew")
    r1 = _head(p)
    assert _html_version(p, "demo-d", "octpass1") == r1
    cookie = _login(p["S"], "demo-d.example.org", "/html/_login", "octpass1")      # a participant
    pid = _live_pid(p, "demo-d")
    passes = {f: (p["host"] / f / "sites" / "demo-d" / "pass").stat().st_mtime_ns for f in ("static", "live")}

    out = stx("limit", "demo-d", "2", "--allow-skew").stdout
    assert f"{r1}-s3" in out
    page = _html_page(p, "demo-d", cookie)                    # the same session, still open
    assert "Slide s3 of document d" in page and "Slide s4" not in page and '"s4"' not in page
    assert _html_version(p, "demo-d", "octpass1") == f"{r1}-s3"
    assert _live_pid(p, "demo-d") == pid                      # the live face did not restart
    assert passes == {f: (p["host"] / f / "sites" / "demo-d" / "pass").stat().st_mtime_ns
                      for f in ("static", "live")}            # no password rewritten
    assert "already there" in stx("limit", "demo-d", "3", "--allow-skew").stdout   # same block: same cut
    assert "up to 3" in stx("status").stdout

    # a new release keeps the limit
    bck = p["root"] / "docs" / "d" / "blocks" / "bck_one.py"
    bck.write_text(bck.read_text().replace("version one", "version two"))
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "d two")
    r2 = _head(p)
    assert "level up to slide 3" in stx("publish", "demo-d", "--allow-skew").stdout
    assert _html_version(p, "demo-d", "octpass1") == f"{r2}-s3"

    # rollback of a publication: both faces; of a limit: the HTML face alone
    assert f"back on {r1}" in stx("rollback", "demo-d").stdout
    time.sleep(2)                                             # nginx reloading, as after any rollback
    assert _html_version(p, "demo-d", "octpass1") == f"{r1}-s3"
    stx("rollback", "demo-d")
    time.sleep(2)
    assert _html_version(p, "demo-d", "octpass1") == f"{r2}-s3"
    stx("limit", "demo-d", "all", "--allow-skew")
    assert _html_version(p, "demo-d", "octpass1") == r2
    assert "Slide s4" in _html_page(p, "demo-d", _login(p["S"], "demo-d.example.org", "/html/_login", "octpass1"))
    pid = _live_pid(p, "demo-d")
    assert "live face is unchanged" in stx("rollback", "demo-d").stdout
    time.sleep(2)
    assert _html_version(p, "demo-d", "octpass1") == f"{r2}-s3"
    assert _live_pid(p, "demo-d") == pid
    status = stx("status").stdout
    assert "GAP" not in status and "up to 3" in status
    refused = stx("limit", "demo-c", "2", "--allow-skew", check=False)
    assert refused.returncode == 1 and "no HTML face" in refused.stderr



ACCESS = """
    [default]
    live = "LIVE-ALL:livepass1"
    html = [["PROMO-OCT", "octpass1"], ["PROMO-FULL", "fullpass1"]]
    [demo.sites.demo-b]
    open = ["html"]
    [demo.sites.demo-a]
    html = "ONLY-A:onlya1"
    [demo-d.sites.demo-d]
    html = [
      { seance = "S-ONE", mot = "onepass1", limite = 1 },
      { seance = "S-TWO", mot = "twopass1", limite = 2 },
      { seance = "S-ALL", mot = "allpass1", limite = "all" },
      { seance = "S-NONE", mot = "nonepass1" },
      { seance = "S-LATER", mot = "laterpass1", limite = [["2020-01-01T00:00", 1], ["2099-01-01T00:00", "all"]] },
    ]
    [admin]
    live = "ADMIN:rootpass1"
    html = "ADMIN:rootpass1"
"""


def _seen(p, site, cookie):
    """What the HTML face serves to this session: its release, "closed" (not open yet) or the code."""
    code, _, body = _req(p["S"] + "/html/version.txt", f"{site}.example.org", cookie=cookie)
    if code == 200 and "stx-closed" in body:
        return "closed"
    return body.split("\n")[0] if code == 200 else code


def test_access_end_to_end(project):
    """#147, #148: [admin] everywhere, one login across sites, a level per session (a cut, all, closed,
    a schedule), `limit --label` writing the file, sessions kept, rollback."""
    p, stx, git = project, project["stx"], project["git"]
    git("checkout", "-q", "--", ".")
    bck = p["root"] / "docs" / "a" / "blocks" / "bck_main.py"            # repaired after the broken publish
    if "broken on purpose" in bck.read_text():
        bck.write_text(bck.read_text().replace("\nraise RuntimeError('broken on purpose')\n", "\n"))
        git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "repaired")
    pwf = p["root"] / ".stx-passwords.toml"
    pwf.write_text(textwrap.dedent(ACCESS))
    out = stx("publish", "demo-a", "demo-c", "demo-d", "--allow-skew").stdout
    r = _head(p)
    assert "level up to slide 1" in out and "level up to slide 2" in out
    levels = (p["host"] / "static" / "sites" / "demo-d" / "levels").read_text()
    assert f"S-ONE\treleases/{r}-s1\n" in levels and f"S-TWO\treleases/{r}-s3\n" in levels
    assert "S-NONE\tclosed\n" in levels and "ADMIN\tcurrent\n" in levels and "S-ALL\tcurrent\n" in levels

    # the administrator: one login on the HTML face of demo-a, every HTML site opens, all the slides
    admin = _login(p["S"], "demo-a.example.org", "/html/_login", "rootpass1")
    assert admin.startswith("stx_session_")
    assert _seen(p, "demo-a", admin) == r and _seen(p, "demo-d", admin) == r
    assert "Slide s4" in _html_page(p, "demo-d", admin)
    live = _login(p["L"], "demo-a.example.org", "/_login", "rootpass1")          # one login per face
    for site in ("demo-a", "demo-c", "demo-d"):
        assert _req(p["L"] + "/", f"{site}.example.org", cookie=live)[0] == 200, site

    # each session its level
    s = {w: _login(p["S"], "demo-d.example.org", "/html/_login", f"{w}pass1")
         for w in ("one", "two", "all", "none", "later")}
    assert [_seen(p, "demo-d", s[w]) for w in ("one", "two", "all", "none", "later")] == \
        [f"{r}-s1", f"{r}-s3", r, "closed", f"{r}-s1"]
    page = _html_page(p, "demo-d", s["two"])
    assert "Slide s3 of document d" in page and "Slide s4" not in page
    code, _, closed = _req(p["S"] + "/html/en/d/d.html", "demo-d.example.org", cookie=s["none"])
    assert code == 200 and "pas encore ouvert" in closed and "Slide" not in closed
    assert _req(p["S"] + "/html/nothing-here.html", "demo-d.example.org", cookie=admin)[0] == 404   # a real 404
    only = _login(p["S"], "demo-a.example.org", "/html/_login", "onlya1")       # a password of demo-a only
    assert _seen(p, "demo-a", only) == r and _seen(p, "demo-d", only) == 401

    # limit --label: the file's line changes, the open sessions see their new level on the next page
    before = pwf.read_text()
    stx("limit", "demo-d", "none", "--label", "S-TWO", "--allow-skew")
    stx("limit", "demo-d", "2", "--label", "S-NONE", "--allow-skew")
    after = pwf.read_text()
    assert after == before.replace('mot = "twopass1", limite = 2 }', 'mot = "twopass1" }').replace(
        'mot = "nonepass1" }', 'mot = "nonepass1", limite = 2 }')
    assert _seen(p, "demo-d", s["two"]) == "closed" and _seen(p, "demo-d", s["none"]) == f"{r}-s3"
    assert "[not open yet]" in stx("auth-status", "demo-d").stdout

    # rollback of a limit: the previous levels; the sessions are still open
    assert "still holds the new levels" in stx("rollback", "demo-d").stdout    # the last change only
    assert _seen(p, "demo-d", s["none"]) == "closed" and _seen(p, "demo-d", s["two"]) == "closed"
    pwf.write_text(before)

    # writing the passwords again closes no session; a changed password closes only its own
    stx("passwd")
    assert _seen(p, "demo-d", admin) == r and _seen(p, "demo-d", s["one"]) == f"{r}-s1"
    pwf.write_text(before.replace('"onepass1"', '"onepass2"'))
    stx("passwd")
    assert _seen(p, "demo-d", s["one"]) == 401
    assert _seen(p, "demo-d", admin) == r and _seen(p, "demo-d", s["all"]) == r
    assert "GAP" not in stx("status").stdout
