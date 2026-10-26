"""Tests for streamtex.deploy.stx_auth — the server-side login service (#104, #108)."""

import ast
import http.client
import os
import stat
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

import pytest

from streamtex.deploy import stx_auth
from streamtex.deploy.stx_auth import (
    AuthServer,
    Entry,
    check_password,
    check_token,
    format_entry,
    hash_password,
    make_token,
    parse_entry,
    parse_records,
)

# A cheap scrypt cost keeps the suite fast; the format is the same.
FAST = {"n": 16, "r": 1, "p": 1}


def _rec(word: str) -> str:
    return hash_password(word, **FAST)


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


class TestRecords:
    def test_hash_and_check(self):
        rec = _rec("PT790948")
        assert rec.startswith("scrypt$16$1$1$")
        assert check_password(rec, "PT790948")
        assert not check_password(rec, "pt790948")
        assert not check_password("garbage", "PT790948")

    def test_default_cost_is_the_documented_one(self):
        assert hash_password("x").startswith("scrypt$16384$8$1$")

    def test_plain_record_gets_default_label(self):
        rec = _rec("a")
        e = parse_entry(rec)
        assert e == Entry("default", rec, None)

    def test_labelled_record_with_end_date(self):
        rec = _rec("a")
        e = parse_entry(f"PROMPT270115:{rec}:2027-01-31")
        assert e == Entry("PROMPT270115", rec, date(2027, 1, 31))
        assert format_entry(e) == f"PROMPT270115:{rec}:2027-01-31"

    def test_round_trip(self):
        e = Entry("cohort-1", _rec("a"))
        assert parse_entry(format_entry(e)) == e

    @pytest.mark.parametrize("line", [
        "alice",
        "bad label:scrypt$16$1$1$00$00",
        "lbl:md5$abc",
        "lbl:scrypt$16$1$1$zz$zz",
        "lbl:{rec}:2027-13-45",
    ])
    def test_invalid_lines(self, line):
        assert parse_entry(line.format(rec=_rec("a"))) is None

    def test_open_only_when_alone(self):
        assert parse_records("open\n").open
        assert parse_records("# a comment\n\nopen\n").open
        mixed = parse_records(f"open\nA:{_rec('a')}\n")
        assert not mixed.open
        assert [e.label for e in mixed.entries] == ["A"]

    def test_empty_file_is_closed(self):
        r = parse_records("")
        assert not r.open and r.entries == ()

    def test_invalid_lines_ignored_and_first_label_wins(self):
        r1, r2 = _rec("one"), _rec("two")
        r = parse_records(f"A:{r1}\nnot a record\nA:{r2}\nB:{r2}\n")
        assert [(e.label, e.record) for e in r.entries] == [("A", r1), ("B", r2)]

    def test_entry_cap(self):
        rec = _rec("a")
        text = "\n".join(f"L{i}:{rec}" for i in range(stx_auth.MAX_ENTRIES + 10))
        assert len(parse_records(text).entries) == stx_auth.MAX_ENTRIES


class TestTokens:
    KEY = b"k" * 32

    def test_valid_token(self):
        e = Entry("A", _rec("a"))
        r = parse_records(format_entry(e))
        tok = make_token(self.KEY, "site", e, 60)
        assert check_token(self.KEY, "site", r, tok) == e

    def test_expired_token(self):
        e = Entry("A", _rec("a"))
        r = parse_records(format_entry(e))
        tok = make_token(self.KEY, "site", e, 60, now=time.time() - 120)
        assert check_token(self.KEY, "site", r, tok) is None

    def test_other_site_other_key_tampered(self):
        e = Entry("A", _rec("a"))
        r = parse_records(format_entry(e))
        tok = make_token(self.KEY, "site", e, 60)
        assert check_token(self.KEY, "other", r, tok) is None
        assert check_token(b"x" * 32, "site", r, tok) is None
        expiry, rest = tok.split(".", 1)
        assert check_token(self.KEY, "site", r, f"{int(expiry) + 999}.{rest}") is None
        assert check_token(self.KEY, "site", r, "garbage") is None
        assert check_token(self.KEY, "site", r, "") is None

    def test_label_cannot_be_swapped(self):
        a, b = Entry("A", _rec("a")), Entry("B", _rec("b"))
        r = parse_records(f"{format_entry(a)}\n{format_entry(b)}")
        expiry, _label, _gen, sig = make_token(self.KEY, "s", a, 60).split(".")
        assert check_token(self.KEY, "s", r, f"{expiry}.B.{b.generation}.{sig}") is None


