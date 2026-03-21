"""CLI entry point for StreamTeX utilities.

Usage (with CLI deps installed):
    uv run stx --help
    uv run python -m streamtex --help

Fallback (without click/rich):
    uv run python -m streamtex generate-stubs refs.bib [-o custom/bib_refs.py]
"""

import sys


def main():
    # If click is available, delegate to the full CLI
    try:
        from streamtex.cli.main import app
        app()
        return
    except ImportError:
        pass

    # Fallback: argparse for generate-stubs only (retro-compat)
    import argparse

    parser = argparse.ArgumentParser(
        prog="streamtex",
        description=(
            "StreamTeX command-line utilities.\n\n"
            "For the full CLI, install optional deps:\n"
            "  uv add \"streamtex[cli]\"      # if using uv\n"
            "  pip install \"streamtex[cli]\"  # if using pip"
        ),
    )
    sub = parser.add_subparsers(dest="command")

    # --- generate-stubs ---
    stubs = sub.add_parser(
        "generate-stubs",
        help="Generate a .py module with typed BibRefs for IDE autocompletion",
    )
    stubs.add_argument(
        "sources", nargs="+",
        help="Bibliography source files (.bib, .json, .ris, .csl-json)",
    )
    stubs.add_argument(
        "-o", "--output", default="",
        help="Output .py file path (prints to stdout if omitted)",
    )

    # Also support --generate-stubs as a top-level flag for convenience
    parser.add_argument(
        "--generate-stubs", nargs="+", metavar="FILE",
        help="Shorthand: generate typed BibRefs module from bibliography files",
    )
    parser.add_argument(
        "-o", "--output", default="",
        help="Output .py file path (used with --generate-stubs)",
    )

    args = parser.parse_args()

    # Handle --generate-stubs shorthand
    sources = None
    output = ""
    if args.generate_stubs:
        sources = args.generate_stubs
        output = args.output
    elif args.command == "generate-stubs":
        sources = args.sources
        output = args.output

    if sources:
        from .bib import generate_bib_stubs
        content = generate_bib_stubs(*sources, output_path=output)
        if not output:
            print(content)
        else:
            n = content.count("@property")
            print(f"Generated {output} ({n} entries)")
        return

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
