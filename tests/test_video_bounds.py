"""st_video(max_vw=, max_vh=, natural_size=): two bounds, the ratio read from the MP4 (#141)."""

import logging
import struct
from unittest.mock import patch

import pytest

import streamtex.export as export_mod
import streamtex.export_widgets as ew
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
from streamtex.export_widgets import _mp4_size, st_video


def _box(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I4s", 8 + len(payload), kind) + payload


def _tkhd(w: float, h: float, quarter_turn: bool = False, version: int = 0) -> bytes:
    times = b"\x00" * (8 if version == 0 else 16)
    duration = b"\x00" * (4 if version == 0 else 8)
    head = bytes([version, 0, 0, 3]) + times + b"\x00\x00\x00\x01" + b"\x00" * 4 + duration
    one, zero = 0x10000, 0
    a, b, c, d = (zero, one, -one, zero) if quarter_turn else (one, zero, zero, one)
    matrix = struct.pack(">9i", a, b, 0, c, d, 0, 0, 0, 0x40000000)
    rest = b"\x00" * 8 + b"\x00" * 8 + matrix + struct.pack(">II", int(w * 65536), int(h * 65536))
    return _box(b"tkhd", head + rest)


def _mp4(w=174, h=100, *, quarter_turn=False, audio_first=False, moov_last=False, mdat=64, version=0):
    traks = [_box(b"trak", _tkhd(w, h, quarter_turn, version))]
    if audio_first:
        traks.insert(0, _box(b"trak", _tkhd(0, 0)))
    moov = _box(b"moov", _box(b"mvhd", b"\x00" * 100) + b"".join(traks))
    parts = [_box(b"ftyp", b"isom\x00\x00\x02\x00"), moov, _box(b"mdat", b"\x00" * mdat)]
    if moov_last:
        parts[1], parts[2] = parts[2], parts[1]
    return b"".join(parts)


@pytest.fixture
def clip(tmp_path):
    def make(name="clip.mp4", **kw):
        path = tmp_path / name
        path.write_bytes(_mp4(**kw))
        return str(path)
    return make


class TestMp4Size:
    def test_the_picture_size(self, clip):
        assert _mp4_size(clip(), 1) == (174, 100)

    def test_a_version_1_header(self, clip):
        assert _mp4_size(clip(version=1), 1) == (174, 100)

    def test_the_audio_track_is_skipped(self, clip):
        assert _mp4_size(clip(audio_first=True), 1) == (174, 100)

    def test_a_quarter_turn_swaps_the_sides(self, clip):
        assert _mp4_size(clip(w=1920, h=1080, quarter_turn=True), 1) == (1080, 1920)

    def test_a_header_beyond_the_first_mib_is_not_read(self, clip):
        path = clip(moov_last=True, mdat=4096)
        with patch.object(ew, "_MP4_HEAD", 2048):
            assert ew._mp4_size.__wrapped__(path, 1) is None
        assert _mp4_size(path, 1) == (174, 100)        # within the head: found

    def test_not_an_mp4(self, tmp_path):
        path = tmp_path / "clip.webm"
        path.write_bytes(b"\x1aE\xdf\xa3" + b"\x00" * 64)
        assert _mp4_size(str(path), 1) is None


@patch("streamtex.export_widgets.st")
class TestStVideoBounds:
    def setup_method(self):
        export_mod._buffer = None
        ew._warned_ratio.clear()

    def teardown_method(self):
        export_mod._buffer = None

    def test_both_bounds_with_the_file_ratio(self, mock_st, clip):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(clip(), max_vw=100, max_vh=50)
        html = generate_export_html()
        assert "width:min(100%, 100vw, calc(50vh * 1.740000));max-width:100%" in html

    def test_width_takes_part(self, mock_st, clip):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(clip(), width="80%", max_vw=60)
        assert "width:min(80%, 60vw);" in generate_export_html()

    def test_natural_size_for_a_url(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video("https://example.com/v.mp4", max_vh=50, natural_size=(1600, 900))
        assert "calc(50vh * 1.777778)" in generate_export_html()

    def test_unreadable_ratio_warns_once_and_keeps_the_width_bound(self, mock_st, clip, caplog):
        path = clip(moov_last=True, mdat=4096)
        reset_export_buffer(ExportConfig(enabled=True))
        with patch.object(ew, "_MP4_HEAD", 2048), caplog.at_level(logging.WARNING):
            ew._mp4_size.cache_clear()
            st_video(path, max_vw=90, max_vh=50)
            st_video(path, max_vw=90, max_vh=50)
        ew._mp4_size.cache_clear()
        warnings = [r for r in caplog.records if "faststart" in r.getMessage()]
        assert len(warnings) == 1 and "natural_size" in warnings[0].getMessage()
        html = generate_export_html()
        assert "width:min(100%, 90vw);" in html and "vh" not in html.split("<video")[0]

    def test_without_bounds_nothing_changes(self, mock_st, clip):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(clip())
        assert "stx_media_box" not in generate_export_html()
        assert "min(" not in generate_export_html()

    def test_streamlit_gets_no_new_argument(self, mock_st, clip):
        path = clip()
        st_video(path, max_vw=100, max_vh=50, autoplay=True, muted=True)
        mock_st.video.assert_called_once()
        assert mock_st.video.call_args.kwargs == {"autoplay": True, "muted": True}

    def test_fullscreen_keeps_the_box(self, mock_st, clip):
        reset_export_buffer(ExportConfig(enabled=True))
        st_video(clip(), max_vh=25, fullscreen=True)
        html = generate_export_html()
        assert "calc(25vh * 1.740000)" in html and "stx-vbox" in html

    @pytest.mark.parametrize("kw,message", [
        ({"max_vw": 0}, "max_vw must be a positive"),
        ({"max_vh": -5}, "max_vh must be a positive"),
        ({"max_vh": True}, "max_vh must be a positive"),
        ({"natural_size": (16, 9)}, "natural_size= goes with"),
        ({"max_vh": 50, "natural_size": (16, 0)}, "natural_size must be"),
        ({"max_vh": 50, "natural_size": (16,)}, "natural_size must be"),
        ({"max_vh": 50, "theater": True}, "do not apply with theater"),
    ])
    def test_wrong_values_are_refused(self, mock_st, clip, kw, message):
        with pytest.raises(ValueError, match=message):
            st_video(clip(), **kw)
