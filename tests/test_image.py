"""Tests for streamtex/image.py and streamtex/image_utils.py."""

import os
import base64
import pytest
from unittest.mock import patch, MagicMock, mock_open

from streamtex.image_utils import (
    _is_url,
    _is_absolute_path,
    _is_relative_path,
    _get_mime_type,
    _get_base64_encoded_image,
)


# ---------------------------------------------------------------------------
# image_utils — detection helpers
# ---------------------------------------------------------------------------

class TestIsUrl:
    def test_https_url(self):
        assert _is_url("https://example.com/img.png") is True

    def test_http_url(self):
        assert _is_url("http://example.com/img.png") is True

    def test_www_url(self):
        assert _is_url("www.example.com/img.png") is True

    def test_relative_path_is_not_url(self):
        assert _is_url("./images/photo.png") is False

    def test_bare_filename_is_not_url(self):
        assert _is_url("photo.png") is False

    def test_absolute_path_is_not_url(self):
        assert _is_url("/usr/local/share/photo.png") is False


class TestIsAbsolutePath:
    def test_unix_absolute(self):
        assert _is_absolute_path("/usr/local/images/photo.png") is True

    def test_relative_is_not_absolute(self):
        assert _is_absolute_path("./photo.png") is False

    def test_bare_filename_is_not_absolute(self):
        assert _is_absolute_path("photo.png") is False


class TestIsRelativePath:
    def test_dot_prefix(self):
        assert _is_relative_path("./file.txt") is True

    def test_dotdot_prefix(self):
        assert _is_relative_path("../file.txt") is True

    def test_slash_prefix(self):
        assert _is_relative_path("/file.txt") is True

    def test_backslash_prefix(self):
        assert _is_relative_path("\\file.txt") is True

    def test_bare_filename_is_not_relative(self):
        assert _is_relative_path("photo.png") is False

    def test_url_is_not_relative(self):
        assert _is_relative_path("https://example.com") is False


class TestGetMimeType:
    def test_png(self):
        assert _get_mime_type("photo.png") == "image/png"

    def test_jpeg(self):
        assert _get_mime_type("photo.jpeg") == "image/jpeg"

    def test_jpg(self):
        assert _get_mime_type("photo.jpg") == "image/jpeg"

    def test_gif(self):
        assert _get_mime_type("anim.gif") == "image/gif"

    def test_svg_fallback(self):
        # SVG may not be detected by mimetypes on all platforms; fallback dict covers it
        result = _get_mime_type("icon.svg")
        assert result == "image/svg+xml"

    def test_webp_fallback(self):
        result = _get_mime_type("photo.webp")
        assert result == "image/webp"

    def test_bmp_fallback(self):
        result = _get_mime_type("image.bmp")
        assert result == "image/bmp"

    def test_ico_fallback(self):
        result = _get_mime_type("favicon.ico")
        assert result in ("image/x-icon", "image/vnd.microsoft.icon")

    def test_unsupported_extension(self):
        assert _get_mime_type("file.xyz123") is None

    def test_no_extension(self):
        assert _get_mime_type("imagefile") is None


class TestGetBase64EncodedImage:
    def test_reads_file_and_returns_base64(self):
        fake_bytes = b"fake image data"
        expected = base64.b64encode(fake_bytes).decode("utf-8")
        with patch("builtins.open", mock_open(read_data=fake_bytes)):
            result = _get_base64_encoded_image("/fake/path/photo.png")
        assert result == expected

    def test_returns_none_on_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError("no file")):
            result = _get_base64_encoded_image("/nonexistent/path/photo.png")
        assert result is None

    def test_returns_none_on_permission_error(self):
        with patch("builtins.open", side_effect=PermissionError("denied")):
            result = _get_base64_encoded_image("/protected/photo.png")
        assert result is None


# ---------------------------------------------------------------------------
# image.py — get_image_src and st_image
# ---------------------------------------------------------------------------

