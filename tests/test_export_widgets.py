"""Unit tests for streamtex.export_widgets — export-aware widget helpers."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import streamtex.export as export_mod
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
from streamtex.export_widgets import (
    _dataframe_to_html,
    _to_dataframe,
    st_area_chart,
    st_audio,
    st_bar_chart,
    st_dataframe,
    st_graphviz,
    st_json,
    st_line_chart,
    st_metric,
    st_scatter_chart,
    st_table,
    st_video,
)

# ---------------------------------------------------------------------------
# _to_dataframe
# ---------------------------------------------------------------------------

class TestToDataframe:
    def test_dict_input(self):
        result = _to_dataframe({"a": [1, 2], "b": [3, 4]})
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["a", "b"]

    def test_dataframe_passthrough(self):
        df = pd.DataFrame({"x": [10]})
        result = _to_dataframe(df)
        assert result is df

    def test_list_input(self):
        result = _to_dataframe([{"a": 1}, {"a": 2}])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# _dataframe_to_html
# ---------------------------------------------------------------------------

class TestDataframeToHtml:
    def test_css_class(self):
        df = pd.DataFrame({"col": [1]})
        html = _dataframe_to_html(df)
        assert 'class="dataframe stx-table"' in html

    def test_no_index(self):
        df = pd.DataFrame({"col": [1, 2]})
        html = _dataframe_to_html(df)
        # Index column values should not appear as row headers
        assert "<th>0</th>" not in html
        assert "<th>1</th>" not in html


# ---------------------------------------------------------------------------
# st_dataframe
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestStDataframe:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_calls_st_dataframe(self, mock_st):
        data = {"a": [1]}
        st_dataframe(data)
        mock_st.dataframe.assert_called_once_with(data)

    def test_noop_when_inactive(self, mock_st):
        st_dataframe({"a": [1]})
        assert generate_export_html() is None

    def test_appends_when_active(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_dataframe({"a": [1, 2]})
        html = generate_export_html()
        assert "stx-table" in html
        assert "<table" in html


# ---------------------------------------------------------------------------
# st_table
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestStTable:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_calls_st_table(self, mock_st):
        data = {"a": [1]}
        st_table(data)
        mock_st.table.assert_called_once_with(data)

    def test_appends_when_active(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_table({"a": [1]})
        html = generate_export_html()
        assert "stx-table" in html


# ---------------------------------------------------------------------------
# st_metric
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestStMetric:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_calls_st_metric(self, mock_st):
        st_metric("Revenue", "$1M", delta="5%")
        mock_st.metric.assert_called_once_with("Revenue", "$1M", delta="5%")

    def test_no_delta(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_metric("Label", "42")
        html = generate_export_html()
        assert "stx-metric" in html
        # The class name appears in CSS, so check the div is not rendered
        assert '<div class="stx-metric-delta"' not in html

    def test_positive_delta(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_metric("Revenue", "$1M", delta="5")
        html = generate_export_html()
        assert "#09ab3b" in html  # green
        assert "&#9650;" in html  # up arrow

    def test_negative_delta(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_metric("Cost", "$500K", delta="-3")
        html = generate_export_html()
        assert "#ff2b2b" in html  # red
        assert "&#9660;" in html  # down arrow


# ---------------------------------------------------------------------------
# st_json
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestStJson:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_calls_st_json(self, mock_st):
        data = {"key": "value"}
        st_json(data)
        mock_st.json.assert_called_once_with(data)

    def test_appends_when_active(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_json({"key": "value"})
        html = generate_export_html()
        assert "stx-json" in html
        assert "key" in html
        assert "value" in html

    def test_string_input(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_json('{"raw": true}')
        html = generate_export_html()
        assert "stx-json" in html

    def test_html_escaping(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_json({"tag": "<script>alert(1)</script>"})
        html = generate_export_html()
        # The payload itself must not survive as markup.  The document
        # carries a <script> of its own since 0.7.34 (the list marker
        # mode), so the assertion targets the injected tag, not the tag
        # name anywhere in the page.
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html


# ---------------------------------------------------------------------------
# st_graphviz
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestStGraphviz:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_calls_st_graphviz_chart(self, mock_st):
        dot = "digraph { A -> B }"
        st_graphviz(dot)
        mock_st.graphviz_chart.assert_called_once_with(dot, use_container_width=True)

    @patch("streamtex.export_widgets.gv", create=True)
    def test_appends_svg_when_active(self, mock_gv, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        mock_source = MagicMock()
        mock_source.pipe.return_value = b"<svg>graph</svg>"
        mock_gv.Source.return_value = mock_source

        # Patch the import inside the function
        original_graphviz = None
        try:
            import graphviz as real_gv
            original_graphviz = real_gv
        except ImportError:
            pass

        dot = "digraph { A -> B }"
        st_graphviz(dot)
        html = generate_export_html()
        assert "stx-graphviz" in html

    def test_noop_when_inactive(self, mock_st):
        st_graphviz("digraph { A -> B }")
        assert generate_export_html() is None


# ---------------------------------------------------------------------------
# Chart helpers — line, bar, area, scatter
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestChartHelpers:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def _sample_data(self):
        return pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})

    def test_line_chart_calls_st(self, mock_st):
        data = self._sample_data()
        st_line_chart(data, x="x", y="y")
        mock_st.line_chart.assert_called_once()

    def test_bar_chart_calls_st(self, mock_st):
        data = self._sample_data()
        st_bar_chart(data, x="x", y="y")
        mock_st.bar_chart.assert_called_once()

    def test_area_chart_calls_st(self, mock_st):
        data = self._sample_data()
        st_area_chart(data, x="x", y="y")
        mock_st.area_chart.assert_called_once()

    def test_scatter_chart_calls_st(self, mock_st):
        data = self._sample_data()
        st_scatter_chart(data, x="x", y="y")
        mock_st.scatter_chart.assert_called_once()

    @patch("streamtex.export_widgets._chart_to_svg", return_value='<div class="stx-chart"><svg></svg></div>')
    def test_line_chart_exports_svg(self, mock_svg, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        data = self._sample_data()
        st_line_chart(data, x="x", y="y")
        html = generate_export_html()
        assert "stx-chart" in html

    @patch("streamtex.export_widgets._chart_to_svg", return_value='<div class="stx-chart"><svg></svg></div>')
    def test_bar_chart_exports_svg(self, mock_svg, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_bar_chart(self._sample_data(), x="x", y="y")
        html = generate_export_html()
        assert "stx-chart" in html

    @patch("streamtex.export_widgets._chart_to_svg", return_value='<div class="stx-chart"><svg></svg></div>')
    def test_area_chart_exports_svg(self, mock_svg, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_area_chart(self._sample_data(), x="x", y="y")
        html = generate_export_html()
        assert "stx-chart" in html

    @patch("streamtex.export_widgets._chart_to_svg", return_value='<div class="stx-chart"><svg></svg></div>')
    def test_scatter_chart_exports_svg(self, mock_svg, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_scatter_chart(self._sample_data(), x="x", y="y")
        html = generate_export_html()
        assert "stx-chart" in html

    def test_chart_noop_when_inactive(self, mock_st):
        st_line_chart(self._sample_data())
        assert generate_export_html() is None


# ---------------------------------------------------------------------------
# st_audio
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestStAudio:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_calls_st_audio(self, mock_st):
        st_audio("test.wav", format="audio/wav")
        mock_st.audio.assert_called_once_with("test.wav", format="audio/wav")

    def test_noop_when_inactive(self, mock_st):
        st_audio("test.wav")
        assert generate_export_html() is None

    def test_url_source(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_audio("https://example.com/audio.mp3", format="audio/mpeg")
        html = generate_export_html()
        assert "<audio" in html
        assert "https://example.com/audio.mp3" in html

    def test_bytes_source(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_audio(b"\x00\x01\x02", format="audio/wav")
        html = generate_export_html()
        assert "<audio" in html
        assert "data:audio/wav;base64," in html

    def test_remote_mp3_gets_its_type(self, mock_st):
        """#114: the same gap as st_video, for a remote audio file."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_audio("https://example.com/talk.mp3")
        assert '<source src="https://example.com/talk.mp3" type="audio/mpeg">' in generate_export_html()


