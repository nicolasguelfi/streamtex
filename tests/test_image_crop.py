"""Tests for streamtex.image_crop — CropConfig, natural-size resolution,
crop container emission, and st_image(crop=...) integration."""

import os
from unittest.mock import patch

import pytest

from streamtex.image_crop import (
    CropConfig,
    _parse_svg_size,
    build_crop_html,
    get_natural_size,
    normalize_crop,
)


def _make_png(path, w, h, color=(255, 0, 0)):
    from PIL import Image
    Image.new("RGB", (w, h), color).save(path)


def _capture_render(captured):
    def _side_effect(html, **kw):
        captured.append(html)
    return _side_effect


class TestCropConfigValidation:
    def test_valid_values_accepted(self):
        cfg = CropConfig(4, 0, 10, 6)
        assert (cfg.top, cfg.right, cfg.bottom, cfg.left) == (4, 0, 10, 6)

    def test_floats_accepted(self):
        cfg = CropConfig(top=2.5, bottom=7.25)
        assert cfg.top == 2.5

    def test_zero_crop_accepted(self):
        CropConfig(0, 0, 0, 0)

    def test_negative_value_rejected(self):
        with pytest.raises(ValueError, match=r"top.*\[0, 100\)"):
            CropConfig(top=-1)

    def test_value_at_100_rejected(self):
        with pytest.raises(ValueError, match=r"right.*\[0, 100\)"):
            CropConfig(right=100)

    def test_non_number_rejected(self):
        with pytest.raises(ValueError, match="left"):
            CropConfig(left="10")

    def test_vertical_sum_rejected(self):
        with pytest.raises(ValueError, match="top . bottom"):
            CropConfig(top=60, bottom=40)

    def test_horizontal_sum_rejected(self):
        with pytest.raises(ValueError, match="left . right"):
            CropConfig(left=55, right=50)

    def test_natural_size_valid(self):
        cfg = CropConfig(1, 1, 1, 1, natural_size=(2560, 1800))
        assert cfg.natural_size == (2560.0, 1800.0)

    def test_natural_size_zero_rejected(self):
        with pytest.raises(ValueError, match="natural_size"):
            CropConfig(1, 1, 1, 1, natural_size=(0, 1800))

    def test_natural_size_wrong_arity_rejected(self):
        with pytest.raises(ValueError, match="natural_size"):
            CropConfig(1, 1, 1, 1, natural_size=(100, 200, 300))


class TestNormalizeCrop:
    def test_tuple_normalized_in_css_inset_order(self):
        cfg = normalize_crop((4, 0, 10, 6))
        assert (cfg.top, cfg.right, cfg.bottom, cfg.left) == (4, 0, 10, 6)

    def test_list_accepted(self):
        cfg = normalize_crop([1, 2, 3, 4])
        assert cfg.bottom == 3

    def test_config_passthrough(self):
        cfg = CropConfig(1, 2, 3, 4)
        assert normalize_crop(cfg) is cfg

    def test_natural_size_merged_into_tuple_form(self):
        cfg = normalize_crop((1, 2, 3, 4), natural_size=(800, 600))
        assert cfg.natural_size == (800.0, 600.0)

    def test_natural_size_merged_into_config_form(self):
        cfg = normalize_crop(CropConfig(1, 2, 3, 4), natural_size=(800, 600))
        assert cfg.natural_size == (800.0, 600.0)

    def test_natural_size_given_twice_rejected(self):
        with pytest.raises(ValueError, match="twice"):
            normalize_crop(
                CropConfig(1, 2, 3, 4, natural_size=(800, 600)),
                natural_size=(800, 600),
            )

    def test_wrong_arity_rejected(self):
        with pytest.raises(ValueError, match=r"top, right, bottom, left"):
            normalize_crop((4, 10))

    def test_scalar_rejected(self):
        with pytest.raises(ValueError, match="crop must be"):
            normalize_crop(10)


