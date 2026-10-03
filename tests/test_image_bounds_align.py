"""st_image(max_vw=, max_vh=, align=): bounds from the natural ratio, explicit placement (#82, #83)."""

import os
from unittest.mock import patch

import pytest

from streamtex.image import st_image
from streamtex.styles import Style


def _capture(captured):
    def _fake(html, **_kw):
        captured.append(html)
    return _fake


def _png(path, w, h):
    from PIL import Image

    Image.new("RGB", (w, h), (200, 100, 50)).save(path)
    return str(path)


def test_image_without_new_params_is_byte_identical(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(uri="https://example.com/a.png", width="300px", alt="x")
    assert captured == ['<img src="https://example.com/a.png" alt="x" style=" width: 300px; height: auto;">']


def test_image_bounds_use_the_natural_ratio(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    uri = _png(tmp_path / "wide.png", 200, 100)          # ratio 2
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(uri="./wide.png", max_vw=80, max_vh=40)
        st_image(uri="./wide.png", max_vh=50, natural_size=(300, 100))   # explicit ratio 3
    assert "width: min(100%, 80vw, calc(40vh * 2.000000)); height: auto;" in captured[0]
    assert "width: min(100%, calc(50vh * 3.000000)); height: auto;" in captured[1]
    assert os.path.isfile(uri)


def test_image_bounds_without_natural_size_fall_back_to_css_limits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(uri="https://example.com/a.png", max_vw=50, max_vh=30)
    assert "width: auto; height: auto; max-width: min(100%, 50vw); max-height: 30vh;" in captured[0]


def test_image_bounds_follow_the_cropped_zone(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _png(tmp_path / "tall.png", 100, 200)
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(uri="./tall.png", max_vh=50, crop=(0, 0, 50, 0))   # visible 100x100 -> ratio 1
    assert "calc(50vh * 1.000000)" in captured[0]


@pytest.mark.parametrize("kwargs, msg", [
    ({"max_vh": 0}, "positive"),
    ({"max_vw": -5}, "positive"),
    ({"max_vh": 40, "height": "300px"}, "incompatible"),
    ({"align": "middle"}, "align="),
])
def test_image_bound_and_align_validation(kwargs, msg, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("streamtex.image._render"), pytest.raises(ValueError, match=msg):
        st_image(uri="https://example.com/a.png", **kwargs)


def test_align_places_the_image_and_style_text_align_stays_a_no_op(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    captured = []
    with patch("streamtex.image._render", side_effect=_capture(captured)):
        st_image(Style("text-align: center;", "c"), uri="https://example.com/a.png", width="50%")
        st_image(uri="https://example.com/a.png", width="50%", align="right")
    assert "stx-image-align" not in captured[0]           # unchanged: no inferred placement
    assert captured[1].startswith('<div class="stx-image-align" style="text-align: right; width: 100%; line-height: 0;">')
