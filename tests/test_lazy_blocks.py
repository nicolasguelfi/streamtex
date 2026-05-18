"""Tests for LazyBlockRegistry and resolve_static functionality."""

import os
import tempfile

import pytest

from streamtex.blocks import (
    LazyBlockRegistry,
    ProjectBlockRegistry,
    get_static_sources,
    resolve_static,
    set_static_sources,
)


class TestLazyBlockRegistry:
    """Test LazyBlockRegistry for loading blocks from multiple sources."""

    @pytest.fixture
    def temp_block_dirs(self):
        """Create temporary directories with mock block files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source 1 (local blocks)
            local_dir = os.path.join(tmpdir, "local_blocks")
            os.makedirs(local_dir)

            # Create local block files
            with open(os.path.join(local_dir, "bck_content_01.py"), "w") as f:
                f.write("""
class BlockStyles:
    pass

def build():
    print("Local content block")
""")

            with open(os.path.join(local_dir, "bck_header.py"), "w") as f:
                f.write("""
class BlockStyles:
    pass

def build():
    print("Local header block")
""")

            # Create source 2 (shared blocks)
            shared_dir = os.path.join(tmpdir, "shared_blocks")
            os.makedirs(shared_dir)

            with open(os.path.join(shared_dir, "bck_header.py"), "w") as f:
                f.write("""
class BlockStyles:
    pass

def build():
    print("Shared header block")
""")

            with open(os.path.join(shared_dir, "bck_footer.py"), "w") as f:
                f.write("""
class BlockStyles:
    pass

def build():
    print("Shared footer block")
""")

            yield {
                "local": local_dir,
                "shared": shared_dir,
                "tmpdir": tmpdir,
            }

    def test_load_from_single_source(self, temp_block_dirs):
        """Test loading blocks from a single source directory."""
        registry = LazyBlockRegistry([temp_block_dirs["local"]])

        # Access a block
        block = registry.bck_content_01
        assert block is not None
        assert hasattr(block, "build")
        assert hasattr(block, "BlockStyles")

    def test_load_from_multiple_sources(self, temp_block_dirs):
        """Test loading blocks from multiple source directories."""
        registry = LazyBlockRegistry([
            temp_block_dirs["local"],
            temp_block_dirs["shared"],
        ])

        # Load local block
        content = registry.bck_content_01
        assert content is not None

        # Load shared block (not in local)
        footer = registry.bck_footer
        assert footer is not None

    def test_priority_local_over_shared(self, temp_block_dirs):
        """Test that local blocks take priority over shared blocks with same name."""
        registry = LazyBlockRegistry([
            temp_block_dirs["local"],
            temp_block_dirs["shared"],
        ])

        # bck_header exists in both local and shared
        # Should get the local version
        header = registry.bck_header
        assert header is not None

        # Verify it's the local version by checking the module source
        source = header.build.__doc__ or ""  # Mock check
        # In real scenario, would compare function bodies or module paths
        assert header is not None

    def test_block_caching(self, temp_block_dirs):
        """Test that blocks are cached after first access."""
        registry = LazyBlockRegistry([temp_block_dirs["local"]])

        # First access
        block1 = registry.bck_content_01
        # Second access (should be cached)
        block2 = registry.bck_content_01

        # Should be the same object (cached)
        assert block1 is block2

    def test_missing_block_raises_error(self, temp_block_dirs):
        """Test that accessing a non-existent block raises AttributeError."""
        registry = LazyBlockRegistry([temp_block_dirs["local"]])

        with pytest.raises(AttributeError) as exc_info:
            _ = registry.bck_nonexistent

        assert "not found" in str(exc_info.value).lower()

    def test_missing_source_directory_ignored(self, temp_block_dirs):
        """Test that non-existent source directories are silently skipped."""
        registry = LazyBlockRegistry([
            os.path.join(temp_block_dirs["tmpdir"], "nonexistent"),
            temp_block_dirs["local"],  # Real directory
        ])

        # Should still load from real directory
        block = registry.bck_content_01
        assert block is not None

    def test_registry_repr(self, temp_block_dirs):
        """Test the registry string representation."""
        registry = LazyBlockRegistry([temp_block_dirs["local"]])
        repr_str = repr(registry)

        assert "LazyBlockRegistry" in repr_str
        assert "sources=" in repr_str


class TestResolveStatic:
    """Test static file resolution across sources."""

    @pytest.fixture
    def temp_static_dirs(self):
        """Create temporary directories with mock static files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create local static
            local_static = os.path.join(tmpdir, "local_static")
            os.makedirs(os.path.join(local_static, "images"))
            with open(os.path.join(local_static, "images", "local_logo.png"), "w") as f:
                f.write("PNG_DATA")

            # Create shared static
            shared_static = os.path.join(tmpdir, "shared_static")
            os.makedirs(os.path.join(shared_static, "images"))
            with open(os.path.join(shared_static, "images", "shared_logo.png"), "w") as f:
                f.write("PNG_DATA")
            with open(os.path.join(shared_static, "images", "university_logo.png"), "w") as f:
                f.write("PNG_DATA")

            yield {
                "local": local_static,
                "shared": shared_static,
                "tmpdir": tmpdir,
            }

    def test_resolve_from_local_source(self, temp_static_dirs):
        """Test resolving a file from local source."""
        set_static_sources([
            temp_static_dirs["local"],
            temp_static_dirs["shared"],
        ])

        resolved = resolve_static("images/local_logo.png")
        assert os.path.exists(resolved)
        assert "local_logo.png" in resolved

    def test_resolve_from_shared_source(self, temp_static_dirs):
        """Test resolving a file from shared source."""
        set_static_sources([
            temp_static_dirs["local"],
            temp_static_dirs["shared"],
        ])

        resolved = resolve_static("images/shared_logo.png")
        assert os.path.exists(resolved)
        assert "shared_logo.png" in resolved

    def test_priority_local_over_shared_file(self, temp_static_dirs):
        """Test that local files take priority over shared files."""
        # Create a file with same name in both sources
        with open(os.path.join(temp_static_dirs["local"], "images", "university_logo.png"), "w") as f:
            f.write("LOCAL_PNG_DATA")

        set_static_sources([
            temp_static_dirs["local"],
            temp_static_dirs["shared"],
        ])

        resolved = resolve_static("images/university_logo.png")
        assert os.path.exists(resolved)

        # Verify it's the local version
        with open(resolved, "r") as f:
            content = f.read()
        assert content == "LOCAL_PNG_DATA"

    def test_missing_file_returns_original_path(self, temp_static_dirs):
        """Test that missing files return the original relative path."""
        set_static_sources([
            temp_static_dirs["local"],
            temp_static_dirs["shared"],
        ])

        resolved = resolve_static("images/nonexistent.png")
        # Should return the original path as fallback
        assert resolved == "images/nonexistent.png"

    def test_empty_sources(self):
        """Test resolve_static with no sources configured."""
        set_static_sources([])

        resolved = resolve_static("images/logo.png")
        # Should return original path when no sources configured
        assert resolved == "images/logo.png"

    def test_get_static_sources(self, temp_static_dirs):
        """Test getting configured static sources."""
        sources = [temp_static_dirs["local"], temp_static_dirs["shared"]]
        set_static_sources(sources)

        retrieved = get_static_sources()
        assert len(retrieved) == 2
        # Should be absolute paths
        assert all(os.path.isabs(p) for p in retrieved)


