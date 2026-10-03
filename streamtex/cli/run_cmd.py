"""Run command: launch a StreamTeX project with Streamlit."""

import logging
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time

import click

from .console import get_console

logger = logging.getLogger(__name__)

# Browser launch commands per OS
_BROWSER_COMMANDS = {
    "darwin": {
        "chrome": ["open", "-a", "Google Chrome"],
        "firefox": ["open", "-a", "Firefox"],
        "safari": ["open", "-a", "Safari"],
    },
    "linux": {
        "chrome": ["google-chrome"],
        "firefox": ["firefox"],
    },
    "windows": {
        "chrome": ["start", "chrome"],
        "firefox": ["start", "firefox"],
        "edge": ["start", "msedge"],
    },
}

_DEFAULT_PORT = 8501


def _get_os_key() -> str:
    s = platform.system().lower()
    if s == "darwin":
        return "darwin"
    if s == "windows":
        return "windows"
    return "linux"


def _detect_chrome() -> bool:
    """Return True if Google Chrome is available on this machine."""
    os_key = _get_os_key()
    if os_key == "darwin":
        return os.path.isdir("/Applications/Google Chrome.app")
    if os_key == "windows":
        return shutil.which("chrome") is not None or os.path.exists(
            os.path.join(
                os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                "Google", "Chrome", "Application", "chrome.exe",
            )
        )
    # Linux
    return shutil.which("google-chrome") is not None


def _open_browser(browser: str, url: str) -> None:
    """Open a specific browser with the given URL."""
    os_key = _get_os_key()
    commands = _BROWSER_COMMANDS.get(os_key, {})
    cmd = commands.get(browser)
    if cmd is None:
        console = get_console()
        available = ", ".join(sorted(commands.keys())) or "(none)"
        console.print(
            f"[yellow]Browser '{browser}' not supported on {os_key}. "
            f"Available: {available}[/yellow]"
        )
        return
    try:
        subprocess.Popen([*cmd, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        console = get_console()
        console.print(f"[yellow]Could not open {browser}.[/yellow]")


def _find_book(book: str | None) -> str:
    """Resolve the book entry point file."""
    if book:
        if not os.path.isfile(book):
            raise click.ClickException(f"File not found: {book}")
        return book
    # Auto-detect book.py in current directory
    if os.path.isfile("book.py"):
        return "book.py"
    raise click.ClickException(
        "No book.py found in current directory. "
        "Specify a file: stx run myfile.py"
    )


def _read_port_from_config() -> int | None:
    """Read server port from .streamlit/config.toml if it exists."""
    config_path = os.path.join(".streamlit", "config.toml")
    if not os.path.isfile(config_path):
        return None
    try:
        import tomllib

        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("server", {}).get("port")
    except (OSError, ValueError, KeyError):
        return None


def _kill_port(port: int) -> bool:
    """Kill the process listening on the given port. Returns True if a process was killed."""
    console = get_console()
    os_key = _get_os_key()

    if os_key == "windows":
        # Windows: netstat + taskkill
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid], timeout=5)
                    console.print(f"[yellow]Killed process {pid} on port {port}[/yellow]")
                    return True
        except (subprocess.TimeoutExpired, OSError):
            logger.debug("Failed to kill process on port %s (Windows)", port, exc_info=True)
        return False

    # macOS / Linux: lsof
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, timeout=5,
        )
        pids = result.stdout.strip().splitlines()
        if not pids:
            return False
        for pid_str in pids:
            try:
                pid = int(pid_str.strip())
                os.kill(pid, signal.SIGTERM)
                console.print(f"[yellow]Killed process {pid} on port {port}[/yellow]")
            except (ValueError, ProcessLookupError, PermissionError):
                continue
        # Give the process time to release the port
        time.sleep(1)
        return True
    except (subprocess.TimeoutExpired, OSError):
        return False


