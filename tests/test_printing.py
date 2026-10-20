"""Usage notice and print rules of a document: st_book(notice=, printable=) (#107)."""
import sys
import textwrap

import pytest
from click.testing import CliRunner
from streamlit.testing.v1 import AppTest

from streamtex.export_enrich import _build_sidebar_html
from streamtex.printing import (
    PRINT_KEY,
    PrintConfig,
    apply_html_print_rule,
    print_block_css,
    print_state,
    resolve_printable,
)

PAGE = "<html><head><style>p { color: red; }</style></head><body><p>x</p></body></html>"


class TestRules:
    def test_true_allows_everything(self):
        assert resolve_printable(True) == PrintConfig()

    def test_false_forbids_printing_and_pdf_but_keeps_the_html_download(self):
        assert resolve_printable(False) == PrintConfig(app_print=False, app_pdf=False,
                                                       html_print=False, app_html=True)

    def test_a_print_config_is_kept(self):
        cfg = PrintConfig(app_pdf=False)
        assert resolve_printable(cfg) is cfg

    @pytest.mark.parametrize("bad", [None, 0, "no", {"app_pdf": False}])
    def test_anything_else_is_refused(self, bad):
        with pytest.raises(TypeError, match="printable"):
            resolve_printable(bad)

    def test_the_notice_follows_the_language(self):
        notice = {"en": "For participants", "fr": "Réservé aux participants"}
        assert print_state(True, notice, "fr")["notice"] == "Réservé aux participants"
        assert print_state(True, notice, "en")["notice"] == "For participants"
        assert print_state(True, "Plain", None)["notice"] == "Plain"
        assert print_state()["notice"] == ""


class TestPrintRule:
    def test_allowed_leaves_the_file_unchanged(self):
        assert apply_html_print_rule(PAGE, print_state(True, "n")) == PAGE

    def test_forbidden_prints_the_notice_alone(self):
        out = apply_html_print_rule(PAGE, print_state(False, "For participants"))
        style = out.split("<style>")[1].split("</style>")[0]
        assert "@media print" in style and "body > * { display: none !important; }" in style
        assert 'content: "For participants"' in style
        assert out.count("</style>") == 1 and "<p>x</p>" in out    # the page itself is untouched

    def test_only_html_print_matters_for_the_file(self):
        state = print_state(PrintConfig(app_print=False, app_pdf=False), "n")
        assert apply_html_print_rule(PAGE, state) == PAGE

    def test_a_file_without_style_gets_one(self):
        out = apply_html_print_rule("<html><head></head><body></body></html>", print_state(False))
        assert "<style>\n@media print" in out and out.index("@media") < out.index("</head>")

    def test_the_notice_cannot_break_out_of_the_css_string(self):
        css = print_block_css('a "quote" \\ </style><script>x</script>\nline 2')
        assert "</style>" not in css and "<script>" not in css
        assert 'content: "a \\"quote\\" \\\\ \\3C /style>\\3C script>x\\3C /script>\\A line 2"' in css


class TestExportSidebar:
    TOC = [{"level": 1, "key_anchor": "a", "title": "A"}]

    def test_the_notice_sits_under_the_version(self):
        html = _build_sidebar_html(self.TOC, doc_version="1.0", lib_version="0.7",
                                   notice="Réservé <b>aux</b> participants")
        assert html.index("docs 1.0") < html.index('class="stx-notice"')
        assert "Réservé &lt;b&gt;aux&lt;/b&gt; participants" in html

    def test_no_notice_no_line(self):
        assert "stx-notice" not in _build_sidebar_html(self.TOC, doc_version="1.0")


# -- the "Download as..." panel of the app ---------------------------------------------

def _panel(rules):
    def app(rules):
        import streamlit as st

        from streamtex.book import _offer_export_downloads
        from streamtex.export import ExportConfig, HtmlExportBuffer, reset_export_buffer

        reset_export_buffer(ExportConfig(enabled=False))
        st.session_state["_stx_print"] = rules
        buf = HtmlExportBuffer(ExportConfig(enabled=True))
        buf.append("<p>hello</p>")
        _offer_export_downloads(buf.generate_full_html(), "doc")

    return AppTest.from_function(app, kwargs={"rules": rules}).run()


def _boxes(at):
    return [c.label for c in at.checkbox if c.label in ("HTML", "PDF")]


def test_panel_without_pdf_offers_html_only(monkeypatch):
    monkeypatch.setattr("streamtex.book._is_pdf_available", lambda: True)
    at = _panel(print_state(PrintConfig(app_pdf=False)))
    assert "HTML" in _boxes(at) and "PDF" not in _boxes(at)
    assert not any("streamtex[pdf]" in c.value for c in at.caption)


def test_panel_without_html_download():
    at = _panel(print_state(PrintConfig(app_html=False)))
    assert "HTML" not in _boxes(at)


