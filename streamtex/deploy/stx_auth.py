"""stx_auth — the server-side login screen of a deployed StreamTeX site (#104).

A small HTTP service, standard library only, that runs next to nginx in the
container. nginx asks it before serving any protected page of either face
(the Streamlit app on ``/`` and the static export on ``/html/``):

- ``GET /check``  -> 204 (session valid, ``X-Stx-Label`` names the entry) or 401;
- ``GET /login``  -> the login form (status 401), in the visitor's language;
- ``POST /login`` -> checks the password, sets the session cookie, 303 back.
  Whitespace typed anywhere in the password is removed first (#129).

nginx describes each request with headers it sets itself (a client cannot
supply them, the service listens on 127.0.0.1 only):

- ``X-Stx-Site``   the record set to use: ``<root>/sites/<site>/pass``;
- ``X-Stx-Cookie`` the cookie name (default ``stx_session_<site>``);
- ``X-Stx-Login``  the form's action as the visitor sees it (default ``/_login``);
- ``X-Stx-Home``   where to go when the return address is unusable (default ``/``);
- ``X-Stx-Domain`` the domain the sites share (``example.org``), optional: the
  session is then valid on every site of the server (#147, below);
- ``X-Original-URI`` and ``X-Forwarded-Prefix``: the page asked for.

One login for every site (#147). With ``X-Stx-Domain``, the cookie is set
for that domain and its token no longer names the site: a site accepts it when
ITS OWN records hold the same label with the same record (same password, same
generation). A password given to several sites opens them all after one
login; a password of one site only stays valid there; a stolen cookie gives no
more than the password itself. The cookie name ends with a tag of the server
key, so two projects sharing a domain never overwrite each other's session.

What each session sees (#148). ``GET /check`` also answers ``X-Stx-View``: the
folder of the label's level, read from ``<root>/sites/<site>/levels``, one line
per label::

    S1027	releases/r2-s120
    S1103	closed
    S1110	1762761600=releases/r2-s52;1762779600=current

A scheduled level is the last step whose time (epoch seconds) has passed, and
``closed`` before the first one. ``closed`` and a label missing from the file
mean "not open yet"; without the file, everyone sees ``current``. nginx serves
``<root>/sites/<site>/<folder>``.

Record file, one entry per line (blank lines and ``#`` comments ignored)::

    open                                          # the site is open (only entry)
    scrypt$16384$8$1$<salt>$<hash>                # one password, label "default"
    PROMPT261013:scrypt$16384$8$1$<salt>$<hash>   # labelled password
    PROMPT270115:scrypt$...$<hash>:2027-01-31     # labelled, valid through that day (UTC)

Security properties:

- only scrypt records are stored; comparisons run in constant time;
- the cookie is HttpOnly, Secure, SameSite=Lax, expires, and is signed
  (HMAC-SHA256) with a server key created at first start (mode 600);
- the signature covers the site (or the shared mark), the label and a
  generation taken from that entry's record: changing or removing one entry
  ends only its sessions;
- a site with no record file, or no usable entry, is closed;
- the return address only accepts a path on the same site.

Throughput (#108): a browser asks for about a hundred files at once and nginx
checks each one. The listen backlog is raised from the standard library's 5,
HTTP/1.1 keep-alive lets nginx reuse its connections, the record file is
parsed once per change, and concurrent scrypt computations are capped.

Run with ``python3 stx_auth.py``; configured by ``STX_AUTH_ROOT``,
``STX_AUTH_PORT`` and ``STX_AUTH_SESSION_HOURS``.

Interface (#135). Projects copy this file onto their servers, so what it
expects from nginx and from the tooling that writes the record files is a
contract, numbered by ``AUTH_INTERFACE``:

- the request headers above (``X-Stx-Site``, ``X-Stx-Cookie``,
  ``X-Stx-Login``, ``X-Stx-Home``, ``X-Original-URI``,
  ``X-Forwarded-Prefix``, ``X-Stx-Domain``) and the response headers
  ``X-Stx-Label`` and ``X-Stx-View`` (``current``, ``closed`` or
  ``releases/<name>``);
- the environment variables above;
- the record files ``<root>/sites/<site>/pass``, their line grammar and the
  scrypt record format; ``<root>/sites/<site>/levels`` and its line grammar;
  the server key ``<root>/conf/session.key``;
- the cookie ``stx_session_<site>`` (``<name>_<key tag>`` for a shared
  session) and its token ``<expiry>.<label>.<generation>.<signature>``.

Any change to one of them bumps ``AUTH_INTERFACE`` and is announced in the
CHANGELOG. ``STX_VERSION`` is the library release the file comes from. Both
are plain constants (a copied file can be checked with ``grep``), and
``GET /check`` returns them in ``X-Stx-Auth`` (``<interface> <version>``):
nginx's auth sub-request keeps that header from the visitor.
"""

