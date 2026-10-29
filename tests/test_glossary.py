"""Glossary: gloss("term") hover definitions and st_glossary(), CSS only (#12)."""
import re
import sys
import textwrap
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from streamtex import bib, glossary
from streamtex.glossary import GlossaryConfig, gloss, load_glossary


@pytest.fixture(autouse=True)
def _clean():
    bib.reset_bib_registry()
    glossary.reset_glossary_registry()
    glossary.set_glossary_config(GlossaryConfig())
    yield
    bib.reset_bib_registry()
    glossary.reset_glossary_registry()
    glossary.set_glossary_config(GlossaryConfig())


YAML = """\
LLM: Large Language Model
RLHF:
  title: Reinforcement Learning from Human Feedback
  note: The model is tuned on human rankings of its answers.
"AT&T":
  abbreviation: "<AT&T>"
  title: "A \\"quoted\\" <b>name</b>"
"""

BIB = """\
@glossary{GPT, abbreviation = {GPT}, title = {Generative Pre-trained Transformer}, note = {A decoder-only model.}}
@book{knuth84, author = {Knuth, Donald}, year = {1984}, title = {The TeXbook}}
"""


def _register(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    glossary.get_glossary_registry().register_many(load_glossary(str(p)))
    return p


def test_yaml_terms_load(tmp_path):
    _register(tmp_path, "g.yaml", YAML)
    reg = glossary.get_glossary_registry()
    assert len(reg) == 3
    assert reg.get("LLM").title == "Large Language Model" and reg.get("LLM").entry_type == "glossary"
    assert reg.get("RLHF").note.startswith("The model is tuned")
    assert reg.get("AT&T").extra["abbreviation"] == "<AT&T>"


def test_json_mapping_and_bib_glossary_entries_load(tmp_path):
    _register(tmp_path, "g.json", '{"NLU": "Natural Language Understanding"}')
    _register(tmp_path, "g.bib", BIB)
    reg = glossary.get_glossary_registry()
    assert reg.get("NLU").title == "Natural Language Understanding"
    assert reg.get("GPT").note == "A decoder-only model."
    assert "knuth84" not in reg                                   # a reference is not a term


def test_gloss_markup_is_escaped_and_accessible(tmp_path):
    _register(tmp_path, "g.yaml", YAML)
    html = gloss("AT&T")
    assert html.startswith('<span class="stx-gloss" tabindex="0">&lt;AT&amp;T&gt;')
    assert '<span class="stx-gloss-tip" role="tooltip"><b>A &quot;quoted&quot; &lt;b&gt;name&lt;/b&gt;</b></span>' in html
    assert gloss("RLHF", text="human feedback").startswith('<span class="stx-gloss" tabindex="0">human feedback<')
    assert "<br>The model is tuned" in gloss("RLHF")


def test_an_unknown_key_warns_or_raises(caplog):
    assert gloss("nope") == "[nope?]" and "nope" in caplog.text
    glossary.set_glossary_config(GlossaryConfig(strict=True))
    with pytest.raises(KeyError, match="nope"):
        gloss("nope")


def test_the_bibliography_does_not_change(tmp_path):
    """Terms in the shared .bib take no citation number and stay out of st_bibliography()."""
    from streamtex.book import _setup_bibliography
    p = tmp_path / "refs.bib"
    p.write_text(BIB, encoding="utf-8")
    _setup_bibliography([str(p)], None)
    assert bib.get_bib_registry().list_keys() == ["knuth84"]
    gloss("GPT")
    assert bib.get_bib_registry()._cited == []
    assert ">Knuth, 1984<" in bib.cite("knuth84") and bib.get_bib_registry().cite("knuth84") == 1
    captured = []
    with patch("streamtex.export._render", side_effect=lambda h, **k: captured.append(h)), \
         patch("streamtex.write.st_write"), patch("streamtex.space.st_space"), patch("streamtex.container.st_block"):
        bib.st_bibliography(only_cited=False)
    assert len(captured) == 1 and 'id="bib-knuth84"' in captured[0] and "GPT" not in captured[0]


def _listed(**kw):
    captured, titles = [], []
    with patch("streamtex.export._render", side_effect=lambda h, **k: captured.append(h)), \
         patch("streamtex.write.st_write", side_effect=lambda s, t, toc_lvl=None, **k: titles.append((t, toc_lvl))), \
         patch("streamtex.space.st_space"), patch("streamtex.container.st_block"):
        glossary.st_glossary(**kw)
    return [re.search(r'id="gloss-([^"]+)"', h).group(1) for h in captured], captured, titles


def test_st_glossary_lists_the_used_terms_alphabetically(tmp_path):
    _register(tmp_path, "g.yaml", YAML)
    assert _listed()[0] == []                                     # nothing used yet: nothing rendered
    gloss("RLHF"), gloss("LLM")
    keys, html, titles = _listed(toc_lvl="1")
    assert keys == ["LLM", "RLHF"] and titles == [("Glossary", "1")]
    assert "<span style=\"font-weight:bold;\">RLHF</span> — Reinforcement Learning from Human Feedback. The model" in html[1]
    assert _listed(only_used=False)[0] == ["AT&amp;T", "LLM", "RLHF"]


def test_default_css_has_the_hover_and_print_rules():
    from streamtex.export import _load_default_css
    css = _load_default_css()
    assert ".stx-gloss:hover .stx-gloss-tip" in css and ".stx-gloss:focus .stx-gloss-tip" in css
    assert re.search(r"@media print \{\s*\.stx-gloss-tip \{ display: none !important; \}", css)
    assert "underline dotted" in css


def test_the_toc_label_holds_no_definition(tmp_path):
    from streamtex.utils import plain_label
    _register(tmp_path, "g.yaml", YAML)
    assert plain_label("Why " + gloss("RLHF") + " works") == "Why RLHF works"


@pytest.fixture
def deck(tmp_path):
    p = tmp_path / "deck"
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    (p / "glossary.yaml").write_text(YAML, encoding="utf-8")
    (p / "blocks" / "bck_gloss.py").write_text(textwrap.dedent("""
        import streamtex as stx
        def build(**k):
            stx.st_write("How ", stx.gloss("LLM"), " models learn", toc_lvl="1")
            stx.st_slide_break()
            stx.st_glossary(toc_lvl="1")
    """))
    (p / "book.py").write_text(textwrap.dedent("""
        from pathlib import Path
        import streamtex as stx
        from blocks import bck_gloss
        stx.st_book([bck_gloss], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(),
                    glossary_sources=[str(Path(__file__).parent / "glossary.yaml")],
                    html_export_mode="continuous")
    """))
    yield p
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def test_the_export_keeps_the_term_its_css_and_the_list(deck, tmp_path):
    from streamtex.cli.export_cmd import export_html
    out = tmp_path / "out"
    r = CliRunner().invoke(export_html, [str(deck), "-o", str(out)])
    assert r.exit_code == 0, r.output
    html = next(out.rglob("deck.html")).read_text(encoding="utf-8")
    assert "[LLM?]" not in html
    assert '<span class="stx-gloss" tabindex="0">LLM<span class="stx-gloss-tip" role="tooltip">' in html
    assert ".stx-gloss:hover .stx-gloss-tip" in html
    assert 'id="gloss-LLM"' in html and 'id="gloss-RLHF"' not in html
    assert "How LLM models learn" in html                         # the TOC label, without the definition
    assert "How LLMLarge" not in html
