"""Access control of deployed projects: ``stx deploy lock / unlock / passwd / auth-status`` (#10, #104).

An extensible registry of authentication modes, each one able to enable,
disable and report itself on a Coolify application:

| Mode           | Level       | Applies with | What it sets                                  |
|----------------|-------------|--------------|-----------------------------------------------|
| ``session``    | proxy       | restart      | ``STX_AUTH_LIVE`` / ``STX_AUTH_HTML`` (hashes) |
| ``stx-password`` | application | restart    | ``STX_PASSWORD`` (the keypad)                  |
| ``basic``      | proxy       | restart      | Coolify's HTTP Basic Authentication            |

``session`` is the server-side login screen: passwords are read from
``.stx-passwords.toml`` (git-ignored), hashed on this machine with scrypt, and
only the records reach Coolify. When it guards the app, the keypad is not
shown (one prompt only).

``.stx-passwords.toml``::

    [default]                       # or a section named after the service
    live = "apassword"              # one password, label "default"
    html = "COHORT1:pw1,COHORT2:pw2"  # labelled passwords

    [default.live]                  # the same as a table (needed when a
    COHORT1 = "pw1"                 # password contains ':' or ',')
    COHORT2 = { password = "pw2", valid_until = "2027-01-31" }

An end date may also follow a password as ``:YYYY-MM-DD`` (``"COHORT1:pw1:2027-01-31"``,
``COHORT1 = "pw1:2027-01-31"``), and a list of pairs is accepted:
``[["COHORT1", "pw1"], ["COHORT2", "pw2", "2027-01-31"]]`` — the writings of the
streamtex-all-trainings prototype, kept for stx release (#136).

A password holds no whitespace: the login screen removes the spaces typed
(phones add one after a word), so a stored one could never match (#129).
"""

from __future__ import annotations

import base64
import re
import subprocess
import tomllib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import click

from ..deploy.stx_auth import LABEL_RE, Entry, format_entry, hash_password, parse_records
from .console import get_console

PASSWORDS_FILE = ".stx-passwords.toml"
FACES = ("live", "html")
FACE_ENV = {"live": "STX_AUTH_LIVE", "html": "STX_AUTH_HTML"}
MAX_PASSWORDS = 32  # tried one by one at login: 32 x ~31 ms


# ---------------------------------------------------------------------------
# Password lists (.stx-passwords.toml)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlainEntry:
    """A password as the author wrote it (never sent anywhere)."""

    label: str
    password: str
    valid_until: date | None = None


def _parse_date(value: object, where: str) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as e:
        raise click.ClickException(f"{where}: valid_until must be a date (YYYY-MM-DD), got {value!r}") from e


_DATED_RE = re.compile(r"^(.*):(\d{4}-\d{2}-\d{2})$")


def _dated(label: str, word: str, where: str) -> PlainEntry:
    """A labelled password whose word may end with ``:YYYY-MM-DD`` (its end date)."""
    m = _DATED_RE.match(word)
    if m:
        return PlainEntry(label, m.group(1), _parse_date(m.group(2), f"{where}.{label}"))
    return PlainEntry(label, word)


def parse_password_spec(spec: object, where: str) -> list[PlainEntry]:
    """Read one face's passwords: a string, a table or a list of pairs, see the module docstring."""
    entries: list[PlainEntry] = []
    if isinstance(spec, str):
        if ":" not in spec:
            entries.append(PlainEntry("default", spec))
        else:
            for pair in spec.split(","):
                label, sep, password = pair.strip().partition(":")
                if not sep:
                    raise click.ClickException(f"{where}: '{pair.strip()}' is not label:password")
                entries.append(_dated(label.strip(), password, where))
    elif isinstance(spec, dict):
        for label, value in spec.items():
            if isinstance(value, str):
                entries.append(_dated(label, value, where))
            elif isinstance(value, dict) and isinstance(value.get("password"), str):
                until = value.get("valid_until")
                entries.append(PlainEntry(label, value["password"],
                                          _parse_date(until, f"{where}.{label}") if until else None))
            else:
                raise click.ClickException(f"{where}.{label}: expected a password or {{ password = ... }}")
    elif isinstance(spec, list):
        for item in spec:
            if not (isinstance(item, list) and len(item) in (2, 3) and all(isinstance(x, str) for x in item)):
                raise click.ClickException(f"{where}: a list of passwords holds pairs "
                                           f"[\"LABEL\", \"password\"] (a 3rd item: the end date YYYY-MM-DD)")
            until = _parse_date(item[2], f"{where}.{item[0]}") if len(item) == 3 else None
            entries.append(PlainEntry(item[0], item[1], until))
    else:
        raise click.ClickException(f"{where}: expected a string, a table or a list of pairs")
    _check_entries(entries, where)
    return entries


