"""Passwords per site (#111): ``.stx-passwords.toml``, git-ignored, read in three levels::

    [default]                          # every site
    live = "…"
    html = "COHORT1:pw1,COHORT2:pw2:2026-11-30"

    [CHAT1D]                           # a group of sites (Site.group)
    html = [["PROMO-OCT", "pw1"], ["PROMO-NOV", "pw2", "2026-11-30"]]

    [CHAT1D.sites.chat1d]              # one site
    open = true                        # both faces open; or open = ["html"]

    [admin]                            # added to EVERY site, both faces (#147)
    live = "ADMIN:…"
    html = "ADMIN:…"

    [GAI.sites.gai-slides]             # one line per session, each with its level (#148)
    html = [
      { seance = "S1027", mot = "…", limite = 120, fin = "2026-12-31" },
      { seance = "S1103", mot = "…" },                   # no limit: "not open yet"
      { seance = "S1110", mot = "…", limite = [["2026-11-10T09:00", 50], ["2026-11-10T14:00", "all"]] },
    ]

A face's value uses the library's grammar (``deploy_auth_cmd.parse_password_spec``): one password, a
labelled list as a string, a table, or a list of pairs, each with an optional end date. A later level
overrides an earlier one, face by face. ``open`` is explicit: an empty string is refused, and a face
with no password at any level is an error, never an open site.

``[admin]`` (#147) is not a level: its entries are ADDED to the passwords of every face of every site
(an open face stays open), so the administrator's password is written once. A face given no password at
any level but ``[admin]`` is the administrator's alone. The labels of ``[admin]`` always see the whole
content; ``full = ["PROMO-A"]``, at any level, adds labels that see it too on a site with a slide limit.
No rule is set on what a password contains: only what the login screen could never match is refused.

A face written one line per session (#148, the all-trainings form; English keys ``label``, ``password``,
``limit``, ``until`` too) gives each session its level on the HTML face: ``limite = N`` (slides 1 to N),
``"all"``, a schedule ``[["2026-11-10T09:00", 50], ["2026-11-10T14:00", "all"]]`` (local time of this
machine; ``"none"`` closes), or no ``limite``: the session sees "not open yet". The other forms give
every label the site's level (``stx release limit SITE N``, else all the slides).

One record per (label, password) and per run (``RecordPool``): the same password gets the same record
on every site and face, so one login opens every site that holds it; a record already on the server is
kept while it still matches, so writing the files again closes no session.

``convert`` turns the streamtex-all-trainings prototype's file (``[default] < [TRAINING] <
[TRAINING.kind]``, ``""`` = open) into this one without touching a single password, then checks that
every site gets exactly the same passwords, labels and end dates as before (rel2 formes=a).
"""

from __future__ import annotations

import datetime as dt
import os
import re
import tomllib
from pathlib import Path

import click

from ..cli.deploy_auth_cmd import PlainEntry, _check_entries, parse_password_spec
from ..deploy.stx_auth import Entry, check_password, format_entry, hash_password, parse_entry
from . import ReleaseError
from .config import FACES, ReleaseConfig, Site

PASSWORDS_FILE = ".stx-passwords.toml"
#: Another passwords file (relative to the project root, or absolute), for a rehearsal with dummy
#: passwords that leaves the real file in place (all-trainings, 2026-10-26).
PASSWORDS_ENV = "STX_PASSWORDS_FILE"
OPEN = None          # a face resolved to "open"
_LEVEL_KEYS = {"live", "html", "open", "full"}
ADMIN = "admin"
#: The keys of a session line (#148): all-trainings' and their English aliases.
LINE_KEYS = {"seance": "label", "mot": "password", "limite": "limit", "fin": "until",
             "label": "label", "password": "password", "limit": "limit", "until": "until"}
DEFAULT = "default"        # a label's level: the site's (state up_to_slide), else all the slides


def passwords_path(root: Path) -> Path:
    """The passwords file of the project at *root*: ``$STX_PASSWORDS_FILE`` when set, else
    ``.stx-passwords.toml``."""
    return root / (os.environ.get(PASSWORDS_ENV) or PASSWORDS_FILE)


def load_file(path: Path) -> dict:
    if not path.is_file():
        where = f"at {path}" if os.environ.get(PASSWORDS_ENV) else "at the project root (git-ignored)"
        raise ReleaseError(f"{path.name} not found {where}: it gives, for every "
                           "site, the passwords of the live and html faces, or open = true")
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ReleaseError(f"{path}: {e}") from None


