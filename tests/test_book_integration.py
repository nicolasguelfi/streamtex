"""Integration tests for streamtex/book.py helper functions.

Only pure-logic helpers that do not require a live Streamlit session are
tested here: _compute_cache_hash, _get_page_titles, and st_include.
The full st_book / _paginated_book functions require an active Streamlit
runtime and are excluded from unit testing.
"""

import hashlib
import types
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# _compute_cache_hash
# ---------------------------------------------------------------------------

class TestComputeCacheHash:
    """Tests for book._compute_cache_hash."""

    def _hash(self, *names):
        """Compute the expected MD5 for the given module names."""
        joined = "|".join(names)
        return hashlib.md5(joined.encode()).hexdigest()

    def _make_module(self, name):
        m = types.ModuleType(name)
        m.__name__ = name
        return m

    def test_single_module_stable(self):
        from streamtex.book import _compute_cache_hash
        m = self._make_module("block_a")
        result = _compute_cache_hash([m])
        assert result == self._hash("block_a")

    def test_same_input_same_hash(self):
        from streamtex.book import _compute_cache_hash
        m1 = self._make_module("block_a")
        m2 = self._make_module("block_b")
        h1 = _compute_cache_hash([m1, m2])
        h2 = _compute_cache_hash([m1, m2])
        assert h1 == h2

    def test_different_order_gives_different_hash(self):
        """Different module order → different hash (order-sensitive join)."""
        from streamtex.book import _compute_cache_hash
        m1 = self._make_module("block_a")
        m2 = self._make_module("block_b")
        h_ab = _compute_cache_hash([m1, m2])
        h_ba = _compute_cache_hash([m2, m1])
        assert h_ab != h_ba

    def test_empty_list(self):
        from streamtex.book import _compute_cache_hash
        result = _compute_cache_hash([])
        assert result == hashlib.md5(b"").hexdigest()

    def test_different_modules_give_different_hash(self):
        from streamtex.book import _compute_cache_hash
        m1 = self._make_module("block_a")
        m2 = self._make_module("block_b")
        assert _compute_cache_hash([m1]) != _compute_cache_hash([m2])

    def test_returns_hex_string(self):
        from streamtex.book import _compute_cache_hash
        m = self._make_module("block_a")
        result = _compute_cache_hash([m])
        assert isinstance(result, str)
        # MD5 hex digest is always 32 characters
        assert len(result) == 32

    def test_object_without_name_uses_str(self):
        """Objects lacking __name__ fall back to str() representation."""
        from streamtex.book import _compute_cache_hash

        class NoName:
            def __str__(self):
                return "no-name-object"

        obj = NoName()
        result = _compute_cache_hash([obj])
        assert result == hashlib.md5(b"no-name-object").hexdigest()


# ---------------------------------------------------------------------------
# _get_page_titles
# ---------------------------------------------------------------------------

class TestGetPageTitles:
    """Tests for book._get_page_titles."""

    def test_fallback_section_n_for_empty_cache(self):
        from streamtex.book import _get_page_titles
        titles = _get_page_titles({}, total=3)
        assert titles == ["Section 1", "Section 2", "Section 3"]

    def test_fallback_section_n_for_no_toc_key(self):
        from streamtex.book import _get_page_titles
        titles = _get_page_titles({"toc": []}, total=2)
        assert titles == ["Section 1", "Section 2"]

    def test_toc_entry_replaces_fallback(self):
        from streamtex.book import _get_page_titles
        cache = {
            "toc": [
                {"page_idx": 0, "title": "Introduction"},
                {"page_idx": 1, "title": "Advanced Topics"},
            ]
        }
        titles = _get_page_titles(cache, total=3)
        assert titles[0] == "Introduction"
        assert titles[1] == "Advanced Topics"
        assert titles[2] == "Section 3"  # no TOC entry → fallback

    def test_toc_entry_out_of_range_is_ignored(self):
        from streamtex.book import _get_page_titles
        cache = {
            "toc": [
                {"page_idx": 99, "title": "Out of Range"},
            ]
        }
        titles = _get_page_titles(cache, total=2)
        assert titles == ["Section 1", "Section 2"]

    def test_second_toc_entry_for_same_page_does_not_overwrite(self):
        """Only the first TOC entry for a page sets the title (startswith guard)."""
        from streamtex.book import _get_page_titles
        cache = {
            "toc": [
                {"page_idx": 0, "title": "First Title"},
                {"page_idx": 0, "title": "Second Title"},  # should be ignored
            ]
        }
        titles = _get_page_titles(cache, total=2)
        assert titles[0] == "First Title"

    def test_single_page_total(self):
        from streamtex.book import _get_page_titles
        titles = _get_page_titles({}, total=1)
        assert titles == ["Section 1"]

    def test_zero_pages_returns_empty(self):
        from streamtex.book import _get_page_titles
        titles = _get_page_titles({}, total=0)
        assert titles == []

    def test_toc_with_missing_page_idx_defaults_to_zero(self):
        """Entries without page_idx key should default to 0."""
        from streamtex.book import _get_page_titles
        cache = {
            "toc": [
                {"title": "No Index Entry"},  # no page_idx key
            ]
        }
        titles = _get_page_titles(cache, total=2)
        assert titles[0] == "No Index Entry"
        assert titles[1] == "Section 2"