def _check_entries(entries: list[PlainEntry], where: str) -> None:
    if not entries:
        raise click.ClickException(f"{where}: no password")
    if len(entries) > MAX_PASSWORDS:
        raise click.ClickException(f"{where}: {len(entries)} passwords; at most {MAX_PASSWORDS} "
                                   "(each one is tried at login)")
    labels: set[str] = set()
    passwords: dict[str, str] = {}
    for e in entries:
        if not LABEL_RE.match(e.label):
            raise click.ClickException(f"{where}: label '{e.label}' (letters, digits, '-' and '_' only)")
        if e.label in labels:
            raise click.ClickException(f"{where}: label '{e.label}' appears twice")
        if not e.password:
            raise click.ClickException(f"{where}.{e.label}: empty password")
        if any(c.isspace() for c in e.password):
            raise click.ClickException(
                f"{where}.{e.label}: the password contains whitespace; the login screen "
                "removes whitespace before checking, so it could never match")
        if e.password in passwords:
            raise click.ClickException(
                f"{where}: '{e.label}' and '{passwords[e.password]}' share a password; "
                "the server could not tell them apart")
        labels.add(e.label)
        passwords[e.password] = e.label


def load_passwords(path: Path, section: str | None, faces: tuple[str, ...]) -> dict[str, list[PlainEntry]]:
    """The passwords of each face in *faces*, from *section* or ``[default]``."""
    if not path.is_file():
        raise click.ClickException(f"{path} not found. Write the passwords there (git-ignored), "
                                   "see 'stx deploy lock --help'.")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise click.ClickException(f"{path}: {e}") from e
    name = section if section and section in data else "default"
    table = data.get(name)
    if not isinstance(table, dict):
        raise click.ClickException(f"{path}: no [{section or 'default'}] section (nor [default])")
    result = {}
    for face in faces:
        if face not in table:
            raise click.ClickException(f"{path}: [{name}] has no '{face}' passwords")
        result[face] = parse_password_spec(table[face], f"[{name}].{face}")
    return result


def records_text(entries: list[PlainEntry]) -> str:
    """The record file of a face: one hashed line per password, labels kept."""
    return "".join(format_entry(Entry(e.label, hash_password(e.password), e.valid_until)) + "\n"
                   for e in entries)


def encode_face(entries: list[PlainEntry] | None) -> str:
    """The value of ``STX_AUTH_<FACE>``: ``open``, or the base64 of the records."""
    if entries is None:
        return "open"
    return base64.b64encode(records_text(entries).encode()).decode()


def describe_face(value: str | None) -> str:
    """What a ``STX_AUTH_<FACE>`` value means, without any secret."""
    if value is None:
        return "off"
    if value == "open":
        return "open"
    try:
        records = parse_records(base64.b64decode(value, validate=True).decode())
    except ValueError:
        return "closed (unreadable value)"
    if not records.entries:
        return "closed (no valid entry)"
    parts = []
    for e in records.entries:
        tag = e.label
        if e.valid_until:
            tag += f" until {e.valid_until.isoformat()}" + (" (expired)" if e.expired() else "")
        parts.append(tag)
    return f"password ({len(parts)}: {', '.join(parts)})"


def _warn_if_tracked(path: Path, console) -> None:
    """Warn when the passwords file is not ignored by git."""
    try:
        r = subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=path.parent,
                           capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return
    if r.returncode == 1:
        console.print(f"[yellow]⚠ {path.name} is not git-ignored: add it to .gitignore "
                      "(it holds plain passwords)[/yellow]")


# ---------------------------------------------------------------------------
# Mode registry
# ---------------------------------------------------------------------------


