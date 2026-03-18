"""Tests for AssetCollector and external asset export."""

import base64
import os
import tempfile
import zipfile

from streamtex.export import AssetCollector, AssetMode, ExportConfig


class TestAssetCollector:
    """Unit tests for the AssetCollector class."""

    def test_register_data_uri_returns_relative_path(self):
        c = AssetCollector()
        data = b"fake png data"
        b64 = base64.b64encode(data).decode()
        uri = f"data:image/png;base64,{b64}"
        path = c.register_data_uri(uri)
        assert path.startswith("data/images/")
        assert path.endswith(".png")

    def test_register_data_uri_deduplication(self):
        c = AssetCollector()
        data = b"same content"
        b64 = base64.b64encode(data).decode()
        uri = f"data:image/png;base64,{b64}"
        path1 = c.register_data_uri(uri)
        path2 = c.register_data_uri(uri)
        assert path1 == path2
        assert len(c.assets) == 1

    def test_register_data_uri_different_content(self):
        c = AssetCollector()
        for i in range(3):
            data = f"content_{i}".encode()
            b64 = base64.b64encode(data).decode()
            uri = f"data:image/png;base64,{b64}"
            c.register_data_uri(uri)
        assert len(c.assets) == 3

    def test_register_bytes_audio(self):
        c = AssetCollector()
        path = c.register_bytes(b"audio data", "audio/mpeg")
        assert path.startswith("data/audio/")
        assert path.endswith(".mp3")

    def test_register_bytes_video(self):
        c = AssetCollector()
        path = c.register_bytes(b"video data", "video/mp4")
        assert path.startswith("data/video/")
        assert path.endswith(".mp4")

    def test_register_file(self):
        c = AssetCollector()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake image")
            f.flush()
            path = c.register_file(f.name, "image/png")
        os.unlink(f.name)
        assert path.startswith("data/images/")
        assert path.endswith(".png")
        assert len(c.assets) == 1

    def test_register_file_preserves_name(self):
        c = AssetCollector()
        with tempfile.NamedTemporaryFile(suffix=".jpg", prefix="photo_", delete=False) as f:
            f.write(b"jpeg data")
            f.flush()
            path = c.register_file(f.name, "image/jpeg")
        os.unlink(f.name)
        # Should contain original filename stem
        assert "photo_" in path

    def test_register_file_nonexistent(self):
        c = AssetCollector()
        path = c.register_file("/nonexistent/file.png", "image/png")
        assert path == "/nonexistent/file.png"  # returned unchanged
        assert len(c.assets) == 0

    def test_non_data_uri_returned_unchanged(self):
        c = AssetCollector()
        assert c.register_data_uri("https://example.com/img.png") == "https://example.com/img.png"
        assert c.register_data_uri("not-a-data-uri") == "not-a-data-uri"

    def test_unknown_mime_uses_other_dir(self):
        c = AssetCollector()
        path = c.register_bytes(b"mystery", "application/octet-stream")
        assert path.startswith("data/other/")

    def test_reset_clears_assets(self):
        c = AssetCollector()
        c.register_bytes(b"data", "image/png")
        assert len(c.assets) == 1
        c.reset()
        assert len(c.assets) == 0


class TestRewriteHtml:
    """Tests for AssetCollector.rewrite_html()."""

    def test_replaces_data_uri_in_img(self):
        c = AssetCollector()
        data = b"image bytes"
        b64 = base64.b64encode(data).decode()
        html = f'<img src="data:image/png;base64,{b64}" alt="test">'
        result = c.rewrite_html(html)
        assert "data:image/png;base64," not in result
        assert 'src="data/images/' in result
        assert len(c.assets) == 1

    def test_replaces_data_uri_in_audio(self):
        c = AssetCollector()
        data = b"audio bytes"
        b64 = base64.b64encode(data).decode()
        html = f'<source src="data:audio/wav;base64,{b64}" type="audio/wav">'
        result = c.rewrite_html(html)
        assert "data:audio/wav;base64," not in result
        assert 'src="data/audio/' in result

    def test_replaces_data_uri_in_video(self):
        c = AssetCollector()
        data = b"video bytes"
        b64 = base64.b64encode(data).decode()
        html = f'<source src="data:video/mp4;base64,{b64}" type="video/mp4">'
        result = c.rewrite_html(html)
        assert "data:video/mp4;base64," not in result
        assert 'src="data/video/' in result

    def test_preserves_url_sources(self):
        c = AssetCollector()
        html = '<img src="https://example.com/photo.jpg" alt="external">'
        result = c.rewrite_html(html)
        assert result == html  # unchanged
        assert len(c.assets) == 0

    def test_multiple_images_in_same_html(self):
        c = AssetCollector()
        imgs = []
        for i in range(3):
            data = f"img_{i}".encode()
            b64 = base64.b64encode(data).decode()
            imgs.append(f'<img src="data:image/png;base64,{b64}">')
        html = "\n".join(imgs)
        result = c.rewrite_html(html)
        assert result.count("data:image/png;base64,") == 0
        assert result.count("data/images/") == 3
        assert len(c.assets) == 3

    def test_deduplicates_same_image(self):
        c = AssetCollector()
        data = b"same image"
        b64 = base64.b64encode(data).decode()
        html = (
            f'<img src="data:image/png;base64,{b64}">'
            f'<img src="data:image/png;base64,{b64}">'
        )
        result = c.rewrite_html(html)
        assert len(c.assets) == 1  # deduplicated
        # Both should point to the same path
        paths = [m for m in result.split('src="') if m.startswith("data/")]
        assert len(paths) == 2