# ---------------------------------------------------------------------------
# HTTP service
# ---------------------------------------------------------------------------


@pytest.fixture
def server(tmp_path):
    srv = AuthServer(("127.0.0.1", 0), tmp_path, session_seconds=3600)
    t = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    t.start()
    yield srv
    srv.shutdown()
    srv.server_close()


def _write(srv: AuthServer, site: str, text: str) -> None:
    d = Path(srv.root) / "sites" / site
    d.mkdir(parents=True, exist_ok=True)
    p = d / "pass"
    p.write_text(text, encoding="utf-8")
    # A rewrite within the same mtime tick must still be seen.
    st = p.stat()
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000))


def _req(srv, method, path, headers=None, body=None, conn=None):
    own = conn is None
    conn = conn or http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        resp = conn.getresponse()
        data = resp.read()
        return resp, data
    finally:
        if own:
            conn.close()


def _h(site="demo", **extra):
    return {"X-Stx-Site": site, **extra}


def _login(srv, word, site="demo", nxt="/page?x=1", **extra):
    body = urlencode({"password": word, "next": nxt})
    headers = _h(site, **extra)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    return _req(srv, "POST", "/login", headers, body)


def _cookie(resp):
    sc = resp.getheader("Set-Cookie")
    return sc.split(";")[0] if sc else None