# ---------------------------------------------------------------------------
# st_include
# ---------------------------------------------------------------------------

class TestStInclude:
    """Tests for book.st_include."""

    def test_calls_build_on_module(self):
        from streamtex.book import st_include
        build_called = []

        mod = types.ModuleType("fake_block")
        mod.__name__ = "fake_block"
        mod.build = lambda *a, **kw: build_called.append((a, kw))

        with patch("streamtex.book.st") as mock_st:
            st_include(mod)

        assert len(build_called) == 1

    def test_passes_args_and_kwargs_to_build(self):
        from streamtex.book import st_include
        received = []

        mod = types.ModuleType("fake_block")
        mod.__name__ = "fake_block"
        mod.build = lambda *a, **kw: received.append((a, kw))

        with patch("streamtex.book.st"):
            st_include(mod, "arg1", key="val")

        assert received[0] == (("arg1",), {"key": "val"})

    def test_missing_build_shows_error_markdown(self):
        """Module without build() triggers st.markdown error message.

        book.py accesses block_file_module.__path__ in the error message,
        which only exists on *package* modules.  We set it explicitly so the
        f-string succeeds and st.markdown is actually reached.
        """
        from streamtex.book import st_include
        mod = types.ModuleType("no_build_block")
        mod.__name__ = "no_build_block"
        mod.__path__ = ["<fake/path>"]   # needed by book.py's error f-string
        # deliberately no build() attribute

        with patch("streamtex.book.st") as mock_st:
            st_include(mod)

        # st.markdown should be called with a red-background warning
        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args[0][0]
        assert "build()" in call_args or "does not contain" in call_args

    def test_none_module_shows_error_markdown(self):
        """st_include(None) triggers the falsy-module guard and shows an error."""
        from streamtex.book import st_include

        with patch("streamtex.book.st") as mock_st:
            st_include(None)
            mock_st.markdown.assert_called_once()
            assert "not found" in mock_st.markdown.call_args[0][0].lower()

    def test_build_exception_is_reraised(self):
        from streamtex.book import st_include

        mod = types.ModuleType("bad_block")
        mod.__name__ = "bad_block"
        mod.build = lambda: (_ for _ in ()).throw(RuntimeError("block exploded"))

        with patch("streamtex.book.st"):
            with pytest.raises(RuntimeError, match="block exploded"):
                st_include(mod)

    def test_build_exception_shows_error_markdown(self):
        """When build() raises, st.markdown is called before re-raising."""
        from streamtex.book import st_include

        mod = types.ModuleType("bad_block")
        mod.__name__ = "bad_block"
        mod.build = lambda: (_ for _ in ()).throw(ValueError("oops"))

        with patch("streamtex.book.st") as mock_st:
            with pytest.raises(ValueError):
                st_include(mod)

        mock_st.markdown.assert_called_once()
        call_text = mock_st.markdown.call_args[0][0]
        assert "bad_block" in call_text or "Error" in call_text

    def test_build_return_value_is_ignored(self):
        """st_include does not forward build()'s return value."""
        from streamtex.book import st_include

        mod = types.ModuleType("returning_block")
        mod.__name__ = "returning_block"
        mod.build = lambda: "should be ignored"

        with patch("streamtex.book.st"):
            result = st_include(mod)

        assert result is None
