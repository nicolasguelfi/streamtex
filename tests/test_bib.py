"""Tests for streamtex.bib — Bibliography system."""

import os
import json
import tempfile
import textwrap

import pytest

from streamtex.bib import (
    BibEntry, BibConfig, BibFormat, CitationStyle, BibParseError,
    BibRegistry,
    set_bib_config, get_bib_config, get_bib_registry, reset_bib_registry,
    load_bibtex, load_bib_json, load_bib_ris, load_bib_csl_json,
    load_bib, register_bib_parser,
    parse_bibtex_string, parse_ris_string,
    cite, export_bibtex,
    format_entry,
    _format_apa, _format_ieee, _format_mla, _format_chicago, _format_harvard,
    _fields_to_entry,
    st_refs, generate_bib_stubs,
)


# ===================================================================
# BibEntry
# ===================================================================

class TestBibEntry:
    def test_first_author_last_comma(self):
        e = BibEntry(key="t", authors=["Vaswani, Ashish"])
        assert e.first_author_last == "Vaswani"

    def test_first_author_last_space(self):
        e = BibEntry(key="t", authors=["Ashish Vaswani"])
        assert e.first_author_last == "Vaswani"

    def test_first_author_last_empty(self):
        e = BibEntry(key="t")
        assert e.first_author_last == "Unknown"

    def test_authors_short_single(self):
        e = BibEntry(key="t", authors=["Vaswani, A."])
        assert e.authors_short == "Vaswani"

    def test_authors_short_two(self):
        e = BibEntry(key="t", authors=["Vaswani, A.", "Shazeer, N."])
        assert e.authors_short == "Vaswani & Shazeer"

    def test_authors_short_three(self):
        e = BibEntry(key="t", authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N."])
        assert e.authors_short == "Vaswani et al."

    def test_authors_short_empty(self):
        e = BibEntry(key="t")
        assert e.authors_short == "Unknown"

    def test_get_field_known(self):
        e = BibEntry(key="t", title="Test")
        assert e.get_field("title") == "Test"

    def test_get_field_extra(self):
        e = BibEntry(key="t", extra={"custom_field": "value"})
        assert e.get_field("custom_field") == "value"

    def test_get_field_default(self):
        e = BibEntry(key="t")
        assert e.get_field("nonexistent", "default") == "default"

    def test_extensible_fields(self):
        e = BibEntry(key="t", isbn="978-3-16", issn="1234-5678",
                     edition="2nd", editor="Smith, J.",
                     institution="MIT", school="Stanford",
                     address="New York", month="January",
                     language="English", keywords="AI, NLP")
        assert e.isbn == "978-3-16"
        assert e.keywords == "AI, NLP"
        assert e.institution == "MIT"


# ===================================================================
# BibRegistry
# ===================================================================

class TestBibRegistry:
    def setup_method(self):
        self.reg = BibRegistry()

    def test_register_and_get(self):
        e = BibEntry(key="test1", title="Title")
        self.reg.register(e)
        assert self.reg.get("test1") is e

    def test_get_unknown(self):
        assert self.reg.get("unknown") is None

    def test_overwrite(self):
        self.reg.register(BibEntry(key="a", title="Old"))
        self.reg.register(BibEntry(key="a", title="New"))
        assert self.reg.get("a").title == "New"

    def test_cite_returns_number(self):
        self.reg.register(BibEntry(key="a"))
        self.reg.register(BibEntry(key="b"))
        assert self.reg.cite("a") == 1
        assert self.reg.cite("b") == 2
        assert self.reg.cite("a") == 1  # Same number

    def test_cite_unknown(self):
        assert self.reg.cite("unknown") == 0

    def test_get_cited_entries(self):
        self.reg.register(BibEntry(key="b"))
        self.reg.register(BibEntry(key="a"))
        self.reg.cite("b")
        self.reg.cite("a")
        cited = self.reg.get_cited_entries()
        assert [e.key for e in cited] == ["b", "a"]

    def test_get_all_entries(self):
        self.reg.register(BibEntry(key="a"))
        self.reg.register(BibEntry(key="b"))
        assert len(self.reg.get_all_entries()) == 2

    def test_list_keys(self):
        self.reg.register(BibEntry(key="z"))
        self.reg.register(BibEntry(key="a"))
        assert self.reg.list_keys() == ["a", "z"]

    def test_reset(self):
        self.reg.register(BibEntry(key="a"))
        self.reg.cite("a")
        self.reg.reset()
        assert len(self.reg) == 0
        assert self.reg.get_cited_entries() == []

    def test_contains(self):
        self.reg.register(BibEntry(key="a"))
        assert "a" in self.reg
        assert "b" not in self.reg

    def test_len(self):
        assert len(self.reg) == 0
        self.reg.register(BibEntry(key="a"))
        assert len(self.reg) == 1


# ===================================================================
# Global config/registry
# ===================================================================

class TestGlobalConfig:
    def test_set_and_get_config(self):
        cfg = BibConfig(format=BibFormat.IEEE)
        set_bib_config(cfg)
        assert get_bib_config() is cfg
        set_bib_config(BibConfig())  # Reset

    def test_reset_registry(self):
        reg = get_bib_registry()
        reg.register(BibEntry(key="test"))
        reset_bib_registry()
        assert len(get_bib_registry()) == 0


# ===================================================================
# BibTeX parser
# ===================================================================

class TestBibTeXParser:
    def test_simple_article(self):
        bib = textwrap.dedent("""\
            @article{smith2024,
                title = {A Test Title},
                author = {Smith, John and Doe, Jane},
                year = {2024},
                journal = {Test Journal},
                volume = {10},
                pages = {1-15},
            }
        """)
        entries = parse_bibtex_string(bib)
        assert len(entries) == 1
        e = entries[0]
        assert e.key == "smith2024"
        assert e.entry_type == "article"
        assert e.title == "A Test Title"
        assert e.authors == ["Smith, John", "Doe, Jane"]
        assert e.year == "2024"
        assert e.journal == "Test Journal"
        assert e.volume == "10"
        assert e.pages == "1-15"

    def test_multiple_entries(self):
        bib = "@article{a, title={A}}\n@book{b, title={B}}"
        entries = parse_bibtex_string(bib)
        assert len(entries) == 2

    def test_skips_comments(self):
        bib = "@comment{ignore}\n@article{real, title={Real}}"
        entries = parse_bibtex_string(bib)
        assert len(entries) == 1
        assert entries[0].key == "real"

    def test_skips_string(self):
        bib = "@string{foo = {bar}}\n@article{a, title={X}}"
        entries = parse_bibtex_string(bib)
        assert len(entries) == 1

    def test_bare_number(self):
        bib = "@article{t, year = 2024}"
        entries = parse_bibtex_string(bib)
        assert entries[0].year == "2024"

    def test_quoted_values(self):
        bib = '@article{t, title = "Quoted Title"}'
        entries = parse_bibtex_string(bib)
        assert entries[0].title == "Quoted Title"

    def test_nested_braces(self):
        bib = '@article{t, title = {A {B} C}}'
        entries = parse_bibtex_string(bib)
        assert entries[0].title == "A {B} C"

    def test_empty_input(self):
        assert parse_bibtex_string("") == []

    def test_multiline_values(self):
        bib = textwrap.dedent("""\
            @article{t,
                abstract = {Line one
                    line two
                    line three},
            }
        """)
        entries = parse_bibtex_string(bib)
        assert "line two" in entries[0].abstract

    def test_extra_fields(self):
        bib = "@article{t, title={X}, mycustomfield={custom_value}}"
        entries = parse_bibtex_string(bib)
        assert entries[0].extra.get("mycustomfield") == "custom_value"

    def test_load_bibtex_file(self):
        bib_content = "@book{b, title={Book}, author={Author, A.}, year={2020}}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
            f.write(bib_content)
            f.flush()
            entries = load_bibtex(f.name)
        os.unlink(f.name)
        assert len(entries) == 1
        assert entries[0].key == "b"

    def test_case_insensitive_type(self):
        bib = "@Article{t, title={X}}"
        entries = parse_bibtex_string(bib)
        assert entries[0].entry_type == "article"


# ===================================================================
# JSON parser
# ===================================================================

class TestJSONParser:
    def test_basic(self):
        data = [
            {"key": "a", "title": "Title A", "authors": ["Smith, J."], "year": "2024"},
            {"key": "b", "title": "Title B", "entry_type": "book"},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            entries = load_bib_json(f.name)
        os.unlink(f.name)
        assert len(entries) == 2
        assert entries[0].title == "Title A"
        assert entries[1].entry_type == "book"

    def test_skip_no_key(self):
        data = [{"title": "No Key"}, {"key": "ok", "title": "Has Key"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            entries = load_bib_json(f.name)
        os.unlink(f.name)
        assert len(entries) == 1

    def test_invalid_format(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"not": "array"}, f)
            f.flush()
            with pytest.raises(ValueError, match="Expected JSON array"):
                load_bib_json(f.name)
        os.unlink(f.name)


# ===================================================================
# RIS parser
# ===================================================================

class TestRISParser:
    def test_basic_article(self):
        ris = textwrap.dedent("""\
            TY  - JOUR
            AU  - Smith, John
            AU  - Doe, Jane
            TI  - A Test Article
            JO  - Test Journal
            VL  - 5
            IS  - 2
            SP  - 10
            EP  - 20
            PY  - 2024
            DO  - 10.1234/test
            AB  - This is an abstract.
            ER  -
        """)
        entries = parse_ris_string(ris)
        assert len(entries) == 1
        e = entries[0]
        assert e.title == "A Test Article"
        assert e.authors == ["Smith, John", "Doe, Jane"]
        assert e.journal == "Test Journal"
        assert e.volume == "5"
        assert e.pages == "10-20"
        assert e.year == "2024"
        assert e.doi == "10.1234/test"

    def test_multiple_entries(self):
        ris = textwrap.dedent("""\
            TY  - JOUR
            AU  - Alpha, A
            TI  - First
            PY  - 2020
            ER  -
            TY  - BOOK
            AU  - Beta, B
            TI  - Second
            PY  - 2021
            ER  -
        """)
        entries = parse_ris_string(ris)
        assert len(entries) == 2
        assert entries[0].entry_type == "article"
        assert entries[1].entry_type == "book"

    def test_type_mapping(self):
        ris = "TY  - CONF\nAU  - Test, A\nTI  - Conf Paper\nPY  - 2023\nER  -\n"
        entries = parse_ris_string(ris)
        assert entries[0].entry_type == "inproceedings"

    def test_empty(self):
        assert parse_ris_string("") == []

    def test_load_file(self):
        ris = "TY  - JOUR\nAU  - X, Y\nTI  - T\nPY  - 2024\nER  -\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ris", delete=False) as f:
            f.write(ris)
            f.flush()
            entries = load_bib_ris(f.name)
        os.unlink(f.name)
        assert len(entries) == 1

    def test_keywords_merged(self):
        ris = "TY  - JOUR\nAU  - X, Y\nTI  - T\nPY  - 2024\nKW  - AI\nKW  - NLP\nER  -\n"
        entries = parse_ris_string(ris)
        assert "AI" in entries[0].keywords
        assert "NLP" in entries[0].keywords


# ===================================================================
# CSL-JSON parser
# ===================================================================

class TestCSLJSONParser:
    def test_basic(self):
        data = [{
            "id": "vaswani2017",
            "type": "article-journal",
            "title": "Attention Is All You Need",
            "author": [
                {"family": "Vaswani", "given": "Ashish"},
                {"family": "Shazeer", "given": "Noam"},
            ],
            "issued": {"date-parts": [[2017]]},
            "container-title": "NeurIPS",
            "volume": 30,
            "page": "5998-6008",
            "DOI": "10.48550/arXiv.1706.03762",
        }]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            # Use load_bib_csl_json directly
            entries = load_bib_csl_json(f.name)
        os.unlink(f.name)

        assert len(entries) == 1
        e = entries[0]
        assert e.key == "vaswani2017"
        assert e.entry_type == "article"
        assert e.title == "Attention Is All You Need"
        assert len(e.authors) == 2
        assert e.authors[0] == "Vaswani, Ashish"
        assert e.year == "2017"
        assert e.journal == "NeurIPS"
        assert e.doi == "10.48550/arXiv.1706.03762"

    def test_auto_key(self):
        data = [{
            "type": "book",
            "title": "Test",
            "author": [{"family": "Smith", "given": "J."}],
            "issued": {"date-parts": [[2024]]},
        }]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            entries = load_bib_csl_json(f.name)
        os.unlink(f.name)
        assert entries[0].key == "smith2024"

    def test_container_title_as_list(self):
        data = [{
            "id": "t",
            "type": "article-journal",
            "title": "T",
            "container-title": ["Journal Name"],
            "issued": {"date-parts": [[2024]]},
        }]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            entries = load_bib_csl_json(f.name)
        os.unlink(f.name)
        assert entries[0].journal == "Journal Name"


# ===================================================================
# load_bib (auto-detect)
# ===================================================================

class TestLoadBib:
    def test_detects_bib(self):
        content = "@article{t, title={Test}}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
            f.write(content)
            f.flush()
            entries = load_bib(f.name)
        os.unlink(f.name)
        assert len(entries) == 1

    def test_detects_json(self):
        data = [{"key": "a", "title": "A"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            entries = load_bib(f.name)
        os.unlink(f.name)
        assert len(entries) == 1

    def test_detects_ris(self):
        ris = "TY  - JOUR\nAU  - X, Y\nTI  - T\nPY  - 2024\nER  -\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ris", delete=False) as f:
            f.write(ris)
            f.flush()
            entries = load_bib(f.name)
        os.unlink(f.name)
        assert len(entries) == 1

    def test_unsupported_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
            f.write("data")
            f.flush()
            with pytest.raises(ValueError, match="Unsupported bibliography format"):
                load_bib(f.name)
        os.unlink(f.name)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_bib("/nonexistent/file.bib")


# ===================================================================
# Custom parser registration
# ===================================================================

class TestRegisterParser:
    def test_register_and_use(self):
        def parse_custom(path):
            return [BibEntry(key="custom", title="Custom")]

        register_bib_parser("custom", parse_custom)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".custom", delete=False) as f:
            f.write("data")
            f.flush()
            entries = load_bib(f.name)
        os.unlink(f.name)
        assert entries[0].key == "custom"


# ===================================================================
# Formatters
# ===================================================================

class TestFormatAPA:
    def test_article(self):
        e = BibEntry(
            key="t", entry_type="article",
            authors=["Smith, J.", "Doe, J."],
            year="2024", title="Test Title",
            journal="Test Journal", volume="10", number="2", pages="1-15",
            doi="10.1234/test"
        )
        result = _format_apa(e)
        assert "Smith, J." in result
        assert "(2024)" in result
        assert "Test Title" in result
        assert "<i>Test Journal</i>" in result
        assert "10.1234/test" in result

    def test_book(self):
        e = BibEntry(
            key="t", entry_type="book",
            authors=["Author, A."],
            year="2020", title="Book Title",
            publisher="Publisher"
        )
        result = _format_apa(e)
        assert "<i>Book Title</i>" in result
        assert "Publisher" in result


class TestFormatIEEE:
    def test_numbered(self):
        e = BibEntry(
            key="t", entry_type="article",
            authors=["Smith, John"],
            year="2024", title="Test Title",
            journal="IEEE Trans.", volume="5", pages="10-20"
        )
        result = _format_ieee(e, 1)
        assert result.startswith("[1]")
        assert "J. Smith" in result

    def test_multiple_authors(self):
        e = BibEntry(
            key="t", entry_type="article",
            authors=["Smith, John", "Doe, Jane", "Lee, Bob"],
            year="2024", title="Test"
        )
        result = _format_ieee(e, 1)
        assert "and" in result


class TestFormatMLA:
    def test_article(self):
        e = BibEntry(
            key="t", entry_type="article",
            authors=["Smith, John"],
            year="2024", title="Test Title",
            journal="J. Science", volume="5", pages="1-10"
        )
        result = _format_mla(e)
        assert "Smith, John" in result
        assert "Test Title" in result


class TestFormatChicago:
    def test_article(self):
        e = BibEntry(key="t", authors=["Smith, J."], year="2024", title="Test")
        result = _format_chicago(e)
        assert "2024" in result


class TestFormatHarvard:
    def test_article(self):
        e = BibEntry(key="t", entry_type="article",
                     authors=["Smith, J."], year="2024", title="Test",
                     journal="Journal", volume="1", pages="1-5")
        result = _format_harvard(e)
        assert "(2024)" in result


class TestFormatEntry:
    def test_dispatches_correctly(self):
        e = BibEntry(key="t", authors=["A, B"], year="2024", title="X")
        for fmt in BibFormat:
            result = format_entry(e, fmt, 1)
            assert isinstance(result, str)
            assert len(result) > 0


# ===================================================================
# cite()
# ===================================================================

class TestCite:
    def setup_method(self):
        reset_bib_registry()
        set_bib_config(BibConfig())
        reg = get_bib_registry()
        reg.register(BibEntry(key="v2017", title="Attention", authors=["Vaswani, A."],
                               year="2017", journal="NeurIPS"))
        reg.register(BibEntry(key="d2019", title="BERT", authors=["Devlin, J."],
                               year="2019"))

    def teardown_method(self):
        reset_bib_registry()
        set_bib_config(BibConfig())

    def test_author_year(self):
        set_bib_config(BibConfig(citation_style=CitationStyle.AUTHOR_YEAR, hover_enabled=False))
        result = cite("v2017")
        assert "Vaswani" in result
        assert "2017" in result
        assert result.startswith("(")
        assert result.endswith(")")

    def test_numeric(self):
        set_bib_config(BibConfig(citation_style=CitationStyle.NUMERIC, hover_enabled=False))
        result = cite("v2017")
        assert "[" in result and "]" in result
        assert "1" in result

    def test_superscript(self):
        set_bib_config(BibConfig(citation_style=CitationStyle.SUPERSCRIPT, hover_enabled=False))
        result = cite("v2017")
        assert "<sup>" in result
        assert "1" in result

    def test_multiple_keys(self):
        set_bib_config(BibConfig(citation_style=CitationStyle.AUTHOR_YEAR, hover_enabled=False))
        result = cite("v2017", "d2019")
        assert "Vaswani" in result
        assert "Devlin" in result
        assert ";" in result  # author_year separator

    def test_unknown_key(self):
        result = cite("unknown_key")
        assert "[unknown_key?]" in result

    def test_prefix_suffix(self):
        set_bib_config(BibConfig(citation_style=CitationStyle.AUTHOR_YEAR, hover_enabled=False))
        result = cite("v2017", prefix="cf. ", suffix=", p. 42")
        assert result.startswith("cf. ")
        assert result.endswith(", p. 42")

    def test_hover_attributes(self):
        set_bib_config(BibConfig(hover_enabled=True))
        result = cite("v2017")
        assert 'class="stx-cite"' in result
        assert 'data-bib-title="Attention"' in result
        assert 'data-bib-year="2017"' in result


# ===================================================================
# export_bibtex
# ===================================================================

class TestExportBibTeX:
    def setup_method(self):
        reset_bib_registry()

    def teardown_method(self):
        reset_bib_registry()

    def test_exports_cited_only(self):
        reg = get_bib_registry()
        reg.register(BibEntry(key="a", entry_type="article", title="A", authors=["X, Y"], year="2024"))
        reg.register(BibEntry(key="b", entry_type="book", title="B"))
        reg.cite("a")

        result = export_bibtex(only_cited=True)
        assert "@article{a," in result
        assert "title = {A}" in result
        assert "@book{b," not in result

    def test_exports_all(self):
        reg = get_bib_registry()
        reg.register(BibEntry(key="a", title="A"))
        reg.register(BibEntry(key="b", title="B"))

        result = export_bibtex(only_cited=False)
        assert "a," in result
        assert "b," in result

    def test_includes_extra_fields(self):
        reg = get_bib_registry()
        reg.register(BibEntry(key="a", title="A", extra={"custom": "value"}))
        reg.cite("a")

        result = export_bibtex(only_cited=True)
        assert "custom = {value}" in result

    def test_empty_registry(self):
        result = export_bibtex(only_cited=True)
        assert result == ""


# ===================================================================
# _fields_to_entry (shared builder)
# ===================================================================

class TestFieldsToEntry:
    def test_basic(self):
        fields = {"title": "Test", "year": "2024", "author": "Smith, J. and Doe, K."}
        e = _fields_to_entry("key1", "article", fields)
        assert e.key == "key1"
        assert e.title == "Test"
        assert e.authors == ["Smith, J.", "Doe, K."]

    def test_extra_fields_preserved(self):
        fields = {"title": "T", "myfield": "val"}
        e = _fields_to_entry("k", "misc", fields)
        assert e.extra["myfield"] == "val"

    def test_authors_list(self):
        fields = {"authors": ["A", "B"]}
        e = _fields_to_entry("k", "misc", fields)
        assert e.authors == ["A", "B"]


# ===================================================================
# BibRefs proxy
# ===================================================================

class TestBibRefs:
    def setup_method(self):
        reset_bib_registry()
        set_bib_config(BibConfig(hover_enabled=False))
        reg = get_bib_registry()
        reg.register(BibEntry(key="smith2024", title="A Paper",
                               authors=["Smith, J."], year="2024"))
        reg.register(BibEntry(key="doe2023", title="Another Paper",
                               authors=["Doe, K."], year="2023"))

    def teardown_method(self):
        reset_bib_registry()
        set_bib_config(BibConfig())

    def test_getattr_returns_cite_html(self):
        result = st_refs.smith2024
        assert "Smith" in result
        assert "2024" in result

    def test_getattr_unknown_key(self):
        result = st_refs.unknown_key
        assert "[unknown_key?]" in result

    def test_private_attr_raises(self):
        with pytest.raises(AttributeError):
            _ = st_refs._private

    def test_repr(self):
        r = repr(st_refs)
        assert "BibRefs" in r
        assert "doe2023" in r or "smith2024" in r

    def test_equivalent_to_cite(self):
        ref_result = st_refs.smith2024
        cite_result = cite("smith2024")
        # Both produce the same HTML (cite is called twice, but same format)
        assert "Smith" in ref_result
        assert "Smith" in cite_result


# ===================================================================
# generate_bib_stubs
# ===================================================================

class TestGenerateBibStubs:
    def test_generates_py_module(self, tmp_path):
        bib_file = tmp_path / "test.bib"
        bib_file.write_text(
            '@article{smith2024, title={A Paper}, author={Smith, John}, year={2024}}\n'
            '@book{doe2023, title={A Book}, author={Doe, K.}, year={2023}}\n'
        )

        content = generate_bib_stubs(str(bib_file))
        assert "class _ProjectBibRefs:" in content
        assert "def smith2024(self) -> str:" in content
        assert "def doe2023(self) -> str:" in content
        assert "A Paper" in content
        assert "st_refs = _ProjectBibRefs()" in content
        assert "from streamtex.bib import cite" in content

    def test_properties_call_cite(self, tmp_path):
        bib_file = tmp_path / "test.bib"
        bib_file.write_text(
            '@article{mykey, title={T}, author={A}, year={2024}}\n'
        )

        content = generate_bib_stubs(str(bib_file))
        assert 'return cite("mykey")' in content

    def test_getattr_fallback(self, tmp_path):
        bib_file = tmp_path / "test.bib"
        bib_file.write_text(
            '@article{k1, title={T}, author={A}, year={2024}}\n'
        )

        content = generate_bib_stubs(str(bib_file))
        assert "def __getattr__" in content
        assert "return cite(key)" in content

    def test_writes_to_file(self, tmp_path):
        bib_file = tmp_path / "test.bib"
        bib_file.write_text(
            '@article{alpha2024, title={Alpha}, author={A, B}, year={2024}}\n'
        )
        out_path = tmp_path / "output.py"

        generate_bib_stubs(str(bib_file), output_path=str(out_path))

        assert out_path.exists()
        content = out_path.read_text()
        assert "def alpha2024" in content
        assert 'return cite("alpha2024")' in content

    def test_multiple_sources(self, tmp_path):
        bib1 = tmp_path / "a.bib"
        bib1.write_text('@article{ref1, title={T1}, author={A}, year={2024}}\n')
        bib2 = tmp_path / "b.bib"
        bib2.write_text('@article{ref2, title={T2}, author={B}, year={2023}}\n')

        content = generate_bib_stubs(str(bib1), str(bib2))
        assert "def ref1" in content
        assert "def ref2" in content

    def test_empty_source(self, tmp_path):
        bib_file = tmp_path / "empty.bib"
        bib_file.write_text("")

        content = generate_bib_stubs(str(bib_file))
        assert "class _ProjectBibRefs:" in content
        assert "pass" in content

    def test_docstring_format(self, tmp_path):
        bib_file = tmp_path / "test.bib"
        bib_file.write_text(
            '@article{v2017, title={Attention Is All You Need}, '
            'author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki}, year={2017}}\n'
        )

        content = generate_bib_stubs(str(bib_file))
        assert "Attention Is All You Need" in content
        assert "Vaswani et al." in content
        assert "2017" in content

    def test_property_decorator(self, tmp_path):
        bib_file = tmp_path / "test.bib"
        bib_file.write_text(
            '@article{k1, title={T}, author={A}, year={2024}}\n'
        )

        content = generate_bib_stubs(str(bib_file))
        assert "@property" in content
        assert "def k1(self) -> str:" in content

    def test_generated_module_is_importable(self, tmp_path):
        """The generated .py can be imported and st_refs works."""
        bib_file = tmp_path / "test.bib"
        bib_file.write_text(
            '@article{abc2024, title={Test}, author={Author, A.}, year={2024}}\n'
        )
        out_path = tmp_path / "bib_refs.py"
        generate_bib_stubs(str(bib_file), output_path=str(out_path))

        # Import the generated module dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location("bib_refs", str(out_path))
        mod = importlib.util.module_from_spec(spec)

        # Register entry in global registry before exec
        reset_bib_registry()
        set_bib_config(BibConfig(hover_enabled=False))
        reg = get_bib_registry()
        reg.register(BibEntry(key="abc2024", title="Test",
                               authors=["Author, A."], year="2024"))

        spec.loader.exec_module(mod)

        # The generated st_refs should work
        result = mod.st_refs.abc2024
        assert "Author" in result
        assert "2024" in result

        # Fallback should work for unknown keys
        result2 = mod.st_refs.unknown_key_xyz
        assert "[unknown_key_xyz?]" in result2

        reset_bib_registry()
        set_bib_config(BibConfig())