class TestGetImageSrc:
    """Tests for streamtex.image.get_image_src."""

    def test_url_returned_directly(self):
        from streamtex.image import get_image_src
        result = get_image_src("https://example.com/img.png")
        assert result == "https://example.com/img.png"

    def test_http_url_returned_directly(self):
        from streamtex.image import get_image_src
        result = get_image_src("http://example.com/img.png")
        assert result == "http://example.com/img.png"

    def test_www_url_returned_directly(self):
        from streamtex.image import get_image_src
        result = get_image_src("www.example.com/img.png")
        assert result == "www.example.com/img.png"

    def test_missing_absolute_path_returns_empty(self):
        from streamtex.image import get_image_src
        with patch("os.path.exists", return_value=False):
            result = get_image_src("/nonexistent/photo.png")
        assert result == ""

    def test_existing_absolute_path_returns_data_uri(self):
        import streamtex.image as img_mod
        fake_bytes = b"PNG\x89data"
        fake_b64 = base64.b64encode(fake_bytes).decode("utf-8")
        with patch("os.path.exists", return_value=True), \
             patch.object(img_mod, "__get_mime_type", return_value="image/png"), \
             patch.object(img_mod, "__get_base64_encoded_image", return_value=fake_b64):
            result = img_mod.get_image_src("/valid/photo.png")
        assert result.startswith("data:image/png;base64,")
        assert fake_b64 in result

    def test_missing_relative_path_returns_empty(self):
        from streamtex.image import get_image_src
        with patch("os.path.exists", return_value=False):
            result = get_image_src("./images/photo.png")
        assert result == ""

    def test_static_name_falls_back_to_legacy_path(self):
        """A bare filename with no static sources should use the legacy path."""
        from streamtex.image import get_image_src
        with patch("streamtex.image.get_static_sources", return_value=[]), \
             patch("os.path.isfile", return_value=False):
            result = get_image_src("logo.png")
        assert "logo.png" in result

    def test_static_source_resolved_to_data_uri(self):
        """A bare filename found in a registered static source returns base64."""
        import streamtex.image as img_mod
        fake_bytes = b"PNG data"
        fake_b64 = base64.b64encode(fake_bytes).decode("utf-8")
        with patch("streamtex.image.get_static_sources", return_value=["/static"]), \
             patch("os.path.isfile", return_value=True), \
             patch.object(img_mod, "__get_mime_type", return_value="image/png"), \
             patch.object(img_mod, "__get_base64_encoded_image", return_value=fake_b64):
            result = img_mod.get_image_src("logo.png")
        assert result.startswith("data:image/png;base64,")
        assert fake_b64 in result


class TestConfigureImagePath:
    def test_configure_changes_base(self):
        from streamtex import image as img_mod
        original = img_mod._static_image_base
        try:
            img_mod.configure_image_path("custom/images")
            assert img_mod._static_image_base == "custom/images"
        finally:
            img_mod._static_image_base = original


def _capture_render(captured):
    """Side-effect for _render mock that accepts the light_bg kwarg."""
    def _side_effect(html, **kw):
        captured.append(html)
    return _side_effect


class TestStImage:
    """Tests for streamtex.image.st_image — mock _render to capture output."""

    def test_url_renders_img_tag(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png")
        assert len(captured) == 1
        assert '<img src="https://example.com/img.png"' in captured[0]

    def test_missing_image_renders_placeholder(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image.get_image_src", return_value=""), \
             patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="missing.png")
        assert len(captured) == 1
        assert "Image not found" in captured[0]
        assert "border" in captured[0]

    def test_integer_width_converted_to_px(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", width=200)
        assert "200px" in captured[0]

    def test_integer_height_converted_to_px(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", height=150)
        assert "150px" in captured[0]

    def test_alt_text_included(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", alt="My photo")
        assert 'alt="My photo"' in captured[0]

    def test_link_wraps_image(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", link="https://example.com")
        assert "https://example.com" in captured[0]

    def test_light_bg_default_false(self):
        """By default, light_bg is False (no assumption about image type)."""
        from streamtex.image import st_image
        mock_render = MagicMock()
        with patch("streamtex.image._render", mock_render):
            st_image(uri="https://example.com/photo.png")
        assert mock_render.call_args.kwargs.get("light_bg") is False

    def test_light_bg_true_passed_to_render(self):
        """When light_bg=True, it is forwarded to _render."""
        from streamtex.image import st_image
        mock_render = MagicMock()
        with patch("streamtex.image._render", mock_render):
            st_image(uri="https://example.com/diagram.svg", light_bg=True)
        assert mock_render.call_args.kwargs.get("light_bg") is True
