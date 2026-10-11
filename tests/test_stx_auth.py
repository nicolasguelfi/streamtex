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