@dataclass
class AuthContext:
    """What a mode needs to act on one application."""

    client: object
    uuid: str
    name: str
    project: Path
    console: object
    options: dict = field(default_factory=dict)

    def env(self) -> dict[str, str]:
        """The application's environment (production values, previews ignored)."""
        out: dict[str, str] = {}
        for e in self.client.get_env_vars(self.uuid):
            if not e.get("is_preview") and e.get("key"):
                out[e["key"]] = e.get("value") or e.get("real_value") or ""
        return out


class AuthMode(ABC):
    """One way of protecting a deployed application."""

    name: str = ""
    level: str = ""           # "proxy" or "application"
    instant: bool = False     # True when no restart is needed
    summary: str = ""

    @abstractmethod
    def enable(self, ctx: AuthContext) -> None: ...

    @abstractmethod
    def disable(self, ctx: AuthContext) -> None: ...

    @abstractmethod
    def status(self, ctx: AuthContext, env: dict[str, str]) -> str:
        """One line: ``off``, or what is enabled (never a secret)."""


AUTH_MODES: dict[str, AuthMode] = {}


def register_auth_mode(mode: AuthMode) -> AuthMode:
    """Add *mode* to the registry (also for modes defined outside the library)."""
    AUTH_MODES[mode.name] = mode
    return mode


class SessionMode(AuthMode):
    name = "session"
    level = "proxy"
    summary = "server-side login screen on / and /html/ (one cookie per face)"

    def enable(self, ctx: AuthContext) -> None:
        faces = ctx.options.get("faces") or FACES
        path = ctx.project / ctx.options.get("file", PASSWORDS_FILE)
        passwords = load_passwords(path, ctx.options.get("section") or ctx.name, faces)
        _warn_if_tracked(path, ctx.console)
        for face in FACES:
            value = encode_face(passwords.get(face)) if face in faces else "open"
            ctx.client.set_env_var(ctx.uuid, FACE_ENV[face], value, is_literal=True)
            ctx.console.print(f"  {face}: {describe_face(value)}")
        if ctx.env().get("STX_PASSWORD") and "live" in faces:
            ctx.console.print("[yellow]⚠ STX_PASSWORD is set: the keypad will not be shown, "
                              "the login screen replaces it[/yellow]")

    def disable(self, ctx: AuthContext) -> None:
        for face in FACES:
            ctx.client.delete_env_var(ctx.uuid, FACE_ENV[face])

    def status(self, ctx: AuthContext, env: dict[str, str]) -> str:
        if not any(FACE_ENV[f] in env for f in FACES):
            return "off"
        # The entrypoint closes a face left without a value once one is set.
        return "; ".join(
            f"{face}: {describe_face(env.get(FACE_ENV[face])) if FACE_ENV[face] in env else 'closed'}"
            for face in FACES)


class StxPasswordMode(AuthMode):
    name = "stx-password"
    level = "application"
    summary = "the keypad inside the Streamlit app (STX_PASSWORD; /html/ stays open)"

    def enable(self, ctx: AuthContext) -> None:
        password = ctx.options.get("password") or click.prompt("Keypad sequence (A-Z, 0-9)", hide_input=True)
        ctx.client.set_env_var(ctx.uuid, "STX_PASSWORD", password)
        env = ctx.env()
        if any(FACE_ENV[f] in env for f in FACES) and env.get("STX_AUTH_LIVE") != "open":
            ctx.console.print("[yellow]⚠ The login screen (session) protects the app: "
                              "the keypad will not be shown while it is on[/yellow]")

    def disable(self, ctx: AuthContext) -> None:
        ctx.client.delete_env_var(ctx.uuid, "STX_PASSWORD")

    def status(self, ctx: AuthContext, env: dict[str, str]) -> str:
        if not env.get("STX_PASSWORD"):
            return "off"
        if any(FACE_ENV[f] in env for f in FACES) and env.get("STX_AUTH_LIVE") != "open":
            return "set, not shown (the login screen replaces it)"
        return "on"