class TestParseSvgSize:
    def test_width_height_attributes(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480"></svg>'
        assert _parse_svg_size(svg) == (640.0, 480.0)

    def test_px_units_accepted(self):
        svg = '<svg width="640px" height="480px"></svg>'
        assert _parse_svg_size(svg) == (640.0, 480.0)

    def test_viewbox_fallback(self):
        svg = '<svg viewBox="0 0 1024 768"></svg>'
        assert _parse_svg_size(svg) == (1024.0, 768.0)

    def test_relative_width_falls_back_to_viewbox(self):
        svg = '<svg width="100%" height="100%" viewBox="0 0 300 150"></svg>'
        assert _parse_svg_size(svg) == (300.0, 150.0)

    def test_no_dimensions_returns_none(self):
        assert _parse_svg_size("<svg></svg>") is None

    def test_not_an_svg_returns_none(self):
        assert _parse_svg_size("<html></html>") is None


class TestGetNaturalSize:
    def test_natural_size_short_circuits_all_reads(self):
        cfg = CropConfig(1, 1, 1, 1, natural_size=(2560, 1800))
        with patch("streamtex.image_crop._find_local_file") as find, \
             patch("streamtex.image_crop._read_local_image_size") as read:
            assert get_natural_size("whatever.png", cfg) == (2560.0, 1800.0)
        find.assert_not_called()
        read.assert_not_called()

    def test_remote_uri_without_natural_size_rejected(self):
        with pytest.raises(ValueError, match="remote URI.*natural_size"):
            get_natural_size("https://cdn.example/x.png", CropConfig(1, 1, 1, 1))

    def test_remote_uri_with_natural_size_needs_no_network(self):
        cfg = CropConfig(1, 1, 1, 1, natural_size=(400, 250))
        assert get_natural_size("https://cdn.example/x.png", cfg) == (400.0, 250.0)

    def test_local_png_read_via_pillow(self, tmp_path):
        png = tmp_path / "img.png"
        _make_png(str(png), 123, 45)
        assert get_natural_size(str(png), CropConfig(1, 1, 1, 1)) == (123.0, 45.0)

    def test_local_svg_read_via_viewbox(self, tmp_path):
        svg = tmp_path / "img.svg"
        svg.write_text('<svg viewBox="0 0 320 200"></svg>')
        assert get_natural_size(str(svg), CropConfig(1, 1, 1, 1)) == (320.0, 200.0)

    def test_cache_invalidated_on_mtime_change(self, tmp_path):
        png = tmp_path / "img.png"
        _make_png(str(png), 10, 10)
        cfg = CropConfig(1, 1, 1, 1)
        assert get_natural_size(str(png), cfg) == (10.0, 10.0)
        _make_png(str(png), 20, 30)
        os.utime(str(png), (os.path.getmtime(str(png)) + 5,) * 2)
        assert get_natural_size(str(png), cfg) == (20.0, 30.0)

    def test_missing_file_rejected_with_hint(self):
        with pytest.raises(ValueError, match="natural_size"):
            get_natural_size("/nonexistent/img.png", CropConfig(1, 1, 1, 1))

    def test_unreadable_format_rejected_with_hint(self, tmp_path):
        bad = tmp_path / "img.png"
        bad.write_bytes(b"not an image at all")
        with pytest.raises(ValueError, match="natural_size"):
            get_natural_size(str(bad), CropConfig(1, 1, 1, 1))

    def test_svg_without_dimensions_rejected_with_hint(self, tmp_path):
        svg = tmp_path / "img.svg"
        svg.write_text("<svg></svg>")
        with pytest.raises(ValueError, match="viewBox"):
            get_natural_size(str(svg), CropConfig(1, 1, 1, 1))


class TestServedImageResolution:
    """Images served via configure_image_path (the "served, never inlined"
    pattern): the URI is deliberately NOT found by the static sources, but
    crop must locate the bytes on disk to read their dimensions."""

    @pytest.fixture(autouse=True)
    def _reset_image_path_config(self):
        import streamtex.image as img_mod
        yield
        img_mod.configure_image_path("app/static/images")

    def _make_served_tree(self, tmp_path, w=200, h=100):
        """Repro tree: <app>/book.py + <app>/static/media/captures/x.png."""
        captures = tmp_path / "static" / "media" / "captures"
        captures.mkdir(parents=True)
        _make_png(str(captures / "shot.png"), w, h)
        (tmp_path / "book.py").write_text("# main script")
        return "captures/shot.png"

    def _fake_ctx(self, tmp_path):
        from types import SimpleNamespace
        return SimpleNamespace(main_script_path=str(tmp_path / "book.py"))

    def test_served_uri_resolved_via_streamlit_ctx(self, tmp_path):
        from streamtex.image import configure_image_path
        configure_image_path("app/static/media")
        uri = self._make_served_tree(tmp_path)
        with patch("streamtex.image_crop.get_script_run_ctx",
                   return_value=self._fake_ctx(tmp_path)):
            assert get_natural_size(uri, CropConfig(1, 1, 1, 1)) == (200.0, 100.0)

    def test_served_uri_resolved_with_foreign_cwd(self, tmp_path, monkeypatch):
        """The real trap: launcher started from the repo root, not the
        module dir — the ctx anchor must win over the cwd."""
        from streamtex.image import configure_image_path
        configure_image_path("app/static/media")
        uri = self._make_served_tree(tmp_path)
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        monkeypatch.chdir(elsewhere)
        with patch("streamtex.image_crop.get_script_run_ctx",
                   return_value=self._fake_ctx(tmp_path)):
            assert get_natural_size(uri, CropConfig(1, 1, 1, 1)) == (200.0, 100.0)

    def test_served_uri_resolved_headless_via_cwd(self, tmp_path, monkeypatch):
        """No ScriptRunContext (headless CLI export, which chdirs to the
        project dir before exec'ing book.py): the cwd anchor applies."""
        from streamtex.image import configure_image_path
        configure_image_path("app/static/media")
        uri = self._make_served_tree(tmp_path)
        monkeypatch.chdir(tmp_path)
        with patch("streamtex.image_crop.get_script_run_ctx", return_value=None):
            assert get_natural_size(uri, CropConfig(1, 1, 1, 1)) == (200.0, 100.0)

    def test_missing_served_file_keeps_current_error(self, tmp_path, monkeypatch):
        from streamtex.image import configure_image_path
        configure_image_path("app/static/media")
        self._make_served_tree(tmp_path)
        monkeypatch.chdir(tmp_path)
        with patch("streamtex.image_crop.get_script_run_ctx", return_value=None), \
             pytest.raises(ValueError, match="cannot locate local image"):
            get_natural_size("captures/absent.png", CropConfig(1, 1, 1, 1))

    def test_natural_size_still_short_circuits_served_lookup(self, tmp_path):
        from streamtex.image import configure_image_path
        configure_image_path("app/static/media")
        cfg = CropConfig(1, 1, 1, 1, natural_size=(1134, 8796))
        with patch("streamtex.image_crop._find_local_file") as find_local, \
             patch("streamtex.image_crop._find_served_file") as find_served, \
             patch("streamtex.image_crop._read_local_image_size") as read:
            assert get_natural_size("captures/shot.png", cfg) == (1134.0, 8796.0)
        find_local.assert_not_called()
        find_served.assert_not_called()
        read.assert_not_called()

    def test_explicit_fs_root_wins_and_covers_custom_prefixes(self, tmp_path):
        """fs_root works even for a prefix outside app/static (CDN,
        reverse proxy) where the automatic derivation cannot help."""
        from streamtex.image import configure_image_path
        media = tmp_path / "mirror"
        media.mkdir()
        _make_png(str(media / "x.png"), 64, 32)
        configure_image_path("cdn/media", fs_root=media)
        with patch("streamtex.image_crop.get_script_run_ctx", return_value=None):
            assert get_natural_size("x.png", CropConfig(1, 1, 1, 1)) == (64.0, 32.0)

    def test_fs_root_has_priority_over_derivation(self, tmp_path):
        from streamtex.image import configure_image_path
        uri = self._make_served_tree(tmp_path, 200, 100)
        mirror = tmp_path / "mirror" / "captures"
        mirror.mkdir(parents=True)
        _make_png(str(mirror / "shot.png"), 400, 50)
        configure_image_path("app/static/media", fs_root=tmp_path / "mirror")
        with patch("streamtex.image_crop.get_script_run_ctx",
                   return_value=self._fake_ctx(tmp_path)):
            assert get_natural_size(uri, CropConfig(1, 1, 1, 1)) == (400.0, 50.0)

    def test_non_app_static_prefix_without_fs_root_keeps_error(self, tmp_path):
        from streamtex.image import configure_image_path
        configure_image_path("cdn/media")
        with patch("streamtex.image_crop.get_script_run_ctx", return_value=None), \
             pytest.raises(ValueError, match="cannot locate local image"):
            get_natural_size("x.png", CropConfig(1, 1, 1, 1))

    def test_ctx_without_main_script_path_degrades_cleanly(self, tmp_path, monkeypatch):
        """Streamlit version drift (ctx lacking main_script_path) must
        degrade to the other anchors, never crash."""
        from types import SimpleNamespace

        from streamtex.image import configure_image_path
        configure_image_path("app/static/media")
        uri = self._make_served_tree(tmp_path)
        monkeypatch.chdir(tmp_path)
        with patch("streamtex.image_crop.get_script_run_ctx",
                   return_value=SimpleNamespace()):
            assert get_natural_size(uri, CropConfig(1, 1, 1, 1)) == (200.0, 100.0)

    def test_st_image_served_crop_end_to_end(self, tmp_path):
        """Full repro of the downstream ticket: served URI + crop → the
        emitted src stays a served URL (never inlined base64) AND the
        aspect-ratio comes from the measured dimensions."""
        from streamtex.image import configure_image_path, st_image
        configure_image_path("app/static/media")
        uri = self._make_served_tree(tmp_path, 1134, 8796)
        captured = []
        with patch("streamtex.image_crop.get_script_run_ctx",
                   return_value=self._fake_ctx(tmp_path)), \
             patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri=uri, width="min(22vw, 29vh)", crop=(0, 0, 72, 0))
        html = captured[0]
        assert 'src="app/static/media/captures/shot.png"' in html
        assert "base64" not in html
        assert 'aspect-ratio:1134 / 2462.88;' in html


