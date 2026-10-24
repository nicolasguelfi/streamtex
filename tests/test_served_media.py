"""A local video or sound under the app's static folder is served, not read into memory (#140)."""

import os
import textwrap
from unittest.mock import patch

import pytest

import streamtex.export as export_mod
from streamtex.export import (
    AssetCollector,
    ExportConfig,
    generate_export_html,
    materialize_served_media,
    reset_export_buffer,
)
from streamtex.export_widgets import _live_source, _static_rel, st_audio, st_video


@pytest.fixture
def app(tmp_path):
    """A project folder with ``static/media/clip.mp4`` and a video outside ``static``."""
    media = tmp_path / "static" / "media"
    media.mkdir(parents=True)
    (media / "clip.mp4").write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64)
    (media / "my talk.mp4").write_bytes(b"\x00" * 16)
    (media / "voice.mp3").write_bytes(b"ID3" + b"\x00" * 16)
    (tmp_path / "outside.mp4").write_bytes(b"\x00" * 16)
    with patch("streamtex.image_crop._app_static_dir", return_value=str(tmp_path / "static")):
        yield tmp_path


@pytest.fixture
def serving():
    with patch("streamtex.export_widgets.st.get_option", return_value=True) as opt:
        yield opt


class TestLiveSource:
    def test_a_file_of_static_gets_its_url(self, app, serving):
        assert _live_source(str(app / "static/media/clip.mp4")) == "/app/static/media/clip.mp4"

    def test_a_relative_path_and_a_pathlib_path(self, app, serving, monkeypatch):
        monkeypatch.chdir(app)
        assert _live_source("static/media/clip.mp4") == "/app/static/media/clip.mp4"
        assert _live_source(app / "static/media/clip.mp4") == "/app/static/media/clip.mp4"

    def test_spaces_are_encoded(self, app, serving):
        assert _live_source(str(app / "static/media/my talk.mp4")) == "/app/static/media/my%20talk.mp4"

    def test_a_file_outside_static_is_passed_on(self, app, serving):
        path = str(app / "outside.mp4")
        assert _live_source(path) == path

    def test_without_static_serving_the_path_is_passed_on(self, app):
        path = str(app / "static/media/clip.mp4")
        with patch("streamtex.export_widgets.st.get_option", return_value=False):
            assert _live_source(path) == path

    def test_urls_bytes_and_missing_files_are_passed_on(self, app, serving):
        for data in ("https://example.com/v.mp4", b"\x00", str(app / "static/media/none.mp4")):
            assert _live_source(data) is data

    def test_a_link_leaving_static_is_not_served(self, app, serving):
        link = app / "static" / "media" / "linked.mp4"
        link.symlink_to(app / "outside.mp4")
        assert _static_rel(str(link)) is None

    def test_a_linked_folder_inside_static_is_served(self, app, serving):
        (app / "static" / "clips").symlink_to(app / "static" / "media")
        assert _live_source(str(app / "static/clips/clip.mp4")) == "/app/static/clips/clip.mp4"

    def test_a_file_over_streamlit_limit_is_not_served(self, app, serving):
        with patch("streamtex.export_widgets._SERVED_MAX_BYTES", 8):
            assert _static_rel(str(app / "static/media/clip.mp4")) is None


@patch("streamtex.export_widgets.st")
class TestWidgets:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_st_video_gives_streamlit_the_url(self, mock_st, app):
        mock_st.get_option.return_value = True
        st_video(str(app / "static/media/clip.mp4"), autoplay=True, muted=True)
        mock_st.video.assert_called_once_with("/app/static/media/clip.mp4", autoplay=True, muted=True)

    def test_a_boxed_and_a_staged_video_too(self, mock_st, app):
        mock_st.get_option.return_value = True
        st_video(str(app / "static/media/clip.mp4"), width="60vw")
        st_video(str(app / "static/media/clip.mp4"), theater=True)
        assert [c.args[0] for c in mock_st.video.call_args_list] == ["/app/static/media/clip.mp4"] * 2

    def test_st_audio_too(self, mock_st, app):
        mock_st.get_option.return_value = True
        st_audio(str(app / "static/media/voice.mp3"))
        mock_st.audio.assert_called_once_with("/app/static/media/voice.mp3")

    def test_the_export_writes_the_served_path(self, mock_st, app):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(str(app / "static/media/clip.mp4"))
        html = generate_export_html()
        assert '<source src="app/static/media/clip.mp4" type="video/mp4">' in html
        assert "base64" not in html

    def test_the_export_still_inlines_a_file_outside_static(self, mock_st, app):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(str(app / "outside.mp4"))
        assert "data:video/mp4;base64," in generate_export_html()

    def test_the_exported_file_lands_in_data(self, mock_st, app, monkeypatch):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(str(app / "static/media/clip.mp4"))
        monkeypatch.chdir(app)
        collector = AssetCollector()
        html = materialize_served_media(generate_export_html(), collector, project_root=str(app))
        assert 'src="data/' in html and ".mp4" in html
        assert "app/static/" not in html


SCRIPT = textwrap.dedent("""
    import streamlit as st
    from streamtex import st_video
    st_video("static/media/clip.mp4")
""")


@pytest.mark.parametrize("serving", [True, False])
def test_streamlit_never_reads_the_served_video(tmp_path, monkeypatch, serving):
    """Real Streamlit: the media file manager never opens a served file; without
    static serving it reads it, as before."""
    from streamlit import config
    from streamlit.runtime.memory_media_file_storage import MemoryMediaFileStorage
    from streamlit.testing.v1 import AppTest

    media = tmp_path / "static" / "media"
    media.mkdir(parents=True)
    (media / "clip.mp4").write_bytes(b"\x00" * 1024)
    (tmp_path / "book.py").write_text(SCRIPT)
    monkeypatch.chdir(tmp_path)
    reads = []
    original = MemoryMediaFileStorage._read_file

    def spy(self, path):
        reads.append(os.path.basename(str(path)))
        return original(self, path)

    monkeypatch.setattr(MemoryMediaFileStorage, "_read_file", spy)
    before = config.get_option("server.enableStaticServing")
    config.set_option("server.enableStaticServing", serving)
    try:
        at = AppTest.from_file(str(tmp_path / "book.py")).run()
    finally:
        config.set_option("server.enableStaticServing", before)
    assert not at.exception
    url = at.get("video")[0].proto.url
    if serving:
        assert reads == [] and url == "/app/static/media/clip.mp4"
    else:
        assert reads == ["clip.mp4"] and "/media/" in url