class BasicMode(AuthMode):
    """Coolify's HTTP Basic Authentication.

    Coolify's OpenAPI lists these fields only for creation, but its PATCH
    accepts them (Coolify 4.0.0-beta.468, tried 2026-10-11). Turning it off
    sends only ``is_http_basic_auth_enabled=false``: Coolify refuses an empty
    user name or password, so the stored pair stays, inactive. The result is
    read back, in case another Coolify ignores the change.
    """

    name = "basic"
    level = "proxy"
    summary = "Coolify's HTTP Basic Authentication (browser pop-up, one user)"

    _FIELDS = ("is_http_basic_auth_enabled", "http_basic_auth_username", "http_basic_auth_password")

    def _apply(self, ctx: AuthContext, body: dict) -> None:
        from .coolify import CoolifyError

        try:
            ctx.client.update_app(ctx.uuid, **body)
            app = ctx.client.get_app_raw(ctx.uuid)
        except CoolifyError as e:
            raise click.ClickException(
                f"Coolify refused the HTTP Basic Authentication change ({e}). "
                "Its API documents these fields only when an application is created; "
                "set it in the Coolify dashboard (Configuration > General).") from e
        if bool(app.get("is_http_basic_auth_enabled")) != body["is_http_basic_auth_enabled"]:
            raise click.ClickException(
                "Coolify accepted the request but did not change HTTP Basic Authentication: "
                "this Coolify does not allow it through its API. Set it in the dashboard "
                "(Configuration > General).")

    def enable(self, ctx: AuthContext) -> None:
        user = ctx.options.get("user") or click.prompt("User name")
        password = ctx.options.get("password") or click.prompt("Password", hide_input=True)
        self._apply(ctx, {"is_http_basic_auth_enabled": True,
                          "http_basic_auth_username": user, "http_basic_auth_password": password})

    def disable(self, ctx: AuthContext) -> None:
        self._apply(ctx, {"is_http_basic_auth_enabled": False})

    def status(self, ctx: AuthContext, env: dict[str, str]) -> str:
        from .coolify import CoolifyError

        try:
            app = ctx.client.get_app_raw(ctx.uuid)
        except CoolifyError:
            return "unknown"
        if not app.get("is_http_basic_auth_enabled"):
            return "off"
        return f"on (user {app.get('http_basic_auth_username') or '?'})"


for _mode in (SessionMode(), StxPasswordMode(), BasicMode()):
    register_auth_mode(_mode)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _modes(value: str, allow_all: bool) -> list[AuthMode]:
    names = [n.strip() for n in value.split(",") if n.strip()]
    if allow_all and names == ["all"]:
        return list(AUTH_MODES.values())
    unknown = [n for n in names if n not in AUTH_MODES]
    if unknown or not names:
        raise click.BadParameter(f"unknown mode {', '.join(unknown) or value!r}; "
                                 f"choose from {', '.join(AUTH_MODES)}" + (" or all" if allow_all else ""))
    return [AUTH_MODES[n] for n in names]


def _faces(value: str) -> tuple[str, ...]:
    faces = tuple(f.strip() for f in value.split(",") if f.strip())
    if not faces or any(f not in FACES for f in faces):
        raise click.BadParameter(f"faces are {', '.join(FACES)}")
    return faces


def _context(target: str | None, path: str, options: dict) -> AuthContext:
    from .coolify import CoolifyClient, CoolifyError
    from .deploy_cmd import _print_credential_sources, _resolve_target

    console = get_console()
    try:
        client = CoolifyClient.from_env()
    except CoolifyError as e:
        raise click.ClickException(str(e)) from e
    _print_credential_sources(console, client)
    uuid, name = _resolve_target(client, target, console)
    return AuthContext(client, uuid, name, Path(path), console, options)


def _restart(ctx: AuthContext, restart: bool) -> None:
    if not restart:
        ctx.console.print("[yellow]Not restarted: the change applies at the next restart "
                          f"(stx deploy update {ctx.name} --quick)[/yellow]")
        return
    from .coolify import load_typed_state

    uuids = [ctx.uuid]
    for entry in load_typed_state().applications or []:
        if entry.uuid == ctx.uuid and entry.replica_uuids:
            uuids.extend(entry.replica_uuids)
    for uid in uuids:
        result = ctx.client.restart(uid)
        if not result.success:
            raise click.ClickException(f"Restart failed for {uid}: {result.message}")
    ctx.console.print(f"[green]✓ Restart queued ({len(uuids)} container{'s' if len(uuids) > 1 else ''})[/green]")


