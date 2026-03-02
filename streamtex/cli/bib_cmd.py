"""Bibliography CLI commands: generate-stubs."""

import click


@click.command("generate-stubs")
@click.argument("sources", nargs=-1, required=True)
@click.option("-o", "--output", default="", help="Output .py file path (prints to stdout if omitted).")
def generate_stubs(sources, output):
    """Generate a typed BibRefs module for IDE autocompletion."""
    from streamtex.bib import generate_bib_stubs

    content = generate_bib_stubs(*sources, output_path=output)
    if not output:
        click.echo(content)
    else:
        n = content.count("@property")
        click.echo(f"Generated {output} ({n} entries)")