class TestBuildCropHtml:
    """Reference geometry: 1000x600 source, crop=(5, 20, 15, 10) —
    visible zone 700x480, img enlarged to 1000/700, shifted by (10%, 5%)."""

    def test_reference_geometry(self):
        html = build_crop_html(
            "src.png", "alt text", CropConfig(5, 20, 15, 10), 1000, 600,
            width="44vw",
        )
        assert 'aspect-ratio:700 / 480;' in html
        assert "overflow:hidden; width:44vw;" in html
        assert "width:142.8571%;" in html
        assert "transform:translate(-10%, -5%);" in html
        assert "display:block;" in html
        assert "height:auto;" in html
        assert 'class="stx-crop-box"' in html
        assert '<img src="src.png" alt="alt text"' in html

    def test_caller_css_precedes_crop_declarations(self):
        html = build_crop_html(
            "s.png", "", CropConfig(5, 20, 15, 10), 1000, 600,
            width="300px", caller_css="border-radius:8px;",
        )
        style = html.split('style="', 1)[1].split('"', 1)[0]
        assert style.index("border-radius") < style.index("overflow:hidden")

    def test_inside_overlay_fills_wrapper(self):
        html = build_crop_html(
            "s.png", "", CropConfig(5, 20, 15, 10), 1000, 600,
            width="300px", inside_overlay=True,
        )
        assert "width:100%;" in html
        assert "width:300px" not in html

    def test_fractional_percentages(self):
        html = build_crop_html(
            "s.png", "", CropConfig(2.5, 0, 0, 12.5), 800, 400, width="100%",
        )
        assert "transform:translate(-12.5%, -2.5%);" in html
        assert "width:114.2857%;" in html