_common = [
    click.argument("target", required=False, default=None),
    click.option("--path", default=".", show_default=True, help="Project directory (for .stx-passwords.toml)."),
    click.option("--no-restart", is_flag=True, help="Change the settings without restarting."),
    click.option("--yes", is_flag=True, help="Skip the confirmation."),
]


def _with_common(f):
    for decorator in reversed(_common):
        f = decorator(f)
    return f


@click.command("lock")
@_with_common
@click.option("--mode", "mode_names", default="session", show_default=True,
              help="Mode(s), comma-separated: session, stx-password, basic.")
@click.option("--faces", default="live,html", show_default=True,
              help="session: faces to protect (live = /, html = /html/); the others stay open.")
@click.option("--file", "file_name", default=PASSWORDS_FILE, show_default=True,
              help="session: passwords file, relative to --path.")
@click.option("--section", default=None, help="session: section of the file (default: the service name, "
                                               "then [default]).")
@click.option("--user", default=None, help="basic: user name (prompted if omitted).")
@click.option("--password", default=None,
              help="stx-password / basic: the password (prompted if omitted, which keeps it out of the "
                   "shell history).")
def lock_cmd(target, path, no_restart, yes, mode_names, faces, file_name, section, user, password):
    """Protect a deployed application.

    The default mode, session, puts a login screen in front of both faces:
    passwords come from .stx-passwords.toml, are hashed here, and only the
    hashes reach Coolify. Needs deployment files generated by streamtex >= 0.7.44.
    """
    modes = _modes(mode_names, allow_all=False)
    ctx = _context(target, path, {"faces": _faces(faces), "file": file_name, "section": section,
                                  "user": user, "password": password})
    if not yes and not click.confirm(f"Lock {ctx.name} with {', '.join(m.name for m in modes)}?", default=True):
        return
    for mode in modes:
        ctx.console.print(f"[cyan]{mode.name}[/cyan]: {mode.summary}")
        mode.enable(ctx)
    _restart(ctx, not no_restart)


@click.command("unlock")
@_with_common
@click.option("--mode", "mode_names", default="all", show_default=True,
              help="Mode(s) to turn off, comma-separated, or all.")
def unlock_cmd(target, path, no_restart, yes, mode_names):
    """Remove access control from a deployed application."""
    modes = _modes(mode_names, allow_all=True)
    ctx = _context(target, path, {})
    env = ctx.env()
    active = [m for m in modes if m.status(ctx, env) != "off"]
    if not active:
        ctx.console.print("Nothing to unlock.")
        return
    if not yes and not click.confirm(f"Unlock {ctx.name} ({', '.join(m.name for m in active)})?", default=True):
        return
    for mode in active:
        mode.disable(ctx)
        ctx.console.print(f"[green]✓ {mode.name} off[/green]")
    _restart(ctx, not no_restart)


@click.command("passwd")
@_with_common
@click.option("--faces", default="live,html", show_default=True, help="Faces to protect; the others stay open.")
@click.option("--file", "file_name", default=PASSWORDS_FILE, show_default=True, help="Passwords file.")
@click.option("--section", default=None, help="Section of the file (default: the service name, then [default]).")
def passwd_cmd(target, path, no_restart, yes, faces, file_name, section):
    """Re-apply .stx-passwords.toml to the login screen (session mode).

    Removing an entry ends only its sessions; changing a password ends the
    sessions opened with the old one.
    """
    ctx = _context(target, path, {"faces": _faces(faces), "file": file_name, "section": section})
    if not yes and not click.confirm(f"Apply {file_name} to {ctx.name}?", default=True):
        return
    AUTH_MODES["session"].enable(ctx)
    _restart(ctx, not no_restart)


@click.command("auth-status")
@click.argument("target", required=False, default=None)
def auth_status_cmd(target):
    """Show every access-control mode of a deployed application (never a secret)."""
    from rich.table import Table

    ctx = _context(target, ".", {})
    env = ctx.env()
    table = Table(title=f"Access control for {ctx.name}")
    table.add_column("Mode", style="cyan")
    table.add_column("Level")
    table.add_column("Status")
    table.add_column("Applies with")
    for mode in AUTH_MODES.values():
        table.add_row(mode.name, mode.level, mode.status(ctx, env), "at once" if mode.instant else "restart")
    ctx.console.print(table)
