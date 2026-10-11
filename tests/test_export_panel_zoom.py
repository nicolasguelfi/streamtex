"""Export panel: "Zoom HTML (%)" fixes the zoom of the HTML file (#110)."""

from streamlit.testing.v1 import AppTest


def _app(html_zoom=0, view_zoom=100):
    def app(html_zoom, view_zoom):
        import streamlit as st

        from streamtex.book import _offer_export_downloads
        from streamtex.export import ExportConfig, HtmlExportBuffer, reset_export_buffer

        reset_export_buffer(ExportConfig(enabled=False))  # no asset collector left by another test
        st.session_state.setdefault("_stx_zoom", view_zoom)
        st.session_state.setdefault("_stx_page_width", 90)
        buf = HtmlExportBuffer(ExportConfig(enabled=True, zoom=view_zoom / 100, page_width="90%"))
        buf.append("<p>hello</p>")
        _offer_export_downloads(buf.generate_full_html(), "doc", html_zoom=html_zoom)

    return AppTest.from_function(app, kwargs={"html_zoom": html_zoom, "view_zoom": view_zoom})


def _generate(at, zoom=None):
    if zoom is not None:
        next(n for n in at.number_input if n.label == "Zoom HTML (%)").set_value(zoom)
    # plain HTML, no enrichment, keeps the check simple
    next(c for c in at.checkbox if c.label.startswith("Enriched navigation")).uncheck()
    at.button[0].click().run()
    return at.session_state["_stx_export_doc"]["html"]


def test_default_follows_the_view_zoom():
    at = _app(view_zoom=80).run()
    html = _generate(at)
    assert "zoom: 0.8;" in html
    assert ".streamtex-page { max-width" not in html.split("</style>")[-2]  # no override added


def test_fixed_html_zoom_replaces_the_view_zoom():
    at = _app(view_zoom=80).run()
    html = _generate(at, zoom=70)
    assert html.rstrip().count(".streamtex-page { max-width: 90%; zoom: 0.7; }") == 1


def test_starting_value_from_st_book():
    at = _app(html_zoom=60).run()
    field = next(n for n in at.number_input if n.label == "Zoom HTML (%)")
    assert field.value == 60
    assert "zoom: 0.6; }" in _generate(at)