class TestStImageCropIntegration:
    def test_crop_none_is_byte_identical_to_legacy(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", width="300px", alt="x")
        assert captured[0] == (
            '<img src="https://example.com/img.png" alt="x" '
            'style=" width: 300px; height: auto;">'
        )

    def test_crop_on_remote_uri_with_natural_size(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", width="44vw",
                     crop=(5, 20, 15, 10), natural_size=(1000, 600))
        html = captured[0]
        assert 'aspect-ratio:700 / 480;' in html
        assert "width:44vw;" in html
        assert "transform:translate(-10%, -5%);" in html

    def test_crop_on_local_file(self, tmp_path):
        from streamtex.image import st_image
        png = tmp_path / "shot.png"
        _make_png(str(png), 500, 300)
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri=str(png), width="400px", crop=(10, 0, 10, 0))
        assert 'aspect-ratio:500 / 240;' in captured[0]

    def test_crop_on_remote_uri_without_natural_size_rejected(self):
        from streamtex.image import st_image
        with pytest.raises(ValueError, match="natural_size"):
            st_image(uri="https://example.com/img.png", crop=(1, 1, 1, 1))

    def test_natural_size_without_crop_rejected(self):
        from streamtex.image import st_image
        with pytest.raises(ValueError, match="natural_size= requires crop="):
            st_image(uri="https://example.com/img.png", natural_size=(100, 100))

    def test_explicit_height_with_crop_rejected(self):
        from streamtex.image import st_image
        with pytest.raises(ValueError, match="height"):
            st_image(uri="https://example.com/img.png", height="200px",
                     crop=(1, 1, 1, 1), natural_size=(100, 100))

    def test_invalid_crop_values_rejected(self):
        from streamtex.image import st_image
        with pytest.raises(ValueError, match=r"\[0, 100\)"):
            st_image(uri="https://example.com/img.png", crop=(-1, 0, 0, 0))

    def test_caller_style_on_container_not_on_img(self):
        from streamtex.image import st_image
        from streamtex.styles import Style
        captured = []
        style = Style("border-radius:8px;", "crop_test_style")
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(style, uri="https://example.com/img.png", width="300px",
                     crop=(5, 20, 15, 10), natural_size=(1000, 600))
        html = captured[0]
        img_style = html.split("<img", 1)[1].split('style="', 1)[1].split('"', 1)[0]
        assert "border-radius" not in img_style
        container_style = html.split('style="', 1)[1].split('"', 1)[0]
        assert "border-radius:8px;" in container_style

    def test_crop_with_overlay_wraps_the_container(self):
        from streamtex.image import st_image
        from streamtex.media_overlay import MediaOverlay
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", width="300px",
                     crop=(5, 20, 15, 10), natural_size=(1000, 600),
                     overlay=MediaOverlay(text="AI"))
        html = captured[0]
        # Wrapper carries the width, crop container fills it, badge inside.
        assert html.index("stx-media-box") < html.index("stx-crop-box")
        assert "width:300px" in html.split("stx-crop-box")[0]
        wrapper_inner = html.split("stx-crop-box", 1)[1]
        assert "width:100%;" in wrapper_inner
        assert "stx-media-overlay" in html
        # The badge is a sibling of the crop container, not inside it.
        assert html.index("</div>") < html.index("stx-media-overlay")

    def test_managed_display_width_lands_on_crop_container(self):
        """Editor-panel display_width overrides width= and must apply to
        the crop container (the visible zone), not the inner img."""
        from types import SimpleNamespace

        from streamtex.image import st_image
        captured = []
        fake_st = SimpleNamespace(session_state={
            "stx_img_display_hero_initialized": True,
            "stx_img_display_hero_width": "250px",
        })
        with patch("streamtex.image._st", fake_st), \
             patch("streamtex.ai.history.get_current", return_value=""), \
             patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", name="hero",
                     width="600px", crop=(5, 20, 15, 10),
                     natural_size=(1000, 600))
        html = captured[0]
        container_style = html.split('style="', 1)[1].split('"', 1)[0]
        img_style = html.split("<img", 1)[1].split('style="', 1)[1].split('"', 1)[0]
        assert "width:250px;" in container_style
        assert "600px" not in html
        assert "width:142.8571%;" in img_style

    def test_managed_display_height_conflicts_with_crop(self):
        """A display_height persisted by the editor panel is an explicit
        height — refused with crop, like the height= parameter."""
        from types import SimpleNamespace

        from streamtex.image import st_image
        fake_st = SimpleNamespace(session_state={
            "stx_img_display_hero_initialized": True,
            "stx_img_display_hero_height": "200px",
        })
        with patch("streamtex.image._st", fake_st), \
             patch("streamtex.ai.history.get_current", return_value=""), \
             pytest.raises(ValueError, match="height"):
            st_image(uri="https://example.com/img.png", name="hero",
                     crop=(5, 20, 15, 10), natural_size=(1000, 600))

    def test_crop_with_link_wraps_everything(self):
        from streamtex.image import st_image
        captured = []
        with patch("streamtex.image._render", side_effect=_capture_render(captured)):
            st_image(uri="https://example.com/img.png", width="300px",
                     crop=(5, 20, 15, 10), natural_size=(1000, 600),
                     link="https://example.org")
        html = captured[0]
        assert html.index("<a ") < html.index("stx-crop-box")
        assert 'href="https://example.org"' in html