def _level_faces(level: dict, where: str) -> dict:
    """The faces a level sets: {face: raw value | OPEN}."""
    extra = set(level) - _LEVEL_KEYS - {"sites"}
    if extra:
        raise ReleaseError(f"{where}: unknown key(s) {sorted(extra)} — live, html, open")
    out: dict = {}
    for face in FACES:
        if face in level:
            if level[face] == "":
                raise ReleaseError(f"{where}.{face} is an empty string — write open = [\"{face}\"] to open it")
            out[face] = level[face]
    opened = level.get("open", False)
    if opened is True:
        opened = list(FACES)
    if opened is False:
        opened = []
    if not isinstance(opened, list) or any(f not in FACES for f in opened):
        raise ReleaseError(f"{where}.open: true, or a list of faces such as [\"html\"]")
    for face in opened:
        if face in out:
            raise ReleaseError(f"{where}: '{face}' is both open and given a password")
        out[face] = OPEN
    return out


def resolve_raw(data: dict, site: Site) -> dict:
    """{face: raw value | OPEN} after the three levels; faces with nothing are absent."""
    out: dict = {}
    group = data.get(site.group, {}) if isinstance(data.get(site.group), dict) else {}
    sites = group.get("sites", {}) if isinstance(group.get("sites"), dict) else {}
    levels = [("[default]", data.get("default", {})), (f"[{site.group}]", group),
              (f"[{site.group}.sites.{site.site}]", sites.get(site.site, {}))]
    for where, level in levels:
        if isinstance(level, dict):
            out.update(_level_faces(level, where))
    return out


def _limit(value, where: str):
    """A session's level: None (closed), "all", N, or a schedule ((epoch seconds, level), …)."""
    if value is None or value == "none":
        return None
    if value == "all":
        return "all"
    if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
        return value
    if isinstance(value, list) and value:
        steps = []
        for step in value:
            if not (isinstance(step, list) and len(step) == 2):
                raise ReleaseError(f"{where}: a schedule is [[\"YYYY-MM-DDTHH:MM\", N | \"all\" | \"none\"], …]")
            when, level = step
            try:
                moment = when if isinstance(when, dt.datetime) else dt.datetime.fromisoformat(str(when))
            except ValueError:
                raise ReleaseError(f"{where}: {when!r} is not a time (YYYY-MM-DDTHH:MM)") from None
            inner = _limit(level, where)
            if isinstance(inner, tuple):
                raise ReleaseError(f"{where}: a schedule step is N, \"all\" or \"none\"")
            steps.append((int(moment.astimezone().timestamp()), inner))
        return tuple(sorted(steps))
    raise ReleaseError(f"{where}: limite is a slide number (1 or more), \"all\", \"none\" or a schedule")


def _lines(value, where: str) -> tuple[list, dict] | None:
    """A face written one line per session: (its pairs for parse_password_spec, {label: level})."""
    if not (isinstance(value, list) and value and all(isinstance(c, dict) for c in value)):
        return None
    pairs, levels = [], {}
    for c in value:
        line: dict = {}
        for key, v in c.items():
            if key not in LINE_KEYS:
                raise ReleaseError(f"{where}: unknown key '{key}' — seance, mot, limite, fin "
                                   "(or label, password, limit, until)")
            if LINE_KEYS[key] in line:
                raise ReleaseError(f"{where}: '{key}' and its alias are both given")
            line[LINE_KEYS[key]] = v
        label, word = line.get("label"), line.get("password")
        if not isinstance(label, str) or not isinstance(word, str):
            raise ReleaseError(f"{where}: each line needs seance = \"LABEL\" and mot = \"…\"")
        pairs.append([label, word] + ([str(line["until"])] if line.get("until") else []))
        levels[label] = _limit(line.get("limit"), f"{where}.{label}")
    return pairs, levels


def _own(raw, where: str) -> tuple[list[PlainEntry], dict]:
    """The entries of a face's own value and the level of each label."""
    lines = _lines(raw, where)
    try:
        entries = parse_password_spec(lines[0] if lines else raw, where)
    except click.ClickException as e:
        raise ReleaseError(e.message) from None
    return entries, (lines[1] if lines else {e.label: DEFAULT for e in entries})


