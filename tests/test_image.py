"""Tests for streamtex/image.py and streamtex/image_utils.py."""

import base64
from unittest.mock import MagicMock, mock_open, patch

from streamtex.image_utils import (
    _get_base64_encoded_image,
    _get_mime_type,
    _is_absolute_path,
    _is_relative_path,
    _is_url,
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
             patch("os.path.getmtime", return_value=1234567890.0), \
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
             patch("os.path.getmtime", return_value=1234567890.0), \
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


# ===================================================================
# st_image — AI auto_generate integration
# ===================================================================

class TestStImageAutoGenerate:
    """Tests for the auto_generate fallback in st_image(prompt=..., auto_generate=True)."""

    def test_cached_prompt_renders_image(self):
        """prompt + cached → image rendered via cache, no API call."""
        from streamtex.image import st_image
        captured = []
        fake_path = "/tmp/cached.png"
        with patch("streamtex.image.get_image_src", side_effect=["", "data:image/png;base64,AA=="]), \
             patch("streamtex.image._render", side_effect=_capture_render(captured)), \
             patch("streamtex.ai.generate.is_cached", return_value=True), \
             patch("streamtex.ai.generate.generate_image", return_value=fake_path):
            result = st_image(uri="", prompt="a cat")
        assert len(captured) == 1
        assert "<img" in captured[0]

    def test_auto_generate_true_calls_api(self):
        """prompt + not cached + auto_generate=True → API called."""
        from streamtex.ai.config import AIImageConfig, set_ai_image_config
        from streamtex.image import st_image
        captured = []
        fake_path = "/tmp/gen.png"
        cfg = AIImageConfig(auto_generate=True)
        set_ai_image_config(cfg)
        try:
            with patch("streamtex.image.get_image_src", side_effect=["", "data:image/png;base64,AA=="]), \
                 patch("streamtex.image._render", side_effect=_capture_render(captured)), \
                 patch("streamtex.ai.generate.is_cached", return_value=False), \
                 patch("streamtex.ai.generate.generate_image", return_value=fake_path):
                st_image(uri="", prompt="a sunset")
            assert len(captured) == 1
            assert "<img" in captured[0]
        finally:
            set_ai_image_config(None)

    def test_auto_generate_false_shows_placeholder(self):
        """prompt + not cached + auto_generate=False → placeholder."""
        from streamtex.ai.config import AIImageConfig, set_ai_image_config
        from streamtex.image import st_image
        captured = []
        cfg = AIImageConfig(auto_generate=False)
        set_ai_image_config(cfg)
        try:
            with patch("streamtex.image.get_image_src", return_value=""), \
                 patch("streamtex.image._render", side_effect=_capture_render(captured)), \
                 patch("streamtex.ai.generate.is_cached", return_value=False):
                st_image(uri="", prompt="a sunset")
            assert len(captured) == 1
            assert "Image not found" in captured[0]
        finally:
            set_ai_image_config(None)

    def test_auto_generate_saves_managed_version(self):
        """prompt + name + auto_generate=True → save_version() called."""
        from streamtex.ai.config import AIImageConfig, set_ai_image_config
        from streamtex.image import st_image
        cfg = AIImageConfig(auto_generate=True)
        set_ai_image_config(cfg)
        try:
            with patch("streamtex.image.get_image_src", side_effect=["", "data:image/png;base64,AA=="]), \
                 patch("streamtex.image._render"), \
                 patch("streamtex.ai.generate.is_cached", return_value=False), \
                 patch("streamtex.ai.generate.generate_image", return_value="/tmp/g.png"), \
                 patch("streamtex.ai.history.save_version") as mock_save:
                st_image(uri="", prompt="a cat", editable=True, name="hero")
            mock_save.assert_called_once()
            assert mock_save.call_args.kwargs["prompt"] == "a cat"
        finally:
            set_ai_image_config(None)

    def test_no_prompt_no_generation(self):
        """uri= without prompt → classic placeholder, no AI logic."""
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image.get_image_src", return_value=""), \
             patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="missing.png")
        assert len(captured) == 1
        assert "Image not found" in captured[0]


# ===================================================================
# st_image — native overlay slot (MediaOverlay)
# ===================================================================

class TestStImageOverlay:
    """Tests for st_image(overlay=MediaOverlay(...)) — plan P-C §6."""

    URL = "https://example.com/img.png"

    # --- 1. Non-regression: overlay=None → HTML identical to 0.7.22 ---

    def test_no_overlay_html_identical_to_0722_default(self):
        """Without overlay, the emitted HTML is byte-identical to 0.7.22."""
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri=self.URL, alt="Ref")
        # Reference string frozen from the 0.7.22 emission — do NOT reformat.
        assert captured[0] == (
            f'<img src="{self.URL}" alt="Ref" style=" width: 100%; height: auto;">'
        )

    def test_no_overlay_html_identical_to_0722_styled_sized(self):
        """Styled + sized reference case, frozen from 0.7.22."""
        from streamtex.image import st_image
        from streamtex.styles import Style
        captured = []
        style = Style("border-radius:8px;", "overlay_ref_style")
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(style, uri=self.URL, width="80%", height=150)
        assert captured[0] == (
            f'<img src="{self.URL}" alt="" '
            f'style="border-radius:8px; width: 80%; height: 150px;">'
        )

    # --- 2. Structure with overlay ---

    def test_overlay_img_and_badge_in_same_media_box(self):
        from streamtex import MediaOverlay
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri=self.URL, overlay=MediaOverlay(text="✦ AI"))
        html = captured[0]
        assert html.startswith('<span class="stx-media-box"')
        assert html.endswith("</span>")
        assert html.count('class="stx-media-box"') == 1
        # img first, badge second, both inside the same wrapper
        assert html.index("<img") < html.index('class="stx-media-overlay"')
        assert "✦ AI" in html
        assert 'role="note"' in html

    def test_overlay_wrapper_carries_width_img_fills_it(self):
        """The wrapper carries the resolved width; the img fills the wrapper."""
        from streamtex import MediaOverlay
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri=self.URL, width="50%", overlay=MediaOverlay(text="✦ AI"))
        html = captured[0]
        assert "width:50%;" in html.split("<img")[0]      # wrapper side
        assert "width: 100%;" in html.split("<img")[1]    # img side

    def test_overlay_text_escaped(self):
        from streamtex import MediaOverlay
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(
                uri=self.URL,
                overlay=MediaOverlay(text="<script>x</script>", aria_label='a "b"'),
            )
        html = captured[0]
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert 'aria-label="a &quot;b&quot;"' in html

    def test_overlay_position_translated(self):
        from streamtex import MediaOverlay
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri=self.URL, overlay=MediaOverlay(text="x", position="top-left"))
        assert "left:8px; top:8px;" in captured[0]

    # --- 3. display_zoom (managed sidecar) ---

    def test_display_zoom_80_percent_on_wrapper(self):
        """Sidecar zoom 80% → wrapper carries width:80%, img stays at 100%."""
        from types import SimpleNamespace

        from streamtex import MediaOverlay
        from streamtex.image import st_image
        captured = []
        fake_st = SimpleNamespace(session_state={
            "stx_img_display_hero_initialized": True,
            "stx_img_display_hero_zoom": 80,
        })
        with patch("streamtex.image._st", fake_st), \
             patch("streamtex.ai.history.get_current", return_value=""), \
             patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri=self.URL, name="hero", overlay=MediaOverlay(text="✦ AI"))
        html = captured[0]
        wrapper_style = html.split("<img")[0]
        img_style = html.split("<img")[1].split(">")[0]
        assert "width:80%;" in wrapper_style
        assert "width: 100%;" in img_style
        assert "width: 80%" not in img_style

    # --- 4. link: anchor wraps the whole box, badge lets clicks through ---

    def test_link_wraps_media_box_and_badge_has_pointer_events_none(self):
        from streamtex import MediaOverlay
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(
                uri=self.URL, link="https://example.com",
                overlay=MediaOverlay(text="✦ AI"),
            )
        html = captured[0]
        assert html.startswith("<a ")
        assert html.index("<a ") < html.index('class="stx-media-box"')
        # hover survives the wrapper: the hover class sits on the anchor
        assert 'class="streamtex-link"' in html
        badge = html.split('class="stx-media-overlay"')[1]
        assert "pointer-events:none" in badge

    # --- 5. export: the badge travels inside the image element ---

    def test_export_buffer_contains_badge_inside_image_fragment(self):
        import streamtex.export as export_mod
        from streamtex import MediaOverlay
        from streamtex.export import ExportConfig, reset_export_buffer
        from streamtex.image import st_image
        reset_export_buffer(ExportConfig(enabled=True))
        try:
            with patch("streamtex.export.st", MagicMock()):
                st_image(uri=self.URL, overlay=MediaOverlay(text="✦ AI"))
            body = export_mod._buffer.get_body_html()
            # One export fragment holds BOTH the img and the badge
            fragment = next(f for f in body.split('<div class="stx-el"') if "<img" in f)
            assert 'class="stx-media-overlay"' in fragment
            assert "✦ AI" in fragment
        finally:
            reset_export_buffer(None)