def _is_port_free(port: int) -> bool:
    """Return True if the given port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False


def _find_free_port(start: int = _DEFAULT_PORT, max_tries: int = 50) -> int:
    """Find the first free port starting from *start*."""
    for offset in range(max_tries):
        candidate = start + offset
        if _is_port_free(candidate):
            return candidate
    return start


def _resolve_port(port_arg: int | None) -> int:
    """Resolve the effective port: CLI arg > config file > first free port."""
    if port_arg:
        return port_arg
    config_port = _read_port_from_config()
    if config_port:
        return config_port
    return _find_free_port()


@click.command(name="run")
@click.argument("book", required=False, default=None)
@click.option("-p", "--port", type=int, default=None, help="Server port (default: Streamlit auto).")
@click.option(
    "-b", "--browser",
    type=click.Choice(["chrome", "firefox", "safari", "edge", "none"]),
    default=None,
    help="Browser to open (default: Chrome if available, else system default).",
)
@click.option("--headless", is_flag=True, help="Don't open any browser.")
@click.option("-f", "--force", is_flag=True, help="Kill any process using the target port before starting.")
@click.option("--set", "run_set_flag", is_flag=True,
              help="Run the documents declared in stx.toml [[run.documents]] together, in the background "
                   "(fixed ports, $STX_URL_<ID> for each). Restrict with --doc.")
@click.option("--doc", "docs", multiple=True, help="With --set / --list / --kill: only this document id.")
@click.option("--list", "list_only", is_flag=True, help="List the declared documents and their state.")
@click.option("--kill", is_flag=True, help="Stop the declared documents (or --doc ones).")
@click.option("--fresh", is_flag=True, help="With --set: stop, clear the page cache, start again.")
@click.option("--lang", default=None, help="With --set / --list: URLs carry ?lang=CODE.")
@click.option("--ports-offset", default=0, show_default=True, help="With --set: add N to every declared port.")
@click.option("--open/--no-open", "open_browser", default=False, help="With --set: open the documents.")
@click.option("--chrome-profile", default=None,
              help="With --set --open: a dedicated Chrome profile directory, media autoplay allowed "
                   "(projection), e.g. ~/.stx-projection-chrome.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def run(book, port, browser, headless, force, run_set_flag, docs, list_only, kill, fresh, lang,
        ports_offset, open_browser, chrome_profile, extra_args):
    """Run a StreamTeX project (shortcut for streamlit run).

    With --set: run every document of a multi-document project (stx.toml
    [[run.documents]]); --list, --kill manage them.
    """
    console = get_console()
    if run_set_flag or list_only or kill:
        from .run_set import run_set

        run_set(tuple(docs), list_only=list_only, kill=kill and not run_set_flag, fresh=fresh,
                lang=lang, offset=ports_offset, open_browser=open_browser,
                chrome_profile=chrome_profile, console=console)
        return
    entry = _find_book(book)

    actual_port = _resolve_port(port)

    # Kill existing process on the port if --force
    if force:
        _kill_port(actual_port)

    # Auto-detect Chrome when no --browser is specified
    # Priority: explicit --browser > auto-detect Chrome > Streamlit default
    if not headless and browser is None and _detect_chrome():
        browser = "chrome"

    # Build streamlit command — use `uv run` so Streamlit runs inside the
    # project's .venv (not the uv-tool Python that hosts the CLI).
    uv = shutil.which("uv")
    if uv:
        cmd = [uv, "run", "streamlit", "run", entry]
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", entry]

    cmd.extend(["--server.port", str(actual_port)])

    # If a specific browser is requested or headless, run in headless mode
    # and open the browser manually
    if browser or headless:
        cmd.extend(["--server.headless", "true"])

    cmd.extend(extra_args)

    url = f"http://localhost:{actual_port}"

    if browser and browser != "none" and not headless:
        console.print(
            f"[bold]Starting[/bold] {entry} on port [cyan]{actual_port}[/cyan] "
            f"with [cyan]{browser}[/cyan] …"
        )
    else:
        console.print(
            f"[bold]Starting[/bold] {entry} on port [cyan]{actual_port}[/cyan] …"
        )

    # Launch streamlit
    try:
        proc = subprocess.Popen(cmd)

        # Open specific browser after a short delay
        if browser and browser != "none" and not headless:
            time.sleep(2)
            _open_browser(browser, url)

        proc.wait()
        raise SystemExit(proc.returncode)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped.[/yellow]")
        raise SystemExit(0)