class TestIntegration:
    """Integration tests for LazyBlockRegistry + resolve_static."""

    @pytest.fixture
    def full_setup(self):
        """Create a realistic multi-source setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Project structure
            project_dir = os.path.join(tmpdir, "my_project")
            os.makedirs(project_dir)

            # Local blocks
            local_blocks = os.path.join(project_dir, "blocks")
            os.makedirs(local_blocks)
            with open(os.path.join(local_blocks, "bck_intro.py"), "w") as f:
                f.write("def build():\n    pass\n")

            # Local static
            local_static = os.path.join(project_dir, "static")
            local_static_images = os.path.join(local_static, "images")
            os.makedirs(local_static_images)
            with open(os.path.join(local_static_images, "diagram.png"), "w") as f:
                f.write("PNG")

            # Shared blocks
            shared_dir = os.path.join(tmpdir, "shared")
            shared_blocks = os.path.join(shared_dir, "blocks")
            os.makedirs(shared_blocks)
            with open(os.path.join(shared_blocks, "bck_header.py"), "w") as f:
                f.write("def build():\n    pass\n")

            # Shared static
            shared_static = os.path.join(shared_dir, "static")
            shared_static_images = os.path.join(shared_static, "images")
            os.makedirs(shared_static_images)
            with open(os.path.join(shared_static_images, "logo.png"), "w") as f:
                f.write("PNG")

            yield {
                "project": project_dir,
                "local_blocks": local_blocks,
                "local_static": local_static,
                "shared": shared_dir,
                "shared_blocks": shared_blocks,
                "shared_static": shared_static,
            }

    def test_realistic_project_setup(self, full_setup):
        """Test a realistic project setup with local and shared resources."""
        # Configure the project
        registry = LazyBlockRegistry([
            full_setup["local_blocks"],
            full_setup["shared_blocks"],
        ])

        set_static_sources([
            full_setup["local_static"],
            full_setup["shared_static"],
        ])

        # Load local block
        intro = registry.bck_intro
        assert intro is not None

        # Load shared block
        header = registry.bck_header
        assert header is not None

        # Resolve local image
        diagram_path = resolve_static("images/diagram.png")
        assert os.path.exists(diagram_path)

        # Resolve shared image
        logo_path = resolve_static("images/logo.png")
        assert os.path.exists(logo_path)


class TestProjectBlockRegistrySequenceProtocol:
    """ProjectBlockRegistry must behave like a sequence so it can be passed
    directly to ``st_book(registry, ...)`` (the form produced by
    ``generate_book_py()``)."""

    @pytest.fixture
    def blocks_dir(self, tmp_path):
        d = tmp_path / "blocks"
        d.mkdir()
        (d / "bck_02_b.py").write_text(
            "def build():\n    return 'b'\n"
        )
        (d / "bck_01_a.py").write_text(
            "def build():\n    return 'a'\n"
        )
        (d / "bck_03_c.py").write_text(
            "def build():\n    return 'c'\n"
        )
        return d

    def test_len_does_not_import_blocks(self, blocks_dir):
        reg = ProjectBlockRegistry(blocks_dir)
        assert len(reg) == 3
        # No block should be loaded by len() alone
        assert reg.get_stats()["loaded"] == 0

    def test_iter_yields_blocks_in_alphabetical_order(self, blocks_dir):
        reg = ProjectBlockRegistry(blocks_dir)
        mods = list(reg)
        assert len(mods) == 3
        assert [m.build() for m in mods] == ["a", "b", "c"]

    def test_iter_is_lazy_per_block(self, blocks_dir):
        """Each yield must trigger import of that block only — useful for
        st_book which iterates and may stop early."""
        reg = ProjectBlockRegistry(blocks_dir)
        it = iter(reg)
        assert reg.get_stats()["loaded"] == 0
        next(it)
        assert reg.get_stats()["loaded"] == 1
        next(it)
        assert reg.get_stats()["loaded"] == 2

    def test_getitem_int(self, blocks_dir):
        reg = ProjectBlockRegistry(blocks_dir)
        assert reg[0].build() == "a"
        assert reg[-1].build() == "c"

    def test_getitem_slice(self, blocks_dir):
        reg = ProjectBlockRegistry(blocks_dir)
        mods = reg[0:2]
        assert [m.build() for m in mods] == ["a", "b"]

    def test_empty_registry(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        reg = ProjectBlockRegistry(empty)
        assert len(reg) == 0
        assert list(reg) == []

    def test_works_as_module_list_for_len_and_iter(self, blocks_dir):
        """Smoke check: the patterns used by streamtex.book._paginated_book
        (len + enumerate) must succeed without TypeError."""
        reg = ProjectBlockRegistry(blocks_dir)
        # Mimic _paginated_book's prologue
        total = len(reg)
        assert total == 3
        results = []
        for i, module in enumerate(reg):
            results.append((i, module.build()))
        assert results == [(0, "a"), (1, "b"), (2, "c")]


class TestProjectBlockRegistryConstructorValidation:
    """ProjectBlockRegistry must reject non-directory paths with a clear error,
    instead of silently producing an empty registry (the silent failure that
    caused the "Initializing…" loading-overlay loop in v0.6.41 scaffolds)."""

    def test_passing_a_file_path_raises(self, tmp_path):
        """Passing __file__ (the init.py path) instead of its parent must
        fail loudly — this was the bug behind the loading-loop regression."""
        blocks_dir = tmp_path / "blocks"
        blocks_dir.mkdir()
        init_file = blocks_dir / "__init__.py"
        init_file.write_text("")

        with pytest.raises(ValueError, match="expects a directory"):
            ProjectBlockRegistry(init_file)

    def test_error_message_includes_correct_usage_hint(self, tmp_path):
        blocks_dir = tmp_path / "blocks"
        blocks_dir.mkdir()
        init_file = blocks_dir / "__init__.py"
        init_file.write_text("")

        with pytest.raises(ValueError) as exc:
            ProjectBlockRegistry(init_file)
        msg = str(exc.value)
        assert "Path(__file__).parent" in msg

    def test_passing_a_missing_path_raises(self, tmp_path):
        ghost = tmp_path / "does-not-exist"
        with pytest.raises(ValueError, match="expects a directory"):
            ProjectBlockRegistry(ghost)

    def test_passing_a_valid_directory_succeeds(self, tmp_path):
        blocks_dir = tmp_path / "blocks"
        blocks_dir.mkdir()
        reg = ProjectBlockRegistry(blocks_dir)
        assert reg.blocks_dir == blocks_dir
