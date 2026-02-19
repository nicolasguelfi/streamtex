"""Unit tests for streamtex.export_widgets — export-aware widget helpers."""

from unittest.mock import patch, MagicMock
import json

import pandas as pd
import pytest

import streamtex.export as export_mod
from streamtex.export import ExportConfig, reset_export_buffer, generate_export_html, is_export_active
from streamtex.export_widgets import (
    _to_dataframe,
    _dataframe_to_html,
    st_dataframe,
    st_table,
    st_metric,
    st_json,
    st_graphviz,
    st_line_chart,
    st_bar_chart,
    st_area_chart,
    st_scatter_chart,
    st_audio,
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
        assert "<script>" not in html
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
        mock_st.graphviz_chart.assert_called_once_with(dot)

    @patch("streamtex.export_widgets.gv", create=True)
    def test_appends_svg_when_active(self, mock_gv, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        mock_source = MagicMock()
        mock_source.pipe.return_value = b"<svg>graph</svg>"
        mock_gv.Source.return_value = mock_source

        # Patch the import inside the function
        import streamtex.export_widgets as ew
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

    def test_bytes_source(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(b"\x00\x01\x02", format="video/mp4")
        html = generate_export_html()
        assert "<video" in html
        assert "data:video/mp4;base64," in html
