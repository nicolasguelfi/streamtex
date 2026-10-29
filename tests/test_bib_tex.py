"""BibTeX: TeX decoding, nested braces (#34), institutional authors, ancient
dates, strict keys, projection cards, long URLs (#54) — #86."""

import re

import pytest

from streamtex import bib
from streamtex.bib import BibConfig, cite, parse_bibtex_string


@pytest.fixture(autouse=True)
def _reset():
    bib.reset_bib_registry()
    bib.set_bib_config(BibConfig())
    yield
    bib.reset_bib_registry()
    bib.set_bib_config(BibConfig())


def _one(src):
    entries = parse_bibtex_string(src)
    assert len(entries) == 1
    return entries[0]


def test_accent_macros_at_any_depth_keep_the_author(  # #34
):
    e = _one(r"@book{z, author = {{\v{Z}}{\'i}dek, Jan and M{\"o}ller, K.}, year = {2020}, title = {T}}")
    assert e.authors == ["Žídek, Jan", "Möller, K."]
    assert e.authors_short == "Žídek & Möller"


@pytest.mark.parametrize("raw, shown", [
    (r"Saint-Exup\'ery", "Saint-Exupéry"),
    (r"Kenzabur\=o \=Oe", "Kenzaburō Ōe"),
    (r"Ad\`ele {\oe}uvre", "Adèle œuvre"),
    (r"Fran\c{c}ois \ss", "François ß"),
    (r"R\&D 50\% \#92", "R&D 50% #92"),
    (r"The {GPT} model", "The GPT model"),
    ("Plain title — unchanged", "Plain title — unchanged"),
])
def test_tex_decoding(raw, shown):
    assert _one("@misc{k, title = {" + raw + "}}").title == shown


def test_institutional_authors_shown_whole():
    e = _one("@misc{un, author = {{United Nations}}, year = {1992}}")
    assert e.authors_short == "United Nations"
    assert e.first_author_last == "United Nations"
    e2 = _one("@misc{x, author = {{European Parliament} and {Council}}, year = {2024}}")
    assert e2.authors == ["European Parliament", "Council"]


def test_shortauthor_shortens_the_citation_not_the_bibliography():
    from streamtex.bib import BibFormat, format_entry

    e = _one("@misc{aiact, author = {{European Parliament and Council}}, "
             "shortauthor = {EU}, year = {2024}, title = {AI Act}}")
    assert e.authors_short == "EU"
    bib.get_bib_registry().register_many([e])
    assert "EU, 2024" in cite("aiact")
    for fmt in BibFormat:
        assert "European Parliament and Council" in format_entry(e, fmt, 1)
    # without the field, nothing changes
    assert _one("@misc{un, author = {{United Nations}}, year = {1992}}").authors_short == "United Nations"


def test_ancient_and_original_dates_in_the_citation_code():
    entries = parse_bibtex_string(
        "@book{plato, author = {Plato}, year = {1935}, origdate = {-380}}\n"
        "@book{fuku, author = {Fukuzawa, Yukichi}, year = {1960}, origdate = {1899}}\n"
        "@book{iso, author = {Isocrates}, year = {-354}}\n"
        "@book{now, author = {Doe}, year = {2020}}\n")
    reg = bib.get_bib_registry()
    reg.register_many(entries)
    assert "Plato, c. 380 BCE" in cite("plato")
    assert "Fukuzawa, 1899" in cite("fuku")
    assert "Isocrates, c. 354 BCE" in cite("iso")
    assert "Doe, 2020" in cite("now")
    bib.set_bib_config(BibConfig(locale="fr"))
    assert "Plato, ~380 av. J.-C." in cite("plato")


def test_strict_unknown_key_raises_default_prints_marker():
    assert "[nope?]" in cite("nope")
    bib.set_bib_config(BibConfig(strict=True))
    with pytest.raises(KeyError, match="nope"):
        cite("nope")


def test_projection_preset():
    c = BibConfig.projection()
    assert (c.card_width, c.card_font_scale) == ("780px", 2.0)
    assert BibConfig.projection(strict=True).strict is True


def test_bibliography_entries_wrap_long_urls(monkeypatch):  # #54
    from unittest.mock import patch

    reg = bib.get_bib_registry()
    reg.register_many(parse_bibtex_string(
        "@misc{u, author = {A}, year = {2020}, title = {T}, url = {https://x.org/" + "a" * 200 + "}}"))
    captured = []
    with patch("streamtex.export._render", side_effect=lambda h, **k: captured.append(h)), \
         patch("streamtex.write.st_write"), patch("streamtex.container.st_block"):
        bib.st_bibliography(only_cited=False)
    assert any("overflow-wrap:anywhere;" in h for h in captured)


