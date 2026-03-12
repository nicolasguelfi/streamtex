"""Tests for image_utils — base64 encoding, MIME detection, path helpers."""

import base64
import os
import tempfile


class TestIsUrl:
    def test_http_url(self):
        from streamtex.image_utils import _is_url
        assert _is_url("http://example.com/img.png") is True

    def test_https_url(self):
        from streamtex.image_utils import _is_url
        assert _is_url("https://example.com/img.png") is True

    def test_www_url(self):
        from streamtex.image_utils import _is_url
        assert _is_url("www.example.com/img.png") is True

    def test_local_path_not_url(self):
        from streamtex.image_utils import _is_url
        assert _is_url("/home/user/img.png") is False

    def test_relative_path_not_url(self):
        from streamtex.image_utils import _is_url
        assert _is_url("images/photo.jpg") is False


class TestIsAbsolutePath:
    def test_absolute_unix(self):
        from streamtex.image_utils import _is_absolute_path
        assert _is_absolute_path("/usr/local/img.png") is True

    def test_relative_not_absolute(self):
        from streamtex.image_utils import _is_absolute_path
        assert _is_absolute_path("images/photo.jpg") is False


class TestIsRelativePath:
    def test_dot_relative(self):
        from streamtex.image_utils import _is_relative_path
        assert _is_relative_path("./images/photo.jpg") is True

    def test_dotdot_relative(self):
        from streamtex.image_utils import _is_relative_path
        assert _is_relative_path("../images/photo.jpg") is True

    def test_slash_relative(self):
        from streamtex.image_utils import _is_relative_path
        assert _is_relative_path("/images/photo.jpg") is True

    def test_bare_name_not_relative(self):
        from streamtex.image_utils import _is_relative_path
        assert _is_relative_path("photo.jpg") is False


class TestGetMimeType:
    def test_png(self):
        from streamtex.image_utils import _get_mime_type
        assert _get_mime_type("image.png") == "image/png"

    def test_jpeg(self):
        from streamtex.image_utils import _get_mime_type
        result = _get_mime_type("photo.jpeg")
        assert result == "image/jpeg"

    def test_svg_fallback(self):
        from streamtex.image_utils import _get_mime_type
        result = _get_mime_type("icon.svg")
        assert result == "image/svg+xml"

    def test_webp_fallback(self):
        from streamtex.image_utils import _get_mime_type
        result = _get_mime_type("photo.webp")
        assert result == "image/webp"

    def test_unknown_extension(self):
        from streamtex.image_utils import _get_mime_type
        result = _get_mime_type("file.xyz")
        assert result is None

    def test_no_extension(self):
        from streamtex.image_utils import _get_mime_type
        result = _get_mime_type("noext")
        assert result is None


class TestGetBase64EncodedImage:
    def test_encodes_file(self, mock_streamlit):
        """Reads a file and returns base64 string."""
        from streamtex.image_utils import _get_base64_encoded_image

        content = b"fake image data"
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(content)
            path = f.name

        try:
            result = _get_base64_encoded_image.__wrapped__(path, 0)
            expected = base64.b64encode(content).decode("utf-8")
            assert result == expected
        finally:
            os.unlink(path)

    def test_nonexistent_file_returns_none(self, mock_streamlit):
        """Non-existent file returns None."""
        from streamtex.image_utils import _get_base64_encoded_image
        result = _get_base64_encoded_image.__wrapped__("/no/such/file.png", 0)
        assert result is None