class TestToZip:
    """Tests for AssetCollector.to_zip()."""

    def test_creates_valid_zip(self):
        c = AssetCollector()
        data = b"image content"
        b64 = base64.b64encode(data).decode()
        html = f'<html><img src="data:image/png;base64,{b64}"></html>'
        zip_bytes = c.to_zip(html, "mybook")
        assert len(zip_bytes) > 0

        import io
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            names = zf.namelist()
            assert "mybook/mybook.html" in names
            # Should have at least one asset
            asset_names = [n for n in names if n.startswith("mybook/data/")]
            assert len(asset_names) == 1

            # HTML should NOT contain data URIs
            html_content = zf.read("mybook/mybook.html").decode()
            assert "data:image/png;base64," not in html_content
            assert "data/images/" in html_content

            # Asset should contain original bytes
            asset_content = zf.read(asset_names[0])
            assert asset_content == data

    def test_zip_with_multiple_asset_types(self):
        c = AssetCollector()
        img = base64.b64encode(b"image").decode()
        aud = base64.b64encode(b"audio").decode()
        vid = base64.b64encode(b"video").decode()
        html = (
            f'<img src="data:image/png;base64,{img}">'
            f'<source src="data:audio/wav;base64,{aud}">'
            f'<source src="data:video/mp4;base64,{vid}">'
        )
        zip_bytes = c.to_zip(html, "multi")

        import io
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            names = zf.namelist()
            assert any("data/images/" in n for n in names)
            assert any("data/audio/" in n for n in names)
            assert any("data/video/" in n for n in names)

    def test_zip_no_assets(self):
        c = AssetCollector()
        html = "<html><p>No media</p></html>"
        zip_bytes = c.to_zip(html, "plain")

        import io
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            names = zf.namelist()
            assert names == ["plain/plain.html"]
            content = zf.read("plain/plain.html").decode()
            assert content == html


class TestWriteToDisk:
    """Tests for AssetCollector.write_to_disk()."""

    def test_writes_html_and_assets(self):
        c = AssetCollector()
        data = b"disk image"
        b64 = base64.b64encode(data).decode()
        html = f'<html><img src="data:image/png;base64,{b64}"></html>'

        with tempfile.TemporaryDirectory() as tmpdir:
            path = c.write_to_disk(html, tmpdir, "doc")
            assert os.path.isfile(path)

            # Check HTML file
            with open(path) as f:
                content = f.read()
            assert "data:image/png;base64," not in content
            assert "data/images/" in content

            # Check asset file exists
            asset_dir = os.path.join(tmpdir, "doc", "data", "images")
            assert os.path.isdir(asset_dir)
            assets = os.listdir(asset_dir)
            assert len(assets) == 1
            with open(os.path.join(asset_dir, assets[0]), "rb") as f:
                assert f.read() == data


class TestExportConfigAssetMode:
    """Tests for AssetMode in ExportConfig."""

    def test_default_is_external(self):
        cfg = ExportConfig()
        assert cfg.asset_mode == AssetMode.EXTERNAL

    def test_can_set_embedded(self):
        cfg = ExportConfig(asset_mode=AssetMode.EMBEDDED)
        assert cfg.asset_mode == AssetMode.EMBEDDED

    def test_buffer_creates_collector_for_external(self):
        from streamtex.export import get_asset_collector, reset_export_buffer
        reset_export_buffer(ExportConfig(enabled=True, asset_mode=AssetMode.EXTERNAL))
        assert get_asset_collector() is not None
        reset_export_buffer(None)

    def test_buffer_no_collector_for_embedded(self):
        from streamtex.export import get_asset_collector, reset_export_buffer
        reset_export_buffer(ExportConfig(enabled=True, asset_mode=AssetMode.EMBEDDED))
        assert get_asset_collector() is None
        reset_export_buffer(None)