def test_panel_disappears_with_nothing_to_offer():
    at = _panel(print_state(PrintConfig(app_html=False, app_pdf=False)))
    assert not at.expander and not at.button


def test_downloaded_html_carries_the_print_rule_and_the_notice():
    at = _panel(print_state(False, "For participants"))
    at.button[0].click().run()
    html = at.session_state["_stx_export_doc"]["html"]
    assert 'content: "For participants"' in html
    assert 'class="stx-notice"' not in html          # no sidebar in this one-block file


# -- st_book in the live app -----------------------------------------------------------

def _book(**book_kwargs):
    def app(book_kwargs):
        import types

        import streamtex as stx

        blk = types.ModuleType("bck_print_demo")
        blk.build = lambda **k: stx.st_write("body text")
        stx.st_book([blk], export=False, loading=False, **book_kwargs)

    return AppTest.from_function(app, kwargs={"book_kwargs": book_kwargs}).run()


@pytest.fixture
def side(mock_streamlit):
    """What the book wrote with st.markdown (patched for every test by conftest)."""
    return lambda: "\n".join(str(c.args[0]) for c in mock_streamlit["markdown"].call_args_list if c.args)


def test_live_app_shows_the_notice_and_blocks_printing(side):
    at = _book(notice="For participants", printable=False)
    assert not at.exception
    side = side()
    assert 'class="stx-notice"' in side and "For participants" in side
    assert "@media print" in side
    assert at.session_state[PRINT_KEY]["app_pdf"] is False


def test_live_app_printable_by_default(side):
    at = _book()
    assert not at.exception
    side = side()
    assert "@media print" not in side and "stx-notice" not in side


def test_live_app_can_allow_printing_and_keep_the_notice(side):
    at = _book(notice="Note", printable=PrintConfig(html_print=False))
    side = side()
    assert "stx-notice" in side and "@media print" not in side


def test_a_wrong_printable_stops_the_book():
    at = _book(printable="no")
    assert at.exception and "printable" in at.exception[0].message


# -- stx export html --------------------------------------------------------------------

@pytest.fixture
def module(tmp_path):
    def make(book_args):
        p = tmp_path / "deck"
        (p / "blocks").mkdir(parents=True)
        (p / "blocks" / "__init__.py").write_text("")
        (p / "blocks" / "bck_one.py").write_text(textwrap.dedent("""
            import streamtex as stx
            def build(**k):
                stx.st_marker("bck_one")
                stx.st_write("text-one", toc_lvl="1")
        """))
        (p / "book.py").write_text(textwrap.dedent(f"""
            import streamtex as stx
            from blocks import bck_one
            stx.st_book([bck_one], toc_config=stx.TOCConfig(), marker_config=stx.MarkerConfig(),
                        doc_version="1.0", {book_args})
        """))
        return p
    yield make
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def _export(project, out):
    from streamtex.cli.export_cmd import export_html
    r = CliRunner().invoke(export_html, [str(project), "-o", str(out)])
    assert r.exit_code == 0, r.output
    return r


def test_cli_export_not_printable(module, tmp_path):
    _export(module('notice={"en": "For participants", "fr": "Participants"}, printable=False,'
                   ' html_export_mode="both"'), tmp_path / "out")
    files = list((tmp_path / "out").rglob("*.html"))
    assert len(files) >= 2                               # continuous + its page files
    for f in files:
        html = f.read_text()
        assert 'content: "For participants"' in html, f
        assert 'class="stx-notice"' in html and html.index("docs 1.0") < html.index("stx-notice")


def test_cli_export_printable_with_a_notice(module, tmp_path):
    _export(module('notice="For participants"'), tmp_path / "out")
    html = (tmp_path / "out" / "deck" / "deck.html").read_text()
    assert "stx-notice" in html and 'content: "For participants"' not in html


def test_cli_export_without_settings_is_unchanged(module, tmp_path):
    _export(module("printable=True"), tmp_path / "out")
    html = (tmp_path / "out" / "deck" / "deck.html").read_text()
    assert "stx-notice" not in html and "body::before" not in html


def test_panel_pdf_is_whole_when_only_html_printing_is_off(monkeypatch):
    seen = {}

    def fake_pdf(html, **kw):
        seen["html"] = html
        return b"%PDF"

    monkeypatch.setattr("streamtex.book._is_pdf_available", lambda: True)
    monkeypatch.setattr("streamtex.pdf_export.export_pdf", fake_pdf)
    at = _panel(print_state(PrintConfig(html_print=False), "n"))
    next(c for c in at.checkbox if c.label == "PDF").check().run()
    at.button[0].click().run()
    assert "hello" in seen["html"] and "body::before" not in seen["html"]
    assert "body::before" in at.session_state["_stx_export_doc"]["html"]