def _admin(data: dict) -> dict[str, list[PlainEntry]]:
    """The entries ``[admin]`` adds to each face."""
    level = data.get(ADMIN)
    if level is None:
        return {}
    if not isinstance(level, dict) or set(level) - set(FACES):
        raise ReleaseError("[admin]: live and/or html, the administrator's password(s) added to every site")
    out = {}
    for face in FACES:
        if face in level:
            try:
                out[face] = parse_password_spec(level[face], f"[admin].{face}")
            except click.ClickException as e:
                raise ReleaseError(e.message) from None
    return out


def full_labels(data: dict, site: Site) -> frozenset[str]:
    """The labels that see the whole content of *site* when it has a slide limit: ``[admin]``'s and the
    ``full`` list of the last level that sets one."""
    labels: list = []
    group = data.get(site.group, {}) if isinstance(data.get(site.group), dict) else {}
    sites = group.get("sites", {}) if isinstance(group.get("sites"), dict) else {}
    for where, level in (("[default]", data.get("default", {})), (f"[{site.group}]", group),
                         (f"[{site.group}.sites.{site.site}]", sites.get(site.site, {}))):
        if isinstance(level, dict) and "full" in level:
            labels = level["full"]
            if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
                raise ReleaseError(f"{where}.full: a list of password labels, such as [\"PROMO-A\"]")
    return frozenset(labels) | {e.label for e in _admin(data).get("html", [])}


def for_site(data: dict, site: Site) -> dict[str, list[PlainEntry] | None]:
    """The checked passwords of each published face of *site* (``None`` = open)."""
    raw = resolve_raw(data, site)
    admin = _admin(data)
    result: dict[str, list[PlainEntry] | None] = {}
    for face in site.faces:
        if face not in raw and face not in admin:
            raise ReleaseError(f"no '{face}' password for site {site.site} (group {site.group}) in "
                               f"{PASSWORDS_FILE} — an omission never opens a site: write open = [\"{face}\"]")
        if raw.get(face, "") is OPEN:
            result[face] = None
            continue
        own = _own(raw[face], f"{site.site}.{face}")[0] if face in raw else []
        entries = own + admin.get(face, [])
        if own and admin.get(face):
            try:
                _check_entries(entries, f"{site.site}.{face} with [admin]")
            except click.ClickException as e:
                raise ReleaseError(e.message) from None
        result[face] = entries
    return result


def levels_for(data: dict, site: Site) -> dict:
    """What each label sees on the HTML face (#148): {label: None | "all" | N | schedule | DEFAULT}.

    ``[admin]`` and the ``full`` labels see all the slides; an open face: ``{"open": DEFAULT}``."""
    if "html" not in site.faces:
        return {}
    raw = resolve_raw(data, site).get("html")
    if raw is OPEN:
        return {"open": DEFAULT}
    levels = _own(raw, f"{site.site}.html")[1] if raw is not None else {}
    for label in full_labels(data, site):
        if label in levels or label in {e.label for e in _admin(data).get("html", [])}:
            levels[label] = "all"
    return levels


class RecordPool:
    """One record per (label, password) for a run; *existing*: the record files already on the server."""

    def __init__(self, existing: str = "") -> None:
        self._known: dict[str, list[str]] = {}
        for line in existing.splitlines():
            e = parse_entry(line.strip())
            if e is not None and e.record not in self._known.setdefault(e.label, []):
                self._known[e.label].append(e.record)
        self._made: dict[tuple[str, str], str] = {}

    def record(self, label: str, password: str) -> str:
        key = (label, password)
        if key not in self._made:
            self._made[key] = next((r for r in self._known.get(label, []) if check_password(r, password)),
                                   None) or hash_password(password)
        return self._made[key]

    def text(self, entries: list[PlainEntry] | None) -> str:
        if entries is None:
            return "open\n"
        return "".join(format_entry(Entry(e.label, self.record(e.label, e.password), e.valid_until)) + "\n"
                       for e in entries)


def pass_text(entries: list[PlainEntry] | None, pool: RecordPool | None = None) -> str:
    """The record file of a face: ``open``, or one hashed line per password, labels and dates kept."""
    return (pool or RecordPool()).text(entries)


def first_password(entries: list[PlainEntry] | None) -> str:
    """The password ``stx release`` logs in with to check what is served."""
    return entries[0].password if entries else ""


# ---------------------------------------------------------------------------
# The prototype's file → this grammar (rel2 formes=a)
# ---------------------------------------------------------------------------

def _old_value(level: dict, face: str):
    v = level.get(face) if isinstance(level, dict) else None
    return v if isinstance(v, (str, dict, list)) else None


