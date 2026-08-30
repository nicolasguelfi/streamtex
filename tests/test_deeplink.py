"""Tests for streamtex.deeplink — ?marker= / ?page= resolution and page_url()."""

import pytest

from streamtex.deeplink import find_marker, page_url, resolve_initial_page

MARKERS = [
    {"index": 0, "label": "How we debate", "anchor": "stx-marker-how-we-debate-0", "hidden": False, "page_idx": 0},
    {"index": 1, "label": "Electricity", "anchor": "stx-marker-electricity-1", "hidden": False, "page_idx": 3},
    {"index": 2, "label": "Électricité", "anchor": "stx-marker-électricité-2", "hidden": False, "page_idx": 4,
     "key": "electricity"},
    {"index": 3, "label": "Wave 3", "anchor": "stx-marker-wave-3-3", "hidden": True, "page_idx": 5},
    # auto marker bridged from a TOC heading: anchor is the TOC key_anchor
    {"index": 4, "label": "Provenance", "anchor": "2-provenance", "hidden": False, "page_idx": 7},
]


class TestFindMarker:
    def test_key_wins_over_label_slug(self):
        # index 1 has the slug "electricity" but index 2 carries the explicit key
        assert find_marker(MARKERS, "electricity")["index"] == 2

    def test_exact_anchor(self):
        assert find_marker(MARKERS, "stx-marker-wave-3-3")["index"] == 3

    def test_label_slug_prefix(self):
        assert find_marker(MARKERS, "how-we-debate")["index"] == 0

    def test_label_text_is_slugified(self):
        assert find_marker(MARKERS, "How we debate")["index"] == 0

    def test_slug_ending_with_digits(self):
        assert find_marker(MARKERS, "wave-3")["index"] == 3

    def test_toc_bridged_marker_by_label(self):
        assert find_marker(MARKERS, "provenance")["index"] == 4

    def test_unknown_and_empty(self):
        assert find_marker(MARKERS, "nope") is None
        assert find_marker(MARKERS, "") is None
        assert find_marker([], "electricity") is None


class TestResolveInitialPage:
    def test_no_params(self):
        assert resolve_initial_page({}, MARKERS, 10) == (0, None)

    def test_marker_gives_page_and_index(self):
        assert resolve_initial_page({"marker": "how-we-debate"}, MARKERS, 10) == (0, 0)
        assert resolve_initial_page({"marker": "electricity"}, MARKERS, 10) == (4, 2)

    def test_marker_wins_over_page(self):
        assert resolve_initial_page({"marker": "wave-3", "page": "2"}, MARKERS, 10) == (5, 3)

    def test_unknown_marker_falls_back_to_page(self):
        assert resolve_initial_page({"marker": "nope", "page": "2"}, MARKERS, 10) == (1, None)

    def test_page_is_one_based_and_bounded(self):
        assert resolve_initial_page({"page": "1"}, MARKERS, 10) == (0, None)
        assert resolve_initial_page({"page": "10"}, MARKERS, 10) == (9, None)
        assert resolve_initial_page({"page": "11"}, MARKERS, 10) == (0, None)
        assert resolve_initial_page({"page": "0"}, MARKERS, 10) == (0, None)
        assert resolve_initial_page({"page": "-3"}, MARKERS, 10) == (0, None)

    def test_garbage_never_raises(self):
        assert resolve_initial_page({"page": "abc"}, MARKERS, 10) == (0, None)
        assert resolve_initial_page({"page": ["3", "4"]}, MARKERS, 10) == (2, None)
        assert resolve_initial_page({"marker": None, "page": None}, MARKERS, 10) == (0, None)
        assert resolve_initial_page({"page": "3"}, MARKERS, 0) == (0, None)

    def test_stale_marker_page_falls_through(self):
        # cache says page 7 but the book now has 5 pages: not a target
        assert resolve_initial_page({"marker": "provenance"}, MARKERS, 5) == (0, None)
        assert resolve_initial_page({"marker": "provenance", "page": "2"}, MARKERS, 5) == (1, None)

    def test_other_params_ignored(self):
        assert resolve_initial_page({"lang": "fr", "project": "x"}, MARKERS, 10) == (0, None)


class TestPageUrl:
    def test_marker_keeps_existing_query(self):
        assert page_url("https://x/waves?lang=en", marker="electricity") == \
            "https://x/waves?lang=en&marker=electricity"

    def test_page_is_one_based(self):
        assert page_url("https://x/waves", page=3) == "https://x/waves?page=3"
        with pytest.raises(ValueError):
            page_url("https://x/waves", page=0)

    def test_marker_wins_over_page(self):
        assert page_url("https://x/w", marker="m", page=3) == "https://x/w?marker=m"

    def test_extra_params_and_override(self):
        assert page_url("https://x/w?lang=en", marker="m", lang="fr") == "https://x/w?lang=fr&marker=m"

    def test_replaces_previous_deep_link(self):
        assert page_url("https://x/w?marker=old&lang=en", page=2) == "https://x/w?lang=en&page=2"

    def test_fragment_preserved_and_encoding(self):
        assert page_url("https://x/w#top", marker="é lec") == "https://x/w?marker=%C3%A9+lec#top"

    def test_extra_param_keeps_existing_deep_link(self):
        assert page_url("https://x/w?marker=m", lang="fr") == "https://x/w?marker=m&lang=fr"
        assert page_url("https://x/w?page=3", lang="fr") == "https://x/w?page=3&lang=fr"

    def test_no_change_without_args(self):
        assert page_url("https://x/w?lang=en") == "https://x/w?lang=en"
        assert page_url("https://x/w") == "https://x/w"

    def test_exported_from_package(self):
        import streamtex
        assert streamtex.page_url is page_url
