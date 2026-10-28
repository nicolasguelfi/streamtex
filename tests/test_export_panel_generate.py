"""Export panel: one click on Generate is enough when the full document must be rebuilt first (#151)."""

from streamlit.testing.v1 import AppTest


def _app():
    def app():
        import streamlit as st

        from streamtex.book import _STX_FULL_EXPORT_HTML_KEY, _offer_export_downloads
        from streamtex.export import ExportConfig, HtmlExportBuffer, reset_export_buffer

        reset_export_buffer(ExportConfig(enabled=False))
        page = HtmlExportBuffer(ExportConfig(enabled=True))
        page.append("<p>CURRENT-PAGE</p>")
        full = HtmlExportBuffer(ExportConfig(enabled=True))
        full.append("<p>FULL-DOCUMENT</p>")

        def rebuild():                     # what st_book stores: the full export, built on demand
            st.session_state[_STX_FULL_EXPORT_HTML_KEY] = full.generate_full_html()

        if "_stx_rebuild_given" not in st.session_state:   # a new session: no full export yet
            st.session_state["_stx_rebuild_given"] = True
            st.session_state["_stx_export_rebuild_fn"] = rebuild
        _offer_export_downloads(page.generate_full_html(), "doc", paginated=True)

    return AppTest.from_function(app)


def test_one_click_generates_the_full_document():
    at = _app().run()
    next(c for c in at.checkbox if c.label.startswith("Enriched navigation")).uncheck()
    at.button[0].click().run()
    assert "_stx_export_doc" in at.session_state, "the first click produced nothing"
    html = at.session_state["_stx_export_doc"]["html"]
    assert "FULL-DOCUMENT" in html and "CURRENT-PAGE" not in html
