"""``stx run --set``: run the documents of a multi-document project together (#91).

The launcher both large projects wrote for themselves (sumvadis
``run-postair.py``, 396 lines; all-trainings ``run-trainings.py``, 366 lines,
a copy of the first): fixed ports, background servers, cross-document links,
targeted kill, fresh restart, projection browser.

Declared in the project's ``stx.toml``::

    [[run.documents]]
    id = "opening"                                   # → $STX_URL_OPENING for every document
    book = "modules/postair_opening/book.py"
    port = 8731

    [[run.documents]]
    id = "survey"
    book = "modules/postair_survey/book.py"
    port = 8732

State lives in ``.stx_run/`` (one ``<id>.json`` and ``<id>.log`` per
document) next to ``stx.toml``.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path

import click

STATE_DIR = ".stx_run"


@dataclass
class Document:
    id: str
    book: Path
    port: int

    @property
    def env_key(self) -> str:
        return "STX_URL_" + self.id.upper().replace("-", "_")

    def url(self, lang: str | None = None) -> str:
        url = f"http://localhost:{self.port}"
        return f"{url}/?lang={lang}" if lang else url


def find_project_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for d in (cur, *cur.parents):
        if (d / "stx.toml").is_file():
            return d
    raise click.ClickException("No stx.toml found here or above — `stx run --set` needs [[run.documents]].")


def load_documents(root: Path, offset: int = 0) -> list[Document]:
    with open(root / "stx.toml", "rb") as f:
        entries = tomllib.load(f).get("run", {}).get("documents", [])
    if not entries:
        raise click.ClickException(
            f"{root / 'stx.toml'} declares no [[run.documents]] (id, book, port).")
    docs, seen_ids, seen_ports = [], set(), set()
    for i, e in enumerate(entries):
        try:
            doc = Document(str(e["id"]), (root / e["book"]).resolve(), int(e["port"]) + offset)
        except (KeyError, TypeError, ValueError) as exc:
            raise click.ClickException(f"[[run.documents]] #{i + 1}: needs id, book and port ({exc})") from exc
        if doc.id in seen_ids or doc.port in seen_ports:
            raise click.ClickException(f"[[run.documents]]: duplicate id or port for {doc.id!r} ({doc.port})")
        if not doc.book.is_file():
            raise click.ClickException(f"[[run.documents]] {doc.id!r}: book not found: {doc.book}")
        seen_ids.add(doc.id)
        seen_ports.add(doc.port)
        docs.append(doc)
    return docs


def select(docs: list[Document], ids: tuple[str, ...]) -> list[Document]:
    if not ids:
        return docs
    known = {d.id: d for d in docs}
    missing = [i for i in ids if i not in known]
    if missing:
        raise click.ClickException(f"unknown document(s): {', '.join(missing)} (known: {', '.join(known)})")
    return [known[i] for i in ids]


def _state(root: Path, doc: Document) -> Path:
    return root / STATE_DIR / f"{doc.id}.json"


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def running_pid(root: Path, doc: Document) -> int | None:
    path = _state(root, doc)
    if not path.is_file():
        return None
    try:
        pid = int(json.loads(path.read_text())["pid"])
    except (ValueError, KeyError, OSError):
        return None
    return pid if _alive(pid) else None


def _port_busy(port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def stop(root: Path, doc: Document) -> bool:
    """Stop *doc*: its recorded process group, then whatever holds its port."""
    from .run_cmd import _kill_port

    stopped = False
    pid = running_pid(root, doc)
    if pid:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            stopped = True
        except (OSError, ProcessLookupError):
            pass
    _state(root, doc).unlink(missing_ok=True)
    if _port_busy(doc.port):
        stopped = _kill_port(doc.port) or stopped
    return stopped


def start(root: Path, docs_all: list[Document], doc: Document, *, fresh: bool = False) -> str:
    """Start *doc* in the background; returns ``started`` / ``running`` / an error."""
    if fresh:
        stop(root, doc)
        shutil.rmtree(doc.book.parent / ".stx_cache", ignore_errors=True)
    if running_pid(root, doc):
        return "running"
    if _port_busy(doc.port):
        return f"port {doc.port} busy (another program) — use --kill or --fresh"
    (root / STATE_DIR).mkdir(exist_ok=True)
    env = {**os.environ, **{d.env_key: d.url() for d in docs_all}}
    # The project's own .venv when it has one (no implicit `uv run` sync while
    # documents start), else `uv run`, else this interpreter.
    venv_python = root / ".venv" / "bin" / "python"
    uv = shutil.which("uv")
    if venv_python.exists():
        launcher = [str(venv_python), "-m", "streamlit", "run"]
    elif uv:
        launcher = [uv, "run", "streamlit", "run"]
    else:
        launcher = [sys.executable, "-m", "streamlit", "run"]
    cmd = launcher + [doc.book.name, "--server.port", str(doc.port), "--server.headless", "true"]
    log = open(root / STATE_DIR / f"{doc.id}.log", "w", encoding="utf-8")  # noqa: SIM115 — handed to the child
    proc = subprocess.Popen(cmd, cwd=doc.book.parent, env=env, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True)
    _state(root, doc).write_text(json.dumps({"pid": proc.pid, "port": doc.port, "book": str(doc.book),
                                             "started": time.strftime("%Y-%m-%dT%H:%M:%S")}))
    return "started"


def open_urls(urls: list[str], chrome_profile: str | None) -> None:
    """Open *urls*; with *chrome_profile*, in a dedicated Chrome allowed to autoplay media."""
    if chrome_profile:
        flags = [f"--user-data-dir={os.path.expanduser(chrome_profile)}",
                 "--autoplay-policy=no-user-gesture-required", "--new-window"]
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-na", "Google Chrome", "--args", *flags, *urls])
            return
        chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
        if chrome:
            subprocess.Popen([chrome, *flags, *urls])
            return
    import webbrowser

    for url in urls:
        webbrowser.open_new_tab(url)


def run_set(ids: tuple[str, ...], *, list_only: bool, kill: bool, fresh: bool, lang: str | None,
            offset: int, open_browser: bool, chrome_profile: str | None, console) -> None:
    root = find_project_root()
    docs_all = load_documents(root, offset)
    docs = select(docs_all, ids)
    if list_only:
        for d in docs_all:
            pid = running_pid(root, d)
            state = f"[green]running[/green] (pid {pid})" if pid else (
                "[yellow]port busy[/yellow]" if _port_busy(d.port) else "[dim]stopped[/dim]")
            console.print(f"  {d.id:<18} :{d.port}  {state}  {d.url(lang)}  "
                          f"[dim]{os.path.relpath(d.book, root)}[/dim]")
        return
    if kill:
        for d in docs:
            console.print(f"  {d.id:<18} :{d.port}  {'stopped' if stop(root, d) else 'was not running'}")
        return
    for d in docs:
        status = start(root, docs_all, d, fresh=fresh)
        color = "green" if status in ("started", "running") else "red"
        console.print(f"  {d.id:<18} :{d.port}  [{color}]{status}[/{color}]  {d.url(lang)}")
    console.print(f"[dim]logs and state: {root / STATE_DIR}/ — `stx run --set --list`, `--kill`[/dim]")
    if open_browser:
        time.sleep(2)
        open_urls([d.url(lang) for d in docs], chrome_profile)
