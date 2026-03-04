"""Tests for stx bib generate-stubs command."""


from click.testing import CliRunner

from streamtex.cli.commands import cli


def _write_bib(path, content):
    """Helper to write a .bib file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


SAMPLE_BIB = """\
@article{vaswani2017,
  title = {Attention Is All You Need},
  author = {Vaswani, Ashish and Shazeer, Noam},
  year = {2017},
  journal = {NeurIPS},
}
"""


def test_generates_to_stdout(tmp_path):
    bib_file = tmp_path / "refs.bib"
    _write_bib(bib_file, SAMPLE_BIB)

    runner = CliRunner()
    result = runner.invoke(cli, ["bib", "generate-stubs", str(bib_file)])
    assert result.exit_code == 0
    assert "vaswani2017" in result.output
    assert "@property" in result.output
    assert "st_refs" in result.output


def test_generates_to_file(tmp_path):
    bib_file = tmp_path / "refs.bib"
    _write_bib(bib_file, SAMPLE_BIB)
    output_file = tmp_path / "bib_refs.py"

    runner = CliRunner()
    result = runner.invoke(cli, ["bib", "generate-stubs", str(bib_file), "-o", str(output_file)])
    assert result.exit_code == 0
    assert output_file.is_file()
    content = output_file.read_text()
    assert "vaswani2017" in content


def test_requires_sources():
    runner = CliRunner()
    result = runner.invoke(cli, ["bib", "generate-stubs"])
    assert result.exit_code != 0
