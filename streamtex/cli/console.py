"""Rich console helper for the stx CLI."""


def get_console():
    """Return a Rich Console instance (lazy import)."""
    from rich.console import Console

    return Console()