def _old_resolved(old: dict, site: Site) -> dict:
    """The prototype's levels for (training, kind) = site.legacy; "" = open."""
    training, kind = site.legacy
    group = old.get(training, {}) if isinstance(old.get(training), dict) else {}
    out: dict = {}
    for level in (old.get("default", {}), group, group.get(kind, {}) if isinstance(group.get(kind), dict) else {}):
        for face in FACES:
            v = _old_value(level, face)
            if v is not None:
                out[face] = OPEN if v == "" else v
    return out


def _new_level(level: dict) -> dict:
    out: dict = {}
    opened = []
    for face in FACES:
        v = _old_value(level, face)
        if v == "":
            opened.append(face)
        elif v is not None:
            out[face] = v
    if opened:
        out["open"] = True if len(opened) == 2 else opened
    return out


def _normalize(raw: dict, faces: tuple[str, ...], where: str) -> dict:
    """{face: OPEN | "<missing>" | (sorted (label, password, end date), sorted (label, level))}."""
    out = {}
    for face in faces:
        v = raw.get(face, "<missing>")
        if v is OPEN or v == "<missing>":
            out[face] = v
            continue
        entries, levels = _own(v, f"{where}.{face}")
        out[face] = (sorted((e.label, e.password, e.valid_until) for e in entries),
                     sorted((label, repr(level)) for label, level in levels.items()))
    return out


def convert(cfg: ReleaseConfig, old_path: Path, new_path: Path) -> list[str]:
    """Write *new_path* from the prototype's *old_path*; returns the report lines (never a password)."""
    if new_path.exists():
        raise ReleaseError(f"{new_path} already exists — choose another --to or remove it first")
    old = load_file(old_path)
    without = [s.site for s in cfg.sites if not s.legacy]
    if without:
        raise ReleaseError("convert-passwords needs legacy = [training, kind] on every site; missing for: "
                           + ", ".join(without))
    by_legacy = {s.legacy: s for s in cfg.sites}
    new: dict = {}
    if isinstance(old.get("default"), dict):
        new["default"] = _new_level(old["default"])
    unmapped: list[str] = []
    for key, table in old.items():
        if key == "default" or not isinstance(table, dict):
            continue
        group = _new_level(table)
        for sub, level in table.items():
            if sub in FACES or not isinstance(level, dict):
                continue
            site = by_legacy.get((key, sub))
            if site is None:
                unmapped.append(f"[{key}.{sub}]")
                continue
            if site.group != key:
                raise ReleaseError(f"site {site.site}: group '{site.group}' but the old file puts it under "
                                   f"[{key}] — set group = \"{key}\" so that it inherits the same passwords")
            group.setdefault("sites", {})[site.site] = _new_level(level)
        new[key] = group
    if unmapped:
        raise ReleaseError("no site for " + ", ".join(unmapped) + " (legacy = [training, kind] in the site list)")
    # The proof: every site gets the same passwords, labels and dates as before.
    report: list[str] = []
    problems: list[str] = []
    for site in cfg.sites:
        before = _normalize(_old_resolved(old, site), site.faces, f"{site.site} (old)")
        try:
            after = _normalize(resolve_raw(new, site), site.faces, f"{site.site} (new)")
        except ReleaseError as e:
            problems.append(str(e.message))
            continue
        for face in site.faces:
            if before[face] != after[face]:
                problems.append(f"{site.site}.{face}: not the same passwords after conversion")
            elif before[face] == "<missing>":
                problems.append(f"{site.site}.{face}: no password in the old file either")
            elif before[face] is not OPEN:
                try:
                    _check_entries([PlainEntry(lb, pw, d) for lb, pw, d in before[face][0]], f"{site.site}.{face}")
                except click.ClickException as e:
                    problems.append(e.message)
        report.append(f"{site.site}: " + ", ".join(
            f"{face} {'open' if after.get(face) is OPEN else f'{len(after[face][0])} password(s)'}"
            for face in site.faces if after.get(face) != "<missing>")
            + ("" if not isinstance(after.get("html"), tuple) else
               " — levels: " + ", ".join(f"{lb} {lvl}" for lb, lvl in after["html"][1] if lvl != repr(DEFAULT))))
    if problems:
        raise ReleaseError("conversion refused, nothing written:\n  " + "\n  ".join(problems))
    new_path.write_text(dumps(new), encoding="utf-8")
    new_path.chmod(0o600)
    return report


# ---------------------------------------------------------------------------
# A small TOML writer for this file's shapes
# ---------------------------------------------------------------------------