class TestService:
    def test_closed_without_file(self, server):
        resp, _ = _req(server, "GET", "/check", _h())
        assert resp.status == 401
        resp, _ = _req(server, "GET", "/check", {})
        assert resp.status == 401

    def test_open_site(self, server):
        _write(server, "demo", "open\n")
        resp, _ = _req(server, "GET", "/check", _h())
        assert resp.status == 204
        assert resp.getheader("X-Stx-Label") == "open"

    def test_form_page(self, server):
        _write(server, "demo", _rec("a") + "\n")
        resp, body = _req(server, "GET", "/login", _h(**{
            "X-Original-URI": "/book?marker=3", "X-Stx-Login": "/html/_login", "Host": "demo.example.org"}))
        assert resp.status == 401
        assert resp.getheader("Cache-Control") == "no-store"
        assert resp.getheader("Server") == "stx-auth"
        text = body.decode()
        assert 'action="/html/_login"' in text
        assert 'value="/book?marker=3"' in text
        assert text.count('type="password"') == 1
        assert "demo.example.org" in text

    def test_form_in_french(self, server):
        _, body = _req(server, "GET", "/login", _h(**{"Accept-Language": "fr-FR,fr;q=0.9"}))
        assert "Mot de passe" in body.decode()

    def test_prefix_restored(self, server):
        _, body = _req(server, "GET", "/login", _h(**{
            "X-Original-URI": "/chapter/index.html", "X-Forwarded-Prefix": "/html"}))
        assert 'value="/html/chapter/index.html"' in body.decode()

    @pytest.mark.parametrize("nxt", ["//evil.example/x", "https://evil.example/", "/_stx_auth", "javascript:x"])
    def test_no_open_redirect(self, server, nxt):
        _write(server, "demo", _rec("a") + "\n")
        resp, _ = _login(server, "a", nxt=nxt, **{"X-Stx-Home": "/html/"})
        assert resp.status == 303
        assert resp.getheader("Location") == "/html/"

    def test_injection_is_escaped(self, server):
        _, body = _req(server, "GET", "/login", _h(**{"X-Original-URI": '/x"><script>alert(1)</script>'}))
        assert "<script>alert" not in body.decode()

    def test_wrong_password(self, server):
        _write(server, "demo", _rec("right") + "\n")
        resp, body = _login(server, "wrong")
        assert resp.status == 401
        assert _cookie(resp) is None
        assert "Wrong password" in body.decode()
        resp, _ = _login(server, "")
        assert resp.status == 401

    @pytest.mark.parametrize("typed", ["pw", " pw", "pw ", "p w", "p\u00a0w", "p\u202fw", "\tpw\n"])
    def test_whitespace_typed_is_removed(self, server, typed):
        """#129: a space added by a phone or a copy-paste does not refuse the password."""
        _write(server, "demo", _rec("pw") + "\n")
        resp, _ = _login(server, typed)
        assert resp.status == 303
        assert _cookie(resp)

    def test_case_still_matters_and_spaces_do_not_open_a_wrong_password(self, server):
        _write(server, "demo", _rec("pw") + "\n")
        assert _login(server, "pW")[0].status == 401
        resp, body = _login(server, " p x ")
        assert resp.status == 401
        assert "Wrong password" in body.decode()
        assert _login(server, "   ")[0].status == 401

    def test_login_then_check(self, server):
        _write(server, "demo", _rec("right") + "\n")
        resp, _ = _login(server, "right")
        assert resp.status == 303
        assert resp.getheader("Location") == "/page?x=1"
        sc = resp.getheader("Set-Cookie")
        assert sc.startswith("stx_session_demo=")
        for flag in ("HttpOnly", "Secure", "SameSite=Lax", "Max-Age=3600", "Path=/"):
            assert flag in sc
        resp, _ = _req(server, "GET", "/check", _h(Cookie=_cookie(resp)))
        assert resp.status == 204
        assert resp.getheader("X-Stx-Label") == "default"

    def test_cookie_name_from_nginx(self, server):
        _write(server, "demo", _rec("right") + "\n")
        resp, _ = _login(server, "right", **{"X-Stx-Cookie": "stx_html"})
        cookie = _cookie(resp)
        assert cookie.startswith("stx_html=")
        resp, _ = _req(server, "GET", "/check", _h(Cookie=cookie))
        assert resp.status == 401  # default cookie name expected here
        resp, _ = _req(server, "GET", "/check", _h(Cookie=cookie, **{"X-Stx-Cookie": "stx_html"}))
        assert resp.status == 204

    def test_cookie_of_site_a_refused_on_b(self, server):
        rec = _rec("same")
        _write(server, "site-a", rec + "\n")
        _write(server, "site-b", rec + "\n")
        resp, _ = _login(server, "same", site="site-a", **{"X-Stx-Cookie": "c"})
        cookie = _cookie(resp)
        resp, _ = _req(server, "GET", "/check", _h("site-b", Cookie=cookie, **{"X-Stx-Cookie": "c"}))
        assert resp.status == 401

    def test_labelled_list(self, server):
        _write(server, "demo", f"PROMPT261013:{_rec('PT790948')}\nPROMPT270115:{_rec('PT599038')}\n")
        resp, _ = _login(server, "PT599038")
        assert resp.status == 303
        resp, _ = _req(server, "GET", "/check", _h(Cookie=_cookie(resp)))
        assert resp.getheader("X-Stx-Label") == "PROMPT270115"

    def test_removing_one_entry_ends_only_its_sessions(self, server):
        a, b = f"A:{_rec('aaa')}", f"B:{_rec('bbb')}"
        _write(server, "demo", f"{a}\n{b}\n")
        ca = _cookie(_login(server, "aaa")[0])
        cb = _cookie(_login(server, "bbb")[0])
        _write(server, "demo", f"{b}\n")
        assert _req(server, "GET", "/check", _h(Cookie=ca))[0].status == 401
        assert _req(server, "GET", "/check", _h(Cookie=cb))[0].status == 204

    def test_changing_a_password_ends_its_sessions(self, server):
        _write(server, "demo", f"A:{_rec('old')}\n")
        ca = _cookie(_login(server, "old")[0])
        _write(server, "demo", f"A:{_rec('new')}\n")
        assert _req(server, "GET", "/check", _h(Cookie=ca))[0].status == 401
        assert _login(server, "old")[0].status == 401

    def test_end_date(self, server):
        yesterday = (date.today() - timedelta(days=2)).isoformat()
        tomorrow = (date.today() + timedelta(days=2)).isoformat()
        _write(server, "demo", f"OLD:{_rec('old')}:{yesterday}\nNEW:{_rec('new')}:{tomorrow}\n")
        assert _login(server, "old")[0].status == 401
        resp, _ = _login(server, "new")
        assert resp.status == 303
        cookie = _cookie(resp)
        assert _req(server, "GET", "/check", _h(Cookie=cookie))[0].status == 204
        # The date passes while the session is open: the next check refuses it.
        rec_line = parse_records((Path(server.root) / "sites/demo/pass").read_text()).entry("NEW")
        _write(server, "demo", f"NEW:{rec_line.record}:{yesterday}\n")
        assert _req(server, "GET", "/check", _h(Cookie=cookie))[0].status == 401

    def test_oversized_body(self, server):
        resp, _ = _req(server, "POST", "/login", _h(**{"Content-Type": "application/x-www-form-urlencoded"}),
                       body="password=" + "x" * 10000)
        assert resp.status == 413

    def test_unknown_paths(self, server):
        assert _req(server, "GET", "/pass", _h())[0].status == 404
        assert _req(server, "GET", "/sites/demo/pass", _h())[0].status == 404
        assert _req(server, "POST", "/check", _h(), body="")[0].status == 404

    def test_key_file_mode(self, server):
        key = Path(server.root) / "conf" / "session.key"
        assert stat.S_IMODE(key.stat().st_mode) == 0o600
        assert len(key.read_bytes()) == 32

    def test_keep_alive(self, server):
        _write(server, "demo", "open\n")
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=10)
        try:
            for _ in range(20):
                resp, _ = _req(server, "GET", "/check", _h(), conn=conn)
                assert resp.status == 204
        finally:
            conn.close()

    def test_burst_of_parallel_checks(self, server):
        """#108: a browser opens ~100 connections at once; none may wait for SYN retries."""
        _write(server, "demo", _rec("right") + "\n")
        cookie = _cookie(_login(server, "right")[0])

        def one(_):
            t0 = time.monotonic()
            resp, _ = _req(server, "GET", "/check", _h(Cookie=cookie))
            return resp.status, time.monotonic() - t0

        t0 = time.monotonic()
        with ThreadPoolExecutor(max_workers=200) as pool:
            results = list(pool.map(one, range(400)))
        total = time.monotonic() - t0
        assert all(status == 204 for status, _ in results)
        # A full backlog shows up as 1 s, 3 s, 7 s... connect retries.
        assert max(d for _, d in results) < 0.9
        assert total < 5