# ---------------------------------------------------------------------------
# st_video
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestStVideo:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_calls_st_video(self, mock_st):
        st_video("test.mp4", format="video/mp4")
        mock_st.video.assert_called_once_with("test.mp4", format="video/mp4")

    def test_noop_when_inactive(self, mock_st):
        st_video("test.mp4")
        assert generate_export_html() is None

    def test_youtube_url(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        html = generate_export_html()
        assert "<iframe" in html
        assert "youtube.com/embed/dQw4w9WgXcQ" in html

    def test_youtube_short_url(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video("https://youtu.be/dQw4w9WgXcQ")
        html = generate_export_html()
        assert "<iframe" in html
        assert "youtube.com/embed/dQw4w9WgXcQ" in html

    def test_regular_url(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video("https://example.com/video.mp4", format="video/mp4")
        html = generate_export_html()
        assert "<video" in html
        assert "https://example.com/video.mp4" in html

    def test_plain_video_keeps_controls_only(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video("https://example.com/video.mp4", format="video/mp4")
        html = generate_export_html()
        assert "<video controls class=" in html
        assert "autoplay" not in html and "loop" not in html

    def test_autoplay_loop_muted_exported(self, mock_st):
        """A looping silent clip (a GIF replaced by a video) plays alone in the export too."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_video("https://example.com/clip.mp4", format="video/mp4", autoplay=True, loop=True, muted=True)
        mock_st.video.assert_called_once_with(
            "https://example.com/clip.mp4", format="video/mp4", autoplay=True, loop=True, muted=True)
        html = generate_export_html()
        assert "<video controls autoplay playsinline loop muted" in html
        assert "width:100%" in html

    def test_bytes_source(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(b"\x00\x01\x02", format="video/mp4")
        html = generate_export_html()
        assert "<video" in html
        assert "data:video/mp4;base64," in html

    @pytest.mark.parametrize("url,mime", [
        ("https://example.com/promptleon.mp4", "video/mp4"),
        ("https://example.com/clip.webm", "video/webm"),
        ("https://example.com/clip.OGG", "video/ogg"),
        ("https://example.com/clip.mp4?v=2#t=3", "video/mp4"),
    ])
    def test_remote_url_gets_its_type_from_the_extension(self, mock_st, url, mime):
        """#114: a remote video is not written as application/octet-stream."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(url)
        html = generate_export_html()
        assert f'<source src="{url}" type="{mime}">' in html
        assert "octet-stream" not in html

    def test_remote_url_without_extension_has_no_type(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video("https://example.com/video?id=42")
        html = generate_export_html()
        assert '<source src="https://example.com/video?id=42">' in html

    def test_format_given_by_the_author_wins(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video("https://example.com/video?id=42", format="video/webm")
        assert 'type="video/webm"' in generate_export_html()


# ---------------------------------------------------------------------------
# st_video / st_audio: width and align (#126), autoplay without muted (#35)
# ---------------------------------------------------------------------------

@patch("streamtex.export_widgets.st")
class TestMediaWidthAndAutoplay:
    def setup_method(self):
        import streamtex.export_widgets as ew
        export_mod._buffer = None
        ew._warned_autoplay = False

    def teardown_method(self):
        export_mod._buffer = None

    def _html(self, call):
        reset_export_buffer(ExportConfig(enabled=True))
        call()
        return generate_export_html()

    def test_autoplay_without_muted_is_muted_once_with_a_warning(self, mock_st, caplog):
        import logging
        with caplog.at_level(logging.WARNING, logger="streamtex.export_widgets"):
            html = self._html(lambda: (st_video("https://example.com/a.mp4", autoplay=True),
                                       st_video("https://example.com/b.mp4", autoplay=True)))
        assert mock_st.video.call_args_list[0].kwargs == {"autoplay": True, "muted": True}
        assert html.count("autoplay playsinline muted") == 2
        assert sum("needs muted=True" in r.message for r in caplog.records) == 1

    def test_muted_autoplay_unchanged(self, mock_st, caplog):
        st_video("https://example.com/a.mp4", autoplay=True, muted=True)
        mock_st.video.assert_called_once_with("https://example.com/a.mp4", autoplay=True, muted=True)
        assert "needs muted" not in caplog.text

    def test_no_width_keeps_the_full_width_output(self, mock_st):
        html = self._html(lambda: st_video("https://example.com/v.mp4"))
        assert '<div class="stx-block"' not in html and 'style="width:100%;max-width:100%"' in html

    @pytest.mark.parametrize("width,align,css", [
        ("50%", "center", "width:50%;max-width:100%;margin-left:auto;margin-right:auto;"),
        (800, "center", "width:800px;max-width:100%;margin-left:auto;margin-right:auto;"),
        ("60vw", "left", "width:60vw;max-width:100%;margin-right:auto;"),
        ("40%", "right", "width:40%;max-width:100%;margin-left:auto;"),
    ])
    def test_width_draws_a_sized_box(self, mock_st, width, align, css):
        html = self._html(lambda: st_video("https://example.com/v.mp4", width=width, align=align))
        box = html.index(css)
        assert html.index("<video", box) > box
        mock_st.video.assert_called_once_with("https://example.com/v.mp4")

    def test_youtube_in_a_box_fills_it(self, mock_st):
        html = self._html(lambda: st_video("https://youtu.be/dQw4w9WgXcQ", width="50%"))
        assert 'style="width:100%;height:auto;aspect-ratio:16/9"' in html
        assert 'width="560"' not in html

    def test_audio_in_a_box_fills_it(self, mock_st):
        html = self._html(lambda: st_audio("https://example.com/talk.mp3", width="30%", align="left"))
        assert "width:30%;max-width:100%;margin-right:auto;" in html
        assert '<audio controls class="stx-media" style="width:100%">' in html
        mock_st.audio.assert_called_once_with("https://example.com/talk.mp3")

    @pytest.mark.parametrize("kw", [{"width": "half"}, {"width": "50"}, {"width": True},
                                    {"width": 1.5}, {"align": "middle"}])
    def test_bad_width_or_align_is_refused(self, mock_st, kw):
        with pytest.raises(ValueError):
            st_video("https://example.com/v.mp4", **kw)
