"""Run command: launch a StreamTeX project with Streamlit."""

import os
import platform
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
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def run(book, port, browser, headless, extra_args):
    """Run a StreamTeX project (shortcut for streamlit run)."""
    console = get_console()
    entry = _find_book(book)

    # Build streamlit command
    cmd = [sys.executable, "-m", "streamlit", "run", entry]

    if port:
        cmd.extend(["--server.port", str(port)])

    # If a specific browser is requested or headless, run in headless mode
    # and open the browser manually
    if browser or headless:
        cmd.extend(["--server.headless", "true"])

    cmd.extend(extra_args)

    actual_port = port or 8501
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