def test_service_uses_only_the_standard_library():
    """The container runs the file outside the package: no streamtex, no streamlit."""
    tree = ast.parse(Path(stx_auth.__file__).read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    assert names <= set(sys.stdlib_module_names) | {"__future__"}


# ---------------------------------------------------------------------------
# Interface (#135): the file is copied onto servers by projects
# ---------------------------------------------------------------------------

_REC = "scrypt$16384$8$1$" + "0" * 32 + "$" + "1" * 64

#: What each interface number promises. Changing one of these means a new
#: number: add a key here, bump AUTH_INTERFACE and say it in the CHANGELOG.
INTERFACES = {
    1: {
        "headers": ["X-Forwarded-Prefix", "X-Original-URI", "X-Stx-Auth", "X-Stx-Cookie",
                    "X-Stx-Home", "X-Stx-Label", "X-Stx-Login", "X-Stx-Site"],
        "env": ["STX_AUTH_PORT", "STX_AUTH_ROOT", "STX_AUTH_SESSION_HOURS"],
        "patterns": {
            "SITE_RE": r"^[a-z0-9-]{1,63}$",
            "LABEL_RE": r"^[A-Za-z0-9_-]{1,64}$",
            "COOKIE_RE": r"^[A-Za-z0-9_-]{1,64}$",
            "DATE_RE": r"^\d{4}-\d{2}-\d{2}$",
            "RECORD_RE": r"^scrypt\$\d+\$\d+\$\d+\$[0-9a-f]{16,128}\$[0-9a-f]{32,128}$",
        },
        "scrypt": [16384, 8, 1],
        "defaults": ["/var/lib/stx-auth", 9100, "default"],
        "paths": ["conf", "pass", "session.key", "sites"],
        "cookie": ["stx_session_"],
        "token": "1060.T1.0db25f8b5ddde317.f13e6b4c04deb8e405280bfff7bc09d81dc4f8320a4e7a22f6cae5952ade00c1",
        "lines": ["default:" + _REC, "T1:" + _REC, "T1:" + _REC + ":2027-01-31"],
    },
    2: {   # #147: a session shared by the sites of a domain, the full or limited view
        "headers": ["X-Forwarded-Prefix", "X-Original-URI", "X-Stx-Auth", "X-Stx-Cookie", "X-Stx-Domain",
                    "X-Stx-Home", "X-Stx-Label", "X-Stx-Login", "X-Stx-Site", "X-Stx-View"],
        "env": ["STX_AUTH_PORT", "STX_AUTH_ROOT", "STX_AUTH_SESSION_HOURS"],
        "patterns": {
            "SITE_RE": r"^[a-z0-9-]{1,63}$",
            "LABEL_RE": r"^[A-Za-z0-9_-]{1,64}$",
            "COOKIE_RE": r"^[A-Za-z0-9_-]{1,64}$",
            "DOMAIN_RE": r"^(?=.{3,253}$)[a-z0-9-]{1,63}(\.[a-z0-9-]{1,63})+$",
            "DATE_RE": r"^\d{4}-\d{2}-\d{2}$",
            "RECORD_RE": r"^scrypt\$\d+\$\d+\$\d+\$[0-9a-f]{16,128}\$[0-9a-f]{32,128}$",
        },
        "scrypt": [16384, 8, 1],
        "defaults": ["/var/lib/stx-auth", 9100, "default"],
        "paths": ["conf", "full", "limited", "pass", "session.key", "sites"],
        "cookie": ["stx_session_"],
        "shared": "*",
        "token": "1060.T1.0db25f8b5ddde317.f13e6b4c04deb8e405280bfff7bc09d81dc4f8320a4e7a22f6cae5952ade00c1",
        "lines": ["default:" + _REC, "T1:" + _REC, "T1:" + _REC + ":2027-01-31"],
    },
}


def _interface():
    import re
    code = Path(stx_auth.__file__).read_text(encoding="utf-8").split('"""', 2)[2]
    return {
        "headers": sorted(set(re.findall(r'"(X-[A-Za-z]+(?:-[A-Za-z]+)*)"', code))),
        "env": sorted(set(re.findall(r'"(STX_AUTH_[A-Z_]+)"', code))),
        "patterns": {n: getattr(stx_auth, n).pattern
                     for n in ("SITE_RE", "LABEL_RE", "COOKIE_RE", "DOMAIN_RE", "DATE_RE", "RECORD_RE")},
        "scrypt": [stx_auth.SCRYPT_N, stx_auth.SCRYPT_R, stx_auth.SCRYPT_P],
        "defaults": [stx_auth.DEFAULT_ROOT, stx_auth.DEFAULT_PORT, stx_auth.DEFAULT_LABEL],
        "paths": sorted(set(re.findall(r'"(sites|pass|conf|session\.key|full|limited)"', code))),
        "cookie": sorted(set(re.findall(r"stx_session_", code))),
        "shared": stx_auth.SHARED,
        "token": make_token(b"k" * 32, "demo", Entry("T1", _REC), 60, now=1000),
        "lines": [format_entry(Entry(stx_auth.DEFAULT_LABEL, _REC)), format_entry(Entry("T1", _REC)),
                  format_entry(Entry("T1", _REC, date(2027, 1, 31)))],
    }


class TestInterface:
    def test_the_interface_matches_its_number(self):
        assert _interface() == INTERFACES[stx_auth.AUTH_INTERFACE]

    def test_the_version_is_the_release(self):
        import tomllib
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        version = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
        assert stx_auth.STX_VERSION == version, "bump STX_VERSION in streamtex/deploy/stx_auth.py"

    def test_check_returns_the_stamp(self, server):
        stamp = f"{stx_auth.AUTH_INTERFACE} {stx_auth.STX_VERSION}"
        _write(server, "demo", _rec("pw") + "\n")
        resp, _ = _req(server, "GET", "/check", _h())
        assert resp.status == 401 and resp.getheader("X-Stx-Auth") == stamp
        _write(server, "shut", "open\n")
        resp, _ = _req(server, "GET", "/check", _h("shut"))
        assert resp.status == 204 and resp.getheader("X-Stx-Auth") == stamp

    def test_the_login_page_does_not_show_the_version(self, server):
        resp, _ = _req(server, "GET", "/login", _h())
        assert resp.getheader("X-Stx-Auth") is None


# ---------------------------------------------------------------------------
# #147: one login for every site of a domain; the full or limited view
# ---------------------------------------------------------------------------

def _shared(site, **extra):
    return _h(site, **{"X-Stx-Cookie": "stx_session", "X-Stx-Domain": "example.org",
                       "Host": f"{site}.example.org", **extra})


class TestSharedSession:
    def _two_sites(self, server, admin_b=True):
        admin = _rec("root-pw")                       # ONE record on both sites, as stx release writes it
        _write(server, "a", f"ADMIN:{admin}\nPROMO-A:{_rec('pa')}\n")
        _write(server, "b", (f"ADMIN:{admin}\n" if admin_b else "") + f"PROMO-B:{_rec('pb')}\n")

    def test_the_cookie_is_set_for_the_domain(self, server):
        self._two_sites(server)
        resp, _ = _login(server, "root-pw", "a", **{k: v for k, v in _shared("a").items() if k != "X-Stx-Site"})
        sc = resp.getheader("Set-Cookie")
        assert resp.status == 303 and "Domain=example.org;" in sc
        assert sc.startswith(f"stx_session_{server.key_tag}=")

    def test_one_login_opens_the_other_site_holding_the_same_password(self, server):
        self._two_sites(server)
        resp, _ = _login(server, "root-pw", "a", **{k: v for k, v in _shared("a").items() if k != "X-Stx-Site"})
        cookie = _cookie(resp)
        for site in ("a", "b"):
            resp, _ = _req(server, "GET", "/check", _shared(site, Cookie=cookie))
            assert resp.status == 204 and resp.getheader("X-Stx-Label") == "ADMIN"

    def test_a_password_of_one_site_stays_there(self, server):
        self._two_sites(server)
        resp, _ = _login(server, "pa", "a", **{k: v for k, v in _shared("a").items() if k != "X-Stx-Site"})
        cookie = _cookie(resp)
        assert _req(server, "GET", "/check", _shared("a", Cookie=cookie))[0].status == 204
        assert _req(server, "GET", "/check", _shared("b", Cookie=cookie))[0].status == 401

    def test_a_site_without_the_label_refuses(self, server):
        self._two_sites(server, admin_b=False)
        resp, _ = _login(server, "root-pw", "a", **{k: v for k, v in _shared("a").items() if k != "X-Stx-Site"})
        assert _req(server, "GET", "/check", _shared("b", Cookie=_cookie(resp)))[0].status == 401

    def test_the_same_label_with_another_password_refuses(self, server):
        _write(server, "a", f"ADMIN:{_rec('root-pw')}\n")
        _write(server, "b", f"ADMIN:{_rec('root-pw')}\n")    # same word, another salt: another record
        resp, _ = _login(server, "root-pw", "a", **{k: v for k, v in _shared("a").items() if k != "X-Stx-Site"})
        assert _req(server, "GET", "/check", _shared("b", Cookie=_cookie(resp)))[0].status == 401

    def test_a_host_outside_the_domain_keeps_a_site_session(self, server):
        self._two_sites(server)
        headers = _shared("a", Host="a.other.net")
        resp, _ = _login(server, "root-pw", "a", **{k: v for k, v in headers.items() if k != "X-Stx-Site"})
        sc = resp.getheader("Set-Cookie")
        assert "Domain=" not in sc and sc.startswith("stx_session=")

    def test_a_site_session_is_not_a_shared_one(self, server):
        self._two_sites(server)
        resp, _ = _login(server, "root-pw", "a", **{"X-Stx-Cookie": "stx_session"})
        old = _cookie(resp).split("=", 1)[1]
        cookie = f"stx_session_{server.key_tag}={old}"
        assert _req(server, "GET", "/check", _shared("a", Cookie=cookie))[0].status == 401

    def test_two_values_of_the_cookie_any_valid_one_counts(self, server):
        self._two_sites(server)
        resp, _ = _login(server, "root-pw", "a", **{k: v for k, v in _shared("a").items() if k != "X-Stx-Site"})
        good = _cookie(resp)
        name = good.split("=", 1)[0]
        resp, _ = _req(server, "GET", "/check", _shared("b", Cookie=f"{name}=1.x.y.z; {good}"))
        assert resp.status == 204

    def test_without_the_domain_header_nothing_changes(self, server):
        self._two_sites(server)
        resp, _ = _login(server, "root-pw", "a")
        assert resp.getheader("Set-Cookie").startswith("stx_session_a=")
        assert "Domain=" not in resp.getheader("Set-Cookie")


class TestView:
    def _limited(self, server, site="demo", full=None):
        d = Path(server.root) / "sites" / site
        (d / "releases" / "r1-s3").mkdir(parents=True, exist_ok=True)
        if not (d / "limited").exists():
            (d / "limited").symlink_to("releases/r1-s3")
        if full is not None:
            (d / "full").write_text("".join(f"{x}\n" for x in full), encoding="utf-8")

    def _view(self, server, word, site="demo"):
        resp, _ = _login(server, word, site)
        resp, _ = _req(server, "GET", "/check", _h(site, Cookie=_cookie(resp)))
        assert resp.status == 204
        return resp.getheader("X-Stx-View")

    def test_without_a_limited_release_everyone_sees_everything(self, server):
        _write(server, "demo", f"ADMIN:{_rec('root')}\nP:{_rec('p')}\n")
        assert self._view(server, "p") == "full"

    def test_a_limited_release_for_the_labels_not_listed(self, server):
        _write(server, "demo", f"ADMIN:{_rec('root')}\nPA:{_rec('pa')}\nPB:{_rec('pb')}\n")
        self._limited(server, full=["ADMIN", "PA"])
        assert [self._view(server, w) for w in ("root", "pa", "pb")] == ["full", "full", "limited"]

    def test_the_full_list_is_read_again_when_it_changes(self, server):
        _write(server, "demo", f"PB:{_rec('pb')}\n")
        self._limited(server, full=[])
        assert self._view(server, "pb") == "limited"
        full = Path(server.root) / "sites" / "demo" / "full"
        full.write_text("PB\n", encoding="utf-8")
        st = full.stat()
        os.utime(full, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000))
        assert self._view(server, "pb") == "full"

    def test_an_open_site_with_a_limit_is_limited(self, server):
        _write(server, "demo", "open\n")
        self._limited(server)
        resp, _ = _req(server, "GET", "/check", _h())
        assert resp.status == 204 and resp.getheader("X-Stx-View") == "limited"