from __future__ import annotations

import hashlib
import hmac
import html
import os
import re
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

#: The library release this file ships with, and its interface number (#135).
STX_VERSION = "0.7.78"
AUTH_INTERFACE = 3

DEFAULT_ROOT = "/var/lib/stx-auth"
DEFAULT_PORT = 9100
DEFAULT_SESSION_HOURS = 12

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_MAXMEM = 64 * 1024 * 1024
MAX_SCRYPT_AT_ONCE = 4
MAX_ENTRIES = 64
MAX_BODY = 4096

DEFAULT_LABEL = "default"
SITE_RE = re.compile(r"^[a-z0-9-]{1,63}$")
LABEL_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
COOKIE_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
DOMAIN_RE = re.compile(r"^(?=.{3,253}$)[a-z0-9-]{1,63}(\.[a-z0-9-]{1,63})+$")
SHARED = "*"           # the "site" a shared session is signed for (#147)
VIEW_RE = re.compile(r"^(current|closed|releases/[A-Za-z0-9_-][A-Za-z0-9._-]{0,127})$")
PATH_RE = re.compile(r"^/[A-Za-z0-9._~!$&'()*+,;=:@%/?-]*$")
PREFIX_RE = re.compile(r"^/[A-Za-z0-9_-]{1,32}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RECORD_RE = re.compile(r"^scrypt\$\d+\$\d+\$\d+\$[0-9a-f]{16,128}\$[0-9a-f]{32,128}$")


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Entry:
    """One accepted password: its label, its scrypt record, its last valid day."""

    label: str
    record: str
    valid_until: date | None = None

    @property
    def generation(self) -> str:
        return hashlib.sha256(self.record.encode()).hexdigest()[:16]

    def expired(self, today: date | None = None) -> bool:
        if self.valid_until is None:
            return False
        return (today or _today()) > self.valid_until


@dataclass(frozen=True)
class Records:
    """The parsed record file of one site."""

    open: bool = False
    entries: tuple[Entry, ...] = ()

    def entry(self, label: str) -> Entry | None:
        for e in self.entries:
            if e.label == label:
                return e
        return None


CLOSED = Records()


def _today() -> date:
    return datetime.now(timezone.utc).date()


def hash_password(word: str, *, n: int = SCRYPT_N, r: int = SCRYPT_R, p: int = SCRYPT_P) -> str:
    """Return the scrypt record of *word*: ``scrypt$n$r$p$<salt>$<hash>``."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(word.encode("utf-8"), salt=salt, n=n, r=r, p=p,
                            maxmem=SCRYPT_MAXMEM, dklen=32)
    return f"scrypt${n}${r}${p}${salt.hex()}${digest.hex()}"


def typed_password(word: str) -> str:
    """The password typed at login without its whitespace (#129).

    Phones add a space after a word and a copy-paste keeps one at the end;
    ``str.split()`` also removes tabs, newlines and no-break spaces.  A stored
    password never holds whitespace (``stx deploy auth`` refuses it).
    """
    return "".join(word.split())


def check_password(record: str, word: str) -> bool:
    """True when *word* matches the scrypt *record* (constant-time comparison)."""
    try:
        algo, n, r, p, salt, digest = record.split("$")
        if algo != "scrypt":
            return False
        got = hashlib.scrypt(word.encode("utf-8"), salt=bytes.fromhex(salt), n=int(n), r=int(r),
                             p=int(p), maxmem=SCRYPT_MAXMEM, dklen=len(digest) // 2)
    except (ValueError, MemoryError):
        return False
    return hmac.compare_digest(got.hex(), digest)


def format_entry(entry: Entry) -> str:
    """The record-file line of *entry*."""
    line = f"{entry.label}:{entry.record}"
    if entry.valid_until is not None:
        line += f":{entry.valid_until.isoformat()}"
    return line


def parse_entry(line: str) -> Entry | None:
    """Parse one record-file line; None when it is not a valid entry."""
    label, record, until = DEFAULT_LABEL, line, None
    if not line.startswith("scrypt$"):
        label, sep, record = line.partition(":")
        if not sep:
            return None
    head, sep, tail = record.rpartition(":")
    if sep and DATE_RE.match(tail):
        record = head
        try:
            until = date.fromisoformat(tail)
        except ValueError:
            return None
    if not LABEL_RE.match(label) or not RECORD_RE.match(record):
        return None
    return Entry(label, record, until)


def parse_records(text: str) -> Records:
    """Parse a record file. Lines that are not valid entries are ignored.

    ``open`` counts only when it is the only entry. A label seen twice keeps
    its first line. Beyond :data:`MAX_ENTRIES` entries, the rest is ignored.
    """
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln and not ln.startswith("#")]
    if lines == ["open"]:
        return Records(open=True)
    entries: list[Entry] = []
    seen: set[str] = set()
    for ln in lines:
        e = parse_entry(ln)
        if e is None or e.label in seen:
            continue
        seen.add(e.label)
        entries.append(e)
        if len(entries) >= MAX_ENTRIES:
            break
    return Records(entries=tuple(entries))


class RecordStore:
    """Reads ``<root>/sites/<site>/pass``, re-parsing a file only when it changes."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._cache: dict[str, tuple[tuple[int, int], Records]] = {}
        self._levels: dict[str, tuple[tuple[int, int], dict]] = {}
        self._lock = threading.Lock()

    def get(self, site: str) -> Records:
        if not SITE_RE.match(site or ""):
            return CLOSED
        path = self.root / "sites" / site / "pass"
        try:
            st = path.stat()
        except OSError:
            return CLOSED
        stamp = (st.st_mtime_ns, st.st_size)
        with self._lock:
            hit = self._cache.get(site)
        if hit is not None and hit[0] == stamp:
            return hit[1]
        try:
            records = parse_records(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return CLOSED
        with self._lock:
            self._cache[site] = (stamp, records)
        return records

    def levels(self, site: str) -> dict[str, tuple[tuple[int, str], ...]] | None:
        """``sites/<site>/levels``: {label: ((from, folder), …)}; None without the file."""
        path = self.root / "sites" / site / "levels"
        try:
            st = path.stat()
        except OSError:
            return None
        stamp = (st.st_mtime_ns, st.st_size)
        with self._lock:
            hit = self._levels.get(site)
        if hit is not None and hit[0] == stamp:
            return hit[1]
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return {}                                  # unreadable: every label closed
        levels = {}
        for line in text.splitlines():
            label, sep, spec = line.strip().partition("\t")
            if not sep or not LABEL_RE.match(label):
                continue
            steps = []
            for part in spec.split(";"):
                when, eq, where = part.rpartition("=")
                if eq and not when.isdigit():
                    steps = None
                    break
                if VIEW_RE.match(where) and ".." not in where:
                    steps.append((int(when) if eq else 0, where))
            levels[label] = tuple(sorted(steps)) if steps else ((0, "closed"),)
        with self._lock:
            self._levels[site] = (stamp, levels)
        return levels

    def view(self, site: str, label: str, now: float | None = None) -> str:
        """The folder *label* sees on *site* now: ``current``, ``closed`` or ``releases/<name>``."""
        if not SITE_RE.match(site or ""):
            return "closed"
        levels = self.levels(site)
        if levels is None:
            return "current"
        moment = now if now is not None else time.time()
        seen = "closed"
        for start, where in levels.get(label, ()):
            if start <= moment:
                seen = where
        return seen


# ---------------------------------------------------------------------------
# Session cookie
# ---------------------------------------------------------------------------


def load_key(root: Path) -> bytes:
    """The server's signing key, created at first start with mode 600."""
    path = root / "conf" / "session.key"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(secrets.token_bytes(32))
    return path.read_bytes()


def _sign(key: bytes, site: str, label: str, expiry: int, gen: str) -> str:
    msg = f"{site}|{label}|{expiry}|{gen}".encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def make_token(key: bytes, site: str, entry: Entry, seconds: int, now: float | None = None) -> str:
    """Session token for *entry*: ``<expiry>.<label>.<generation>.<signature>``."""
    expiry = int(now if now is not None else time.time()) + seconds
    gen = entry.generation
    return f"{expiry}.{entry.label}.{gen}.{_sign(key, site, entry.label, expiry, gen)}"


def check_token(key: bytes, site: str, records: Records, token: str,
                now: float | None = None) -> Entry | None:
    """The entry a valid token belongs to, or None."""
    try:
        expiry_s, label, gen, sig = token.split(".")
        expiry = int(expiry_s)
    except ValueError:
        return None
    if expiry < (now if now is not None else time.time()):
        return None
    entry = records.entry(label)
    if entry is None or entry.expired() or not hmac.compare_digest(gen, entry.generation):
        return None
    if not hmac.compare_digest(sig, _sign(key, site, label, expiry, gen)):
        return None
    return entry


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


PAGE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>{title}</title><style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#14171F;
color:#F2EEE6;font:18px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:16px}}
form{{width:100%;max-width:26rem;display:flex;flex-direction:column;gap:1rem}}
h1{{margin:0;font-size:1.6rem;color:#4FD8C9}}p{{margin:0;color:#9AA5AD}}
input{{font:inherit;padding:.8rem 1rem;border-radius:10px;border:1px solid #2A3242;background:#1F2531;color:#F2EEE6}}
input:focus{{outline:2px solid #4FD8C9;outline-offset:1px}}
button{{font:inherit;font-weight:700;padding:.8rem 1rem;border-radius:10px;border:0;background:#4FD8C9;
color:#14171F;cursor:pointer}}
.err{{color:#EE9187}}</style></head><body>
<form method="post" action="{action}" autocomplete="off">
<h1>{title}</h1><p>{host}</p>{error}
<input type="password" name="password" placeholder="{label}" aria-label="{label}" required autofocus>
<input type="hidden" name="next" value="{next}">
<button type="submit">{button}</button></form></body></html>"""

WORDS = {
    "fr": ("Mot de passe", "Entrer", "Mot de passe incorrect."),
    "en": ("Password", "Enter", "Wrong password."),
}


def login_page(host: str, action: str, nxt: str, lang: str, error: bool) -> bytes:
    label, button, err = WORDS.get(lang, WORDS["en"])
    return PAGE.format(
        lang=lang, title=html.escape(label), host=html.escape(host),
        action=html.escape(action, quote=True), label=html.escape(label),
        button=html.escape(button), next=html.escape(nxt, quote=True),
        error=f'<p class="err">{html.escape(err)}</p>' if error else "",
    ).encode("utf-8")


def safe_path(value: str, fallback: str) -> str:
    """A path on the same site (never ``//elsewhere`` nor ``http…``), else *fallback*."""
    if value and PATH_RE.match(value) and not value.startswith("//") and "/_" not in value.split("?")[0]:
        return value
    return fallback


class AuthServer(ThreadingHTTPServer):
    """Threaded server with a listen backlog sized for a browser's burst (#108)."""

    request_queue_size = 512
    daemon_threads = True

    def __init__(self, address: tuple[str, int], root: Path,
                 session_seconds: int = DEFAULT_SESSION_HOURS * 3600) -> None:
        self.root = root
        self.store = RecordStore(root)
        self.key = load_key(root)
        self.key_tag = hashlib.sha256(self.key).hexdigest()[:8]
        self.session_seconds = session_seconds
        self.scrypt_slots = threading.BoundedSemaphore(MAX_SCRYPT_AT_ONCE)
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    server: AuthServer
    protocol_version = "HTTP/1.1"
    timeout = 60

    def version_string(self) -> str:
        return "stx-auth"

    def log_message(self, format: str, *args) -> None:  # noqa: A002 — nginx logs requests
        pass

    # -- request description (headers set by nginx) --

    def _header(self, name: str, pattern: re.Pattern[str], default: str) -> str:
        value = (self.headers.get(name) or "").strip()
        return value if pattern.match(value) else default

    def site(self) -> str:
        return self._header("X-Stx-Site", SITE_RE, "")

    def cookie_name(self) -> str:
        name = self._header("X-Stx-Cookie", COOKIE_RE, f"stx_session_{self.site()}")
        return f"{name}_{self.server.key_tag}" if self.domain() else name

    def domain(self) -> str:
        """The domain of a shared session (#147): ``X-Stx-Domain``, when the host is one of its sites."""
        value = (self.headers.get("X-Stx-Domain") or "").strip().lower()
        host = self.host().split(":")[0].lower()
        return value if DOMAIN_RE.match(value) and host.endswith("." + value) else ""

    def signed_for(self) -> str:
        return SHARED if self.domain() else self.site()

    def _local_path(self, name: str, default: str) -> str:
        value = (self.headers.get(name) or "").strip()
        return value if PATH_RE.match(value) and not value.startswith("//") else default

    def login_action(self) -> str:
        return self._local_path("X-Stx-Login", "/_login").split("?")[0]

    def home(self) -> str:
        return self._local_path("X-Stx-Home", "/")

    def original_uri(self) -> str:
        """The page as the visitor asked for it: a proxy that stripped a prefix
        (``/html``) sends it in ``X-Forwarded-Prefix``; it is put back so that
        the return after login does not land on the other face."""
        uri = self.headers.get("X-Original-URI", "") or ""
        prefix = (self.headers.get("X-Forwarded-Prefix", "") or "").rstrip("/")
        if prefix and PREFIX_RE.match(prefix) and not uri.startswith(prefix + "/"):
            return prefix + uri
        return uri

    def lang(self) -> str:
        uri = self.headers.get("X-Original-URI", "") or ""
        accept = self.headers.get("Accept-Language", "") or ""
        return "fr" if "/fr/" in uri or "lang=fr" in uri or accept.startswith("fr") else "en"

    def tokens(self) -> list[str]:
        """Every value of the session cookie: a browser may send two (an old host cookie and the
        shared one)."""
        name = self.cookie_name()
        values = []
        for part in (self.headers.get("Cookie") or "").split(";"):
            key, _, value = part.strip().partition("=")
            if key == name:
                values.append(value)
        return values[:4]

    def host(self) -> str:
        return (self.headers.get("Host") or "").split(",")[0].strip()[:253]

    # -- responses --

    def send(self, code: int, body: bytes = b"", headers: dict[str, str] | None = None) -> None:
        self.send_response(code)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def form(self, nxt: str, error: bool) -> None:
        self.send(401, login_page(self.host(), self.login_action(), nxt, self.lang(), error))

    def do_GET(self) -> None:  # noqa: N802 — BaseHTTPRequestHandler API
        path = urlsplit(self.path).path
        site = self.site()
        records = self.server.store.get(site)
        if path == "/check":
            stamp = {"X-Stx-Auth": f"{AUTH_INTERFACE} {STX_VERSION}"}
            if records.open:
                return self.send(204, headers={**stamp, "X-Stx-Label": "open",
                                               "X-Stx-View": self.server.store.view(site, "open")})
            signed = self.signed_for()
            entry = next((e for t in self.tokens()
                          if (e := check_token(self.server.key, signed, records, t)) is not None), None)
            if entry is None:
                return self.send(401, headers=stamp)
            return self.send(204, headers={**stamp, "X-Stx-Label": entry.label,
                                           "X-Stx-View": self.server.store.view(site, entry.label)})
        if path == "/login":
            return self.form(safe_path(self.original_uri(), self.home()), error=False)
        return self.send(404)

    def do_POST(self) -> None:  # noqa: N802 — BaseHTTPRequestHandler API
        if urlsplit(self.path).path != "/login":
            self.close_connection = True
            return self.send(404)
        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            self.close_connection = True
            return self.send(413)
        form = parse_qs(self.rfile.read(length).decode("utf-8", "replace"))
        word = typed_password((form.get("password") or [""])[0])
        nxt = safe_path((form.get("next") or [""])[0], self.home())
        site = self.site()
        records = self.server.store.get(site)
        if records.open:
            return self.send(303, headers={"Location": nxt})
        entry = self._match(records, word)
        if entry is None:
            return self.form(nxt, error=True)
        seconds = self.server.session_seconds
        token = make_token(self.server.key, self.signed_for(), entry, seconds)
        domain = self.domain()
        cookie = (f"{self.cookie_name()}={token}; Path=/; Max-Age={seconds}; "
                  + (f"Domain={domain}; " if domain else "") + "HttpOnly; Secure; SameSite=Lax")
        return self.send(303, headers={"Location": nxt, "Set-Cookie": cookie})

    def _match(self, records: Records, word: str) -> Entry | None:
        """The first unexpired entry whose password is *word*."""
        if not word:
            return None
        today = _today()
        with self.server.scrypt_slots:
            for entry in records.entries:
                if not entry.expired(today) and check_password(entry.record, word):
                    return entry
        return None


def main() -> None:
    root = Path(os.environ.get("STX_AUTH_ROOT", DEFAULT_ROOT))
    port = int(os.environ.get("STX_AUTH_PORT", str(DEFAULT_PORT)))
    hours = float(os.environ.get("STX_AUTH_SESSION_HOURS", str(DEFAULT_SESSION_HOURS)))
    AuthServer(("127.0.0.1", port), root, int(hours * 3600)).serve_forever()


if __name__ == "__main__":
    main()
