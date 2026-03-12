"""Run command: launch a StreamTeX project with Streamlit."""

import os
import platform
import shutil
import signal
import subprocess
import sys
import time

import click

from .console import get_console

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
            pass
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


def _resolve_port(port_arg: int | None) -> int:
    """Resolve the effective port: CLI arg > config file > default."""
    if port_arg:
        return port_arg
    config_port = _read_port_from_config()
    if config_port:
        return config_port
    return _DEFAULT_PORT


@click.command(name="run")
@click.argument("book", required=False, default=None)
@click.option("-p", "--port", type=int, default=None, help="Server port (default: Streamlit auto).")
@click.option(
    "-b", "--browser",
    type=click.Choice(["chrome", "firefox", "safari", "edge", "none"]),
    default=None,
    help="Browser to open (default: system default).",
)
@click.option("--headless", is_flag=True, help="Don't open any browser.")
@click.option("-f", "--force", is_flag=True, help="Kill any process using the target port before starting.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def run(book, port, browser, headless, force, extra_args):
    """Run a StreamTeX project (shortcut for streamlit run)."""
    console = get_console()
    entry = _find_book(book)

    actual_port = _resolve_port(port)

    # Kill existing process on the port if --force
    if force:
        _kill_port(actual_port)

    # Build streamlit command — use `uv run` so Streamlit runs inside the
    # project's .venv (not the uv-tool Python that hosts the CLI).
    uv = shutil.which("uv")
    if uv:
        cmd = [uv, "run", "streamlit", "run", entry]
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", entry]

    if port or _read_port_from_config():
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