_BARE = re.compile(r"^[A-Za-z0-9_-]+$")


def _key(k: str) -> str:
    return k if _BARE.match(k) else _str(k)


def _str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t") + '"'


def _value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return _str(v)
    if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
        return "[\n" + "".join(f"  {_value(x)},\n" for x in v) + "]"        # one session per line (#148)
    if isinstance(v, list):
        return "[" + ", ".join(_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{_key(k)} = {_value(x)}" for k, x in v.items()) + " }"
    if hasattr(v, "isoformat"):
        return v.isoformat()
    raise ReleaseError(f"cannot write {type(v).__name__} in {PASSWORDS_FILE}")


def dumps(data: dict) -> str:
    lines = ["# .stx-passwords.toml — written by `stx release convert-passwords`; git-ignored, never committed.", ""]

    def table(name: str, t: dict) -> None:
        lines.append(f"[{name}]")
        for k, v in t.items():
            if k != "sites":
                lines.append(f"{_key(k)} = {_value(v)}")
        lines.append("")
        for site, st in t.get("sites", {}).items():
            table(f"{name}.sites.{_key(site)}", st)

    for name, t in data.items():
        table(_key(name), t)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# `stx release limit SITE N --label L`: the session's line, its `limite` alone (#148)
# ---------------------------------------------------------------------------

_LIMIT_VALUE = r'(?:\d+|"[^"]*"|\[\[.*?\]\])'


def _section_span(text: str, site: Site) -> tuple[int, int] | None:
    """Where the site's own section ``[group.sites.site]`` starts and ends in *text*."""
    name = r'\s*\.\s*'.join(rf'(?:"{re.escape(p)}"|{re.escape(p)})' for p in (site.group, "sites", site.site))
    m = re.search(rf"^\[\s*{name}\s*\]\s*$", text, flags=re.M)
    if not m:
        return None
    nxt = re.search(r"^\s*\[", text[m.end():], flags=re.M)
    return m.end(), m.end() + nxt.start() if nxt else len(text)


def write_limit(path: Path, site: Site, labels: list[str], value) -> list[str]:
    """Set ``limite`` (N, "all", or None: removed, "not open yet") on the line of each label in the site's
    own section of *path*, touching nothing else; returns what changed (labels and levels, never a
    password). The file is checked again before it is written."""
    text = path.read_text(encoding="utf-8")
    span = _section_span(text, site)
    where = f"[{site.group}.sites.{site.site}]"
    if span is None:
        raise ReleaseError(f"{site.site}: no section {where} in {path.name} — the levels are per document: "
                           f"put the site's html lines there, one per session")
    start, end = span
    section = text[start:end]
    changes = []
    for label in labels:
        line = re.search(rf'\{{[^{{}}\n]*\b(seance|label)\s*=\s*"{re.escape(label)}"[^{{}}\n]*\}}', section)
        if not line:
            raise ReleaseError(f"{site.site}: no line for session {label} in {where} — add "
                               f'{{ seance = "{label}", mot = "…", limite = N }} to its html list')
        table = line.group(0)
        key = "limite" if line.group(1) == "seance" else "limit"
        old = re.search(rf"\b(limite|limit)\s*=\s*({_LIMIT_VALUE})", table)
        if value is None:
            new_table = re.sub(rf",\s*\b(limite|limit)\s*=\s*{_LIMIT_VALUE}|\b(limite|limit)\s*=\s*"
                               rf"{_LIMIT_VALUE}\s*,?\s*", "", table, count=1)
        else:
            literal = str(value) if isinstance(value, int) else f'"{value}"'
            new_table = (table[:old.start(2)] + literal + table[old.end(2):] if old
                         else re.sub(r"\s*\}$", f", {key} = {literal} }}", table))
        section = section[:line.start()] + new_table + section[line.end():]
        changes.append(f"{label}: {old.group(2) if old else 'not open yet'} → "
                       f"{value if value is not None else 'not open yet'}")
    new_text = text[:start] + section + text[end:]
    try:
        data = tomllib.loads(new_text)
    except tomllib.TOMLDecodeError as e:
        raise ReleaseError(f"{path.name}: the change would break the file ({e}) — nothing written") from None
    got = levels_for(data, site)
    for label in labels:
        if got.get(label) != value:
            raise ReleaseError(f"{site.site}: {label} would be {got.get(label)!r}, not {value!r} — nothing "
                               "written (is its line given at another level too?)")
    path.write_text(new_text, encoding="utf-8")
    return changes