# -- the label before each entry follows citation_style (#23) ----------------------------

def _labels(monkeypatch, citation_style, **kw):
    from unittest.mock import patch

    from streamtex.bib import BibConfig, CitationStyle
    reg = bib.get_bib_registry()
    reg.register_many(parse_bibtex_string(
        "@article{dart, author = {Dart, Eli and Rotman, Lauren and Tierney, Brian}, year = {2013}, title = {DMZ}}\n"
        "@book{knuth, author = {Knuth, Donald}, year = {1984}, title = {TeX}}"))
    monkeypatch.setattr(bib, "_bib_config", BibConfig(citation_style=getattr(CitationStyle, citation_style)))
    captured = []
    with patch("streamtex.export._render", side_effect=lambda h, **k: captured.append(h)), \
         patch("streamtex.write.st_write"), patch("streamtex.container.st_block"):
        bib.st_bibliography(only_cited=False, **kw)
    return [re.search(r'<span style="[^"]*">(.*?)</span>', h).group(1) for h in captured if 'id="bib-' in h]


def test_author_year_lists_show_the_inline_label(monkeypatch):
    labels = _labels(monkeypatch, "AUTHOR_YEAR")
    assert len(labels) == 2 and all(lb.startswith("(") and lb.endswith(")") for lb in labels)
    assert any("Knuth" in lb and "1984" in lb for lb in labels)
    assert any("Dart" in lb and "2013" in lb for lb in labels)


@pytest.mark.parametrize("style", ["NUMERIC", "SUPERSCRIPT"])
def test_numbered_lists_keep_their_numbers(monkeypatch, style):
    assert _labels(monkeypatch, style) == ["[1]", "[2]"]


def test_label_style_overrides_the_citation_style(monkeypatch):
    from streamtex.bib import CitationStyle
    assert _labels(monkeypatch, "AUTHOR_YEAR", label_style=CitationStyle.NUMERIC) == ["[1]", "[2]"]


# -- a long list split over slides (#23, part 2) -------------------------------------------

def _chunks(n, **kw):
    """Render *n* entries; the calls in order: ("title", text, toc_lvl), ("break", label), ("entry", label)."""
    from unittest.mock import patch
    reg = bib.get_bib_registry()
    reg.register_many(parse_bibtex_string("\n".join(
        f"@misc{{k{i:02d}, author = {{A{i:02d}}}, year = {{2000}}, title = {{T}}}}" for i in range(n))))
    bib.set_bib_config(BibConfig(sort_by="key"))
    seen = []
    with patch("streamtex.export._render", side_effect=lambda h, **k: seen.append(
                ("entry", re.search(r'<span style="[^"]*">(.*?)</span>', h).group(1)))), \
         patch("streamtex.write.st_write", side_effect=lambda s, t, toc_lvl=None, label="", **k: seen.append(
             ("title", t, toc_lvl, label))), \
         patch("streamtex.slide.st_slide_break", side_effect=lambda **k: seen.append(("break", k["marker_label"]))), \
         patch("streamtex.space.st_space"), patch("streamtex.container.st_block"):
        bib.st_bibliography(only_cited=False, label_style=bib.CitationStyle.NUMERIC, toc_lvl="1", **kw)
    return seen


def test_chunk_size_splits_the_list_over_slides():
    seen = _chunks(5, chunk_size=2)
    assert [s for s in seen if s[0] != "entry"] == [
        ("title", "References (1/3)", "1", "References"), ("break", "References 2/3"),
        ("title", "References (2/3)", None, ""), ("break", "References 3/3"), ("title", "References (3/3)", None, "")]
    assert [s[1] for s in seen if s[0] == "entry"] == ["[1]", "[2]", "[3]", "[4]", "[5]"]   # numbering goes on
    assert seen.index(("break", "References 2/3")) == 3                                      # after 2 entries


def test_without_chunk_size_nothing_changes():
    seen = _chunks(5)
    assert [s for s in seen if s[0] != "entry"] == [("title", "References", "1", "References")]
    assert len(seen) == 6


def test_one_chunk_keeps_the_plain_title():
    assert [s for s in _chunks(3, chunk_size=10) if s[0] != "entry"] == [("title", "References", "1", "References")]


def test_chunk_size_must_be_positive():
    with pytest.raises(ValueError, match="chunk_size"):
        _chunks(3, chunk_size=0)
